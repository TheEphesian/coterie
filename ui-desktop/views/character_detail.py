"""Character Detail View for viewing and editing characters."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QTabWidget,
    QFormLayout, QSpinBox, QMessageBox, QScrollArea,
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui_desktop.api_client import APIClient


class CharacterDetailView(QWidget):
    """View for viewing and editing a character."""
    
    back_requested = pyqtSignal()
    character_updated = pyqtSignal()
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.character_id = None
        self.character_data = None
        self.players = []
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        self.title_label = QLabel("Character Details")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.title_label, stretch=1)
        
        # Save button
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.save_btn.clicked.connect(self._save_character)
        header_layout.addWidget(self.save_btn)
        
        # Delete button
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self._delete_character)
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Tabs
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
        
        # Basic Info Tab
        self.basic_tab = self._create_basic_tab()
        self.tabs.addTab(self.basic_tab, "Basic Info")
        
        # Traits Tab
        self.traits_tab = self._create_traits_tab()
        self.tabs.addTab(self.traits_tab, "Traits")
        
        # Biography Tab
        self.bio_tab = self._create_bio_tab()
        self.tabs.addTab(self.bio_tab, "Biography & Notes")
        
        # XP History Tab
        self.xp_tab = self._create_xp_tab()
        self.tabs.addTab(self.xp_tab, "XP History")
        
        layout.addWidget(self.tabs)
    
    def _create_basic_tab(self) -> QWidget:
        """Create the basic info tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Character Name")
        self.name_input.setStyleSheet(self._input_style())
        layout.addRow("Name:", self.name_input)
        
        # Race type
        self.race_combo = QComboBox()
        races = [
            "vampire", "werewolf", "mage", "changeling", "wraith",
            "mummy", "kuei_jin", "fera", "hunter", "demon", "mortal", "various"
        ]
        for race in races:
            self.race_combo.addItem(race.replace("_", "-").title(), race)
        self.race_combo.setStyleSheet(self._input_style())
        layout.addRow("Race:", self.race_combo)
        
        # Player
        self.player_combo = QComboBox()
        self.player_combo.addItem("No Player", "")
        self.player_combo.setStyleSheet(self._input_style())
        layout.addRow("Player:", self.player_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItem("Active", "active")
        self.status_combo.addItem("Inactive", "inactive")
        self.status_combo.setStyleSheet(self._input_style())
        layout.addRow("Status:", self.status_combo)
        
        # NPC checkbox
        self.npc_checkbox = QComboBox()
        self.npc_checkbox.addItem("No", False)
        self.npc_checkbox.addItem("Yes", True)
        layout.addRow("Is NPC:", self.npc_checkbox)
        
        # XP
        xp_layout = QHBoxLayout()
        
        self.xp_unspent = QSpinBox()
        self.xp_unspent.setMaximum(99999)
        self.xp_unspent.setStyleSheet(self._input_style())
        xp_layout.addWidget(QLabel("Unspent:"))
        xp_layout.addWidget(self.xp_unspent)
        
        self.xp_earned = QSpinBox()
        self.xp_earned.setMaximum(99999)
        self.xp_earned.setStyleSheet(self._input_style())
        xp_layout.addWidget(QLabel("Earned:"))
        xp_layout.addWidget(self.xp_earned)
        
        xp_layout.addStretch()
        layout.addRow("Experience:", xp_layout)
        
        # Narrator
        self.narrator_input = QLineEdit()
        self.narrator_input.setPlaceholderText("Narrator Name")
        self.narrator_input.setStyleSheet(self._input_style())
        layout.addRow("Narrator:", self.narrator_input)
        
        scroll.setWidget(widget)
        return scroll
    
    def _create_traits_tab(self) -> QWidget:
        """Create the traits tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel("Traits editing coming soon...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #7f8c8d; font-size: 16px; padding: 50px;")
        layout.addWidget(label)
        
        return widget
    
    def _create_bio_tab(self) -> QWidget:
        """Create the biography tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Biography
        bio_label = QLabel("Biography:")
        bio_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(bio_label)
        
        self.biography_text = QTextEdit()
        self.biography_text.setPlaceholderText("Enter character biography...")
        self.biography_text.setMinimumHeight(200)
        self.biography_text.setStyleSheet(self._text_area_style())
        layout.addWidget(self.biography_text)
        
        # Notes
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(notes_label)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter notes...")
        self.notes_text.setMinimumHeight(150)
        self.notes_text.setStyleSheet(self._text_area_style())
        layout.addWidget(self.notes_text)
        
        return widget
    
    def _create_xp_tab(self) -> QWidget:
        """Create the XP history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add XP section
        add_xp_layout = QHBoxLayout()
        
        self.xp_amount = QSpinBox()
        self.xp_amount.setMinimum(-999)
        self.xp_amount.setMaximum(999)
        self.xp_amount.setStyleSheet(self._input_style())
        add_xp_layout.addWidget(QLabel("Amount:"))
        add_xp_layout.addWidget(self.xp_amount)
        
        self.xp_reason = QLineEdit()
        self.xp_reason.setPlaceholderText("Reason for XP change")
        self.xp_reason.setStyleSheet(self._input_style())
        add_xp_layout.addWidget(QLabel("Reason:"), stretch=0)
        add_xp_layout.addWidget(self.xp_reason, stretch=1)
        
        add_xp_btn = QPushButton("Add XP")
        add_xp_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_xp_btn.clicked.connect(self._add_xp)
        add_xp_layout.addWidget(add_xp_btn)
        
        layout.addLayout(add_xp_layout)
        
        # XP History label
        history_label = QLabel("XP History:")
        history_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(history_label)
        
        # XP History display (placeholder)
        self.xp_history_label = QLabel("No XP history available")
        self.xp_history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.xp_history_label.setStyleSheet("color: #7f8c8d; padding: 20px;")
        layout.addWidget(self.xp_history_label)
        
        layout.addStretch()
        
        return widget
    
    def _input_style(self) -> str:
        """Get standard input style."""
        return """
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #3498db;
            }
        """
    
    def _text_area_style(self) -> str:
        """Get text area style."""
        return """
            QTextEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """
    
    def new_character(self):
        """Prepare form for creating a new character."""
        self.character_id = None
        self.character_data = None
        self.title_label.setText("New Character")
        
        # Clear all fields
        self.name_input.clear()
        self.race_combo.setCurrentIndex(0)
        self.player_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.npc_checkbox.setCurrentIndex(0)
        self.xp_unspent.setValue(0)
        self.xp_earned.setValue(0)
        self.narrator_input.clear()
        self.biography_text.clear()
        self.notes_text.clear()
        self.xp_history_label.setText("No XP history available")
        
        # Load players
        self._load_players()
    
    def load_character(self, character_id: str):
        """Load a character into the form."""
        self.character_id = character_id
        
        try:
            self.character_data = self.api_client.get_character(character_id)
            self._populate_form()
            self._load_players()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load character: {str(e)}")
    
    def _populate_form(self):
        """Populate the form with character data."""
        if not self.character_data:
            return
        
        self.title_label.setText(f"Editing: {self.character_data.get('name', 'Unknown')}")
        
        # Basic info
        self.name_input.setText(self.character_data.get("name", ""))
        
        race_type = self.character_data.get("race_type", "")
        index = self.race_combo.findData(race_type)
        if index >= 0:
            self.race_combo.setCurrentIndex(index)
        
        status = self.character_data.get("status", "active")
        index = self.status_combo.findData(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        is_npc = self.character_data.get("is_npc", False)
        self.npc_checkbox.setCurrentIndex(1 if is_npc else 0)
        
        self.xp_unspent.setValue(self.character_data.get("xp_unspent", 0))
        self.xp_earned.setValue(self.character_data.get("xp_earned", 0))
        self.narrator_input.setText(self.character_data.get("narrator", ""))
        
        # Biography
        self.biography_text.setText(self.character_data.get("biography", ""))
        self.notes_text.setText(self.character_data.get("notes", ""))
        
        # XP History
        xp_history = self.character_data.get("xp_history", [])
        if xp_history:
            history_text = "Recent changes:\n"
            for entry in xp_history[-10:]:  # Show last 10
                entry_type = entry.get("entry_type", "unknown")
                amount = entry.get("change_amount", 0)
                reason = entry.get("reason", "No reason")
                date = entry.get("date", "Unknown date")
                history_text += f"\n{date}: {entry_type} {amount:+d} XP - {reason}"
            self.xp_history_label.setText(history_text)
    
    def _load_players(self):
        """Load players into the combo box."""
        try:
            self.players = self.api_client.get_players()
            self.player_combo.clear()
            self.player_combo.addItem("No Player", "")
            
            current_player_id = self.character_data.get("player_id") if self.character_data else None
            selected_index = 0
            
            for i, player in enumerate(self.players):
                self.player_combo.addItem(player.get("name", "Unknown"), player.get("id"))
                if player.get("id") == current_player_id:
                    selected_index = i + 1
            
            self.player_combo.setCurrentIndex(selected_index)
        except Exception:
            pass  # Fail silently, not critical
    
    def _save_character(self):
        """Save the character."""
        data = {
            "name": self.name_input.text(),
            "race_type": self.race_combo.currentData(),
            "player_id": self.player_combo.currentData() or None,
            "status": self.status_combo.currentData(),
            "is_npc": self.npc_checkbox.currentData(),
            "xp_unspent": self.xp_unspent.value(),
            "xp_earned": self.xp_earned.value(),
            "narrator": self.narrator_input.text() or None,
            "biography": self.biography_text.toPlainText() or None,
            "notes": self.notes_text.toPlainText() or None,
            "data": {},  # Race-specific data
        }
        
        try:
            if self.character_id:
                # Update existing
                self.api_client.update_character(self.character_id, data)
                QMessageBox.information(self, "Success", "Character updated successfully!")
            else:
                # Create new
                result = self.api_client.create_character(data)
                self.character_id = result.get("id")
                QMessageBox.information(self, "Success", "Character created successfully!")
            
            self.character_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save character: {str(e)}")
    
    def _delete_character(self):
        """Delete the character."""
        if not self.character_id:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this character?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_character(self.character_id)
                QMessageBox.information(self, "Success", "Character deleted successfully!")
                self.character_updated.emit()
                self.back_requested.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete character: {str(e)}")
    
    def _add_xp(self):
        """Add XP to the character."""
        if not self.character_id:
            QMessageBox.warning(self, "Warning", "Please save the character first.")
            return
        
        amount = self.xp_amount.value()
        reason = self.xp_reason.text()
        
        if amount == 0:
            QMessageBox.warning(self, "Warning", "XP amount cannot be zero.")
            return
        
        try:
            endpoint = "/xp/add" if amount > 0 else "/xp/spend"
            data = {
                "amount": abs(amount),
                "reason": reason or "Manual adjustment"
            }
            self.api_client.post(f"/api/v1/characters/{self.character_id}{endpoint}", data)
            QMessageBox.information(self, "Success", f"XP {'added' if amount > 0 else 'spent'} successfully!")
            self.load_character(self.character_id)  # Reload to show updated values
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update XP: {str(e)}")
