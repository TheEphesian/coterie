"""Grapevine Desktop Application - Main Entry Point."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui_desktop.main_window import MainWindow
from ui_desktop.api_client import APIClient


def main():
    """Main entry point for the desktop application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Grapevine Modern")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Grapevine")
    
    # Set application-wide stylesheet
    app.setStyle("Fusion")
    
    # Create API client
    api_client = APIClient(base_url="http://localhost:8000")
    
    # Create and show main window
    window = MainWindow(api_client)
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
