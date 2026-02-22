"""Boon Management View for tracking favors between characters."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QMessageBox, QAbstractItemView, QDialog,
    QFormLayout, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui_desktop.api_client import APIClient


class BoonView(QWidget):
    """View for managing boons (favors between characters)."""
    
    boon_selected = pyqtSignal(str)  # Emits boon_id
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.boons = []
        self.characters = []
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Boons (Favors)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Create button
        create_btn = QPushButton("➕ New Boon")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        create_btn.clicked.connect(self._create_boon)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Filters
        filters_layout = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search boons...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.search_input, stretch=2)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Status", "")
        self.status_filter.addItem("Active", "active")
        self.status_filter.addItem("Repaid", "repaid")
        self.status_filter.addItem("Defaulted", "defaulted")
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.status_filter, stretch=1)
        
        # Boon type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", "")
        self.type_filter.addItem("Trivial", "trivial")
        self.type_filter.addItem("Minor", "minor")
        self.type_filter.addItem("Major", "major")
        self.type_filter.addItem("Blood", "blood")
        self.type_filter.addItem("Life", "life")
        self.type_filter.currentIndexChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.type_filter, stretch=1)
        
        layout.addLayout(filters_layout)
        
        # Tabs for held vs owed
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # All Boons Tab
        self.all_boons_tab = self._create_boons_table()
        self.tabs.addTab(self.all_boons_tab, "All Boons")
        
        layout.addWidget(self.tabs)
        
        # Status
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)
    
    def _create_boons_table(self) -> QWidget:
        """Create the boons table widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Boons table
        self.boons_table = QTableWidget()
        self.boons_table.setColumnCount(8)
        self.boons_table.setHorizontalHeaderLabels([
            "Type", "Status", "Holder", "Owes To", "Description", "Created", "Due Date", "Actions"
        ])
        self.boons_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.boons_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.boons_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.boons_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.boons_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.boons_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.boons_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.boons_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.boons_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.boons_table.setAlternatingRowColors(True)
        self.boons_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
            }
        """)
        
        layout.addWidget(self.boons_table)
        return widget
    
    def refresh(self):
        """Refresh the boon list."""
        try:
            self.boons = self.api_client.get_boonds()
            self.characters = self.api_client.get_characters()
            self._apply_filters()
            self.status_label.setText(f"{len(self.boons)} boons total")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load boons: {str(e)}")
            self.status_label.setText("Error loading boons")
    
    def _apply_filters(self):
        """Apply filters to the boon list."""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentData()
        type_filter = self.type_filter.currentData()
        
        filtered = self.boons
        
        if search_text:
            filtered = [
                b for b in filtered
                if search_text in b.get("description", "").lower()
                or search_text in b.get("holder_name", "").lower()
                or search_text in b.get("owes_to_name", "").lower()
            ]
        
        if status_filter:
            filtered = [b for b in filtered if b.get("status") == status_filter]
        
        if type_filter:
            filtered = [b for b in filtered if b.get("boon_type") == type_filter]
        
        self._update_table(filtered)
    
    def _update_table(self, boons: list):
        """Update the table with boon data."""
        self.boons_table.setRowCount(len(boons))
        
        for row, boon in enumerate(boons):
            # Type
            boon_type = boon.get("boon_type", "unknown")
            self.boons_table.setItem(row, 0, QTableWidgetItem(boon_type.title()))
            
            # Status
            status = boon.get("status", "unknown")
            status_item = QTableWidgetItem(status.title())
            if status == "active":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif status == "repaid":
                status_item.setForeground(Qt.GlobalColor.darkBlue)
            elif status == "defaulted":
                status_item.setForeground(Qt.GlobalColor.darkRed)
            self.boons_table.setItem(row, 1, status_item)
            
            # Holder
            holder_name = boon.get("holder_name") or "Unknown"
            holder_item = QTableWidgetItem(holder_name)
            holder_item.setData(Qt.ItemDataRole.UserRole, boon.get("id"))
            self.boons_table.setItem(row, 2, holder_item)
            
            # Owes To
            owes_to_name = boon.get("owes_to_name") or "Unknown"
            self.boons_table.setItem(row, 3, QTableWidgetItem(owes_to_name))
            
            # Description
            desc = boon.get("description", "")
            self.boons_table.setItem(row, 4, QTableWidgetItem(desc[:50] + "..." if len(desc) > 50 else desc))
            
            # Created
            created = boon.get("created_at", "")[:10] if boon.get("created_at") else "-"
            self.boons_table.setItem(row, 5, QTableWidgetItem(created))
            
            # Due Date
            due = boon.get("due_date") or "-"
            self.boons_table.setItem(row, 6, QTableWidgetItem(due))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            status = boon.get("status", "active")
            
            if status == "active":
                repay_btn = QPushButton("Repay")
                repay_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
                repay_btn.clicked.connect(lambda checked, bid=boon.get("id"): self._repay_boon(bid))
                actions_layout.addWidget(repay_btn)
                
                default_btn = QPushButton("Default")
                default_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                default_btn.clicked.connect(lambda checked, bid=boon.get("id"): self._default_boon(bid))
                actions_layout.addWidget(default_btn)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, b=boon: self._edit_boon(b))
            actions_layout.addWidget(edit_btn)
            
            self.boons_table.setCellWidget(row, 7, actions_widget)
        
        self.boons_table.resizeRowsToContents()
    
    def _create_boon(self):
        """Open dialog to create a new boon."""
        dialog = BoonDialog(self.api_client, characters=self.characters, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _edit_boon(self, boon: dict):
        """Open dialog to edit a boon."""
        dialog = BoonDialog(self.api_client, boon=boon, characters=self.characters, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _repay_boon(self, boon_id: str):
        """Mark a boon as repaid."""
        reply = QMessageBox.question(
            self,
            "Confirm Repayment",
            "Mark this boon as repaid?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.repay_boon(boon_id)
                QMessageBox.information(self, "Success", "Boon marked as repaid!")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to repay boon: {str(e)}")
    
    def _default_boon(self, boon_id: str):
        """Mark a boon as defaulted."""
        reply = QMessageBox.question(
            self,
            "Confirm Default",
            "Mark this boon as defaulted? This is a serious action.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.default_boon(boon_id)
                QMessageBox.information(self, "Success", "Boon marked as defaulted!")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to default boon: {str(e)}")


class BoonDialog(QDialog):
    """Dialog for creating/editing a boon."""
    
    def __init__(self, api_client: APIClient, boon: dict | None = None, 
                 characters: list | None = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.boon = boon
        self.characters = characters or []
        self.setWindowTitle("Edit Boon" if boon else "New Boon")
        self.setMinimumWidth(500)
        self._build_ui()
        
        if boon:
            self._populate_form()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Boon Type
        self.type_combo = QComboBox()
        boon_types = [
            ("Trivial", "trivial"),
            ("Minor", "minor"),
            ("Major", "major"),
            ("Blood", "blood"),
            ("Life", "life"),
        ]
        for label, value in boon_types:
            self.type_combo.addItem(label, value)
        form_layout.addRow("Boon Type:", self.type_combo)
        
        # Holder (character who holds the boon)
        self.holder_combo = QComboBox()
        self.holder_combo.addItem("Select Character...", "")
        for char in self.characters:
            self.holder_combo.addItem(char.get("name", "Unknown"), char.get("id"))
        form_layout.addRow("Holder:", self.holder_combo)
        
        # Owes To (character who owes the boon)
        self.owes_to_combo = QComboBox()
        self.owes_to_combo.addItem("Select Character...", "")
        for char in self.characters:
            self.owes_to_combo.addItem(char.get("name", "Unknown"), char.get("id"))
        form_layout.addRow("Owes To:", self.owes_to_combo)
        
        # Description
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Describe the boon/favor...")
        self.description_text.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_text)
        
        # Due Date
        self.due_date_input = QLineEdit()
        self.due_date_input.setPlaceholderText("YYYY-MM-DD (optional)")
        form_layout.addRow("Due Date:", self.due_date_input)
        
        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Additional notes...")
        self.notes_text.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.notes_text)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self._save)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _populate_form(self):
        """Populate form with boon data."""
        if not self.boon:
            return
        
        # Type
        boon_type = self.boon.get("boon_type", "trivial")
        index = self.type_combo.findData(boon_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Holder
        holder_id = self.boon.get("holder_id")
        if holder_id:
            index = self.holder_combo.findData(holder_id)
            if index >= 0:
                self.holder_combo.setCurrentIndex(index)
        
        # Owes To
        owes_to_id = self.boon.get("owes_to_id")
        if owes_to_id:
            index = self.owes_to_combo.findData(owes_to_id)
            if index >= 0:
                self.owes_to_combo.setCurrentIndex(index)
        
        # Description
        self.description_text.setText(self.boon.get("description", ""))
        
        # Due Date
        due_date = self.boon.get("due_date")
        if due_date:
            self.due_date_input.setText(due_date)
        
        # Notes
        notes = self.boon.get("notes")
        if notes:
            self.notes_text.setText(notes)
    
    def _save(self):
        """Save the boon."""
        # Validation
        holder_id = self.holder_combo.currentData()
        owes_to_id = self.owes_to_combo.currentData()
        
        if not holder_id:
            QMessageBox.warning(self, "Validation Error", "Please select a holder character.")
            return
        
        if not owes_to_id:
            QMessageBox.warning(self, "Validation Error", "Please select who owes the boon.")
            return
        
        if holder_id == owes_to_id:
            QMessageBox.warning(self, "Validation Error", "Holder and debtor cannot be the same character.")
            return
        
        data = {
            "boon_type": self.type_combo.currentData(),
            "holder_id": holder_id,
            "owes_to_id": owes_to_id,
            "description": self.description_text.toPlainText() or None,
            "due_date": self.due_date_input.text() or None,
            "notes": self.notes_text.toPlainText() or None,
        }
        
        try:
            if self.boon:
                self.api_client.update_boon(self.boon["id"], data)
            else:
                self.api_client.create_boon(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save boon: {str(e)}")
