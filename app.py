

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QFrame
)
from PySide6.QtGui import QIcon, QAction, QColor, QPalette
from PySide6.QtCore import QThread, Signal, QTimer, Qt, Slot
from PySide6.QtSvgWidgets import QSvgWidget
from qt_material import apply_stylesheet
from ssh_manager import PasswallManager
from config import Config


class MainWindow(QMainWindow):
    """
    Main application window. Emits signals for user actions.
    """
    toggle_requested = Signal()
    refresh_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Passwall Switch Dashboard")
        self.setMinimumSize(400, 300)

        # --- UI Elements ---
        self.status_indicator = QLabel("Unknown")
        self.status_indicator.setFrameShape(QFrame.StyledPanel)
        self.status_indicator.setAlignment(Qt.AlignCenter)

        self.toggle_button = QPushButton("Toggle Passwall")
        self.refresh_button = QPushButton("Refresh Status")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        # Set monospace font for better log alignment
        font = self.log_view.font()
        font.setFamily("Consolas, Courier, monospace")
        self.log_view.setFont(font)

        # --- Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Current Status:"))
        status_layout.addWidget(self.status_indicator)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.toggle_button)
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(status_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Logs:"))
        main_layout.addWidget(self.log_view)

        # --- Connections ---
        self.toggle_button.clicked.connect(self.toggle_requested)
        self.refresh_button.clicked.connect(self.refresh_requested)

    @Slot(str)
    def log(self, message):
        """Append a timestamped message to the log view with proper wrapping alignment."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] "
        # Split message into lines if it contains newlines
        lines = message.splitlines()
        formatted_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                formatted_lines.append(f"{prefix}{line}")
            else:
                formatted_lines.append(f"{' ' * len(prefix)}{line}")
        formatted_message = "\n".join(formatted_lines)
        self.log_view.append(formatted_message)

    @Slot(str)
    def update_status_ui(self, status):
        """Update the UI elements based on the new status."""
        status_descriptions = {
            "active": "Passwall service is currently ACTIVE and running",
            "inactive": "Passwall service is currently INACTIVE and stopped", 
            "error": "ERROR: Unable to determine Passwall service status",
            "unknown": "UNKNOWN: Service status has not been determined yet"
        }
        
        description = status_descriptions.get(status, f"Status changed to: {status.upper()}")
        self.log(f"STATUS UPDATE: {description}")
        self.status_indicator.setText(status.capitalize())

        palette = self.status_indicator.palette()
        if status == "active":
            palette.setColor(QPalette.Window, QColor("green"))
            self.toggle_button.setText("Disable Passwall")
        elif status == "inactive":
            palette.setColor(QPalette.Window, QColor("red"))
            self.toggle_button.setText("Enable Passwall")
        else: # error
            palette.setColor(QPalette.Window, QColor("orange"))
            self.toggle_button.setText("Toggle Passwall")
        self.status_indicator.setPalette(palette)
        self.status_indicator.setAutoFillBackground(True)

    def closeEvent(self, event):
        """Override the close event to hide the window instead of quitting."""
        event.ignore()
        self.hide()


class StatusWorker(QThread):
    """
    Performs all SSH operations in a background thread.
    """
    status_updated = Signal(str)
    log_message = Signal(str)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.running = True
        self.poll_interval = 5  # Default, can be overridden

    @Slot()
    def check_status(self):
        """Perform a single status check and emit the result."""
        self.log_message.emit("INFO: Initiating status check - connecting to OpenWrt router via SSH...")
        status = self.manager.get_status()
        
        if status == "error":
            self.log_message.emit("ERROR: Failed to retrieve Passwall service status from router")
        elif status == "active":
            self.log_message.emit("SUCCESS: Passwall service status check completed - service is ACTIVE")
        elif status == "inactive":
            self.log_message.emit("SUCCESS: Passwall service status check completed - service is INACTIVE")
        else:
            self.log_message.emit(f"INFO: Passwall service status check completed - status: {status.upper()}")
            
        self.status_updated.emit(status)

    @Slot(str)
    def request_toggle(self, current_status):
        """Toggle the service in the background and then check status."""
        action = "STOP" if current_status == "active" else "START"
        self.log_message.emit(f"INFO: Initiating Passwall service toggle operation - attempting to {action} service (current state: {current_status.upper()})")
        
        result = self.manager.toggle_service(current_status)
        
        if result == "error":
            self.log_message.emit(f"ERROR: Failed to {action.lower()} Passwall service - SSH command execution failed")
        else:
            self.log_message.emit(f"SUCCESS: Passwall service {action.lower()} command sent successfully to router")
            
        # After toggling, always check the actual status to be sure
        self.log_message.emit("INFO: Verifying service state change by performing status check...")
        self.check_status()

    def run(self):
        """Main thread loop: poll status at configured interval."""
        self.log_message.emit(f"INFO: Background status monitoring started - polling interval: {self.poll_interval} seconds")
        while self.running:
            self.check_status()
            self.sleep(self.poll_interval)

    def stop(self):
        """Stop the thread and wait for it to finish."""
        self.log_message.emit("INFO: Stopping background status monitoring thread...")
        self.running = False
        self.wait()
        self.log_message.emit("INFO: Background status monitoring thread stopped successfully")


class PasswallTrayApp(QApplication):
    """
    Main application controller.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_status = "unknown"

        # Load configuration
        self.config = Config()
        apply_stylesheet(self, theme=self.config.get('app.theme'))

        # Initialize SSH manager (but don't connect yet)
        self.manager = PasswallManager(
            host=self.config.get('ssh.host'),
            user=self.config.get('ssh.user'),
            port=self.config.get('ssh.port'),
            password=self.config.get('ssh.password'),
            key_file=self.config.get('ssh.key_file')
        )

        # Setup UI and Worker
        self.window = MainWindow()
        self.worker = StatusWorker(self.manager)
        poll_interval = self.config.get('app.poll_interval')
        self.worker.poll_interval = poll_interval if poll_interval is not None else 5

        # Connect signals and slots
        self.worker.status_updated.connect(self.update_status)
        self.worker.log_message.connect(self.window.log)
        self.window.refresh_requested.connect(self.worker.check_status)
        self.window.toggle_requested.connect(self.handle_toggle_request)

        # Setup Tray Icon
        self._setup_tray_icon()
        self._load_icons()
        self.tray_icon.setIcon(self.icons["error"])
        self.tray_icon.show()

        # Start background worker and show window
        self.worker.start()
        self.window.show()

    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("Passwall Switch")
        self.menu = QMenu()
        self.status_action = QAction("Status: Unknown")
        self.status_action.setEnabled(False)
        self.toggle_action = QAction("Toggle Passwall")
        self.toggle_action.triggered.connect(self.handle_toggle_request)
        self.show_action = QAction("Show Window")
        self.show_action.triggered.connect(self.window.show)
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.quit_app)
        
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        self.menu.addAction(self.toggle_action)
        self.menu.addAction(self.show_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.menu)

    def _load_icons(self):
        """Load icons from the assets directory."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_path, "assets")
        self.icons = {
            "active": QIcon(os.path.join(assets_path, "passwall_on.svg")),
            "inactive": QIcon(os.path.join(assets_path, "passwall_off.svg")),
            "error": QIcon(os.path.join(assets_path, "passwall_error.svg"))
        }

    @Slot()
    def handle_toggle_request(self):
        """Pass the toggle request to the worker thread with the current status."""
        self.worker.request_toggle(self.current_status)

    @Slot(str)
    def update_status(self, status):
        """Update state and all UI elements with the new status."""
        self.current_status = status
        self.window.update_status_ui(status)
        self.status_action.setText(f"Status: {status.capitalize()}")
        
        icon = self.icons.get(status, self.icons["error"])
        self.tray_icon.setIcon(icon)

        if status == "active":
            self.toggle_action.setText("Disable Passwall")
            self.tray_icon.showMessage(
                "Passwall Switch",
                "Passwall has been activated and is now running.",
                QSystemTrayIcon.Information
            )
        elif status == "inactive":
            self.toggle_action.setText("Enable Passwall")
            self.tray_icon.showMessage(
                "Passwall Switch",
                "Passwall has been deactivated and is now stopped.",
                QSystemTrayIcon.Information
            )
        elif status == "error":
            self.tray_icon.showMessage(
                "Passwall Switch",
                "Failed to connect or retrieve status.",
                QSystemTrayIcon.Critical
            )

    def run(self):
        """Start the Qt event loop."""
        sys.exit(self.exec())

    def quit_app(self):
        """Cleanly stop background thread, close SSH, and quit app."""
        self.window.log("Quitting application...")
        self.worker.stop()
        self.manager.close()
        self.quit()


if __name__ == "__main__":
    app = PasswallTrayApp(sys.argv)
    app.run()
