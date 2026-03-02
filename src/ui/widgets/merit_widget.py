from typing import Dict, List, Tuple, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QMenu,
    QInputDialog, QMessageBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QAction


class MeritWidget(QWidget):
    """
    Widget for displaying and managing merits with point costs.
    
    Each merit has a name and a point cost (trait_cost).
    """
    
    meritsChanged = pyqtSignal(list)  # Emitted when merits are modified
    
    def __init__(self, title: str = "Merits", parent: Optional[QWidget] = None):
        """
        Initialize the merit widget.
        
        Args:
            title (str): The title for the merit section
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.merits: List[Tuple[str, int]] = []  # List of (merit_name, point_cost)
        self.available_merits: Dict[str, Dict] = {}
        
        self._setup_ui()
        self._populate_merits()
        
    def _setup_ui(self):
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(self.title)
        label.setObjectName("merit_label")
        layout.addWidget(label)
        
        self.merit_list_widget = QListWidget()
        layout.addWidget(self.merit_list_widget)
        
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Merit")
        self.add_btn.clicked.connect(self._show_add_menu)
        btn_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self._remove_selected_merit)
        btn_layout.addWidget(self.remove_btn)
        
        layout.addLayout(btn_layout)
    
    def _populate_merits(self):
        """Populate the merit list with existing merits."""
        self.merit_list_widget.clear()
        for merit_name, point_cost in self.merits:
            item_text = f"{merit_name} ({point_cost} pts)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, (merit_name, point_cost))
            self.merit_list_widget.addItem(item)
    
    def set_available_merits(self, merits: Dict[str, List[Dict]]) -> None:
        """Set available merits grouped by category.
        
        Args:
            merits: Dictionary of category -> list of merit dicts with 'name' and 'trait_cost'
        """
        self.available_merits = merits
        if merits:
            self.add_btn.setMenu(self._create_add_menu())
        else:
            self.add_btn.setMenu(None)
    
    def _create_add_menu(self) -> QMenu:
        """Create a menu with available merits for adding."""
        menu = QMenu(self)
        
        for category, merit_list in self.available_merits.items():
            category_menu = menu.addMenu(category)
            for merit in merit_list:
                merit_name = merit.get('name', '')
                trait_cost = merit.get('trait_cost', 1)
                action = QAction(f"{merit_name} ({trait_cost} pts)", self)
                action.triggered.connect(
                    lambda checked, m=merit_name, c=trait_cost: self._add_merit(m, c)
                )
                category_menu.addAction(action)
            category_menu.addSeparator()
        
        custom_action = QAction("Enter Custom...", self)
        custom_action.triggered.connect(self._add_custom_merit)
        menu.addAction(custom_action)
        
        return menu
    
    def _show_add_menu(self):
        """Show the add merit menu."""
        if self.available_merits:
            menu = self._create_add_menu()
            menu.exec(self.add_btn.mapToGlobal(self.add_btn.rect().bottomLeft()))
        else:
            self._add_custom_merit()
    
    def _add_merit(self, name: str, cost: int) -> None:
        """Add a merit with the given name and cost."""
        self.merits.append((name, cost))
        self._populate_merits()
        self.meritsChanged.emit(self.merits)
    
    def _add_custom_merit(self) -> None:
        """Add a custom merit through user input."""
        name, ok_name = QInputDialog.getText(
            self,
            f"Add {self.title}",
            "Enter merit name:"
        )
        
        if not ok_name or not name:
            return
        
        cost, ok_cost = QInputDialog.getInt(
            self,
            f"Add {self.title}",
            "Enter point cost:",
            value=1,
            min=1,
            max=10
        )
        
        if ok_cost:
            self._add_merit(name, cost)
    
    def _remove_selected_merit(self):
        """Remove the currently selected merit."""
        current_item = self.merit_list_widget.currentItem()
        if not current_item:
            return
        
        row = self.merit_list_widget.currentRow()
        self.merit_list_widget.takeItem(row)
        self.merits.pop(row)
        self.meritsChanged.emit(self.merits)
    
    def get_merits(self) -> List[Tuple[str, int]]:
        """Get the list of merits with their point costs.
        
        Returns:
            List of tuples (merit_name, point_cost)
        """
        return self.merits
    
    def set_merits(self, merits: List[Tuple[str, int]]) -> None:
        """Set the merits list.
        
        Args:
            merits: List of tuples (merit_name, point_cost)
        """
        self.merits = merits
        self._populate_merits()
