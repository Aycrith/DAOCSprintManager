# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2024-05-13

### Added
- UI Performance Statistics Display: Real-time window for CPU, memory, FPS, and session stats.
- Diagnostic Report Export: Feature to generate a ZIP file with logs, system info, and settings for troubleshooting.
- User Interface Customization: 'Start Minimized to Tray' option.
- User Interface Customization: 'Minimize GUI Windows to Tray instead of Closing' option for dialogs.
- Auto-Update Enhancement: Periodic background check for updates with system tray notification.

### Changed
- Updated Pydantic models to use V2 style validators, resolving deprecation warnings.
- Improved thread management and resource cleanup.
- Enhanced test stability and error handling.

## [0.4.0] - 2024-04-29

### Added
- Profile Management System: Create, edit, and switch between detection profiles
- Advanced ROI Selection: Visual region selection for detection areas
- Auto-Profile Switching: Automatically switch profiles based on window title
- Update System: Check for updates, download, and install new versions
- Custom Icon Detection: Support for custom icon templates and ML model integration

### Changed
- Complete UI overhaul with tabbed configuration dialog
- Improved detection algorithm with confidence tracking
- Enhanced error handling and thread safety
- Added session statistics and performance monitoring

## [0.3.0] - 2024-04-01

### Added
- System tray application with status indicator
- Configuration UI for setting detection parameters
- Support for multiple detection methods (template matching and ML)
- Adjustable detection area (Region of Interest)
- Game window detection and automatic tracking
- Customizable key bindings
- Detailed logging system

### Changed
- Migrated to Python-based implementation
- Improved detection reliability
- Added support for multiple game window sizes

## [0.2.0] - 2024-03-01

### Added
- Initial release with basic sprint detection
- AutoHotkey implementation
- Support for Dark Age of Camelot Classic servers

[0.5.0]: https://github.com/yourusername/daoc-sprint-manager/releases/tag/v0.5.0
[0.4.0]: https://github.com/yourusername/daoc-sprint-manager/releases/tag/v0.4.0
[0.3.0]: https://github.com/yourusername/daoc-sprint-manager/releases/tag/v0.3.0
[0.2.0]: https://github.com/yourusername/daoc-sprint-manager/releases/tag/v0.2.0 