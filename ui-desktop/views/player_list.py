"""Player List View for managing players."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
    QMessageBox, QAbstractItemView, QDialog, QFormLayout,
    QSpinBox
)
from PyQt6.QtCore import Qt

from ui_desktop.api_client import APIClient


class PlayerListView(QWidget):
    """View for listing and managing players."""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.players = []
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Players")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Create button
        create_btn = QPushButton("➕ New Player")
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
        create_btn.clicked.connect(self._create_player)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search players...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self._apply_filters)
        layout.addWidget(self.search_input)
        
        # Players table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Email", "Status", "PP Unspent", "PP Earned", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
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
        
        layout.addWidget(self.table)
        
        # Status
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh the player list."""
        try:
            self.players = self.api_client.get_players()
            self._apply_filters()
            self.status_label.setText(f"{len(self.players)} players total")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load players: {str(e)}")
            self.status_label.setText("Error loading players")
    
    def _apply_filters(self):
        """Apply search filter."""
        search_text = self.search_input.text().lower()
        
        filtered = self.players
        if search_text:
            filtered = [
                p for p in filtered
                if search_text in p.get("name", "").lower()
                or search_text in (p.get("email") or "").lower()
            ]
        
        self._update_table(filtered)
    
    def _update_table(self, players: list):
        """Update the table with player data."""
        self.table.setRowCount(len(players))
        
        for row, player in enumerate(players):
            # Name
            name_item = QTableWidgetItem(player.get("name", "Unknown"))
            name_item.setData(Qt.ItemDataRole.UserRole, player.get("id"))
            self.table.setItem(row, 0, name_item)
            
            # Email
            self.table.setItem(row, 1, QTableWidgetItem(player.get("email") or "-"))
            
            # Status
            self.table.setItem(row, 2, QTableWidgetItem(player.get("status", "active").title()))
            
            # PP Unspent
            self.table.setItem(row, 3, QTableWidgetItem(str(player.get("pp_unspent", 0))))
            
            # PP Earned
            self.table.setItem(row, 4, QTableWidgetItem(str(player.get("pp_earned", 0))))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
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
            edit_btn.clicked.connect(lambda checked, p=player: self._edit_player(p))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
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
            delete_btn.clicked.connect(lambda checked, pid=player.get("id"): self._delete_player(pid))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.resizeRowsToContents()
    
    def _create_player(self):
        """Open dialog to create a new player."""
        dialog = PlayerDialog(self.api_client, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _edit_player(self, player: dict):
        """Open dialog to edit a player."""
        dialog = PlayerDialog(self.api_client, player=player, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _delete_player(self, player_id: str):
        """Delete a player."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this player?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_player(player_id)
                QMessageBox.information(self, "Success", "Player deleted successfully!")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete player: {str(e)}")


class PlayerDialog(QDialog):
    """Dialog for creating/editing a player."""
    
    def __init__(self, api_client: APIClient, player: dict = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.player = player
        self.setWindowTitle("Edit Player" if player else "New Player")
        self.setMinimumWidth(400)
        self._build_ui()
        
        if player:
            self._populate_form()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Player Name")
        form_layout.addRow("Name:", self.name_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Position
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Position/Title")
        form_layout.addRow("Position:", self.position_input)
        
        # PP
        pp_layout = QHBoxLayout()
        
        self.pp_unspent = QSpinBox()
        self.pp_unspent.setMaximum(9999)
        pp_layout.addWidget(QLabel("Unspent:"))
        pp_layout.addWidget(self.pp_unspent)
        
        self.pp_earned = QSpinBox()
        self.pp_earned.setMaximum(9999)
        pp_layout.addWidget(QLabel("Earned:"))
        pp_layout.addWidget(self.pp_earned)
        
        pp_layout.addStretch()
        form_layout.addRow("Player Points:", pp_layout)
        
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
        """Populate form with player data."""
        if not self.player:
            return
        
        self.name_input.setText(self.player.get("name", ""))
        self.email_input.setText(self.player.get("email") or "")
        self.phone_input.setText(self.player.get("phone") or "")
        self.position_input.setText(self.player.get("position") or "")
        self.pp_unspent.setValue(self.player.get("pp_unspent", 0))
        self.pp_earned.setValue(self.player.get("pp_earned", 0))
    
    def _save(self):
        """Save the player."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        data = {
            "name": name,
            "email": self.email_input.text() or None,
            "phone": self.phone_input.text() or None,
            "position": self.position_input.text() or None,
            "pp_unspent": self.pp_unspent.value(),
            "pp_earned": self.pp_earned.value(),
        }
        
        try:
            if self.player:
                self.api_client.update_player(self.player["id"], data)
            else:
                self.api_client.create_player(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save player: {str(e)}")
