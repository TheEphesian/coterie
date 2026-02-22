"""Plots management widget for Coterie."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QComboBox, QSplitter, QGroupBox, QFormLayout, QMessageBox,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.core.engine import get_session
from src.core.models import Plot

logger = logging.getLogger(__name__)


class PlotDialog(QDialog):
    """Dialog for creating or editing a plot."""

    def __init__(self, parent: Optional[QWidget] = None, plot: Optional[Plot] = None):
        super().__init__(parent)
        self.plot = plot
        self.setWindowTitle("Edit Plot" if plot else "New Plot")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        if plot:
            self._load_plot(plot)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Plot title...")
        form.addRow("Title:", self.title_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "resolved", "abandoned", "on hold"])
        form.addRow("Status:", self.status_combo)

        layout.addLayout(form)

        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe this plot line...")
        self.description_edit.setMinimumHeight(200)
        layout.addWidget(self.description_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_plot(self, plot: Plot) -> None:
        self.title_edit.setText(plot.title or "")
        idx = self.status_combo.findText(plot.status or "active")
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        self.description_edit.setPlainText(plot.description or "")

    def _on_accept(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Plot title is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "status": self.status_combo.currentText(),
            "description": self.description_edit.toPlainText().strip(),
        }


class PlotsWidget(QWidget):
    """Widget for managing plots in a chronicle."""

    plot_selected = pyqtSignal(int)  # plot id

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.chronicle_id: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Plots")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.new_btn = QPushButton("New Plot")
        self.new_btn.clicked.connect(self._on_new_plot)
        header_layout.addWidget(self.new_btn)
        layout.addLayout(header_layout)

        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "active", "resolved", "abandoned", "on hold"])
        self.status_filter.currentTextChanged.connect(self.refresh)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Splitter: list + detail
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: plot list
        list_group = QGroupBox("Plot List")
        list_layout = QVBoxLayout(list_group)
        self.plot_list = QListWidget()
        self.plot_list.currentItemChanged.connect(self._on_selection_changed)
        self.plot_list.itemDoubleClicked.connect(self._on_edit_plot)
        list_layout.addWidget(self.plot_list)

        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit_plot)
        self.edit_btn.setEnabled(False)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete_plot)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)
        list_layout.addLayout(btn_layout)

        splitter.addWidget(list_group)

        # Right: detail panel
        detail_group = QGroupBox("Plot Details")
        detail_layout = QVBoxLayout(detail_group)

        form = QFormLayout()
        self.detail_title = QLabel("-")
        self.detail_title.setFont(QFont("", -1, QFont.Weight.Bold))
        form.addRow("Title:", self.detail_title)

        self.detail_status = QLabel("-")
        form.addRow("Status:", self.detail_status)
        detail_layout.addLayout(form)

        detail_layout.addWidget(QLabel("Description:"))
        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        detail_layout.addWidget(self.detail_description)

        splitter.addWidget(detail_group)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

    def set_chronicle(self, chronicle_id: Optional[int]) -> None:
        self.chronicle_id = chronicle_id
        self.refresh()

    def refresh(self) -> None:
        self.plot_list.clear()
        self._clear_detail()

        try:
            session = get_session()
            try:
                query = session.query(Plot)
                if self.chronicle_id:
                    query = query.filter(Plot.game_id == self.chronicle_id)

                status_filter = self.status_filter.currentText()
                if status_filter != "All":
                    query = query.filter(Plot.status == status_filter)

                plots = query.order_by(Plot.title).all()
                for plot in plots:
                    item = QListWidgetItem()
                    status_icon = {"active": "●", "resolved": "✓", "abandoned": "✗", "on hold": "⏸"}.get(
                        plot.status, "●"
                    )
                    item.setText(f"{status_icon} {plot.title}")
                    item.setData(Qt.ItemDataRole.UserRole, plot.id)
                    self.plot_list.addItem(item)

                    # Store plot data for detail view
                    item.setToolTip(plot.description or "")
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to load plots: {e}")

    def _clear_detail(self) -> None:
        self.detail_title.setText("-")
        self.detail_status.setText("-")
        self.detail_description.clear()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _on_selection_changed(self, current: Optional[QListWidgetItem], _) -> None:
        if not current:
            self._clear_detail()
            return

        plot_id = current.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        try:
            session = get_session()
            try:
                plot = session.query(Plot).filter_by(id=plot_id).first()
                if plot:
                    self.detail_title.setText(plot.title or "-")
                    self.detail_status.setText(plot.status or "-")
                    self.detail_description.setPlainText(plot.description or "")
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to load plot detail: {e}")

    def _on_new_plot(self) -> None:
        dialog = PlotDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                session = get_session()
                try:
                    plot = Plot(
                        title=data["title"],
                        status=data["status"],
                        description=data["description"],
                        game_id=self.chronicle_id,
                    )
                    session.add(plot)
                    session.commit()
                    self.refresh()
                    logger.info(f"Created plot: {plot.title}")
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()
            except Exception as e:
                logger.error(f"Failed to create plot: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create plot: {e}")

    def _on_edit_plot(self, *args) -> None:
        item = self.plot_list.currentItem()
        if not item:
            return

        plot_id = item.data(Qt.ItemDataRole.UserRole)

        try:
            session = get_session()
            try:
                plot = session.query(Plot).filter_by(id=plot_id).first()
                if not plot:
                    return

                dialog = PlotDialog(self, plot)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    plot.title = data["title"]
                    plot.status = data["status"]
                    plot.description = data["description"]
                    session.commit()
                    self.refresh()
                    logger.info(f"Updated plot: {plot.title}")
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to update plot: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update plot: {e}")

    def _on_delete_plot(self) -> None:
        item = self.plot_list.currentItem()
        if not item:
            return

        title = item.text()
        plot_id = item.data(Qt.ItemDataRole.UserRole)

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete plot '{title.lstrip('● ✓✗⏸ ')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            session = get_session()
            try:
                plot = session.query(Plot).filter_by(id=plot_id).first()
                if plot:
                    session.delete(plot)
                    session.commit()
                    self.refresh()
                    logger.info(f"Deleted plot id={plot_id}")
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to delete plot: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete plot: {e}")
