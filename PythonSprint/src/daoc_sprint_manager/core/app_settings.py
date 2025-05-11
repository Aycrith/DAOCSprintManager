"""
DAOC Sprint Manager - Application Settings
=======================================

This module handles application settings and configuration.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class AppSettings:
    """Manages application settings and configuration."""
    
    def __init__(self):
        """Initialize application settings."""
        # Core settings
        self.config_dir = Path.home() / ".daoc_sprint_manager"
        self.config_file = self.config_dir / "config.json"
        
        # Default operational settings (can be overridden by config or CLI in test mode)
        self.game_window_title = "Dark Age of Camelot"
        self.capture_fps = 10.0
        self.detection_method = "template"
        
        # Test mode settings - these will be primarily set by CLI args
        self.test_mode = False
        self.test_window_title = "MOCK_GAME"
        
        # Performance settings (these are somewhat arbitrary defaults if not loaded)
        # For real app, these would come from the more detailed settings.json
        self.ml_input_size_wh: Tuple[int, int] = (32, 32)
        self.icon_size: Tuple[int, int] = (32, 32)
        
        # Load or create configuration from ~/.daoc_sprint_manager/config.json
        # This will override defaults if the file exists and has corresponding keys.
        self.load_or_create_config()
    
    def load_or_create_config(self):
        """Load existing configuration or create default one."""
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True, exist_ok=True)
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.update_settings(config)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                # If config file doesn't exist, save current defaults to create it
                self.save_config()
                logger.info(f"Default configuration created at {self.config_file}")
                
        except Exception as e:
            logger.error(f"Error loading or creating configuration: {e}", exc_info=True)
            # Attempt to save defaults if loading failed catastrophically
            if not self.config_file.exists():
                 self.save_config() 
    
    def update_settings(self, config: Dict):
        """Update settings from configuration dictionary.
        
        Args:
            config: Dictionary containing settings to update
        """
        # Update core settings if present in config
        self.game_window_title = config.get("game_window_title", self.game_window_title)

        # Test mode settings can also be in config, but CLI usually overrides for test runs
        self.test_mode = config.get("test_mode", self.test_mode)
        self.test_window_title = config.get("test_window_title", self.test_window_title)
        
        # Capture_fps and detection_method can be overridden by config file too
        self.capture_fps = float(config.get("capture_fps", self.capture_fps))
        self.detection_method = config.get("detection_method", self.detection_method)
        
        # Performance settings
        ml_size = config.get("ml_input_size_wh", self.ml_input_size_wh)
        if isinstance(ml_size, list) and len(ml_size) == 2:
            self.ml_input_size_wh = tuple(ml_size)
        
        icon_s = config.get("icon_size", self.icon_size)
        if isinstance(icon_s, list) and len(icon_s) == 2:
             self.icon_size = tuple(icon_s)
    
    def save_config(self):
        """Save current settings to configuration file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config = {
                "game_window_title": self.game_window_title,
                "test_mode": self.test_mode,
                "test_window_title": self.test_window_title,
                "capture_fps": self.capture_fps,
                "detection_method": self.detection_method,
                "ml_input_size_wh": list(self.ml_input_size_wh),
                "icon_size": list(self.icon_size)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
                
            logger.info(f"Configuration saved successfully to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True) 