#!/usr/bin/env python3
"""Desktop UI entry point for Coterie."""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.core.engine import init_db


def main():
    """Run the desktop UI application."""
    app = QApplication(sys.argv)
    
    # Initialize database
    init_db()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
