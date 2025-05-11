"""
Main application entry point for the DAOC Sprint Manager.

Initializes configuration, logging, and the system tray application.
"""

import logging
import pathlib
import sys
import threading

# Ensure the project root is added to sys.path for imports if needed
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
# sys.path.insert(0, str(ROOT_DIR / 'src')) # Might be needed depending on execution context

try:
    # Attempt to import project modules
    from daoc_sprint_manager.config_manager import ConfigManager
    from daoc_sprint_manager.data_models import AppSettings
    from daoc_sprint_manager.ui.system_tray import SystemTrayUI as SprintManagerApp, PYSTRAY_AVAILABLE
    from daoc_sprint_manager.utils.logger import setup_logger
except ImportError:
    # Fallback for simpler execution or testing contexts
    print("Could not import modules using package structure. Trying direct imports...")
    # This assumes main.py is run from src/daoc_sprint_manager or similar relative path.
    # For robust execution, running as a package (`python -m daoc_sprint_manager.main`) is preferred.
    try:
         from config_manager import ConfigManager
         from data_models import AppSettings
         from ui.system_tray import SystemTrayUI as SprintManagerApp, PYSTRAY_AVAILABLE
         from utils.logger import setup_logger
    except ImportError as e:
         print(f"Import Error: {e}. Ensure the script is run correctly or dependencies are installed.")
         sys.exit(1)


LOGS_DIR = ROOT_DIR / "logs"


def run_application():
    """Initializes and runs the main application logic via the tray app."""
    # --- Preliminary Setup ---
    prelim_log_file = LOGS_DIR / "startup_app.log"
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        prelim_logger = setup_logger("startup", prelim_log_file, logging.DEBUG)
        prelim_logger.info(f"Preliminary logging started. Project Root: {ROOT_DIR}")
    except Exception as e:
        print(f"FATAL: Could not set up preliminary logger at {prelim_log_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Configuration Loading ---
    main_logger = prelim_logger
    app_settings = None
    try:
        # Updated paths to use the ROOT_DIR / "config" location
        settings_file = ROOT_DIR / "config" / "settings.json"
        template_file = ROOT_DIR / "config" / "settings.json.template"
        main_logger.info(f"Settings path: {settings_file}")
        main_logger.info(f"Template path: {template_file}")

        config_manager = ConfigManager(settings_file, template_file, main_logger)
        app_settings = config_manager.load_settings()

        # --- Main Logger Setup ---
        actual_log_file_path = LOGS_DIR / app_settings.log_file_name
        log_level_from_config = getattr(logging, app_settings.log_level.upper(), logging.INFO)
        main_logger = setup_logger("DAOCSprintManager", actual_log_file_path, log_level_from_config)
        main_logger.info("Main application logger initialized.")
        main_logger.info(f"Logging to file: {actual_log_file_path}")
        main_logger.info(f"Log level set to: {app_settings.log_level}")

    except Exception as e:
        main_logger.critical(f"Failed during configuration or main logger setup: {e}", exc_info=True)
        sys.exit(1)

    # --- Initialize and Start Tray Application ---
    if not PYSTRAY_AVAILABLE:
        main_logger.critical("pystray or Pillow not found. Cannot run system tray application.")
        print("ERROR: pystray or Pillow library not found. Install using: pip install pystray Pillow", file=sys.stderr)
        sys.exit(1)

    # Read test mode from settings
    test_mode = getattr(app_settings, 'test_mode', False)
    main_logger.info(f"Test mode setting from config: {test_mode}")
    
    # In test mode, we don't need to initialize the real SprintManager
    if test_mode:
        main_logger.info("Running in test mode - using mock components")
        # Pass just app_settings to SystemTrayUI in test mode
        app = SprintManagerApp(app_settings, test_mode=True)
        main_logger.info("Starting SprintManagerApp in test mode...")
    else:
        # Normal operation - initialize SprintManager and SystemTrayUI
        try:
            from daoc_sprint_manager.core.sprint_manager import SprintManager
            sprint_manager = SprintManager(app_settings, main_logger)
            app = SprintManagerApp(sprint_manager)
            main_logger.info("Starting SprintManagerApp in normal mode...")
        except Exception as e:
            main_logger.critical(f"Failed to initialize application: {e}")
            sys.exit(1)
    
    # Start the app - this will block until the tray app exits
    app.start()

    # --- Post-Application Run ---
    # Code here runs after the tray application has stopped
    main_logger.info("Application finished running.")
    return 0


if __name__ == "__main__":
    import os
    # Set CWD if running as script
    if not getattr(sys, 'frozen', False):
         # Change CWD to project root for relative paths in config/icon loading
         os.chdir(ROOT_DIR)
         print(f"Changed CWD to: {os.getcwd()}")

    # Setup basic logging immediately
    initial_logger = logging.getLogger("main_entry")
    initial_logger.setLevel(logging.INFO)
    if not initial_logger.handlers:
        initial_handler = logging.StreamHandler(sys.stdout)
        initial_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        initial_handler.setFormatter(initial_formatter)
        initial_logger.addHandler(initial_handler)

    exit_code = 0
    app_thread = None
    try:
        # Run the application in a separate thread to allow KeyboardInterrupt handling
        # Although pystray handles SIGINT, this provides a fallback
        app_thread = threading.Thread(target=run_application, daemon=True)
        app_thread.start()

        # Keep the main thread alive, waiting for app_thread or KeyboardInterrupt
        while app_thread.is_alive():
             app_thread.join(timeout=0.5) # Check every 0.5 seconds

    except KeyboardInterrupt:
        initial_logger.info("KeyboardInterrupt received in main thread. Signaling application to stop...")
        # How to signal stop? The tray app handles its own exit signal (_on_clicked_exit)
        # which sets the stop_event. If pystray handles Ctrl+C well, this might not be needed.
        # If needed, we'd have to get the 'app' instance back or use a shared mechanism.
        # For now, rely on pystray's signal handling and the _on_clicked_exit logic.
        print("Attempting graceful shutdown via pystray exit signal...")
        # Potential improvement: Implement a global signal handler or queue
        exit_code = 0
    except Exception as e:
        initial_logger.critical(f"Unhandled exception in main execution: {e}", exc_info=True)
        exit_code = 1
    finally:
        initial_logger.info("Main thread exiting.")
        logging.shutdown()
        print("Main shutdown sequence complete.")
        # Force exit if something hangs
        # os._exit(exit_code) # Use cautiously, prevents cleanup
        sys.exit(exit_code) 