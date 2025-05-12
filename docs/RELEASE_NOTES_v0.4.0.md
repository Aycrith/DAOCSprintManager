# DAOC Sprint Manager v0.4.0 Release Notes

*Release Date: June 28, 2024*

## Overview

We're excited to announce the release of DAOC Sprint Manager v0.4.0! This version introduces our new automatic update system, providing a secure and convenient way to keep your application up to date with the latest features and improvements.

## New Features

### Automatic Update System
- **Smart Version Checking**: Automatically checks for new versions according to your configured schedule
- **Secure Downloads**: All updates are verified with SHA256 checksum before installation
- **Seamless Installation**: Updates are applied with minimal disruption and automatic restart
- **User Control**: Choose when to update with "Update Now" or "Remind Me Later" options
- **Failure Protection**: Automatic backup and rollback in case of any update issues
- **Background Processing**: Update checks happen in the background without affecting performance

### Enhanced System Tray Experience
- **Update Notifications**: Receive notifications when updates are available
- **Manual Check Option**: Check for updates anytime via the system tray menu
- **Update Status**: Tray menu shows when updates are available or being downloaded

## Improvements

- **Enhanced Error Handling**: Improved error reporting and user feedback for update-related actions
- **Application Restart Logic**: Better handling of application restart after updates
- **Robust Testing Framework**: Comprehensive end-to-end testing to ensure reliability

## Installation & Update

### Fresh Installation
1. Download the application package: [DAOCSprintManager_v0.4.0.zip](https://github.com/Aycrith/DAOCSprintManager/releases/download/v0.4.0/DAOCSprintManager_v0.4.0.zip)
2. Extract the files to your desired location
3. Run `DAOC Sprint Manager.exe`

### Updating from v0.3.0
The application will automatically detect, download, and install this update. Simply accept the update when prompted.

### Security Verification
SHA256 Checksum: `1b4c36729555d0c6221d597f8e634ff1ddb49bf6ff381020689b2bed054b5d95`

To manually verify the download integrity:
1. Download the ZIP file
2. Open PowerShell and navigate to the download location
3. Run `certutil -hashfile "DAOCSprintManager_v0.4.0.zip" SHA256`
4. Confirm the output matches the checksum above

## Configuration Options

The update system can be configured through the Configuration GUI:
1. Right-click the system tray icon and select "Open Configuration"
2. Navigate to the Advanced tab
3. Find the "Update Settings" section:
   - Enable/disable background update checks
   - Set check interval (hours)
   - View last check timestamp

## Known Issues

No major issues have been reported with this release. Please report any issues you encounter on our GitHub page.

## Acknowledgements

Special thanks to all our beta testers who helped ensure the reliability of our new update system.

---

For more information, please visit our [GitHub repository](https://github.com/Aycrith/DAOCSprintManager) or refer to the included documentation. 