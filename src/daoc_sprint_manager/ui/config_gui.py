"""
Configuration GUI for the DAOC Sprint Manager.

This module provides a Tkinter-based graphical user interface for editing application settings.
"""

import logging
import pathlib
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
import time

# Import Pillow for screenshots
from PIL import Image, ImageTk, ImageGrab

# Import project modules
try:
    from ..config_manager import ConfigManager
    from ..data_models import AppSettings
except ImportError:
    # For standalone testing or direct execution
    import sys
    from pathlib import Path
    # Assumes config_gui.py is in src/daoc_sprint_manager/ui
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / 'src'))
    from daoc_sprint_manager.config_manager import ConfigManager
    from daoc_sprint_manager.data_models import AppSettings


class Tooltip:
    """Simple tooltip implementation for Tkinter widgets."""
    
    def __init__(self, widget, text: str):
        """
        Initialize a tooltip for a widget.
        
        Args:
            widget: The widget to attach the tooltip to
            text: The tooltip text
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)
    
    def _on_enter(self, event=None):
        """Show the tooltip when mouse enters the widget."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create toplevel window for tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # No window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Create label with tooltip text
        label = ttk.Label(
            self.tooltip_window, 
            text=self.text, 
            justify=tk.LEFT,
            background="#ffffe0", 
            relief=tk.SOLID, 
            borderwidth=1,
            wraplength=250
        )
        label.pack(padx=2, pady=2)
    
    def _on_leave(self, event=None):
        """Hide the tooltip when mouse leaves the widget."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ConfigGUI:
    """
    Tkinter-based configuration GUI for the application.
    
    Provides a user-friendly interface for editing all application settings.
    """
    
    def __init__(self, master: tk.Tk, config_manager: ConfigManager, current_settings: AppSettings, logger: logging.Logger, 
                 on_apply_callback: Optional[Callable[[AppSettings], None]] = None,
                 destroy_handler: Optional[Callable[[bool], None]] = None):
        """
        Initialize the configuration GUI.
        
        Args:
            master: The parent Tkinter window.
            config_manager: ConfigManager instance for loading/saving settings.
            current_settings: Current application settings.
            logger: Logger instance for logging events.
            on_apply_callback: Optional callback function called when settings are applied, with the new settings as argument.
            destroy_handler: Optional callback function called when the dialog is closed, with a boolean indicating if settings were applied.
        """
        self.master = master
        self.config_manager = config_manager
        self.initial_settings = current_settings
        self.logger = logger
        self.on_apply_callback = on_apply_callback
        self.destroy_handler = destroy_handler
        
        # Dictionary to store widgets and their variables
        self.widgets: Dict[str, Dict[str, Any]] = {}
        
        # Create toplevel dialog
        self.dialog = tk.Toplevel(master)
        self.dialog.title("DAOC Sprint Manager - Configuration")
        self.dialog.transient(master)  # Make dialog modal to master
        self.dialog.grab_set()  # Make dialog modal
        
        # Track whether changes have been made
        self.unsaved_changes = False
        
        # Create main content frame
        main_content_frame = ttk.Frame(self.dialog, padding="10")
        main_content_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create tabbed interface
        self.notebook = ttk.Notebook(main_content_frame)
        
        # Create tab frames
        self.tab_general = ttk.Frame(self.notebook, padding="10")
        self.tab_detection = ttk.Frame(self.notebook, padding="10")
        self.tab_performance = ttk.Frame(self.notebook, padding="10")
        self.tab_advanced = ttk.Frame(self.notebook, padding="10")
        
        # Add tabs to notebook
        self.notebook.add(self.tab_general, text="General")
        self.notebook.add(self.tab_detection, text="Detection")
        self.notebook.add(self.tab_performance, text="Performance")
        self.notebook.add(self.tab_advanced, text="Advanced")
        
        # Pack the notebook
        self.notebook.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
        
        # Create tab content
        self._create_general_tab()
        self._create_detection_tab()
        self._create_performance_tab()
        self._create_advanced_tab()
        
        # Create button frame
        button_frame = ttk.Frame(main_content_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Create action buttons
        self.apply_button = ttk.Button(button_frame, text="Apply", command=self._apply_settings)
        self.apply_button.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self._cancel_settings)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        self.ok_button = ttk.Button(button_frame, text="OK", command=self._ok_settings)
        self.ok_button.pack(side=tk.RIGHT, padx=5)
        
        # Handle window close event
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel_settings)
        
        # Center the dialog on the screen
        self._center_window()
        
        # Initialize current displayed settings
        self._load_settings_to_ui(self.initial_settings)
        
        self.logger.info("Configuration GUI initialized")
    
    def _center_window(self):
        """Center the dialog window on the screen."""
        self.dialog.update_idletasks()
        
        # Get the dialog dimensions
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()
        
        # Get the screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set the position
        self.dialog.geometry(f"+{x}+{y}")
    
    def _ok_settings(self):
        """Handle OK button click."""
        self.logger.info("OK button clicked.")
        if self._apply_settings():  # Apply settings and continue only if successful
            # Notify destroy handler if provided (true = settings were applied)
            if self.destroy_handler:
                self.destroy_handler(True)
            self.dialog.destroy()
    
    def _cancel_settings(self):
        """Handle Cancel button click."""
        self.logger.info("Cancel button clicked.")
        if self.unsaved_changes:
            if messagebox.askyesno("Confirm Cancel", 
                                   "You have unsaved changes. Are you sure you want to cancel?", 
                                   parent=self.dialog):
                # Notify destroy handler if provided (false = settings were not applied)
                if self.destroy_handler:
                    self.destroy_handler(False)
                self.dialog.destroy()
        else:
            # Notify destroy handler if provided (false = settings were not applied)
            if self.destroy_handler:
                self.destroy_handler(False)
            self.dialog.destroy()
    
    def _apply_settings(self) -> bool:
        """
        Handle Apply button click.
        
        Returns:
            True if settings were successfully applied, False otherwise.
        """
        self.logger.info("Apply button clicked.")
        
        # Validate the settings
        if not self._validate_ui_settings():
            messagebox.showerror("Validation Error", 
                                "Invalid settings found.", 
                                parent=self.dialog)
            return False
        
        # Collect settings from UI
        new_settings = self._collect_settings_from_ui()
        
        # Log settings
        self.logger.info(f"Applying settings")
        
        # Save settings using config manager
        try:
            self.config_manager.save_settings(new_settings)
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Save Error", 
                               f"Error saving settings: {e}", 
                               parent=self.dialog)
            return False
        
        # Update initial settings (applied settings are now the baseline)
        self.initial_settings = new_settings
        
        # Mark changes as saved
        self.unsaved_changes = False
        
        # Call the on_apply_callback if provided
        if self.on_apply_callback:
            try:
                self.on_apply_callback(new_settings)
            except Exception as e:
                self.logger.error(f"Error in apply callback: {e}")
                # Don't fail the apply operation due to callback error
        
        # Show confirmation
        messagebox.showinfo("Apply Settings", 
                           "Settings Applied", 
                           parent=self.dialog)
        
        return True
    
    def _load_settings_to_ui(self, settings: AppSettings):
        """
        Load settings to the UI components.
        
        Args:
            settings: The settings object to load from
        """
        self.logger.info("Loading settings to UI")
        self.current_displayed_settings = settings
        
        # Loop through all widgets and set their values
        for setting_name, widget_info in self.widgets.items():
            # Special case for ML input size components
            if setting_name in ["ml_input_width_var", "ml_input_height_var"]:
                continue
                
            # Get the variable
            var = widget_info['var']
            widget_type = widget_info['type']
            
            # Get the setting value if it exists
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                
                # Set the variable based on widget type
                if widget_type == 'checkbox':
                    var.set(bool(value))
                elif widget_type in ['entry', 'file_browser', 'combobox']:
                    var.set(str(value))
                elif widget_type == 'spinbox':
                    var.set(str(value))
            else:
                self.logger.warning(f"Setting '{setting_name}' not found in AppSettings")
                
        # Handle ML input size separately
        if hasattr(settings, 'ml_input_size_wh') and 'ml_input_width_var' in self.widgets and 'ml_input_height_var' in self.widgets:
            try:
                self.widgets['ml_input_width_var']['var'].set(str(settings.ml_input_size_wh[0]))
                self.widgets['ml_input_height_var']['var'].set(str(settings.ml_input_size_wh[1]))
            except (IndexError, TypeError) as e:
                self.logger.warning(f"Error setting ML input size: {e}")
                # Set default values
                self.widgets['ml_input_width_var']['var'].set("32")
                self.widgets['ml_input_height_var']['var'].set("32")
    
    def _collect_settings_from_ui(self) -> AppSettings:
        """
        Collect settings from UI components.
        
        Returns:
            A new AppSettings instance with values from the UI
        """
        self.logger.info("Collecting settings from UI")
        
        # Start with a copy of the initial settings to ensure all fields are present
        collected_settings_dict = vars(self.initial_settings).copy()
        
        # Loop through all widgets and collect their values
        for setting_name, widget_info in self.widgets.items():
            # Skip ML input size components (handled separately)
            if setting_name in ["ml_input_width_var", "ml_input_height_var"]:
                continue
                
            # Get the variable
            var = widget_info['var']
            widget_type = widget_info['type']
            
            # Get and convert the value based on widget type
            try:
                if widget_type == 'checkbox':
                    collected_settings_dict[setting_name] = var.get()
                elif widget_type in ['entry', 'file_browser', 'combobox']:
                    collected_settings_dict[setting_name] = var.get()
                elif widget_type == 'spinbox':
                    value = var.get()
                    if 'is_float' in widget_info and widget_info['is_float']:
                        collected_settings_dict[setting_name] = float(value)
                    else:
                        collected_settings_dict[setting_name] = int(value)
            except (ValueError, TypeError) as e:
                self.logger.error(f"Error converting {setting_name}: {e}")
                # Keep the original value
                collected_settings_dict[setting_name] = getattr(self.initial_settings, setting_name)
        
        # Handle ML input size separately
        if 'ml_input_width_var' in self.widgets and 'ml_input_height_var' in self.widgets:
            try:
                width = int(self.widgets['ml_input_width_var']['var'].get())
                height = int(self.widgets['ml_input_height_var']['var'].get())
                collected_settings_dict['ml_input_size_wh'] = [width, height]
            except (ValueError, TypeError) as e:
                self.logger.error(f"Error converting ML input size: {e}")
                # Keep the original value
                collected_settings_dict['ml_input_size_wh'] = self.initial_settings.ml_input_size_wh
        
        # Create a new AppSettings instance
        return AppSettings(**collected_settings_dict)
    
    def _validate_ui_settings(self) -> bool:
        """
        Validate settings in the UI.
        
        Performs validation checks on all settings based on their type and expected constraints.
        
        Returns:
            True if all settings are valid, False if any validation fails
        """
        self.logger.info("Validating UI settings")
        
        # Validate ROI coordinates and dimensions
        for setting_name in ['roi_x', 'roi_y', 'roi_width', 'roi_height']:
            if not self._validate_numeric_range(
                self.widgets[setting_name]['var'], 
                0, 
                float('inf'), 
                setting_name,
                int_only=True
            ):
                return False
        
        # Validate template match threshold (0.0-1.0)
        if not self._validate_numeric_range(
            self.widgets['template_match_threshold']['var'], 
            0.0, 
            1.0, 
            'template match threshold'
        ):
            return False
        
        # Validate FPS (1-60)
        if not self._validate_numeric_range(
            self.widgets['capture_fps']['var'], 
            1.0, 
            60.0, 
            'capture FPS'
        ):
            return False
        
        # Validate retry delay values
        if not self._validate_numeric_range(
            self.widgets['game_not_found_retry_delay_s']['var'], 
            0.1, 
            30.0, 
            'game not found retry delay'
        ):
            return False
            
        if not self._validate_numeric_range(
            self.widgets['capture_error_retry_delay_s']['var'], 
            0.1, 
            30.0, 
            'capture error retry delay'
        ):
            return False
        
        # Validate ML confidence threshold (0.0-1.0)
        if not self._validate_numeric_range(
            self.widgets['ml_confidence_threshold']['var'], 
            0.0, 
            1.0, 
            'ML confidence threshold'
        ):
            return False
        
        # Validate temporal consistency frames (1-20)
        if not self._validate_numeric_range(
            self.widgets['temporal_consistency_frames']['var'], 
            1, 
            20, 
            'temporal consistency frames',
            int_only=True
        ):
            return False
        
        # Validate ML input size dimensions
        if not self._validate_numeric_range(
            self.widgets['ml_input_width_var']['var'], 
            8, 
            1024, 
            'ML input width',
            int_only=True
        ):
            return False
            
        if not self._validate_numeric_range(
            self.widgets['ml_input_height_var']['var'], 
            8, 
            1024, 
            'ML input height',
            int_only=True
        ):
            return False
        
        # Validate required file paths
        file_path_settings = [
            ('sprint_on_icon_path', 'sprint ON icon', ['.png', '.jpg', '.jpeg', '.bmp']),
            ('sprint_off_icon_path', 'sprint OFF icon', ['.png', '.jpg', '.jpeg', '.bmp']),
            ('app_icon_path', 'application icon', ['.png', '.jpg', '.jpeg', '.bmp', '.ico']),
            ('ml_model_path', 'ML model', ['.onnx'])
        ]
        
        for setting_name, display_name, extensions in file_path_settings:
            if not self._validate_file_path(
                self.widgets[setting_name]['var'], 
                display_name, 
                expected_exts=extensions
            ):
                return False
        
        # Validate non-empty string fields
        for setting_name, display_name in [
            ('game_window_title', 'game window title'),
            ('log_file_name', 'log file name'),
            ('sprint_key', 'sprint key')
        ]:
            if not self._validate_not_empty(
                self.widgets[setting_name]['var'], 
                display_name
            ):
                return False
        
        # Validate sprint key format (single character or valid key name)
        sprint_key = self.widgets['sprint_key']['var'].get().strip()
        if len(sprint_key) != 1 and not sprint_key.lower() in [
            'tab', 'enter', 'space', 'esc', 'shift', 'ctrl', 'alt',
            'up', 'down', 'left', 'right', 'backspace', 'delete',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
        ]:
            messagebox.showerror(
                "Validation Error", 
                "Sprint key must be a single character or a valid key name (e.g., 'tab', 'enter', 'space', 'esc', 'shift').",
                parent=self.dialog
            )
            return False
        
        # Validate log level selection
        log_level = self.widgets['log_level']['var'].get().upper()
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_log_levels:
            messagebox.showerror(
                "Validation Error", 
                f"Log level must be one of: {', '.join(valid_log_levels)}",
                parent=self.dialog
            )
            return False
        
        # All validations passed
        self.logger.info("All settings validated successfully")
        return True
    
    def _validate_numeric_range(self, widget_var, min_val, max_val, setting_name_for_error: str, int_only: bool = False) -> bool:
        """
        Validate a numeric value is within a specified range.
        
        Args:
            widget_var: The Tkinter variable to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            setting_name_for_error: Name of the setting for error messages
            int_only: Whether the value must be an integer
            
        Returns:
            True if valid, False otherwise
        """
        try:
            value = widget_var.get()
            if int_only:
                numeric_value = int(value)
            else:
                numeric_value = float(value)
                
            if numeric_value < min_val or numeric_value > max_val:
                messagebox.showerror(
                    "Validation Error", 
                    f"The {setting_name_for_error} must be between {min_val} and {max_val}.",
                    parent=self.dialog
                )
                return False
        except ValueError:
            type_str = "integer" if int_only else "number"
            messagebox.showerror(
                "Validation Error", 
                f"The {setting_name_for_error} must be a valid {type_str}.",
                parent=self.dialog
            )
            return False
        
        return True
    
    def _validate_file_path(self, widget_var, setting_name_for_error: str, must_exist: bool = True, expected_exts: list = None) -> bool:
        """
        Validate a file path.
        
        Args:
            widget_var: The Tkinter variable to validate
            setting_name_for_error: Name of the setting for error messages
            must_exist: Whether the file must exist
            expected_exts: List of expected file extensions (e.g., ['.png', '.jpg'])
            
        Returns:
            True if valid, False otherwise
        """
        file_path = widget_var.get().strip()
        
        if not file_path:
            messagebox.showerror(
                "Validation Error", 
                f"The {setting_name_for_error} path cannot be empty.",
                parent=self.dialog
            )
            return False
            
        path_obj = pathlib.Path(file_path)
        
        # Check if file exists if required
        if must_exist and not path_obj.is_file():
            messagebox.showerror(
                "Validation Error", 
                f"The {setting_name_for_error} file does not exist: {file_path}",
                parent=self.dialog
            )
            return False
            
        # Check file extension if specified
        if expected_exts and path_obj.suffix.lower() not in expected_exts:
            messagebox.showerror(
                "Validation Error", 
                f"The {setting_name_for_error} file must have one of these extensions: {', '.join(expected_exts)}",
                parent=self.dialog
            )
            return False
            
        return True
    
    def _validate_not_empty(self, widget_var, setting_name_for_error: str) -> bool:
        """
        Validate a string value is not empty.
        
        Args:
            widget_var: The Tkinter variable to validate
            setting_name_for_error: Name of the setting for error messages
            
        Returns:
            True if valid, False otherwise
        """
        value = widget_var.get().strip()
        
        if not value:
            messagebox.showerror(
                "Validation Error", 
                f"The {setting_name_for_error} cannot be empty.",
                parent=self.dialog
            )
            return False
            
        return True
    
    def show(self):
        """Show the configuration dialog and wait for user interaction."""
        self.dialog.deiconify()  # Make sure dialog is visible
        self.dialog.wait_window()  # Wait until dialog is closed

    def _create_entry_field(self, parent, setting_name: str, label_text: str, tooltip_text: str, width: int = 40) -> ttk.Frame:
        """
        Create a labeled entry field with tooltip.
        
        Args:
            parent: Parent widget
            setting_name: Name of the setting in AppSettings
            label_text: Text to display in the label
            tooltip_text: Text to display in the tooltip
            width: Width of the entry field
            
        Returns:
            The frame containing the widgets
        """
        frame = ttk.Frame(parent)
        
        # Create label
        label = ttk.Label(frame, text=label_text, width=20, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create entry with variable
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var, width=width)
        entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Store widget info
        self.widgets[setting_name] = {
            'widget': entry,
            'var': var,
            'type': 'entry'
        }
        
        # Add tooltip
        Tooltip(entry, tooltip_text)
        
        # Bind change event
        entry.bind("<KeyRelease>", self._mark_as_changed)
        
        return frame
    
    def _create_checkbox(self, parent, setting_name: str, label_text: str, tooltip_text: str) -> ttk.Frame:
        """
        Create a checkbox with tooltip.
        
        Args:
            parent: Parent widget
            setting_name: Name of the setting in AppSettings
            label_text: Text to display in the label
            tooltip_text: Text to display in the tooltip
            
        Returns:
            The frame containing the widgets
        """
        frame = ttk.Frame(parent)
        
        # Create variable
        var = tk.BooleanVar()
        
        # Create checkbox
        checkbox = ttk.Checkbutton(
            frame, 
            text=label_text, 
            variable=var,
            command=self._mark_as_changed
        )
        checkbox.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Store widget info
        self.widgets[setting_name] = {
            'widget': checkbox,
            'var': var,
            'type': 'checkbox'
        }
        
        # Add tooltip
        Tooltip(checkbox, tooltip_text)
        
        return frame
    
    def _create_spinbox(
        self, 
        parent, 
        setting_name: str, 
        label_text: str, 
        from_val: float, 
        to_val: float, 
        increment: float, 
        tooltip_text: str, 
        width: int = 10,
        format_str: str = None
    ) -> ttk.Frame:
        """
        Create a labeled spinbox with tooltip.
        
        Args:
            parent: Parent widget
            setting_name: Name of the setting in AppSettings
            label_text: Text to display in the label
            from_val: Minimum value
            to_val: Maximum value
            increment: Increment step
            tooltip_text: Text to display in the tooltip
            width: Width of the spinbox
            format_str: Format string for the spinbox value (e.g., "%.2f")
            
        Returns:
            The frame containing the widgets
        """
        frame = ttk.Frame(parent)
        
        # Create label
        label = ttk.Label(frame, text=label_text, width=20, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create spinbox with variable
        var = tk.StringVar()
        spinbox_kwargs = {
            'textvariable': var,
            'from_': from_val,
            'to': to_val,
            'increment': increment,
            'width': width
        }
        
        if format_str:
            spinbox_kwargs['format'] = format_str
            
        spinbox = ttk.Spinbox(frame, **spinbox_kwargs)
        spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Store widget info
        self.widgets[setting_name] = {
            'widget': spinbox,
            'var': var,
            'type': 'spinbox',
            'is_float': '.' in str(increment) or '.' in str(from_val) or '.' in str(to_val)
        }
        
        # Add tooltip
        Tooltip(spinbox, tooltip_text)
        
        # Bind change events
        spinbox.bind("<KeyRelease>", self._mark_as_changed)
        spinbox.bind("<<Increment>>", self._mark_as_changed)
        spinbox.bind("<<Decrement>>", self._mark_as_changed)
        
        return frame
    
    def _create_combobox(
        self, 
        parent, 
        setting_name: str, 
        label_text: str, 
        values: list, 
        tooltip_text: str, 
        width: int = 38,
        readonly: bool = True
    ) -> ttk.Frame:
        """
        Create a labeled combobox with tooltip.
        
        Args:
            parent: Parent widget
            setting_name: Name of the setting in AppSettings
            label_text: Text to display in the label
            values: List of values for the combobox
            tooltip_text: Text to display in the tooltip
            width: Width of the combobox
            readonly: Whether the combobox should be readonly
            
        Returns:
            The frame containing the widgets
        """
        frame = ttk.Frame(parent)
        
        # Create label
        label = ttk.Label(frame, text=label_text, width=20, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create combobox with variable
        var = tk.StringVar()
        combobox = ttk.Combobox(
            frame, 
            textvariable=var, 
            values=values, 
            width=width
        )
        
        if readonly:
            combobox.state(['readonly'])
            
        combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Store widget info
        self.widgets[setting_name] = {
            'widget': combobox,
            'var': var,
            'type': 'combobox'
        }
        
        # Add tooltip
        Tooltip(combobox, tooltip_text)
        
        # Bind change event
        combobox.bind("<<ComboboxSelected>>", self._mark_as_changed)
        
        return frame
    
    def _create_file_browser(
        self, 
        parent, 
        setting_name: str, 
        label_text: str, 
        dialog_title: str, 
        file_types: list, 
        tooltip_text: str, 
        entry_width: int = 30
    ) -> ttk.Frame:
        """
        Create a file browser field with button.
        
        Args:
            parent: Parent widget
            setting_name: Name of the setting in AppSettings
            label_text: Text to display in the label
            dialog_title: Title for the file dialog
            file_types: List of file type tuples for the file dialog
            tooltip_text: Text to display in the tooltip
            entry_width: Width of the entry field
            
        Returns:
            The frame containing the widgets
        """
        frame = ttk.Frame(parent)
        
        # Create label
        label = ttk.Label(frame, text=label_text, width=20, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create entry with variable
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var, width=entry_width)
        entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Create browse function
        def browse_file():
            filename = filedialog.askopenfilename(
                title=dialog_title,
                filetypes=file_types,
                parent=self.dialog
            )
            if filename:
                var.set(filename)
                self._mark_as_changed()
        
        # Create browse button
        browse_button = ttk.Button(frame, text="Browse...", command=browse_file)
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Store widget info
        self.widgets[setting_name] = {
            'widget': entry,
            'var': var,
            'type': 'file_browser'
        }
        
        # Add tooltip
        Tooltip(entry, tooltip_text)
        
        # Bind change event
        entry.bind("<KeyRelease>", self._mark_as_changed)
        
        return frame
    
    def _create_section_label(self, parent, text: str) -> ttk.Frame:
        """
        Create a section heading label with separator.
        
        Args:
            parent: Parent widget
            text: Text to display in the label
            
        Returns:
            The frame containing the widgets
        """
        frame = ttk.Frame(parent)
        
        # Create label
        label = ttk.Label(frame, text=text, font=("TkDefaultFont", 10, "bold"))
        label.pack(anchor=tk.W, padx=5, pady=(10, 2))
        
        # Create separator
        separator = ttk.Separator(frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        return frame
    
    def _mark_as_changed(self, event=None):
        """Mark settings as changed."""
        self.unsaved_changes = True
        self.logger.debug("GUI settings modified.")
    
    def _create_general_tab(self):
        """Create and populate the General tab with widgets."""
        # Game Settings frame
        game_frame = ttk.LabelFrame(self.tab_general, text="Game Settings", padding=10)
        game_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        # Game window title
        self._create_entry_field(
            game_frame,
            "game_window_title",
            "Window Title:",
            "Window title to search for. Should match a unique part of the game's window title."
        ).pack(fill=tk.X)
        
        # Sprint key
        self._create_entry_field(
            game_frame,
            "sprint_key",
            "Sprint Key:",
            "Keyboard key to press/release for sprint toggle (e.g. 'z', 'r')."
        ).pack(fill=tk.X)
    
    def _create_detection_tab(self):
        """Create and populate the Detection tab with widgets."""
        # Region of Interest frame
        roi_frame = ttk.LabelFrame(self.tab_detection, text="Region of Interest (ROI)", padding=10)
        roi_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        # ROI coordinates
        self._create_spinbox(
            roi_frame,
            "roi_x",
            "X Coordinate:",
            0, 8000, 1,
            "X-coordinate of the top-left corner of the region of interest in the game window."
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            roi_frame,
            "roi_y",
            "Y Coordinate:",
            0, 8000, 1,
            "Y-coordinate of the top-left corner of the region of interest in the game window."
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            roi_frame,
            "roi_width",
            "Width:",
            10, 1000, 1,
            "Width of the region of interest in pixels."
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            roi_frame,
            "roi_height",
            "Height:",
            10, 1000, 1,
            "Height of the region of interest in pixels."
        ).pack(fill=tk.X)
        
        # ROI selection button
        roi_button_frame = ttk.Frame(roi_frame)
        roi_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        roi_button = ttk.Button(roi_button_frame, text="Select ROI Visually...", command=self._select_roi_visual)
        roi_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Template Matching frame
        template_frame = ttk.LabelFrame(self.tab_detection, text="Template Matching", padding=10)
        template_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        self._create_file_browser(
            template_frame,
            "sprint_on_icon_path",
            "ON Icon Template:",
            "Select Sprint ON Icon Template",
            [("PNG files", "*.png"), ("All files", "*.*")],
            "Path to the sprint 'ON' icon template image, relative to the project root."
        ).pack(fill=tk.X)
        
        self._create_file_browser(
            template_frame,
            "sprint_off_icon_path",
            "OFF Icon Template:",
            "Select Sprint OFF Icon Template",
            [("PNG files", "*.png"), ("All files", "*.*")],
            "Path to the sprint 'OFF' icon template image, relative to the project root."
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            template_frame,
            "template_match_threshold",
            "Match Threshold:",
            0.0, 1.0, 0.05,
            "Confidence threshold for template matching (0.0-1.0). Higher values require closer matches.",
            format_str="%.2f"
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            template_frame,
            "temporal_consistency_frames",
            "Consistency Frames:",
            1, 20, 1,
            "Number of consecutive consistent frames required to confirm a state change."
        ).pack(fill=tk.X)
        
        # Detection Method frame
        detection_method_frame = ttk.LabelFrame(self.tab_detection, text="Detection Method", padding=10)
        detection_method_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        self._create_combobox(
            detection_method_frame,
            "detection_method",
            "Method:",
            ["template", "ml"],
            "Detection method to use: template matching or machine learning."
        ).pack(fill=tk.X)
        
        # ML Detection Settings frame
        ml_frame = ttk.LabelFrame(self.tab_detection, text="ML Detection Settings", padding=10)
        ml_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        self._create_file_browser(
            ml_frame,
            "ml_model_path",
            "ML Model:",
            "Select ML Model",
            [("ONNX models", "*.onnx"), ("All files", "*.*")],
            "Path to the ONNX ML model file, relative to the project root."
        ).pack(fill=tk.X)
        
        # ML input size (special case with two spinboxes)
        ml_size_frame = ttk.Frame(ml_frame)
        ml_size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ml_size_frame, text="ML Input Size:", width=20, anchor=tk.W).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        # Width spinbox
        width_var = tk.StringVar()
        width_spinbox = ttk.Spinbox(
            ml_size_frame,
            textvariable=width_var,
            from_=8,
            to=256,
            increment=1,
            width=5
        )
        width_spinbox.grid(row=0, column=1, padx=2, pady=5)
        
        ttk.Label(ml_size_frame, text="×").grid(row=0, column=2, padx=2, pady=5)
        
        # Height spinbox
        height_var = tk.StringVar()
        height_spinbox = ttk.Spinbox(
            ml_size_frame,
            textvariable=height_var,
            from_=8,
            to=256,
            increment=1,
            width=5
        )
        height_spinbox.grid(row=0, column=3, padx=2, pady=5)
        
        ttk.Label(ml_size_frame, text="pixels").grid(row=0, column=4, padx=2, pady=5)
        
        # Store the variables
        self.widgets["ml_input_width_var"] = {
            'widget': width_spinbox,
            'var': width_var,
            'type': 'spinbox',
            'is_float': False
        }
        
        self.widgets["ml_input_height_var"] = {
            'widget': height_spinbox,
            'var': height_var,
            'type': 'spinbox',
            'is_float': False
        }
        
        # Add tooltips
        Tooltip(width_spinbox, "Required input width in pixels for the ML model.")
        Tooltip(height_spinbox, "Required input height in pixels for the ML model.")
        
        # Bind change events
        width_spinbox.bind("<KeyRelease>", self._mark_as_changed)
        width_spinbox.bind("<<Increment>>", self._mark_as_changed)
        width_spinbox.bind("<<Decrement>>", self._mark_as_changed)
        height_spinbox.bind("<KeyRelease>", self._mark_as_changed)
        height_spinbox.bind("<<Increment>>", self._mark_as_changed)
        height_spinbox.bind("<<Decrement>>", self._mark_as_changed)
        
        # ML confidence threshold
        self._create_spinbox(
            ml_frame,
            "ml_confidence_threshold",
            "ML Threshold:",
            0.0, 1.0, 0.05,
            "Confidence threshold for ML detection (0.0-1.0). Higher values require higher confidence.",
            format_str="%.2f"
        ).pack(fill=tk.X)
    
    def _create_performance_tab(self):
        """Create and populate the Performance tab with widgets."""
        # Capture & Processing frame
        capture_frame = ttk.LabelFrame(self.tab_performance, text="Capture & Processing", padding=10)
        capture_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        self._create_spinbox(
            capture_frame,
            "capture_fps",
            "Capture FPS:",
            1, 60, 1,
            "Target frames per second for capture and detection loop."
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            capture_frame,
            "inactive_window_poll_delay_s",
            "Inactive Poll Delay:",
            0.1, 10.0, 0.1,
            "Delay in seconds between polls when the game window is inactive.",
            format_str="%.1f"
        ).pack(fill=tk.X)
        
        # Retry Delays frame
        retry_frame = ttk.LabelFrame(self.tab_performance, text="Retry Delays", padding=10)
        retry_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        self._create_spinbox(
            retry_frame,
            "game_not_found_retry_delay_s",
            "Window Retry Delay:",
            1, 60, 1,
            "Delay in seconds between retries when game window is not found."
        ).pack(fill=tk.X)
        
        self._create_spinbox(
            retry_frame,
            "capture_error_retry_delay_s",
            "Capture Retry Delay:",
            1, 60, 1,
            "Delay in seconds between retries when capture fails."
        ).pack(fill=tk.X)
        
        # Metrics frame
        metrics_frame = ttk.LabelFrame(self.tab_performance, text="Metrics", padding=10)
        metrics_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.N)
        
        self._create_checkbox(
            metrics_frame,
            "show_performance_metrics",
            "Show Performance Metrics",
            "Whether to periodically log performance metrics."
        ).pack(fill=tk.X)
    
    def _create_advanced_tab(self):
        """Create the advanced settings tab."""
        self.logger.debug("Creating advanced settings tab")
        
        # Auto Profile Switching Settings
        profile_section_frame = self._create_section_label(self.tab_advanced, "Profile Settings")
        profile_section_frame.pack(fill=tk.X, pady=(0, 10))
        
        auto_switch_frame = self._create_checkbox(
            self.tab_advanced,
            "enable_auto_profile_switching",
            "Enable automatic profile switching",
            "When enabled, the application will automatically switch to profiles with matching window title patterns"
        )
        auto_switch_frame.pack(fill=tk.X, pady=5)

        # Logging Settings
        logging_section_frame = self._create_section_label(self.tab_advanced, "Logging Settings")
        logging_section_frame.pack(fill=tk.X, pady=(10, 10))
        
        log_level_frame = self._create_combobox(
            self.tab_advanced,
            "log_level",
            "Log Level:",
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "Controls how much detail is written to the log file. DEBUG is the most verbose, CRITICAL the least."
        )
        log_level_frame.pack(fill=tk.X, pady=5)
        
        log_filename_frame = self._create_entry_field(
            self.tab_advanced,
            "log_file_name",
            "Log File Name:",
            "Name of the log file to be created in the logs directory."
        )
        log_filename_frame.pack(fill=tk.X, pady=5)
        
        # UI Settings
        ui_section_frame = self._create_section_label(self.tab_advanced, "UI Settings")
        ui_section_frame.pack(fill=tk.X, pady=(10, 10))
        
        app_icon_frame = self._create_file_browser(
            self.tab_advanced,
            "app_icon_path",
            "System Tray Icon:",
            "Select System Tray Icon",
            [("PNG Files", "*.png"), ("All Files", "*.*")],
            "Path to the icon image displayed in the system tray. Recommended: 16x16 or 32x32 PNG with transparency."
        )
        app_icon_frame.pack(fill=tk.X, pady=5)
        
        # Diagnostics Settings
        diagnostics_section_frame = self._create_section_label(self.tab_advanced, "Diagnostics")
        diagnostics_section_frame.pack(fill=tk.X, pady=(10, 10))
        
        save_frames_frame = self._create_checkbox(
            self.tab_advanced,
            "save_problematic_frames",
            "Save Problematic Frames",
            "Save frames that cause detection issues for later analysis and debugging."
        )
        save_frames_frame.pack(fill=tk.X, pady=5)
        
        frames_path_frame = self._create_entry_field(
            self.tab_advanced,
            "problematic_frame_save_path",
            "Problematic Frames Save Path:",
            "Directory where problematic frames will be saved (relative to project root)."
        )
        frames_path_frame.pack(fill=tk.X, pady=5)
    
    def _select_roi_visual(self):
        """
        Open a fullscreen window with a screenshot for visual ROI selection.
        
        This allows the user to draw a rectangle on a screenshot to select
        the region of interest for sprint icon detection.
        """
        self.logger.info("Starting visual ROI selection")
        
        # Hide the main dialog temporarily
        self.dialog.withdraw()
        self.dialog.update_idletasks()  # Ensure dialog is hidden before screenshot
        time.sleep(0.1)  # Small delay to ensure dialog is hidden
        
        try:
            # Capture the primary screen
            screenshot = ImageGrab.grab(all_screens=False)
            
            # Create a new toplevel window for ROI selection
            self.roi_selector_window = tk.Toplevel(self.dialog)
            self.roi_selector_window.title("ROI Selection")
            
            # Make the window fullscreen
            self.roi_selector_window.attributes("-fullscreen", True)
            
            # Make it modal
            self.roi_selector_window.transient(self.dialog)
            self.roi_selector_window.grab_set()
            
            # Convert Pillow image to Tkinter PhotoImage
            photo_image = ImageTk.PhotoImage(screenshot)
            
            # Create a canvas for the screenshot that fills the window
            self.canvas = tk.Canvas(
                self.roi_selector_window,
                width=screenshot.width,
                height=screenshot.height
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Display the screenshot on the canvas
            self.canvas.create_image(0, 0, image=photo_image, anchor=tk.NW)
            self.canvas.image = photo_image  # Keep a reference to prevent garbage collection
            
            # Create instruction label
            instruction_label = tk.Label(
                self.roi_selector_window,
                text="Click and drag to select the ROI. Press Enter to confirm, Escape to cancel.",
                font=("TkDefaultFont", 12, "bold"),
                bg="#ffffcc",
                relief=tk.SOLID,
                borderwidth=1,
                padx=10,
                pady=5
            )
            instruction_label.place(x=10, y=10)
            
            # Initialize selection variables
            self._roi_start_x = None
            self._roi_start_y = None
            self._current_roi_rect_id = None
            self._selected_roi_coords = None
            
            # Bind canvas events for rectangle drawing
            self.canvas.bind("<ButtonPress-1>", self._on_roi_canvas_press)
            self.canvas.bind("<B1-Motion>", self._on_roi_canvas_drag)
            self.canvas.bind("<ButtonRelease-1>", self._on_roi_canvas_release)
            
            # Bind keyboard events for confirmation/cancellation
            self.roi_selector_window.bind("<Escape>", lambda e: self._cancel_roi_selection())
            self.roi_selector_window.bind("<Return>", lambda e: self._confirm_roi_selection())
            
        except Exception as e:
            self.logger.error(f"Error in ROI selection: {e}")
            messagebox.showerror(
                "Screenshot Error", 
                f"Failed to capture screenshot: {e}",
                parent=self.dialog
            )
            self.dialog.deiconify()  # Show the dialog again
    
    def _on_roi_canvas_press(self, event):
        """Handle mouse button press on the ROI selection canvas."""
        # Store the starting point
        self._roi_start_x = event.x
        self._roi_start_y = event.y
        
        # Clear any existing rectangle
        if self._current_roi_rect_id is not None:
            self.canvas.delete(self._current_roi_rect_id)
            self._current_roi_rect_id = None
    
    def _on_roi_canvas_drag(self, event):
        """Handle mouse drag on the ROI selection canvas."""
        if self._roi_start_x is None:
            return
            
        # Delete the previous rectangle if it exists
        if self._current_roi_rect_id is not None:
            self.canvas.delete(self._current_roi_rect_id)
            
        # Draw a new rectangle
        self._current_roi_rect_id = self.canvas.create_rectangle(
            self._roi_start_x, self._roi_start_y, 
            event.x, event.y,
            outline="red",
            width=2
        )
    
    def _on_roi_canvas_release(self, event):
        """Handle mouse button release on the ROI selection canvas."""
        if self._roi_start_x is None:
            return
            
        # Get the end coordinates
        end_x = event.x
        end_y = event.y
        
        # Calculate the final ROI coordinates
        # Ensure x, y is the top-left corner and width, height are positive
        final_roi_x = min(self._roi_start_x, end_x)
        final_roi_y = min(self._roi_start_y, end_y)
        final_roi_width = abs(end_x - self._roi_start_x)
        final_roi_height = abs(end_y - self._roi_start_y)
        
        # Store the selected ROI
        self._selected_roi_coords = (final_roi_x, final_roi_y, final_roi_width, final_roi_height)
        
        # Update the rectangle to have a more prominent appearance
        if self._current_roi_rect_id is not None:
            self.canvas.delete(self._current_roi_rect_id)
            
        self._current_roi_rect_id = self.canvas.create_rectangle(
            final_roi_x, final_roi_y,
            final_roi_x + final_roi_width,
            final_roi_y + final_roi_height,
            outline="red",
            width=3
        )
    
    def _confirm_roi_selection(self):
        """Confirm the ROI selection and update the settings."""
        if self._selected_roi_coords is None:
            messagebox.showwarning(
                "ROI Selection",
                "No ROI selected. Please draw a rectangle or press Escape to cancel.",
                parent=self.roi_selector_window
            )
            return
            
        x, y, width, height = self._selected_roi_coords
        
        # Validate the selection
        if width <= 0 or height <= 0:
            messagebox.showwarning(
                "Invalid ROI",
                "The selected area is too small. Please try again.",
                parent=self.roi_selector_window
            )
            return
            
        # Update the ROI fields in the GUI
        self.widgets['roi_x']['var'].set(str(x))
        self.widgets['roi_y']['var'].set(str(y))
        self.widgets['roi_width']['var'].set(str(width))
        self.widgets['roi_height']['var'].set(str(height))
        
        # Mark settings as changed
        self._mark_as_changed()
        
        # Log the new ROI
        self.logger.info(f"ROI selected visually: x={x}, y={y}, width={width}, height={height}")
        
        # Close the ROI selector window
        self.roi_selector_window.destroy()
        
        # Show the main dialog again
        self.dialog.deiconify()
    
    def _cancel_roi_selection(self):
        """Cancel the ROI selection process."""
        self.logger.info("ROI selection cancelled")
        
        # Close the ROI selector window
        self.roi_selector_window.destroy()
        
        # Show the main dialog again
        self.dialog.deiconify()


if __name__ == "__main__":
    """Self-test code for the ConfigGUI with validation testing."""
    import sys
    from pathlib import Path
    
    # Assumes config_gui.py is in src/daoc_sprint_manager/ui
    # Moves up three levels to get to PythonSprint/
    project_root_for_test = Path(__file__).resolve().parent.parent.parent
    src_path_for_test = project_root_for_test / 'src'
    if str(src_path_for_test) not in sys.path:
        sys.path.insert(0, str(src_path_for_test))
    
    from daoc_sprint_manager.utils.logger import setup_logger
    from daoc_sprint_manager.config_manager import ConfigManager
    from daoc_sprint_manager.data_models import AppSettings
    
    # Create a root window
    root = tk.Tk()
    root.title("ConfigGUI Test - Settings Validation")
    root.geometry("400x250")
    
    # Set up a dummy logger
    logs_dir = project_root_for_test / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "config_gui_test.log"
    logger = setup_logger("config_gui_test", log_file, logging.DEBUG)
    
    # Mock ConfigManager for testing
    class MockConfigManager:
        def __init__(self, settings_file_path=None, template_file_path=None, logger=None):
            self.logger = logger or logging.getLogger("MockConfigManager")
            self.logger.info("Mock ConfigManager initialized")
        
        def load_settings(self) -> AppSettings:
            self.logger.info("Mock load_settings called")
            # Create an AppSettings with default values plus some test values
            settings = AppSettings(
                game_window_title="Dark Age of Camelot Test",
                roi_x=100,
                roi_y=100,
                roi_width=300,
                roi_height=300,
                sprint_key="z",
                template_match_threshold=0.8,
                capture_fps=10.0,
                ml_confidence_threshold=0.7,
                detection_method="template",
                inactive_window_poll_delay_s=5.0,
                save_problematic_frames=True,
                problematic_frame_save_path="data/problematic_frames"
            )
            return settings
        
        def save_settings(self, settings_to_save: AppSettings) -> bool:
            self.logger.info(f"Mock save_settings called - would save to: {settings_to_save}")
            return True
    
    # Add a frame with test buttons
    test_frame = ttk.LabelFrame(root, text="Testing Options")
    test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add buttons for different test scenarios
    def open_config_dialog(test_type=None):
        # Create mock objects
        mock_config_manager = MockConfigManager(logger=logger)
        mock_settings = mock_config_manager.load_settings()
        
        # Create and show the configuration GUI
        config_gui = ConfigGUI(root, mock_config_manager, mock_settings, logger)
        
        # If we have a test type, introduce validation errors
        if test_type == "numeric_error":
            # Set an invalid value for capture_fps to test numeric validation
            config_gui.widgets['capture_fps']['var'].set("not a number")
            logger.info("Introduced numeric validation error for testing")
        elif test_type == "range_error":
            # Set an out-of-range value for template match threshold
            config_gui.widgets['template_match_threshold']['var'].set("2.5")
            logger.info("Introduced range validation error for testing")
        elif test_type == "path_error":
            # Set a non-existent path for testing file path validation
            config_gui.widgets['sprint_on_icon_path']['var'].set("/path/does/not/exist.png")
            logger.info("Introduced file path validation error for testing")
        elif test_type == "empty_error":
            # Set an empty value for a required field
            config_gui.widgets['game_window_title']['var'].set("")
            logger.info("Introduced empty field validation error for testing")
        
        config_gui.show()
        
        # After the dialog is closed, log the result
        logger.info("Configuration dialog closed")
    
    # Create buttons for normal and validation testing scenarios
    ttk.Button(
        test_frame, 
        text="Open Normal Config Dialog", 
        command=lambda: open_config_dialog()
    ).pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(
        test_frame, 
        text="Test Numeric Validation Error", 
        command=lambda: open_config_dialog("numeric_error")
    ).pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(
        test_frame, 
        text="Test Range Validation Error", 
        command=lambda: open_config_dialog("range_error")
    ).pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(
        test_frame, 
        text="Test File Path Validation Error", 
        command=lambda: open_config_dialog("path_error")
    ).pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(
        test_frame, 
        text="Test Empty Field Validation Error", 
        command=lambda: open_config_dialog("empty_error")
    ).pack(fill=tk.X, padx=5, pady=5)
    
    # Instructions label
    ttk.Label(
        root, 
        text="Click any button to open the config dialog with different validation test scenarios.\n"
             "Try clicking Apply or OK to test validation.",
        justify=tk.CENTER
    ).pack(fill=tk.X, padx=10, pady=5)
    
    # Start the main event loop
    logger.info("Starting test application with validation testing")
    root.mainloop() 