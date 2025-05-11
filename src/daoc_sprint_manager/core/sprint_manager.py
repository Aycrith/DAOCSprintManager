"""
Sprint Manager module for DAOC Sprint Manager.

This is a mock implementation for test purposes.
"""

import logging
import threading
import time
from typing import Any, Optional

class SprintManager:
    """
    Mock implementation of the SprintManager for testing.
    
    In a real implementation, this would manage the detection and toggling
    of the sprint state in the game.
    """
    
    def __init__(self, app_settings: Any = None, logger: Optional[logging.Logger] = None):
        """Initialize the SprintManager.
        
        Args:
            app_settings: Application settings
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.app_settings = app_settings
        self.is_active = False
        self.stop_event = threading.Event()
        self.logger.info("Mock SprintManager initialized")
        
    def toggle(self) -> bool:
        """Toggle the sprint detection state.
        
        Returns:
            Current state after toggling (True for active, False for inactive)
        """
        self.is_active = not self.is_active
        status = "active" if self.is_active else "inactive"
        self.logger.info(f"Sprint detection {status}")
        return self.is_active
        
    def stop(self) -> None:
        """Stop sprint detection."""
        self.is_active = False
        self.stop_event.set()
        self.logger.info("Sprint detection stopped") 