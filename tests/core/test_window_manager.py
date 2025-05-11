import unittest
from unittest.mock import patch, MagicMock, ANY
import logging
import sys
from pathlib import Path
import numpy as np

# Adjust sys.path to allow importing from the src directory
# This assumes the tests directory is at the same level as the src directory
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent 
src_root = project_root / "src"
sys.path.insert(0, str(project_root)) # Add project root for general imports
sys.path.insert(0, str(src_root)) # Add src for daoc_sprint_manager imports

# Create mocks outside patches so we can set them up
mock_pygetwindow = MagicMock()
mock_win32gui = MagicMock()
mock_win32ui = MagicMock()
mock_win32con = MagicMock()
mock_cv2 = MagicMock()


class MockLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.log_messages = []

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        self.log_messages.append((level, msg, args))
        # For testing, we can also print if needed:
        # print(f"{logging.getLevelName(level)}: {msg % args if args else msg}")

    def assert_message_logged(self, level, expected_msg_part):
        found = any(
            log_level == level and (expected_msg_part in msg_format or (args and expected_msg_part in (msg_format % args)))
            for log_level, msg_format, args in self.log_messages
        )
        if not found:
            raise AssertionError(f"Expected message part '{expected_msg_part}' with level {logging.getLevelName(level)} not found in logs. Logs: {self.log_messages}")
        return True


class TestWindowManager(unittest.TestCase):
    def setUp(self):
        # Setup mocks
        self.setup_pygetwindow_mocks()
        self.setup_win32_mocks()
        self.setup_cv2_mocks()
        
        # Apply patches to sys.modules
        self.module_patches = [
            patch.dict('sys.modules', {'pygetwindow': mock_pygetwindow}),
            patch.dict('sys.modules', {'win32gui': mock_win32gui}),
            patch.dict('sys.modules', {'win32ui': mock_win32ui}),
            patch.dict('sys.modules', {'win32con': mock_win32con}),
            patch.dict('sys.modules', {'cv2': mock_cv2})
        ]
        
        for p in self.module_patches:
            p.start()
            self.addCleanup(p.stop)
        
        # Now import the WindowManager after patching sys.modules
        # This reload trick ensures our patched modules are used
        import importlib
        if 'daoc_sprint_manager.core.window_manager' in sys.modules:
            importlib.reload(sys.modules['daoc_sprint_manager.core.window_manager'])
        
        from daoc_sprint_manager.core.window_manager import WindowManager
        
        # Apply patches to constants
        self.constant_patches = [
            patch('daoc_sprint_manager.core.window_manager.PYGETWINDOW_AVAILABLE', True),
            patch('daoc_sprint_manager.core.window_manager.WIN32_AVAILABLE', True),
            patch('daoc_sprint_manager.core.window_manager.OPENCV_AVAILABLE', True),
        ]
        
        for p in self.constant_patches:
            p.start()
            self.addCleanup(p.stop)
        
        self.mock_logger = MockLogger("TestWindowManager")
        self.window_manager = WindowManager(self.mock_logger)
        
        # Create a mock window for tests with common attributes
        self.mock_win_attrs = {
            'title': 'Test Game Window',
            'left': 100, 'top': 100, 'width': 800, 'height': 600,
            'visible': True, 'isActive': False, '_hWnd': 12345
        }
        
        # Create a mock window that will be returned from pygetwindow
        self.mock_window = MagicMock()
        for attr, value in self.mock_win_attrs.items():
            setattr(self.mock_window, attr, value)

    def setup_pygetwindow_mocks(self):
        # Setup BaseWindow class on pygetwindow
        class MockBaseWindow:
            pass
        
        class MockWin32Window(MockBaseWindow):
            pass
        
        # Set up the module structure
        mock_pygetwindow.BaseWindow = MockBaseWindow
        mock_pygetwindow.windows = MagicMock()
        mock_pygetwindow.windows.Win32Window = MockWin32Window
        
        # Set up functions and returns
        mock_pygetwindow.getWindowsWithTitle = MagicMock(return_value=[])
        mock_pygetwindow.getAllWindows = MagicMock(return_value=[])
    
    def setup_win32_mocks(self):
        # Set up common win32gui functions
        mock_win32gui.IsWindowVisible = MagicMock(return_value=True)
        mock_win32gui.GetWindowTextLength = MagicMock(return_value=15)
        mock_win32gui.GetWindowText = MagicMock(return_value="Test Game Window")
        mock_win32gui.GetWindowRect = MagicMock(return_value=(100, 100, 900, 700))  # left, top, right, bottom
        mock_win32gui.GetWindowDC = MagicMock(return_value=9999)  # DC handle
        mock_win32gui.ReleaseDC = MagicMock()
        mock_win32gui.DeleteObject = MagicMock()
        mock_win32gui.EnumWindows = MagicMock()
        mock_win32gui.error = Exception  # Mock error class
        
        # Set up win32ui MockDC and MockBitmap classes
        class MockDC(MagicMock):
            def CreateCompatibleDC(self):
                compatible_dc = MockDC()
                compatible_dc.BitBlt = MagicMock()
                compatible_dc.SelectObject = MagicMock()
                return compatible_dc
                
        class MockBitmap(MagicMock):
            def CreateCompatibleBitmap(self, dc, width, height):
                pass
                
            def GetInfo(self):
                return {'bmWidth': 800, 'bmHeight': 600}
                
            def GetBitmapBits(self, as_string=False):
                if as_string:
                    return b'\x00\x00\x00\xFF' * (800 * 600)
                return [0, 0, 0, 255] * (800 * 600)
                
            def GetHandle(self):
                return 8888
        
        # Setup win32ui functions
        mock_win32ui.CreateDCFromHandle = MagicMock(return_value=MockDC())
        mock_win32ui.CreateBitmap = MagicMock(return_value=MockBitmap())
        
        # Setup win32con constants
        mock_win32con.SRCCOPY = 0xCC0020  # Example value
    
    def setup_cv2_mocks(self):
        # Setup cv2.cvtColor to return a valid numpy array
        def mock_cvtColor(img, conversion_type):
            if isinstance(img, np.ndarray):
                # If height and width in shape, use them
                if len(img.shape) >= 2:
                    h, w = img.shape[:2]
                    return np.zeros((h, w, 3), dtype=np.uint8)
            # Default shape if input isn't as expected
            return np.zeros((600, 800, 3), dtype=np.uint8)
            
        mock_cv2.cvtColor = MagicMock(side_effect=mock_cvtColor)
        mock_cv2.COLOR_BGRA2BGR = 4  # Example value

    def test_find_window_success_pygetwindow(self):
        # First set up mock instance with proper spec
        mock_win32window_instance = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        for attr, value in self.mock_win_attrs.items():
            setattr(mock_win32window_instance, attr, value)
            
        # Make it return valid window when title matches
        mock_pygetwindow.getWindowsWithTitle.return_value = [mock_win32window_instance]
        
        window = self.window_manager.find_window("Test Game")
        
        self.assertEqual(window, mock_win32window_instance)
        mock_pygetwindow.getWindowsWithTitle.assert_called_once_with("Test Game")

    def test_find_window_success_win32(self):
        # Disable pygetwindow for this test
        with patch('daoc_sprint_manager.core.window_manager.PYGETWINDOW_AVAILABLE', False):
            # Make win32gui return a valid window
            mock_hwnd = 12345
            
            # Configure EnumWindows to call the callback with our hwnd
            def enum_windows_side_effect(callback, results_list):
                callback(mock_hwnd, results_list)
                
            mock_win32gui.EnumWindows.side_effect = enum_windows_side_effect
            
            window = self.window_manager.find_window("Test Game")
            
            self.assertEqual(window, mock_hwnd)
            mock_win32gui.IsWindowVisible.assert_called_with(mock_hwnd)
            mock_win32gui.GetWindowTextLength.assert_called_with(mock_hwnd)
            mock_win32gui.GetWindowText.assert_called_with(mock_hwnd)

    def test_find_window_not_found(self):
        # No windows returned by PyGetWindow
        mock_pygetwindow.getWindowsWithTitle.return_value = []
        
        # No windows found by Win32 either
        def no_match_enum_windows(callback, results_list):
            pass  # No windows found
            
        mock_win32gui.EnumWindows.side_effect = no_match_enum_windows
        
        window = self.window_manager.find_window("NonExistent")
        
        self.assertIsNone(window)

    def test_find_window_empty_title_substring(self):
        window = self.window_manager.find_window("")
        self.assertIsNone(window)
        self.mock_logger.assert_message_logged(logging.ERROR, "Window title substring cannot be empty")

    def test_get_all_window_titles_pygetwindow(self):
        # Create mock windows to return
        mock_win1 = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        mock_win1.title = "Window 1"
        mock_win1.visible = True
        mock_win1._hWnd = 1
        
        mock_win2 = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        mock_win2.title = "Window 2"
        mock_win2.visible = True
        mock_win2._hWnd = 2
        
        mock_win_hidden = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        mock_win_hidden.title = "Hidden Window"
        mock_win_hidden.visible = False
        mock_win_hidden._hWnd = 3
        
        mock_win_no_title = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        mock_win_no_title.title = ""
        mock_win_no_title.visible = True
        mock_win_no_title._hWnd = 4
        
        mock_pygetwindow.getAllWindows.return_value = [mock_win1, mock_win2, mock_win_hidden, mock_win_no_title]
        
        titles_details = self.window_manager.get_all_window_titles()
        
        # The implementation should filter out windows that are not visible or have no title
        self.assertEqual(len(titles_details), 2)
        titles = [td[0] for td in titles_details]
        self.assertIn("Window 1", titles)
        self.assertIn("Window 2", titles)
        self.assertNotIn("Hidden Window", titles)
        self.assertNotIn("", titles)

    def test_get_all_window_titles_win32(self):
        # Test Win32 path by disabling PyGetWindow
        with patch('daoc_sprint_manager.core.window_manager.PYGETWINDOW_AVAILABLE', False):
            # Create mock window data to return through the callback
            mock_windows = {
                1: "Window A",
                2: "Window B",
                3: "",  # No title
            }
            
            # Define a side effect that simulates EnumWindows calling the callback
            def enum_windows_side_effect(callback, results_list):
                for hwnd, title in mock_windows.items():
                    # Mock the return values for each window check
                    mock_win32gui.GetWindowTextLength.return_value = len(title)
                    mock_win32gui.GetWindowText.return_value = title
                    
                    # Call the callback with the current hwnd
                    callback(hwnd, results_list)
                    
            mock_win32gui.EnumWindows.side_effect = enum_windows_side_effect
            
            titles_details = self.window_manager.get_all_window_titles()
            
            # Check results - expecting non-empty title windows
            self.assertEqual(len(titles_details), 2)  # Windows A and B
            titles = [td[0] for td in titles_details]
            self.assertIn("Window A", titles)
            self.assertIn("Window B", titles)
            self.assertNotIn("", titles)

    def test_capture_window_success_pygetwindow_obj(self):
        # Create a mock window with the right spec
        mock_window = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        for attr, value in self.mock_win_attrs.items():
            setattr(mock_window, attr, value)
        
        # GetWindowRect should return valid dimensions
        mock_win32gui.GetWindowRect.return_value = (100, 100, 900, 700)  # left, top, right, bottom
        
        # Expected capture dimensions
        width = 800
        height = 600
        
        # We need to also properly mock the bitmap creation
        mock_bitmap = MagicMock()
        mock_bitmap.GetInfo.return_value = {'bmWidth': width, 'bmHeight': height}
        mock_bitmap.GetBitmapBits.return_value = b'\x00\x00\x00\xFF' * (width * height)
        
        # Create a valid DC hierarchy
        mock_wdc = 1234  # Mock window DC
        mock_win32gui.GetWindowDC.return_value = mock_wdc
        
        mock_dcobj = MagicMock()
        mock_cdc = MagicMock()
        mock_dcobj.CreateCompatibleDC.return_value = mock_cdc
        mock_win32ui.CreateDCFromHandle.return_value = mock_dcobj
        
        mock_win32ui.CreateBitmap.return_value = mock_bitmap
        
        # Mock the numpy.frombuffer call to return a valid image array
        with patch('numpy.frombuffer', return_value=np.zeros((height*width*4), dtype=np.uint8).reshape(height, width, 4)):
            # Make cv2.cvtColor return appropriate sized array
            mock_cv2.cvtColor.return_value = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Capture the window
            img = self.window_manager.capture_window(mock_window)
            
            self.assertIsNotNone(img)
            self.assertEqual(img.shape[0], height)
            self.assertEqual(img.shape[1], width)
            self.assertEqual(img.shape[2], 3)
            
            # Verify the window's HWND was used
            mock_win32gui.GetWindowDC.assert_called_with(mock_window._hWnd)

    def test_capture_window_success_hwnd(self):
        # Test capturing from a raw HWND
        mock_hwnd = 12345
        
        # GetWindowRect should return valid dimensions
        mock_win32gui.GetWindowRect.return_value = (50, 50, 150, 150)  # left, top, right, bottom
        
        # Expected shape after capture
        width, height = 100, 100  # right-left, bottom-top
        
        # We need to also properly mock the bitmap creation
        mock_bitmap = MagicMock()
        mock_bitmap.GetInfo.return_value = {'bmWidth': width, 'bmHeight': height}
        mock_bitmap.GetBitmapBits.return_value = b'\x00\x00\x00\xFF' * (width * height)
        
        # Create a valid DC hierarchy
        mock_wdc = 1234  # Mock window DC
        mock_win32gui.GetWindowDC.return_value = mock_wdc
        
        mock_dcobj = MagicMock()
        mock_cdc = MagicMock()
        mock_dcobj.CreateCompatibleDC.return_value = mock_cdc
        mock_win32ui.CreateDCFromHandle.return_value = mock_dcobj
        
        mock_win32ui.CreateBitmap.return_value = mock_bitmap
        
        # Mock the numpy.frombuffer call to return a valid image array
        with patch('numpy.frombuffer', return_value=np.zeros((height*width*4), dtype=np.uint8).reshape(height, width, 4)):
            # Make cv2.cvtColor return appropriate sized array
            mock_cv2.cvtColor.return_value = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Capture the window
            img = self.window_manager.capture_window(mock_hwnd)
            
            self.assertIsNotNone(img)
            self.assertEqual(img.shape[0], height)
            self.assertEqual(img.shape[1], width)
            self.assertEqual(img.shape[2], 3)
            
            # Verify the HWND was used
            mock_win32gui.GetWindowDC.assert_called_with(mock_hwnd)

    def test_capture_window_zero_dimensions(self):
        # Create a mock window with invalid dimensions
        mock_window = MagicMock(spec=mock_pygetwindow.windows.Win32Window)
        for attr, value in self.mock_win_attrs.items():
            setattr(mock_window, attr, value)
        
        # Set zero width
        mock_window.width = 0
        
        # Make GetWindowRect return zero width as well
        mock_win32gui.GetWindowRect.return_value = (100, 100, 100, 700)  # left=right => width=0
        
        img = self.window_manager.capture_window(mock_window)
        
        self.assertIsNone(img)
        self.mock_logger.assert_message_logged(logging.ERROR, "invalid dimensions")

    def test_capture_roi_valid(self):
        # Mock window capture to return a valid test image
        mock_capture = np.zeros((200, 200, 3), dtype=np.uint8)
        
        with patch.object(self.window_manager, 'capture_window', return_value=mock_capture):
            roi_img = self.window_manager.capture_roi_from_window(self.mock_window, 50, 50, 100, 100)
            
            self.assertIsNotNone(roi_img)
            self.assertEqual(roi_img.shape, (100, 100, 3))
            self.window_manager.capture_window.assert_called_once_with(self.mock_window)

    def test_capture_roi_outside_bounds_clamping(self):
        # Mock window capture to return a test image
        mock_capture = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch.object(self.window_manager, 'capture_window', return_value=mock_capture):
            # ROI partially outside window bounds
            roi_img = self.window_manager.capture_roi_from_window(self.mock_window, 50, 50, 100, 100)
            
            # Expect clamped dimensions (50x50)
            self.assertIsNotNone(roi_img)
            self.assertEqual(roi_img.shape, (50, 50, 3))  # Should be clamped

    def test_capture_roi_fully_outside(self):
        # Mock window capture to return a test image
        mock_capture = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch.object(self.window_manager, 'capture_window', return_value=mock_capture):
            # ROI completely outside the window bounds
            roi_img = self.window_manager.capture_roi_from_window(self.mock_window, 200, 200, 50, 50)
            
            # Should return None as the ROI is completely outside
            self.assertIsNone(roi_img)

    def test_capture_roi_base_capture_fails(self):
        # Mock capture_window to return None (failure case)
        with patch.object(self.window_manager, 'capture_window', return_value=None):
            roi_img = self.window_manager.capture_roi_from_window(self.mock_window, 10, 10, 20, 20)
            
            self.assertIsNone(roi_img)

    def test_capture_roi_invalid_roi_dims(self):
        # Test with invalid ROI dimensions
        roi_img = self.window_manager.capture_roi_from_window(self.mock_window, 10, 10, 0, 20)
        
        self.assertIsNone(roi_img)
        self.mock_logger.assert_message_logged(logging.ERROR, "Invalid ROI dimensions")

    def test_capture_with_win32_getwindowdc_fails(self):
        # Make GetWindowDC fail by returning None
        mock_win32gui.GetWindowDC.return_value = None
        
        img = self.window_manager._capture_with_win32(123, (0, 0, 100, 80))
        
        self.assertIsNone(img)
        self.mock_logger.assert_message_logged(logging.ERROR, "GetWindowDC failed")


if __name__ == '__main__':
    unittest.main() 