# DAOC Sprint Manager Distribution Guide

This guide explains how to build and distribute the DAOC Sprint Manager application.

## Prerequisites

- Python 3.9 or later
- PyInstaller 6.0 or later
- All development dependencies installed:
  ```bash
  pip install -r requirements.txt
  pip install pyinstaller
  ```

## Project Structure

```
PythonSprint/
├── src/
│   └── daoc_sprint_manager/
│       ├── main.py
│       ├── core/
│       ├── models/
│       └── utils/
├── assets/
│   ├── app_icon.ico
│   └── app_icon.png
├── models/
│   └── sprint_classifier.onnx
├── config/
│   └── settings.json.template
├── docs/
│   ├── INSTALLATION.md
│   └── DISTRIBUTION_GUIDE.md
├── tests/
├── build_exe.py
├── daoc_sprint_manager.spec
├── file_version_info.txt
└── README.md
```

## Building the Application

### 1. Prepare the Environment

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Generate Application Icon

```bash
# Generate icon files
python scripts/generate_icon.py
```

This creates:
- `assets/app_icon.png`
- `assets/app_icon.ico`

### 3. Build the Executable

```bash
# Option 1: Using build script
python build_exe.py

# Option 2: Using PyInstaller directly
pyinstaller --clean daoc_sprint_manager.spec
```

The build process:
1. Cleans previous builds
2. Compiles Python files
3. Collects dependencies
4. Bundles assets and configuration
5. Creates the executable

Output location: `dist/DAOC Sprint Manager/`

## Distribution Package Contents

The following files/folders should be included in the distribution:

```
DAOC Sprint Manager/
├── DAOC Sprint Manager.exe
├── assets/
│   ├── app_icon.ico
│   └── app_icon.png
├── models/
│   └── sprint_classifier.onnx
├── config/
│   └── settings.json.template
├── docs/
│   ├── INSTALLATION.md
│   └── DISTRIBUTION_GUIDE.md
├── README.md
└── LICENSE
```

## Creating a Release

1. **Update Version Information**
   - Update `file_version_info.txt`
   - Update version in `src/daoc_sprint_manager/__init__.py`
   - Update changelog in documentation

2. **Build and Test**
   ```bash
   python build_exe.py
   # Test the executable thoroughly
   ```

3. **Create Distribution Package**
   ```bash
   # Create ZIP archive
   cd dist
   zip -r DAOC_Sprint_Manager_vX.Y.Z.zip "DAOC Sprint Manager"
   ```

4. **Release Checklist**
   - [ ] Version numbers updated
   - [ ] Changelog updated
   - [ ] All dependencies included
   - [ ] Documentation up to date
   - [ ] License included
   - [ ] Test on clean Windows installation
   - [ ] Verify startup performance
   - [ ] Check memory usage
   - [ ] Test all major features

## Deployment

### GitHub Release

1. Tag the release:
   ```bash
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   git push origin vX.Y.Z
   ```

2. Create GitHub release:
   - Upload ZIP file
   - Include release notes
   - Mark as pre-release if applicable
   - Include installation instructions

### Distribution Channels

- GitHub Releases (primary)
- Project website (if applicable)
- Community forums (with permission)

## Post-Release

1. **Monitor Issues**
   - Watch for bug reports
   - Address critical issues promptly
   - Update documentation as needed

2. **User Support**
   - Monitor GitHub issues
   - Update FAQ if needed
   - Provide support in community channels

3. **Maintenance**
   - Regular dependency updates
   - Security patches
   - Performance improvements

## Troubleshooting Distribution Issues

### Common Problems

1. **Missing Dependencies**
   - Use `pyinstaller --debug` for detailed output
   - Check `warn-daoc_sprint_manager.txt` in build directory
   - Verify all imports in spec file

2. **Icon Issues**
   - Ensure icon files exist in correct location
   - Verify icon format is valid
   - Check path in spec file

3. **Runtime Errors**
   - Test on clean Windows installation
   - Check for missing DLLs
   - Verify file permissions

### Support Resources

- PyInstaller Documentation
- GitHub Issues
- Community Forums
- Development Team Contacts 