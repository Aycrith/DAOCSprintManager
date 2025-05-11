"""
ProfileEditDialog for creating and editing user profiles.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, List, Callable # Added Callable
import uuid # For new profile IDs
from datetime import datetime # For creation/last_used dates

try:
    # Assuming data_models.py and config_gui.py are in the expected package structure
    from ..data_models import Profile, AppSettings
    from ..config_manager import ConfigManager # For ConfigGUI
    from .config_gui import ConfigGUI
except ImportError:
    # Fallback for standalone testing
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent # PythonSprint/
    sys.path.insert(0, str(project_root / "src"))
    from daoc_sprint_manager.data_models import Profile, AppSettings
    from daoc_sprint_manager.config_manager import ConfigManager # For ConfigGUI
    from daoc_sprint_manager.ui.config_gui import ConfigGUI


class ProfileEditDialog(tk.Toplevel):
    """
    A dialog for creating a new profile or editing an existing one.
    """

    def __init__(self, 
                 master: tk.Widget, 
                 logger: logging.Logger, 
                 config_manager_for_appsettings: ConfigManager, # Main app's ConfigManager
                 project_root_dir: pathlib.Path, # Needed by ConfigGUI for relative paths
                 existing_profile: Optional[Profile] = None, 
                 existing_profile_names: Optional[List[str]] = None):
        """
        Initializes the ProfileEditDialog.

        Args:
            master: The parent window.
            logger: The logger instance.
            config_manager_for_appsettings: The main application's ConfigManager instance,
                                            used by ConfigGUI when editing AppSettings.
            project_root_dir: The root directory of the application, for resolving paths.
            existing_profile: The Profile object to edit, or None if creating a new one.
            existing_profile_names: A list of names of already existing profiles,
                                     used for uniqueness validation (excluding the current
                                     profile's name if editing).
        """
        super().__init__(master)
        self.logger = logger
        self.config_manager_for_appsettings = config_manager_for_appsettings
        self.project_root_dir = project_root_dir
        self.existing_profile = existing_profile
        self.existing_profile_names = existing_profile_names or []
        
        self.profile_data: Optional[Profile] = None # This will hold the result

        if self.existing_profile:
            self.title("Edit Profile")
            # Start with a copy of the existing profile's app_settings
            self.current_app_settings_for_profile = AppSettings(**self.existing_profile.app_settings.dict())
        else:
            self.title("Create New Profile")
            self.current_app_settings_for_profile = AppSettings() # Start with default AppSettings

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._setup_ui()
        self._center_window()
        
        self.logger.debug(f"ProfileEditDialog initialized. Editing profile: {existing_profile.profile_name if existing_profile else 'New Profile'}")

    def _center_window(self):
        """Centers the dialog window on the screen or master window."""
        self.update_idletasks()
        master_win = self.master
        master_x = master_win.winfo_x()
        master_y = master_win.winfo_y()
        master_width = master_win.winfo_width()
        master_height = master_win.winfo_height()
        dialog_width = self.winfo_reqwidth()
        dialog_height = self.winfo_reqheight()
        x_coordinate = master_x + (master_width // 2) - (dialog_width // 2)
        y_coordinate = master_y + (master_height // 2) - (dialog_height // 2)
        x_coordinate = max(0, min(x_coordinate, self.winfo_screenwidth() - dialog_width))
        y_coordinate = max(0, min(y_coordinate, self.winfo_screenheight() - dialog_height))
        self.geometry(f"+{x_coordinate}+{y_coordinate}")

    def _setup_ui(self):
        """Sets up the UI elements for the dialog."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Profile Name
        pn_frame = ttk.Frame(main_frame)
        pn_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pn_frame, text="Profile Name:", width=20).pack(side=tk.LEFT)
        self.profile_name_var = tk.StringVar()
        if self.existing_profile:
            self.profile_name_var.set(self.existing_profile.profile_name)
        profile_name_entry = ttk.Entry(pn_frame, textvariable=self.profile_name_var, width=40)
        profile_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Game Character Name
        gcn_frame = ttk.Frame(main_frame)
        gcn_frame.pack(fill=tk.X, pady=5)
        ttk.Label(gcn_frame, text="Game Character Name:", width=20).pack(side=tk.LEFT)
        self.char_name_var = tk.StringVar()
        if self.existing_profile and self.existing_profile.game_character_name:
            self.char_name_var.set(self.existing_profile.game_character_name)
        char_name_entry = ttk.Entry(gcn_frame, textvariable=self.char_name_var, width=40)
        char_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Window Title Pattern
        wtp_frame = ttk.Frame(main_frame)
        wtp_frame.pack(fill=tk.X, pady=5)
        ttk.Label(wtp_frame, text="Window Title Pattern:", width=20).pack(side=tk.LEFT)
        self.window_pattern_var = tk.StringVar()
        if self.existing_profile and self.existing_profile.window_title_pattern:
            self.window_pattern_var.set(self.existing_profile.window_title_pattern)
        window_pattern_entry = ttk.Entry(wtp_frame, textvariable=self.window_pattern_var, width=40)
        window_pattern_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Add a tooltip or hint label
        pattern_hint = ttk.Label(main_frame, text="(Pattern to match against game window titles for auto-switching)", 
                               font=("", 8, "italic"), foreground="gray")
        pattern_hint.pack(fill=tk.X, padx=(20, 0), anchor=tk.W)

        # Edit Application Settings Button
        app_settings_button = ttk.Button(main_frame, text="Edit Application Settings...", command=self._edit_app_settings)
        app_settings_button.pack(pady=10)

        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))

        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT)

    def _app_settings_applied_callback(self, new_app_settings: AppSettings):
        """Callback from ConfigGUI when its settings are applied."""
        self.logger.debug("Application settings updated from ConfigGUI.")
        self.current_app_settings_for_profile = new_app_settings
        # Potentially mark as unsaved changes here if needed for the ProfileEditDialog
        messagebox.showinfo("Settings Updated", "Application settings for this profile have been updated in memory. Click 'Save' in the Profile Editor to persist all changes.", parent=self)


    def _edit_app_settings(self):
        """Launches the ConfigGUI to edit the AppSettings for this profile."""
        self.logger.debug("Launching ConfigGUI to edit AppSettings for the current profile.")
        
        # The ConfigManager passed is the main app's one, which knows about global settings file.
        # ConfigGUI is designed to load from and save to that file.
        # For profile editing, we want ConfigGUI to edit an AppSettings object in memory.
        # ConfigGUI's on_apply_callback can be used to get the modified AppSettings.
        
        # Create a deep copy of the current_app_settings_for_profile for ConfigGUI to modify
        # This ensures that cancelling ConfigGUI doesn't affect our current_app_settings_for_profile
        # until "Apply" or "OK" is hit in ConfigGUI.
        settings_to_edit_copy = AppSettings(**self.current_app_settings_for_profile.dict())

        # The ConfigManager is passed for ConfigGUI's internal structure,
        # but its save_settings won't be called by ConfigGUI if we use callbacks right.
        # Or, ConfigGUI needs modification to accept an AppSettings object to directly manipulate
        # and a callback for when its "OK" or "Apply" is hit.
        
        # For simplicity, assuming ConfigGUI's _apply_settings and _ok_settings
        # will call its self.on_apply_callback.
        config_gui_instance = ConfigGUI(
            master=self,  # ProfileEditDialog is the master for ConfigGUI
            config_manager=self.config_manager_for_appsettings, # Main app's config manager
            current_settings=settings_to_edit_copy, # Pass a copy
            logger=self.logger,
            on_apply_callback=self._app_settings_applied_callback,
            # ConfigGUI also needs a destroy_handler if we want to know if it was saved or cancelled
            # destroy_handler=lambda saved: self.logger.debug(f"ConfigGUI closed, saved={saved}")
        )
        config_gui_instance.show() # This blocks until ConfigGUI is closed
        self.logger.debug("Returned from ConfigGUI.show()")
        # self.current_app_settings_for_profile should have been updated by the callback if user applied/OK'd in ConfigGUI


    def _on_save(self):
        """Validates input and prepares the Profile object."""
        profile_name_str = self.profile_name_var.get().strip()
        char_name_str = self.char_name_var.get().strip() or None # None if empty
        window_pattern_str = self.window_pattern_var.get().strip() or None # None if empty

        # Validate Profile Name
        if not profile_name_str:
            messagebox.showerror("Validation Error", "Profile Name cannot be empty.", parent=self)
            return

        # Check for uniqueness (excluding self if editing)
        temp_existing_names = self.existing_profile_names[:]
        if self.existing_profile and self.existing_profile.profile_name in temp_existing_names:
            temp_existing_names.remove(self.existing_profile.profile_name)
        
        if profile_name_str in temp_existing_names:
            messagebox.showerror("Validation Error", f"A profile named '{profile_name_str}' already exists.", parent=self)
            return

        if self.existing_profile: # Editing existing profile
            self.profile_data = Profile(
                profile_id=self.existing_profile.profile_id,
                profile_name=profile_name_str,
                creation_date=self.existing_profile.creation_date, # Preserve original creation date
                last_used_date=datetime.utcnow(), # Update last used date
                version=self.existing_profile.version, # Preserve version or update if structure changes
                game_character_name=char_name_str,
                window_title_pattern=window_pattern_str,
                app_settings=self.current_app_settings_for_profile # Use the (potentially) modified AppSettings
            )
            self.logger.info(f"Profile '{profile_name_str}' updated.")
        else: # Creating new profile
            self.profile_data = Profile(
                profile_id=str(uuid.uuid4()), # Generate new ID
                profile_name=profile_name_str,
                # creation_date and last_used_date will use default_factory
                game_character_name=char_name_str,
                window_title_pattern=window_pattern_str,
                app_settings=self.current_app_settings_for_profile # Use the (potentially) modified AppSettings
            )
            self.logger.info(f"New profile '{profile_name_str}' created.")
        
        self.destroy()

    def _on_cancel(self):
        """Handles dialog cancellation."""
        self.logger.debug("ProfileEditDialog cancelled.")
        self.profile_data = None
        self.destroy()

    def show(self) -> Optional[Profile]:
        """
        Shows the dialog and waits for it to be closed.

        Returns:
            The created/edited Profile object if saved, otherwise None.
        """
        self.wait_window()
        return self.profile_data

if __name__ == "__main__":
    # This self-test block allows independent testing of ProfileEditDialog
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(console_handler)
    
    test_logger = logging.getLogger("ProfileEditDialogTest")

    # Mock ConfigManager for AppSettings editing within ProfileEditDialog
    # This mock needs to simulate the ConfigManager that ConfigGUI expects
    class MockMainConfigManager:
        def __init__(self, settings_file_path, template_file_path, logger):
            self.logger = logger
            self.logger.info("MockMainConfigManager for ProfileEditDialog test initialized.")
        
        def load_settings(self) -> AppSettings: # ConfigGUI calls this
            self.logger.info("MockMainConfigManager: load_settings() called by ConfigGUI, returning default AppSettings.")
            return AppSettings() 
            
        def save_settings(self, settings_to_save: AppSettings) -> bool: # ConfigGUI calls this
            self.logger.info(f"MockMainConfigManager: save_settings() called by ConfigGUI with: {settings_to_save}")
            return True

    # Project root needed for ConfigGUI if it loads resources like icons
    # Assuming this script is in src/daoc_sprint_manager/ui/
    _project_root = pathlib.Path(__file__).resolve().parent.parent.parent 
    
    # Dummy paths for MockMainConfigManager
    dummy_settings_file = _project_root / "config" / "dummy_main_settings.json"
    dummy_template_file = _project_root / "config" / "dummy_main_settings.json.template"
    (dummy_settings_file.parent).mkdir(parents=True, exist_ok=True) # Ensure dir exists

    mock_main_cm = MockMainConfigManager(dummy_settings_file, dummy_template_file, test_logger)

    root = tk.Tk()
    root.withdraw() # Hide root window

    def test_create_new():
        test_logger.info("Testing Profile Creation:")
        dialog = ProfileEditDialog(root, test_logger, mock_main_cm, _project_root, existing_profile_names=["Existing Profile 1", "Another Profile"])
        new_profile = dialog.show()
        if new_profile:
            test_logger.info(f"New profile created: {new_profile.profile_name}, ID: {new_profile.profile_id}")
            test_logger.info(f"  AppSettings for new profile: {new_profile.app_settings.dict()}")
        else:
            test_logger.info("Profile creation cancelled.")

    def test_edit_existing():
        test_logger.info("\nTesting Profile Editing:")
        existing_app_settings = AppSettings(sprint_key="q", roi_x=50)
        profile_to_edit = Profile(
            profile_name="Old Profile Name", 
            game_character_name="OldChar", 
            app_settings=existing_app_settings
        )
        dialog = ProfileEditDialog(root, test_logger, mock_main_cm, _project_root, existing_profile=profile_to_edit, existing_profile_names=["Other Profile"])
        edited_profile = dialog.show()
        if edited_profile:
            test_logger.info(f"Profile edited: {edited_profile.profile_name}, ID: {edited_profile.profile_id}")
            test_logger.info(f"  Original AppSettings sprint_key: {existing_app_settings.sprint_key}")
            test_logger.info(f"  Edited AppSettings sprint_key: {edited_profile.app_settings.sprint_key}")
            assert edited_profile.profile_id == profile_to_edit.profile_id # ID should persist
        else:
            test_logger.info("Profile editing cancelled.")

    # Run tests sequentially
    test_create_new()
    root.update() # Process events
    
    test_edit_existing()
    root.update()

    root.destroy()
    test_logger.info("ProfileEditDialog self-test finished.")
