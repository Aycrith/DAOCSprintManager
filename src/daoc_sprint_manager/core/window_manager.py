"""
Window management module for finding and capturing from game windows.

Provides functionality to locate game windows by title and capture
regions of interest for icon detection.
"""

import logging
import time
import sys  # Add import for sys
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
# Update to use the proper type for pygetwindow
WindowType = Union[object, int] if PYGETWINDOW_AVAILABLE else Union[int, object]


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

        self.can_find_windows = PYGETWINDOW_AVAILABLE or WIN32_AVAILABLE
        self.can_capture = WIN32_AVAILABLE and OPENCV_AVAILABLE

        if not self.can_find_windows:
            self.logger.critical(
                "Cannot find windows: no window management library available. "
                "Consider installing pygetwindow and/or pywin32."
            )

        if not self.can_capture:
            self.logger.critical(
                "Cannot capture from windows: required libraries missing. "
                "Consider installing pywin32 and opencv-python."
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

        self.logger.debug(f"Searching for window with title substring: '{window_title_substring}'")
        try:
            # Try PyGetWindow first if available and on Windows
            if PYGETWINDOW_AVAILABLE and sys.platform == "win32":
                try:
                    # pygetwindow.getWindowsWithTitle can return a list of BaseWindow objects
                    windows: List[pygetwindow.BaseWindow] = pygetwindow.getWindowsWithTitle(window_title_substring)
                    if windows:
                        # Ensure we are working with Win32Window if possible for consistency
                        # The type hint for WindowType reflects this preference.
                        found_window = windows[0]
                        if isinstance(found_window, pygetwindow.windows.Win32Window): # Check specific type
                            window_info = f"'{found_window.title}' at ({found_window.left}, {found_window.top})"
                            self.logger.debug(f"Found window using PyGetWindow: {window_info}")
                            return found_window
                        else:
                            self.logger.warning(f"PyGetWindow found a window of type {type(found_window)}, but Win32Window expected for full functionality. HWND might not be available.")
                            # If _hWnd is needed later, this window might not work with win32 capture.
                            # For now, return it if it's the only option from pygetwindow.
                            return found_window

                    else:
                        self.logger.debug(f"No windows found with title containing '{window_title_substring}' using PyGetWindow.")
                except Exception as e:
                    self.logger.warning(f"Error using PyGetWindow.getWindowsWithTitle: {e}. Trying Win32 if available.")

            # Fall back to Win32 if PyGetWindow failed, isn't available, or not on Windows
            if WIN32_AVAILABLE:
                windows_found_hwnds: List[int] = []

                def enum_callback(hwnd: int, results_list: List[int]):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowTextLength(hwnd) > 0:
                        window_text = win32gui.GetWindowText(hwnd)
                        if window_title_substring.lower() in window_text.lower():
                            self.logger.debug(f"Win32 found matching window: '{window_text}' (hwnd: {hwnd})")
                            results_list.append(hwnd)
                    return True

                try:
                    win32gui.EnumWindows(enum_callback, windows_found_hwnds)
                    if windows_found_hwnds:
                        hwnd = windows_found_hwnds[0]
                        self.logger.debug(f"Selected window with hwnd: {hwnd} using Win32.")
                        return hwnd
                    else:
                        self.logger.debug(f"No windows found with title containing '{window_title_substring}' using Win32 EnumWindows.")
                except Exception as e:
                    self.logger.error(f"Error using Win32 EnumWindows to find windows: {e}")

            self.logger.debug(f"Ultimately, no window found with title containing '{window_title_substring}'.")
            return None

        except Exception as e:
            self.logger.exception(f"Unexpected error finding window with title substring '{window_title_substring}': {e}")
            return None

    def get_all_window_titles(self) -> List[Tuple[str, WindowType]]:
        """
        Retrieves a list of (title, window_object) for all currently visible windows with non-empty titles.
        Prefers pygetwindow if available, otherwise falls back to win32gui.

        Returns:
            List of tuples, where each tuple is (window_title: str, window_object: WindowType).
        """
        window_details: List[Tuple[str, WindowType]] = []
        if not self.can_find_windows:
            self.logger.error("Cannot get all window titles: required window management libraries not available.")
            return window_details

        if PYGETWINDOW_AVAILABLE and sys.platform == "win32":
            try:
                all_windows: List[pygetwindow.BaseWindow] = pygetwindow.getAllWindows()
                for win in all_windows:
                    if win.title and win.visible and isinstance(win, pygetwindow.windows.Win32Window):
                        window_details.append((win.title, win))
                self.logger.debug(f"Retrieved {len(window_details)} visible window details using pygetwindow.")
                return window_details
            except Exception as e:
                self.logger.warning(f"Error using pygetwindow.getAllWindows: {e}. Trying win32gui fallback if available.")
                window_details.clear() # Clear partial results from pygetwindow if it failed mid-way

        if WIN32_AVAILABLE:
            self.logger.debug("Using win32gui to get all window titles as fallback or primary.")
            def enum_callback(hwnd: int, results_list: List[Tuple[str, WindowType]]):
                if win32gui.IsWindowVisible(hwnd):
                    window_text_len = win32gui.GetWindowTextLength(hwnd)
                    if window_text_len > 0:
                        window_text = win32gui.GetWindowText(hwnd)
                        results_list.append((window_text, hwnd)) # Store HWND as the window object
                return True

            try:
                win32gui.EnumWindows(enum_callback, window_details)
                self.logger.debug(f"Retrieved {len(window_details)} visible window details using win32gui.")
                return window_details
            except Exception as e:
                self.logger.error(f"Error enumerating windows with win32gui: {e}")
        
        return window_details


    def capture_window(self, window: WindowType) -> Optional[np.ndarray]:
        if not self.can_capture:
            self.logger.error("Cannot capture: required libraries (pywin32, opencv-python) not available.")
            return None
        if window is None:
            self.logger.error("Cannot capture from None window.")
            return None

        hwnd: Optional[int] = None
        window_rect_tuple: Optional[Tuple[int, int, int, int]] = None

        try:
            if PYGETWINDOW_AVAILABLE and isinstance(window, pygetwindow.windows.Win32Window):
                if hasattr(window, '_hWnd'): # Ensure it's a Win32Window with an HWND
                    hwnd = window._hWnd
                    if window.width > 0 and window.height > 0:
                        # Using GetWindowRect for pygetwindow objects to be consistent and get screen coordinates
                        # as pygetwindow's left/top/width/height are usually client area relative or less reliable.
                        # For capture, we need screen coordinates for BitBlt source if it's not a child window capture.
                        # However, _capture_with_win32 expects window's own width/height for bitmap creation.
                        # Let's try to get reliable dimensions.
                        try:
                            gdi_rect = win32gui.GetWindowRect(hwnd)
                            win_w, win_h = gdi_rect[2] - gdi_rect[0], gdi_rect[3] - gdi_rect[1]
                            if win_w > 0 and win_h > 0:
                                window_rect_tuple = (gdi_rect[0], gdi_rect[1], win_w, win_h)
                            else: # Fallback to pygetwindow's dimensions if GetWindowRect fails or gives zero size
                                self.logger.warning(f"GetWindowRect for HWND {hwnd} (from pygetwindow object '{window.title}') gave zero size. Falling back to pygetwindow dimensions.")
                                if window.width > 0 and window.height > 0:
                                     window_rect_tuple = (window.left, window.top, window.width, window.height) # These might be client coords
                                else:
                                    self.logger.error(f"PyGetWindow object '{window.title}' also has invalid dimensions W={window.width}, H={window.height}.")
                                    return None
                        except win32gui.error as e_gwr:
                            self.logger.error(f"win32gui.GetWindowRect failed for HWND {hwnd} (from pygetwindow object '{window.title}'): {e_gwr}. Cannot capture.")
                            return None
                    else:
                        self.logger.error(f"PyGetWindow object '{window.title}' has invalid dimensions W={window.width}, H={window.height}. Cannot capture.")
                        return None
                else:
                    self.logger.error(f"Window object (type {type(window)}) from pygetwindow does not have _hWnd. Cannot use win32 capture.")
                    return None
            elif WIN32_AVAILABLE and isinstance(window, int): # It's an HWND
                hwnd = window
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width, height = right - left, bottom - top
                    if width <= 0 or height <= 0:
                        self.logger.error(f"Invalid window dimensions from GetWindowRect for HWND {hwnd}: W={width}, H={height}")
                        return None
                    window_rect_tuple = (left, top, width, height)
                except win32gui.error as e:
                    self.logger.error(f"Error getting window rect for HWND {hwnd}: {e}")
                    return None
            else:
                self.logger.error(f"Unsupported window type for capture: {type(window)}. Expected pygetwindow.Win32Window or int (HWND).")
                return None

            if hwnd is not None and window_rect_tuple is not None:
                return self._capture_with_win32(hwnd, window_rect_tuple)
            else:
                self.logger.error("Could not resolve HWND or valid window dimensions for capture.")
                return None

        except Exception as e:
            self.logger.exception(f"Unexpected error during window capture setup for window '{str(window)}': {e}")
            return None

    def _capture_with_win32(self, hwnd: int, window_rect_abs: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        # window_rect_abs are screen coordinates: (left, top, width, height)
        # For BitBlt from GetWindowDC, the source coordinates are relative to the window itself (0,0).
        # The bitmap needs to be the size of the window (width, height from window_rect_abs).

        _abs_left, _abs_top, width, height = window_rect_abs

        if width <= 0 or height <= 0:
            self.logger.error(f"Invalid window dimensions for GDI capture: W={width}, H={height}")
            return None
        
        wDC, dcObj, cDC, dataBitMap = None, None, None, None # Initialize for finally block
        try:
            wDC = win32gui.GetWindowDC(hwnd)
            if not wDC:
                self.logger.error(f"GetWindowDC failed for HWND {hwnd}.")
                return None
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
            cDC.SelectObject(dataBitMap)

            # BitBlt from the window's DC (source) to our compatible DC (destination)
            # Source (0,0) means top-left of the window (including title bar etc.)
            cDC.BitBlt((0,0), (width,height), dcObj, (0,0), win32con.SRCCOPY)
            
            # Get bitmap data
            bmpinfo = dataBitMap.GetInfo()
            bmpstr = dataBitMap.GetBitmapBits(True) # Get data as BGRA
            img = np.frombuffer(bmpstr, dtype='uint8').reshape(bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            self.logger.debug(f"Captured HWND {hwnd} ({width}x{height}) with GDI.")
            return img_bgr
        except Exception as e:
            self.logger.error(f"Exception during GDI capture for HWND {hwnd}: {e}", exc_info=True)
            return None
        finally:
            if dataBitMap: win32gui.DeleteObject(dataBitMap.GetHandle())
            if dcObj: dcObj.DeleteDC()
            if cDC: cDC.DeleteDC()
            if wDC: win32gui.ReleaseDC(hwnd, wDC)

    def capture_roi_from_window(self, window: WindowType, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        if width <= 0 or height <= 0:
            self.logger.error(f"Invalid ROI dimensions for capture: {width}x{height}")
            return None

        try:
            window_capture = self.capture_window(window)
            if window_capture is None:
                self.logger.error("Failed to capture base window for ROI extraction.")
                return None

            window_height_cap, window_width_cap = window_capture.shape[:2]

            # x, y are relative to the window's client area for user convenience.
            # capture_window captures the whole window (including non-client parts for win32).
            # We assume x,y are offsets from the top-left of the *captured image*.
            
            final_x, final_y, final_w, final_h = x, y, width, height

            if x < 0 or y < 0 or (x + width) > window_width_cap or (y + height) > window_height_cap:
                self.logger.warning(
                    f"Requested ROI ({x},{y}, {width}x{height}) is partially/fully outside captured window "
                    f"({window_width_cap}x{window_height_cap}). Clamping ROI."
                )
                final_x = max(0, x)
                final_y = max(0, y)
                final_w = min(width, window_width_cap - final_x)
                final_h = min(height, window_height_cap - final_y)

                if final_w <= 0 or final_h <= 0:
                    self.logger.error(f"Clamped ROI results in zero/negative size ({final_w}x{final_h}). Cannot capture ROI.")
                    return None
                self.logger.debug(f"ROI clamped to: x={final_x}, y={final_y}, w={final_w}, h={final_h}")
            
            roi_to_extract = window_capture[final_y : final_y + final_h, final_x : final_x + final_w]
            self.logger.debug(f"Extracted ROI with final dimensions: {final_w}x{final_h} from {final_x},{final_y}")
            
            return roi_to_extract.copy()

        except Exception as e:
            self.logger.exception(f"Error capturing ROI from window: {e}")
            return None


if __name__ == "__main__":
    import sys
    _test_logger_wm = logging.getLogger("WindowManagerTest")
    _test_logger_wm.setLevel(logging.DEBUG)
    if not _test_logger_wm.handlers:
        _ch = logging.StreamHandler(sys.stdout)
        _ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'))
        _test_logger_wm.addHandler(_ch)

    wm = WindowManager(_test_logger_wm)

    print("\n--- Testing WindowManager ---")
    print(f"\nLibs: PyGetWindow={PYGETWINDOW_AVAILABLE}, Win32={WIN32_AVAILABLE}, OpenCV={OPENCV_AVAILABLE}")
    print(f"Can find: {wm.can_find_windows}, Can capture: {wm.can_capture}")

    if not wm.can_find_windows: sys.exit("Window finding unavailable.")

    print("\nTest 0: Get all window titles...")
    all_win_details = wm.get_all_window_titles()
    if all_win_details:
        print(f"Found {len(all_win_details)} windows. First 5:")
        for i, (title, win_obj) in enumerate(all_win_details[:5]):
            print(f"  {i+1}. '{title}' (Type: {type(win_obj)})")
    else:
        print(" -> No visible windows with titles found.")

    title_substr = input("\nEnter part of a VISIBLE window title to test find_window: ")
    target_win = wm.find_window(title_substr)
    if target_win:
         _test_logger_wm.info(f"find_window found: {target_win} (type: {type(target_win)})")
         if wm.can_capture:
             print("\nTest 2: Capturing found window...")
             img_cap = wm.capture_window(target_win)
             if img_cap is not None:
                 _test_logger_wm.info(f"Window capture successful, shape: {img_cap.shape}")
                 # cv2.imwrite("test_main_capture.png", img_cap)
                 print("\nTest 3: Capturing ROI (50,50,100,100) from captured window...")
                 roi_img = wm.capture_roi_from_window(target_win, 50, 50, 100, 100)
                 if roi_img is not None:
                     _test_logger_wm.info(f"ROI capture successful, shape: {roi_img.shape}")
                     # cv2.imwrite("test_roi_capture.png", roi_img)
                 else: _test_logger_wm.error("ROI capture failed.")
             else: _test_logger_wm.error("Window capture failed.")
         else: print("Capture tests skipped (libs missing).")
    else:
        _test_logger_wm.error(f"Window with substring '{title_substr}' not found.")

    print("\n--- WindowManager Test Complete ---")
