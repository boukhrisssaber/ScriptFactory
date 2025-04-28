import subprocess
import sys
import os
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init()

def print_colored(message, color=Fore.WHITE):
    """Print a colored message"""
    print(f"{color}{message}{Style.RESET_ALL}")

def install_requirements():
    """Install requirements from requirements.txt"""
    print_colored("Installing requirements for Tool-Deployer...", Fore.CYAN)
    
    try:
        # Get the path to requirements.txt
        requirements_path = "requirements.txt"
        
        # Check if requirements.txt exists
        if not os.path.exists(requirements_path):
            print_colored("Error: requirements.txt not found!", Fore.RED)
            sys.exit(1)
            
        # Install requirements with progress bar
        print_colored("Installing dependencies...", Fore.GREEN)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)
        
        print_colored("\nRequirements installed successfully!", Fore.GREEN)
        print_colored("You can now run tool_deployer.py", Fore.CYAN)
        
    except subprocess.CalledProcessError as e:
        print_colored(f"Error installing requirements: {e}", Fore.RED)
        sys.exit(1)
    except Exception as e:
        print_colored(f"An unexpected error occurred: {e}", Fore.RED)
        sys.exit(1)

if __name__ == "__main__":
    install_requirements() 