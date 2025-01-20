# Changelog

All notable changes to this project will be documented here.

## [1.0.1] - 2025-01-20
### Added
- Cross-platform compatibility for Windows:
  - Detect operating system and adapt commands accordingly.
  - Use `setx` for adding `BIN_DIR` to the PATH on Windows.
- Option to cancel installation at any critical prompt with the input "Cancel".

### Improved
- Enhanced error handling:
  - Specific error messages for failed commands.
  - Retry logic for network-dependent operations such as repository cloning.
- Input validation for GitHub repository URLs.
- Usability improvements in handling user inputs and executable detection.

## [1.0.0] - 2024-12-24
### Added
- Initial release of `tool_deployer.py`
- Automatic GitHub repository cloning and tool installation.
- Dependency detection and symlink creation.

- #### Known Issues
- No support for batch installations.
- Limited to none dependency handling for package managers other than `pip`.
