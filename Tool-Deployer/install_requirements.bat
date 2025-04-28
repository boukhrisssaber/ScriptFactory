@echo off
setlocal enabledelayedexpansion

:: Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "CYAN=[96m"
set "NC=[0m"

:: Function to print colored messages
:print_colored
echo %~2%~1%NC%
goto :eof

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    call :print_colored "%RED%" "Error: Python is not installed. Please install Python first."
    exit /b 1
)

:: Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    call :print_colored "%RED%" "Error: pip is not installed. Please install pip first."
    exit /b 1
)

call :print_colored "%CYAN%" "Installing requirements for Tool-Deployer..."

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    call :print_colored "%RED%" "Error: requirements.txt not found!"
    exit /b 1
)

:: Install requirements
call :print_colored "%GREEN%" "Installing dependencies..."
python -m pip install -r requirements.txt

if errorlevel 1 (
    call :print_colored "%RED%" "Error installing requirements. Please check the error message above."
    exit /b 1
) else (
    call :print_colored "%GREEN%" "Requirements installed successfully!"
    call :print_colored "%CYAN%" "You can now run tool_deployer.py"
)

endlocal 