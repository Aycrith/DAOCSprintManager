"""
Test script for the Configuration GUI.

This script provides a simple way to test the ConfigGUI without running the full application.
"""

import logging
import os
import pathlib
import sys
import tkinter as tk
from tkinter import messagebox

# Add parent directory to path so we can import modules
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent.parent))

try:
    from daoc_sprint_manager.ui.config_gui import ConfigGUI
    from daoc_sprint_manager.config_manager import ConfigManager
    from daoc_sprint_manager.data_models import AppSettings
except ImportError:
    print("Error importing required modules. Make sure you're running from the correct directory.")
    sys.exit(1)

def setup_logger():
    """Set up a logger for the test script."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("ConfigGUI_Test")

def create_test_config_files():
    """Create test configuration files if they don't exist."""
    # Get project root directory
    root_dir = current_dir.parent.parent.parent
    
    # Create config directory if it doesn't exist
    config_dir = root_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Define paths
    config_path = config_dir / "test_settings.json"
    template_path = config_dir / "test_settings.json.template"
    
    # Create template file if it doesn't exist
    if not template_path.exists():
        print(f"Creating test template file: {template_path}")
        with open(template_path, 'w') as f:
            f.write('''{
  "game_window_title": "Test Game Window",
  "roi_x": 100,
  "roi_y": 100,
  "roi_width": 50,
  "roi_height": 50,
  "sprint_key": "z",
  "template_match_threshold": 0.8,
  "temporal_consistency_frames": 3,
  "capture_fps": 10.0,
  "show_performance_metrics": true,
  "log_level": "INFO",
  "ml_model_path": "data/models/test_model.onnx",
  "ml_input_size_wh": [32, 32],
  "ml_confidence_threshold": 0.7
}''')
    
    return config_path, template_path

def main():
    """Main function to test the ConfigGUI."""
    # Set up logger
    logger = setup_logger()
    logger.info("Testing ConfigGUI")
    
    # Create test configuration files
    config_path, template_path = create_test_config_files()
    logger.info(f"Using test config path: {config_path}")
    logger.info(f"Using test template path: {template_path}")
    
    # Create ConfigManager and load settings
    config_manager = ConfigManager(config_path, template_path, logger)
    app_settings = config_manager.load_settings()
    
    # Create test application
    root = tk.Tk()
    root.title("ConfigGUI Test Harness")
    root.geometry("200x100")
    
    # Add a button to launch the config dialog
    def open_config():
        logger.info("Opening ConfigGUI")
        gui = ConfigGUI(root, config_manager, app_settings, logger)
        gui.show()
    
    tk.Button(root, text="Open Config Dialog", command=open_config).pack(padx=20, pady=30)
    
    logger.info("GUI test harness started")
    root.mainloop()

if __name__ == "__main__":
    main() 