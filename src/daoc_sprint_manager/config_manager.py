"""
Configuration management module.

Handles loading, saving, and validating application settings from JSON files.
"""

import json
import logging
import os
import pathlib
import shutil
from typing import Dict, Optional, Union

try:
    from .data_models import AppSettings, PYDANTIC_AVAILABLE
except ImportError:
    # For standalone testing or direct execution
    from data_models import AppSettings, PYDANTIC_AVAILABLE

class ConfigManager:
    """
    Manages application configuration loading and saving.
    
    Handles JSON configuration files with template fallback and validation.
    """
    
    def __init__(
        self,
        config_file_path: Union[str, pathlib.Path],
        template_file_path: Union[str, pathlib.Path],
        logger: logging.Logger
    ):
        """
        Initialize the ConfigManager.
        
        Args:
            config_file_path: Path to the main configuration file.
            template_file_path: Path to the template configuration file
                (used as fallback if main file doesn't exist).
            logger: Logger instance for recording operations and errors.
        """
        self.config_file_path = pathlib.Path(config_file_path)
        self.template_file_path = pathlib.Path(template_file_path)
        self.logger = logger
        self.logger.debug(f"ConfigManager initialized with config path: {self.config_file_path}")
    
    def load_settings(self) -> AppSettings:
        """
        Load application settings from configuration file.
        
        If the config file doesn't exist, it's created from the template.
        Validates all settings after loading.
        
        Returns:
            Loaded and validated AppSettings instance.
            
        Raises:
            ValueError: If settings validation fails.
            FileNotFoundError: If neither config nor template file can be found.
            json.JSONDecodeError: If the config file contains invalid JSON.
        """
        # Create config directory if it doesn't exist
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If config file doesn't exist but template does, copy it
        if not self.config_file_path.exists() and self.template_file_path.exists():
            self.logger.info(f"Config file not found. Creating from template: {self.template_file_path}")
            try:
                shutil.copy2(self.template_file_path, self.config_file_path)
                self.logger.info(f"Created config file at: {self.config_file_path}")
            except Exception as e:
                self.logger.error(f"Failed to copy template to config file: {e}")
                # Continue to try loading from template directly
        
        # Determine which file to load from
        source_file = self.config_file_path if self.config_file_path.exists() else self.template_file_path
        
        if not source_file.exists():
            err_msg = "Neither config file nor template exists. Cannot load settings."
            self.logger.critical(err_msg)
            raise FileNotFoundError(err_msg)
        
        self.logger.info(f"Loading settings from: {source_file}")
        
        try:
            # Load and parse JSON file
            with open(source_file, 'r') as f:
                config_data = json.load(f)
                self.logger.debug(f"Successfully read JSON from {source_file}")
            
            # Create settings object from loaded data
            if PYDANTIC_AVAILABLE:
                # Use pydantic's built-in parsing and validation
                settings = AppSettings(**config_data)
                self.logger.debug("Settings validated using pydantic")
            else:
                # Manual approach without pydantic
                settings = AppSettings(**config_data)
                self.logger.debug("Settings created without pydantic validation")
            
            self.logger.info("Settings loaded successfully")
            return settings
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file {source_file}: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Settings validation failed: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error loading settings: {e}")
            raise
    
    def save_settings(self, settings: AppSettings) -> bool:
        """
        Save application settings to the configuration file.
        
        Args:
            settings: The AppSettings instance to save.
            
        Returns:
            True if settings were saved successfully, False otherwise.
        """
        try:
            # Create config directory if it doesn't exist
            self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert settings to dict for JSON serialization
            if PYDANTIC_AVAILABLE:
                # Use pydantic's built-in dict conversion
                settings_dict = settings.dict()
            else:
                # Manual approach without pydantic
                settings_dict = {
                    attr: getattr(settings, attr)
                    for attr in dir(settings)
                    if not attr.startswith('_') and not callable(getattr(settings, attr))
                }
            
            # Write to JSON file with pretty formatting
            with open(self.config_file_path, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            
            self.logger.info(f"Settings saved successfully to {self.config_file_path}")
            return True
            
        except PermissionError:
            self.logger.error(f"Permission denied when writing to config file: {self.config_file_path}")
            return False
        except Exception as e:
            self.logger.exception(f"Error saving settings: {e}")
            return False
    
    def backup_config_file(self, backup_suffix: str = ".backup") -> Optional[pathlib.Path]:
        """
        Create a backup of the current configuration file.
        
        Args:
            backup_suffix: Suffix to append to the original filename for the backup.
            
        Returns:
            Path to the backup file if successful, None otherwise.
        """
        if not self.config_file_path.exists():
            self.logger.warning(f"Cannot backup config file, it doesn't exist: {self.config_file_path}")
            return None
        
        backup_path = self.config_file_path.with_suffix(self.config_file_path.suffix + backup_suffix)
        
        try:
            shutil.copy2(self.config_file_path, backup_path)
            self.logger.info(f"Created config backup at: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create config backup: {e}")
            return None


if __name__ == "__main__":
    """Test the ConfigManager functionality."""
    import sys
    import tempfile
    
    # Set up a test logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    test_logger = logging.getLogger("ConfigManagerTest")
    
    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as config_tmp:
        config_path = pathlib.Path(config_tmp.name)
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as template_tmp:
        template_path = pathlib.Path(template_tmp.name)
    
    try:
        print(f"Testing ConfigManager with:")
        print(f" - Config path: {config_path}")
        print(f" - Template path: {template_path}")
        
        # Create a test template file
        template_data = {
            "game_window_title": "Test Game",
            "roi_x": 10,
            "roi_y": 20,
            "roi_width": 100,
            "roi_height": 50,
            "template_match_threshold": 0.75,
            "sprint_key": "r"
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        # Test loading from template (config doesn't exist yet)
        # First, make sure config doesn't exist
        if config_path.exists():
            os.unlink(config_path)
            
        print("\nTest 1: Loading from template (config doesn't exist)")
        config_manager = ConfigManager(config_path, template_path, test_logger)
        settings = config_manager.load_settings()
        print(f"Loaded settings: game_window_title = {settings.game_window_title}")
        
        # Check that config was created from template
        print(f"Config file exists after loading: {config_path.exists()}")
        
        # Test saving modified settings
        print("\nTest 2: Saving modified settings")
        if PYDANTIC_AVAILABLE:
            settings.game_window_title = "Modified Game" 
        else:
            settings.game_window_title = "Modified Game"
        
        save_result = config_manager.save_settings(settings)
        print(f"Save result: {save_result}")
        
        # Test loading from the config file
        print("\nTest 3: Loading from existing config file")
        config_manager2 = ConfigManager(config_path, template_path, test_logger)
        settings2 = config_manager2.load_settings()
        print(f"Loaded settings: game_window_title = {settings2.game_window_title}")
        
        # Test backup functionality
        print("\nTest 4: Testing config backup")
        backup_path = config_manager.backup_config_file(".test_backup")
        print(f"Backup path: {backup_path}")
        
        print("\nAll tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary files
        for path in [config_path, template_path]:
            try:
                if path.exists():
                    os.unlink(path)
            except Exception as e:
                print(f"Warning: Failed to clean up {path}: {e}")
        
        # Clean up backup file if it exists
        backup_path = config_path.with_suffix(config_path.suffix + ".test_backup")
        if backup_path.exists():
            try:
                os.unlink(backup_path)
            except Exception as e:
                print(f"Warning: Failed to clean up backup file {backup_path}: {e}") 