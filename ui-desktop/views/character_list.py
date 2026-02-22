"""Character List View for displaying and filtering characters."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui_desktop.api_client import APIClient


class CharacterListView(QWidget):
    """View for listing and filtering characters."""
    
    character_selected = pyqtSignal(str)  # Emits character_id
    create_character_requested = pyqtSignal()
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.characters = []
        self._build_ui()
        self.refresh()
    
    def _build_ui(self):
        """Build the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Characters")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Create button
        create_btn = QPushButton("➕ New Character")
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
        create_btn.clicked.connect(self.create_character_requested.emit)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Filters
        filters_layout = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search characters...")
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
        
        # Race filter
        self.race_filter = QComboBox()
        self.race_filter.addItem("All Races", "")
        races = [
            "vampire", "werewolf", "mage", "changeling", "wraith",
            "mummy", "kuei_jin", "fera", "hunter", "demon", "mortal", "various"
        ]
        for race in races:
            self.race_filter.addItem(race.replace("_", "-").title(), race)
        self.race_filter.currentIndexChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.race_filter, stretch=1)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Status", "")
        self.status_filter.addItem("Active", "active")
        self.status_filter.addItem("Inactive", "inactive")
        self.status_filter.addItem("NPC", "npc")
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.status_filter, stretch=1)
        
        layout.addLayout(filters_layout)
        
        # Character table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Race", "Player", "Status", "XP", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        
        layout.addWidget(self.table)
        
        # Status label
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh the character list."""
        try:
            self.characters = self.api_client.get_characters()
            self._apply_filters()
            self.status_label.setText(f"{len(self.characters)} characters total")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load characters: {str(e)}")
            self.status_label.setText("Error loading characters")
    
    def _apply_filters(self):
        """Apply filters to the character list."""
        search_text = self.search_input.text().lower()
        race_filter = self.race_filter.currentData()
        status_filter = self.status_filter.currentData()
        
        filtered = self.characters
        
        if search_text:
            filtered = [
                c for c in filtered
                if search_text in c.get("name", "").lower()
                or search_text in c.get("player_name", "").lower()
            ]
        
        if race_filter:
            filtered = [c for c in filtered if c.get("race_type") == race_filter]
        
        if status_filter:
            filtered = [c for c in filtered if c.get("status") == status_filter]
        
        self._update_table(filtered)
    
    def _update_table(self, characters: list):
        """Update the table with character data."""
        self.table.setRowCount(len(characters))
        
        for row, char in enumerate(characters):
            # Name
            name_item = QTableWidgetItem(char.get("name", "Unknown"))
            name_item.setData(Qt.ItemDataRole.UserRole, char.get("id"))
            self.table.setItem(row, 0, name_item)
            
            # Race
            race = char.get("race_type", "unknown")
            self.table.setItem(row, 1, QTableWidgetItem(race.replace("_", "-").title()))
            
            # Player
            player_name = char.get("player_name") or "No Player"
            self.table.setItem(row, 2, QTableWidgetItem(player_name))
            
            # Status
            status = "NPC" if char.get("is_npc") else char.get("status", "unknown").title()
            self.table.setItem(row, 3, QTableWidgetItem(status))
            
            # XP
            xp = f"{char.get('xp_unspent', 0)} / {char.get('xp_earned', 0)}"
            self.table.setItem(row, 4, QTableWidgetItem(xp))
            
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
            edit_btn.clicked.connect(lambda checked, cid=char.get("id"): self.character_selected.emit(cid))
            actions_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.resizeRowsToContents()
    
    def _on_row_double_clicked(self, index):
        """Handle double click on a row."""
        row = index.row()
        character_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if character_id:
            self.character_selected.emit(character_id)
