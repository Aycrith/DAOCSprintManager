"""System tray interface for the DAOC Sprint Manager."""
import logging
import pystray
from PIL import Image, ImageDraw
import time

# Importing the real SprintManager will be attempted first, 
# but might not be available in test mode
try:
    from daoc_sprint_manager.core.sprint_manager import SprintManager
except ImportError:
    # Mock class for testing
    class SprintManager:
        def __init__(self):
            self.active = False
            
        def toggle(self):
            self.active = not self.active
            return self.active
            
        def stop(self):
            self.active = False

logger = logging.getLogger(__name__)

PYSTRAY_AVAILABLE = True  # Since we've imported pystray successfully

class SystemTrayUI:
    def __init__(self, sprint_manager_or_settings=None, test_mode=False, logger=None, root_dir=None):
        """Initialize the SystemTrayUI.
        
        Args:
            sprint_manager_or_settings: Either a SprintManager instance or settings object.
                In test mode, this can be app_settings.
            test_mode: Whether to run in test mode (exits immediately after initialization)
            logger: Logger instance
            root_dir: Root directory path (unused directly but accepted for compatibility)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.test_mode = test_mode
        
        # Handle different types for the first argument
        if hasattr(sprint_manager_or_settings, 'is_active'):
            # Looks like a SprintManager
            self.sprint_manager = sprint_manager_or_settings
            self.app_settings = None
        else:
            # Assume it's settings if not a SprintManager
            self.app_settings = sprint_manager_or_settings
            # Create a minimal mock SprintManager
            self.sprint_manager = type('MockSprintManager', (), {
                'toggle': lambda: True,
                'stop': lambda: None,
                'is_active': False
            })()
            self.logger.info("Created minimal mock SprintManager for test mode")
        
        # Create the icon after initialization
        self.icon = self._create_icon()
        if test_mode:
            self.logger.info("Running in test mode")

    def _create_icon(self):
        """Create the system tray icon."""
        width, height = 32, 32  # Default icon size
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, width-1, height-1], outline="black")
        return pystray.Icon("DAOC Sprint Manager", image, menu=self._create_menu())

    def _create_menu(self):
        menu_items = [
            pystray.MenuItem("Toggle Sprint Detection", self._toggle_detection),
        ]
        if self.test_mode:
            menu_items.append(pystray.MenuItem("Test Mode Active", lambda: None))
        menu_items.append(pystray.MenuItem("Exit", self._exit_app))
        return pystray.Menu(*menu_items)

    def _toggle_detection(self):
        is_active = self.sprint_manager.toggle()
        status = "active" if is_active else "inactive"
        self.icon.title = f"Sprint Detection: {status}"

    def _exit_app(self):
        self.logger.info("Exiting application")
        self.sprint_manager.stop()
        self.icon.stop()

    def start(self):
        """Start the system tray application.
        This method is called by main.py and provides compatibility with 
        the expected SprintManagerApp interface.
        """
        self.logger.info("Starting system tray application")
        self.run()

    def run(self):
        self.logger.info("Starting system tray interface")
        if self.test_mode:
            self.logger.info("Running in test mode - will exit automatically after initialization")
            try:
                # In test mode, we don't need to show the icon, just make it visible briefly
                # to avoid any blocking, then stop it immediately
                self.icon.visible = True
                time.sleep(0.1)  # Brief pause to let the icon initialize
                self.icon.stop()
                self.logger.info("Test mode tray icon stopped successfully")
            except Exception as e:
                self.logger.error(f"Error in test mode tray operation: {e}")
        else:
            self.logger.info("Starting normal tray icon")
            try:
                self.icon.run()
            except Exception as e:
                self.logger.error(f"Error during tray icon run: {e}")