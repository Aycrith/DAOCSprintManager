"""
System tray application class for DAOC Sprint Manager.

Handles the system tray icon, menu, threading for the detection loop,
and overall application lifecycle management.
"""

import logging
import os
import pathlib
import shutil 
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Tuple, List

try:
    import pystray
    from PIL import Image, UnidentifiedImageError
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

try:
    import pygetwindow
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

# Import project components
try:
    from ..data_models import AppSettings, Profile
    from ..core.window_manager import WindowManager
    from ..core.icon_detector import IconDetector
    from ..core.input_manager import InputManager
    from ..utils.performance_monitor import PerformanceMonitor
    from ..core.ml_detector import MLDetector, ONNXRUNTIME_AVAILABLE
    from .config_gui import ConfigGUI 
    from .profile_manager_dialog import ProfileManagerDialog 
    from ..config_manager import ConfigManager # Added for use in _open_profile_manager etc.
    from ..core.profile_io_manager import ProfileIOManager # Added
except (ImportError, ValueError):
    current_dir = pathlib.Path(__file__).parent.resolve()
    project_src_dir = current_dir.parent
    if str(project_src_dir) not in sys.path:
         sys.path.insert(0, str(project_src_dir))
    
    from data_models import AppSettings, Profile
    from core.window_manager import WindowManager
    from core.icon_detector import IconDetector
    from core.input_manager import InputManager
    from utils.performance_monitor import PerformanceMonitor
    from core.ml_detector import MLDetector, ONNXRUNTIME_AVAILABLE
    from ui.config_gui import ConfigGUI 
    from ui.profile_manager_dialog import ProfileManagerDialog
    from config_manager import ConfigManager # Added for use in _open_profile_manager etc.
    from core.profile_io_manager import ProfileIOManager # Added

try:
    CONFIG_GUI_AVAILABLE = True
except NameError:
    CONFIG_GUI_AVAILABLE = False

class SprintManagerApp:
    """
    Manages the system tray application, detection loop thread, and state.
    """

    def __init__(self, app_settings: AppSettings, logger: logging.Logger, root_dir: pathlib.Path, config_manager: ConfigManager):
        """
        Initializes the SprintManagerApp.

        Args:
            app_settings: Loaded application settings (global or initially active profile's).
            logger: Logger instance.
            root_dir: The root directory of the project.
            config_manager: The main application's ConfigManager instance.
        """
        self.app_settings = app_settings # This will hold the *currently active* settings
        self.logger = logger
        self.root_dir = root_dir
        self.config_manager = config_manager # Store the main ConfigManager
        
        self.tk_root_for_config: Optional[tk.Tk] = None 

        if not PYSTRAY_AVAILABLE:
            self.logger.critical("pystray or Pillow library not found. System tray UI cannot run. Install using: pip install pystray Pillow")
            sys.exit("FATAL: Missing required libraries (pystray, Pillow) for tray application.")
        
        if not PYGETWINDOW_AVAILABLE:
            self.logger.warning("pygetwindow library not found. Game window focus checking will be disabled. Install using: pip install pygetwindow")

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.status_message: str = "Initializing..."
        self.status_lock = threading.Lock()
        self.pystray_icon: Optional[pystray.Icon] = None
        self.sprint_key_physical_state: bool = False
        self.detection_thread: Optional[threading.Thread] = None
        self.config_gui_instance: Optional[ConfigGUI] = None
        self.profile_manager_dialog_instance: Optional[ProfileManagerDialog] = None 

        self.game_not_found_consecutive_count: int = 0
        self.ml_prediction_failure_consecutive_count: int = 0
        self.was_auto_paused_due_to_game_not_found: bool = False
        
        self.perf_monitor = PerformanceMonitor(self.logger)
        self.window_manager = WindowManager(self.logger)
        self.icon_detector = IconDetector(self.logger, self.app_settings.temporal_consistency_frames)
        self.input_manager = InputManager(self.logger)
        self.ml_detector: Optional[MLDetector] = None

        self.detection_cache: Dict[int, Tuple[float, Tuple[bool, float, Optional[Tuple[int, int, int, int]]]]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_evictions = 0

        # Profile Management
        self.profile_io_manager = ProfileIOManager(profiles_dir=self.root_dir / "profiles", logger=self.logger)
        self.current_profile: Optional[Profile] = None
        self._apply_active_profile_settings() # Load and apply active profile settings at startup
        # _load_resources is now called by _apply_active_profile_settings
        
        self.logger.info("SprintManagerApp initialized.")

    def _apply_active_profile_settings(self):
        """Loads the active profile and applies its AppSettings."""
        global_app_settings = self.config_manager.load_settings() # Load global settings to get active_profile_id
        active_id = global_app_settings.active_profile_id
        
        initial_app_settings_source = "global"

        if active_id:
            all_profiles = self.profile_io_manager.load_profiles()
            active_profile_obj = next((p for p in all_profiles if p.profile_id == active_id), None)

            if active_profile_obj:
                self.current_profile = active_profile_obj
                self.app_settings = active_profile_obj.app_settings # Use profile's AppSettings
                # Crucially, ensure the global active_profile_id is also part of this AppSettings instance
                # so that if this AppSettings is saved by ConfigGUI, active_profile_id is preserved.
                self.app_settings.active_profile_id = active_id 
                self.logger.info(f"Applied settings from active profile: {active_profile_obj.profile_name} (ID: {active_id})")
                initial_app_settings_source = f"profile '{active_profile_obj.profile_name}'"
            else:
                self.logger.warning(f"Active profile ID '{active_id}' set in global settings, but profile not found. Using global settings.")
                self.current_profile = None
                self.app_settings = global_app_settings # Fallback to global if active profile is missing
        else:
            self.logger.info("No active profile set. Using global settings.")
            self.current_profile = None
            self.app_settings = global_app_settings # Use global if no active_profile_id

        self.logger.info(f"Initial AppSettings loaded from: {initial_app_settings_source}")
        
        # Always reload resources when applying profile settings
        self._load_resources(is_reload=True)
        
        # Resources (like detectors) have been reloaded/re-initialized based on the now active self.app_settings

    def _update_status(self, message: str):
        with self.status_lock:
            self.status_message = message
            if self.pystray_icon and hasattr(self.pystray_icon, 'update_menu'):
                 self.pystray_icon.title = f"DAOC Sprint Manager: {self.status_message}"
        self.logger.info(f"Status updated: {message}")


    def _on_clicked_pause_resume(self, icon: Optional[pystray.Icon], item: Optional[pystray.MenuItem]):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self._update_status(f"Running ({self.app_settings.detection_method})") 
            self.logger.info("Application Resumed.")
        else:
            self.pause_event.set()
            self._update_status("Paused")
            self.logger.info("Application Paused.")
        if self.pystray_icon:
             self.pystray_icon.update_menu()

    def _on_clicked_open_config(self, icon: Optional[pystray.Icon], item: Optional[pystray.MenuItem]):
        if self.config_gui_instance is not None and hasattr(self.config_gui_instance, 'dialog') and self.config_gui_instance.dialog.winfo_exists():
            self.logger.debug("Config dialog already open, bringing to front")
            self.config_gui_instance.dialog.lift()
            self.config_gui_instance.dialog.focus_force()
            return
        
        self.logger.info("Opening configuration dialog")
        
        if not CONFIG_GUI_AVAILABLE:
            self.logger.warning("ConfigGUI class not available. Falling back to text editor.")
            config_path = self.root_dir / "config" / "settings.json" # Global settings file
            # ... (existing fallback logic to open with os.startfile etc.)
            return

        try:
            if self.tk_root_for_config is None or not self.tk_root_for_config.winfo_exists():
                self.tk_root_for_config = tk.Tk()
                self.tk_root_for_config.withdraw()
            
            # ConfigGUI always edits the *currently active* AppSettings.
            # If a profile is active, its AppSettings are in self.app_settings.
            # If no profile is active, global AppSettings are in self.app_settings.
            # The ConfigManager passed to ConfigGUI is the main one, for saving global settings (like active_profile_id).
            # However, if a profile is active, saving from ConfigGUI should update the profile's AppSettings
            # and then save all profiles via ProfileIOManager.
            # This makes _handle_settings_applied_from_gui more complex.

            # Decision for now: ConfigGUI opened from tray ALWAYS edits the GLOBAL settings.json.
            # To edit PROFILE settings, user must go through Profile Manager.
            settings_to_edit = self.config_manager.load_settings() # Load fresh global settings

            self.config_gui_instance = ConfigGUI(
                self.tk_root_for_config, 
                self.config_manager, # Pass the main ConfigManager
                settings_to_edit, 
                self.logger,
                on_apply_callback=self._handle_settings_applied_from_gui, # This callback will handle global settings
                destroy_handler=self._on_config_gui_closed
            )
            self.config_gui_instance.show()
        except Exception as e:
            self.logger.exception(f"Error opening configuration dialog: {e}")
            messagebox.showerror("Error", f"Could not open configuration dialog: {e}")

    def _handle_settings_applied_from_gui(self, new_settings: AppSettings):
        """Callback from ConfigGUI when GLOBAL settings are applied or OK'd."""
        self.logger.info("Global settings changes received from ConfigGUI.")
        
        # new_settings here are the potentially modified global settings.
        # We save them via self.config_manager which points to settings.json
        # self.config_manager.save_settings(new_settings) # ConfigGUI already saved them.

        # If no profile is active, these new global settings become the app's current settings.
        if self.current_profile is None:
            self.logger.info("Applying new global settings as no profile is active.")
            self.app_settings = new_settings
            self._load_resources(is_reload=True)
            self._update_status(f"Global Settings Updated ({self.app_settings.detection_method})")
        else:
            # A profile IS active. Global settings were changed.
            # The active profile's settings (in self.app_settings) are NOT changed by this.
            # The active_profile_id in the global settings might have changed.
            self.logger.info(f"Global settings file changed. Active profile '{self.current_profile.profile_name}' remains in use with its own settings.")
            self.logger.info(f"New global active_profile_id is: {new_settings.active_profile_id}")
            # If the active_profile_id in the *global settings file* changed,
            # and it's different from our current_profile.profile_id,
            # the user might expect a switch. However, _select_profile is the explicit way.
            # For now, changing global settings doesn't auto-switch an active profile.
            # The user would need to use the "Set Active" in ProfileManager or re-select from tray.
            self._update_status(f"Global Settings File Updated. Active profile: '{self.current_profile.profile_name}' ({self.app_settings.detection_method})")
            # We might need to refresh the active profile ID in the tray menu if it changed globally
            if self.pystray_icon:
                self.pystray_icon.update_menu()


    def _on_config_gui_closed(self, save_applied: bool):
        self.logger.debug(f"ConfigGUI dialog closed, save_applied={save_applied}")
        self.config_gui_instance = None
        # ... (rest of the Tk root handling logic remains the same) ...

    def _get_profiles(self) -> List[Profile]: # Renamed from _get_mock_profiles
        """Loads profiles from the ProfileIOManager."""
        return self.profile_io_manager.load_profiles()

    def _select_profile(self, profile: Profile):
        """Selects and activates a profile."""
        self.logger.info(f"Profile selected via tray: {profile.profile_name} (ID: {profile.profile_id})")
        
        # Load global settings to update active_profile_id
        global_settings = self.config_manager.load_settings()
        global_settings.active_profile_id = profile.profile_id
        save_ok = self.config_manager.save_settings(global_settings)

        if save_ok:
            self.logger.info(f"Set active profile ID to '{profile.profile_id}' in global settings.")
            
            # Update the last_used_date for the profile and save it
            all_profiles = self.profile_io_manager.load_profiles()
            selected_profile = next((p for p in all_profiles if p.profile_id == profile.profile_id), None)
            if selected_profile:
                # Update the last_used_date
                from datetime import datetime
                selected_profile.last_used_date = datetime.utcnow()
                # Save all profiles with the updated last_used_date
                if self.profile_io_manager.save_profiles(all_profiles):
                    self.logger.info(f"Updated last_used_date for profile '{profile.profile_name}'")
                else:
                    self.logger.error(f"Failed to save updated last_used_date for profile '{profile.profile_name}'")
            
            self._apply_active_profile_settings() # This updates self.app_settings and reloads resources
            
            if self.pystray_icon:
                self.pystray_icon.update_menu() # Refresh tray menu for checkmark
            
            self.logger.info(f"Profile '{profile.profile_name}' activated. Detection method: {self.app_settings.detection_method}")
            self._update_status(f"Profile: {profile.profile_name} ({self.app_settings.detection_method})")
        else:
            self.logger.error("Failed to save active profile ID to global settings.")
            messagebox.showerror("Error", "Could not save active profile selection.", parent=self.tk_root_for_config)


    def _build_profile_sub_menu(self):
        profiles = self._get_profiles()
        if not profiles:
            return pystray.Menu(pystray.MenuItem("No profiles available", None, enabled=False))

        menu_items = []
        active_id = self.app_settings.active_profile_id # Get current active ID

        for p in profiles:
            # Closure issue: p must be captured correctly for each lambda
            # Correct way: use a default argument in lambda
            menu_items.append(
                pystray.MenuItem(
                    p.profile_name,
                    lambda profile_to_select=p: self._select_profile(profile_to_select),
                    checked=lambda item, current_p_id=p.profile_id: (current_p_id == self.app_settings.active_profile_id), # Dynamic check
                    radio=True
                )
            )
        return pystray.Menu(*menu_items)

    def _open_profile_manager(self):
        if self.profile_manager_dialog_instance is not None and self.profile_manager_dialog_instance.winfo_exists():
            self.logger.debug("Profile Manager dialog already open, bringing to front")
            self.profile_manager_dialog_instance.lift()
            self.profile_manager_dialog_instance.focus_force()
            return

        self.logger.info("Opening Profile Manager dialog.")
        if self.tk_root_for_config is None or not self.tk_root_for_config.winfo_exists():
            self.tk_root_for_config = tk.Tk()
            self.tk_root_for_config.withdraw()

        self.profile_manager_dialog_instance = ProfileManagerDialog(
            self.tk_root_for_config,
            self.config_manager, # Pass main ConfigManager for active_profile_id handling
            self.logger,
            self.root_dir, # Pass project_root_dir
            on_close_callback=self._on_profile_manager_closed,
            on_active_profile_changed_callback=self._handle_active_profile_change_from_dialog
        )
        self.profile_manager_dialog_instance.show()

    def _on_profile_manager_closed(self):
        self.logger.debug("Profile Manager dialog closed.")
        self.profile_manager_dialog_instance = None
        if self.pystray_icon: 
            self.pystray_icon.update_menu()
        # ... (rest of the Tk root handling logic remains the same) ...
        
    def _handle_active_profile_change_from_dialog(self, new_active_profile_id: Optional[str]):
        """Called by ProfileManagerDialog when the active profile is set or cleared."""
        self.logger.info(f"Active profile changed via dialog. New active ID: {new_active_profile_id}")
        
        # The ProfileManagerDialog should have already updated the global settings file
        # with the new active_profile_id. We just need to re-apply.
        self._apply_active_profile_settings() # This will load the new active profile and reconfigure
        
        if self.pystray_icon:
            self.pystray_icon.update_menu()
        
        # Update status to reflect the newly active profile
        if self.current_profile:
            self._update_status(f"Profile: {self.current_profile.profile_name} ({self.app_settings.detection_method})")
        else:
            self._update_status(f"Global Settings Active ({self.app_settings.detection_method})")


    def _reinitialize_detector(self): # Renamed for clarity, calls _load_resources
        """Reinitialize the detector and other resources based on current AppSettings."""
        self.logger.info(f"Re-initializing resources. Current detection method: {self.app_settings.detection_method}")
        self._load_resources(is_reload=True)

    def _update_performance_settings(self):
        # This is now largely handled by _load_resources on settings changes.
        # Specific component updates can still happen here if needed.
        self.icon_detector.temporal_consistency_frames = self.app_settings.temporal_consistency_frames
        self.logger.info("Performance settings (temporal consistency) updated.")

    def _check_and_apply_auto_profile_switch(self):
        """
        Checks the current game window title and automatically switches to the appropriate profile.
        Returns True if a switch was made, False otherwise.
        """
        if not self.app_settings.enable_auto_profile_switching:
            return False
        
        # Get the current window title
        current_window = self.window_manager.find_window(self.app_settings.game_window_title)
        if not current_window:
            self.logger.debug("Auto-switch check: Game window not found")
            return False
        
        try:
            # Get the full window title
            if PYGETWINDOW_AVAILABLE and isinstance(current_window, pygetwindow.Win32Window):
                current_title = current_window.title
            elif WIN32_AVAILABLE and isinstance(current_window, int):
                current_title = win32gui.GetWindowText(current_window)
            else:
                self.logger.warning("Auto-switch check: Unsupported window type")
                return False
            
            if not current_title:
                self.logger.debug("Auto-switch check: Empty window title")
                return False
            
            # Get all profiles with window title patterns
            all_profiles = self._get_profiles()
            matching_profiles = []
            
            for profile in all_profiles:
                if (profile.window_title_pattern and 
                    profile.profile_id != self.app_settings.active_profile_id):
                    # Check if the pattern matches the window title
                    pattern = profile.window_title_pattern.lower()
                    if pattern in current_title.lower():
                        matching_profiles.append(profile)
            
            if not matching_profiles:
                return False
                
            # If multiple profiles match, select the one with the most specific pattern
            # (determined by pattern length as a simple heuristic)
            if len(matching_profiles) > 1:
                matching_profiles.sort(
                    key=lambda p: len(p.window_title_pattern or ""), 
                    reverse=True
                )
                self.logger.info(f"Multiple matching profiles found, selecting the most specific one: {matching_profiles[0].profile_name}")
            
            selected_profile = matching_profiles[0]
            
            # Switch to the matching profile
            self.logger.info(f"Auto-switching to profile: {selected_profile.profile_name} based on window title match")
            self._select_profile(selected_profile)
            return True
            
        except Exception as e:
            self.logger.error(f"Error during auto-profile switching: {e}")
            return False
    
    def run_detection_logic(self):
        """
        Main detection and action loop.
        
        Runs in a dedicated thread, handling window finding, ROI capture,
        sprint icon detection, and key press/release actions.
        """
        last_perf_report_time = 0
        last_auto_switch_check_time = 0
        auto_switch_check_interval = 5.0  # Check for auto-switching every 5 seconds
        
        self.logger.info("Detection thread started.")
        self._update_status(f"Running ({self.app_settings.detection_method})")
        
        start_time = time.time()
        
        while not self.stop_event.is_set():
            loop_start_time = time.time()
            
            # Check if paused
            if self.pause_event.is_set():
                time.sleep(0.1)
                continue
                
            # Check for auto-profile switching periodically
            elapsed_since_last_check = time.time() - last_auto_switch_check_time
            if elapsed_since_last_check > auto_switch_check_interval:
                switched = self._check_and_apply_auto_profile_switch()
                if switched:
                    # If we switched profiles, restart the loop to use the new settings
                    last_auto_switch_check_time = time.time()
                    continue
                else:
                    last_auto_switch_check_time = time.time()
            
            # Find the game window
            window = self.window_manager.find_window(self.app_settings.game_window_title)
            
            if not window:
                self.game_not_found_consecutive_count += 1
                if self.game_not_found_consecutive_count > 5 and not self.was_auto_paused_due_to_game_not_found:
                    self.pause_event.set()
                    self.was_auto_paused_due_to_game_not_found = True
                    self._update_status("Paused: Game window not found")
                    self.logger.warning(f"Game window not found after {self.game_not_found_consecutive_count} attempts. Auto-paused.")
                    if self.pystray_icon:
                        self.pystray_icon.update_menu()
                
                time.sleep(self.app_settings.game_not_found_retry_delay_s)
                continue
            
            # Reset counters if we found the window
            self.game_not_found_consecutive_count = 0
            if self.was_auto_paused_due_to_game_not_found:
                self.pause_event.clear()
                self.was_auto_paused_due_to_game_not_found = False
                self._update_status(f"Resumed: Game window found ({self.app_settings.detection_method})")
                self.logger.info("Auto-resumed: Game window found.")
                if self.pystray_icon:
                    self.pystray_icon.update_menu()
            
            # Rest of your existing detection logic continues here
            # ...
            
            # Sleep to maintain target FPS
            elapsed_time = time.time() - loop_start_time
            target_frame_time = 1.0 / self.app_settings.capture_fps
            sleep_time = max(0, target_frame_time - elapsed_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    # Ensure the menu property correctly uses _build_profile_sub_menu
    @property
    def menu(self) -> pystray.Menu:
        """Dynamically generates the tray menu."""
        paused_state = self.pause_event.is_set()
        status_item_text = f"Status: {self.status_message}"
        
        # Build the profile sub-menu items dynamically
        profile_sub_menu_items = self._build_profile_sub_menu()

        return pystray.Menu(
            pystray.MenuItem(status_item_text, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                'Pause' if not paused_state else 'Resume',
                self._on_clicked_pause_resume,
                checked=lambda item: self.pause_event.is_set() 
            ),
            pystray.MenuItem('Open Configuration', self._on_clicked_open_config), # Edits GLOBAL settings
            pystray.Menu.SEPARATOR, 
            pystray.MenuItem('Profiles', profile_sub_menu_items), # Assign the dynamic sub-menu
            pystray.MenuItem('Manage Profiles...', self._open_profile_manager),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', self._on_clicked_exit)
        )

    # run_detection_logic method (ensure it uses self.app_settings for all configurations)
    # ... (no significant changes needed beyond what was done for ML integration, assuming self.app_settings is correctly updated by profile switching)

    # _load_resources method (ensure it's robust as per Phase 3, Step 2 & 3)
    # ... (ensure it uses self.app_settings for all path and config values)

    # start method (ensure it uses self.config_manager for global settings, and current self.app_settings for initial setup)
    # ...
