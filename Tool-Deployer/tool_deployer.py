import os, sys, subprocess, re, time, platform

# Define the static ASCII banner
banner = """
 __________  ____  __     ___  _______  __   ______  _________ 
/_  __/ __ \/ __ \/ /    / _ \/ __/ _ \/ /  / __ \ \/ / __/ _ \\
 / / / /_/ / /_/ / /__  / // / _// ___/ /__/ /_/ /\  / _// , _/
/_/  \____/\____/____/ /____/___/_/  /____/\____/ /_/___/_/|_|                                                             TOOL DEPLOYER v1.0.0
"""

def show_banner():
    """Displays the banner to the user."""
    print(banner)
    print("\t\tScriptFactory by W1SEBYT3S")
    print("\thttps://github.com/boukhrisssaber/ScriptFactory\n")

# Directories for installation
INSTALL_DIR = os.path.expanduser("~/tools")
BIN_DIR = os.path.expanduser("~/bin")

def run_command(command, cwd=None, check=True, retries=3):
    """Run a system command with retries for network operations."""
    for attempt in range(retries):
        try:
            subprocess.run(command, shell=True, check=check, cwd=cwd)
            return  # Command succeeded, exit the loop
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print("Retrying...")
                time.sleep(2)  # Short delay before retry
            else:
                print(f"Command failed after {retries} attempts: {command}")
                sys.exit(1)

def clone_repo(repo_url, install_dir):
    """Clone a GitHub repository."""
    print(f"Cloning repository {repo_url} into {install_dir}...")
    run_command(f"git clone {repo_url} {install_dir}")

def detect_requirements(tool_dir):
    """Check if a requirements.txt file exists and handle dependencies."""
    requirements_file = os.path.join(tool_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        print("Detected a requirements.txt file. Installing dependencies...")
        run_command(f"{sys.executable} -m pip install -r {requirements_file}")
        return True
    print("No requirements.txt file detected.")
    return False

def make_executable(path):
    """Ensure a file has executable permissions."""
    if not os.access(path, os.X_OK):
        print(f"Making {path} executable...")
        run_command(f"chmod +x {path}")

def detect_executables(tool_dir):
    """Detect potential executables in the tool directory."""
    executables = []
    for root, _, files in os.walk(tool_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Prioritize .py and .sh files, exclude Git hook samples and irrelevant files
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
        # Use setx to persistently add the bin directory to PATH
        print(f"Adding {bin_dir} to PATH on Windows...")
        run_command(f'setx PATH "%PATH%;{bin_dir}"', check=False)
        print(f"\nRestart your terminal to apply the changes.")
    else:  # For Linux/macOS
        if bin_dir not in os.environ["PATH"].split(":"):
            print(f"{bin_dir} is not in your PATH. Adding it now...")
            shell_config = os.path.expanduser("~/.bashrc")
            with open(shell_config, "a") as f:
                f.write(f'\nexport PATH="{bin_dir}:$PATH"\n')
            print(f"\nTo activate the changes, run:")
            print(f"source {shell_config}")

def create_symlink(executable, symlink_path):
    """Create a symlink for the executable, handling Windows separately."""
    system = platform.system()
    if system == "Windows":
        # On Windows, copy the executable to the bin_dir
        print(f"Copying {executable} to {symlink_path} on Windows...")
        run_command(f'copy "{executable}" "{symlink_path}"', check=False)
    else:
        # On Unix-like systems, create a symlink
        print(f"Creating symlink for {executable} at {symlink_path}...")
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(executable, symlink_path)
        print(f"Symlink created: {symlink_path}")

def is_valid_url(url):
    """Validate the GitHub repository URL."""
    return re.match(r'https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+(\.git)?$', url)

def get_user_input(prompt, allow_cancel=True):
    """Prompt the user for input, with an option to cancel."""
    while True:
        user_input = input(f"{prompt} ").strip()
        if allow_cancel and user_input.lower() == "cancel":
            print("Installation canceled by user.")
            sys.exit(0)
        if user_input:  # Ensure non-empty input
            return user_input
        print("Input cannot be empty. Please try again.")

def main():
    # Show the fancy banner
    show_banner()
    
    # Ensure necessary directories exist
    os.makedirs(INSTALL_DIR, exist_ok=True)
    os.makedirs(BIN_DIR, exist_ok=True)

    # Detect the OS and inform the user
    system = platform.system()
    print(f"Detected Operating System: {system}")

    # Validate and get GitHub repo URL
    while True:
        repo_url = get_user_input("Enter the GitHub repository URL (or type 'Cancel' to exit):")
        if is_valid_url(repo_url):
            break
        print("Invalid GitHub URL. Please enter a valid URL, e.g., 'https://github.com/user/repo.git'")

    tool_name = get_user_input(
        "Enter a name for the tool (default: repo name) (or type 'Cancel' to exit):",
        allow_cancel=True,
    ) or repo_url.split("/")[-1].replace(".git", "")
    install_path = os.path.join(INSTALL_DIR, tool_name)

    if os.path.exists(install_path):
        print(f"{tool_name} is already installed in {install_path}.")
        reinstall = get_user_input("Do you want to reinstall it? (y/n or type 'Cancel' to exit):").lower()
        if reinstall != "y":
            print("Exiting...")
            return
        run_command(f"rm -rf {install_path}")

    # Clone repository
    try:
        clone_repo(repo_url, install_path)
    except Exception as e:
        print(f"Error during cloning: {e}")
        sys.exit(1)

    # Detect and handle requirements
    if not detect_requirements(install_path):
        install_deps = get_user_input("Does this tool require additional dependencies? (y/n or type 'Cancel' to exit):").strip().lower() == "y"
        if install_deps:
            print("Please install the dependencies manually or provide further instructions.")

    # Detect executables
    executables = detect_executables(install_path)
    if executables:
        while True:
            try:
                print("Detected potential executables:")
                for idx, exe in enumerate(executables, 1):
                    print(f"{idx}. {os.path.basename(exe)}")
                choice = int(get_user_input("Enter the number of the executable to use (or type 'Cancel' to exit):")) - 1
                if 0 <= choice < len(executables):
                    executable_path = executables[choice]
                    break
                else:
                    raise IndexError
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a number corresponding to one of the executables.")
    else:
        print("No executable detected in the repository.")
        return

    if executable_path:
        make_executable(executable_path)
        symlink_path = os.path.join(BIN_DIR, tool_name)
        create_symlink(executable_path, symlink_path)
        print(f"{tool_name} is now installed. You can run it using '{tool_name}' if {BIN_DIR} is in your PATH.")
    else:
        print(f"No valid executable was selected. {tool_name} is installed in {install_path}.")

    # Ensure BIN_DIR is in PATH
    ensure_path_in_environment(BIN_DIR)

if __name__ == "__main__":
    main()
