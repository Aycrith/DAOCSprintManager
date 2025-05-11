"""
ROI Helper utility for DAOC Sprint Manager.

Helps users configure the Region of Interest (ROI) for sprint icon detection.
"""

import argparse
import json
import logging
import os
import pathlib
import sys
import time
from typing import Dict, List, Optional, Tuple

try:
    import cv2
    import numpy as np
    import pygetwindow as gw
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    print("Error: Required libraries not installed.")
    print("Install with: pip install opencv-python numpy pygetwindow pillow")
    sys.exit(1)

# Try to import tkinter for the GUI
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter not available. Limited functionality only.")

# Get the project root directory
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "src" / "daoc_sprint_manager" / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "settings.json"

class ROISelector:
    """Helper for selecting the Region of Interest in the game window."""
    
    def __init__(self, window_title: str, config_path: pathlib.Path = DEFAULT_CONFIG_PATH):
        """Initialize the ROI selector.
        
        Args:
            window_title: Title of the game window to capture from.
            config_path: Path to the configuration file to update.
        """
        self.window_title = window_title
        self.config_path = config_path
        self.roi = (0, 0, 100, 100)  # Default ROI (x, y, width, height)
        self.config = self._load_config()
        self.setting_roi = False
        self.mouse_points = []
        
        # Preload any existing ROI from config
        if self.config:
            self.roi = (
                self.config.get("roi_x", 0),
                self.config.get("roi_y", 0),
                self.config.get("roi_width", 100),
                self.config.get("roi_height", 100)
            )
    
    def _load_config(self) -> Dict:
        """Load the configuration file.
        
        Returns:
            Dictionary containing configuration settings.
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _save_config(self) -> bool:
        """Save the updated configuration file.
        
        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update ROI in config
            self.config["roi_x"] = self.roi[0]
            self.config["roi_y"] = self.roi[1]
            self.config["roi_width"] = self.roi[2]
            self.config["roi_height"] = self.roi[3]
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"Saved ROI configuration to {self.config_path}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _find_game_window(self) -> Optional[gw.Win32Window]:
        """Find the game window by title.
        
        Returns:
            Game window object if found, None otherwise.
        """
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                return windows[0]
            print(f"No window found with title '{self.window_title}'")
            return None
        except Exception as e:
            print(f"Error finding window: {e}")
            return None
    
    def _capture_window(self, window: gw.Win32Window) -> Optional[np.ndarray]:
        """Capture a screenshot of the window.
        
        Args:
            window: Window object to capture.
            
        Returns:
            Screenshot image as numpy array, or None if failed.
        """
        try:
            # Make sure the window is active
            try:
                window.activate()
                time.sleep(0.2)  # Give time for window to activate
            except Exception as e:
                print(f"Could not activate window: {e}")
            
            # Get window position and size
            left, top = window.left, window.top
            width, height = window.width, window.height
            
            # Take screenshot using PIL
            from PIL import ImageGrab
            screenshot = ImageGrab.grab((left, top, left + width, top + height))
            
            # Convert to numpy array for OpenCV
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error capturing window: {e}")
            return None
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Mouse event callback for ROI selection."""
        if not self.setting_roi:
            return
            
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.mouse_points) < 2:
                self.mouse_points.append((x, y))
                if len(self.mouse_points) == 2:
                    # Calculate ROI from two points
                    x1, y1 = self.mouse_points[0]
                    x2, y2 = self.mouse_points[1]
                    self.roi = (
                        min(x1, x2),                  # x
                        min(y1, y2),                  # y
                        abs(x2 - x1),                 # width
                        abs(y2 - y1)                  # height
                    )
                    self.setting_roi = False
                    print(f"ROI set to: {self.roi}")
                    
                    # Update the display
                    if 'image' in param and 'window_name' in param:
                        self._draw_roi(param['image'], param['window_name'])
    
    def _draw_roi(self, image: np.ndarray, window_name: str) -> None:
        """Draw the ROI on the image and show it.
        
        Args:
            image: Image to draw on.
            window_name: Name of the display window.
        """
        image_copy = image.copy()
        x, y, w, h = self.roi
        
        # Draw the ROI rectangle
        cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add text with ROI coordinates
        roi_text = f"ROI: ({x}, {y}, {w}, {h})"
        cv2.putText(
            image_copy, roi_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        
        # Show the image
        cv2.imshow(window_name, image_copy)
    
    def select_roi_opencv(self) -> bool:
        """Use OpenCV to select the ROI.
        
        Returns:
            True if ROI was selected successfully, False otherwise.
        """
        # Find the game window
        window = self._find_game_window()
        if not window:
            return False
        
        # Capture the window
        image = self._capture_window(window)
        if image is None:
            return False
        
        # Create a window for ROI selection
        window_name = "ROI Selection - Click top-left then bottom-right corners"
        cv2.namedWindow(window_name)
        
        # Set up the mouse callback
        self.setting_roi = True
        self.mouse_points = []
        param = {'image': image, 'window_name': window_name}
        cv2.setMouseCallback(window_name, self._mouse_callback, param)
        
        # Show the initial image
        cv2.imshow(window_name, image)
        
        # Draw ROI if already set
        if all(v > 0 for v in self.roi[2:]):
            self._draw_roi(image, window_name)
        
        print("Click on the top-left corner of the sprint icon area, then on the bottom-right corner.")
        print("Press 'S' to save, 'R' to reset, or 'Q' to quit without saving.")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Quitting without saving.")
                break
                
            elif key == ord('r'):
                self.setting_roi = True
                self.mouse_points = []
                cv2.imshow(window_name, image)
                print("ROI selection reset. Click on the top-left corner, then on the bottom-right corner.")
                
            elif key == ord('s'):
                if all(v > 0 for v in self.roi[2:]):
                    saved = self._save_config()
                    if saved:
                        print("ROI saved successfully!")
                    break
                else:
                    print("Invalid ROI. Please select a valid region first.")
        
        # Clean up
        cv2.destroyAllWindows()
        return all(v > 0 for v in self.roi[2:])
    
    def print_instructions(self) -> None:
        """Print instructions for using the ROI selector."""
        print("\n=== ROI Selection Instructions ===")
        print("1. Make sure your game window is visible")
        print("2. The game window will be captured")
        print("3. Click on the top-left corner of your sprint icon")
        print("4. Then click on the bottom-right corner to complete the selection")
        print("5. Press 'S' to save, 'R' to reset, or 'Q' to quit without saving")
        print("=====================================\n")

def main():
    """Main function to run the ROI helper."""
    parser = argparse.ArgumentParser(description='ROI Helper for DAOC Sprint Manager')
    parser.add_argument('--title', type=str, default="Dark Age of Camelot",
                        help='Window title to search for')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to config file (default: PROJECT_ROOT/src/daoc_sprint_manager/config/settings.json)')
    args = parser.parse_args()
    
    # Set up the config path
    config_path = DEFAULT_CONFIG_PATH
    if args.config:
        config_path = pathlib.Path(args.config)
    
    # Create the ROI selector
    selector = ROISelector(args.title, config_path)
    
    # Print instructions
    selector.print_instructions()
    
    # Run the ROI selection
    success = selector.select_roi_opencv()
    
    if success:
        print("\nROI selection completed successfully.")
        print(f"Updated settings saved to: {config_path}")
    else:
        print("\nROI selection was not completed or had an error.")

if __name__ == "__main__":
    main() 