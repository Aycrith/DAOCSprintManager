# Quick Start Guide

Get DAOC Sprint Manager up and running in minutes!

## 1. Installation

### Pre-built Executable (Recommended)
1. Download the latest release from the [Releases page](https://github.com/yourusername/daoc-sprint-manager/releases)
2. Extract the ZIP file to your desired location
3. Run `SprintManager.exe`

### From Source
1. Clone the repository
2. Install Python 3.8 or later
3. Run `pip install -r requirements.txt`
4. Run `python main.py`

## 2. Initial Setup

1. **Launch the Application**
   - The system tray icon will appear
   - Right-click the icon for the menu

2. **Open Configuration**
   - Select "Configure" from the tray menu
   - The configuration window will open

3. **Essential Settings**
   - Set `Game Window Title` to match your DAOC window
   - Configure `Sprint Key` (default: NumPad0)
   - Set up Region of Interest (ROI):
     1. Click "Configure ROI"
     2. Use the selection tool to draw around your sprint icon
     3. Click "Save ROI"

4. **Detection Method**
   - Template Matching (Default, Recommended)
     - Works out of the box
     - CPU efficient
   - ML Detection (Advanced)
     - Requires ONNX model
     - Better accuracy in some cases

## 3. Create Your First Profile

1. Open Profile Manager from tray menu
2. Click "New Profile"
3. Enter profile name (e.g., "Main Character")
4. Configure profile-specific settings
5. Save profile

## 4. Start Detection

1. Ensure DAOC is running
2. Right-click tray icon → "Start Detection"
3. Status will show "Running"
4. Sprint icon will be detected automatically

## 5. Verify Operation

1. Enter combat in DAOC
2. Sprint icon should appear
3. Sprint will activate automatically
4. Check system tray icon for status

## 6. Troubleshooting

### Common Issues

1. **Game Window Not Found**
   - Verify game window title matches configuration
   - Restart application after DAOC launches

2. **Sprint Not Detecting**
   - Adjust ROI using configuration tool
   - Verify sprint icon is visible
   - Check detection method settings

3. **Performance Issues**
   - Lower capture FPS in settings
   - Reduce ROI size
   - Close unnecessary background applications

### Logs Location
- Logs are in `%APPDATA%/DAOCSprintManager/logs/`
- Check `sprint_manager.log` for details

## 7. Next Steps

1. **Fine-tune Settings**
   - Adjust detection sensitivity
   - Configure auto-profile switching
   - Customize hotkeys

2. **Create Additional Profiles**
   - Different characters
   - Different UI layouts
   - Different servers

3. **Read Full Documentation**
   - Check README.md for detailed features
   - Review INSTALLATION.md for advanced setup
   - See KNOWN_ISSUES.md for limitations

## Need Help?

- Check the [FAQ](docs/FAQ.md)
- Review [Known Issues](docs/KNOWN_ISSUES.md)
- Submit an issue on GitHub
- Join our Discord community 