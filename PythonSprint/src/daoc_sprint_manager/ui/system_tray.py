"""System tray interface for the DAOC Sprint Manager."""
import logging
import pystray
from PIL import Image, ImageDraw

from daoc_sprint_manager.core.sprint_manager import SprintManager

logger = logging.getLogger(__name__)

class SystemTrayUI:
    def __init__(self, sprint_manager):
        self.sprint_manager = sprint_manager
        self.icon = self._create_icon()

    def _create_icon(self):
        """Create the system tray icon."""
        width, height = self.sprint_manager.settings.icon_size
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, width-1, height-1], outline="black")
        return pystray.Icon("DAOC Sprint Manager", image, menu=self._create_menu())

    def _create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Toggle Sprint Detection", self._toggle_detection),
            pystray.MenuItem("Exit", self._exit_app)
        )

    def _toggle_detection(self):
        is_active = self.sprint_manager.toggle()
        status = "active" if is_active else "inactive"
        self.icon.title = f"Sprint Detection: {status}"

    def _exit_app(self):
        logger.info("Exiting application")
        self.sprint_manager.stop()
        self.icon.stop()

    def run(self):
        logger.info("Starting system tray interface")
        self.icon.run()
