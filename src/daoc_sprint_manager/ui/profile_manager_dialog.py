"""
Profile Manager Dialog for the DAOC Sprint Manager.

This module provides a Tkinter-based graphical user interface for managing application profiles.
"""

import logging
import pathlib
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Callable, Dict, Any
import datetime

# Import project modules
try:
    from ..data_models import Profile, AppSettings
except ImportError:
    # For standalone testing or direct execution
    import sys
    from pathlib import Path
    # Assumes profile_manager_dialog.py is in src/daoc_sprint_manager/ui
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / 'src'))
    from daoc_sprint_manager.data_models import Profile, AppSettings


class ProfileManagerDialog(tk.Toplevel):
    """
    Tkinter-based Profile Manager dialog for the application.
    
    Provides a user interface for creating, editing, importing, and exporting profiles.
    """
    
    def __init__(self, master: tk.Tk, config_manager, logger: logging.Logger, 
                 profiles: List[Profile], on_close_callback: Optional[Callable] = None):
        """
        Initialize the Profile Manager dialog.
        
        Args:
            master: The parent Tkinter window.
            config_manager: ConfigManager or ProfileIOManager instance for profile operations.
            logger: Logger instance for logging events.
            profiles: List of currently available profiles.
            on_close_callback: Optional callback function called when the dialog is closed.
        """
        super().__init__(master)
        self.config_manager = config_manager
        self.logger = logger
        self.profiles = profiles[:]  # Make a copy of the profiles list
        self.on_close_callback = on_close_callback
        
        # Set window properties
        self.title("Profile Manager")
        self.transient(master)  # Make dialog modal to master
        self.grab_set()  # Make dialog modal
        
        # Set up the UI
        self._setup_ui()
        
        # Center the window on the screen
        self._center_window()
        
        # Set window close protocol
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_window(self):
        """Center the dialog window on the screen."""
        self.update_idletasks()
        
        # Get the dialog dimensions
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Get the screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set the position
        self.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Create main content frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Profile List Display
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
        
        # Create and configure Treeview
        columns = ("ID", "Profile Name", "Character Name", "Last Used")
        self.profile_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Hide the ID column but keep it for reference
        self.profile_tree.heading("ID", text="ID")
        self.profile_tree.column("ID", width=0, stretch=tk.NO)
        
        # Configure visible columns
        self.profile_tree.heading("Profile Name", text="Profile Name")
        self.profile_tree.column("Profile Name", width=200, anchor=tk.W)
        
        self.profile_tree.heading("Character Name", text="Character Name")
        self.profile_tree.column("Character Name", width=150, anchor=tk.W)
        
        self.profile_tree.heading("Last Used", text="Last Used")
        self.profile_tree.column("Last Used", width=150, anchor=tk.W)
        
        # Set displaycolumns to hide the ID column visually
        self.profile_tree["displaycolumns"] = ("Profile Name", "Character Name", "Last Used")
        
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.profile_tree.yview)
        self.profile_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack tree and scrollbar
        self.profile_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Create buttons
        create_button = ttk.Button(buttons_frame, text="Create New", command=self._create_new_profile)
        create_button.pack(side=tk.LEFT, padx=2, pady=5)
        
        edit_button = ttk.Button(buttons_frame, text="Edit Selected", command=self._edit_selected_profile)
        edit_button.pack(side=tk.LEFT, padx=2, pady=5)
        
        delete_button = ttk.Button(buttons_frame, text="Delete Selected", command=self._delete_selected_profile)
        delete_button.pack(side=tk.LEFT, padx=2, pady=5)
        
        set_active_button = ttk.Button(buttons_frame, text="Set as Active", command=self._set_active_profile)
        set_active_button.pack(side=tk.LEFT, padx=2, pady=5)
        
        import_button = ttk.Button(buttons_frame, text="Import Profile(s)", command=self._import_profiles)
        import_button.pack(side=tk.LEFT, padx=2, pady=5)
        
        export_button = ttk.Button(buttons_frame, text="Export Selected", command=self._export_selected_profile)
        export_button.pack(side=tk.LEFT, padx=2, pady=5)
        
        close_button = ttk.Button(buttons_frame, text="Close", command=self._on_close)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Load profiles into the list
        self._load_profiles_to_list()
    
    def _load_profiles_to_list(self):
        """Load profiles into the Treeview."""
        # Clear existing items
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        
        # Insert profiles into the Treeview
        for profile in self.profiles:
            # Format last_used_date
            last_used_formatted = profile.last_used_date.strftime('%Y-%m-%d %H:%M') if profile.last_used_date else "Never"
            
            # Insert profile data
            self.profile_tree.insert(
                "", 
                "end", 
                iid=profile.profile_id,  # Use profile_id as the item ID for easy retrieval
                values=(
                    profile.profile_id,
                    profile.profile_name,
                    profile.game_character_name or "-",
                    last_used_formatted
                )
            )
    
    def _create_new_profile(self):
        """Placeholder for creating a new profile."""
        self.logger.info("Create New Profile button clicked (placeholder).")
        messagebox.showinfo("Create New Profile", "This feature will be implemented in Task 3.3.")
    
    def _edit_selected_profile(self):
        """Placeholder for editing the selected profile."""
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to edit.")
            return
        
        selected_id = selected_items[0]  # Get the profile_id of the selected item
        self.logger.info(f"Edit Profile button clicked for profile ID: {selected_id} (placeholder).")
        messagebox.showinfo("Edit Profile", f"This feature will be implemented in Task 3.3.\nSelected Profile ID: {selected_id}")
    
    def _delete_selected_profile(self):
        """Placeholder for deleting the selected profile."""
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to delete.")
            return
        
        selected_id = selected_items[0]  # Get the profile_id of the selected item
        
        # Get the profile name for the confirmation message
        selected_item_values = self.profile_tree.item(selected_id, "values")
        profile_name = selected_item_values[1] if len(selected_item_values) > 1 else "Unknown"
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete the profile '{profile_name}'?\nThis action cannot be undone."
        )
        
        if confirm:
            self.logger.info(f"Delete Profile confirmed for profile ID: {selected_id} (placeholder).")
            messagebox.showinfo("Delete Profile", f"This feature will be implemented in Task 3.3.\nProfile '{profile_name}' would be deleted.")
        else:
            self.logger.info(f"Delete Profile cancelled for profile ID: {selected_id}.")
    
    def _set_active_profile(self):
        """Placeholder for setting the selected profile as active."""
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to set as active.")
            return
        
        selected_id = selected_items[0]  # Get the profile_id of the selected item
        
        # Get the profile name for the info message
        selected_item_values = self.profile_tree.item(selected_id, "values")
        profile_name = selected_item_values[1] if len(selected_item_values) > 1 else "Unknown"
        
        self.logger.info(f"Set as Active button clicked for profile ID: {selected_id} (placeholder).")
        messagebox.showinfo("Set Active Profile", f"This feature will be implemented in Task 3.3.\nProfile '{profile_name}' would be set as active.")
    
    def _import_profiles(self):
        """Placeholder for importing profiles from file."""
        filetypes = [("JSON Files", "*.json"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=filetypes,
            parent=self
        )
        
        if file_path:
            self.logger.info(f"Import Profile file selected: {file_path} (placeholder).")
            messagebox.showinfo("Import Profile", f"This feature will be implemented in Task 3.3.\nSelected file: {file_path}")
        else:
            self.logger.info("Import Profile cancelled.")
    
    def _export_selected_profile(self):
        """Placeholder for exporting selected profile to file."""
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a profile to export.")
            return
        
        selected_id = selected_items[0]  # Get the profile_id of the selected item
        
        # Get the profile name for default filename suggestion
        selected_item_values = self.profile_tree.item(selected_id, "values")
        profile_name = selected_item_values[1] if len(selected_item_values) > 1 else "profile"
        
        # Suggest a filename based on the profile name (normalize for safe filename)
        safe_filename = "".join(c if c.isalnum() or c in "._- " else "_" for c in profile_name)
        suggested_filename = f"{safe_filename.strip()}.json"
        
        filetypes = [("JSON Files", "*.json"), ("All Files", "*.*")]
        file_path = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            initialfile=suggested_filename,
            filetypes=filetypes,
            parent=self
        )
        
        if file_path:
            self.logger.info(f"Export Profile file selected for profile ID {selected_id}: {file_path} (placeholder).")
            messagebox.showinfo("Export Profile", f"This feature will be implemented in Task 3.3.\nProfile would be exported to: {file_path}")
        else:
            self.logger.info(f"Export Profile cancelled for profile ID: {selected_id}.")
    
    def _on_close(self):
        """Handle dialog close."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
    
    def show(self):
        """Show the dialog and wait for it to be closed."""
        self._load_profiles_to_list()
        self.deiconify()
        self.wait_window()


# Self-test block
if __name__ == "__main__":
    # Create a simple logger
    logger = logging.getLogger("ProfileManagerTest")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Create a mock ConfigManager
    class MockConfigManager:
        def __init__(self):
            self.logger = logger
        
        def load_settings(self):
            return AppSettings()
        
        def save_settings(self, settings):
            return True
    
    # Create dummy profiles for testing
    mock_profiles = [
        Profile(
            profile_name="Default Profile",
            app_settings=AppSettings()
        ),
        Profile(
            profile_name="My Warrior",
            game_character_name="Conan",
            app_settings=AppSettings(sprint_key="z")
        ),
        Profile(
            profile_name="My Mage",
            game_character_name="Gandalf",
            app_settings=AppSettings(sprint_key="x", roi_x=100, roi_y=100)
        )
    ]
    
    # Create and run the dialog
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    dialog = ProfileManagerDialog(
        root,
        MockConfigManager(),
        logger,
        mock_profiles
    )
    
    dialog.show()
    
    # Start the Tkinter main loop
    root.mainloop() 