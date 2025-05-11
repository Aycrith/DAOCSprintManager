# Changelog

All notable changes to the DAOC Sprint Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-03-20

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