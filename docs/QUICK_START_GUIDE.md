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
   - Note: You can enable "Start Minimized to Tray" in settings for future launches

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

4. **UI Behavior Settings**
   - In the Configuration window, navigate to the Advanced tab
   - Configure UI behavior preferences:
     - "Start Minimized to Tray" - Application starts silently in tray
     - "Minimize GUI to Tray" - Windows minimize to tray instead of closing
   - Configure update behavior:
     - "Enable Background Update Check" - Periodically check for updates
     - "Update Check Interval" - Hours between automatic checks

5. **Detection Method**
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

## 5. Additional Features

1. **Performance Statistics**
   - Right-click tray icon → "View Performance Stats"
   - Monitor real-time application performance:
     - CPU and memory usage
     - Frame processing time
     - Detection success rate
   - Reset session statistics with the "Reset" button

2. **Automatic Updates** (New in v0.4.0)
   - DAOC Sprint Manager now features a secure automatic update system:
     1. **Update Detection**:
        - The application checks for updates in the background at your configured interval
        - You can also manually check via the system tray menu -> "Check for Updates"
        - When a new version is detected, you'll receive a system tray notification
     
     2. **Update Options**:
        - **Update Now**: Immediately download and apply the update
        - **Remind Me Later**: Postpone the update until next application launch
        - After multiple deferrals, the notification will become more prominent
     
     3. **Download & Installation Process**:
        - The update package is downloaded with a progress indicator
        - SHA256 checksum verification ensures update integrity
        - If verification succeeds, the application:
          - Creates a backup of your current installation
          - Applies the update using a batch script
          - Automatically restarts with the new version
     
     4. **Failure Handling**:
        - If download fails: Error notification appears, current version continues running
        - If checksum verification fails: Update is rejected, current version continues running
        - If installation fails: Automatic rollback to previous version
     
     5. **Configuration Options**:
        - Open Configuration GUI -> Advanced tab
        - Enable/disable background update checks
        - Set check interval (hours)
        - View last check timestamp and result

3. **Diagnostic Reporting**
   - If you encounter issues, generate a diagnostic report:
     - Right-click tray icon → "Export Diagnostic Report"
     - Choose save location for the ZIP file
     - Submit with any bug reports for faster troubleshooting

## 6. Verify Operation

1. Enter combat in DAOC
2. Sprint icon should appear
3. Sprint will activate automatically
4. Check system tray icon for status

## 7. Troubleshooting

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
   - Check Performance Stats window for metrics

### Diagnostic Tools
- Export a diagnostic report for troubleshooting: right-click tray icon → "Export Diagnostic Report"
- Logs are in `%APPDATA%/DAOCSprintManager/logs/`
- Check `sprint_manager.log` for details

### Update Issues
- **Connection Problems**: Ensure you have internet connectivity for update checks
- **Download Failures**: Check your firewall settings or try manually downloading from GitHub
- **Checksum Errors**: This indicates a corrupted download - try checking for updates again
- **Installation Errors**: Check logs for details; the application automatically restores from backup
- **Manual Alternative**: You can always download and install updates manually from our GitHub releases page

## 8. Next Steps

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