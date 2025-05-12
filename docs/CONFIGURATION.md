# DAOC Sprint Manager Configuration Guide

This document provides a comprehensive guide to configuring the DAOC Sprint Manager application through its settings file.

## Configuration File Location

The application's settings are stored in `config/settings.json`. On first run, this file is created from the template if it doesn't exist. You can also copy `config/settings.json.template` manually and modify it.

## Settings Categories

### Game Window Settings
- `game_window_title` (string): Window title to search for. Should match a unique part of the game's window title.
  - Default: `"Dark Age of Camelot"`

### Region of Interest (ROI) Settings
These settings define the area of the game window where the sprint icon appears:
- `roi_x` (integer): X-coordinate of the top-left corner of the region of interest
  - Default: `200`
- `roi_y` (integer): Y-coordinate of the top-left corner of the region of interest
  - Default: `200`
- `roi_width` (integer): Width of the region of interest in pixels
  - Default: `100`
- `roi_height` (integer): Height of the region of interest in pixels
  - Default: `100`

### Icon Template Settings
- `sprint_on_icon_path` (string): Path to the sprint 'ON' icon template image
  - Default: `"data/icon_templates/sprint_on.png"`
- `sprint_off_icon_path` (string): Path to the sprint 'OFF' icon template image
  - Default: `"data/icon_templates/sprint_off.png"`
- `template_match_threshold` (float): Confidence threshold for template matching (0.0-1.0)
  - Default: `0.8`

### Temporal Consistency Settings
- `temporal_consistency_frames` (integer): Number of consecutive consistent frames required to confirm a state change
  - Default: `3`

### Input Settings
- `sprint_key` (string): Keyboard key to press/release for sprint toggle
  - Default: `"z"`

### Performance Settings
- `capture_fps` (float): Target frames per second for capture and detection loop
  - Default: `10.0`
- `game_not_found_retry_delay_s` (float): Delay in seconds between retries when game window is not found
  - Default: `2.0`
- `capture_error_retry_delay_s` (float): Delay in seconds between retries when capture fails
  - Default: `1.0`
- `show_performance_metrics` (boolean): Whether to periodically log performance metrics
  - Default: `true`

### Cache Settings
- `enable_detection_cache` (boolean): Whether to cache detection results to reduce redundant processing
  - Default: `true`
- `detection_cache_size` (integer): Maximum number of frames to keep in the detection cache
  - Default: `50`
- `detection_cache_ttl_s` (float): Time-to-live for cache entries in seconds
  - Default: `0.5`

### Logging Settings
- `log_level` (string): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Default: `"INFO"`
- `log_file_name` (string): Name of the log file in the logs directory
  - Default: `"daoc_sprint_manager.log"`

### UI Settings
- `app_icon_path` (string): Path to the application icon image for system tray
  - Default: `"data/app_icon.png"`
- `start_minimized_to_tray` (boolean): Whether to start the application minimized to system tray
  - Default: `false`
- `minimize_gui_to_tray` (boolean): Whether GUI windows minimize to tray instead of closing
  - Default: `true`

### Update Settings
- `background_update_check_enabled` (boolean): Enable periodic background checking for application updates
  - Default: `true`
  - *Added in v0.5.0*
- `background_update_check_interval_hours` (integer): Interval in hours between background update checks (1-168)
  - Default: `24`
  - *Added in v0.5.0*
- `auto_download_updates` (boolean): Automatically download updates when available
  - Default: `false`
- `auto_install_updates` (boolean): Automatically install downloaded updates on application exit
  - Default: `false`
- `update_check_url` (string): GitHub API URL to check for updates
  - Default: `"https://api.github.com/repos/yourusername/daoc-sprint-manager/releases/latest"`
- `downloads_dir` (string): Directory to store downloaded updates, relative to the app's data directory
  - Default: `"downloads"`

### Detection Method Settings
- `detection_method` (string): Detection method to use ('template' or 'ml')
  - Default: `"template"`

### ML Detection Settings
- `ml_model_path` (string): Path to the ONNX ML model file
  - Default: `"data/models/sprint_classifier.onnx"`
- `ml_input_size_wh` (array): Required input size for the ML model as [width, height]
  - Default: `[32, 32]`
- `ml_confidence_threshold` (float): Confidence threshold for ML detection (0.0-1.0)
  - Default: `0.7`
- `save_problematic_frames` (boolean): Whether to save frames with uncertain detection scores
  - Default: `false`
- `problematic_frame_save_path` (string): Path to save problematic frames
  - Default: `"data/problem_frames"`

### Profile Settings
- `active_profile_id` (string|null): The ID of the currently active profile
  - Default: `null`
- `enable_auto_profile_switching` (boolean): Whether to automatically switch profiles based on window title patterns
  - Default: `true`
- `window_title_pattern` (string|null): Pattern to match against game window titles for auto-switching
  - Default: `null`

## Validation Rules

The application validates all settings when loading the configuration file:

1. Numeric thresholds (template_match_threshold, ml_confidence_threshold) must be between 0.0 and 1.0
2. Cache size must be between 10 and 1000
3. Cache TTL must be between 0.1 and 10.0 seconds
4. Temporal consistency frames must be between 1 and 20
5. Capture FPS must be between 0 and 120
6. Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
7. ML input size must be a list of exactly 2 positive integers
8. Detection method must be either 'template' or 'ml'
9. Update check interval must be between 1 and 168 hours (1 week)
10. Update channel must be either 'stable' or 'beta'
11. Update check URL must be a valid GitHub API URL

If validation fails for any setting, the application will log an error and use the default value for that setting. 