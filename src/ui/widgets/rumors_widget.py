"""Rumors management widget for Coterie."""

import logging
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QComboBox, QSplitter, QGroupBox, QFormLayout, QMessageBox,
    QDialog, QDialogButtonBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.core.engine import get_session
from src.core.models import Rumor

logger = logging.getLogger(__name__)

RUMOR_LEVELS = {
    1: "Street",
    2: "City",
    3: "Regional",
    4: "National",
    5: "International",
}

RUMOR_CATEGORIES = ["All Races", "Vampire", "Werewolf", "Mage", "Changeling", "Mortal", "ST Only"]


class RumorDialog(QDialog):
    """Dialog for creating or editing a rumor."""

    def __init__(self, parent: Optional[QWidget] = None, rumor: Optional[Rumor] = None):
        super().__init__(parent)
        self.rumor = rumor
        self.setWindowTitle("Edit Rumor" if rumor else "New Rumor")
        self.setMinimumSize(550, 450)
        self._setup_ui()
        if rumor:
            self._load_rumor(rumor)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Rumor headline...")
        form.addRow("Title:", self.title_edit)

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(1)
        level_layout = QHBoxLayout()
        level_layout.addWidget(self.level_spin)
        self.level_desc = QLabel(RUMOR_LEVELS[1])
        level_layout.addWidget(self.level_desc)
        level_layout.addStretch()
        self.level_spin.valueChanged.connect(
            lambda v: self.level_desc.setText(RUMOR_LEVELS.get(v, ""))
        )
        form.addRow("Level:", level_layout)

        self.category_combo = QComboBox()
        self.category_combo.addItems(RUMOR_CATEGORIES)
        form.addRow("Target Race:", self.category_combo)

        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("YYYY-MM-DD (e.g., 2024-01-15)")
        self.date_edit.setText(datetime.now().strftime("%Y-%m-%d"))
        form.addRow("Date:", self.date_edit)

        layout.addLayout(form)

        content_label = QLabel("Content:")
        layout.addWidget(content_label)

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("What characters hear about this topic...")
        self.content_edit.setMinimumHeight(200)
        layout.addWidget(self.content_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_rumor(self, rumor: Rumor) -> None:
        self.title_edit.setText(rumor.title or "")
        self.level_spin.setValue(rumor.level or 1)
        idx = self.category_combo.findText(rumor.target_race or "All Races")
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        self.date_edit.setText(rumor.rumor_date or datetime.now().strftime("%Y-%m-%d"))
        self.content_edit.setPlainText(rumor.content or "")

    def _on_accept(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Rumor title is required.")
            return
        date_text = self.date_edit.text().strip()
        if not date_text:
            QMessageBox.warning(self, "Validation", "Date is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "level": self.level_spin.value(),
            "target_race": self.category_combo.currentText(),
            "rumor_date": self.date_edit.text().strip(),
            "content": self.content_edit.toPlainText().strip(),
        }


class RumorsWidget(QWidget):
    """Widget for managing rumors in a chronicle."""

    rumor_selected = pyqtSignal(int)  # rumor id

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.chronicle_id: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Rumors")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.new_btn = QPushButton("New Rumor")
        self.new_btn.clicked.connect(self._on_new_rumor)
        header_layout.addWidget(self.new_btn)
        layout.addLayout(header_layout)

        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Target:"))
        self.race_filter = QComboBox()
        self.race_filter.addItems(["All"] + RUMOR_CATEGORIES)
        self.race_filter.currentTextChanged.connect(self.refresh)
        filter_layout.addWidget(self.race_filter)

        filter_layout.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItem("All", 0)
        for lvl, name in RUMOR_LEVELS.items():
            self.level_filter.addItem(f"Level {lvl} ({name})", lvl)
        self.level_filter.currentIndexChanged.connect(self.refresh)
        filter_layout.addWidget(self.level_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Splitter: list + detail
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: rumor list
        list_group = QGroupBox("Rumor List")
        list_layout = QVBoxLayout(list_group)
        self.rumor_list = QListWidget()
        self.rumor_list.currentItemChanged.connect(self._on_selection_changed)
        self.rumor_list.itemDoubleClicked.connect(self._on_edit_rumor)
        list_layout.addWidget(self.rumor_list)

        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit_rumor)
        self.edit_btn.setEnabled(False)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete_rumor)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)
        list_layout.addLayout(btn_layout)

        splitter.addWidget(list_group)

        # Right: detail panel
        detail_group = QGroupBox("Rumor Details")
        detail_layout = QVBoxLayout(detail_group)

        form = QFormLayout()
        self.detail_title = QLabel("-")
        self.detail_title.setFont(QFont("", -1, QFont.Weight.Bold))
        self.detail_title.setWordWrap(True)
        form.addRow("Title:", self.detail_title)

        self.detail_level = QLabel("-")
        form.addRow("Level:", self.detail_level)

        self.detail_race = QLabel("-")
        form.addRow("Target:", self.detail_race)

        self.detail_date = QLabel("-")
        form.addRow("Date:", self.detail_date)
        detail_layout.addLayout(form)

        detail_layout.addWidget(QLabel("Content:"))
        self.detail_content = QTextEdit()
        self.detail_content.setReadOnly(True)
        detail_layout.addWidget(self.detail_content)

        splitter.addWidget(detail_group)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

    def set_chronicle(self, chronicle_id: Optional[int]) -> None:
        self.chronicle_id = chronicle_id
        self.refresh()

    def refresh(self) -> None:
        self.rumor_list.clear()
        self._clear_detail()

        try:
            session = get_session()
            try:
                query = session.query(Rumor)
                if self.chronicle_id:
                    query = query.filter(Rumor.game_id == self.chronicle_id)

                race_filter = self.race_filter.currentText()
                if race_filter != "All":
                    query = query.filter(Rumor.target_race == race_filter)

                level_filter = self.level_filter.currentData()
                if level_filter:
                    query = query.filter(Rumor.level == level_filter)

                rumors = query.order_by(Rumor.rumor_date.desc()).all()
                for rumor in rumors:
                    item = QListWidgetItem()
                    level_name = RUMOR_LEVELS.get(rumor.level, f"L{rumor.level}")
                    item.setText(f"[{level_name}] {rumor.title}")
                    item.setData(Qt.ItemDataRole.UserRole, rumor.id)
                    self.rumor_list.addItem(item)
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to load rumors: {e}")

    def _clear_detail(self) -> None:
        self.detail_title.setText("-")
        self.detail_level.setText("-")
        self.detail_race.setText("-")
        self.detail_date.setText("-")
        self.detail_content.clear()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _on_selection_changed(self, current: Optional[QListWidgetItem], _) -> None:
        if not current:
            self._clear_detail()
            return

        rumor_id = current.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        try:
            session = get_session()
            try:
                rumor = session.query(Rumor).filter_by(id=rumor_id).first()
                if rumor:
                    self.detail_title.setText(rumor.title or "-")
                    level_name = RUMOR_LEVELS.get(rumor.level, str(rumor.level))
                    self.detail_level.setText(f"Level {rumor.level} ({level_name})")
                    self.detail_race.setText(rumor.target_race or "All Races")
                    self.detail_date.setText(rumor.rumor_date or "-")
                    self.detail_content.setPlainText(rumor.content or "")
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to load rumor detail: {e}")

    def _on_new_rumor(self) -> None:
        dialog = RumorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                session = get_session()
                try:
                    rumor = Rumor(
                        title=data["title"],
                        level=data["level"],
                        target_race=data["target_race"],
                        rumor_date=data["rumor_date"],
                        content=data["content"],
                        game_id=self.chronicle_id,
                    )
                    session.add(rumor)
                    session.commit()
                    self.refresh()
                    logger.info(f"Created rumor: {rumor.title}")
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()
            except Exception as e:
                logger.error(f"Failed to create rumor: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create rumor: {e}")

    def _on_edit_rumor(self, *args) -> None:
        item = self.rumor_list.currentItem()
        if not item:
            return

        rumor_id = item.data(Qt.ItemDataRole.UserRole)

        try:
            session = get_session()
            try:
                rumor = session.query(Rumor).filter_by(id=rumor_id).first()
                if not rumor:
                    return

                dialog = RumorDialog(self, rumor)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    rumor.title = data["title"]
                    rumor.level = data["level"]
                    rumor.target_race = data["target_race"]
                    rumor.rumor_date = data["rumor_date"]
                    rumor.content = data["content"]
                    session.commit()
                    self.refresh()
                    logger.info(f"Updated rumor: {rumor.title}")
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to update rumor: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update rumor: {e}")

    def _on_delete_rumor(self) -> None:
        item = self.rumor_list.currentItem()
        if not item:
            return

        rumor_id = item.data(Qt.ItemDataRole.UserRole)

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this rumor?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            session = get_session()
            try:
                rumor = session.query(Rumor).filter_by(id=rumor_id).first()
                if rumor:
                    session.delete(rumor)
                    session.commit()
                    self.refresh()
                    logger.info(f"Deleted rumor id={rumor_id}")
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to delete rumor: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete rumor: {e}")
