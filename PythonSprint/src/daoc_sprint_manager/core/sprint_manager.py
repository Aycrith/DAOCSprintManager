"""
DAOC Sprint Manager - Core Manager
==============================

This module contains the core sprint detection and management logic.
"""

import logging
import threading
import time
from typing import Optional

import cv2
import numpy as np

# Keep win32 imports as they are used for actual capture
try:
    import win32gui
    import win32ui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logging.getLogger("SprintManagerSetup").warning("win32 libraries not found. Window capture will not work in normal mode.")

from .app_settings import AppSettings

logger = logging.getLogger(__name__)

class SprintManager:
    """Manages sprint detection and window capture."""

    def __init__(self, settings: AppSettings):
        """Initialize the SprintManager.
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.running = False
        self.detection_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        self.hwnd: Optional[int] = None  # Window handle
        
        # Initialize window handle based on mode
        self._initialize_window_handle()
        
        self.last_frame_time = 0.0
        self.frame_interval = 1.0 / self.settings.capture_fps if self.settings.capture_fps > 0 else 0.1
        
        logger.info(f"SprintManager initialized. Target FPS: {self.settings.capture_fps:.2f}")
        if self.settings.test_mode:
            logger.info(f"Running in TEST MODE. Target window title for FindWindow: '{self.settings.test_window_title}'")
            if not self.hwnd:
                logger.warning("Test mode: No external mock window found by title. Capture will return dummy frames if FindWindow fails.")
        else:
            logger.info(f"Running in NORMAL MODE. Target window title: '{self.settings.game_window_title}'")
            if not WIN32_AVAILABLE:
                logger.critical("Win32 libraries are not available. SprintManager cannot function in normal mode.")
    
    def _initialize_window_handle(self):
        """Initialize the window handle based on current mode."""
        window_title_to_find = (self.settings.test_window_title 
                               if self.settings.test_mode 
                               else self.settings.game_window_title)
        
        if not WIN32_AVAILABLE and not self.settings.test_mode:
            logger.error("Win32 API not available, cannot find window for normal mode.")
            self.hwnd = None
            return

        if WIN32_AVAILABLE:  # Only try FindWindow if win32 is available
            try:
                self.hwnd = win32gui.FindWindow(None, window_title_to_find)
                if self.hwnd:
                    logger.info(f"Window '{window_title_to_find}' found with HWND: {self.hwnd}")
                else:
                    logger.warning(f"Window '{window_title_to_find}' not found by FindWindow.")
            except Exception as e:
                logger.error(f"Error calling FindWindow for '{window_title_to_find}': {e}")
                self.hwnd = None
        elif self.settings.test_mode:  # WIN32_AVAILABLE is False but in test mode
            logger.info("Test mode: WIN32_AVAILABLE is False. Actual window capture is not possible. Will rely on dummy frames if FindWindow fails conceptually.")
            # self.hwnd will remain None, _capture_window will handle this in test mode
        else:  # Not test mode and no win32
            self.hwnd = None

    def start(self):
        """Start the sprint detection process."""
        if self.running:
            logger.warning("Sprint detection already running.")
            return
            
        if not self.settings.test_mode and not self.hwnd:
            logger.error("Normal mode: No valid window handle. Cannot start detection.")
            return
        if not self.settings.test_mode and not WIN32_AVAILABLE:
            logger.error("Normal mode: Win32 libraries not available. Cannot start detection.")
            return

        self.running = True
        self.stop_event.clear()
        self.detection_thread = threading.Thread(target=self._detection_loop, name="SprintDetectionLoop")
        self.detection_thread.daemon = True
        self.detection_thread.start()
        logger.info("Sprint detection started.")
    
    def stop(self):
        """Stop the sprint detection process."""
        if not self.running:
            return
            
        logger.info("Stopping sprint detection...")
        self.running = False
        self.stop_event.set()
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)
            if self.detection_thread.is_alive():
                logger.warning("Detection thread did not join in time.")
        self.detection_thread = None
        logger.info("Sprint detection stopped.")
    
    def _detection_loop(self):
        """Main detection loop."""
        logger.info("Detection loop started.")
        loop_count = 0
        self.last_frame_time = time.perf_counter()  # Initialize for first frame calculation

        while self.running and not self.stop_event.is_set():
            loop_start_time = time.perf_counter()
            
            frame = None
            if self.settings.test_mode:
                if self.hwnd:  # If an external mock window was found
                    if WIN32_AVAILABLE:
                        frame = self._capture_window_win32()
                    else:  # Should not happen if hwnd is set
                        logger.warning("Test mode: HWND found but WIN32_AVAILABLE is false. This is inconsistent.")
                        frame = self._create_dummy_frame()
                else:  # No external mock window, just create dummy frames
                    frame = self._create_dummy_frame()
                if loop_count % 100 == 0:  # Log less frequently
                     logger.debug(f"Test mode: Frame acquired (shape: {frame.shape if frame is not None else 'None'})")
            elif self.hwnd and WIN32_AVAILABLE:  # Normal mode
                frame = self._capture_window_win32()
            else:  # Normal mode, but no HWND or win32 libs
                if loop_count % 10 == 0:
                    logger.warning(f"Target window ('{self.settings.game_window_title}') not found or win32 libs missing. Skipping capture.")
                self.stop_event.wait(1.0)  # Wait before retrying to find window or exiting
                loop_count += 1
                continue

            if frame is not None:
                self._process_frame(frame)
            else:
                if loop_count % 10 == 0 and not self.settings.test_mode:
                     logger.warning(f"Failed to capture frame from window HWND: {self.hwnd}")
            
            # Frame rate control
            self.frame_interval = 1.0 / self.settings.capture_fps if self.settings.capture_fps > 0 else 0.1
            processing_time = time.perf_counter() - loop_start_time
            sleep_duration = max(0, self.frame_interval - processing_time)
            
            if sleep_duration > 0:
                self.stop_event.wait(sleep_duration)
            self.last_frame_time = time.perf_counter()  # Update for next iteration
            loop_count += 1

        logger.info("Detection loop finished.")

    def _create_dummy_frame(self) -> np.ndarray:
        """Creates a dummy numpy array frame for test mode when no window is captured."""
        # Use ROI dimensions from settings if available, otherwise default
        w = self.settings.roi_width if hasattr(self.settings, 'roi_width') and self.settings.roi_width > 0 else 100
        h = self.settings.roi_height if hasattr(self.settings, 'roi_height') and self.settings.roi_height > 0 else 100
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        # Add some pattern to make it identifiable
        cv2.circle(frame, (w // 2, h // 2), min(w, h) // 4, (0, 255, 0), -1)
        return frame

    def _capture_window_win32(self) -> Optional[np.ndarray]:
        """Capture the current window frame using Win32 API.
        
        Returns:
            Optional[np.ndarray]: Captured frame or None if capture fails
        """
        if not self.hwnd or not WIN32_AVAILABLE:
            return None
            
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                logger.warning(f"Window HWND {self.hwnd} has invalid dimensions: {width}x{height}")
                return None

            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)
            
            img = np.frombuffer(bmp_str, dtype='uint8').reshape((bmp_info['bmHeight'], bmp_info['bmWidth'], 4))
            
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwnd_dc)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing window via Win32: {e}", exc_info=True)
            return None
    
    def _process_frame(self, frame: np.ndarray):
        """Process a captured frame for sprint detection.
        
        Args:
            frame: The captured frame to process
        """
        # Placeholder for detection logic
        pass  # For performance testing, this can be minimal.
    
    def toggle(self):
        """Toggle sprint detection state."""
        if self.running:
            self.stop()
        else:
            self.start()
        return self.running 