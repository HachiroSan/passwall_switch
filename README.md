# Pass Wall Switch System Tray App

A system tray application to monitor and control Pass Wall on OpenWrt via SSH.

## Features
- Shows Pass Wall status (active, inactive, error)
- Enable/disable Pass Wall from tray menu
- Status polling (default: every 5 seconds)
- Windows notifications on status change
- Real-time IP address monitoring (external and local fallback)
- Beautiful Material Design UI with Dracula theme

## How it Works
The app connects to your OpenWrt device over SSH and runs commands to enable or disable the Pass Wall service. It checks the service status and allows you to toggle it from the system tray. For IP address monitoring, it uses external services with local IP fallback when internet is unavailable.

## Requirements
- Python 3.8+
- OpenWrt device with SSH access
- Pass Wall must be installed on the OpenWrt device
- Windows 10/11 (for system tray functionality)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd passwall_switch
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 4. Configuration
Edit `config.json` to configure your SSH connection and app settings:

```json
{
  "ssh": {
    "host": "192.168.1.1",
    "user": "root",
    "port": 22,
    "password": "your_password",
    "key_file": null
  },
  "app": {
    "theme": "dark_purple.xml",
    "poll_interval": 5
  }
}
```

**SSH Configuration Options:**
- `host`: Your OpenWrt router's IP address
- `user`: SSH username (usually "root")
- `port`: SSH port (usually 22)
- `password`: SSH password (leave null if using key file)
- `key_file`: Path to SSH private key file (leave null if using password)

**App Configuration Options:**
- `theme`: Material Design theme (e.g., "dark_purple.xml", "light_blue.xml")
- `poll_interval`: Status check interval in seconds (default: 5)

### 5. Run the Application

#### Option 1: Using the Launcher (Recommended)
```bash
# Double-click launch_app.pyw or run from command line
python launch_app.pyw
```
The launcher automatically handles virtual environment activation and dependency checking.

#### Option 2: Direct Execution
```bash
# Make sure virtual environment is activated
python app.py
```
Runs with console window for debugging.

#### Option 3: Windows Executable (No Console)
```bash
# Double-click app.pyw for no-console execution
python app.pyw
```
Runs without console window, suitable for end users.

#### Option 4: Windows Batch Launcher
```bash
# Double-click start_passwall_switch.bat
```
Alternative launcher using batch file for Windows users.

## Usage

### System Tray Menu
- **Status**: Shows current Pass Wall status
- **IP**: Shows current IP address (external or local)
- **Toggle Passwall**: Enable/disable Pass Wall service
- **Refresh IP**: Manually refresh IP address
- **Show Window**: Open the main application window
- **Quit**: Exit the application

### Main Window
The main window provides:
- Real-time status display
- Current IP address
- Manual control buttons
- Detailed log view

## Development

### Project Structure
```
passwall_switch/
├── app.py              # Main application (with console)
├── app.pyw             # Main application (no console)
├── launch_app.pyw      # Launcher with virtual environment handling
├── ssh_manager.py      # SSH communication module
├── config.py           # Configuration management
├── config.json         # Configuration file
├── requirements.txt    # Python dependencies
├── start_passwall_switch.bat  # Windows batch launcher
├── assets/             # Icons and resources
│   ├── passwall_on.svg
│   ├── passwall_off.svg
│   └── passwall_error.svg
└── README.md
```

### Key Dependencies
- **PySide6**: Qt-based GUI framework
- **paramiko**: SSH client library
- **requests**: HTTP requests for IP checking
- **qt-material**: Material Design theme support

## Building Executable (Windows)

### Using PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build single executable
pyinstaller --onefile --windowed --icon=assets/passwall.ico app.py

# The executable will be created in dist/app.exe
```

### Using PySide6 Deploy
```bash
# Install PySide6 deploy tools
pip install pyside6-deploy

# Deploy application
pyside6-deploy app.py
```

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify router IP address in config.json
   - Check SSH credentials
   - Ensure SSH is enabled on OpenWrt

2. **System Tray Not Available**
   - Restart the application
   - Check Windows system tray settings
   - Ensure running on Windows 10/11

3. **IP Address Not Showing**
   - Check internet connection
   - Verify firewall settings
   - Application will fall back to local IP if external services are unavailable

4. **Virtual Environment Issues**
   - Ensure Python 3.8+ is installed
   - Use `python -m venv venv` instead of `virtualenv`
   - Activate environment before installing dependencies

### Logs
Check the application logs in the main window for detailed error messages and troubleshooting information.

## License
This project is open source. Feel free to modify and distribute according to your needs.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests. 