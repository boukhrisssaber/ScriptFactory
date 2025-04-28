import os, sys, subprocess, re, time, platform
from tqdm import tqdm
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init()

# Define the static ASCII banner
banner = """
 __________  ____  __     ___  _______  __   ______  _________ 
/_  __/ __ \/ __ \/ /    / _ \/ __/ _ \/ /  / __ \ \/ / __/ _ \\
 / / / /_/ / /_/ / /__  / // / _// ___/ /__/ /_/ /\  / _// , _/
/_/  \____/\____/____/ /____/___/_/  /____/\____/ /_/___/_/|_|                                                             TOOL DEPLOYER v1.0.0
"""

class Config:
    """Configuration class for user experience settings"""
    def __init__(self):
        self.quiet = False
        self.no_color = False
        self.verbose = False

    def print(self, message, color=Fore.WHITE, end='\n'):
        """Print message with color if enabled"""
        if not self.quiet:
            if self.no_color:
                print(message, end=end)
            else:
                print(f"{color}{message}{Style.RESET_ALL}", end=end)

    def progress(self, iterable, desc=None):
        """Create a progress bar if not in quiet mode"""
        if self.quiet:
            return iterable
        return tqdm(iterable, desc=desc, disable=self.quiet)

# Global configuration
config = Config()

def show_banner():
    """Displays the banner to the user."""
    if not config.quiet:
        print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
        print(f"\t\t{Fore.GREEN}ScriptFactory by W1SEBYT3S{Style.RESET_ALL}")
        print(f"\t{Fore.BLUE}https://github.com/boukhrisssaber/ScriptFactory{Style.RESET_ALL}\n")

# Directories for installation
INSTALL_DIR = os.path.expanduser("~/tools")
BIN_DIR = os.path.expanduser("~/bin")

def run_command(command, cwd=None, check=True, retries=3):
    """Run a system command with retries for network operations."""
    for attempt in config.progress(range(retries), desc="Attempting command"):
        try:
            subprocess.run(command, shell=True, check=check, cwd=cwd)
            return  # Command succeeded, exit the loop
        except subprocess.CalledProcessError as e:
            config.print(f"Attempt {attempt + 1} failed: {e}", Fore.YELLOW)
            if attempt < retries - 1:
                config.print("Retrying...", Fore.YELLOW)
                time.sleep(2)  # Short delay before retry
            else:
                config.print(f"Command failed after {retries} attempts: {command}", Fore.RED)
                sys.exit(1)

def clone_repo(repo_url, install_dir):
    """Clone a GitHub repository."""
    config.print(f"Cloning repository {repo_url} into {install_dir}...", Fore.CYAN)
    run_command(f"git clone {repo_url} {install_dir}")

def detect_requirements(tool_dir):
    """Check if a requirements.txt file exists and handle dependencies."""
    requirements_file = os.path.join(tool_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        config.print("Detected a requirements.txt file. Installing dependencies...", Fore.GREEN)
        run_command(f"{sys.executable} -m pip install -r {requirements_file}")
        return True
    config.print("No requirements.txt file detected.", Fore.YELLOW)
    return False

def make_executable(path):
    """Ensure a file has executable permissions."""
    if not os.access(path, os.X_OK):
        config.print(f"Making {path} executable...", Fore.CYAN)
        run_command(f"chmod +x {path}")

def detect_executables(tool_dir):
    """Detect potential executables in the tool directory."""
    executables = []
    config.print("Scanning for executables...", Fore.CYAN)
    for root, _, files in config.progress(os.walk(tool_dir), desc="Scanning files"):
        for file in files:
            file_path = os.path.join(root, file)
            if (
                file.endswith((".py", ".sh")) and
                "sample" not in file.lower() and
                not file.startswith(".git")
            ):
                executables.append(file_path)
    return executables

def ensure_path_in_environment(bin_dir):
    """Ensure the bin directory is in the PATH, adapting for different OSes."""
    system = platform.system()
    if system == "Windows":
        config.print(f"Adding {bin_dir} to PATH on Windows...", Fore.CYAN)
        run_command(f'setx PATH "%PATH%;{bin_dir}"', check=False)
        config.print(f"\nRestart your terminal to apply the changes.", Fore.YELLOW)
    else:  # For Linux/macOS
        if bin_dir not in os.environ["PATH"].split(":"):
            config.print(f"{bin_dir} is not in your PATH. Adding it now...", Fore.CYAN)
            shell_config = os.path.expanduser("~/.bashrc")
            with open(shell_config, "a") as f:
                f.write(f'\nexport PATH="{bin_dir}:$PATH"\n')
            config.print(f"\nTo activate the changes, run:", Fore.YELLOW)
            config.print(f"source {shell_config}", Fore.GREEN)

def create_symlink(executable, symlink_path):
    """Create a symlink for the executable, handling Windows separately."""
    system = platform.system()
    if system == "Windows":
        config.print(f"Copying {executable} to {symlink_path} on Windows...", Fore.CYAN)
        run_command(f'copy "{executable}" "{symlink_path}"', check=False)
    else:
        config.print(f"Creating symlink for {executable} at {symlink_path}...", Fore.CYAN)
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(executable, symlink_path)
        config.print(f"Symlink created: {symlink_path}", Fore.GREEN)

def is_valid_url(url):
    """Validate the GitHub repository URL."""
    return re.match(r'https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+(\.git)?$', url)

def get_user_input(prompt, allow_cancel=True):
    """Prompt the user for input, with an option to cancel."""
    while True:
        user_input = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL} ").strip()
        if allow_cancel and user_input.lower() == "cancel":
            config.print("Installation canceled by user.", Fore.YELLOW)
            sys.exit(0)
        if user_input:  # Ensure non-empty input
            return user_input
        config.print("Input cannot be empty. Please try again.", Fore.RED)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Tool Deployer - Automate tool installation from GitHub")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode (no output)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    config.quiet = args.quiet
    config.no_color = args.no_color
    config.verbose = args.verbose

    # Show the fancy banner
    show_banner()
    
    # Ensure necessary directories exist
    os.makedirs(INSTALL_DIR, exist_ok=True)
    os.makedirs(BIN_DIR, exist_ok=True)

    # Detect the OS and inform the user
    system = platform.system()
    config.print(f"Detected Operating System: {system}", Fore.CYAN)

    # Validate and get GitHub repo URL
    while True:
        repo_url = get_user_input("Enter the GitHub repository URL (or type 'Cancel' to exit):")
        if is_valid_url(repo_url):
            break
        config.print("Invalid GitHub URL. Please enter a valid URL, e.g., 'https://github.com/user/repo.git'", Fore.RED)

    tool_name = get_user_input(
        "Enter a name for the tool (default: repo name) (or type 'Cancel' to exit):",
        allow_cancel=True,
    ) or repo_url.split("/")[-1].replace(".git", "")
    install_path = os.path.join(INSTALL_DIR, tool_name)

    if os.path.exists(install_path):
        config.print(f"{tool_name} is already installed in {install_path}.", Fore.YELLOW)
        reinstall = get_user_input("Do you want to reinstall it? (y/n or type 'Cancel' to exit):").lower()
        if reinstall != "y":
            config.print("Exiting...", Fore.YELLOW)
            return
        run_command(f"rm -rf {install_path}")

    # Clone repository
    try:
        clone_repo(repo_url, install_path)
    except Exception as e:
        config.print(f"Error during cloning: {e}", Fore.RED)
        sys.exit(1)

    # Detect and handle requirements
    if not detect_requirements(install_path):
        install_deps = get_user_input("Does this tool require additional dependencies? (y/n or type 'Cancel' to exit):").strip().lower() == "y"
        if install_deps:
            config.print("Please install the dependencies manually or provide further instructions.", Fore.YELLOW)

    # Detect executables
    executables = detect_executables(install_path)
    if executables:
        while True:
            try:
                config.print("Detected potential executables:", Fore.GREEN)
                for idx, exe in enumerate(executables, 1):
                    config.print(f"{idx}. {os.path.basename(exe)}", Fore.CYAN)
                choice = int(get_user_input("Enter the number of the executable to use (or type 'Cancel' to exit):")) - 1
                if 0 <= choice < len(executables):
                    executable_path = executables[choice]
                    break
                else:
                    raise IndexError
            except (ValueError, IndexError):
                config.print("Invalid choice. Please enter a number corresponding to one of the executables.", Fore.RED)
    else:
        config.print("No executable detected in the repository.", Fore.RED)
        return

    if executable_path:
        make_executable(executable_path)
        symlink_path = os.path.join(BIN_DIR, tool_name)
        create_symlink(executable_path, symlink_path)
        config.print(f"{tool_name} is now installed. You can run it using '{tool_name}' if {BIN_DIR} is in your PATH.", Fore.GREEN)
    else:
        config.print(f"No valid executable was selected. {tool_name} is installed in {install_path}.", Fore.YELLOW)

    # Ensure BIN_DIR is in PATH
    ensure_path_in_environment(BIN_DIR)

if __name__ == "__main__":
    main()
