# DAOC Sprint Manager Installation Guide

## System Requirements

- Windows 10 or later
- Python 3.9 or later
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- DirectX 9 compatible graphics card (for game window detection)

## Installation Methods

### Method 1: Using Pre-built Executable (Recommended)

1. Download the latest release from the releases page
2. Extract the ZIP file to your desired location
3. Run `DAOC Sprint Manager.exe` from the extracted folder

### Method 2: Installing from Source

#### Prerequisites

1. Install Python 3.9 or later from [python.org](https://python.org) or Anaconda
2. Install Git from [git-scm.com](https://git-scm.com)

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/daoc-sprint-manager.git
   cd daoc-sprint-manager
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python src/daoc_sprint_manager/main.py
   ```

## Configuration

1. On first run, the application will create a `config` directory with default settings
2. Edit `config/settings.json` to customize:
   - Icon detection sensitivity
   - Hotkeys
   - UI preferences
   - Model settings

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Verify Python version
   - Check if all dependencies are installed
   - Run from command line to see error messages

2. **Game window not detected**
   - Ensure game is running in windowed or borderless mode
   - Check if DirectX is up to date
   - Verify window title matches configuration

3. **Icon detection issues**
   - Calibrate detection sensitivity in settings
   - Verify game UI scale is set to 100%
   - Check if icon templates match your game version

### Getting Help

- Check the [GitHub Issues](https://github.com/yourusername/daoc-sprint-manager/issues)
- Join our [Discord community](https://discord.gg/yourdiscord)
- Submit a bug report with:
  - System specifications
  - Error messages
  - Steps to reproduce
  - Screenshots if applicable

## Updating

### Pre-built Version
- Download the latest release
- Extract and replace existing files
- Your settings will be preserved

### Source Version
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstallation

### Pre-built Version
- Delete the application directory
- Optionally delete `%APPDATA%/DAOC Sprint Manager` for complete removal

### Source Version
- Deactivate virtual environment: `deactivate`
- Delete project directory
- Remove virtual environment if created 