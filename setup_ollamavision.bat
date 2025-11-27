@echo off
title OllamaVision GUI Setup
color 0A
echo.
echo ========================================
echo    OllamaVision GUI Setup Script
echo ========================================
echo.

REM Get the current directory (where this batch file is located)
set "CURRENT_DIR=%~dp0"
set "APP_NAME=OllamaVision GUI"
set "VENV_DIR=%CURRENT_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "LAUNCHER_BAT=%CURRENT_DIR%launch_ollamavision.bat"

echo Setting up OllamaVision GUI with virtual environment...
echo.

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ✗ Failed to create virtual environment
        echo Please make sure Python is installed and accessible
        echo.
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.

REM Check if Python executable exists in venv
if not exist "%PYTHON_EXE%" (
    echo ✗ Python executable not found in virtual environment
    echo Please recreate the virtual environment
    echo.
    pause
    exit /b 1
)

echo ✓ Python executable found in virtual environment
echo.

REM Check if the main Python file exists
if not exist "%CURRENT_DIR%ollamavision_gui.py" (
    echo ✗ ollamavision_gui.py not found in current directory
    echo Please make sure this script is in the same folder as ollamavision_gui.py
    echo.
    pause
    exit /b 1
)

echo ✓ Main application file found
echo.

REM Install required packages in virtual environment
echo Installing required packages...
"%PYTHON_EXE%" -m pip install --upgrade pip
if exist "%CURRENT_DIR%requirements.txt" (
    echo Using requirements.txt...
    "%PYTHON_EXE%" -m pip install -r "%CURRENT_DIR%requirements.txt"
) else (
    echo Installing basic requirements...
    "%PYTHON_EXE%" -m pip install pillow requests
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ Failed to install required packages
    echo Please check your internet connection
    echo.
    pause
    exit /b 1
)

echo ✓ Required packages installed
echo.

REM Get the desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\%APP_NAME%.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%LAUNCHER_BAT%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "OllamaVision GUI - AI Image Analysis Tool" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%PYTHON_EXE%,0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1
del "%TEMP%\CreateShortcut.vbs" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✓ Desktop shortcut created successfully!
    echo.
    echo ========================================
    echo           Setup Complete!
    echo ========================================
    echo.
    echo You can now find "%APP_NAME%" on your desktop
    echo Double-click the shortcut to launch the application
    echo.
    echo The application uses its own virtual environment
    echo Location: %CURRENT_DIR%
    echo Virtual Environment: %VENV_DIR%
    echo.
) else (
    echo ✗ Error creating desktop shortcut
    echo Please make sure you have the necessary permissions
    echo Try running this script as Administrator
    echo.
)

echo Press any key to exit...
pause >nul
