"""System tray interface for the DAOC Sprint Manager."""
import logging
import pystray
from PIL import Image, ImageDraw

from daoc_sprint_manager.core.sprint_manager import SprintManager

logger = logging.getLogger(__name__)

class SystemTrayUI:
    """System tray interface for the sprint manager."""

    def __init__(self, sprint_manager: SprintManager):
        """Initialize the system tray UI.

        Args:
            sprint_manager: Sprint manager instance
        """
        self.sprint_manager = sprint_manager
        self.icon = self._create_icon()

    def _create_icon(self):
        """Create the system tray icon."""
        width, height = self.sprint_manager.settings.icon_size
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, width-1, height-1], outline='black')

        return pystray.Icon(
            'DAOC Sprint Manager',
            image,
            menu=self._create_menu()
        )

    def _create_menu(self):
        """Create the system tray menu."""
        return pystray.Menu(
            pystray.MenuItem(
                'Toggle Sprint Detection',
                self._toggle_detection,
                default=True  # Make it the default action on left-click 
            ),
            pystray.MenuItem(
                'Exit',
                self._exit_app
            )
        )

    def _toggle_detection(self):
        """Toggle sprint detection."""
        is_active = self.sprint_manager.toggle()
        status = "active" if is_active else "inactive"
        self.icon.title = f"Sprint Detection: {status}"

    def _exit_app(self):
        """Exit the application."""
        logger.info("Exiting application")
        self.sprint_manager.stop()
        self.icon.stop()

    def run(self):
        """Run the system tray application."""
        logger.info("Starting system tray interface")
        self.icon.run() 