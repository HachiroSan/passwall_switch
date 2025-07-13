@echo off
REM Pass Wall Switch Startup Script
REM This script activates the virtual environment and starts the application

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Activate the virtual environment
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Start the application with pythonw (no console window)
pythonw app.pyw

REM Exit the batch file
exit 