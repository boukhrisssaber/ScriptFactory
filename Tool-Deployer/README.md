# Tool Deployer

The Tool Deployer script is part of the **ScriptFactory** project and is designed to automate the installation and setup of tools from GitHub repositories. It simplifies the process by handling dependency installation, executable detection, and creating symlinks for easy usage.

## Features
- Clone and install tools from GitHub repositories with ease.
- Automated dependency detection and installation.
- Intelligent executable detection with user-friendly prompts.
- Creates symlinks for easy access to installed tools.
- Colored output and progress bars for better user experience.
- Quiet mode for automation and scripting.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/boukhrisssaber/ScriptFactory.git
cd ScriptFactory/Tool-Deployer
```

2. Install the requirements using one of the following methods:

### For Unix-like systems (Linux/macOS):
```bash
# Make the script executable
chmod +x install_requirements.sh
# Run the script
./install_requirements.sh
```

The script will:
- Check for and install python3-venv if needed
- Create a virtual environment
- Install all required dependencies in the virtual environment

### For Windows:
```batch
# Run the batch script
install_requirements.bat
```

### Manual installation:
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## Usage
To run the tool, first activate the virtual environment:

```bash
# On Unix-like systems
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

Then run the tool:
```bash
python tool_deployer.py
```

### Command Line Options
- `-q` or `--quiet`: Run in quiet mode (no output)
- `--no-color`: Disable colored output
- `-v` or `--verbose`: Enable verbose output

### Steps:
1. Enter the GitHub repository URL of the tool to deploy.
2. Specify a name for the tool (or use the default detected name).
3. Follow the prompts to detect dependencies and select executables.

### Requirements
- Python 3.6 or higher
- `pip` for managing dependencies
- Git installed on your machine
- python3-venv (for Unix-like systems)

## Example
Install a sample tool from GitHub:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the tool
python tool_deployer.py
# Follow the prompts to install and configure the tool.
```

## Troubleshooting
- Ensure Python and Git are installed and available in your system PATH.
- If dependencies fail to install, manually check the `requirements.txt` file in the tool's directory.
- Run the appropriate installation script for your system to reinstall dependencies if needed.
- If you get "externally-managed-environment" errors, make sure you're using the virtual environment.

## Author
- Saber Boukhriss, CyberSecurity enthusiast.