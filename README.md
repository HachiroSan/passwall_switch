# Passwall Switch System Tray App

A simple, beautiful, and efficient system tray application to monitor and control your Passwall service on OpenWrt via SSH.

## Features
- System tray icon shows Passwall status (active, inactive, error)
- Right-click menu to enable/disable Passwall and quit
- Automatic status polling every 3 seconds
- Material Design (Dracula theme)

## Requirements
- Python 3.8+
- OpenWrt device with SSH access

## Installation
1. Clone this repository.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the app:
   ```bash
   python app.py
   ```
2. The app will appear in your system tray.
3. On first run, a `config.json` file will be created with default settings.

## Configuration
The app uses a `config.json` file for settings:
```json
{
    "ssh": {
        "host": "192.168.1.1",
        "user": "root",
        "port": 22,
        "password": null,
        "key_file": null
    },
    "app": {
        "poll_interval": 3,
        "theme": "dark_teal.xml"
    }
}
```

### SSH Authentication Options:
- **Passwordless (default)**: Uses SSH key authentication (recommended)
- **Password**: Set `"password": "your_password"` in config.json
- **Key file**: Set `"key_file": "/path/to/private/key"` in config.json

**Security Note**: If using password authentication, ensure config.json has proper file permissions (600).

## Packaging (Optional)
To create a standalone executable (e.g., for Windows):
```bash
pip install pyinstaller
pyinstaller --onefile --windowed app.py
```

## License
MIT 