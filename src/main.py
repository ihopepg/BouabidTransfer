"""
BouabidTransfer - Main Entry Point
Professional Windows desktop application for iPhone to PC data transfer
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.utils.logger import get_logger, BouabidLogger
from src.ui.main_window import MainWindow


def main():
    """Main application entry point"""
    # Initialize logging
    logger_instance = BouabidLogger.get_instance()
    logger = logger_instance.get_logger("BouabidTransfer")
    
    logger.info("=" * 60)
    logger.info("BouabidTransfer - Starting Application")
    logger.info("=" * 60)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("BouabidTransfer")
    app.setOrganizationName("BouabidTransfer")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run event loop
        exit_code = app.exec_()
        
        logger.info(f"Application exiting with code {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


