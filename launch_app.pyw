#!/usr/bin/env python3
"""
Simple launcher for Pass Wall Switch
This script can be double-clicked to run the app with proper virtual environment
"""

import sys
import os
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Already in a virtual environment, run the app directly
        try:
            from app import PasswallTrayApp
            app = PasswallTrayApp(sys.argv)
            app.run()
        except Exception as e:
            show_error("Error starting application", str(e))
    else:
        # Not in a virtual environment, use the batch file
        batch_path = os.path.join(script_dir, "start_passwall_switch.bat")
        if os.path.exists(batch_path):
            try:
                subprocess.Popen([batch_path], shell=True)
            except Exception as e:
                show_error("Error launching application", f"Could not start batch file: {e}")
        else:
            show_error("Missing Files", "start_passwall_switch.bat not found. Please ensure all files are in the same directory.")

def show_error(title, message):
    """Show an error dialog."""
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        from PySide6.QtCore import QTimer
        
        app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Auto-close after 10 seconds
        timer = QTimer()
        timer.timeout.connect(msg.close)
        timer.start(10000)
        
        msg.exec()
    except:
        # If even the error dialog fails, we can't do much more
        pass

if __name__ == "__main__":
    main() 