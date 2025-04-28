import os
import subprocess
import platform
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from colorama import Fore

class ToolManager:
    """Manages installed tools and their operations"""
    
    def __init__(self, config):
        self.config = config
        self.install_dir = os.path.expanduser("~/tools")
        self.bin_dir = os.path.expanduser("~/bin")
        self.tools_file = os.path.join(self.install_dir, ".tools.json")
        self.shell_configs = {
            'bash': os.path.expanduser("~/.bashrc"),
            'zsh': os.path.expanduser("~/.zshrc"),
            'fish': os.path.expanduser("~/.config/fish/config.fish")
        }

    def _load_tools(self) -> Dict:
        """Load the tools database"""
        if os.path.exists(self.tools_file):
            try:
                with open(self.tools_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_tools(self, tools: Dict):
        """Save the tools database"""
        os.makedirs(os.path.dirname(self.tools_file), exist_ok=True)
        with open(self.tools_file, 'w') as f:
            json.dump(tools, f, indent=4)

    def list_tools(self) -> List[Dict]:
        """List all installed tools"""
        tools = self._load_tools()
        return [
            {
                'name': name,
                'path': info['path'],
                'executable': info['executable'],
                'installed_at': info['installed_at'],
                'last_updated': info.get('last_updated', info['installed_at'])
            }
            for name, info in tools.items()
        ]

    def install_tool(self, name: str, path: str, executable: str) -> bool:
        """Install a new tool"""
        tools = self._load_tools()
        tools[name] = {
            'path': path,
            'executable': executable,
            'installed_at': datetime.now().isoformat()
        }
        self._save_tools(tools)
        return True

    def uninstall_tool(self, name: str) -> bool:
        """Uninstall a tool"""
        tools = self._load_tools()
        if name not in tools:
            self.config.print(f"Tool {name} is not installed.", Fore.RED)
            return False

        # Remove the tool directory
        tool_path = tools[name]['path']
        if os.path.exists(tool_path):
            try:
                subprocess.run(f"rm -rf {tool_path}", shell=True, check=True)
            except subprocess.CalledProcessError:
                self.config.print(f"Failed to remove tool directory: {tool_path}", Fore.RED)
                return False

        # Remove the symlink
        symlink_path = os.path.join(self.bin_dir, name)
        if os.path.exists(symlink_path):
            try:
                os.remove(symlink_path)
            except Exception as e:
                self.config.print(f"Failed to remove symlink: {e}", Fore.RED)
                return False

        # Remove from tools database
        del tools[name]
        self._save_tools(tools)
        return True

    def update_tool(self, name: str) -> bool:
        """Update an installed tool"""
        tools = self._load_tools()
        if name not in tools:
            self.config.print(f"Tool {name} is not installed.", Fore.RED)
            return False

        tool_path = tools[name]['path']
        if not os.path.exists(tool_path):
            self.config.print(f"Tool directory not found: {tool_path}", Fore.RED)
            return False

        try:
            # Update the git repository
            subprocess.run("git pull", shell=True, cwd=tool_path, check=True)
            
            # Update the last_updated timestamp
            tools[name]['last_updated'] = datetime.now().isoformat()
            self._save_tools(tools)
            
            return True
        except subprocess.CalledProcessError as e:
            self.config.print(f"Failed to update tool: {e}", Fore.RED)
            return False

    def ensure_path_in_environment(self):
        """Ensure the bin directory is in the PATH for all supported shells"""
        system = platform.system()
        
        if system == "Windows":
            self._ensure_windows_path()
        else:
            self._ensure_unix_path()

    def _ensure_windows_path(self):
        """Ensure the bin directory is in the PATH on Windows"""
        try:
            # Use setx to persistently add the bin directory to PATH
            self.config.print(f"Adding {self.bin_dir} to PATH on Windows...", Fore.CYAN)
            subprocess.run(f'setx PATH "%PATH%;{self.bin_dir}"', shell=True, check=True)
            self.config.print("Restart your terminal to apply the changes.", Fore.YELLOW)
        except subprocess.CalledProcessError as e:
            self.config.print(f"Failed to update PATH: {e}", Fore.RED)

    def _ensure_unix_path(self):
        """Ensure the bin directory is in the PATH on Unix-like systems"""
        for shell, config_file in self.shell_configs.items():
            if not os.path.exists(config_file):
                continue

            # Check if the path is already in the config
            with open(config_file, 'r') as f:
                content = f.read()
                if self.bin_dir in content:
                    continue

            # Add the path to the config
            with open(config_file, 'a') as f:
                if shell == 'fish':
                    f.write(f'\nset -gx PATH {self.bin_dir} $PATH\n')
                else:
                    f.write(f'\nexport PATH="{self.bin_dir}:$PATH"\n')

            self.config.print(f"Added {self.bin_dir} to {shell} configuration.", Fore.GREEN)
            self.config.print(f"To activate the changes, run:", Fore.YELLOW)
            if shell == 'fish':
                self.config.print(f"source {config_file}", Fore.CYAN)
            else:
                self.config.print(f"source {config_file}", Fore.CYAN)

    def create_symlink(self, executable: str, symlink_path: str) -> bool:
        """Create a symlink for the executable, handling Windows separately"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # On Windows, copy the executable to the bin_dir
                self.config.print(f"Copying {executable} to {symlink_path} on Windows...", Fore.CYAN)
                subprocess.run(f'copy "{executable}" "{symlink_path}"', shell=True, check=True)
            else:
                # On Unix-like systems, create a symlink
                self.config.print(f"Creating symlink for {executable} at {symlink_path}...", Fore.CYAN)
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                os.symlink(executable, symlink_path)
                self.config.print(f"Symlink created: {symlink_path}", Fore.GREEN)
            return True
        except Exception as e:
            self.config.print(f"Failed to create symlink: {e}", Fore.RED)
            return False 