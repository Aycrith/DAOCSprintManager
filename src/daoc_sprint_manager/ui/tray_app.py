"""
Window management module for finding and capturing from game windows.

Provides functionality to locate game windows by title and capture
regions of interest for icon detection.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

try:
    import pygetwindow
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

try:
    import win32gui # type: ignore
    import win32ui # type: ignore
    import win32con # type: ignore
    # from ctypes import windll # Not strictly needed for current implementation
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Define a Window type hint for whatever window representation we use
WindowType = Union[pygetwindow.Win32Window, int, object] if PYGETWINDOW_AVAILABLE else Union[int, object]


class WindowManager:
    """
    Manages finding and capturing from game windows.

    Uses available window management libraries to locate windows by title
    and capture screenshots or regions of interest.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize the WindowManager.

        Args:
            logger: Logger instance for recording operations and errors.
        """
        self.logger = logger

        # Log available capture methods
        self.can_find_windows = PYGETWINDOW_AVAILABLE or WIN32_AVAILABLE
        self.can_capture = WIN32_AVAILABLE and OPENCV_AVAILABLE

        if not self.can_find_windows:
            self.logger.critical(
                "Cannot find windows: no window management library available. "
                "Install either pygetwindow or pywin32."
            )

        if not self.can_capture:
            self.logger.critical(
                "Cannot capture from windows: required libraries missing. "
                "Install pywin32 and opencv-python."
            )

        self.logger.debug(f"WindowManager initialized with libraries: "
                          f"PyGetWindow={PYGETWINDOW_AVAILABLE}, "
                          f"Win32={WIN32_AVAILABLE}, "
                          f"OpenCV={OPENCV_AVAILABLE}")

    def find_window(self, window_title_substring: str) -> Optional[WindowType]:
        """
        Find a window by a substring of its title.

        The matching is partial and case-insensitive. Returns the first matching window.

        Args:
            window_title_substring: Part of the window title to search for.

        Returns:
            A window object (pygetwindow.Win32Window or HWND int) if found, None otherwise.
        """
        if not window_title_substring:
            self.logger.error("Window title substring cannot be empty for find_window.")
            return None

        if not self.can_find_windows:
            self.logger.error("Cannot find windows: required libraries not available.")
            return None

        try:
            # Try PyGetWindow first if available
            if PYGETWINDOW_AVAILABLE:
                try:
                    windows = pygetwindow.getWindowsWithTitle(window_title_substring)
                    if windows:
                        found_window = windows[0]  # Take the first matching window
                        window_info = f"'{found_window.title}' at ({found_window.left}, {found_window.top})"
                        self.logger.debug(f"Found window using PyGetWindow: {window_info}")
                        return found_window
                    else:
                        self.logger.debug(f"No windows found with title containing '{window_title_substring}' using PyGetWindow.")
                except Exception as e:
                    self.logger.warning(f"Error using PyGetWindow.getWindowsWithTitle: {e}, trying Win32 if available.")

            # Fall back to Win32 if PyGetWindow failed or isn't available
            if WIN32_AVAILABLE:
                windows_found_hwnds: List[int] = []

                def enum_callback(hwnd: int, results_list: List[int]):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if window_title_substring.lower() in window_text.lower():
                            self.logger.debug(f"Found window using Win32: '{window_text}' (hwnd: {hwnd})")
                            results_list.append(hwnd)
                    return True # Continue enumeration

                try:
                    win32gui.EnumWindows(enum_callback, windows_found_hwnds)
                    if windows_found_hwnds:
                        hwnd = windows_found_hwnds[0]  # Take the first matching window
                        self.logger.debug(f"Selected window with hwnd: {hwnd} using Win32.")
                        return hwnd
                    else:
                        self.logger.debug(f"No windows found with title containing '{window_title_substring}' using Win32.")
                except Exception as e:
                    self.logger.error(f"Error using Win32 to find windows: {e}")

            self.logger.debug(f"No window found with title containing '{window_title_substring}'.")
            return None

        except Exception as e:
            self.logger.exception(f"Unexpected error finding window with title substring '{window_title_substring}': {e}")
            return None

    def get_all_window_titles(self) -> List[str]:
        """
        Retrieves a list of titles for all currently visible windows.
        Prefers pygetwindow if available, otherwise falls back to win32gui.
        """
        titles: List[str] = []
        if not self.can_find_windows:
            self.logger.error("Cannot get all window titles: required window management libraries not available.")
            return titles

        if PYGETWINDOW_AVAILABLE:
            try:
                # Filter out windows with empty titles
                titles = [win.title for win in pygetwindow.getAllWindows() if win.title and win.visible]
                self.logger.debug(f"Retrieved {len(titles)} visible window titles using pygetwindow.")
                return titles
            except Exception as e:
                self.logger.warning(f"Error using pygetwindow.getAllWindows: {e}. Trying win32gui fallback if available.")
                # Fall through to win32gui if pygetwindow fails

        if WIN32_AVAILABLE:
            self.logger.debug("Using win32gui to get all window titles as fallback or primary.")
            enum_titles: List[str] = [] # Use a different list for win32 specific results before assigning to titles
            def enum_callback(hwnd: int, results_list: List[str]):
                if win32gui.IsWindowVisible(hwnd): # Ensure window is visible
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text: # Only add if title is not empty
                        results_list.append(window_text)
                return True # Continue enumeration

            try:
                win32gui.EnumWindows(enum_callback, enum_titles)
                self.logger.debug(f"Retrieved {len(enum_titles)} visible window titles using win32gui.")
                return enum_titles # Return the titles collected by win32
            except Exception as e:
                self.logger.error(f"Error enumerating windows with win32gui: {e}")
        
        # If pygetwindow was available but failed, and win32 wasn't, titles will be empty here.
        # If pygetwindow wasn't available and win32 failed, titles will be empty.
        return titles


    def capture_window(self, window: WindowType) -> Optional[np.ndarray]:
        """
        Capture a screenshot of the entire window.

        Args:
            window: The window object to capture from (pygetwindow window or win32gui hwnd).

        Returns:
            NumPy array containing the screenshot image in BGR format, or None if capture fails.
        """
        if not self.can_capture:
            self.logger.error("Cannot capture: required libraries (pywin32, opencv-python) not available.")
            return None

        if window is None:
            self.logger.error("Cannot capture from None window.")
            return None

        try:
            hwnd: Optional[int] = None
            window_rect_tuple: Optional[Tuple[int, int, int, int]] = None

            if PYGETWINDOW_AVAILABLE and isinstance(window, pygetwindow.Win32Window):
                # Ensure it's a Win32Window instance from pygetwindow, which has _hWnd
                # Some pygetwindow BaseWindow types might not have _hWnd (e.g. on Linux)
                if hasattr(window, '_hWnd'):
                    hwnd = window._hWnd
                    # Ensure window dimensions are valid
                    if window.width > 0 and window.height > 0 :
                        window_rect_tuple = (window.left, window.top, window.width, window.height)
                    else:
                        self.logger.warning(f"PyGetWindow window '{window.title}' has invalid dimensions: W={window.width}, H={window.height}. Attempting GetWindowRect.")
                        # Fallback to GetWindowRect if pygetwindow dimensions are odd
                        if WIN32_AVAILABLE and hwnd:
                             try:
                                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                                if (right - left) > 0 and (bottom - top) > 0:
                                    window_rect_tuple = (left, top, right - left, bottom - top)
                                else:
                                    self.logger.error(f"GetWindowRect also returned invalid dimensions for HWND {hwnd}.")
                                    return None
                             except win32gui.error as e:
                                self.logger.error(f"Error getting window rect via win32gui for HWND {hwnd} from pygetwindow object: {e}")
                                return None
                        else:
                            self.logger.error(f"Cannot get valid dimensions for pygetwindow object '{window.title}'.")
                            return None

                else: # Not a Win32Window from pygetwindow or doesn't have _hWnd
                    self.logger.warning(f"Window object of type {type(window)} from pygetwindow does not have _hWnd. Capture might fail or be inaccurate.")
                    # This path is problematic if we rely on HWND for win32 capture.
                    # Consider if a different capture method is needed for non-Win32Window types from pygetwindow.
                    # For now, if no HWND, we can't use _capture_with_win32.
                    return None # Or attempt a different capture method if one exists

            elif WIN32_AVAILABLE and isinstance(window, int): # It's an HWND
                hwnd = window
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    if (right - left) <= 0 or (bottom - top) <= 0:
                        self.logger.error(f"Invalid window dimensions from GetWindowRect for HWND {hwnd}: W={right-left}, H={bottom-top}")
                        return None
                    window_rect_tuple = (left, top, right - left, bottom - top)
                except win32gui.error as e:
                    self.logger.error(f"Error getting window rect for HWND {hwnd}: {e}")
                    return None
            else:
                self.logger.error(f"Unsupported window type for capture: {type(window)}. Expected pygetwindow.Win32Window or int (HWND).")
                return None

            if hwnd is not None and window_rect_tuple is not None:
                 # Capture using Win32 API (requires HWND)
                if WIN32_AVAILABLE and OPENCV_AVAILABLE:
                    return self._capture_with_win32(hwnd, window_rect_tuple)
                else:
                    self.logger.error("No win32 & OpenCV capture method available, though HWND was resolved.")
                    return None
            else:
                self.logger.error("Could not resolve HWND or window dimensions for capture.")
                return None

        except Exception as e:
            self.logger.exception(f"Unexpected error during window capture setup: {e}")
            return None

    def _capture_with_win32(self, hwnd: int, window_rect: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Capture a window screenshot using the Win32 API.

        Args:
            hwnd: Window handle.
            window_rect: Tuple of (left, top, width, height) of the window.

        Returns:
            NumPy array containing the screenshot image in BGR format, or None if capture fails.
        """
        _left, _top, width, height = window_rect # Window rect is absolute screen coords for BitBlt source

        if width <= 0 or height <= 0:
            self.logger.error(f"Invalid window dimensions for capture: {width}x{height}")
            return None

        # To capture a window that might be partially off-screen or behind other windows,
        # it's often better to use PrintWindow if the window supports WM_PRINT or WM_PRINTCLIENT.
        # However, BitBlt from GetWindowDC can work for visible portions.
        # The current BitBlt copies from (0,0) of the window's DC, which is correct.

        wDC = None
        dcObj = None
        cDC = None
        dataBitMap = None
        try:
            # Create device contexts and bitmap
            wDC = win32gui.GetWindowDC(hwnd)
            if not wDC:
                self.logger.error(f"Failed to get WindowDC for HWND {hwnd}.")
                return None
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, width, height) # Create bitmap of window's size
            cDC.SelectObject(dataBitMap)

            # Perform the BitBlt operation.
            # For BitBlt from a WindowDC, the source (0,0) is the top-left of the window's client area + non-client area.
            # The destination (0,0) is the top-left of our compatible bitmap.
            cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)

            # Convert the bitmap to a numpy array
            # signedIntsArray = dataBitMap.GetBitmapBits(True) # Get data as BGRA
            bmpinfo = dataBitMap.GetInfo()
            bmpstr = dataBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8').reshape(bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

            # img.shape = (height, width, 4)  # Should be BGRA from GetBitmapBits(True)

            # Convert from BGRA to BGR (standard OpenCV format)
            # Note: If the window has no alpha, the A channel might be opaque (255) or garbage.
            # If issues arise, check if COLOR_BGRA2BGR is more appropriate.
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            self.logger.debug(f"Captured window HWND {hwnd} with dimensions: {width}x{height}")
            return img_bgr

        except Exception as e:
            self.logger.exception(f"Error during Win32 capture for HWND {hwnd}: {e}")
            return None
        finally:
            # Clean up GDI objects
            if dataBitMap:
                win32gui.DeleteObject(dataBitMap.GetHandle())
            if dcObj:
                dcObj.DeleteDC()
            if cDC:
                cDC.DeleteDC()
            if wDC:
                win32gui.ReleaseDC(hwnd, wDC)


    def capture_roi_from_window(self, window: WindowType, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        Capture a region of interest from a window.

        Args:
            window: The window object to capture from.
            x: X-coordinate of the top-left corner of the ROI (relative to window's client area).
            y: Y-coordinate of the top-left corner of the ROI (relative to window's client area).
            width: Width of the ROI.
            height: Height of the ROI.

        Returns:
            NumPy array containing the ROI image in BGR format, or None if capture fails.
        """
        if width <= 0 or height <= 0:
            self.logger.error(f"Invalid ROI dimensions for capture: {width}x{height}")
            return None

        try:
            window_capture = self.capture_window(window)
            if window_capture is None:
                self.logger.error("Failed to capture base window for ROI extraction.")
                return None

            window_height_cap, window_width_cap = window_capture.shape[:2]

            # Ensure ROI coordinates are within the captured window image
            # (x, y) are relative to the window's top-left.
            # capture_window captures the whole window, so ROI is a slice of it.
            if x < 0 or y < 0 or (x + width) > window_width_cap or (y + height) > window_height_cap:
                self.logger.warning(
                    f"ROI ({x},{y}, {width}x{height}) is partially or fully outside the "
                    f"captured window dimensions ({window_width_cap}x{window_height_cap}). Clamping ROI."
                )
                # Clamp ROI to be within the captured image
                clamped_x = max(0, x)
                clamped_y = max(0, y)
                clamped_width = min(width, window_width_cap - clamped_x)
                clamped_height = min(height, window_height_cap - clamped_y)

                if clamped_width <= 0 or clamped_height <= 0:
                    self.logger.error(f"Clamped ROI results in zero or negative size ({clamped_width}x{clamped_height}). Cannot capture ROI.")
                    return None
                
                roi_to_extract = window_capture[clamped_y : clamped_y + clamped_height, clamped_x : clamped_x + clamped_width]
                self.logger.debug(f"Captured ROI (clamped) with actual dimensions: {clamped_width}x{clamped_height} from {clamped_x},{clamped_y}")

            else: # ROI is fully within bounds
                roi_to_extract = window_capture[y : y + height, x : x + width]
                self.logger.debug(f"Captured ROI with dimensions: {width}x{height} from {x},{y}")
            
            return roi_to_extract.copy() # Return a copy to avoid issues with slices

        except Exception as e:
            self.logger.exception(f"Error capturing ROI from window: {e}")
            return None


if __name__ == "__main__":
    """Test the WindowManager functionality."""
    import sys
    # Set up a test logger
    _test_logger = logging.getLogger("WindowManagerTest")
    _test_logger.setLevel(logging.DEBUG)
    if not _test_logger.handlers:
        _handler = logging.StreamHandler(sys.stdout)
        _handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'))
        _test_logger.addHandler(_handler)

    window_manager = WindowManager(_test_logger)

    print("\n--- Testing WindowManager ---")
    print(f"\nLibraries Status: PyGetWindow={PYGETWINDOW_AVAILABLE}, Win32={WIN32_AVAILABLE}, OpenCV={OPENCV_AVAILABLE}")
    print(f"Can find windows: {window_manager.can_find_windows}")
    print(f"Can capture: {window_manager.can_capture}")

    if not window_manager.can_find_windows:
        print("Cannot run tests: window management libraries missing.")
        sys.exit(1)

    # Test get_all_window_titles
    print("\nTest 0: Getting all window titles...")
    all_titles = window_manager.get_all_window_titles()
    if all_titles:
        print(f"Found {len(all_titles)} window titles. First few:")
        for i, title in enumerate(all_titles[:5]):
            print(f"  {i+1}. {title}")
    else:
        print(" -> No window titles found or error occurred.")


    # Test finding a window
    print("\nTest 1: Finding a window by title substring")
    window_title_substr = input("Enter part of a VISIBLE window title to search for (e.g., 'Notepad', 'Calculator', your game name): ")

    target_window = window_manager.find_window(window_title_substr)
    if target_window:
        if PYGETWINDOW_AVAILABLE and isinstance(target_window, pygetwindow.Win32Window):
            _test_logger.info(f"Found window (PyGetWindow): '{target_window.title}' at ({target_window.left}, {target_window.top}) size {target_window.width}x{target_window.height}")
        elif WIN32_AVAILABLE and isinstance(target_window, int): # HWND
            try:
                win_text = win32gui.GetWindowText(target_window)
                rect = win32gui.GetWindowRect(target_window)
                _test_logger.info(f"Found window (Win32 HWND): '{win_text}' at ({rect[0]}, {rect[1]}) size {rect[2]-rect[0]}x{rect[3]-rect[1]}")
            except Exception as e_detail:
                _test_logger.error(f"Found HWND {target_window} but error getting details: {e_detail}")
        else:
             _test_logger.info(f"Found window of type: {type(target_window)}")
    else:
        _test_logger.error(f"No window found with title substring '{window_title_substr}'. Cannot proceed with capture tests.")
        sys.exit(1)

    if not window_manager.can_capture:
        print("Cannot run capture tests: capture libraries missing.")
        sys.exit(1)

    # Test capturing the entire window
    print("\nTest 2: Capturing the entire found window...")
    window_image = window_manager.capture_window(target_window)
    if window_image is not None:
        _test_logger.info(f"Captured window image with shape: {window_image.shape}")
        # Optional: Save or display image
        # cv2.imwrite("test_window_capture.png", window_image)
        # _test_logger.info("Saved test_window_capture.png")
    else:
        _test_logger.error("Failed to capture window. Cannot proceed with ROI test.")
        sys.exit(1)

    # Test capturing a region of interest
    print("\nTest 3: Capturing a Region of Interest (ROI) from the window...")
    # Define a sample ROI, e.g., top-left 100x100 pixels
    roi_x, roi_y, roi_w, roi_h = 50, 50, 100, 100 
    _test_logger.info(f"Attempting to capture ROI: x={roi_x}, y={roi_y}, w={roi_w}, h={roi_h}")
    
    roi_image = window_manager.capture_roi_from_window(target_window, roi_x, roi_y, roi_w, roi_h)
    if roi_image is not None:
        _test_logger.info(f"Captured ROI image with shape: {roi_image.shape}")
        # Optional: Save or display ROI image
        # cv2.imwrite("test_roi_capture.png", roi_image)
        # _test_logger.info("Saved test_roi_capture.png")
    else:
        _test_logger.error("Failed to capture ROI.")

    print("\n--- WindowManager Tests Completed ---")

def _check_and_apply_auto_profile_switch(self):
    """
    Checks all visible window titles and automatically switches to the appropriate profile.
    Returns True if a switch was made, False otherwise.
    """
    if not self.app_settings.enable_auto_profile_switching:
        return False
    
    try:
        # Get ALL window titles and their corresponding window objects
        all_window_details = self.window_manager.get_all_window_titles()
        if not all_window_details:
            self.logger.debug("Auto-switch check: No visible windows found")
            return False
        
        # Get all profiles with window title patterns
        all_profiles = self._get_profiles()
        matching_profiles = []
        
        # Check each profile against each window title
        for profile in all_profiles:
            if (profile.window_title_pattern and 
                profile.profile_id != self.app_settings.active_profile_id):
                pattern = profile.window_title_pattern.lower()
                
                # Check this pattern against all window titles
                for window_title, window_obj in all_window_details:
                    if pattern in window_title.lower():
                        self.logger.debug(f"Found matching window '{window_title}' for profile '{profile.profile_name}'")
                        matching_profiles.append((profile, len(pattern)))
                        break  # Found a match for this profile, move to next profile
        
        if not matching_profiles:
            return False
            
        # If multiple profiles match, select the one with the most specific pattern
        # (determined by pattern length as a simple heuristic)
        if len(matching_profiles) > 1:
            matching_profiles.sort(key=lambda p: p[1], reverse=True)
            self.logger.info(f"Multiple matching profiles found, selecting the most specific one: {matching_profiles[0][0].profile_name}")
        
        selected_profile = matching_profiles[0][0]
        
        # Switch to the matching profile
        self.logger.info(f"Auto-switching to profile: {selected_profile.profile_name} based on window title match")
        self._select_profile(selected_profile)
        return True
        
    except Exception as e:
        self.logger.error(f"Error during auto-profile switching: {e}")
        return False