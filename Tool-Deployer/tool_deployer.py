import os, sys, subprocess, re, time, platform
from tqdm import tqdm
from colorama import init, Fore, Style
import argparse
from dependency_manager import DependencyManager
from tool_manager import ToolManager

# Initialize colorama
init()

# Define the static ASCII banner
banner = r"""
 __________  ____  __     ___  _______  __   ______  _________ 
/_  __/ __ \/ __ \/ /    / _ \/ __/ _ \/ /  / __ \ \/ / __/ _ \
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

def handle_dependencies(tool_dir):
    """Handle dependencies using the DependencyManager"""
    dep_manager = DependencyManager(config)
    
    # Detect package managers
    managers = dep_manager.detect_package_managers(tool_dir)
    if not managers:
        config.print("No package managers detected.", Fore.YELLOW)
        return False
    
    config.print(f"Detected package managers: {', '.join(managers)}", Fore.GREEN)
    
    # Verify dependencies
    config.print("Verifying dependencies...", Fore.CYAN)
    results = dep_manager.verify_dependencies(tool_dir)
    
    # Display dependency status
    for manager, deps in results.items():
        if deps:
            config.print(f"\n{manager.upper()} Dependencies:", Fore.CYAN)
            for package, required_version, meets_requirements in deps:
                status_color = Fore.GREEN if meets_requirements else Fore.RED
                status = "✓" if meets_requirements else "✗"
                config.print(f"{status} {package} (required: {required_version})", status_color)
    
    # Install dependencies
    for manager in managers:
        if not dep_manager.install_dependencies(tool_dir, manager):
            config.print(f"Failed to install dependencies using {manager}", Fore.RED)
            return False
    
    return True

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
                file.endswith((".py", ".sh", ".js")) and
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
            config.print("Operation canceled by user.", Fore.YELLOW)
            sys.exit(0)
        if user_input:  # Ensure non-empty input
            return user_input
        config.print("Input cannot be empty. Please try again.", Fore.RED)

def parse_arguments(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Tool Deployer - Automate tool installation from GitHub")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode (no output)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a new tool")
    install_parser.add_argument("url", nargs="?", help="GitHub repository URL")
    
    # List command
    subparsers.add_parser("list", help="List installed tools")
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a tool")
    uninstall_parser.add_argument("name", help="Name of the tool to uninstall")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update an installed tool")
    update_parser.add_argument("name", help="Name of the tool to update")
    
    return parser.parse_args(args)

def handle_install(args):
    """Handle the install command"""
    # Get GitHub repo URL
    repo_url = args.url
    if not repo_url:
        while True:
            repo_url = get_user_input("Enter the GitHub repository URL (or type 'Cancel' to exit):")
            if is_valid_url(repo_url):
                break
            config.print("Invalid GitHub URL. Please enter a valid URL, e.g., 'https://github.com/user/repo.git'", Fore.RED)

    tool_name = get_user_input(
        "Enter a name for the tool (default: repo name) (or type 'Cancel' to exit):",
        allow_cancel=True,
    ) or repo_url.split("/")[-1].replace(".git", "")
    
    tool_manager = ToolManager(config)
    install_path = os.path.join(tool_manager.install_dir, tool_name)

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

    # Handle dependencies
    handle_dependencies(install_path)

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
        symlink_path = os.path.join(tool_manager.bin_dir, tool_name)
        if tool_manager.create_symlink(executable_path, symlink_path):
            tool_manager.install_tool(tool_name, install_path, executable_path)
            config.print(f"{tool_name} is now installed. You can run it using '{tool_name}' if {tool_manager.bin_dir} is in your PATH.", Fore.GREEN)
        else:
            config.print(f"Failed to create symlink for {tool_name}.", Fore.RED)
    else:
        config.print(f"No valid executable was selected. {tool_name} is installed in {install_path}.", Fore.YELLOW)

    # Ensure BIN_DIR is in PATH
    tool_manager.ensure_path_in_environment()

def handle_list():
    """Handle the list command"""
    tool_manager = ToolManager(config)
    tools = tool_manager.list_tools()
    
    if not tools:
        config.print("No tools installed.", Fore.YELLOW)
        return
    
    config.print("\nInstalled Tools:", Fore.CYAN)
    for tool in tools:
        config.print(f"\n{tool['name']}:", Fore.GREEN)
        config.print(f"  Path: {tool['path']}", Fore.WHITE)
        config.print(f"  Executable: {tool['executable']}", Fore.WHITE)
        config.print(f"  Installed: {tool['installed_at']}", Fore.WHITE)
        config.print(f"  Last Updated: {tool['last_updated']}", Fore.WHITE)

def handle_uninstall(args):
    """Handle the uninstall command"""
    tool_manager = ToolManager(config)
    if tool_manager.uninstall_tool(args.name):
        config.print(f"Successfully uninstalled {args.name}", Fore.GREEN)
    else:
        config.print(f"Failed to uninstall {args.name}", Fore.RED)

def handle_update(args):
    """Handle the update command"""
    tool_manager = ToolManager(config)
    if tool_manager.update_tool(args.name):
        config.print(f"Successfully updated {args.name}", Fore.GREEN)
    else:
        config.print(f"Failed to update {args.name}", Fore.RED)

def main():
    # Parse command line arguments
    args = parse_arguments()
    config.quiet = args.quiet
    config.no_color = args.no_color
    config.verbose = args.verbose

    # Show the fancy banner
    show_banner()
    
    # Handle commands
    if args.command == "install":
        handle_install(args)
    elif args.command == "list":
        handle_list()
    elif args.command == "uninstall":
        handle_uninstall(args)
    elif args.command == "update":
        handle_update(args)
    else:
        # If no command specified, show help
        parse_arguments(["-h"])

if __name__ == "__main__":
    main()
