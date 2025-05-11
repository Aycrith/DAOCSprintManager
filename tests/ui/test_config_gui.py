"""
Tests for the ConfigGUI class that handles application settings configuration.

This test suite covers:
1. Loading settings into UI elements
2. Collecting settings from UI elements
3. Validation of user input
4. Button actions (apply, ok, cancel)
5. ROI selection functionality
"""

import unittest
import logging
import tempfile
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from unittest.mock import patch, MagicMock, call, PropertyMock
import sys
import os

# Import the modules under test
try:
    from daoc_sprint_manager.ui.config_gui import ConfigGUI, Tooltip
    from daoc_sprint_manager.config_manager import ConfigManager
    from daoc_sprint_manager.data_models import AppSettings
except ImportError:
    # Adjust for test environment if needed
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.daoc_sprint_manager.ui.config_gui import ConfigGUI, Tooltip
    from src.daoc_sprint_manager.config_manager import ConfigManager
    from src.daoc_sprint_manager.data_models import AppSettings


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


class TestConfigGUI(unittest.TestCase):
    """Test cases for the ConfigGUI class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a root Tkinter window that will be withdrawn (not visible)
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create a mock logger
        self.logger = MockLogger()
        
        # Create a mock ConfigManager
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        
        # Create a default AppSettings for testing
        self.test_settings = AppSettings(
            game_window_title="Test Game Window",
            roi_x=100,
            roi_y=100,
            roi_width=300,
            roi_height=200,
            sprint_on_icon_path="data/icons/test_on.png",
            sprint_off_icon_path="data/icons/test_off.png",
            template_match_threshold=0.85,
            sprint_key="z",
            ml_input_size_wh=[32, 48]  # Test different width/height
        )
        
        # Create a mock for apply callback
        self.mock_apply_callback = MagicMock()
        
        # Create a mock for destroy handler
        self.mock_destroy_handler = MagicMock()
        
        # Initialize ConfigGUI with mocks
        self.config_gui = ConfigGUI(
            master=self.root,
            config_manager=self.mock_config_manager,
            current_settings=self.test_settings,
            logger=self.logger,
            on_apply_callback=self.mock_apply_callback,
            destroy_handler=self.mock_destroy_handler
        )
        
        # Patch messagebox functions to prevent actual dialogs
        self.patcher_messagebox = patch('tkinter.messagebox')
        self.mock_messagebox = self.patcher_messagebox.start()
        
        # Patch PIL.ImageGrab for ROI selection tests
        self.patcher_imagegrab = patch('PIL.ImageGrab')
        self.mock_imagegrab = self.patcher_imagegrab.start()
        
        # Patch PIL.ImageTk for ROI selection tests
        self.patcher_imagetk = patch('PIL.ImageTk')
        self.mock_imagetk = self.patcher_imagetk.start()
    
    def tearDown(self):
        """Clean up resources after each test"""
        # Stop patchers
        self.patcher_messagebox.stop()
        self.patcher_imagegrab.stop()
        self.patcher_imagetk.stop()
        
        # Destroy the GUI
        try:
            self.config_gui.dialog.destroy()
        except:
            pass  # Already destroyed
        
        # Destroy the root window
        self.root.destroy()
    
    def test_init(self):
        """Test initialization of ConfigGUI"""
        # Check that ConfigGUI initialized correctly
        self.assertEqual(self.config_gui.master, self.root)
        self.assertEqual(self.config_gui.config_manager, self.mock_config_manager)
        self.assertEqual(self.config_gui.initial_settings, self.test_settings)
        self.assertEqual(self.config_gui.on_apply_callback, self.mock_apply_callback)
        self.assertEqual(self.config_gui.destroy_handler, self.mock_destroy_handler)
        self.assertFalse(self.config_gui.unsaved_changes)
        
        # Check that the dialog was created
        self.assertIsInstance(self.config_gui.dialog, tk.Toplevel)
        
        # Check logger message
        self.assertIn("Configuration GUI initialized", self.logger.info_calls)
        
        # Check that tabbed interface was created
        self.assertIsInstance(self.config_gui.notebook, tk.ttk.Notebook)
        
        # Check that all expected tabs exist
        self.assertTrue(hasattr(self.config_gui, 'tab_general'))
        self.assertTrue(hasattr(self.config_gui, 'tab_detection'))
        self.assertTrue(hasattr(self.config_gui, 'tab_performance'))
        self.assertTrue(hasattr(self.config_gui, 'tab_advanced'))
        
        # Check action buttons exist
        self.assertTrue(hasattr(self.config_gui, 'apply_button'))
        self.assertTrue(hasattr(self.config_gui, 'cancel_button'))
        self.assertTrue(hasattr(self.config_gui, 'ok_button'))
    
    def test_load_settings_to_ui(self):
        """Test loading settings into UI elements"""
        # Create alternative test settings
        test_settings2 = AppSettings(
            game_window_title="Another Game Window",
            roi_x=200,
            roi_y=150,
            roi_width=400,
            roi_height=300,
            sprint_on_icon_path="data/icons/another_on.png",
            sprint_off_icon_path="data/icons/another_off.png",
            template_match_threshold=0.9,
            sprint_key="x",
            ml_input_size_wh=[64, 48]
        )
        
        # Reload the UI with new settings
        self.config_gui._load_settings_to_ui(test_settings2)
        
        # Check some key widget variables to ensure they were updated correctly
        self.assertEqual(self.config_gui.widgets['game_window_title']['var'].get(), "Another Game Window")
        self.assertEqual(self.config_gui.widgets['roi_x']['var'].get(), "200")  # String because it's from an Entry widget
        self.assertEqual(self.config_gui.widgets['roi_y']['var'].get(), "150")
        self.assertEqual(self.config_gui.widgets['roi_width']['var'].get(), "400")
        self.assertEqual(self.config_gui.widgets['roi_height']['var'].get(), "300")
        self.assertEqual(self.config_gui.widgets['sprint_on_icon_path']['var'].get(), "data/icons/another_on.png")
        self.assertEqual(self.config_gui.widgets['sprint_off_icon_path']['var'].get(), "data/icons/another_off.png")
        self.assertEqual(float(self.config_gui.widgets['template_match_threshold']['var'].get()), 0.9)
        self.assertEqual(self.config_gui.widgets['sprint_key']['var'].get(), "x")
        
        # Check ML input size was split correctly
        self.assertEqual(self.config_gui.widgets['ml_input_width']['var'].get(), "64")
        self.assertEqual(self.config_gui.widgets['ml_input_height']['var'].get(), "48")
    
    def test_collect_settings_from_ui(self):
        """Test collecting settings from UI elements"""
        # Manually modify some widget variables to simulate user input
        self.config_gui.widgets['game_window_title']['var'].set("Modified Game Window")
        self.config_gui.widgets['roi_x']['var'].set("250")
        self.config_gui.widgets['roi_y']['var'].set("300")
        self.config_gui.widgets['roi_width']['var'].set("350")
        self.config_gui.widgets['roi_height']['var'].set("400")
        self.config_gui.widgets['template_match_threshold']['var'].set(0.95)
        self.config_gui.widgets['sprint_key']['var'].set("c")
        self.config_gui.widgets['ml_input_width']['var'].set("80")
        self.config_gui.widgets['ml_input_height']['var'].set("60")
        
        # Collect settings from UI
        collected_settings = self.config_gui._collect_settings_from_ui()
        
        # Check type
        self.assertIsInstance(collected_settings, AppSettings)
        
        # Check that values were collected correctly
        self.assertEqual(collected_settings.game_window_title, "Modified Game Window")
        self.assertEqual(collected_settings.roi_x, 250)  # Should convert from string to int
        self.assertEqual(collected_settings.roi_y, 300)
        self.assertEqual(collected_settings.roi_width, 350)
        self.assertEqual(collected_settings.roi_height, 400)
        self.assertEqual(collected_settings.template_match_threshold, 0.95)
        self.assertEqual(collected_settings.sprint_key, "c")
        
        # Check that ml_input_size_wh combined width and height correctly
        self.assertEqual(collected_settings.ml_input_size_wh, [80, 60])
    
    def test_validate_ui_settings_valid(self):
        """Test validation with valid settings"""
        # All settings are valid by default from our setUp
        result = self.config_gui._validate_ui_settings()
        self.assertTrue(result)
    
    def test_validate_ui_settings_invalid_numeric_range(self):
        """Test validation with numeric values out of range"""
        # Set template_match_threshold to invalid value (outside 0.0-1.0 range)
        self.config_gui.widgets['template_match_threshold']['var'].set(1.5)
        
        # Validation should fail
        result = self.config_gui._validate_ui_settings()
        self.assertFalse(result)
        
        # Reset to valid value
        self.config_gui.widgets['template_match_threshold']['var'].set(0.8)
        
        # Set ROI values to negative (invalid)
        self.config_gui.widgets['roi_x']['var'].set("-10")
        
        # Validation should fail
        result = self.config_gui._validate_ui_settings()
        self.assertFalse(result)
    
    def test_validate_ui_settings_invalid_file_path(self):
        """Test validation with invalid file paths"""
        # Set a non-existent file path
        self.config_gui.widgets['sprint_on_icon_path']['var'].set("/path/to/nonexistent/file.png")
        
        # Mock the _validate_file_path method to simulate validation failure
        with patch.object(self.config_gui, '_validate_file_path', return_value=False):
            result = self.config_gui._validate_ui_settings()
            self.assertFalse(result)
    
    def test_validate_ui_settings_invalid_empty_fields(self):
        """Test validation with empty required fields"""
        # Set an empty game window title
        self.config_gui.widgets['game_window_title']['var'].set("")
        
        # Validation should fail
        result = self.config_gui._validate_ui_settings()
        self.assertFalse(result)
    
    def test_validate_numeric_range(self):
        """Test validation of numeric ranges"""
        # Create a mock widget variable with a valid value
        mock_var = MagicMock()
        mock_var.get.return_value = "50"
        
        # Test valid integer in range
        result = self.config_gui._validate_numeric_range(mock_var, 0, 100, "test_setting", int_only=True)
        self.assertTrue(result)
        
        # Test invalid integer (below min)
        mock_var.get.return_value = "-10"
        result = self.config_gui._validate_numeric_range(mock_var, 0, 100, "test_setting", int_only=True)
        self.assertFalse(result)
        
        # Test invalid integer (above max)
        mock_var.get.return_value = "150"
        result = self.config_gui._validate_numeric_range(mock_var, 0, 100, "test_setting", int_only=True)
        self.assertFalse(result)
        
        # Test valid float in range
        mock_var.get.return_value = "0.5"
        result = self.config_gui._validate_numeric_range(mock_var, 0.0, 1.0, "test_setting", int_only=False)
        self.assertTrue(result)
        
        # Test invalid float (below min)
        mock_var.get.return_value = "-0.1"
        result = self.config_gui._validate_numeric_range(mock_var, 0.0, 1.0, "test_setting", int_only=False)
        self.assertFalse(result)
        
        # Test invalid float (above max)
        mock_var.get.return_value = "1.1"
        result = self.config_gui._validate_numeric_range(mock_var, 0.0, 1.0, "test_setting", int_only=False)
        self.assertFalse(result)
        
        # Test invalid format (not a number)
        mock_var.get.return_value = "not_a_number"
        result = self.config_gui._validate_numeric_range(mock_var, 0, 100, "test_setting", int_only=True)
        self.assertFalse(result)
    
    def test_validate_file_path(self):
        """Test validation of file paths"""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            valid_path = tmp_file.name
        
        try:
            # Create a mock widget variable
            mock_var = MagicMock()
            
            # Test with valid existing file
            mock_var.get.return_value = valid_path
            result = self.config_gui._validate_file_path(mock_var, "test_file", must_exist=True, expected_exts=[".png"])
            self.assertTrue(result)
            
            # Test with non-existent file when must_exist=True
            mock_var.get.return_value = "/path/to/nonexistent/file.png"
            result = self.config_gui._validate_file_path(mock_var, "test_file", must_exist=True)
            self.assertFalse(result)
            
            # Test with non-existent file when must_exist=False
            mock_var.get.return_value = "/path/to/nonexistent/file.png"
            result = self.config_gui._validate_file_path(mock_var, "test_file", must_exist=False)
            self.assertTrue(result)
            
            # Test with wrong extension
            mock_var.get.return_value = valid_path
            result = self.config_gui._validate_file_path(mock_var, "test_file", must_exist=True, expected_exts=[".jpg"])
            self.assertFalse(result)
            
            # Test with empty path
            mock_var.get.return_value = ""
            result = self.config_gui._validate_file_path(mock_var, "test_file", must_exist=True)
            self.assertFalse(result)
            
        finally:
            # Clean up temporary file
            os.unlink(valid_path)
    
    def test_validate_not_empty(self):
        """Test validation of non-empty fields"""
        # Create a mock widget variable
        mock_var = MagicMock()
        
        # Test with non-empty value
        mock_var.get.return_value = "valid value"
        result = self.config_gui._validate_not_empty(mock_var, "test_setting")
        self.assertTrue(result)
        
        # Test with empty value
        mock_var.get.return_value = ""
        result = self.config_gui._validate_not_empty(mock_var, "test_setting")
        self.assertFalse(result)
        
        # Test with whitespace-only value
        mock_var.get.return_value = "   "
        result = self.config_gui._validate_not_empty(mock_var, "test_setting")
        self.assertFalse(result)
    
    def test_apply_settings_valid(self):
        """Test applying valid settings"""
        # Mock _validate_ui_settings to return True
        with patch.object(self.config_gui, '_validate_ui_settings', return_value=True):
            # Mock _collect_settings_from_ui to return our test settings
            with patch.object(self.config_gui, '_collect_settings_from_ui', return_value=self.test_settings):
                # Call _apply_settings
                result = self.config_gui._apply_settings()
                
                # Check result
                self.assertTrue(result)
                
                # Check that save_settings was called
                self.mock_config_manager.save_settings.assert_called_once_with(self.test_settings)
                
                # Check that on_apply_callback was called
                self.mock_apply_callback.assert_called_once_with(self.test_settings)
                
                # Check that unsaved_changes was set to False
                self.assertFalse(self.config_gui.unsaved_changes)
    
    def test_apply_settings_invalid(self):
        """Test applying invalid settings"""
        # Mock _validate_ui_settings to return False
        with patch.object(self.config_gui, '_validate_ui_settings', return_value=False):
            # Call _apply_settings
            result = self.config_gui._apply_settings()
            
            # Check result
            self.assertFalse(result)
            
            # Check that save_settings was not called
            self.mock_config_manager.save_settings.assert_not_called()
            
            # Check that on_apply_callback was not called
            self.mock_apply_callback.assert_not_called()
    
    def test_apply_settings_exception(self):
        """Test handling of exceptions during save_settings"""
        # Mock _validate_ui_settings to return True
        with patch.object(self.config_gui, '_validate_ui_settings', return_value=True):
            # Mock _collect_settings_from_ui to return our test settings
            with patch.object(self.config_gui, '_collect_settings_from_ui', return_value=self.test_settings):
                # Mock save_settings to raise an exception
                self.mock_config_manager.save_settings.side_effect = Exception("Test exception")
                
                # Call _apply_settings
                result = self.config_gui._apply_settings()
                
                # Check result
                self.assertFalse(result)
                
                # Check that on_apply_callback was not called
                self.mock_apply_callback.assert_not_called()
                
                # Check that messagebox.showerror was called
                self.mock_messagebox.showerror.assert_called_once()
    
    def test_ok_settings_valid(self):
        """Test OK button action with valid settings"""
        # Mock _apply_settings to return True
        with patch.object(self.config_gui, '_apply_settings', return_value=True):
            # Patch dialog.destroy to prevent actual destruction
            with patch.object(self.config_gui.dialog, 'destroy') as mock_destroy:
                # Call _ok_settings
                self.config_gui._ok_settings()
                
                # Check that dialog.destroy was called
                mock_destroy.assert_called_once()
                
                # Check that destroy_handler was called with True
                self.mock_destroy_handler.assert_called_once_with(True)
    
    def test_ok_settings_invalid(self):
        """Test OK button action with invalid settings"""
        # Mock _apply_settings to return False
        with patch.object(self.config_gui, '_apply_settings', return_value=False):
            # Patch dialog.destroy to prevent actual destruction
            with patch.object(self.config_gui.dialog, 'destroy') as mock_destroy:
                # Call _ok_settings
                self.config_gui._ok_settings()
                
                # Check that dialog.destroy was not called
                mock_destroy.assert_not_called()
                
                # Check that destroy_handler was not called
                self.mock_destroy_handler.assert_not_called()
    
    def test_cancel_settings_with_changes(self):
        """Test Cancel button action with unsaved changes"""
        # Set unsaved_changes to True
        self.config_gui.unsaved_changes = True
        
        # Mock messagebox.askyesno to return True (user confirms cancel)
        self.mock_messagebox.askyesno.return_value = True
        
        # Patch dialog.destroy to prevent actual destruction
        with patch.object(self.config_gui.dialog, 'destroy') as mock_destroy:
            # Call _cancel_settings
            self.config_gui._cancel_settings()
            
            # Check that messagebox.askyesno was called
            self.mock_messagebox.askyesno.assert_called_once()
            
            # Check that dialog.destroy was called
            mock_destroy.assert_called_once()
            
            # Check that destroy_handler was called with False
            self.mock_destroy_handler.assert_called_once_with(False)
    
    def test_cancel_settings_with_changes_canceled(self):
        """Test Cancel button action with unsaved changes but user cancels"""
        # Set unsaved_changes to True
        self.config_gui.unsaved_changes = True
        
        # Mock messagebox.askyesno to return False (user cancels)
        self.mock_messagebox.askyesno.return_value = False
        
        # Patch dialog.destroy to prevent actual destruction
        with patch.object(self.config_gui.dialog, 'destroy') as mock_destroy:
            # Call _cancel_settings
            self.config_gui._cancel_settings()
            
            # Check that messagebox.askyesno was called
            self.mock_messagebox.askyesno.assert_called_once()
            
            # Check that dialog.destroy was not called
            mock_destroy.assert_not_called()
            
            # Check that destroy_handler was not called
            self.mock_destroy_handler.assert_not_called()
    
    def test_cancel_settings_without_changes(self):
        """Test Cancel button action without unsaved changes"""
        # Set unsaved_changes to False
        self.config_gui.unsaved_changes = False
        
        # Patch dialog.destroy to prevent actual destruction
        with patch.object(self.config_gui.dialog, 'destroy') as mock_destroy:
            # Call _cancel_settings
            self.config_gui._cancel_settings()
            
            # Check that messagebox.askyesno was not called
            self.mock_messagebox.askyesno.assert_not_called()
            
            # Check that dialog.destroy was called
            mock_destroy.assert_called_once()
            
            # Check that destroy_handler was called with False
            self.mock_destroy_handler.assert_called_once_with(False)
    
    def test_mark_as_changed(self):
        """Test the _mark_as_changed method"""
        # Set unsaved_changes to False initially
        self.config_gui.unsaved_changes = False
        
        # Call _mark_as_changed
        self.config_gui._mark_as_changed()
        
        # Check that unsaved_changes was set to True
        self.assertTrue(self.config_gui.unsaved_changes)
    
    @patch('tkinter.Toplevel')
    def test_select_roi_visual(self, mock_toplevel):
        """Test the ROI selection functionality initialization"""
        # Mock ImageGrab.grab to return a dummy image
        mock_image = MagicMock()
        self.mock_imagegrab.grab.return_value = mock_image
        
        # Mock ImageTk.PhotoImage
        mock_photo_image = MagicMock()
        self.mock_imagetk.PhotoImage.return_value = mock_photo_image
        
        # Call _select_roi_visual
        self.config_gui._select_roi_visual()
        
        # Check that a toplevel window was created
        self.assertIsNotNone(self.config_gui.roi_selector_window)
        
        # Check that ImageGrab.grab was called
        self.mock_imagegrab.grab.assert_called_once()
        
        # Check that ImageTk.PhotoImage was called with the screenshot
        self.mock_imagetk.PhotoImage.assert_called_once_with(mock_image)
    
    def test_confirm_roi_selection(self):
        """Test the ROI selection confirmation"""
        # Setup mock ROI window and selected coordinates
        self.config_gui.roi_selector_window = MagicMock()
        self.config_gui._selected_roi_coords = (100, 150, 400, 350)  # (x1, y1, x2, y2)
        
        # Call _confirm_roi_selection
        self.config_gui._confirm_roi_selection()
        
        # Check that the ROI widgets were updated correctly
        self.assertEqual(self.config_gui.widgets['roi_x']['var'].get(), "100")
        self.assertEqual(self.config_gui.widgets['roi_y']['var'].get(), "150")
        self.assertEqual(self.config_gui.widgets['roi_width']['var'].get(), "300")  # 400 - 100
        self.assertEqual(self.config_gui.widgets['roi_height']['var'].get(), "200")  # 350 - 150
        
        # Check that unsaved_changes was set to True
        self.assertTrue(self.config_gui.unsaved_changes)
        
        # Check that the ROI selector window was destroyed
        self.config_gui.roi_selector_window.destroy.assert_called_once()
    
    def test_cancel_roi_selection(self):
        """Test canceling ROI selection"""
        # Setup mock ROI window
        self.config_gui.roi_selector_window = MagicMock()
        
        # Call _cancel_roi_selection
        self.config_gui._cancel_roi_selection()
        
        # Check that the ROI selector window was destroyed
        self.config_gui.roi_selector_window.destroy.assert_called_once()


class TestTooltip(unittest.TestCase):
    """Test cases for the Tooltip class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.widget = tk.Label(self.root, text="Test Widget")
        self.tooltip_text = "This is a test tooltip"
        self.tooltip = Tooltip(self.widget, self.tooltip_text)
    
    def tearDown(self):
        """Clean up resources after each test"""
        self.root.destroy()
    
    def test_init(self):
        """Test initialization of Tooltip"""
        self.assertEqual(self.tooltip.widget, self.widget)
        self.assertEqual(self.tooltip.text, self.tooltip_text)
        self.assertIsNone(self.tooltip.tooltip_window)
    
    def test_on_enter(self):
        """Test tooltip appears on mouse enter"""
        # Mock tk.Toplevel
        with patch('tkinter.Toplevel') as mock_toplevel:
            # Mock instance of Toplevel
            mock_toplevel_instance = MagicMock()
            mock_toplevel.return_value = mock_toplevel_instance
            
            # Call _on_enter
            self.tooltip._on_enter()
            
            # Check that a toplevel window was created
            mock_toplevel.assert_called_once_with(self.widget)
            
            # Check that window configuration methods were called
            mock_toplevel_instance.wm_overrideredirect.assert_called_once_with(True)
            mock_toplevel_instance.wm_geometry.assert_called_once()
            
            # Check that the tooltip window was set
            self.assertEqual(self.tooltip.tooltip_window, mock_toplevel_instance)
    
    def test_on_leave(self):
        """Test tooltip disappears on mouse leave"""
        # Create a mock tooltip window
        self.tooltip.tooltip_window = MagicMock()
        
        # Call _on_leave
        self.tooltip._on_leave()
        
        # Check that the tooltip window was destroyed
        self.tooltip.tooltip_window.destroy.assert_called_once()
        
        # Check that tooltip_window was set to None
        self.assertIsNone(self.tooltip.tooltip_window)


if __name__ == '__main__':
    unittest.main() 