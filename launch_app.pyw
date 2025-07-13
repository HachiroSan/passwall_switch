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
        # Not in a virtual environment, try to activate it and run
        venv_activate = os.path.join(script_dir, "venv", "Scripts", "activate.bat")
        if os.path.exists(venv_activate):
            try:
                # Use the batch file to activate venv and run
                batch_path = os.path.join(script_dir, "start_passwall_switch.bat")
                if os.path.exists(batch_path):
                    subprocess.Popen([batch_path], shell=True)
                else:
                    # Fallback: try to run with venv python directly
                    venv_python = os.path.join(script_dir, "venv", "Scripts", "pythonw.exe")
                    if os.path.exists(venv_python):
                        app_path = os.path.join(script_dir, "app.pyw")
                        subprocess.Popen([venv_python, app_path], shell=True)
                    else:
                        show_error("Missing Files", "Virtual environment not found. Please ensure venv is properly set up.")
            except Exception as e:
                show_error("Error launching application", f"Could not start application: {e}")
        else:
            show_error("Missing Virtual Environment", "Virtual environment not found. Please ensure venv is properly set up.")

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