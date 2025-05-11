"""
UI for the Data Collection Module.

This module provides a simple UI for capturing and managing training data
for machine learning models.
"""

import os
import sys
import time
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import shutil

# Add parent directory to path to find other modules
parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from daoc_sprint_manager.training.data_collector import DataCollector

class TextHandler(logging.Handler):
    """Handler for redirecting logging output to a tkinter Text widget."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.see('end')
        self.text_widget.update()

class DataCollectorUI:
    """UI for managing data collection and labeling."""
    
    def __init__(self, root):
        """Initialize the UI."""
        self.root = root
        self.root.title("Sprint Data Collector")
        
        # Initialize data collector
        self.data_collector = DataCollector()
        
        # Image navigation state
        self.current_image_path = None
        self.unsorted_images = []
        self.current_image_index = -1
        self.review_mode = False
        self.current_review_dir = None
        
        # Batch processing state
        self.batch_size = tk.StringVar(value="10")
        self.batch_active = False
        self.batch_remaining = 0
        self.batch_label = None
        
        # Set up directories
        self.unsorted_dir = self.data_collector.unsorted_dir
        self.active_dir = self.data_collector.active_dir
        self.inactive_dir = self.data_collector.inactive_dir
        self.other_dir = self.data_collector.other_dir
        
        # Create main frames
        self.setup_frames()
        self.setup_session_controls()
        self.setup_capture_controls()
        self.setup_image_navigation()
        self.setup_batch_controls()
        self.setup_review_controls()
        self.setup_logging()
        
        # Configure keyboard shortcuts
        self.setup_shortcuts()
        
        # Load initial images
        self.refresh_image_list()
        
    def setup_frames(self):
        """Set up the main UI frames."""
        # Top frame for session controls
        self.session_frame = ttk.LabelFrame(self.root, text="Session Control", padding=5)
        self.session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Middle frame for capture controls
        self.capture_frame = ttk.LabelFrame(self.root, text="Capture Control", padding=5)
        self.capture_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame for image navigation and labeling
        self.nav_frame = ttk.LabelFrame(self.root, text="Image Navigation", padding=5)
        self.nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Bottom frame for logging
        self.log_frame = ttk.LabelFrame(self.root, text="Log", padding=5)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_session_controls(self):
        """Set up controls for managing sessions."""
        # Session name entry
        ttk.Label(self.session_frame, text="Session Name:").pack(side=tk.LEFT, padx=5)
        self.session_name = tk.StringVar()
        ttk.Entry(self.session_frame, textvariable=self.session_name).pack(side=tk.LEFT, padx=5)
        
        # New session button
        ttk.Button(
            self.session_frame,
            text="New Session",
            command=self.new_session
        ).pack(side=tk.LEFT, padx=5)
        
        # Load session button
        ttk.Button(
            self.session_frame,
            text="Load Session",
            command=self.load_session
        ).pack(side=tk.LEFT, padx=5)
        
        # Extract dataset button
        ttk.Button(
            self.session_frame,
            text="Extract Dataset",
            command=self.extract_dataset
        ).pack(side=tk.RIGHT, padx=5)
        
    def setup_capture_controls(self):
        """Set up controls for capturing images."""
        # ROI selection
        ttk.Button(
            self.capture_frame,
            text="Select ROI",
            command=self.select_roi
        ).pack(side=tk.LEFT, padx=5)
        
        # Single capture
        ttk.Button(
            self.capture_frame,
            text="Capture Single",
            command=self.capture_single
        ).pack(side=tk.LEFT, padx=5)
        
        # Sequence capture
        ttk.Button(
            self.capture_frame,
            text="Start Sequence",
            command=self.toggle_sequence
        ).pack(side=tk.LEFT, padx=5)
        
        # Capture interval
        ttk.Label(self.capture_frame, text="Interval (s):").pack(side=tk.LEFT, padx=5)
        self.interval = tk.StringVar(value="0.5")
        ttk.Entry(
            self.capture_frame,
            textvariable=self.interval,
            width=5
        ).pack(side=tk.LEFT, padx=5)
        
    def setup_image_navigation(self):
        """Set up controls for navigating and labeling images."""
        # Navigation buttons frame
        nav_buttons = ttk.Frame(self.nav_frame)
        nav_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        # Previous/Next buttons
        ttk.Button(
            nav_buttons,
            text="Previous (←)",
            command=lambda: self.navigate_images(-1)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            nav_buttons,
            text="Next (→)",
            command=lambda: self.navigate_images(1)
        ).pack(side=tk.LEFT, padx=5)
        
        # Image counter
        self.image_counter = ttk.Label(nav_buttons, text="0/0 images")
        self.image_counter.pack(side=tk.LEFT, padx=20)
        
        # Label selection
        ttk.Label(nav_buttons, text="Label:").pack(side=tk.LEFT, padx=5)
        self.label_var = tk.StringVar()
        self.label_combo = ttk.Combobox(
            nav_buttons,
            textvariable=self.label_var,
            values=["sprint_active", "sprint_inactive", "other"],
            state="readonly",
            width=15
        )
        self.label_combo.pack(side=tk.LEFT, padx=5)
        
        # Save label button
        ttk.Button(
            nav_buttons,
            text="Save Label (Space)",
            command=self.save_labeled_image
        ).pack(side=tk.LEFT, padx=5)
        
        # Image preview frame
        preview_frame = ttk.Frame(self.nav_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image preview label
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
    def setup_batch_controls(self):
        """Set up controls for batch processing."""
        batch_frame = ttk.LabelFrame(self.nav_frame, text="Batch Processing", padding=5)
        batch_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Batch size entry
        ttk.Label(batch_frame, text="Batch Size:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(
            batch_frame,
            textvariable=self.batch_size,
            width=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Batch processing buttons
        ttk.Button(
            batch_frame,
            text="Start Active Batch (Ctrl+1)",
            command=lambda: self.start_batch('sprint_active')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            batch_frame,
            text="Start Inactive Batch (Ctrl+2)",
            command=lambda: self.start_batch('sprint_inactive')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            batch_frame,
            text="Start Other Batch (Ctrl+3)",
            command=lambda: self.start_batch('other')
        ).pack(side=tk.LEFT, padx=5)
        
        # Cancel batch button
        ttk.Button(
            batch_frame,
            text="Cancel Batch (Esc)",
            command=self.cancel_batch
        ).pack(side=tk.RIGHT, padx=5)
        
    def setup_review_controls(self):
        """Set up controls for reviewing labeled images."""
        review_frame = ttk.LabelFrame(self.nav_frame, text="Review & Verification", padding=5)
        review_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Review mode buttons
        ttk.Button(
            review_frame,
            text="Review Active (Alt+1)",
            command=lambda: self.start_review('sprint_active')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            review_frame,
            text="Review Inactive (Alt+2)",
            command=lambda: self.start_review('sprint_inactive')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            review_frame,
            text="Review Other (Alt+3)",
            command=lambda: self.start_review('other')
        ).pack(side=tk.LEFT, padx=5)
        
        # Exit review button
        ttk.Button(
            review_frame,
            text="Exit Review (Alt+X)",
            command=self.exit_review
        ).pack(side=tk.RIGHT, padx=5)
        
    def setup_logging(self):
        """Set up logging text widget."""
        # Create text widget for logging
        self.log_text = tk.Text(self.log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text widget
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Set up logging handler
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        
        # Get logger and add handler
        self.logger = logging.getLogger("DataCollector")
        self.logger.addHandler(handler)
        
    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        self.root.bind('<Left>', lambda e: self.navigate_images(-1))
        self.root.bind('<Right>', lambda e: self.navigate_images(1))
        self.root.bind('<space>', lambda e: self.save_labeled_image())
        self.root.bind('1', lambda e: self.quick_label('sprint_active'))
        self.root.bind('2', lambda e: self.quick_label('sprint_inactive'))
        self.root.bind('3', lambda e: self.quick_label('other'))
        
        # Batch processing shortcuts
        self.root.bind('<Control-Key-1>', lambda e: self.start_batch('sprint_active'))
        self.root.bind('<Control-Key-2>', lambda e: self.start_batch('sprint_inactive'))
        self.root.bind('<Control-Key-3>', lambda e: self.start_batch('other'))
        self.root.bind('<Escape>', lambda e: self.cancel_batch())
        
        # Review mode shortcuts
        self.root.bind('<Alt-Key-1>', lambda e: self.start_review('sprint_active'))
        self.root.bind('<Alt-Key-2>', lambda e: self.start_review('sprint_inactive'))
        self.root.bind('<Alt-Key-3>', lambda e: self.start_review('other'))
        self.root.bind('<Alt-Key-x>', lambda e: self.exit_review())
        
    def quick_label(self, label):
        """Quickly set label and save."""
        self.label_var.set(label)
        self.save_labeled_image()
        
    def refresh_image_list(self):
        """Refresh the list of unsorted images."""
        self.unsorted_images = []
        if self.unsorted_dir.exists():
            self.unsorted_images = [
                p for p in self.unsorted_dir.glob("*.png")
                if p.is_file()
            ]
            self.unsorted_images.sort()
        
        # Reset navigation state
        self.current_image_index = 0 if self.unsorted_images else -1
        self.update_image_counter()
        self.display_current_image()
        
    def update_image_counter(self):
        """Update the image counter display."""
        total = len(self.unsorted_images)
        current = self.current_image_index + 1 if self.current_image_index >= 0 else 0
        self.image_counter.configure(text=f"Unsorted Image {current} of {total}")
        
    def navigate_images(self, direction):
        """Navigate through the unsorted images list.
        
        Args:
            direction: 1 for next, -1 for previous
        """
        if not self.unsorted_images:
            return
            
        new_index = self.current_image_index + direction
        if 0 <= new_index < len(self.unsorted_images):
            self.current_image_index = new_index
            self.update_image_counter()
            self.display_current_image()
            
    def display_current_image(self):
        """Display the current image in the preview area."""
        if self.current_image_index < 0 or not self.unsorted_images:
            return
            
        try:
            image_path = self.unsorted_images[self.current_image_index]
            image = Image.open(image_path)
            
            # Calculate scaling to fit in preview area
            max_size = (400, 400)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update preview label
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo  # Keep reference
            
            self.current_image_path = image_path
            
        except Exception as e:
            self.logger.error(f"Error displaying image: {e}")
            
    def save_labeled_image(self):
        """Save the current image with its label and move it to the appropriate directory."""
        if not self.unsorted_images or self.current_image_index < 0:
            messagebox.showwarning("No Image", "No image is currently selected in the preview.")
            return
            
        label = self.label_var.get()
        if not label:
            messagebox.showwarning("No Label", "Please select a label for the image.")
            return
            
        # Map label to target directory
        label_dir_map = {
            "sprint_active": self.active_dir,
            "sprint_inactive": self.inactive_dir,
            "other": self.other_dir
        }
        
        target_dir = label_dir_map.get(label)
        if not target_dir:
            messagebox.showerror("Error", f"Invalid label: {label}")
            return
            
        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get source and destination paths
            source_path = self.unsorted_images[self.current_image_index]
            dest_path = target_dir / source_path.name
            
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            
            # Log the operation
            self.logger.info(f"Moved {source_path.name} to {label} category")
            
            # Remove from unsorted list and update display
            self.unsorted_images.pop(self.current_image_index)
            
            # Adjust index if we removed the last image
            if self.current_image_index >= len(self.unsorted_images):
                self.current_image_index = max(len(self.unsorted_images) - 1, 0)
                
            # Update UI
            self.update_image_counter()
            self.display_current_image()
            
            # Show success message
            messagebox.showinfo("Image Labeled", f"Image moved to '{label}' category.")
            
        except FileNotFoundError:
            messagebox.showerror("Error", "The image file could not be found.")
            self.refresh_image_list()  # Refresh to ensure our list is accurate
            
        except PermissionError:
            messagebox.showerror("Error", "Permission denied when trying to move the file.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while moving the file: {str(e)}")
            self.logger.exception("Error during image labeling")
            
    def new_session(self):
        """Create a new data collection session."""
        name = self.session_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a session name")
            return
            
        try:
            session = self.data_collector.new_session(name)
            self.logger.info(f"Created new session: {name}")
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            
    def load_session(self):
        """Load an existing data collection session."""
        # TODO: Add session selection dialog
        self.logger.info("Session loading not implemented yet")
        
    def select_roi(self):
        """Open ROI selection window."""
        # TODO: Implement ROI selection
        self.logger.info("ROI selection not implemented yet")
        
    def capture_single(self):
        """Capture a single screenshot."""
        # TODO: Implement single capture
        self.logger.info("Single capture not implemented yet")
        
    def toggle_sequence(self):
        """Toggle sequence capture on/off."""
        # TODO: Implement sequence capture
        self.logger.info("Sequence capture not implemented yet")
        
    def extract_dataset(self):
        """Extract labeled dataset for training."""
        try:
            counts = self.data_collector.extract_dataset("dataset")
            messagebox.showinfo(
                "Success",
                f"Dataset extracted with {counts['total']} images:\n"
                f"Active: {counts['sprint_active']}\n"
                f"Inactive: {counts['sprint_inactive']}\n"
                f"Other: {counts['other']}\n"
                f"Train: {counts['train']}, Val: {counts['val']}, Test: {counts['test']}"
            )
        except Exception as e:
            self.logger.error(f"Error extracting dataset: {e}")
            
    def start_batch(self, label):
        """Start batch processing with the specified label."""
        try:
            batch_size = int(self.batch_size.get())
            if batch_size <= 0:
                raise ValueError("Batch size must be positive")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
            
        if not self.unsorted_images:
            messagebox.showinfo("Info", "No unsorted images available")
            return
            
        self.batch_active = True
        self.batch_remaining = min(batch_size, len(self.unsorted_images))
        self.batch_label = label
        
        self.logger.info(f"Starting batch processing: {self.batch_remaining} images as '{label}'")
        self.quick_label(label)  # Process first image
        
    def cancel_batch(self):
        """Cancel the current batch processing."""
        if self.batch_active:
            self.batch_active = False
            self.batch_remaining = 0
            self.batch_label = None
            self.logger.info("Batch processing cancelled")
            
    def start_review(self, label):
        """Start reviewing images with the specified label."""
        label_dirs = {
            'sprint_active': self.active_dir,
            'sprint_inactive': self.inactive_dir,
            'other': self.other_dir
        }
        
        review_dir = label_dirs[label]
        self.review_mode = True
        self.current_review_dir = review_dir
        
        # Load images from the selected category
        self.unsorted_images = sorted(list(review_dir.glob("*.png")))
        self.current_image_index = 0 if self.unsorted_images else -1
        
        if self.unsorted_images:
            self.display_current_image()
            self.logger.info(f"Reviewing {len(self.unsorted_images)} images labeled as '{label}'")
        else:
            messagebox.showinfo("Info", f"No images found with label '{label}'")
            
    def exit_review(self):
        """Exit review mode and return to unsorted images."""
        if self.review_mode:
            self.review_mode = False
            self.current_review_dir = None
            self.refresh_image_list()  # Return to unsorted images
            self.logger.info("Exited review mode")

def main():
    """Run the data collector UI."""
    root = tk.Tk()
    app = DataCollectorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 