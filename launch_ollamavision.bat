@echo off
title OllamaVision GUI
echo Starting OllamaVision GUI...
echo.

REM Get the current directory (where this batch file is located)
set "CURRENT_DIR=%~dp0"
set "VENV_DIR=%CURRENT_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

REM Change to the application directory
cd /d "%CURRENT_DIR%"

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo.
    echo ✗ Virtual environment not found!
    echo Please run setup_ollamavision.bat first to set up the application
    echo.
    pause
    exit /b 1
)

REM Check if Python executable exists in venv
if not exist "%PYTHON_EXE%" (
    echo.
    echo ✗ Python executable not found in virtual environment
    echo Please run setup_ollamavision.bat to recreate the environment
    echo.
    pause
    exit /b 1
)

REM Launch the Python application using the virtual environment
echo Using virtual environment: %VENV_DIR%
"%PYTHON_EXE%" ollamavision_gui.py

REM If there's an error, show it
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error launching OllamaVision GUI
    echo Please check the error messages above
    echo.
    pause
)
