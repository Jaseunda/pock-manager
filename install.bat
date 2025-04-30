@echo off
setlocal enabledelayedexpansion

:: Colors for output
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "NC=[0m"

:: Function to print colored messages
call :print_message "Starting Pockage installation..."

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%Python is not installed. Please install Python 3.7 or higher.%NC%
        exit /b 1
    )
    set "PYTHON_CMD=python3"
) else (
    set "PYTHON_CMD=python"
)

:: Check Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set "PYTHON_VERSION=%%i"
if %PYTHON_VERSION% LSS 3.7 (
    echo %RED%Python version must be 3.7 or higher. Current version: %PYTHON_VERSION%%NC%
    exit /b 1
)

:: Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    pip3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo %YELLOW%pip is not installed. Installing pip...%NC%
        curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
        %PYTHON_CMD% get-pip.py
        del get-pip.py
    )
)

:: Create temporary directory
set "TEMP_DIR=%TEMP%\pockage-install"
mkdir "%TEMP_DIR%" 2>nul
cd /d "%TEMP_DIR%"

:: Download Pockage
echo %GREEN%Downloading Pockage...%NC%
curl -L -o pockage.zip https://github.com/Jaseunda/pockage/archive/refs/heads/main.zip

:: Extract and install
echo %GREEN%Installing...%NC%
powershell -Command "Expand-Archive -Path pockage.zip -DestinationPath ."
cd pockage-main

:: Install dependencies and Pockage
%PYTHON_CMD% -m pip install -e .

:: Clean up
cd ..
rmdir /s /q "%TEMP_DIR%"

:: Add to PATH
set "PYTHON_SCRIPTS=%APPDATA%\Python\Python%PYTHON_VERSION:~0,1%%PYTHON_VERSION:~2,1%\Scripts"
setx PATH "%PATH%;%PYTHON_SCRIPTS%"

echo %GREEN%Pockage installed successfully!%NC%
echo %GREEN%Please restart your terminal to use Pockage.%NC%

exit /b 0

:print_message
echo %GREEN%[Pockage]%NC% %~1
exit /b 0 