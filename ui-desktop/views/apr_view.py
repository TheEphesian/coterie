"""APR (Actions, Plots, Rumors) View."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QMessageBox, QAbstractItemView, QTextEdit,
    QSpinBox, QDialog, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt

from ui_desktop.api_client import APIClient


class APRView(QWidget):
    """View for managing Actions, Plots, and Rumors."""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.actions = []
        self.plots = []
        self.rumors = []
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Actions, Plots & Rumors")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
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
        
        # Actions Tab
        self.actions_tab = self._create_actions_tab()
        self.tabs.addTab(self.actions_tab, "Actions")
        
        # Plots Tab
        self.plots_tab = self._create_plots_tab()
        self.tabs.addTab(self.plots_tab, "Plots")
        
        # Rumors Tab
        self.rumors_tab = self._create_rumors_tab()
        self.tabs.addTab(self.rumors_tab, "Rumors")
        
        layout.addWidget(self.tabs)
    
    def _create_actions_tab(self) -> QWidget:
        """Create the actions tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        self.action_search = QLineEdit()
        self.action_search.setPlaceholderText("Search actions...")
        self.action_search.textChanged.connect(self._filter_actions)
        header.addWidget(self.action_search, stretch=2)
        
        create_btn = QPushButton("➕ New Action")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        create_btn.clicked.connect(self._create_action)
        header.addWidget(create_btn)
        
        layout.addLayout(header)
        
        # Actions table
        self.actions_table = QTableWidget()
        self.actions_table.setColumnCount(6)
        self.actions_table.setHorizontalHeaderLabels([
            "Date", "Character", "Type", "Level", "Total", "Actions"
        ])
        self.actions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.actions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.actions_table.setAlternatingRowColors(True)
        self.actions_table.setStyleSheet(self._table_style())
        
        layout.addWidget(self.actions_table)
        
        self.actions_status = QLabel("Loading...")
        layout.addWidget(self.actions_status)
        
        return widget
    
    def _create_plots_tab(self) -> QWidget:
        """Create the plots tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        self.plot_search = QLineEdit()
        self.plot_search.setPlaceholderText("Search plots...")
        self.plot_search.textChanged.connect(self._filter_plots)
        header.addWidget(self.plot_search, stretch=2)
        
        create_btn = QPushButton("➕ New Plot")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        create_btn.clicked.connect(self._create_plot)
        header.addWidget(create_btn)
        
        layout.addLayout(header)
        
        # Plots table
        self.plots_table = QTableWidget()
        self.plots_table.setColumnCount(4)
        self.plots_table.setHorizontalHeaderLabels([
            "Title", "Status", "Description", "Actions"
        ])
        self.plots_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.plots_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.plots_table.setAlternatingRowColors(True)
        self.plots_table.setStyleSheet(self._table_style())
        
        layout.addWidget(self.plots_table)
        
        self.plots_status = QLabel("Loading...")
        layout.addWidget(self.plots_status)
        
        return widget
    
    def _create_rumors_tab(self) -> QWidget:
        """Create the rumors tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        self.rumor_search = QLineEdit()
        self.rumor_search.setPlaceholderText("Search rumors...")
        self.rumor_search.textChanged.connect(self._filter_rumors)
        header.addWidget(self.rumor_search, stretch=2)
        
        create_btn = QPushButton("➕ New Rumor")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        create_btn.clicked.connect(self._create_rumor)
        header.addWidget(create_btn)
        
        layout.addLayout(header)
        
        # Rumors table
        self.rumors_table = QTableWidget()
        self.rumors_table.setColumnCount(6)
        self.rumors_table.setHorizontalHeaderLabels([
            "Date", "Title", "Level", "Category", "Target", "Actions"
        ])
        self.rumors_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rumors_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rumors_table.setAlternatingRowColors(True)
        self.rumors_table.setStyleSheet(self._table_style())
        
        layout.addWidget(self.rumors_table)
        
        self.rumors_status = QLabel("Loading...")
        layout.addWidget(self.rumors_status)
        
        return widget
    
    def _table_style(self) -> str:
        """Get table stylesheet."""
        return """
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
        """
    
    def refresh(self):
        """Refresh all APR data."""
        self._load_actions()
        self._load_plots()
        self._load_rumors()
    
    def _load_actions(self):
        """Load actions from API."""
        try:
            self.actions = self.api_client.get_actions()
            self._filter_actions()
            self.actions_status.setText(f"{len(self.actions)} actions")
        except Exception as e:
            self.actions_status.setText(f"Error: {str(e)}")
    
    def _load_plots(self):
        """Load plots from API."""
        try:
            self.plots = self.api_client.get_plots()
            self._filter_plots()
            self.plots_status.setText(f"{len(self.plots)} plots")
        except Exception as e:
            self.plots_status.setText(f"Error: {str(e)}")
    
    def _load_rumors(self):
        """Load rumors from API."""
        try:
            self.rumors = self.api_client.get_rumors()
            self._filter_rumors()
            self.rumors_status.setText(f"{len(self.rumors)} rumors")
        except Exception as e:
            self.rumors_status.setText(f"Error: {str(e)}")
    
    def _filter_actions(self):
        """Filter actions based on search."""
        search = self.action_search.text().lower()
        filtered = [
            a for a in self.actions
            if search in a.get("action_type", "").lower()
            or search in (a.get("character_name") or "").lower()
        ]
        self._update_actions_table(filtered)
    
    def _filter_plots(self):
        """Filter plots based on search."""
        search = self.plot_search.text().lower()
        filtered = [
            p for p in self.plots
            if search in p.get("title", "").lower()
            or search in (p.get("description") or "").lower()
        ]
        self._update_plots_table(filtered)
    
    def _filter_rumors(self):
        """Filter rumors based on search."""
        search = self.rumor_search.text().lower()
        filtered = [
            r for r in self.rumors
            if search in r.get("title", "").lower()
            or search in (r.get("content") or "").lower()
        ]
        self._update_rumors_table(filtered)
    
    def _update_actions_table(self, actions: list):
        """Update actions table."""
        self.actions_table.setRowCount(len(actions))
        for row, action in enumerate(actions):
            self.actions_table.setItem(row, 0, QTableWidgetItem(action.get("action_date", "")))
            self.actions_table.setItem(row, 1, QTableWidgetItem(action.get("character_name") or "-"))
            self.actions_table.setItem(row, 2, QTableWidgetItem(action.get("action_type", "")))
            self.actions_table.setItem(row, 3, QTableWidgetItem(str(action.get("level", 0))))
            self.actions_table.setItem(row, 4, QTableWidgetItem(str(action.get("total", 0))))
    
    def _update_plots_table(self, plots: list):
        """Update plots table."""
        self.plots_table.setRowCount(len(plots))
        for row, plot in enumerate(plots):
            self.plots_table.setItem(row, 0, QTableWidgetItem(plot.get("title", "")))
            self.plots_table.setItem(row, 1, QTableWidgetItem(plot.get("status", "").title()))
            desc = plot.get("description", "")
            self.plots_table.setItem(row, 2, QTableWidgetItem(desc[:50] + "..." if len(desc) > 50 else desc))
    
    def _update_rumors_table(self, rumors: list):
        """Update rumors table."""
        self.rumors_table.setRowCount(len(rumors))
        for row, rumor in enumerate(rumors):
            self.rumors_table.setItem(row, 0, QTableWidgetItem(rumor.get("rumor_date", "")))
            self.rumors_table.setItem(row, 1, QTableWidgetItem(rumor.get("title", "")))
            self.rumors_table.setItem(row, 2, QTableWidgetItem(str(rumor.get("level", 1))))
            self.rumors_table.setItem(row, 3, QTableWidgetItem(rumor.get("category") or "-"))
            self.rumors_table.setItem(row, 4, QTableWidgetItem(rumor.get("target_race") or "All"))
    
    def _create_action(self):
        """Open dialog to create action."""
        QMessageBox.information(self, "Coming Soon", "Action creation dialog coming soon!")
    
    def _create_plot(self):
        """Open dialog to create plot."""
        dialog = PlotDialog(self.api_client, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_plots()
    
    def _create_rumor(self):
        """Open dialog to create rumor."""
        QMessageBox.information(self, "Coming Soon", "Rumor creation dialog coming soon!")


class PlotDialog(QDialog):
    """Dialog for creating/editing a plot."""
    
    def __init__(self, api_client: APIClient, plot: dict = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.plot = plot
        self.setWindowTitle("Edit Plot" if plot else "New Plot")
        self.setMinimumWidth(500)
        self._build_ui()
        
        if plot:
            self._populate_form()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Plot Title")
        form_layout.addRow("Title:", self.title_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItem("Active", "active")
        self.status_combo.addItem("Completed", "completed")
        self.status_combo.addItem("Inactive", "inactive")
        form_layout.addRow("Status:", self.status_combo)
        
        # Description
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Plot description...")
        self.description_text.setMinimumHeight(150)
        form_layout.addRow("Description:", self.description_text)
        
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
        """Populate form with plot data."""
        if not self.plot:
            return
        
        self.title_input.setText(self.plot.get("title", ""))
        
        status = self.plot.get("status", "active")
        index = self.status_combo.findData(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        self.description_text.setText(self.plot.get("description") or "")
    
    def _save(self):
        """Save the plot."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            return
        
        data = {
            "title": title,
            "status": self.status_combo.currentData(),
            "description": self.description_text.toPlainText() or None,
        }
        
        try:
            if self.plot:
                self.api_client.patch(f"/api/v1/apr/plots/{self.plot['id']}", data)
            else:
                self.api_client.create_plot(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save plot: {str(e)}")
