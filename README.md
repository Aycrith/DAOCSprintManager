# DAOC Sprint Manager (Python)

A Python-based utility to automatically manage sprint toggling in Dark Age of Camelot.

## Features

- Automated sprint detection using template matching and ML methods
- System tray interface for easy access and control
- Performance monitoring and statistics display
- Diagnostic report generation
- Multiple profile support with auto-switching
- Automatic updates with secure download and installation
- Customizable detection settings and regions
- Comprehensive logging and error handling

## Requirements

... (requirements) ...

## Installation

... (installation steps) ...

## First-Time Setup & Configuration

... (setup steps) ...

## Usage

1.  Launch the application (`DAOC Sprint Manager.exe` or `python -m src.daoc_sprint_manager.main`).
2.  The application icon will appear in your system tray.
3.  **Right-click** the tray icon for options:
    *   **Pause/Resume**: Toggle the sprint detection and automation.
    *   **Open Configuration**: Open the settings editor (Config GUI or `settings.json`).
    *   **View Performance Stats**: Open the performance statistics window to monitor CPU usage, memory consumption, frame processing time, and other metrics. You can also reset session statistics from this window.
    *   **Export Diagnostic Report**: Generate and save a comprehensive diagnostic ZIP file containing system information, logs, and settings for troubleshooting help.
    *   **Check for Updates**: Manually check if a new version of the application is available. The app also checks periodically in the background based on your settings.
    *   **Profiles**: Select or manage character/game profiles.
    *   **Exit**: Close the application.

## Automatic Updates

Starting with version 0.4.0, DAOC Sprint Manager includes an automatic update system:

- **Background Checks**: The application periodically checks for updates based on your configured interval
- **Update Notifications**: When a new version is available, you'll receive a system tray notification
- **Secure Downloads**: All updates are securely downloaded and verified with SHA256 checksums
- **Seamless Installation**: Updates are automatically applied with minimal disruption
- **User Control**: Choose "Update Now" or "Remind Me Later" when prompted
- **Manual Checks**: You can always manually check for updates via the system tray menu

If an update fails due to network issues or verification problems, the application will continue running on the current version without disruption. You can retry the update at any time.

## Customization Options

The DAOC Sprint Manager offers several customization options in the Configuration GUI:

- **Start Minimized to Tray**: When enabled, the application starts directly in the system tray without showing any window, useful for autostart configurations.
- **Minimize GUI to Tray**: When enabled, GUI windows (Configuration, Profiles, Performance Stats) minimize to the tray instead of closing when you click the X button.
- **Background Update Checking**: Configure automatic checking for updates at a specified interval (hours).
- **Theme Settings**: (if available)
- **Profile-specific settings**: Configure different behaviors for different game characters.

## Troubleshooting

If you encounter issues with the application:

1. Check the application logs in the logs directory
2. Use the "Export Diagnostic Report" option from the tray menu to generate a comprehensive troubleshooting package
3. Review the "Known Issues" documentation
4. Submit an issue on GitHub with the diagnostic report attached (excluding any personal information)

## Recent Updates

### Version 0.5.0 (2024-05-13)
- Added Performance Statistics Display for real-time monitoring of system resources
- Implemented Diagnostic Report Export functionality for troubleshooting
- Added UI customization options (Start Minimized to Tray, Minimize to Tray instead of Close)
- Enhanced Auto-Update with periodic background checks and notifications
- Updated Pydantic models to V2 style validators
- Improved thread management and resource cleanup
- See [CHANGELOG.md](CHANGELOG.md) for complete details
- Download: [DAOC Sprint Manager v0.5.0](https://github.com/Aycrith/DAOCSprintManager/releases/tag/v0.5.0)

### Version 0.4.0 (2024-04-29)
- Introduced automatic update system with secure download and installation
- Added background update checking with user notifications
- Implemented SHA256 checksum verification for update integrity
- Added update deferral tracking with escalating notifications
- Enhanced system tray menu with update options
- Improved error handling for download and verification failures
- Added comprehensive update testing framework

### Version 0.3.0 (2024-04-01)
  - Released on GitHub at https://github.com/Aycrith/DAOCSprintManager
  - Added comprehensive performance testing framework
  - Improved system tray icon handling
  - Enhanced stability and error recovery
  - Complete release notes available in the GitHub release

- **v0.3.0-pre (2024-04-01)**: Fixed system tray icon creation issue. The application now properly handles icon sizing parameters from settings.

## Testing & Coverage (Updated 2024-06-05)

- The project includes a comprehensive suite of unit and integration tests for its core Python modules (`WindowManager`, `IconDetector`, `InputManager`), key UI components (`ConfigGUI`, `SprintManagerApp`), and their primary interactions (`test_detection_flow.py`).
- These tests utilize `unittest`, `pytest`, and extensive mocking to ensure functionality and robustness.
- Test coverage for these primary modules and workflows is high, focusing on logic, error handling, and component interactions.
- To run tests and generate coverage reports:

  ```sh
  # Ensure you have test dependencies installed (see test_requirements.txt)
  # From the project root directory:
  python run_tests.py

```

## Performance Testing

The DAOC Sprint Manager includes comprehensive performance testing capabilities to ensure efficient operation on various systems. These tools allow for monitoring CPU usage, memory consumption, and overall application performance.

### Running Performance Tests

To run the performance tests, use the following commands:

```bash
# Run basic performance test (30 minutes)
python -m testing.performance_test_runner --test baseline --duration 1800

# Run extended stability test (4 hours)
python -m testing.performance_test_runner --test long_duration --duration 14400

# Run high-load test with increased FPS
python -m testing.performance_test_runner --test high_fps --duration 3600
```

Test results are saved to the `test_results` directory, including:
- Time series metrics in JSON and CSV formats
- Summary statistics with average and peak resource usage
- Performance logs for detailed analysis

### Performance Recommendations

For optimal performance:

1. Maintain a stable frame rate with the `--capture-fps` setting
2. Use 'template' detection method for lower CPU usage
3. Ensure adequate system resources (2GB RAM recommended)
4. Limit background applications during gameplay

## Performance Considerations

The DAOC Sprint Manager is designed to be lightweight and efficient, with minimal impact on game performance. Here are some key performance characteristics and recommendations:

### Resource Usage
- **CPU:** Typically uses 2-5% CPU when idle, 15-20% during active detection
- **Memory:** Base footprint of ~50MB, peaks at ~100MB
- **Disk:** Minimal disk I/O, mainly for logging

### Optimization Tips
1. **ROI Configuration:**
   - Keep the Region of Interest (ROI) as small as possible
   - Focus only on the sprint icon area
   - Use the ROI helper tool for precise selection

2. **FPS Settings:**
   - Default 30 FPS is recommended for most systems
   - Lower FPS if running on older hardware
   - Higher FPS provides minimal benefit

3. **Detection Method:**
   - Template matching is CPU-efficient for most setups
   - ML detection may require more resources
   - Choose based on your system capabilities

4. **Profile Management:**
   - Create separate profiles for different characters
   - Disable auto-switching if not needed
   - Remove unused profiles

### System Requirements
- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- Modern dual-core processor
- 100MB free disk space

### Known Performance Impacts
- Initial startup may take 1-2 seconds
- First detection after pause may have slight delay
- CPU usage increases during active detection
- Multiple profiles may increase memory usage slightly
