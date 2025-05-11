<Role_and_Operational_Mandate>
You are an expert Python 3.9+ software engineer. Your mission is the meticulous and sequential implementation of the multi-phase software project detailed below for the "DAOC Sprint Manager."

Your operational protocol is as follows:
1.  **Sequential Execution:** You will be instructed to complete specific Phases or blocks of Deliverables. Do NOT proceed to subsequent Phases or major task blocks until EXPLICITLY INSTRUCTED.
2.  **Deliverable Generation:** For each specified "Deliverable," you MUST provide the COMPLETE, RUNNABLE Python code, file contents (e.g., for `.gitignore`, `README.md`, JSON templates), or fulfill the specified action. All necessary imports, class definitions, and function definitions must be included.
3.  **Adherence to Plan:** Strictly adhere to the defined file structures, module organization, class designs, and method implementations as laid out in the project plan.
4.  **Confirmation of Creation:** For each file or directory structure you are asked to create or provide content for, explicitly confirm its creation or the provisioning of its content (e.g., "Created empty file: src/daoc_sprint_manager/__init__.py", "Provided content for daoc_sprint_manager/.gitignore.").

<Universal_Code_Quality_and_Architectural_Standards>
All Python code you generate MUST adhere to the following universal standards without exception:
1.  **Python Version:** Utilize Python 3.9+ syntax and features.
2.  **Type Hinting:** Implement strict and complete type hints for ALL function and method parameters and return values.
3.  **Style Guidelines:** Adhere rigorously to PEP 8 Python style guidelines.
4.  **Docstrings:** Provide comprehensive docstrings (Google Python Style) for all modules, classes, and functions. Docstrings must clearly state purpose, arguments (with types), return values (with types), and any specific errors raised or handled.
5.  **Error Handling:** Prioritize explicit and specific error handling (e.g., `try-except FileNotFoundError`, `try-except cv2.error`). Implement clear logging of errors and define fallback behaviors (e.g., using defaults, retrying, or exiting gracefully).
6.  **Module Self-Tests:** For each coded deliverable (Python module), provide specific instructions or code within an `if __name__ == "__main__":` block to demonstrate and test its basic functionality independently. This self-test should not rely on other unimplemented modules unless explicitly stated.
7.  **Path Management:** Use `pathlib.Path` for all file system I/O operations.
8.  **Text Encoding:** Specify text encoding (e.g., `encoding='utf-8'`) where applicable for file operations.
9.  **Configuration Values:** Placeholder values in configurations should be clearly marked (e.g., "REPLACE_WITH_ACTUAL_X") or use sensible defaults that allow the application to run in a degraded mode for testing, if possible.
10. **Imports:** Ensure all code snippets or files include all necessary imports to be runnable.

<Project_Plan_and_Tasks>
The DAOC Sprint Manager project is detailed below. The goal is to develop a high-performance, reliable, resource-efficient, and maintainable Python application to monitor the sprint icon in the game "Dark Age of Camelot" (DAOC) and interact accordingly. This plan is engineered for AI-driven development, prioritizing robust architecture, explicit contracts, comprehensive error handling, and progressive feature implementation using modern, well-documented practices.

[[[The rest of this prompt is the *original* detailed development plan, starting from "Optimized Development Plan v3: Python-Based DAOC Sprint Manager" and going all the way to the end, including the "Immediate Next Steps for AI Agent (Claude, etc.)". Any parts like "IGNORE_WHEN_COPYING_START", "content_copy", "download", "Use code with caution.", "Json", "Python", and "IGNORE_WHEN_COPYING_END" artifacts should be considered removed as they are metadata from the prompting environment and not for the LLM. The core plan text itself (deliverables, file contents, code structure details) is to be preserved verbatim from the original prompt.]]]

Optimized Development Plan v3: Python-Based DAOC Sprint Manager

Project Goal: Develop a high-performance, reliable, resource-efficient, and maintainable Python application to monitor the sprint icon in the game "Dark Age of Camelot" (DAOC) and interact accordingly. This plan is engineered for AI-driven development, prioritizing robust architecture, explicit contracts, comprehensive error handling, and progressive feature implementation using modern, well-documented practices.

Pre-Phase: Project Setup & Foundation

Objective: Establish a robust, reproducible development environment and core utilities with clear interfaces and strong typing.

Instructions to AI for Pre-Phase: You will now execute the following setup steps and generate the specified files. All Python code generated must use type hints for all function/method parameters and return types. Assume Python 3.9+ environment.

1.  **Project Directory Structure and Git:**
    *   The top-level project directory will be `daoc_sprint_manager`.
    *   A Git repository will be initialized.
    *   A Python virtual environment is assumed (e.g., `python -m venv .venv`). Activation is a user step.
    *   **Deliverable:** Provide the exact content for `daoc_sprint_manager/.gitignore` using a standard Python template (e.g., from gitignore.io).
    *   **Deliverable:** Provide the exact content for `daoc_sprint_manager/README.md` (include project title: "DAOC Sprint Manager", and purpose: "A Python application to monitor the 'Dark Age of Camelot' sprint icon and automate sprint key presses. Developed with AI assistance.").
    *   **Deliverable:** Provide the exact content for `daoc_sprint_manager/requirements.txt`. Initial content:
        ```
        opencv-python>=4.5
        numpy>=1.20
        pystray>=0.17
        pygetwindow>=0.0.9
        Pillow>=9.0
        pydirectinput>=1.0
        psutil>=5.8
        # onnxruntime will be added in Phase 3 if ML is pursued
        # keyboard will be added in Phase 3 if diagnostic hotkey is implemented
        # PyQt6 will be added in Phase 4 if advanced UI is pursued
        ```
    *   **Deliverable:** Generate the following initial directory and file structure. All `__init__.py` files should be created empty. Confirm the creation of each file/directory structure (e.g., "Created empty file: `src/daoc_sprint_manager/__init__.py`").
        ```
        daoc_sprint_manager/
        ├── .venv/
        ├── src/
        │   └── daoc_sprint_manager/
        │       ├── __init__.py
        │       ├── config_manager.py
        │       ├── core/
        │       │   ├── __init__.py
        │       │   ├── icon_detector.py
        │       │   ├── input_manager.py
        │       │   └── window_manager.py
        │       ├── ui/
        │       │   ├── __init__.py
        │       │   └── tray_app.py
        │       ├── utils/
        │       │   ├── __init__.py
        │       │   └── logger.py
        │       ├── data_models.py
        │       └── main.py
        ├── tests/
        │   └── __init__.py
        ├── data/
        │   ├── icon_templates/
        │   └── app_icon.png
        ├── config/
        │   └── settings.json.template
        ├── .gitignore
        ├── README.md
        └── requirements.txt
        ```

2.  **Logging Framework Setup:**
    *   File: `src/daoc_sprint_manager/utils/logger.py`
    *   Content: Implement a function `setup_logger(name: str, log_file_path: pathlib.Path, level: int = logging.INFO, max_bytes: int = 5*1024*1024, backup_count: int = 2) -> logging.Logger`.
        *   Logger should output to console (`logging.StreamHandler`) and a rotating file (`logging.handlers.RotatingFileHandler` configured with `log_file_path`, `max_bytes`, `backup_count`).
        *   Log format: `%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s`.
        *   Handle potential `IOError` or `PermissionError` during file handler setup by logging a warning to a basic console logger and proceeding with console-only logging if file setup fails.
    *   Testing: In `if __name__ == "__main__":`, demonstrate creating a logger, logging messages at different levels (DEBUG, INFO, ERROR). Configure a temporary log file path for testing. Ensure basic console logger is used if file path is intentionally made invalid for a test case.
    *   **Deliverable:** Full content of `logger.py`.

3.  **Data Models for Configuration:**
    *   File: `src/daoc_sprint_manager/data_models.py`
    *   Content: Define a dataclass named `AppSettings`.
        *   Import `dataclasses.dataclass` and `pathlib.Path`.
        *   Fields must match keys in `settings.json.template` with appropriate type hints (e.g., `log_level: str`, `roi_x: int`, `template_match_threshold: float`). Path-like settings (e.g., `sprint_on_icon_path`) should be typed as `str` here, as they come from JSON as strings. They will be resolved to full paths by consuming code using a base project directory.
        *   Provide default values for all fields directly in the dataclass definition, matching the defaults in `settings.json.template`.
        *   Example field: `game_window_title: str = "Dark Age of Camelot"`
    *   Testing: In `if __name__ == "__main__":`, instantiate `AppSettings` with default values and print it. Instantiate with a few overridden values (simulating loaded JSON) and print it.
    *   **Deliverable:** Full content of `data_models.py`.

4.  **Configuration Management Setup:**
    *   File: `src/daoc_sprint_manager/config_manager.py`
    *   Content: Implement `ConfigManager` class.
        *   Imports: `json`, `pathlib`, `logging`, `shutil`, `typing.Optional`, and `AppSettings` from `..data_models` (relative import).
        *   `__init__(self, settings_file_path: pathlib.Path, template_file_path: pathlib.Path, logger: logging.Logger)`
        *   `load_settings(self) -> AppSettings`:
            *   If `settings_file_path` doesn't exist:
                *   Log a warning.
                *   Attempt to copy `template_file_path` to `settings_file_path` using `shutil.copy`. If copy fails (e.g. `FileNotFoundError` for template, `IOError`, `PermissionError`), log error and return `AppSettings()` (all default values).
                *   Log info that template was copied.
            *   Try to open and load settings from `settings_file_path` (use `encoding='utf-8'`).
            *   Handle `FileNotFoundError` (should be rare if copy logic worked, but good for robustness), `json.JSONDecodeError`. If errors occur, log, and return `AppSettings()` with defaults.
            *   Create an `AppSettings` instance by overriding defaults with values from the loaded JSON dictionary (`AppSettings(**loaded_json_data)`). This naturally handles missing keys in JSON (defaults are used) and extra keys in JSON (they are ignored by dataclass constructor).
            *   Validation (example): Check if `0.0 <= loaded_settings.template_match_threshold <= 1.0`. If not, log a warning, and clamp the value or revert to the default from `AppSettings()`. Perform similar sensible checks for ROI dimensions (e.g., width/height > 0).
            *   Return the validated (or default) `AppSettings` instance.
    *   File: `config/settings.json.template`
    *   Content (JSON): (Ensure this matches `AppSettings` fields and defaults)
        ```json
        {
          "log_level": "INFO",
          "log_file_name": "app.log",
          "game_window_title": "Dark Age of Camelot",
          "roi_x": 0,
          "roi_y": 0,
          "roi_width": 50,
          "roi_height": 50,
          "sprint_on_icon_path": "data/icon_templates/sprint_on.png",
          "sprint_off_icon_path": "data/icon_templates/sprint_off.png",
          "template_match_threshold": 0.8,
          "detection_failure_threshold": 0.5,
          "capture_fps": 10,
          "temporal_consistency_frames": 3,
          "sprint_key": "r",
          "input_delay_ms": 50,
          "show_performance_metrics": true,
          "detection_method": "template",
          "game_not_found_retry_delay_s": 5,
          "capture_error_retry_delay_s": 2,
          "inactive_window_poll_delay_s": 1.0,
          "app_icon_path": "data/app_icon.png"
        }
        ```
    *   Testing: In `if __name__ == "__main__":`, use a temporary directory. Create a dummy logger. Simulate scenarios: no settings file (template should be copied), corrupted settings file (defaults used), valid settings file with some custom values, settings file with missing/extra keys. Check that `AppSettings` instance is correctly populated or defaults are used.
    *   **Deliverables:** Full content of `config_manager.py` and `config/settings.json.template`.

5.  **Initial Main Application Entry Point:**
    *   File: `src/daoc_sprint_manager/main.py`
    *   Content:
        *   Imports: `logging`, `pathlib`, `time`, `sys`. `setup_logger` from `.utils.logger`. `ConfigManager` from `.config_manager`. `AppSettings` from `.data_models`.
        *   `ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent` (this points to `daoc_sprint_manager/` project root from `src/daoc_sprint_manager/main.py`).
        *   In a `run_application()` function:
            *   Define paths using `ROOT_DIR`: `settings_file = ROOT_DIR / "config" / "settings.json"`, `template_file = ROOT_DIR / "config" / "settings.json.template"`.
            *   `log_file_path_prelim = ROOT_DIR / "startup_app.log"` (preliminary before reading config).
            *   Create a basic console logger: `prelim_logger = setup_logger("startup", log_file_path_prelim, logging.DEBUG)`
            *   Initialize `ConfigManager(settings_file, template_file, prelim_logger)` and load `app_settings: AppSettings = config_manager.load_settings()`.
            *   `actual_log_file_path = ROOT_DIR / app_settings.log_file_name`
            *   Set up the main application logger: `main_logger = setup_logger("DAOCSprintManager", actual_log_file_path, getattr(logging, app_settings.log_level.upper(), logging.INFO))`.
            *   `main_logger.info("Application initializing...")`.
            *   `main_logger.debug(f"Loaded settings: {app_settings}")`.
            *   `main_logger.debug(f"Project Root Directory: {ROOT_DIR}")`.
            *   (Placeholder for future logic) `main_logger.info("Main application logic would start here.")`
        *   Add a `try...except KeyboardInterrupt: main_logger.info("Application terminated by user.") finally: main_logger.info("Application shutdown complete.")`.
        *   Call `run_application()` in an `if __name__ == "__main__":` block.
    *   **Deliverable:** Full content of `main.py`.

Phase 1: Foundation & Basic Detection

Objective: Establish robust window capture, implement reliable template matching for icon detection using OpenCV, and create a console-based application demonstrating this.

1.  **Window Manager (`src/daoc_sprint_manager/core/window_manager.py`):**
    *   Imports: `pygetwindow`, `PIL.ImageGrab`, `PIL.Image`, `PIL.UnidentifiedImageError`, `numpy as np`, `cv2`, `typing.Optional`, `typing.Tuple`, `logging`.
    *   Class `WindowManager`:
        *   `__init__(self, logger: logging.Logger)`: Store logger.
        *   `find_window(self, title_substring: str) -> Optional[pygetwindow.BaseWindow]`:
            *   Uses `pygetwindow.getWindowsWithTitle(title_substring)`. Returns first match from the list, or `None`.
            *   Logs if found (with window title and class), if not found, or if multiple are found (logs which one is chosen). Handles `pygetwindow.PyGetWindowException` by logging and returning `None`.
        *   `capture_roi_from_window(self, window: pygetwindow.BaseWindow, roi_x: int, roi_y: int, roi_width: int, roi_height: int) -> Optional[np.ndarray]`:
            *   Calculates absolute screen ROI: `abs_x = window.left + roi_x`, `abs_y = window.top + roi_y`.
            *   Validates ROI: `roi_width > 0`, `roi_height > 0`. Log error and return `None` if invalid. Ensure `window.left`, `window.top`, `window.width`, `window.height` are accessible and valid.
            *   Captures using `ImageGrab.grab(bbox=(abs_x, abs_y, abs_x + roi_width, abs_y + roi_height), all_screens=True)`.
            *   Converts the Pillow Image to BGR NumPy array: `cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)`.
            *   Handles exceptions during capture (e.g., `OSError`, `ValueError` from ImageGrab arguments, `PIL.UnidentifiedImageError`), logs them with details, returns `None`.
    *   Testing: In `if __name__ == "__main__":`, get a dummy logger. Instantiate `WindowManager`. Try to find a common window (e.g., "Notepad", "Calculator" - user ensures one is open). If found, define a sample ROI (e.g., 10,10,100,100) and attempt to capture it. If capture successful, use `cv2.imshow("Test Capture", captured_image)` and `cv2.waitKey(0)` then `cv2.destroyAllWindows()`. Log all steps.
    *   **Deliverable:** Full content of `window_manager.py`.

2.  **Basic Icon Detector (`src/daoc_sprint_manager/core/icon_detector.py`):**
    *   Imports: `cv2`, `numpy as np`, `pathlib`, `typing.Optional`, `typing.Tuple`, `logging`.
    *   Class `IconDetector`:
        *   `__init__(self, logger: logging.Logger)`: Store logger.
        *   `load_template(self, template_path: pathlib.Path) -> Optional[np.ndarray]`:
            *   Checks if `template_path` exists and is a file. Logs error and returns `None` if not.
            *   Loads using `cv2.imread(str(template_path), cv2.IMREAD_COLOR)`. Icon templates must be BGR (standard PNGs without alpha are fine).
            *   Validates loaded image (not None, non-zero dimensions). Logs error/success. Returns template or `None`. Handles `cv2.error`.
        *   `detect_icon(self, frame: np.ndarray, template: np.ndarray, threshold: float) -> Tuple[bool, float, Optional[Tuple[int, int, int, int]]]`:
            *   Input frame and template must be BGR, 8-bit `np.ndarray`. Add basic assertions or checks.
            *   Check if template dimensions (`th, tw = template.shape[:2]`) are smaller than or equal to frame dimensions (`fh, fw = frame.shape[:2]`). Log error and return `(False, 0.0, None)` if not (`tw > fw` or `th > fh`).
            *   Uses `cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)`.
            *   `_minVal, maxVal, _minLoc, top_left_loc = cv2.minMaxLoc(result)`. `confidence_score = float(maxVal)`.
            *   If `confidence_score >= threshold`: `found = True`, `location_rect = (top_left_loc[0], top_left_loc[1], template.shape[1], template.shape[0])` (x, y, w, h). Ensure correct order.
            *   Else: `found = False`, `location_rect = None`.
            *   Return `(found, confidence_score, location_rect)`. Handles `cv2.error` exceptions by logging and returning `(False, 0.0, None)`.
    *   Testing: In `if __name__ == "__main__":`:
        *   Get dummy logger. Create `IconDetector`.
        *   Create a dummy frame (`np.random.randint(0, 256, (300,300,3), dtype=np.uint8)`). Create a smaller dummy template (e.g., `frame[50:100, 50:100].copy()`).
        *   Call `detect_icon` with the frame, exact template, and a high threshold (e.g., 0.99). Print results (should be found).
        *   Call `detect_icon` with the frame, a different random template, and a threshold (e.g., 0.8). Print results (likely not found).
        *   Test edge case: template larger than frame (should fail gracefully and return `False, 0.0, None`).
        *   (Optional: To test `load_template`, create a dummy `test_template.png` file with OpenCV, then load it).
    *   **Deliverable:** Full content of `icon_detector.py`.

3.  **Console-Based Main Application Update (`src/daoc_sprint_manager/main.py`):**
    *   Update `run_application()` function:
        *   Get `main_logger` and `app_settings` as established. Import necessary core modules (`WindowManager`, `IconDetector` using relative imports like `from .core.window_manager import WindowManager`).
        *   Instantiate `window_manager = WindowManager(main_logger)`.
        *   Instantiate `icon_detector = IconDetector(main_logger)`.
        *   `sprint_on_template_path = ROOT_DIR / app_settings.sprint_on_icon_path`
        *   `loaded_template = icon_detector.load_template(sprint_on_template_path)`. If `loaded_template` is `None`, log critical error and `sys.exit(1)`.
        *   Main loop: `main_logger.info("Starting main detection loop...")` then `while True:`
            *   `game_window = window_manager.find_window(app_settings.game_window_title)`. If not found, log, `time.sleep(app_settings.game_not_found_retry_delay_s)`, `continue`.
            *   `frame = window_manager.capture_roi_from_window(game_window, app_settings.roi_x, app_settings.roi_y, app_settings.roi_width, app_settings.roi_height)`. If `frame` is `None`, log, `time.sleep(app_settings.capture_error_retry_delay_s)`, `continue`.
            *   `found, score, loc_rect = icon_detector.detect_icon(frame, loaded_template, app_settings.template_match_threshold)`.
            *   `main_logger.info(f"Icon Detection: Found={found}, Confidence={score:.2f}, Location={loc_rect}")`.
            *   Implement delay: `time.sleep(max(0, 1.0 / app_settings.capture_fps))`. Ensure FPS > 0.
        *   Loop is broken by `KeyboardInterrupt` handled by the outer `try-except` block.
    *   **Deliverable:** Updated `main.py` demonstrating capture and detection cycle.

4.  **Documentation (User Task Reminder):**
    *   AI will output this as a print statement or comment during its execution of this step:
        ```
        User Task Reminder for Phase 1 Completion:
        1. Ensure you have image files for 'sprint_on.png' (and 'sprint_off.png' for later) in the 'daoc_sprint_manager/data/icon_templates/' directory. These should be clear, well-cropped PNG images (standard PNGs without transparency are fine).
        2. Review and adjust 'daoc_sprint_manager/config/settings.json' (created from the template):
           - Set 'game_window_title' to exactly match a unique part of your Dark Age of Camelot game window title.
           - Accurately set 'roi_x', 'roi_y', 'roi_width', 'roi_height' to define the Region of Interest where the sprint icon appears on your screen, relative to the game window's top-left corner.
        3. The console application should now attempt to find the window, capture this ROI, and detect the 'sprint_on.png' template.
        ```
    *   **Deliverable:** AI tô output the above reminder text.

Phase 2: Advanced Detection & Input System

Objective: Enhance detection reliability with temporal consistency. Implement a reliable keyboard input system. Integrate performance monitoring and a basic system tray UI.

1.  **Enhanced Icon Detector (`src/daoc_sprint_manager/core/icon_detector.py` - Refinement):**
    *   Temporal Consistency:
        *   Imports: Add `collections.deque`.
        *   Modify `IconDetector` class:
            *   `__init__(self, logger: logging.Logger, temporal_consistency_frames: int)`: Store `temporal_consistency_frames`. Initialize `self.detection_history = collections.deque(maxlen=temporal_consistency_frames)` and `self.confirmed_detection_state: bool = False`.
            *   New method: `update_consistent_detection_state(self, current_frame_found: bool) -> bool`:
                *   Adds `current_frame_found` to `self.detection_history`.
                *   If `len(self.detection_history) < self.detection_history.maxlen` (i.e., buffer not full yet), return `self.confirmed_detection_state` (no change until buffer full).
                *   If all items in `self.detection_history` are `True`, set `self.confirmed_detection_state = True`.
                *   Else if all items in `self.detection_history` are `False`, set `self.confirmed_detection_state = False`.
                *   (Otherwise, `self.confirmed_detection_state` remains unchanged to prevent flapping during mixed true/false history until a consistent state is observed).
                *   Return `self.confirmed_detection_state`.
    *   Testing: In `if __name__ == "__main__":` (add to existing tests):
        *   Instantiate `IconDetector` with `temporal_consistency_frames=3`.
        *   Simulate a sequence:
            *   `update_consistent_detection_state(True)` -> should return initial state (e.g. False) as buffer not full.
            *   `update_consistent_detection_state(True)` -> False
            *   `update_consistent_detection_state(True)` -> Now buffer is full, all True, so should return True. Confirmed state is True.
            *   `update_consistent_detection_state(False)` -> Buffer [T,T,F], no full consensus, return previous True.
            *   `update_consistent_detection_state(False)` -> Buffer [T,F,F], return True.
            *   `update_consistent_detection_state(False)` -> Buffer [F,F,F], return False. Confirmed state is False.
        *   Verify outputs at each step.
    *   **Deliverable:** Updated `icon_detector.py`. (Integration into main.py comes next).

2.  **Input Manager (`src/daoc_sprint_manager/core/input_manager.py`):**
    *   Imports: `pydirectinput`, `time`, `logging`, `typing.Set`.
    *   Define `VALID_KEYS: Set[str] = set(pydirectinput.KEY_NAMES)` for validation.
    *   Class `InputManager`:
        *   `__init__(self, logger: logging.Logger)`: Store logger.
        *   `_is_valid_key(self, key_code: str) -> bool`: Checks if `key_code.lower()` is in `VALID_KEYS`. Logs warning and returns `False` if invalid.
        *   `press_key(self, key_code: str) -> None`: If `_is_valid_key` passes, `pydirectinput.press(key_code)`. Catch and log `pydirectinput` related exceptions (e.g. if it fails to send).
        *   `release_key(self, key_code: str) -> None`: If `_is_valid_key` passes, `pydirectinput.release(key_code)`. Catch and log exceptions.
        *   `send_keypress(self, key_code: str, press_duration_ms: int = 50) -> None`: If key is valid, calls `press_key`, `time.sleep(max(0, press_duration_ms / 1000.0))`, then `release_key`.
    *   Docstrings must prominently warn: "CRITICAL USER RESPONSIBILITY: Automated input may violate game End User License Agreements (EULA). Use of this module is at the user's own risk. Ensure compliance with all game rules to avoid account penalties."
    *   Testing: In `if __name__ == "__main__":`, get a dummy logger, instantiate `InputManager`. Prompt user: "Please focus a text editor now. A 'z' keypress will be sent in 3 seconds." Wait, then call `send_keypress('z', 100)`. Test with an invalid key too (e.g., "invalidkeyname").
    *   **Deliverable:** Full content of `input_manager.py`.

3.  **Integrate Temporal Consistency and Input into `main.py`:**
    *   Update `run_application()` in `main.py`:
        *   Import `InputManager` from `.core.input_manager`. Import `pygetwindow`.
        *   Update `IconDetector` instantiation: `icon_detector = IconDetector(main_logger, app_settings.temporal_consistency_frames)`.
        *   Instantiate `input_manager = InputManager(main_logger)`.
        *   Add `sprint_key_physical_state: bool = False` (tracks if we are holding the key).
        *   In main loop, after raw detection `found, score, loc_rect = ...`:
            *   `confirmed_icon_is_active = icon_detector.update_consistent_detection_state(found)` (assuming `found` refers to "sprint is active" icon).
            *   `main_logger.debug(f"Raw detection: {found}, Confirmed State: {confirmed_icon_is_active}")`
            *   Logic for pressing/releasing key:
                *   If `confirmed_icon_is_active is True` and not `sprint_key_physical_state`:
                    *   `active_win = pygetwindow.getActiveWindow()`
                    *   If `active_win` and `app_settings.game_window_title.lower()` in `active_win.title.lower()`: # Case-insensitive compare
                        *   `input_manager.press_key(app_settings.sprint_key)`
                        *   `sprint_key_physical_state = True`
                        *   `main_logger.info(f"Sprint key '{app_settings.sprint_key}' PRESSED. Reason: Icon active, key was not pressed, game window focused.")`
                    *   Else:
                        *   `main_logger.debug(f"Sprint icon active, but game window ('{app_settings.game_window_title}') not focused. Active: '{active_win.title if active_win else 'None'}'. Sprint key not pressed.")`
                *   Else if `confirmed_icon_is_active is False` and `sprint_key_physical_state is True`:
                    *   `input_manager.release_key(app_settings.sprint_key)`
                    *   `sprint_key_physical_state = False`
                    *   `main_logger.info(f"Sprint key '{app_settings.sprint_key}' RELEASED. Reason: Icon not active, key was pressed.")`
    *   **Deliverable:** Updated `main.py`.

4.  **Performance Monitoring Utility (New File: `src/daoc_sprint_manager/utils/performance_monitor.py`):**
    *   Imports: `time`, `os`, `psutil`, `logging`, `typing.Dict`, `typing.Tuple`, `typing.Optional`. Initialize `self.last_lap_times: Dict[str, float] = {}`.
    *   Class `PerformanceMonitor`:
        *   `__init__(self, logger: logging.Logger)`: Store logger. Init `self.timers: Dict[str, float] = {}`. Get `self.process = psutil.Process(os.getpid())`. Call `self.process.cpu_percent(interval=None)` once initially to prime it.
        *   `start_timer(self, name: str) -> None`: Records `time.perf_counter()` in `self.timers[name]`.
        *   `stop_timer(self, name: str) -> Optional[float]`: Calculates duration since start. Returns duration or `None` if timer name wasn't started (logs error). Stores duration in `self.last_lap_times[name]`.
        *   `get_fps(self, cycle_time_s: float) -> float`: Returns `1.0 / cycle_time_s` if `cycle_time_s > 0.00001` else 0.0.
        *   `get_script_resource_usage(self) -> Tuple[float, float]`: Returns `(cpu_percent, memory_mb)`. Use `self.process.cpu_percent(interval=None)` (it gives % since last call or process start) and `self.process.memory_info().rss / (1024 * 1024)` (MB).
    *   Testing: `if __name__ == "__main__":`, get a dummy logger. Instantiate `PerformanceMonitor`. Demonstrate: start timer "test", sleep, stop timer "test", print lap time. Get FPS from the lap time. Print resource usage.
    *   **Deliverable:** Full content of `performance_monitor.py`.

5.  **Integrate Performance Monitoring into `main.py`:**
    *   Update `run_application()` in `main.py`:
        *   Import `PerformanceMonitor` from `.utils.performance_monitor`.
        *   Instantiate `perf_monitor = PerformanceMonitor(main_logger)`.
        *   In main loop, at the very beginning: `perf_monitor.start_timer("full_cycle")`.
        *   Wrap key operations:
            *   `perf_monitor.start_timer("window_find")`; `... find_window ...`; `find_time = perf_monitor.stop_timer("window_find")`.
            *   `perf_monitor.start_timer("roi_capture")`; `... capture_roi ...`; `capture_time = perf_monitor.stop_timer("roi_capture")`.
            *   `perf_monitor.start_timer("icon_detection")`; `... detect_icon ...`; `detection_time = perf_monitor.stop_timer("icon_detection")`.
        *   At the end of the loop, before `time.sleep()`:
            *   `full_cycle_time = perf_monitor.stop_timer("full_cycle")`.
            *   If `app_settings.show_performance_metrics` and `full_cycle_time is not None`:
                *   `fps = perf_monitor.get_fps(full_cycle_time)`.
                *   `cpu_usage, mem_usage_mb = perf_monitor.get_script_resource_usage()`.
                *   `main_logger.debug(f"Perf: Cycle={full_cycle_time*1000:.2f}ms (FPS:{fps:.1f}), CPU={cpu_usage:.1f}%, MEM={mem_usage_mb:.1f}MB. Timings(ms): Find={find_time*1000 if find_time else 'N/A':.1f}, Capture={capture_time*1000 if capture_time else 'N/A':.1f}, Detect={detection_time*1000 if detection_time else 'N/A':.1f}")`
    *   **Deliverable:** Updated `main.py`.

6.  **Basic System Tray UI (`src/daoc_sprint_manager/ui/tray_app.py`):**
    *   Imports: `pystray`, `PIL.Image`, `PIL.UnidentifiedImageError`, `threading`, `pathlib`, `logging`, `subprocess`, `sys`, `os`. `AppSettings` from `..data_models`. `WindowManager` from `..core.window_manager`, `IconDetector` from `..core.icon_detector`, `InputManager` from `..core.input_manager`, `PerformanceMonitor` from `..utils.performance_monitor`. `pygetwindow`. `time`.
    *   Class `SprintManagerApp`:
        *   `__init__(self, app_settings: AppSettings, logger: logging.Logger, root_dir: pathlib.Path)`: Store args. Init shared state:
            *   `self.stop_event = threading.Event()`
            *   `self.pause_event = threading.Event()` # When set, detection loop pauses
            *   `self.status_message = "Initializing..."`
            *   `self.status_lock = threading.Lock()`
            *   `self.pystray_icon: Optional[pystray.Icon] = None`
            *   `self.sprint_key_physical_state: bool = False`
        *   Initialize core components as instance variables (e.g., `self.window_manager`, `self.icon_detector` (passing `app_settings.temporal_consistency_frames`), `self.input_manager`, `self.perf_monitor`).
        *   Load `self.sprint_on_template` here using `self.icon_detector.load_template`. Log critical error and `sys.exit(1)` if template fails to load.
        *   `_update_status(self, message: str)`: Thread-safe update `self.status_message`. If `self.pystray_icon`, update `self.pystray_icon.title = f"DAOC Sprint Manager: {message}"`.
        *   `_on_clicked_pause_resume(self, icon, item)`: Toggles `self.pause_event`._update_status to "Paused" or "Running".
        *   `_on_clicked_open_config(self, icon, item)`: Opens `self.root_dir / "config" / "settings.json"` using `os.startfile` (Windows) or `subprocess.call(['xdg-open', path])` (Linux) or `subprocess.call(['open', path])` (macOS). Handles potential errors.
        *   `_on_clicked_exit(self, icon, item)`: `self._update_status("Exiting...")`. `self.stop_event.set()`. If `self.pystray_icon`, `self.pystray_icon.stop()`.
        *   `_build_menu(self)`: Returns `pystray.Menu` with items (Menu Item for status display that is dynamically updated or disabled, "Pause/Resume" (checkable depending on `pause_event`), "Open Config", "Exit").
        *   `run_detection_logic(self)`: Contains the core `while not self.stop_event.is_set():` loop previously in `main.py`.
            *   Incorporates pausing: if `self.pause_event.is_set(): self.pause_event.wait(timeout=1.0); continue;` (or simply sleep and continue if pause_event set). Ensure loop calls`_update_status("Paused")` when paused and not actively looping often.
            *   Calls `self._update_status(...)` with current detection state / FPS.
            *   Uses all core components initialized in `__init__`. (e.g. `self.window_manager`, `self.input_manager`).
            *   Ensure the full detection logic with input management and performance monitoring (if enabled) is correctly transferred here using `self.` attributes.
        *   `start(self)`:
            *   Load app icon: `app_icon_path = self.root_dir / self.app_settings.app_icon_path`. Handle `FileNotFoundError`, `PIL.UnidentifiedImageError`. Fallback to no icon if load fails (log warning). `icon_image = Image.open(app_icon_path)` or `None`.
            *   `self.detection_thread = threading.Thread(target=self.run_detection_logic, daemon=True)`
            *   `self.detection_thread.start()`
            *   `self.pystray_icon = pystray.Icon("DAOCSprintManager", icon_image, "DAOC Sprint Manager", self._build_menu())`. `self.pystray_icon.menu = self._build_menu()` (dynamic update of text based on status).
            *   `self._update_status("Running")`
            *   `self.pystray_icon.run()` (blocks until exit)
            *   After `run()` finishes (icon stopped), ensure `self.stop_event` is set.
            *   `self.detection_thread.join(timeout=5.0)` (ensure thread cleans up).
    *   Refactor `main.py` (`run_application`):
        *   Now primarily initializes `AppSettings`, `logger`, `ROOT_DIR`.
        *   Then instantiates `SprintManagerApp(app_settings, main_logger, ROOT_DIR)`.
        *   Calls `app.start()`. The `try...except KeyboardInterrupt` in `main.py` should signal `app.stop_event.set()` if `app.pystray_icon` is not running (console mode) or gracefully allow ` tray_app`'s exit method to handle it.
    *   User Task Reminder output text: "User Task: Provide an application icon named 'app_icon.png' (e.g., 32x32 or 64x64 pixels) in the 'daoc_sprint_manager/data/' directory. This icon will be used for the system tray. The path is also configurable in settings.json.template as app_icon_path."
    *   **Deliverable:** `tray_app.py` and heavily refactored `main.py`.

Phase 3: Robustness & ML Implementation (Optional)

Objective: Further improve detection accuracy using a lightweight ML model, implement adaptive detection parameters, and create comprehensive error handling and diagnostic tools.

(Assume `ROOT_DIR` and `main_logger` are available or passed where needed.)

1.  **ML-Based Icon Detection (New File: `src/daoc_sprint_manager/core/ml_detector.py`):**
    *   Requires `onnxruntime` in `requirements.txt`. Update `requirements.txt`.
    *   User Task Output Text: "ML Model User Task: Dataset collection (positive/negative examples of the icon ROI under various conditions) and model training (e.g., a lightweight CNN like MobileNetV3-Small using TensorFlow/Keras or PyTorch) are manual user tasks. Export the trained model to ONNX format. Store labeled images (e.g., in data/ml_training_data/icon/ and data/ml_training_data/no_icon/). Place the trained ONNX model at the path specified in config/settings.json (default: data/models/sprint_classifier.onnx). Update settings.json with the correct model path and desired ml_input_size_wh (e.g., [32, 32])."
    *   Update `AppSettings` in `data_models.py` and `settings.json.template` to include:
        *   `ml_model_path: str = "data/models/sprint_classifier.onnx"`
        *   `ml_input_size_wh: list[int] = [32, 32]` # Example size, (width, height)
        *   `ml_confidence_threshold: float = 0.7`
    *   Class `MLDetector`:
        *   Imports: `onnxruntime`, `pathlib`, `cv2`, `numpy as np`, `logging`, `typing.Tuple`, `typing.Optional`.
        *   `__init__(self, model_path: pathlib.Path, input_size_wh: Tuple[int, int], logger: logging.Logger)`:
            *   Store args. Check model file existence. Log error and raise `FileNotFoundError` if not found.
            *   Load ONNX model: `self.ort_session = onnxruntime.InferenceSession(str(model_path))`. Handle exceptions (log, re-raise or set a faulty state).
            *   `self.input_name = self.ort_session.get_inputs()[0].name`. `self.output_name = self.ort_session.get_outputs()[0].name`.
            *   Store `input_size_wh`.
        *   `_preprocess_image(self, frame_roi: np.ndarray) -> Optional[np.ndarray]`:
            *   Ensure `frame_roi` is not `None` and has valid dimensions. If not, log and return `None`.
            *   Resize `frame_roi` to `self.input_size_wh` using `cv2.resize`. Ensure `interpolation=cv2.INTER_AREA` for shrinking or `INTER_LINEAR` for enlarging.
            *   Normalize pixel values (e.g., converted to float32 and divided by 255.0 to get [0,1] range, assumes model expects this). This MUST match model training.
            *   Convert to NCHW format: `img = np.transpose(normalized_image, (2, 0, 1))` then `img_batch = np.expand_dims(img, axis=0)`. (Order depends on model needs; confirm for ONNX model's expected input shape). Cast to `np.float32`.
            *   Handle `cv2.error` and other exceptions (log and return `None`).
        *   `predict(self, frame_roi: np.ndarray) -> Tuple[bool, float]`:
            *   `processed_input = self._preprocess_image(frame_roi)`. If `None`, return `(False, 0.0)`.
            *   `ort_inputs = {self.input_name: processed_input}`.
            *   `ort_outs = self.ort_session.run([self.output_name], ort_inputs)`. (Output structure depends on model – assume `ort_outs[0]` is an array like `[[prob_no_icon, prob_icon]]`).
            *   Extract confidence: `confidence_icon = float(ort_outs[0][0][1])` (example path to icon probability, adjust based on actual model output).
            *   Obtain `app_settings.ml_confidence_threshold` from somewhere (passed in, or `ConfigManager` used to get current settings if dynamic settings are a feature). For now, assume it's made available.
            *   `is_detected = confidence_icon >= self.ml_confidence_threshold` (where threshold is passed or accessed).
            *   Return `(is_detected, confidence_icon)`. Handle `onnxruntime.OrtException` (log and return `(False, 0.0)`).
    *   Testing: `if __name__ == "__main__":` (requires a dummy ONNX model and dummy image). Create dummy logger, instantiate `MLDetector` (pointing to the dummy model). Create a random `np.ndarray` for `frame_roi`. Call `predict`.
    *   **Deliverable:** `ml_detector.py`. Updated `data_models.py` and `config/settings.json.template`. AI to add `onnxruntime` to `requirements.txt`.

2.  **Integrate ML Detector into `SprintManagerApp`:**
    *   Modify `SprintManagerApp`:
        *   In `__init__`: If `self.app_settings.detection_method == "ml"`, initialize `self.ml_detector = MLDetector(model_path=self.root_dir / self.app_settings.ml_model_path, input_size_wh=tuple(self.app_settings.ml_input_size_wh), logger=self.logger)`. Handle initialization errors (e.g., log, and consider falling back to template matching or stopping).
        *   In `run_detection_logic`, where icon detection happens:
            *   If `self.app_settings.detection_method == "ml"` and `hasattr(self, 'ml_detector')` and `self.ml_detector` is working:
                *   `found, score = self.ml_detector.predict(frame)` (Use frame, not frame_roi if preprocess does cropping/ROI expectation) or `frame_roi` if it is already the designated region for classification. This implies ML works on the same ROI as template matching. Ensure this is consistent.
            *   Else (template matching):
                *   `found, score, _loc = self.icon_detector.detect_icon(frame, self.sprint_on_template, self.app_settings.template_match_threshold)`
            *   The rest of the logic (temporal consistency, input) uses this `found` and `score`.
    *   **Deliverable:** Updated `tray_app.py` (or `src/daoc_sprint_manager/main.py` if `tray_app.py` is not the main loop holder).

3.  **Comprehensive Error Handling & Fallback Enhancements:**
    *   Game Closed/Crashed: In `SprintManagerApp.run_detection_logic`, if `find_window` returns `None` for a configurable number of consecutive attempts (e.g., 3 using a counter):
        *   Call `self._update_status("Game Not Found - Pausing scan")`.
        *   If not already paused by user, maybe implicitly set `self.pause_event.set()` or introduce a new event for this state.
        *   The detection loop should then only periodically try to find the window at a much slower rate (e.g., every `app_settings.game_not_found_retry_delay_s`) until the window is found again, then resume normal operation and `self._update_status("Game Found - Resuming")`.
    *   ML Model Failure Fallback: In `SprintManagerApp`:
        *   During `MLDetector` initialization in `__init__`: If it fails (e.g., `FileNotFoundError` for model, `onnxruntime.OrtException`), log it, `self._update_status("ML Error - Using Template Matching")`, and set `self.app_settings.detection_method = "template"` in memory for the current session.
        *   During `ml_detector.predict`: If it throws critical errors consistently (e.g., track failures per minute), implement similar fallback: log, `self._update_status("ML Prediction Error - Switching to Template")`, and change `self.app_settings.detection_method = "template"`.
    *   **Deliverable:** Refined error handling logic within `SprintManagerApp.run_detection_logic` and related init methods.

4.  **Diagnostic Tools:**
    *   New setting in `AppSettings` & `settings.json.template`: `save_problematic_frames: bool = False`, `problematic_frame_save_path: str = "data/problem_frames"`.
    *   In `SprintManagerApp.run_detection_logic`:
        *   After detection results (`found`, `score`):
            *   If `self.app_settings.save_problematic_frames is True`:
                *   Define conditions for "problematic", e.g., for template matching: `(self.app_settings.detection_method == 'template' and self.app_settings.detection_failure_threshold < score < self.app_settings.template_match_threshold)`
                *   Or for ML: `(self.app_settings.detection_method == 'ml' and self.app_settings.ml_confidence_threshold * 0.7 < score < self.app_settings.ml_confidence_threshold)` (i.e., scores in an uncertain range).
                *   If problematic conditions are met:
                    *   `save_dir = self.root_dir / self.app_settings.problematic_frame_save_path`
                    *   `save_dir.mkdir(parents=True, exist_ok=True)`
                    *   `timestamp = time.strftime("%Y%m%d-%H%M%S")`
                    *   `filename = save_dir / f"problem_{timestamp}_score{score:.2f}.png"`
                    *   `cv2.imwrite(str(filename), frame_roi)` (Ensure `frame_roi` is available here; it should be the same image fed to detection).
                    *   Log the saving action: `self.logger.info(f"Saved problematic frame: {filename}")`.
    *   (Optional: Add `keyboard` to `requirements.txt` for global hotkey functionality. This is more complex due to platform differences and focus issues; for AI generation, stick to config-based saving first).
    *   **Deliverable:** Diagnostic frame saving logic in `SprintManagerApp.run_detection_logic`. Updated` data_models.py`, `config/settings.json.template`.

Phase 4: Optimization & User Experience

Objective: Optimize for minimal resource usage while maintaining accuracy. Refine user interface and overall user experience. Create comprehensive documentation and packaging.

1.  **Performance Optimization:**
    *   Adaptive Polling Rate (Game Window Focus):
        *   In `SprintManagerApp.run_detection_logic` loop, right before calculating sleep duration:
            *   `active_win = pygetwindow.getActiveWindow()`
            *   `is_game_focused = active_win and self.app_settings.game_window_title.lower() in active_win.title.lower()`
            *   If `is_game_focused`:
                *   `target_delay = 1.0 / self.app_settings.capture_fps`
            *   Else:
                *   `target_delay = self.app_settings.inactive_window_poll_delay__s`
                *   If `self.sprint_key_physical_state`: # If game loses focus while key is pressed
                    *   `self.input_manager.release_key(self.app_settings.sprint_key)`
                    *   `self.sprint_key_physical_state = False`
                    *   `self.logger.info(f"Sprint key '{self.app_settings.sprint_key}' RELEASED. Reason: Game window lost focus.")`
            *   Get `elapsed_cycle_time` (e.g. from `perf_monitor.last_lap_times["full_cycle"]` if performance monitoring is on, otherwise calculate simply with `time.perf_counter() - cycle_start_time`).
            *   `sleep_duration = max(0, target_delay - elapsed_cycle_time)`
            *   `time.sleep(sleep_duration)`
    *   **Deliverable:** Adaptive polling logic in `SprintManagerApp.run_detection_logic`.

2.  **Comprehensive Documentation (`README.md` & API Docs):**
    *   `README.md` update: Add sections for:
        *   Detailed Installation (Python version, `requirements.txt`).
        *   Configuration (`settings.json` - explain each key's purpose and example values).
        *   Providing Icon Templates (how to create good templates) and App Icon (format, size).
        *   ML Model Setup (if user wants to use it):
            *   Brief mention of data collection needs (screenshots of icon on/off in various conditions).
            *   High-level outline of training (e.g., "train a binary image classifier using your preferred ML framework").
            *   ONNX export necessity and placement.
        *   Troubleshooting (common issues: window not found, icon not detected, permissions, input not working).
        *   How to run the application (console vs. tray).
        *   Performance considerations (impact of FPS, ROI size).
        *   Disclaimer about game EULAs and responsible use.
    *   API Docs (Sphinx - AI to assist, user to finalize):
        *   AI Instruction: "Generate Sphinx reStructuredText stub files for API documentation from existing docstrings. Create a `docs` directory. Use the command: `sphinx-apidoc -o docs/source src/daoc_sprint_manager -e -M -f`. The user will need to install Sphinx (`pip install sphinx sphinx-rtd-theme`), create a basic `docs/source/conf.py` (e.g. using `sphinx-quickstart`), add `sphinx.ext.napoleon` for Google style docstrings to extensions in `conf.py` and `sys.path.insert(0, os.path.abspath('../../src'))`, add `index.rst` to include modules, and then run `sphinx-build -b html docs/source docs/build/html` to build the HTML documentation."
    *   **Deliverable:** AI provides detailed content text for `README.md` sections. AI provides the `sphinx-apidoc` command and subsequent user build instructions.

3.  **Packaging and Deployment (PyInstaller):**
    *   Add `PyInstaller` to `requirements.txt`.
    *   AI Task: Provide a template `daoc_sprint_manager.spec` file for PyInstaller:
        ```python
        # daoc_sprint_manager.spec
        # -*- mode: python ; coding: utf-8 -*-

        block_cipher = None

        a = Analysis(
            ['src/daoc_sprint_manager/main.py'],
            pathex=['.'],  # Project root
            binaries=[],
            datas=[
                ('config/settings.json.template', 'config'),
                ('data/app_icon.png', 'data'),                 # To be included if used by tray
                ('data/icon_templates/sprint_on.png', 'data/icon_templates'), # Example, better to grab all
                ('data/icon_templates/sprint_off.png', 'data/icon_templates'),# Using wildcard: ('data/icon_templates/*.png', 'data/icon_templates')
                # If using ML, include the default model:
                # ('data/models/sprint_classifier.onnx', 'data/models')
            ],
            hiddenimports=[
                'pystray.backends.win32', # For Windows
                'pystray.backends.appindicator', # For Linux with appindicator
                'pystray.backends.gtk', # For GTK based Linux
                'pystray.backends.darwin', # For macOS
                'PIL.Image',
                'PIL.PngImagePlugin', # Often needed explicitly for Pillow images
                'pygetwindow',
                'psutil',
                'pydirectinput',
                'onnxruntime' # If ML is included
                # Add other sub-modules if PyInstaller misses them
            ],
            hookspath=[],
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False
        )
        pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            [],
            name='DAOCSprintManager',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,  # False for GUI app (system tray), True for console debugging version
            icon='data/app_icon.ico' # User should provide/convert .ico for .exe
        )
        ```
    *   User Task Output Text: "User Task for Packaging: 1. Install PyInstaller (`pip install pyinstaller`). 2. If on Windows, create an `.ico` file (e.g., from `data/app_icon.png`) and save it as `data/app_icon.ico`. Update the `icon` path in `daoc_sprint_manager.spec` if different. 3. Review paths in `daoc_sprint_manager.spec`, especially under `datas` (to include all your icon templates like `data/icon_templates/*.png`) and `hiddenimports` list based on your OS and any errors during initial PyInstaller runs. 4. Run `pyinstaller daoc_sprint_manager.spec` from the project root. The executable will be in the `dist/DAOCSprintManager` folder."
    *   **Deliverable:** `daoc_sprint_manager.spec` content. AI to provide user instructions as text. AI to add `pyinstaller` to `requirements.txt`.

4.  **Unit Testing Framework (pytest - Stubs):**
    *   Add `pytest` to `requirements.txt`.
    *   AI Task: For 2-3 key utility functions or pure logic methods (e.g., a validation part of `ConfigManager`, or the logic in `IconDetector.update_consistent_detection_state`), generate example fully self-contained pytest test files in the `tests/` directory (e.g., `tests/core/test_icon_detector.py`, `tests/utils/test_logger.py`).
    *   Example for `tests/core/test_icon_detector.py`:
        ```python
        # tests/core/test_icon_detector.py
        import pytest
        import logging
        from collections import deque
        from daoc_sprint_manager.core.icon_detector import IconDetector # Assuming IconDetector is in this path

        # Minimal mock logger for tests
        class MockLogger:
            def debug(self, msg, *args, **kwargs): pass # print(f"DEBUG: {msg}")
            def info(self, msg, *args, **kwargs): pass  # print(f"INFO: {msg}")
            def warning(self, msg, *args, **kwargs): pass # print(f"WARNING: {msg}")
            def error(self, msg, *args, **kwargs): pass   # print(f"ERROR: {msg}")

        @pytest.fixture
        def mock_logger():
            return MockLogger()

        @pytest.mark.parametrize("history, temporal_frames, expected_confirmations", [
            ([True, True, True], 3, [False, False, True]), # Initial state False, buffer fills, then True
            ([False, False, False], 3, [False, False, False]),# Initial state False, buffer fills, then False
            ([True, False, True], 3, [False, False, False]), # Initial state False, mixed doesn't change from initial
            ([False, True, True, True], 3, [False, False, True, True]), # state changes once buffer is full and consistent
            ([True, True, False, False, False], 3, [False, False, True, True, False]), # Test flapping and settling
            ([True], 3, [False]), # Less than temporal_frames
        ])
        def test_update_consistent_detection_state(mock_logger, history, temporal_frames, expected_confirmations):
            detector = IconDetector(logger=mock_logger, temporal_consistency_frames=temporal_frames)
            detector.confirmed_detection_state = False # Explicitly set initial state for predictability
            
            actual_confirmations = []
            for i, detection_event in enumerate(history):
                confirmed_state = detector.update_consistent_detection_state(detection_event)
                actual_confirmations.append(confirmed_state)
                # Also check the internal state after buffer might be full
                if len(detector.detection_history) == detector.detection_history.maxlen:
                     assert detector.confirmed_detection_state == expected_confirmations[i], f"Failed at event {i+1} internal state"


            assert actual_confirmations == expected_confirmations, "Sequence of confirmed states did not match expected"
        ```
        (Note: The provided test was complex. Making a simpler one for another module may be better for generation.)
        AI Task: Also generate a basic test for `ConfigManager.load_settings()` covering cases like file not found (template copy), corrupted JSON (default use).
    *   User Task Output Text: "User Task for Testing: 1. Install pytest (`pip install pytest`). 2. Review generated test stubs and examples in the `tests/` directory. 3. Implement comprehensive test cases for critical logic in your application. 4. Run tests using the `pytest` command from the project root to ensure code quality and catch regressions."
    *   **Deliverable:** Example pytest test file structure and content for at least two modules. AI to provide user instructions. AI to add `pytest` to `requirements.txt`.

---
Immediate Next Steps for AI Agent (Claude, etc.)

Instruction: You are an expert Python 3.9+ developer AI. Your current task is to execute **only the "Pre-Phase: Project Setup & Foundation"** section of project plan. You will perform each numbered step within the Pre-Phase sequentially. For each step, provide the complete file contents or perform the action as specified, adhering to all Universal Code Quality and Architectural Standards. After completing the Pre-Phase, AWAIT FURTHER INSTRUCTIONS.

1.  **Project Directory Structure and Git:**
    *   Provide the content for `daoc_sprint_manager/.gitignore`.
    *   Provide the content for `daoc_sprint_manager/README.md`.
    *   Provide the content for `daoc_sprint_manager/requirements.txt`.
    *   Confirm the creation of each file/directory listed in "Pre-Phase, item 1, directory structure bullet point". For example, state: "Created empty file: `src/daoc_sprint_manager/__init__.py`", "Created directory: `src/daoc_sprint_manager/core/`", etc.

2.  **Logging Framework Setup:**
    *   Provide the full content for `src/daoc_sprint_manager/utils/logger.py`, including the `if __name__ == "__main__":` test block as specified.

3.  **Data Models for Configuration:**
    *   Provide the full content for `src/daoc_sprint_manager/data_models.py`, including the `if __name__ == "__main__":` test block as specified.

4.  **Configuration Management Setup:**
    *   Provide the full content for `config/settings.json.template` as specified.
    *   Provide the full content for `src/daoc_sprint_manager/config_manager.py`, including the `if __name__ == "__main__":` test block as specified.

5.  **Initial Main Application Entry Point:**
    *   Provide the full content for `src/daoc_sprint_manager/main.py` as specified.

After providing all these files and confirmations from Pre-Phase, await further instructions for Phase 1.