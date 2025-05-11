# DAOC Sprint Manager Distribution Guide

This guide covers building, testing, and distributing the DAOC Sprint Manager application.

## Prerequisites

- Python 3.9 or higher
- Git
- Windows 10 or higher

## Installation for Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PythonSprint
   ```

2. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Building the Executable

### Quick Build

The fastest way to build and test the executable is to run:

```bash
scripts/test_distribution.bat
```

This script will:
1. Build the executable using PyInstaller
2. Run distribution tests
3. Report any issues

### Manual Build Steps

1. Build the executable:
   ```bash
   python scripts/build_exe.py
   ```

2. Run distribution tests:
   ```bash
   python -m pytest scripts/test_distribution.py -v
   ```

## Distribution Package Structure

After building, the distribution package will be in the `dist` directory:

```
dist/
└── DAOCSprintManager.exe
```

## Testing the Distribution

The test suite in `scripts/test_distribution.py` verifies:

1. Executable Creation
   - File exists and has correct size
   - Proper executable permissions
   - Valid Windows executable format

2. Resource Bundling
   - Icon file is included
   - Required resources are bundled

3. Application Startup
   - Executable launches without errors
   - System tray icon appears
   - Process runs correctly

4. Configuration
   - Config directory is created
   - Config file is generated with defaults
   - Training extras functionality works

## Package Distribution

### PyPI Installation

The package can be installed via pip:

```bash
pip install daoc-sprint-manager
```

### Standalone Executable

The standalone executable can be distributed directly. Users only need to:

1. Download `DAOCSprintManager.exe`
2. Run the executable
3. (Optional) Create a desktop shortcut

## Version Management

Version information is maintained in `src/daoc_sprint_manager/__init__.py`.
Current version: 0.3.0

## Troubleshooting

### Common Issues

1. Missing DLLs
   - Ensure all dependencies are installed
   - Check Windows system DLLs

2. Resource Not Found
   - Verify resources directory exists
   - Check resource paths in code

### Debug Build

For debugging, build with console output:

```bash
python scripts/build_exe.py --debug
```

## Future Updates

Planned improvements:
- Automatic update checking
- Installer creation
- Silent installation option

## Support

For issues:
1. Check the troubleshooting guide
2. Search existing GitHub issues
3. Create a new issue with:
   - Windows version
   - Python version
   - Error messages
   - Steps to reproduce 