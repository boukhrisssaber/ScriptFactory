import os
import subprocess
import sys

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
    print("\thttps://github.com/yourusername/ScriptFactory\n")



# Directories for installation
INSTALL_DIR = os.path.expanduser("~/tools")
BIN_DIR = os.path.expanduser("~/bin")

def run_command(command, cwd=None, check=True):
    """Run a system command."""
    try:
        subprocess.run(command, shell=True, check=check, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
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

def create_symlink(executable, symlink_path):
    """Create a symlink for the executable."""
    print(f"Creating symlink for {executable} at {symlink_path}...")
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(executable, symlink_path)
    print(f"Symlink created: {symlink_path}")

def ensure_path_in_environment(bin_dir):
    """Ensure the bin directory is in the PATH."""
    if bin_dir not in os.environ["PATH"].split(":"):
        print(f"{bin_dir} is not in your PATH. Adding it now...")
        shell_config = os.path.expanduser("~/.bashrc")
        with open(shell_config, "a") as f:
            f.write(f'\nexport PATH="{bin_dir}:$PATH"\n')
        print(f"\nTo activate the changes, run:")
        print(f"source {shell_config}")

def main():
    # Show the fancy banner
    show_banner()
    
    # Ensure necessary directories exist
    os.makedirs(INSTALL_DIR, exist_ok=True)
    os.makedirs(BIN_DIR, exist_ok=True)

    # Prompt for GitHub repo URL
    repo_url = input("Enter the GitHub repository URL: ").strip()
    tool_name = input("Enter a name for the tool (default: repo name): ").strip() or repo_url.split("/")[-1].replace(".git", "")
    install_path = os.path.join(INSTALL_DIR, tool_name)

    if os.path.exists(install_path):
        print(f"{tool_name} is already installed in {install_path}.")
        if input("Do you want to reinstall it? (y/n): ").lower() != "y":
            print("Exiting...")
            return
        run_command(f"rm -rf {install_path}")

    # Clone repository
    clone_repo(repo_url, install_path)

    # Detect and handle requirements
    if not detect_requirements(install_path):
        install_deps = input("Does this tool require additional dependencies? (y/n): ").strip().lower() == "y"
        if install_deps:
            print("Please install the dependencies manually or provide further instructions.")

    # Detect executables
    executables = detect_executables(install_path)
    if executables:
        if len(executables) == 1:
            # Auto-detect the single executable but confirm with the user
            executable_path = executables[0]
            print(f"Automatically detected executable: {os.path.basename(executable_path)}")
            use_auto = input(f"Do you want to use this executable? (y/n): ").strip().lower() == "y"
            if not use_auto:
                print("Detected potential executables:")
                for idx, exe in enumerate(executables, 1):
                    print(f"{idx}. {os.path.basename(exe)}")
                choice = int(input("Enter the number of the executable to use: ").strip()) - 1
                executable_path = executables[choice]
        else:
            print("Detected potential executables:")
            for idx, exe in enumerate(executables, 1):
                print(f"{idx}. {os.path.basename(exe)}")
            choice = int(input("Enter the number of the executable to use: ").strip()) - 1
            executable_path = executables[choice]
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
