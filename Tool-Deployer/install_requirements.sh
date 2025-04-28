#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_colored "$RED" "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if python3-venv is installed
if ! dpkg -l | grep -q python3-venv; then
    print_colored "$YELLOW" "python3-venv is not installed. Installing it now..."
    sudo apt-get update && sudo apt-get install -y python3-venv
    if [ $? -ne 0 ]; then
        print_colored "$RED" "Failed to install python3-venv. Please install it manually:"
        print_colored "$YELLOW" "sudo apt-get install python3-venv"
        exit 1
    fi
fi

print_colored "$CYAN" "Installing requirements for Tool-Deployer..."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_colored "$RED" "Error: requirements.txt not found!"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_colored "$CYAN" "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_colored "$RED" "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
print_colored "$CYAN" "Activating virtual environment..."
source venv/bin/activate

# Verify we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    print_colored "$RED" "Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip
print_colored "$CYAN" "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
print_colored "$GREEN" "Installing dependencies..."
python -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_colored "$GREEN" "\nRequirements installed successfully!"
    print_colored "$CYAN" "You can now run tool_deployer.py using the virtual environment:"
    print_colored "$YELLOW" "source venv/bin/activate && python tool_deployer.py"
else
    print_colored "$RED" "\nError installing requirements. Please check the error message above."
    exit 1
fi

# Deactivate virtual environment
deactivate 