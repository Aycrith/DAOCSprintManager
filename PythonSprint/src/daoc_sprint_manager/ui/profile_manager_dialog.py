"""
Profile Manager Dialog for the DAOC Sprint Manager.

This module provides a Tkinter-based graphical user interface for managing application profiles.
"""

import logging
import pathlib
import sys # Added for path manipulation in __main__
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Callable, Dict, Any # Added Dict, Any
import datetime # For formatting dates

# Import project modules
try:
    from ..data_models import Profile, AppSettings
    from ..core.profile_io_manager import ProfileIOManager # Added
    from .profile_edit_dialog import ProfileEditDialog    # Added
    from ..config_manager import ConfigManager # For ProfileEditDialog context
except ImportError:
    # For standalone testing or direct execution
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent # PythonSprint/
    sys.path.insert(0, str(project_root / 'src'))
    from daoc_sprint_manager.data_models import Profile, AppSettings
    from daoc_sprint_manager.core.profile_io_manager import ProfileIOManager # Added
    from daoc_sprint_manager.ui.profile_edit_dialog import ProfileEditDialog      # Added
    from daoc_sprint_manager.config_manager import ConfigManager # For ProfileEditDialog context


class ProfileManagerDialog(tk.Toplevel):
    """
    Tkinter-based Profile Manager dialog for the application.

    Provides a user interface for creating, editing, importing, and exporting profiles.
    """

    def __init__(self, master: tk.Tk, 
                 main_config_manager: ConfigManager, # Main app's ConfigManager
                 logger: logging.Logger,
                 project_root_dir: pathlib.Path, # For ProfileIOManager and ProfileEditDialog
                 # Profiles list removed, will be loaded by ProfileIOManager
                 on_close_callback: Optional[Callable] = None,
                 on_active_profile_changed_callback: Optional[Callable[[Optional[str]], None]] = None): # Callback takes Optional[profile_id]
        """
        Initialize the Profile Manager dialog.

        Args:
            master: The parent Tkinter window.
            main_config_manager: The application's main ConfigManager instance (used for AppSettings in ProfileEditDialog and for global active_profile_id).
            logger: Logger instance for logging events.
            project_root_dir: The root directory of the application.
            on_close_callback: Optional callback function called when the dialog is closed.
            on_active_profile_changed_callback: Callback when active profile changes.
        """
        super().__init__(master)
        self.main_config_manager = main_config_manager
        self.logger = logger
        self.project_root_dir = project_root_dir
        self.on_close_callback = on_close_callback
        self.on_active_profile_changed_callback = on_active_profile_changed_callback

        self.profile_io_manager = ProfileIOManager(
            profiles_dir=self.project_root_dir / "profiles", 
            logger=self.logger
        )
        self.profiles: List[Profile] = [] # Will be loaded

        # Set window properties
        self.title("Profile Manager")
        self.transient(master)
        self.grab_set()

        self._setup_ui()
        self._load_profiles_from_file() # Load actual profiles
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.logger.info("ProfileManagerDialog initialized.")


    def _center_window(self):
        """Center the dialog window on the screen."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Set up the UI components."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 10))

        columns = ("ID", "Active", "Profile Name", "Character Name", "Last Used") # Added "Active"
        self.profile_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        self.profile_tree.heading("ID", text="ID")
        self.profile_tree.column("ID", width=0, stretch=tk.NO) # Hidden
        
        self.profile_tree.heading("Active", text="Active", anchor=tk.CENTER)
        self.profile_tree.column("Active", width=50, stretch=tk.NO, anchor=tk.CENTER)

        self.profile_tree.heading("Profile Name", text="Profile Name")
        self.profile_tree.column("Profile Name", width=200, anchor=tk.W)

        self.profile_tree.heading("Character Name", text="Character Name")
        self.profile_tree.column("Character Name", width=150, anchor=tk.W)

        self.profile_tree.heading("Last Used", text="Last Used")
        self.profile_tree.column("Last Used", width=150, anchor=tk.W)

        self.profile_tree["displaycolumns"] = ("Active", "Profile Name", "Character Name", "Last Used")

        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.profile_tree.yview)
        self.profile_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.profile_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)

        crud_buttons_frame = ttk.Frame(buttons_frame)
        crud_buttons_frame.pack(side=tk.LEFT, anchor=tk.W)

        ttk.Button(crud_buttons_frame, text="Create New", command=self._create_new_profile).pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(crud_buttons_frame, text="Edit Selected", command=self._edit_selected_profile).pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(crud_buttons_frame, text="Delete Selected", command=self._delete_selected_profile).pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(crud_buttons_frame, text="Set as Active", command=self._set_active_profile).pack(side=tk.LEFT, padx=2, pady=5)
        
        import_export_frame = ttk.Frame(buttons_frame)
        import_export_frame.pack(side=tk.LEFT, padx=(20,0), anchor=tk.W) # Add some space

        ttk.Button(import_export_frame, text="Import Profile(s)", command=self._import_profiles).pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(import_export_frame, text="Export Selected", command=self._export_selected_profile).pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Button(buttons_frame, text="Close", command=self._on_close).pack(side=tk.RIGHT, padx=5, pady=5)


    def _load_profiles_from_file(self):
        """Load profiles from ProfileIOManager and update the list."""
        self.profiles = self.profile_io_manager.load_profiles()
        self._load_profiles_to_list()

    def _load_profiles_to_list(self):
        """Load profiles into the Treeview."""
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        
        active_profile_id = self.main_config_manager.load_settings().active_profile_id

        for profile in self.profiles:
            last_used_formatted = profile.last_used_date.strftime('%Y-%m-%d %H:%M') if profile.last_used_date else "Never"
            is_active_str = "Yes" if profile.profile_id == active_profile_id else "No"
            
            self.profile_tree.insert(
                "", "end", iid=profile.profile_id,
                values=(
                    profile.profile_id, # Hidden
                    is_active_str,
                    profile.profile_name,
                    profile.game_character_name or "-",
                    last_used_formatted
                )
            )
        self.logger.debug("Profile list in dialog refreshed.")


    def _create_new_profile(self):
        """Handles creating a new profile."""
        self.logger.info("Create New Profile button clicked.")
        existing_names = [p.profile_name for p in self.profiles]
        
        # Pass the main application's ConfigManager instance
        dialog = ProfileEditDialog(self, self.logger, self.main_config_manager, self.project_root_dir, existing_profile_names=existing_names)
        new_profile = dialog.show()

        if new_profile:
            self.profiles.append(new_profile)
            if self.profile_io_manager.save_profiles(self.profiles):
                self.logger.info(f"New profile '{new_profile.profile_name}' saved.")
                self._load_profiles_to_list() # Refresh list
            else:
                messagebox.showerror("Save Error", "Failed to save new profile.", parent=self)


    def _edit_selected_profile(self):
        """Handles editing the selected profile."""
        self.logger.info("Edit Selected Profile button clicked.")
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to edit.", parent=self)
            return
        
        selected_profile_id = selected_items[0]
        profile_to_edit = next((p for p in self.profiles if p.profile_id == selected_profile_id), None)

        if not profile_to_edit:
            messagebox.showerror("Error", "Selected profile not found.", parent=self)
            return

        existing_names = [p.profile_name for p in self.profiles if p.profile_id != selected_profile_id]
        dialog = ProfileEditDialog(self, self.logger, self.main_config_manager, self.project_root_dir, existing_profile=profile_to_edit, existing_profile_names=existing_names)
        edited_profile = dialog.show()

        if edited_profile:
            # Update the profile in the list
            for i, p in enumerate(self.profiles):
                if p.profile_id == edited_profile.profile_id:
                    self.profiles[i] = edited_profile
                    break
            if self.profile_io_manager.save_profiles(self.profiles):
                self.logger.info(f"Profile '{edited_profile.profile_name}' updated and saved.")
                self._load_profiles_to_list()
            else:
                messagebox.showerror("Save Error", "Failed to save updated profile.", parent=self)


    def _delete_selected_profile(self):
        """Handles deleting the selected profile."""
        self.logger.info("Delete Selected Profile button clicked.")
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to delete.", parent=self)
            return

        selected_profile_id = selected_items[0]
        
        active_profile_id = self.main_config_manager.load_settings().active_profile_id
        if selected_profile_id == active_profile_id:
            messagebox.showerror("Cannot Delete", "Cannot delete the currently active profile. Please set another profile as active first.", parent=self)
            return

        profile_to_delete = next((p for p in self.profiles if p.profile_id == selected_profile_id), None)
        if not profile_to_delete: return # Should not happen

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_to_delete.profile_name}'?", parent=self):
            self.profiles = [p for p in self.profiles if p.profile_id != selected_profile_id]
            if self.profile_io_manager.save_profiles(self.profiles):
                self.logger.info(f"Profile '{profile_to_delete.profile_name}' deleted.")
                self._load_profiles_to_list()
            else:
                messagebox.showerror("Save Error", "Failed to save profiles after deletion.", parent=self)

    def _set_active_profile(self):
        """Sets the selected profile as the active one."""
        self.logger.info("Set as Active button clicked.")
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to set as active.", parent=self)
            return

        selected_profile_id = selected_items[0]
        
        # Load current global settings
        current_global_settings = self.main_config_manager.load_settings()
        if current_global_settings.active_profile_id == selected_profile_id:
            messagebox.showinfo("Already Active", "This profile is already active.", parent=self)
            return

        current_global_settings.active_profile_id = selected_profile_id
        
        # Save the updated global settings (which now includes the active_profile_id)
        if self.main_config_manager.save_settings(current_global_settings):
            self.logger.info(f"Profile ID '{selected_profile_id}' set as active in global settings.")
            
            # Update the last_used_date for the selected profile
            selected_profile = next((p for p in self.profiles if p.profile_id == selected_profile_id), None)
            if selected_profile:
                # Update the last_used_date
                from datetime import datetime
                selected_profile.last_used_date = datetime.utcnow()
                # Save all profiles with the updated last_used_date
                if self.profile_io_manager.save_profiles(self.profiles):
                    self.logger.info(f"Updated last_used_date for profile '{selected_profile.profile_name}'")
                else:
                    self.logger.error(f"Failed to save updated last_used_date for profile '{selected_profile.profile_name}'")
            
            self._load_profiles_to_list() # Refresh list to show new active profile
            if self.on_active_profile_changed_callback:
                self.on_active_profile_changed_callback(selected_profile_id)
            messagebox.showinfo("Profile Activated", f"Profile set as active. The application will use its settings on next suitable check/restart.", parent=self) # Clarify when settings apply
        else:
            messagebox.showerror("Error", "Failed to save active profile setting.", parent=self)


    def _import_profiles(self):
        """Imports profiles from a JSON file."""
        self.logger.info("Import Profile(s) button clicked.")
        file_path = filedialog.askopenfilename(
            title="Import Profile(s)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self
        )
        if not file_path:
            self.logger.info("Import cancelled.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_profiles_count = 0
            # Data can be a single profile object or a list of profile objects
            if isinstance(data, dict): # Single profile
                profiles_to_import_data = [data]
            elif isinstance(data, list): # List of profiles
                profiles_to_import_data = data
            else:
                messagebox.showerror("Import Error", "Invalid file format. Expected a JSON object or a list of JSON objects.", parent=self)
                return

            for profile_data in profiles_to_import_data:
                try:
                    # Ensure app_settings within profile_data is also a dict if needed by Pydantic/manual AppSettings init
                    if 'app_settings' in profile_data and not isinstance(profile_data['app_settings'], dict):
                        self.logger.warning("app_settings in imported profile data is not a dict. Skipping this profile.")
                        continue
                    
                    imported_profile = Profile(**profile_data)
                    
                    # Handle conflicts
                    name_exists = any(p.profile_name == imported_profile.profile_name for p in self.profiles)
                    id_exists = any(p.profile_id == imported_profile.profile_id for p in self.profiles)

                    if id_exists: # If ID exists, always generate a new one
                        old_id = imported_profile.profile_id
                        imported_profile.profile_id = str(uuid.uuid4())
                        self.logger.info(f"Imported profile ID '{old_id}' conflicted, new ID '{imported_profile.profile_id}' generated.")
                    
                    if name_exists:
                        original_name = imported_profile.profile_name
                        count = 1
                        while any(p.profile_name == imported_profile.profile_name for p in self.profiles):
                            imported_profile.profile_name = f"{original_name} (Imported {count})"
                            count += 1
                        self.logger.info(f"Imported profile name '{original_name}' conflicted, renamed to '{imported_profile.profile_name}'.")

                    self.profiles.append(imported_profile)
                    imported_profiles_count += 1
                except Exception as e: # Catch Pydantic validation errors etc.
                    self.logger.error(f"Error importing a profile entry: {e}", exc_info=True)
                    messagebox.showwarning("Import Warning", f"Skipped importing a profile due to error: {e}", parent=self)
            
            if imported_profiles_count > 0:
                if self.profile_io_manager.save_profiles(self.profiles):
                    self.logger.info(f"Successfully imported {imported_profiles_count} profile(s).")
                    self._load_profiles_to_list()
                    messagebox.showinfo("Import Successful", f"{imported_profiles_count} profile(s) imported.", parent=self)
                else:
                    messagebox.showerror("Save Error", "Failed to save profiles after import.", parent=self)
            elif not profiles_to_import_data: # File was empty or not a list/dict
                 messagebox.showwarning("Import Warning", "No profiles found in the selected file.", parent=self)
            else: # No profiles imported due to errors
                 messagebox.showwarning("Import Warning", "No profiles were imported. Check logs for details.", parent=self)


        except Exception as e:
            self.logger.error(f"Failed to import profiles from {file_path}: {e}", exc_info=True)
            messagebox.showerror("Import Error", f"Could not import profiles: {e}", parent=self)


    def _export_selected_profile(self):
        """Exports the selected profile to a JSON file."""
        self.logger.info("Export Selected Profile button clicked.")
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to export.", parent=self)
            return

        selected_profile_id = selected_items[0]
        profile_to_export = next((p for p in self.profiles if p.profile_id == selected_profile_id), None)

        if not profile_to_export: return

        safe_filename = "".join(c if c.isalnum() else "_" for c in profile_to_export.profile_name)
        suggested_filename = f"{safe_filename}.json"

        file_path = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            initialfile=suggested_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self
        )
        if not file_path:
            self.logger.info("Export cancelled.")
            return

        try:
            # Use the same serialization logic as in ProfileIOManager.save_profiles for a single profile
            profile_dict_to_save: Dict[str, Any]
            if PYDANTIC_AVAILABLE:
                profile_dict_to_save = profile_to_export.dict()
            else:
                profile_dict_to_save = vars(profile_to_export).copy()
                if isinstance(profile_dict_to_save.get('app_settings'), AppSettings):
                     profile_dict_to_save['app_settings'] = vars(profile_dict_to_save['app_settings']).copy()
                for key, value in profile_dict_to_save.items():
                    if isinstance(value, datetime):
                        profile_dict_to_save[key] = value.isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if PYDANTIC_AVAILABLE:
                    f.write(profile_to_export.json(indent=4)) # Pydantic's json() handles datetime
                else:
                    json.dump(profile_dict_to_save, f, indent=4)


            self.logger.info(f"Profile '{profile_to_export.profile_name}' exported to {file_path}.")
            messagebox.showinfo("Export Successful", f"Profile exported to {file_path}", parent=self)
        except Exception as e:
            self.logger.error(f"Failed to export profile to {file_path}: {e}", exc_info=True)
            messagebox.showerror("Export Error", f"Could not export profile: {e}", parent=self)


    def _on_close(self):
        """Handle dialog close."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def show(self):
        """Show the dialog and wait for it to be closed."""
        # self._load_profiles_to_list() # Already called after _load_profiles_from_file
        self.deiconify()
        self.wait_window()


# Self-test block
if __name__ == "__main__":
    # Create a simple logger
    _test_logger = logging.getLogger("ProfileManagerDialogTest")
    _test_logger.setLevel(logging.DEBUG)
    if not _test_logger.handlers:
        _handler = logging.StreamHandler(sys.stdout) # Changed to stdout for tests
        _handler.setLevel(logging.DEBUG)
        _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        _handler.setFormatter(_formatter)
        _test_logger.addHandler(_handler)

    # Determine project root for test (assuming this file is in src/daoc_sprint_manager/ui)
    _project_root_test = pathlib.Path(__file__).resolve().parent.parent.parent

    # Mock ConfigManager for testing interaction
    class MockMainConfigManager:
        def __init__(self, settings_file, template_file, logger_instance):
            self.logger = logger_instance
            self.settings = AppSettings(active_profile_id=None) # Start with no active profile
            self.logger.info("MockMainConfigManager (for ProfileManagerDialog test) initialized.")

        def load_settings(self) -> AppSettings:
            self.logger.debug(f"MockMainConfigManager: load_settings() returning: {self.settings.dict(exclude_none=True) if PYDANTIC_AVAILABLE else vars(self.settings)}")
            return self.settings # Return current state

        def save_settings(self, settings_to_save: AppSettings) -> bool:
            self.logger.info(f"MockMainConfigManager: save_settings() called with: {settings_to_save.dict(exclude_none=True) if PYDANTIC_AVAILABLE else vars(settings_to_save)}")
            self.settings = settings_to_save # Update internal state
            return True

    _dummy_settings_file = _project_root_test / "config" / "dummy_main_app_settings.json"
    _dummy_template_file = _project_root_test / "config" / "dummy_main_app_settings.json.template"
    (_dummy_settings_file.parent).mkdir(parents=True, exist_ok=True)


    mock_main_cm = MockMainConfigManager(_dummy_settings_file, _dummy_template_file, _test_logger)

    # Create and run the dialog
    root = tk.Tk()
    root.withdraw()

    # Test with initially empty profiles.json
    test_profiles_dir = _project_root_test / "temp_test_profiles"
    test_profiles_dir.mkdir(exist_ok=True)
    temp_profiles_file = test_profiles_dir / "profiles.json"
    if temp_profiles_file.exists():
        temp_profiles_file.unlink()


    def active_profile_changed(profile_id: Optional[str]):
        _test_logger.info(f"SELF-TEST: Active profile changed callback! New active ID: {profile_id}")

    dialog = ProfileManagerDialog(
        root,
        mock_main_cm, # Pass the main app's config manager
        _test_logger,
        _project_root_test, # Pass project root
        on_active_profile_changed_callback=active_profile_changed
    )

    dialog.show()

    # Clean up
    if temp_profiles_file.exists():
        temp_profiles_file.unlink()
    if test_profiles_dir.exists():
        test_profiles_dir.rmdir()
        
    _test_logger.info("ProfileManagerDialog self-test finished.")
    root.destroy()
