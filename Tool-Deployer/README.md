# Tool Deployer

The Tool Deployer script is part of the **ScriptFactory** project and is designed to automate the installation and setup of tools from GitHub repositories. It simplifies the process by handling dependency installation, executable detection, and creating symlinks for easy usage.

## Features
- Clone and install tools from GitHub repositories with ease.
- Automated dependency detection and installation.
- Intelligent executable detection with user-friendly prompts.
- Creates symlinks for easy access to installed tools.

## Why Use Tool Deployer?
- 🚀 **Quick Deployments**: Automates tool setup from GitHub repositories.
- 🛠️ **No Hassle**: Detects and installs dependencies effortlessly.
- 🔗 **Convenience**: Creates symlinks for easy access.

## FAQ
**Q: What if no executable is detected in the repository?**  
A: Ensure the repository contains scripts or executables. You can manually specify dependencies or use the detected path.

**Q: How do I uninstall a tool?**  
A: Delete the tool's directory in `~/tools` and its symlink in `~/bin`.

## Usage
Run the `tool_deployer.py` script from the project directory:
```bash
python3 tool_deployer.py
```

### Steps:
1. Enter the GitHub repository URL of the tool to deploy.
2. Specify a name for the tool (or use the default detected name).
3. Follow the prompts to detect dependencies and select executables.

### Requirements
- Python 3.6 or higher
- `pip` for managing dependencies
- Git installed on your machine

## Example
Install a sample tool from GitHub:
```bash
python3 tool_deployer.py
# Follow the prompts to install and configure the tool.
```

## Troubleshooting
- Ensure Python and Git are installed and available in your system PATH.
- If dependencies fail to install, manually check the `requirements.txt` file in the tool's directory.

## Author
- W1SEBYT3S, part of the **Securas SAS** team.
