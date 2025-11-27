@echo off
echo Creating OllamaVision GUI Desktop Shortcut...
echo.

REM Get the current directory (where this batch file is located)
set "CURRENT_DIR=%~dp0"
set "LAUNCHER_BAT=%CURRENT_DIR%launch_ollamavision.bat"
set "VENV_DIR=%CURRENT_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo.
    echo ✗ Virtual environment not found!
    echo Please run setup_ollamavision.bat first to set up the application
    echo.
    pause
    exit /b 1
)

REM Check if launcher exists
if not exist "%LAUNCHER_BAT%" (
    echo.
    echo ✗ Launcher script not found!
    echo Please make sure launch_ollamavision.bat exists in the same directory
    echo.
    pause
    exit /b 1
)

REM Get the desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

REM Create the shortcut using VBScript (no admin required)
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\OllamaVision GUI.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%LAUNCHER_BAT%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "OllamaVision GUI - AI Image Analysis Tool" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%PYTHON_EXE%,0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1
del "%TEMP%\CreateShortcut.vbs" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Desktop shortcut created successfully!
    echo ✓ You can now find "OllamaVision GUI" on your desktop
    echo ✓ Double-click the shortcut to launch the application
    echo.
    echo Note: The application uses its own virtual environment
    echo Virtual Environment: %VENV_DIR%
) else (
    echo.
    echo ✗ Error creating desktop shortcut
    echo Please make sure you have the necessary permissions
)

echo.
pause
