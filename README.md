# Passwall Switch System Tray App

A system tray application to monitor and control Passwall on OpenWrt via SSH.

## Features
- Shows Passwall status (active, inactive, error)
- Enable/disable Passwall from tray menu
- Status polling (default: every 60 seconds)
- Windows notifications on status change

## Note
This app communicates with Passwall using SSH commands, not JSON-RPC, to keep things simple.

## How it Works
The app connects to your OpenWrt device over SSH and runs commands to enable or disable the Passwall service. It checks the service status and allows you to toggle it from the system tray.

## Requirements
- Python 3.8+
- OpenWrt device with SSH access
- Passwall must be installed on the OpenWrt device

## Setup
1. Clone the repository.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Edit `config.json` for SSH and app settings.

## Run
```
python app.py
```

## Deploy (Windows)
```
pip install pyside6-deploy
pyside6-deploy app.py
``` 