# DAOC Sprint Manager - Project Planning

## Project Vision

The DAOC Sprint Manager is a specialized utility for Dark Age of Camelot players that automates the management of the sprint toggle. It detects the sprint icon status on the screen and automatically toggles sprint when needed, allowing players to focus on gameplay rather than constantly managing this mechanical aspect.

## Architecture Overview

The application follows a modular architecture with clean separation of concerns:

```
DAOC Sprint Manager
├── Core Components
│   ├── Window Manager (window detection, screen capture)
│   ├── Icon Detector (template matching, ML detection)
│   └── Input Manager (key simulation)
├── UI Components
│   ├── System Tray Interface (status icon, menu)
│   ├── Configuration GUI (settings editor)
│   └── Profile Manager (character profiles)
├── Configuration System
│   ├── Config Manager (loading, saving)
│   └── Data Models (validation, defaults)
└── Utilities
    ├── ROI Helper (region selection)
    ├── Logging (error tracking)
    └── Performance Monitor (resource usage)
```

### Core Design Principles

1. **Modularity**: Components should be loosely coupled and independently testable
2. **Robustness**: Handle edge cases and recover from errors gracefully
3. **Performance**: Minimize resource usage while maintaining reliability
4. **Usability**: Prioritize ease of use and configuration for non-technical users
5. **Extensibility**: Design for future enhancements and feature additions

## Technology Stack

### Core Technologies

- **Python 3.9+**: Primary programming language
- **OpenCV**: Computer vision for template matching
- **PyDirectInput**: Low-level input simulation
- **Pillow (PIL)**: Image processing
- **PyWin32**: Windows API access
- **Tkinter**: Cross-platform GUI framework
- **ONNX Runtime** (planned): Machine learning inference

### Development Tools

- **Poetry**: Dependency management
- **Pytest**: Unit testing
- **Mypy**: Type checking
- **Black**: Code formatting
- **Pylint**: Code quality

## Implementation Plan

### Phase 1: Foundation & Basic Detection (Complete)

1. Project structure setup
2. Window detection and screen capture
3. Basic template matching
4. Configuration system
5. Console-based proof of concept

### Phase 2: Advanced Detection & Input System (Complete)

1. Enhanced detection with temporal consistency
2. Keyboard input management
3. Performance monitoring
4. System tray interface
5. Helper utilities (ROI selection)

### Phase 3: User Interface & Advanced Features (Current)

1. **Configuration GUI** (Current Focus)
   - Settings editor interface
   - Visual ROI selection
   - Input validation
   - Configuration presets

2. **Profile Management**
   - Profile data structure
   - Profile switching interface
   - Auto-profile selection
   - Profile import/export

3. **ML-Based Detection**
   - ONNX runtime integration
   - Dataset collection utility
   - ML detector implementation
   - Performance optimization

4. **Quality of Life Features**
   - Windows startup integration
   - Statistics dashboard
   - Hotkey support
   - Adaptive polling

### Phase 4: Packaging & Distribution (Future)

1. Application bundling (PyInstaller)
2. Installer creation
3. Auto-update mechanism
4. User documentation

## Technical Constraints

1. **Platform Compatibility**
   - Windows-only due to game compatibility
   - Support for Windows 10 and 11 as primary targets
   - Limited testing on Windows 7 and 8.1

2. **Performance Requirements**
   - CPU usage under 5% on modern systems
   - Memory usage under 100MB
   - Response time under 100ms
   - Minimal impact on game performance

3. **Dependencies**
   - Minimize external dependencies
   - Prefer pure Python implementations where possible
   - Ensure all dependencies are available for Windows

## Development Standards

### Code Style

- Follow PEP 8 conventions
- Use type hints throughout
- Document all public functions and classes
- Use meaningful variable and function names
- Keep functions and methods concise and focused

### Testing Strategy

- Write unit tests for all core components
- Implement integration tests for key workflows
- Add self-test capabilities to core modules
- Test on multiple Windows versions

### Error Handling

- Use proper exception handling
- Provide detailed error messages
- Log all errors with context
- Implement graceful degradation
- Auto-recovery where possible

## Current Development Focus

The immediate focus is on implementing the Configuration GUI:

1. **GUI Framework Setup**
   - Basic window structure with tabs
   - Settings loading and population
   - Save/cancel functionality

2. **Settings Panels**
   - Organized by category
   - Input validation
   - Visual feedback

3. **ROI Selection Tool**
   - Screenshot preview
   - Interactive selection
   - Coordinate display

4. **Integration with Existing Components**
   - Connect to ConfigManager
   - Add entry point from tray menu
   - Ensure thread safety

## Risk Assessment

1. **Template Matching Reliability**
   - Risk: Game updates may change icon appearance
   - Mitigation: ML-based detection as backup, easy template updates

2. **Resource Usage**
   - Risk: Screen capture and image processing may be resource-intensive
   - Mitigation: Adaptive polling, performance optimizations

3. **Game Window Detection**
   - Risk: Multiple game instances, title variations
   - Mitigation: Flexible window matching, profile system

4. **Input Simulation**
   - Risk: Game may ignore simulated input or detect as automation
   - Mitigation: Multiple input methods, configurable timing

## Future Considerations

1. **Feature Expansion**
   - Support for other game toggles/abilities
   - Advanced automation capabilities
   - Game state detection

2. **User Experience**
   - Telemetry for common issues
   - UI themes and customization
   - Interactive tutorials

3. **Architecture Evolution**
   - Plugin system for extensibility
   - Shared detection framework
   - Advanced configuration options

## 2024-06 Milestone
- Achieved >84% test coverage, focusing on reliability and maintainability.
- The project is now in a stable, well-tested state, ready for further development or deployment.

## Performance Testing Framework

The DAOC Sprint Manager includes a comprehensive performance testing framework to validate the application's resource usage, stability, and behavior under various conditions.

### Components

1. **Performance Test Runner**: A configurable tool for executing different performance test scenarios
   - Baseline tests for standard performance benchmarking
   - Long-duration tests for stability validation
   - High FPS tests for stress testing

2. **Mock Application**: A simulated version of the sprint manager that mimics core functionality
   - Configurable via command-line arguments
   - Simulates resource usage patterns similar to the real application
   - Runs in test mode for isolated testing

3. **Performance Monitor**: Collects detailed metrics during test execution
   - CPU and memory usage tracking
   - Time series data collection
   - Summary statistics generation
   - JSON and CSV export capabilities

### Test Workflow

1. Configure test parameters (duration, FPS, detection method)
2. Launch mock application with specified configuration
3. Monitor application behavior and resource usage
4. Generate performance reports and metrics
5. Analyze results for optimizations and regressions

### Test Scenarios

- **Baseline Test**: 30-minute test with standard parameters to establish performance benchmarks
- **Long Duration Test**: 4-hour test to evaluate stability and resource leaks
- **High FPS Test**: 1-hour test with increased frame rate to evaluate performance under load

### Usage

```bash
# Run baseline test
python -m testing.performance_test_runner --test baseline --duration 1800

# Run long duration test
python -m testing.performance_test_runner --test long_duration --duration 14400

# Run high FPS test
python -m testing.performance_test_runner --test high_fps --duration 3600
``` 