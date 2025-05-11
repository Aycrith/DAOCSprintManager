# DAOC Sprint Manager (Python)

A Python-based utility to automatically manage sprint toggling in Dark Age of Camelot.

## Features

- Automated sprint detection and activation
- Configurable detection methods (template matching or ML-based)
- Profile management system
- System tray interface
- Customizable settings via GUI

## Requirements

... (requirements) ...

## Installation

... (installation steps) ...

## First-Time Setup & Configuration

... (setup steps) ...

## Usage

... (usage steps) ...

## Troubleshooting

... (troubleshooting) ...

## Recent Updates

- **v0.3.0-pre (2024-06-11)**: Fixed system tray icon creation issue. The application now properly handles icon sizing parameters from settings.

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
