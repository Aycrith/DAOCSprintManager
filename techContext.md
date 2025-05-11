# DAOC Sprint Manager - Technical Context

## Technology Stack

### Core Technologies

- **Python 3.8+**: Primary development language
- **OpenCV (cv2)**: Computer vision library for image processing and template matching
- **NumPy**: Numerical processing for image data
- **PyGetWindow**: Windows GUI interaction for finding and capturing game windows
- **PyDirectInput**: Direct keyboard input simulation
- **PyStray**: System tray icon and menu functionality
- **Pillow (PIL)**: Image processing and manipulation
- **Tkinter/PyQt** (Phase 3): GUI frameworks for configuration dialogs
- **ONNX Runtime** (Phase 3): Machine learning inference for advanced detection

### Development Tools

- **Git**: Version control
- **VSCode/PyCharm**: Recommended IDEs for development
- **Pip**: Package management
- **PyInstaller** (Phase 4): Application packaging for distribution

## System Architecture

The application follows a modular design with clear separation of concerns:

### Core Layer

- **window_manager.py**: Responsible for finding, activating, and capturing game windows
- **icon_detector.py**: Handles template matching and temporal consistency logic
- **input_manager.py**: Manages keyboard input with safety validations

### Application Layer

- **tray_app.py**: Implements the system tray UI and application lifecycle
- **config_manager.py**: Handles loading, validation, and saving of configuration
- **main.py**: Application entry point and orchestration

### Utility Layer

- **performance_monitor.py**: Tracks system resource usage and performance metrics
- **logger.py**: Centralized logging functionality
- **data_models.py**: Data structures and validation for configuration

### Helper Tools

- **create_test_templates.py**: Generates test template images
- **roi_helper.py**: Visual tool for configuring the Region of Interest

## Architectural Patterns

1. **Module-based Architecture**: Functionality is separated into logical modules
2. **Thread-based Concurrency**: UI and detection logic run in separate threads
3. **Composition over Inheritance**: Components are composed rather than inherited
4. **Dependency Injection**: Components receive their dependencies via constructor parameters
5. **Fail-safe Error Handling**: Comprehensive error handling with fallbacks

## Data Flow

1. Window Manager locates the game window and captures the Region of Interest (ROI)
2. Icon Detector analyzes the captured ROI for the sprint icon using template matching
3. Temporal consistency logic reduces false positives/negatives
4. Input Manager sends keyboard commands based on detection results
5. Performance Monitor tracks resource usage and calculates metrics
6. Tray Application provides user feedback and control

## Configuration Management

- **settings.json**: Primary configuration file
- **settings.json.template**: Default configuration template
- Settings are validated during load with fallbacks to defaults
- User can modify via text editor or configuration GUI (Phase 3)

## Extension Points (Phase 3)

1. **Plugin System**: Allow custom detectors and input strategies
2. **Profile System**: Support multiple configurations for different characters
3. **ML Integration**: Add machine learning-based detection alongside template matching
4. **Advanced UI**: Enhance with statistics display and configuration dialogs

## Technical Constraints

1. **Windows-only**: Due to dependencies on PyGetWindow and PyDirectInput
2. **Python Runtime**: Requires Python interpreter unless packaged as executable
3. **Game Window Access**: Requires visible, non-minimized game window
4. **Screen Resolution**: Must adapt to various screen resolutions and game UI settings 

## Testing & Tooling (2024-06)
- Test suite uses unittest, pytest, and coverage for automated testing and reporting.
- Python 3.12+ compatibility.
- Focus on test-driven reliability and maintainability in the latest milestone. 