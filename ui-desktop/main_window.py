"""Main Window for Grapevine Desktop Application."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt

from ui_desktop.api_client import APIClient
from ui_desktop.views.character_list import CharacterListView
from ui_desktop.views.character_detail import CharacterDetailView
from ui_desktop.views.player_list import PlayerListView
from ui_desktop.views.apr_view import APRView
from ui_desktop.views.boon_view import BoonView


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.current_character_id = None
        
        self.setWindowTitle("Grapevine Modern")
        self.setMinimumSize(1200, 800)
        
        # Build UI
        self._build_ui()
        
        # Check API connection
        self._check_connection()
    
    def _build_ui(self):
        """Build the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Create views
        self.character_list_view = CharacterListView(self.api_client)
        self.character_list_view.character_selected.connect(self._on_character_selected)
        self.character_list_view.create_character_requested.connect(self._on_create_character)
        
        self.character_detail_view = CharacterDetailView(self.api_client)
        self.character_detail_view.back_requested.connect(self._show_character_list)
        self.character_detail_view.character_updated.connect(self._on_character_updated)
        
        self.player_list_view = PlayerListView(self.api_client)
        self.apr_view = APRView(self.api_client)
        self.boon_view = BoonView(self.api_client)
        
        # Add views to stack
        self.content_stack.addWidget(self.character_list_view)  # Index 0
        self.content_stack.addWidget(self.character_detail_view)  # Index 1
        self.content_stack.addWidget(self.player_list_view)  # Index 2
        self.content_stack.addWidget(self.apr_view)  # Index 3
        self.content_stack.addWidget(self.boon_view)  # Index 4
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_sidebar(self) -> QWidget:
        """Create the sidebar navigation."""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Grapevine Modern")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = []
        
        characters_btn = QPushButton("📋 Characters")
        characters_btn.setCheckable(True)
        characters_btn.setChecked(True)
        characters_btn.clicked.connect(lambda: self._switch_view(0, characters_btn))
        layout.addWidget(characters_btn)
        self.nav_buttons.append(characters_btn)
        
        players_btn = QPushButton("👥 Players")
        players_btn.setCheckable(True)
        players_btn.clicked.connect(lambda: self._switch_view(2, players_btn))
        layout.addWidget(players_btn)
        self.nav_buttons.append(players_btn)
        
        apr_btn = QPushButton("📊 Actions/Plots/Rumors")
        apr_btn.setCheckable(True)
        apr_btn.clicked.connect(lambda: self._switch_view(3, apr_btn))
        layout.addWidget(apr_btn)
        self.nav_buttons.append(apr_btn)

        boons_btn = QPushButton("🏛️ Boons")
        boons_btn.setCheckable(True)
        boons_btn.clicked.connect(lambda: self._switch_view(4, boons_btn))
        layout.addWidget(boons_btn)
        self.nav_buttons.append(boons_btn)

        layout.addStretch()
        
        # Connection status
        self.connection_label = QLabel("🟡 Checking connection...")
        self.connection_label.setStyleSheet("padding: 10px; font-size: 12px;")
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.connection_label)
        
        return sidebar
    
    def _switch_view(self, index: int, button: QPushButton):
        """Switch to a different view."""
        # Uncheck all buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)
        
        # Check the clicked button
        button.setChecked(True)
        
        # Switch view
        self.content_stack.setCurrentIndex(index)
        
        # Refresh data if needed
        if index == 0:
            self.character_list_view.refresh()
        elif index == 2:
            self.player_list_view.refresh()
        elif index == 3:
            self.apr_view.refresh()
        elif index == 4:
            self.boon_view.refresh()
    
    def _on_character_selected(self, character_id: str):
        """Handle character selection."""
        self.current_character_id = character_id
        self.character_detail_view.load_character(character_id)
        self.content_stack.setCurrentIndex(1)
        
        # Uncheck all nav buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)
    
    def _on_create_character(self):
        """Handle create character request."""
        self.character_detail_view.new_character()
        self.content_stack.setCurrentIndex(1)
        
        # Uncheck all nav buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)
    
    def _show_character_list(self):
        """Show the character list view."""
        self.content_stack.setCurrentIndex(0)
        self.character_list_view.refresh()
        
        # Check characters button
        for btn in self.nav_buttons:
            btn.setChecked(False)
        self.nav_buttons[0].setChecked(True)
    
    def _on_character_updated(self):
        """Handle character update."""
        self.character_list_view.refresh()
    
    def _check_connection(self):
        """Check API connection."""
        try:
            health = self.api_client.health_check()
            self.connection_label.setText("🟢 Connected")
            self.connection_label.setStyleSheet("padding: 10px; font-size: 12px; color: #2ecc71;")
        except Exception as e:
            self.connection_label.setText("🔴 Disconnected")
            self.connection_label.setStyleSheet("padding: 10px; font-size: 12px; color: #e74c3c;")
            QMessageBox.warning(
                self,
                "Connection Error",
                f"Could not connect to API at {self.api_client.base_url}\n\n"
                f"Error: {str(e)}\n\n"
                "Please ensure the API server is running."
            )
