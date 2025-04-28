import os
import subprocess
import re
from packaging import version
import semver
from typing import Dict, List, Optional, Tuple

class DependencyManager:
    """Manages dependencies for different package managers"""
    
    def __init__(self, config):
        self.config = config
        self.package_managers = {
            'pip': {
                'files': ['requirements.txt', 'setup.py'],
                'install_cmd': 'pip install -r {file}',
                'version_cmd': 'pip show {package}',
                'version_regex': r'Version: ([\d.]+)'
            },
            'npm': {
                'files': ['package.json'],
                'install_cmd': 'npm install',
                'version_cmd': 'npm list {package}',
                'version_regex': r'@([\d.]+)'
            },
            'yarn': {
                'files': ['package.json', 'yarn.lock'],
                'install_cmd': 'yarn install',
                'version_cmd': 'yarn list {package}',
                'version_regex': r'@([\d.]+)'
            }
        }

    def detect_package_managers(self, tool_dir: str) -> List[str]:
        """Detect which package managers are used in the tool directory"""
        detected_managers = []
        
        for manager, info in self.package_managers.items():
            for file in info['files']:
                if os.path.exists(os.path.join(tool_dir, file)):
                    detected_managers.append(manager)
                    break
        
        return detected_managers

    def check_package_version(self, manager: str, package: str) -> Optional[str]:
        """Check the installed version of a package"""
        try:
            cmd = self.package_managers[manager]['version_cmd'].format(package=package)
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                match = re.search(self.package_managers[manager]['version_regex'], result.stdout)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            self.config.print(f"Error checking version for {package}: {e}", Fore.RED)
            return None

    def compare_versions(self, current: str, required: str) -> bool:
        """Compare version strings and return True if current version meets requirements"""
        try:
            if manager == 'npm' or manager == 'yarn':
                return semver.compare(current, required) >= 0
            else:
                return version.parse(current) >= version.parse(required)
        except Exception as e:
            self.config.print(f"Error comparing versions: {e}", Fore.RED)
            return False

    def install_dependencies(self, tool_dir: str, manager: str) -> bool:
        """Install dependencies using the specified package manager"""
        try:
            if manager not in self.package_managers:
                self.config.print(f"Unsupported package manager: {manager}", Fore.RED)
                return False

            info = self.package_managers[manager]
            install_cmd = info['install_cmd']
            
            if '{file}' in install_cmd:
                # Find the appropriate file for this manager
                for file in info['files']:
                    file_path = os.path.join(tool_dir, file)
                    if os.path.exists(file_path):
                        install_cmd = install_cmd.format(file=file_path)
                        break
                else:
                    self.config.print(f"No suitable file found for {manager}", Fore.RED)
                    return False

            self.config.print(f"Installing dependencies using {manager}...", Fore.CYAN)
            result = subprocess.run(install_cmd, shell=True, cwd=tool_dir)
            return result.returncode == 0

        except Exception as e:
            self.config.print(f"Error installing dependencies with {manager}: {e}", Fore.RED)
            return False

    def verify_dependencies(self, tool_dir: str) -> Dict[str, List[Tuple[str, str, bool]]]:
        """Verify all dependencies in the tool directory"""
        results = {}
        
        for manager in self.detect_package_managers(tool_dir):
            results[manager] = []
            
            # Read dependency files
            for file in self.package_managers[manager]['files']:
                file_path = os.path.join(tool_dir, file)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                        # Extract dependencies and their versions
                        if manager == 'pip':
                            # Handle requirements.txt
                            for line in content.split('\n'):
                                if '==' in line:
                                    package, required_version = line.split('==')
                                    current_version = self.check_package_version(manager, package)
                                    if current_version:
                                        meets_requirements = self.compare_versions(current_version, required_version)
                                        results[manager].append((package, required_version, meets_requirements))
                        
                        elif manager in ['npm', 'yarn']:
                            # Handle package.json
                            import json
                            try:
                                data = json.loads(content)
                                dependencies = data.get('dependencies', {})
                                for package, required_version in dependencies.items():
                                    current_version = self.check_package_version(manager, package)
                                    if current_version:
                                        meets_requirements = self.compare_versions(current_version, required_version)
                                        results[manager].append((package, required_version, meets_requirements))
                            except json.JSONDecodeError:
                                self.config.print(f"Error parsing {file}", Fore.RED)
        
        return results 