"""
DAOC Sprint Manager - Functional Test Utilities
=========================================

This module provides utilities for functional testing.
"""

import unittest
import sys
import os
import json
import time
import cv2
import numpy as np
import pygetwindow as gw
import pydirectinput
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testing.test_environment_setup import TestEnvironmentSetup

class MockWindow:
    """Mock window class for testing."""
    
    def __init__(self, title: str, left: int, top: int, width: int, height: int):
        """Initialize mock window.
        
        Args:
            title: Window title
            left: Left position
            top: Top position
            width: Window width
            height: Window height
        """
        self.title = title
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self._visible = True
        self._active = False
        self._hWnd = 12345  # Mock window handle
        
        # Create mock screen content
        self._screen_content = np.zeros((height, width, 3), dtype=np.uint8)
        self._update_screen_content()
    
    def _update_screen_content(self):
        """Update mock screen content with test pattern."""
        # Create a test pattern (e.g., gradient)
        x = np.linspace(0, 255, self.width)
        y = np.linspace(0, 255, self.height)
        xx, yy = np.meshgrid(x, y)
        
        # Create RGB channels
        self._screen_content[:, :, 0] = xx.astype(np.uint8)  # Red channel
        self._screen_content[:, :, 1] = yy.astype(np.uint8)  # Green channel
        self._screen_content[:, :, 2] = ((xx + yy) / 2).astype(np.uint8)  # Blue channel
    
    def get_screen_content(self) -> np.ndarray:
        """Get current screen content.
        
        Returns:
            numpy.ndarray: Current screen content
        """
        return self._screen_content.copy()
    
    def set_screen_content(self, content: np.ndarray):
        """Set screen content.
        
        Args:
            content: New screen content as numpy array
        """
        if content.shape == self._screen_content.shape:
            self._screen_content = content.copy()
    
    def activate(self):
        """Activate the window."""
        self._active = True
    
    def minimize(self):
        """Minimize the window."""
        self._visible = False
    
    def restore(self):
        """Restore the window."""
        self._visible = True
    
    @property
    def visible(self) -> bool:
        """Get window visibility.
        
        Returns:
            bool: True if window is visible
        """
        return self._visible
    
    @property
    def isActive(self) -> bool:
        """Get window active state.
        
        Returns:
            bool: True if window is active
        """
        return self._active
    
    def __str__(self) -> str:
        """Get string representation.
        
        Returns:
            str: String representation of the window
        """
        return f"MockWindow(title='{self.title}', pos=({self.left}, {self.top}), size=({self.width}, {self.height}))"

class DAOCSprintManagerFunctionalTests(unittest.TestCase):
    """Functional tests for DAOC Sprint Manager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_env = TestEnvironmentSetup()
        cls.test_env.setup()
        
        # Create mock window for testing
        cls.mock_window = MockWindow(
            title="Test Game Window",
            left=100,
            top=100,
            width=800,
            height=600
        )
    
    def test_01_window_detection(self):
        """Test window detection functionality."""
        # Test window found
        self.mock_window.restore()
        self.assertTrue(self.mock_window.visible)
        
        # Test window not found
        self.mock_window.minimize()
        self.assertFalse(self.mock_window.visible)
        
        # Test window activation
        self.mock_window.restore()
        self.mock_window.activate()
        self.assertTrue(self.mock_window.isActive)
    
    def test_02_screen_content(self):
        """Test screen content functionality."""
        # Get initial screen content
        content = self.mock_window.get_screen_content()
        self.assertEqual(content.shape, (600, 800, 3))
        
        # Set new screen content
        new_content = np.ones((600, 800, 3), dtype=np.uint8) * 128
        self.mock_window.set_screen_content(new_content)
        
        # Verify content was updated
        updated_content = self.mock_window.get_screen_content()
        np.testing.assert_array_equal(updated_content, new_content)

if __name__ == "__main__":
    unittest.main()