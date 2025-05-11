#!/usr/bin/env python3
"""
DAOC Sprint Manager - Main Entry Point
====================================

This module serves as the main entry point for the application.
"""

import argparse
import logging
import sys
from pathlib import Path

from daoc_sprint_manager.core.app_settings import AppSettings
from daoc_sprint_manager.core.sprint_manager import SprintManager
from daoc_sprint_manager.ui.system_tray import SystemTrayUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DAOC Sprint Manager")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode with mock windows")
    parser.add_argument("--window-title", default="MOCK_GAME", help="Window title to use in test mode")
    parser.add_argument("--capture-fps", type=int, default=30, help="Capture FPS for test mode")
    parser.add_argument("--detection-method", choices=["template", "ml"], default="template",
                       help="Detection method to use (template or ml)")
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize components
        settings = AppSettings()
        
        # Update settings based on command line arguments
        if args.test_mode:
            logger.info("Running in test mode")
            settings.test_mode = True
            settings.test_window_title = args.window_title
            settings.capture_fps = args.capture_fps
            settings.detection_method = args.detection_method
        
        sprint_manager = SprintManager(settings)
        system_tray = SystemTrayUI(sprint_manager)
        
        # Run the application
        logger.info("Starting DAOC Sprint Manager")
        system_tray.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 