"""
Tests for the InputManager class that handles keyboard input simulation.

This test suite covers:
1. Key code validation
2. Key press/release functionality
3. Complete keypress simulation
4. Error handling for missing dependencies and invalid keys
"""

import unittest
import logging
from unittest.mock import patch, MagicMock, call
import time
import sys

# Import the module under test, using the same import strategy as icon_detector tests
from daoc_sprint_manager.core.input_manager import InputManager, VALID_KEYS, PYDIRECTINPUT_AVAILABLE

class MockLogger:
    """Mock logger to track method calls and messages"""
    def __init__(self):
        self.debug_calls = []
        self.info_calls = []
        self.warning_calls = []
        self.error_calls = []
        self.critical_calls = []
        self.exception_calls = []
        
    def debug(self, msg):
        self.debug_calls.append(msg)
        
    def info(self, msg):
        self.info_calls.append(msg)
        
    def warning(self, msg):
        self.warning_calls.append(msg)
        
    def error(self, msg):
        self.error_calls.append(msg)
        
    def critical(self, msg):
        self.critical_calls.append(msg)
        
    def exception(self, msg):
        self.exception_calls.append(msg)


class TestInputManager(unittest.TestCase):
    """Test cases for the InputManager class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.logger = MockLogger()
        self.input_manager = InputManager(self.logger)
        
        # Create a fake PyDirectInputException for testing
        if not PYDIRECTINPUT_AVAILABLE:
            # Create a dummy exception class if pydirectinput is not available
            self.PyDirectInputException = type('PyDirectInputException', (Exception,), {})
        else:
            import pydirectinput
            self.PyDirectInputException = pydirectinput.PyDirectInputException
    
    def test_init(self):
        """Test initialization and dependency checking"""
        # Test initialization with proper debug logging
        self.assertIn("InputManager initialized", self.logger.debug_calls)
        
        # Test initialization warning when pydirectinput is not available
        if not PYDIRECTINPUT_AVAILABLE:
            self.assertTrue(any("pydirectinput library is not installed" in msg for msg in self.logger.critical_calls))
    
    def test_is_valid_key(self):
        """Test key validation functionality"""
        # Test valid keys
        valid_key = next(iter(VALID_KEYS))  # Get the first valid key
        self.assertTrue(self.input_manager._is_valid_key(valid_key))
        
        # Test valid key with different case
        if valid_key.lower() != valid_key.upper():  # Only test if key has different cases
            self.assertTrue(self.input_manager._is_valid_key(valid_key.upper()))
        
        # Test invalid key
        self.assertFalse(self.input_manager._is_valid_key('invalid_key_name'))
        self.assertTrue(any("Invalid key code" in msg for msg in self.logger.warning_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_press_key_valid(self, mock_pydirectinput):
        """Test press_key with valid key"""
        # Setup
        test_key = 'a'
        
        # Execute
        self.input_manager.press_key(test_key)
        
        # Verify
        mock_pydirectinput.keyDown.assert_called_once_with(test_key)
        self.assertIn(f"Pressing key: '{test_key}'", self.logger.debug_calls)
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_press_key_invalid(self, mock_pydirectinput):
        """Test press_key with invalid key"""
        # Setup
        test_key = 'invalid_key'
        
        # Mock _is_valid_key to return False for this test
        with patch.object(self.input_manager, '_is_valid_key', return_value=False):
            # Execute
            self.input_manager.press_key(test_key)
            
            # Verify
            mock_pydirectinput.keyDown.assert_not_called()
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_press_key_pydirectinput_exception(self, mock_pydirectinput):
        """Test press_key handling of pydirectinput exceptions"""
        # Setup
        test_key = 'a'
        mock_pydirectinput.PyDirectInputException = self.PyDirectInputException
        mock_pydirectinput.keyDown.side_effect = self.PyDirectInputException("Test exception")
        
        # Execute and verify exception is re-raised
        with self.assertRaises(Exception):
            self.input_manager.press_key(test_key)
            
        # Verify error logging
        self.assertTrue(any(f"pydirectinput error pressing key '{test_key}'" in msg 
                            for msg in self.logger.error_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_press_key_general_exception(self, mock_pydirectinput):
        """Test press_key handling of general exceptions"""
        # Setup
        test_key = 'a'
        mock_pydirectinput.keyDown.side_effect = ValueError("Test general exception")
        
        # Execute and verify exception is re-raised
        with self.assertRaises(ValueError):
            self.input_manager.press_key(test_key)
            
        # Verify exception logging
        self.assertTrue(any(f"Unexpected error pressing key '{test_key}'" in msg 
                            for msg in self.logger.exception_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', False)
    def test_press_key_no_pydirectinput(self):
        """Test press_key when pydirectinput is not available"""
        with self.assertRaises(RuntimeError):
            self.input_manager.press_key('a')
        self.assertTrue(any("Cannot press key: pydirectinput is not available" in msg 
                           for msg in self.logger.error_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_release_key_valid(self, mock_pydirectinput):
        """Test release_key with valid key"""
        # Setup
        test_key = 'a'
        
        # Execute
        self.input_manager.release_key(test_key)
        
        # Verify
        mock_pydirectinput.keyUp.assert_called_once_with(test_key)
        self.assertIn(f"Releasing key: '{test_key}'", self.logger.debug_calls)
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_release_key_invalid(self, mock_pydirectinput):
        """Test release_key with invalid key"""
        # Setup
        test_key = 'invalid_key'
        
        # Mock _is_valid_key to return False for this test
        with patch.object(self.input_manager, '_is_valid_key', return_value=False):
            # Execute
            self.input_manager.release_key(test_key)
            
            # Verify
            mock_pydirectinput.keyUp.assert_not_called()
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_release_key_pydirectinput_exception(self, mock_pydirectinput):
        """Test release_key handling of pydirectinput exceptions"""
        # Setup
        test_key = 'a'
        mock_pydirectinput.PyDirectInputException = self.PyDirectInputException
        mock_pydirectinput.keyUp.side_effect = self.PyDirectInputException("Test exception")
        
        # Execute and verify exception is re-raised
        with self.assertRaises(Exception):
            self.input_manager.release_key(test_key)
            
        # Verify error logging
        self.assertTrue(any(f"pydirectinput error releasing key '{test_key}'" in msg 
                            for msg in self.logger.error_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', False)
    def test_release_key_no_pydirectinput(self):
        """Test release_key when pydirectinput is not available"""
        with self.assertRaises(RuntimeError):
            self.input_manager.release_key('a')
        self.assertTrue(any("Cannot release key: pydirectinput is not available" in msg 
                           for msg in self.logger.error_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    @patch('daoc_sprint_manager.core.input_manager.time')
    def test_send_keypress_valid(self, mock_time, mock_pydirectinput):
        """Test send_keypress with valid key"""
        # Setup
        test_key = 'a'
        test_duration = 100
        
        # Execute
        self.input_manager.send_keypress(test_key, press_duration_ms=test_duration)
        
        # Verify
        mock_pydirectinput.keyDown.assert_called_once_with(test_key)
        mock_time.sleep.assert_called_once_with(test_duration / 1000.0)
        mock_pydirectinput.keyUp.assert_called_once_with(test_key)
        self.assertTrue(any(f"Sending keypress: '{test_key}'" in msg for msg in self.logger.info_calls))
        self.assertTrue(any(f"Keypress '{test_key}' completed" in msg for msg in self.logger.debug_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_send_keypress_invalid(self, mock_pydirectinput):
        """Test send_keypress with invalid key"""
        # Setup
        test_key = 'invalid_key'
        
        # Mock _is_valid_key to return False for this test
        with patch.object(self.input_manager, '_is_valid_key', return_value=False):
            # Execute
            self.input_manager.send_keypress(test_key)
            
            # Verify
            mock_pydirectinput.keyDown.assert_not_called()
            mock_pydirectinput.keyUp.assert_not_called()
            self.assertTrue(any(f"Skipping send_keypress for invalid key: {test_key}" in msg 
                               for msg in self.logger.warning_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    @patch('daoc_sprint_manager.core.input_manager.time')
    def test_send_keypress_minimum_duration(self, mock_time, mock_pydirectinput):
        """Test send_keypress with duration less than minimum"""
        # Setup
        test_key = 'a'
        test_duration = 5  # Less than minimum of 10ms
        
        # Execute
        self.input_manager.send_keypress(test_key, press_duration_ms=test_duration)
        
        # Verify minimum sleep duration of 0.01 seconds (10ms)
        mock_time.sleep.assert_called_once_with(0.01)
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    def test_send_keypress_keydown_exception(self, mock_pydirectinput):
        """Test send_keypress handling exceptions during keyDown"""
        # Setup
        test_key = 'a'
        mock_pydirectinput.PyDirectInputException = self.PyDirectInputException
        mock_pydirectinput.keyDown.side_effect = self.PyDirectInputException("keyDown exception")
        
        # Execute and verify exception is re-raised
        with self.assertRaises(Exception):
            self.input_manager.send_keypress(test_key)
            
        # Verify error logging
        self.assertTrue(any(f"pydirectinput error sending keypress '{test_key}'" in msg 
                            for msg in self.logger.error_calls))
        
        # Verify keyUp was not called after exception in keyDown
        mock_pydirectinput.keyUp.assert_not_called()
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', True)
    @patch('daoc_sprint_manager.core.input_manager.pydirectinput')
    @patch('daoc_sprint_manager.core.input_manager.time')
    def test_send_keypress_keyup_exception(self, mock_time, mock_pydirectinput):
        """Test send_keypress handling exceptions during keyUp"""
        # Setup
        test_key = 'a'
        mock_pydirectinput.PyDirectInputException = self.PyDirectInputException
        mock_pydirectinput.keyUp.side_effect = self.PyDirectInputException("keyUp exception")
        
        # Execute and verify exception is re-raised
        with self.assertRaises(Exception):
            self.input_manager.send_keypress(test_key)
            
        # Verify keyDown was called but then exception was raised in keyUp
        mock_pydirectinput.keyDown.assert_called_once()
        self.assertTrue(any(f"pydirectinput error sending keypress '{test_key}'" in msg 
                            for msg in self.logger.error_calls))
    
    @patch('daoc_sprint_manager.core.input_manager.PYDIRECTINPUT_AVAILABLE', False)
    def test_send_keypress_no_pydirectinput(self):
        """Test send_keypress when pydirectinput is not available"""
        with self.assertRaises(RuntimeError):
            self.input_manager.send_keypress('a')
        self.assertTrue(any("Cannot send keypress: pydirectinput is not available" in msg 
                           for msg in self.logger.error_calls))


if __name__ == "__main__":
    unittest.main() 