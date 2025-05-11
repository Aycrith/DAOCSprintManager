# DAOC Sprint Manager - Project Brief

## Project Overview

The DAOC Sprint Manager is a Python application designed to automate sprint key management for the game "Dark Age of Camelot" (DAOC). It continuously monitors the game window for the presence of a sprint icon and automatically presses the appropriate key when needed.

## Project Goals

1. Create a reliable, low-resource application that detects the sprint icon status in DAOC
2. Automatically manage sprint key presses based on icon detection
3. Provide a simple, unobtrusive user interface through the system tray
4. Implement robust error handling and fallback mechanisms
5. Ensure compatibility with various game window sizes and UI configurations

## Development Phases

The project is being developed in four phases:

1. **Phase 1 (COMPLETED)**: Foundation & Basic Detection
   - Basic window capture
   - Template-based icon detection
   - Console-based application

2. **Phase 2 (COMPLETED)**: Advanced Detection & Input System
   - Enhanced detection with temporal consistency
   - Keyboard input system
   - Performance monitoring
   - System tray UI

3. **Phase 3 (CURRENT)**: Robustness & Advanced Features
   - Machine learning-based detection option
   - Multi-profile support for different characters
   - Enhanced UI with configuration dialog
   - Quality-of-life improvements

4. **Phase 4 (FUTURE)**: Optimization & Packaging
   - Performance optimization
   - Comprehensive documentation
   - Packaging for distribution
   - Installer creation

## Project Scope

### In Scope

- Game window detection and capture
- Icon recognition using template matching and ML
- Keyboard input simulation
- System tray user interface
- Configuration management
- Performance monitoring
- Multi-profile support
- Helper utilities for setup and configuration

### Out of Scope

- Game client modification
- Packet interception or game data analysis
- Complex automation beyond sprint key management
- Support for operating systems other than Windows

## Target Users

The primary users are players of Dark Age of Camelot who want to automate the management of sprint to improve gameplay experience without manual key presses.

## Success Criteria

1. Accurately detects sprint icon state with minimal false positives/negatives
2. Operates with minimal CPU/GPU resource usage (<5% CPU, <100MB RAM)
3. Works consistently across different game window sizes and UI settings
4. Provides intuitive configuration and feedback to users
5. Maintains stability during extended gameplay sessions

## Recent Milestone
- Achieved robust test coverage (>84%) for the DAOC Sprint Manager, focusing on the performance monitoring module and related infrastructure.
- The test suite now covers installation structure, configuration, templates, executables, resource validation, profile management, settings validation, and comprehensive performance monitoring (including error handling and main function coverage).
- This milestone significantly improves the reliability and maintainability of the codebase.
- Remaining uncovered lines are rare error paths that are difficult to trigger in automated tests. 