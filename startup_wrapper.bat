@echo off
REM Pass Wall Switch Startup Wrapper
REM This script adds a delay before starting the application to ensure system tray is ready

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Wait for system to fully boot (30 seconds)
timeout /t 30 /nobreak >nul

REM Start the compiled executable
start "" "%SCRIPT_DIR%app.exe"

REM Exit the batch file
exit 