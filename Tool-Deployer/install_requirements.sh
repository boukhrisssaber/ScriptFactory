#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
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

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_colored "$RED" "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

print_colored "$CYAN" "Installing requirements for Tool-Deployer..."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_colored "$RED" "Error: requirements.txt not found!"
    exit 1
fi

# Install requirements
print_colored "$GREEN" "Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_colored "$GREEN" "\nRequirements installed successfully!"
    print_colored "$CYAN" "You can now run tool_deployer.py"
else
    print_colored "$RED" "\nError installing requirements. Please check the error message above."
    exit 1
fi 