#!/usr/bin/env python3
"""
Passwall Switch - System Tray Application
Runs without console window when double-clicked
"""

import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
if __name__ == "__main__":
    try:
        from app import PasswallTrayApp
        
        # Create and run the application
        app = PasswallTrayApp(sys.argv)
        app.run()
        
    except Exception as e:
        # In case of errors, we can't show console, so we'll create a simple error dialog
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            from PySide6.QtCore import QTimer
            
            app = QApplication(sys.argv)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Passwall Switch Error")
            msg.setText("An error occurred while starting Passwall Switch:")
            msg.setDetailedText(str(e))
            msg.setStandardButtons(QMessageBox.Ok)
            
            # Auto-close after 10 seconds if user doesn't click OK
            timer = QTimer()
            timer.timeout.connect(msg.close)
            timer.start(10000)
            
            msg.exec()
        except:
            # If even the error dialog fails, we can't do much more
            pass 