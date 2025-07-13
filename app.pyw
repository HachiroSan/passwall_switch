#!/usr/bin/env python3
"""
Pass Wall Switch - System Tray Application
Runs without console window when double-clicked
"""

import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if we're in a virtual environment and handle dependencies
def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import PySide6
        import paramiko
        import qt_material
        return True
    except ImportError as e:
        return False, str(e)

# Import and run the main application
if __name__ == "__main__":
    try:
        # Check dependencies first
        deps_ok = check_dependencies()
        if deps_ok is not True:
            # Dependencies missing - show error dialog
            try:
                from PySide6.QtWidgets import QApplication, QMessageBox
                from PySide6.QtCore import QTimer
                
                app = QApplication(sys.argv)
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Pass Wall Switch - Missing Dependencies")
                msg.setText("Required dependencies are not available.")
                msg.setDetailedText(f"Error: {deps_ok[1]}\n\nPlease ensure the virtual environment is activated or dependencies are installed.")
                msg.setStandardButtons(QMessageBox.Ok)
                
                # Auto-close after 15 seconds
                timer = QTimer()
                timer.timeout.connect(msg.close)
                timer.start(15000)
                
                msg.exec()
                sys.exit(1)
            except:
                sys.exit(1)
        
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
            msg.setWindowTitle("Pass Wall Switch Error")
            msg.setText("An error occurred while starting Pass Wall Switch:")
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