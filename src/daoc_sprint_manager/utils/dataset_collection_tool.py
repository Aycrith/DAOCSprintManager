"""Dataset Collection Utility for ML Model Training.

This module provides a standalone graphical tool for capturing,
labeling, and preparing sprint icon images for ML model training.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from pathlib import Path
import datetime
import json
import csv
from typing import Optional, Tuple, List, Dict, Any

import numpy as np
import cv2
from PIL import Image, ImageTk, ImageGrab, ImageOps, ImageEnhance

from daoc_sprint_manager.data_models import AppSettings
from daoc_sprint_manager.config_manager import ConfigManager
from daoc_sprint_manager.utils.logger import setup_logger


class Tooltip:
    """Display a tooltip when hovering over a widget."""
    
    def __init__(self, widget: tk.Widget, text: str):
        """Initialize a tooltip for the specified widget.
        
        Args:
            widget: The widget to attach the tooltip to.
            text: The text to display in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """Show the tooltip when mouse enters the widget."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tooltip_window, 
            text=self.text, 
            background="#FFFFDD", 
            relief=tk.SOLID, 
            borderwidth=1,
            wraplength=350, 
            justify=tk.LEFT
        )
        label.pack(padx=2, pady=2)
    
    def on_leave(self, event=None):
        """Hide the tooltip when mouse leaves the widget."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ROISelector:
    """Interactive ROI selection from screen."""
    
    def __init__(self, parent: tk.Tk, callback):
        """Initialize the ROI selector.
        
        Args:
            parent: The parent tkinter window.
            callback: Function to call with the selected coordinates (x, y, width, height).
        """
        self.parent = parent
        self.callback = callback
        
        # Take a screenshot of the entire screen
        self.screenshot = ImageGrab.grab()
        self.screenshot_np = np.array(self.screenshot)
        self.roi_window = tk.Toplevel(parent)
        self.roi_window.attributes('-fullscreen', True)
        self.roi_window.title("Select ROI")
        
        # Convert the screenshot to a Tkinter PhotoImage
        self.tk_image = ImageTk.PhotoImage(self.screenshot)
        
        # Create a canvas to display the screenshot
        self.canvas = tk.Canvas(
            self.roi_window, 
            width=self.screenshot.width, 
            height=self.screenshot.height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)
        
        # Add rectangle for ROI selection
        self.rect = None
        self.start_x = None
        self.start_y = None
        
        # Add preview window
        self.preview_window = None
        self.preview_label = None
        
        # Bind mouse and keyboard events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.roi_window.bind("<Escape>", lambda e: self.on_cancel())
        self.roi_window.bind("<Return>", lambda e: self.on_confirm())
        
        # Add instructions text with background for better visibility
        instructions = [
            "Click and drag to select the sprint icon",
            "Press Enter to confirm selection",
            "Press Escape to cancel",
            "Selection should be at least 10x10 pixels"
        ]
        
        # Create a semi-transparent background for instructions
        bg_rect = self.canvas.create_rectangle(
            10, 10, 400, 100,
            fill='black', stipple='gray50',
            outline='white'
        )
        
        y_pos = 30
        for instruction in instructions:
            self.canvas.create_text(
                20, y_pos,
                text=instruction,
                fill="white",
                font=("Arial", 12, "bold"),
                anchor=tk.W
            )
            y_pos += 20
        
        # Add buttons frame
        self.buttons_frame = ttk.Frame(self.roi_window)
        self.buttons_frame.place(x=10, y=self.screenshot.height - 50)
        
        ttk.Button(
            self.buttons_frame,
            text="Cancel",
            command=self.on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.buttons_frame,
            text="Confirm",
            command=self.on_confirm
        ).pack(side=tk.LEFT, padx=5)
        
        # Add dimensions display
        self.dimensions_text = self.canvas.create_text(
            10, self.screenshot.height - 70,
            text="",
            fill="white",
            font=("Arial", 10),
            anchor=tk.W
        )
    
    def show_preview(self, x1, y1, x2, y2):
        """Show a preview of the selected region."""
        if self.preview_window is None:
            self.preview_window = tk.Toplevel(self.roi_window)
            self.preview_window.title("ROI Preview")
            self.preview_window.attributes('-topmost', True)
            self.preview_label = ttk.Label(self.preview_window)
            self.preview_label.pack(padx=5, pady=5)
        
        # Get the region from the screenshot
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        if x2 - x1 < 1 or y2 - y1 < 1:
            return
            
        region = self.screenshot.crop((x1, y1, x2, y2))
        
        # Scale up small regions for better visibility
        if region.width < 100 or region.height < 100:
            scale = min(100 / region.width, 100 / region.height)
            new_size = (int(region.width * scale), int(region.height * scale))
            region = region.resize(new_size, Image.LANCZOS)
        
        preview_image = ImageTk.PhotoImage(region)
        self.preview_label.configure(image=preview_image)
        self.preview_label.image = preview_image  # Keep a reference
        
        # Position the preview window
        preview_x = self.roi_window.winfo_x() + x2 + 10
        preview_y = self.roi_window.winfo_y() + y1
        self.preview_window.geometry(f"+{preview_x}+{preview_y}")
    
    def update_dimensions_display(self, x1, y1, x2, y2):
        """Update the dimensions display text."""
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        self.canvas.itemconfig(
            self.dimensions_text,
            text=f"Selection: {width}x{height} pixels"
        )
    
    def on_button_press(self, event):
        """Handle mouse button press to start ROI selection."""
        # Save the starting position
        self.start_x = event.x
        self.start_y = event.y
        
        # Create a rectangle if it doesn't exist
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_move_press(self, event):
        """Handle mouse movement while button is pressed to resize ROI rectangle."""
        cur_x, cur_y = event.x, event.y
        
        # Update the rectangle
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        
        # Update preview and dimensions
        self.show_preview(self.start_x, self.start_y, cur_x, cur_y)
        self.update_dimensions_display(self.start_x, self.start_y, cur_x, cur_y)
    
    def on_button_release(self, event):
        """Handle mouse button release to update selection."""
        end_x, end_y = event.x, event.y
        
        # Ensure coordinates are ordered correctly
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        width = x2 - x1
        height = y2 - y1
        
        # Show warning if selection is too small
        if width < 10 or height < 10:
            messagebox.showwarning(
                "Small Selection",
                "Selection is smaller than recommended (10x10 pixels).\nPlease make a larger selection or press Enter to confirm anyway."
            )
    
    def on_confirm(self):
        """Handle confirmation of ROI selection."""
        if not self.rect:
            return
            
        coords = self.canvas.coords(self.rect)
        if not coords:
            return
            
        x1, y1, x2, y2 = coords
        
        # Calculate ROI
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Call the callback with the ROI
        self.callback((int(x), int(y), int(width), int(height)))
        
        # Clean up
        if self.preview_window:
            self.preview_window.destroy()
        self.roi_window.destroy()
    
    def on_cancel(self):
        """Handle cancel button click."""
        if self.preview_window:
            self.preview_window.destroy()
        self.roi_window.destroy()


class DatasetCollectorTool:
    """Tool for collecting and labeling image datasets for ML training."""
    
    def __init__(
        self, 
        master: tk.Tk, 
        logger: logging.Logger, 
        initial_roi: Optional[Tuple[int, int, int, int]] = None
    ):
        """Initialize the dataset collector tool.
        
        Args:
            master: The root Tkinter window.
            logger: Logger instance for logging messages.
            initial_roi: Optional initial ROI (x, y, width, height).
        """
        self.master = master
        self.logger = logger
        
        # Set default ROI if not provided
        self.roi = initial_roi if initial_roi else (0, 0, 50, 50)
        
        # Set default directories
        self.base_dir = Path("data/ml_training_data")
        self.unsorted_dir = self.base_dir / "unsorted"
        self.active_dir = self.base_dir / "active"
        self.inactive_dir = self.base_dir / "inactive"
        self.other_dir = self.base_dir / "other"
        
        # Ensure directories exist
        for directory in [self.unsorted_dir, self.active_dir, self.inactive_dir, self.other_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set default filename prefix
        self.filename_prefix = "sprint_"
        
        # Counter for captured images
        self.capture_counter = 0
        
        # Currently displayed image
        self.current_image_path = None
        self.current_image = None
        self.current_image_tk = None
        
        # List of unsorted images
        self.unsorted_images = []
        self.unsorted_index = -1
        
        # Set up the UI
        self.setup_ui()
        
        # Update the image list and UI
        self.update_image_list()
        self.update_target_dir_label()
        
        # Log initialization
        self.logger.info("Dataset collector tool initialized")
    
    def setup_ui(self):
        """Set up the user interface."""
        self.master.title("Dataset Collector Tool")
        self.master.geometry("1000x800")
        self.master.minsize(800, 600)
        
        # Create a main frame with padding
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create two columns: left for controls, right for image preview
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- ROI Configuration Section ---
        roi_frame = ttk.LabelFrame(left_frame, text="ROI Configuration", padding="10")
        roi_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ROI entry fields
        roi_fields_frame = ttk.Frame(roi_frame)
        roi_fields_frame.pack(fill=tk.X)
        
        # X Position
        ttk.Label(roi_fields_frame, text="X:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.roi_x_var = tk.IntVar(value=self.roi[0])
        x_spinbox = ttk.Spinbox(
            roi_fields_frame, 
            from_=0, 
            to=3000, 
            textvariable=self.roi_x_var, 
            width=5
        )
        x_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Y Position
        ttk.Label(roi_fields_frame, text="Y:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.roi_y_var = tk.IntVar(value=self.roi[1])
        y_spinbox = ttk.Spinbox(
            roi_fields_frame, 
            from_=0, 
            to=3000, 
            textvariable=self.roi_y_var, 
            width=5
        )
        y_spinbox.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Width
        ttk.Label(roi_fields_frame, text="Width:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.roi_width_var = tk.IntVar(value=self.roi[2])
        width_spinbox = ttk.Spinbox(
            roi_fields_frame, 
            from_=1, 
            to=500, 
            textvariable=self.roi_width_var, 
            width=5
        )
        width_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Height
        ttk.Label(roi_fields_frame, text="Height:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.roi_height_var = tk.IntVar(value=self.roi[3])
        height_spinbox = ttk.Spinbox(
            roi_fields_frame, 
            from_=1, 
            to=500, 
            textvariable=self.roi_height_var, 
            width=5
        )
        height_spinbox.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Select ROI button
        select_roi_button = ttk.Button(
            roi_frame, 
            text="Select ROI from Screen", 
            command=self.select_roi_visual
        )
        select_roi_button.pack(fill=tk.X, pady=(5, 0))
        
        # --- Capture Controls Section ---
        capture_frame = ttk.LabelFrame(left_frame, text="Capture Controls", padding="10")
        capture_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Target directory
        target_dir_frame = ttk.Frame(capture_frame)
        target_dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(target_dir_frame, text="Target Directory:").pack(side=tk.LEFT)
        self.target_dir_label = ttk.Label(target_dir_frame, text="")
        self.target_dir_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Set target directory button
        set_dir_button = ttk.Button(
            capture_frame, 
            text="Set Target Directory", 
            command=self.set_target_directory
        )
        set_dir_button.pack(fill=tk.X, pady=(0, 5))
        
        # Filename prefix
        prefix_frame = ttk.Frame(capture_frame)
        prefix_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(prefix_frame, text="Filename Prefix:").pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar(value=self.filename_prefix)
        prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var)
        prefix_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Capture button
        capture_button = ttk.Button(
            capture_frame, 
            text="Capture ROI", 
            command=self.capture_roi
        )
        capture_button.pack(fill=tk.X, pady=(0, 0))
        
        # --- Image Navigation Section ---
        nav_frame = ttk.LabelFrame(left_frame, text="Image Navigation", padding="10")
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.pack(fill=tk.X)
        
        prev_button = ttk.Button(
            nav_buttons_frame,
            text="Previous",
            command=self.previous_image
        )
        prev_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        next_button = ttk.Button(
            nav_buttons_frame,
            text="Next",
            command=self.next_image
        )
        next_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Image counter
        self.image_counter_var = tk.StringVar(value="No images")
        counter_label = ttk.Label(nav_frame, textvariable=self.image_counter_var)
        counter_label.pack(fill=tk.X, pady=(5, 0))
        
        # --- Labeling Section ---
        labeling_frame = ttk.LabelFrame(left_frame, text="Image Labeling", padding="10")
        labeling_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Label selection
        self.label_var = tk.StringVar(value="Sprint Active")
        
        active_radio = ttk.Radiobutton(
            labeling_frame,
            text="Sprint Active",
            variable=self.label_var,
            value="Sprint Active"
        )
        active_radio.pack(anchor=tk.W, pady=(0, 2))
        
        inactive_radio = ttk.Radiobutton(
            labeling_frame,
            text="Sprint Inactive",
            variable=self.label_var,
            value="Sprint Inactive"
        )
        inactive_radio.pack(anchor=tk.W, pady=(0, 2))
        
        other_radio = ttk.Radiobutton(
            labeling_frame,
            text="Other/Background",
            variable=self.label_var,
            value="Other/Background"
        )
        other_radio.pack(anchor=tk.W, pady=(0, 5))
        
        # Save labeled image button
        save_labeled_button = ttk.Button(
            labeling_frame,
            text="Save Labeled Image",
            command=self.save_labeled_image
        )
        save_labeled_button.pack(fill=tk.X)
        
        # --- Augmentation Section ---
        augment_frame = ttk.LabelFrame(left_frame, text="Augmentation Options", padding="10")
        augment_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Augmentation options
        self.augment_brightness_var = tk.BooleanVar(value=True)
        brightness_check = ttk.Checkbutton(
            augment_frame,
            text="Adjust Brightness/Contrast",
            variable=self.augment_brightness_var
        )
        brightness_check.pack(anchor=tk.W, pady=(0, 2))
        
        self.augment_rotation_var = tk.BooleanVar(value=True)
        rotation_check = ttk.Checkbutton(
            augment_frame,
            text="Minor Rotations",
            variable=self.augment_rotation_var
        )
        rotation_check.pack(anchor=tk.W, pady=(0, 2))
        
        self.augment_scaling_var = tk.BooleanVar(value=True)
        scaling_check = ttk.Checkbutton(
            augment_frame,
            text="Slight Scaling",
            variable=self.augment_scaling_var
        )
        scaling_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Augment button
        augment_button = ttk.Button(
            augment_frame,
            text="Augment Current Image",
            command=self.augment_current_image
        )
        augment_button.pack(fill=tk.X)
        
        # --- Export Section ---
        export_frame = ttk.LabelFrame(left_frame, text="Export", padding="10")
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export manifest button
        export_button = ttk.Button(
            export_frame,
            text="Export Dataset Manifest (CSV)",
            command=self.export_manifest
        )
        export_button.pack(fill=tk.X)
        
        # --- Image Preview Section ---
        preview_frame = ttk.LabelFrame(right_frame, text="Image Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for image display
        self.canvas = tk.Canvas(preview_frame, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add tooltips
        Tooltip(select_roi_button, "Capture ROI visually by selecting an area on the screen")
        Tooltip(capture_button, "Capture the current ROI from the screen")
        Tooltip(save_labeled_button, "Save current image with selected label")
        Tooltip(augment_button, "Create augmented versions of the current image")
        Tooltip(export_button, "Create a CSV file with image paths and labels")
    
    def select_roi_visual(self):
        """Open a fullscreen window to visually select ROI."""
        # Minimize the main window
        self.master.iconify()
        
        # Create a delay to give time for the window to minimize
        self.master.after(500, lambda: ROISelector(self.master, self.set_roi_from_selector))
    
    def set_roi_from_selector(self, roi):
        """Set ROI from the visual selector.
        
        Args:
            roi: Tuple of (x, y, width, height).
        """
        # Set the ROI values
        self.roi_x_var.set(roi[0])
        self.roi_y_var.set(roi[1])
        self.roi_width_var.set(roi[2])
        self.roi_height_var.set(roi[3])
        
        # Update the stored ROI
        self.roi = roi
        
        # Restore the main window
        self.master.deiconify()
        
        # Log the ROI selection
        self.logger.info(f"ROI selected visually: {roi}")
    
    def set_target_directory(self):
        """Open a dialog to set the target directory."""
        directory = filedialog.askdirectory(
            initialdir=str(self.base_dir),
            title="Select Target Directory"
        )
        
        if directory:
            # Set the new base directory
            self.base_dir = Path(directory)
            
            # Update subdirectories
            self.unsorted_dir = self.base_dir / "unsorted"
            self.active_dir = self.base_dir / "active"
            self.inactive_dir = self.base_dir / "inactive"
            self.other_dir = self.base_dir / "other"
            
            # Ensure directories exist
            for dir_path in [self.unsorted_dir, self.active_dir, self.inactive_dir, self.other_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Update the UI
            self.update_target_dir_label()
            self.update_image_list()
            
            # Log the directory change
            self.logger.info(f"Target directory set to: {self.base_dir}")
    
    def update_target_dir_label(self):
        """Update the target directory label in the UI."""
        self.target_dir_label.config(text=str(self.unsorted_dir))
    
    def capture_roi(self):
        """Capture the current ROI from the screen."""
        try:
            # Get ROI coordinates from UI
            x = self.roi_x_var.get()
            y = self.roi_y_var.get()
            width = self.roi_width_var.get()
            height = self.roi_height_var.get()
            
            # Capture the ROI from the screen
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.prefix_var.get()}{timestamp}_{self.capture_counter}.png"
            filepath = self.unsorted_dir / filename
            
            # Save the image
            screenshot.save(filepath)
            
            # Increment the counter
            self.capture_counter += 1
            
            # Update the image list and display the captured image
            self.update_image_list()
            self.display_image(filepath)
            
            # Log the capture
            self.logger.info(f"Captured ROI to: {filepath}")
            
            # Show success message
            messagebox.showinfo("Success", f"ROI captured and saved to: {filepath}")
            
        except Exception as e:
            # Log the error
            self.logger.error(f"Error capturing ROI: {e}")
            
            # Show error message
            messagebox.showerror("Error", f"Failed to capture ROI: {e}")
    
    def update_image_list(self):
        """Update the list of unsorted images."""
        # Get all PNG files in the unsorted directory
        self.unsorted_images = sorted(list(self.unsorted_dir.glob("*.png")))
        
        # Update the image counter
        if self.unsorted_images:
            self.unsorted_index = 0
            self.image_counter_var.set(f"Image 1 of {len(self.unsorted_images)}")
            
            # Display the first image
            if self.unsorted_images:
                self.display_image(self.unsorted_images[0])
        else:
            self.unsorted_index = -1
            self.image_counter_var.set("No images")
            
            # Clear the canvas
            self.canvas.delete("all")
            self.current_image_path = None
            self.current_image = None
            self.current_image_tk = None
    
    def display_image(self, image_path):
        """Display an image on the canvas.
        
        Args:
            image_path: Path to the image to display.
        """
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Store the current image
            self.current_image_path = image_path
            self.current_image = image
            
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Resize the image to fit the canvas (if necessary)
            if canvas_width > 1 and canvas_height > 1:  # Ensure canvas has been drawn
                # Calculate the aspect ratio
                img_width, img_height = image.size
                img_aspect = img_width / img_height
                canvas_aspect = canvas_width / canvas_height
                
                if img_aspect > canvas_aspect:
                    # Image is wider than canvas
                    new_width = canvas_width
                    new_height = int(canvas_width / img_aspect)
                else:
                    # Image is taller than canvas
                    new_height = canvas_height
                    new_width = int(canvas_height * img_aspect)
                
                # Resize the image
                resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            else:
                # Canvas not yet drawn, use original size
                resized_image = image
            
            # Convert to PhotoImage for Tkinter
            self.current_image_tk = ImageTk.PhotoImage(resized_image)
            
            # Clear the canvas
            self.canvas.delete("all")
            
            # Display the image
            self.canvas.create_image(
                canvas_width // 2, 
                canvas_height // 2, 
                image=self.current_image_tk,
                anchor=tk.CENTER
            )
            
            # Update the image counter
            if self.unsorted_images and self.unsorted_index >= 0:
                image_index = self.unsorted_images.index(Path(image_path))
                self.unsorted_index = image_index
                self.image_counter_var.set(f"Image {image_index + 1} of {len(self.unsorted_images)}")
            
            # Log the display
            self.logger.info(f"Displaying image: {image_path}")
            
        except Exception as e:
            # Log the error
            self.logger.error(f"Error displaying image: {e}")
            
            # Show error message
            messagebox.showerror("Error", f"Failed to display image: {e}")
    
    def next_image(self):
        """Display the next unsorted image."""
        if not self.unsorted_images:
            return
        
        if self.unsorted_index < len(self.unsorted_images) - 1:
            self.unsorted_index += 1
            self.display_image(self.unsorted_images[self.unsorted_index])
    
    def previous_image(self):
        """Display the previous unsorted image."""
        if not self.unsorted_images:
            return
        
        if self.unsorted_index > 0:
            self.unsorted_index -= 1
            self.display_image(self.unsorted_images[self.unsorted_index])
    
    def save_labeled_image(self):
        """Save the current image to the appropriate labeled directory."""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "No image selected")
            return
        
        try:
            # Determine the target directory based on the selected label
            label = self.label_var.get()
            if label == "Sprint Active":
                target_dir = self.active_dir
            elif label == "Sprint Inactive":
                target_dir = self.inactive_dir
            else:  # Other/Background
                target_dir = self.other_dir
            
            # Get the original filename
            filename = Path(self.current_image_path).name
            
            # Create the target path
            target_path = target_dir / filename
            
            # Copy the image to the target directory
            self.current_image.save(target_path)
            
            # Remove the image from the unsorted directory
            Path(self.current_image_path).unlink()
            
            # Update the image list
            self.update_image_list()
            
            # Log the labeling
            self.logger.info(f"Image labeled as '{label}' and moved to: {target_path}")
            
            # Show success message
            messagebox.showinfo("Success", f"Image labeled as '{label}' and saved to: {target_path}")
            
        except Exception as e:
            # Log the error
            self.logger.error(f"Error labeling image: {e}")
            
            # Show error message
            messagebox.showerror("Error", f"Failed to label image: {e}")
    
    def augment_current_image(self):
        """Apply augmentations to the current image."""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "No image selected")
            return
        
        try:
            # Load the original image
            image = Image.open(self.current_image_path)
            
            # Get the original filename and directory
            filename = Path(self.current_image_path).name
            file_stem = Path(filename).stem
            file_suffix = Path(filename).suffix
            parent_dir = Path(self.current_image_path).parent
            
            # Counter for augmented images
            aug_count = 0
            
            # Apply brightness/contrast augmentation
            if self.augment_brightness_var.get():
                # Brighter
                enhancer = ImageEnhance.Brightness(image)
                bright_img = enhancer.enhance(1.2)  # +20% brightness
                bright_path = parent_dir / f"{file_stem}_aug_bright{file_suffix}"
                bright_img.save(bright_path)
                aug_count += 1
                
                # Darker
                dark_img = enhancer.enhance(0.8)  # -20% brightness
                dark_path = parent_dir / f"{file_stem}_aug_dark{file_suffix}"
                dark_img.save(dark_path)
                aug_count += 1
                
                # More contrast
                enhancer = ImageEnhance.Contrast(image)
                contrast_img = enhancer.enhance(1.2)  # +20% contrast
                contrast_path = parent_dir / f"{file_stem}_aug_contrast{file_suffix}"
                contrast_img.save(contrast_path)
                aug_count += 1
            
            # Apply rotation augmentation
            if self.augment_rotation_var.get():
                # Rotate clockwise 5 degrees
                cw_img = image.rotate(-5, resample=Image.BICUBIC, expand=False)
                cw_path = parent_dir / f"{file_stem}_aug_rotcw{file_suffix}"
                cw_img.save(cw_path)
                aug_count += 1
                
                # Rotate counter-clockwise 5 degrees
                ccw_img = image.rotate(5, resample=Image.BICUBIC, expand=False)
                ccw_path = parent_dir / f"{file_stem}_aug_rotccw{file_suffix}"
                ccw_img.save(ccw_path)
                aug_count += 1
            
            # Apply scaling augmentation
            if self.augment_scaling_var.get():
                # Get original size
                width, height = image.size
                
                # Scale up 10%
                up_width = int(width * 1.1)
                up_height = int(height * 1.1)
                up_img = image.resize((up_width, up_height), Image.LANCZOS)
                # Crop to original size from center
                left = (up_width - width) // 2
                top = (up_height - height) // 2
                up_img = up_img.crop((left, top, left + width, top + height))
                up_path = parent_dir / f"{file_stem}_aug_scaleup{file_suffix}"
                up_img.save(up_path)
                aug_count += 1
                
                # Scale down 10%
                down_width = int(width * 0.9)
                down_height = int(height * 0.9)
                down_img = image.resize((down_width, down_height), Image.LANCZOS)
                # Paste onto a blank image of original size
                new_img = Image.new("RGB", (width, height), (0, 0, 0))
                left = (width - down_width) // 2
                top = (height - down_height) // 2
                new_img.paste(down_img, (left, top))
                down_path = parent_dir / f"{file_stem}_aug_scaledown{file_suffix}"
                new_img.save(down_path)
                aug_count += 1
            
            # Update the image list
            self.update_image_list()
            
            # Log the augmentation
            self.logger.info(f"Created {aug_count} augmented versions of: {self.current_image_path}")
            
            # Show success message
            messagebox.showinfo("Success", f"Created {aug_count} augmented versions of the image")
            
        except Exception as e:
            # Log the error
            self.logger.error(f"Error augmenting image: {e}")
            
            # Show error message
            messagebox.showerror("Error", f"Failed to augment image: {e}")
    
    def export_manifest(self):
        """Create a CSV manifest of the labeled dataset."""
        try:
            # Create the manifest file path
            manifest_path = self.base_dir / "dataset_manifest.csv"
            
            # Open the CSV file for writing
            with open(manifest_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write the header
                writer.writerow(['filepath', 'label'])
                
                # Write the active images
                for img_path in self.active_dir.glob("*.png"):
                    relative_path = img_path.relative_to(self.base_dir)
                    writer.writerow([str(relative_path), 'active'])
                
                # Write the inactive images
                for img_path in self.inactive_dir.glob("*.png"):
                    relative_path = img_path.relative_to(self.base_dir)
                    writer.writerow([str(relative_path), 'inactive'])
                
                # Write the other images
                for img_path in self.other_dir.glob("*.png"):
                    relative_path = img_path.relative_to(self.base_dir)
                    writer.writerow([str(relative_path), 'other'])
            
            # Log the export
            self.logger.info(f"Exported dataset manifest to: {manifest_path}")
            
            # Show success message
            messagebox.showinfo("Success", f"Dataset manifest exported to: {manifest_path}")
            
        except Exception as e:
            # Log the error
            self.logger.error(f"Error exporting manifest: {e}")
            
            # Show error message
            messagebox.showerror("Error", f"Failed to export manifest: {e}")


if __name__ == "__main__":
    # Set up logging
    logger = setup_logger("dataset_collector")
    
    # Create the main window
    root = tk.Tk()
    
    # Create a dummy initial ROI
    initial_roi = (100, 100, 50, 50)
    
    # Create the dataset collector tool
    collector = DatasetCollectorTool(root, logger, initial_roi)
    
    # Run the main loop
    root.mainloop() 