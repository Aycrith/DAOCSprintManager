# Changelog

All notable changes to the DAOC Sprint Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2024-07-15

### Added
- Performance Statistics UI
  - Real-time monitoring of application performance metrics
  - CPU and memory usage statistics
  - Detection rate and frame processing time display
  - Session statistics with reset capability
- Diagnostic Report Export
  - Comprehensive system information collection
  - Application logs bundling
  - Settings export for troubleshooting
  - One-click ZIP file generation with customizable save location
- User Interface Enhancements
  - "Start Minimized to Tray" option for autostart configurations
  - "Minimize GUI to Tray" for Config, Profiles, and Stats windows
  - Improved system tray menu organization
  - Enhanced tooltip information
- Background Update Checking
  - Periodic automatic checks for new versions
  - Configurable check interval
  - Unobtrusive system tray notifications
  - Dynamic menu updates when updates are available

### Changed
- Updated to Pydantic v2 validation methods
- Improved error handling for GUI operations
- Enhanced application startup sequence
- Reorganized ConfigGUI "Advanced" tab into logical sections
- Optimized dialog handling and lifecycle management
- Improved system tray icon handling

### Fixed
- Window state persistence issues when switching between configurations
- System tray icon title update handling
- Dialog parent-child relationship management
- Error handling in profile switching operations
- Thread safety issues in background operations

## [0.4.0] - 2024-06-28

### Added
- Auto-Update Mechanism:
  - Implemented `UpdateManager` class for handling software updates
  - Version checking against remote/local version information source
  - Secure download of update packages with SHA256 checksum verification
  - Automated application of updates via batch script (handles backup, file replacement, cleanup, and app restart)
  - User notification system with tray notifications for available updates
  - "Update Now" and "Remind Me Later" options for user control
  - Update deferral tracking with escalating prompts after multiple deferrals
  - Background update check thread with configurable check interval
  - Manual "Check for Updates" option in system tray menu
  - Graceful error handling for download failures and checksum verification issues
  - Update progress notification during download
- End-to-End Update Process Testing Framework
  - Test environment setup scripts
  - Comprehensive test scenarios for all update paths
  - Verification procedures for update integrity

### Changed
- Enhanced system tray menu with update-related options and status indicators
- Improved application restart handling for updates
- Added startup check for pending downloaded updates
- Enhanced error reporting and user feedback for update-related actions
- Updated configuration options for update behavior

### Security
- Implemented SHA256 checksum verification for downloaded updates
- Added secure temporary directory handling for update downloads
- Implemented backup and rollback capabilities for failed updates
- Validated update package integrity before installation

## [0.3.0] - 2024-06-11

### Added
- Performance testing framework
  - `performance_test_runner.py` for automated test scenarios
  - `mock_application.py` for controlled testing environment
  - `performance_monitor.py` for resource usage tracking
- Comprehensive performance metrics tracking
  - CPU usage monitoring (average and peak)
  - Memory consumption tracking
  - Frame processing time measurements
  - Long-duration stability testing
- Quick Start Guide for new users
- Known Issues documentation
- Performance optimization task tracking
- Auto-update framework
  - `UpdateManager` class for version checking
  - Automatic update check on application startup
  - Manual "Check for Updates" option in system tray menu
  - Foundation for future automatic update installation

### Changed
- Optimized screen capture operations
- Improved template matching efficiency
- Enhanced memory management
- Updated README with performance considerations
- Refined error handling and recovery
- Improved profile management system

### Fixed
- Memory leak in long-running sessions
- CPU usage spikes during profile switches
- Delayed window detection after game launch
- System tray icon persistence after crashes
- ROI coordinate shifts on resolution changes

### Performance Improvements
- Reduced idle CPU usage to 2-5%
- Optimized active detection CPU usage to 15-20%
- Decreased base memory footprint to ~50MB
- Improved frame processing times to 15-30ms
- Enhanced stability for 8+ hour sessions

## [0.2.1] - 2024-02-15

### Added
- ML detection method support
- Auto-profile switching capability
- Basic performance monitoring

### Fixed
- Template matching accuracy issues
- Profile corruption handling
- Window detection reliability

## [0.2.0] - 2024-01-30

### Added
- Multiple profile support
- ROI selection helper tool
- System tray integration
- Basic configuration GUI

### Changed
- Improved detection accuracy
- Enhanced error reporting
- Updated documentation

## [0.1.0] - 2024-01-15

### Added
- Initial release
- Basic sprint detection
- Template matching method
- Single profile support
- Configuration file
- Command line interface 