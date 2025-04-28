# Function to print colored messages
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if Python is installed
function Test-PythonInstallation {
    try {
        # Check for Python in Program Files
        $pythonPaths = @(
            "C:\Python*",
            "C:\Program Files\Python*",
            "C:\Program Files (x86)\Python*",
            "C:\Users\*\AppData\Local\Programs\Python\Python*"
        )

        $foundPython = $false
        foreach ($path in $pythonPaths) {
            $pythonDirs = Get-ChildItem -Path $path -ErrorAction SilentlyContinue
            foreach ($dir in $pythonDirs) {
                $pythonExe = Join-Path $dir.FullName "python.exe"
                if (Test-Path $pythonExe) {
                    $pythonVersion = & $pythonExe --version 2>&1
                    if ($pythonVersion -match "Python") {
                        Write-ColorOutput "Found Python at: $pythonExe" "Cyan"
                        Write-ColorOutput "Python version: $pythonVersion" "Cyan"
                        $env:PATH = "$($dir.FullName);$($dir.FullName)\Scripts;$env:PATH"
                        $foundPython = $true
                        break
                    }
                }
            }
            if ($foundPython) { break }
        }

        if (-not $foundPython) {
            Write-ColorOutput "Python is not properly installed." "Red"
            Write-ColorOutput "Please follow these steps:" "Yellow"
            Write-ColorOutput "1. Download Python from https://www.python.org/downloads/" "Yellow"
            Write-ColorOutput "2. Run the installer" "Yellow"
            Write-ColorOutput "3. IMPORTANT: Check 'Add Python to PATH' during installation" "Yellow"
            Write-ColorOutput "4. IMPORTANT: Uncheck 'Install for all users' if you don't have admin rights" "Yellow"
            Write-ColorOutput "5. Complete the installation" "Yellow"
            Write-ColorOutput "6. Close and reopen PowerShell" "Yellow"
            Write-ColorOutput "7. Run this script again" "Yellow"
            return $false
        }

        return $true
    } catch {
        Write-ColorOutput "Error checking Python installation: $_" "Red"
        return $false
    }
}

# Check if Python is installed
if (-not (Test-PythonInstallation)) {
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-ColorOutput "Creating virtual environment..." "Cyan"
    try {
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
    } catch {
        Write-ColorOutput "Failed to create virtual environment." "Red"
        Write-ColorOutput "Please follow these steps:" "Yellow"
        Write-ColorOutput "1. Open PowerShell as Administrator" "Yellow"
        Write-ColorOutput "2. Run: Set-ExecutionPolicy RemoteSigned" "Yellow"
        Write-ColorOutput "3. Run: python -m pip install --upgrade pip" "Yellow"
        Write-ColorOutput "4. Run: python -m pip install virtualenv" "Yellow"
        Write-ColorOutput "5. Run this script again" "Yellow"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-ColorOutput "Activating virtual environment..." "Cyan"
try {
    & .\venv\Scripts\Activate.ps1
} catch {
    Write-ColorOutput "Failed to activate virtual environment." "Red"
    Write-ColorOutput "Trying alternative activation method..." "Yellow"
    $env:VIRTUAL_ENV = Join-Path $PWD.Path "venv"
    $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"
    if (-not (Test-Path "$env:VIRTUAL_ENV\Scripts\python.exe")) {
        Write-ColorOutput "Virtual environment activation failed." "Red"
        Write-ColorOutput "Please try running PowerShell as Administrator and run this script again." "Yellow"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Upgrade pip
Write-ColorOutput "Upgrading pip..." "Cyan"
try {
    python -m pip install --upgrade pip
} catch {
    Write-ColorOutput "Failed to upgrade pip." "Red"
    Write-ColorOutput "Please try running PowerShell as Administrator and run this script again." "Yellow"
    Read-Host "Press Enter to exit"
    exit 1
}

# Install requirements
Write-ColorOutput "Installing dependencies..." "Green"
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install requirements"
    }
} catch {
    Write-ColorOutput "Error installing requirements. Please check the error message above." "Red"
    Write-ColorOutput "Please try running PowerShell as Administrator and run this script again." "Yellow"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorOutput "Requirements installed successfully!" "Green"
Write-ColorOutput "You can now run tool_deployer.py using the virtual environment:" "Cyan"
Write-ColorOutput ".\venv\Scripts\Activate.ps1; python tool_deployer.py" "Yellow"

# Deactivate virtual environment
deactivate

Read-Host "Press Enter to exit" 