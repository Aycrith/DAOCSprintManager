"""Unit tests for the SprintManagerApp class.

Tests the system tray application functionality including profile management,
UI interactions, and detection loop behavior.
"""

import logging
import pathlib
import threading
import time
from unittest.mock import MagicMock, patch, PropertyMock, call
import pytest
from typing import Optional, List

from daoc_sprint_manager.data_models import AppSettings, Profile
from daoc_sprint_manager.ui.tray_app import SprintManagerApp, PYSTRAY_AVAILABLE, PYGETWINDOW_AVAILABLE
from daoc_sprint_manager.config_manager import ConfigManager

# Test fixtures and helpers
@pytest.fixture
def mock_logger():
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def mock_config_manager():
    config_manager = MagicMock(spec=ConfigManager)
    # Setup default global settings
    global_settings = AppSettings()
    global_settings.active_profile_id = None
    config_manager.load_settings.return_value = global_settings
    return config_manager

@pytest.fixture
def mock_profile_io_manager():
    with patch('daoc_sprint_manager.ui.tray_app.ProfileIOManager') as mock:
        mock_instance = mock.return_value
        mock_instance.load_profiles.return_value = []
        return mock_instance

@pytest.fixture
def mock_window_manager():
    with patch('daoc_sprint_manager.ui.tray_app.WindowManager') as mock:
        mock_instance = mock.return_value
        mock_instance.find_window.return_value = None
        return mock_instance

@pytest.fixture
def mock_icon_detector():
    with patch('daoc_sprint_manager.ui.tray_app.IconDetector') as mock:
        return mock.return_value

@pytest.fixture
def mock_input_manager():
    with patch('daoc_sprint_manager.ui.tray_app.InputManager') as mock:
        return mock.return_value

@pytest.fixture
def mock_perf_monitor():
    with patch('daoc_sprint_manager.ui.tray_app.PerformanceMonitor') as mock:
        return mock.return_value

@pytest.fixture
def mock_pystray():
    with patch('daoc_sprint_manager.ui.tray_app.pystray') as mock:
        mock.Icon.return_value = MagicMock()
        return mock

@pytest.fixture
def app_settings():
    settings = AppSettings()
    settings.game_window_title = "Test Game"
    settings.detection_method = "template"
    settings.temporal_consistency_frames = 3
    settings.capture_fps = 30
    settings.game_not_found_retry_delay_s = 0.1
    settings.enable_auto_profile_switching = False
    return settings

@pytest.fixture
def root_dir(tmp_path):
    return tmp_path

@pytest.fixture
def tray_app(app_settings, mock_logger, root_dir, mock_config_manager, 
             mock_profile_io_manager, mock_window_manager, mock_icon_detector,
             mock_input_manager, mock_perf_monitor, mock_pystray):
    app = SprintManagerApp(app_settings, mock_logger, root_dir, mock_config_manager)
    return app

class TestSprintManagerApp:
    """Test suite for SprintManagerApp class."""

    def test_initialization(self, tray_app, mock_logger, app_settings):
        """Test proper initialization of SprintManagerApp."""
        assert tray_app.app_settings == app_settings
        assert tray_app.logger == mock_logger
        assert tray_app.status_message == "Initializing..."
        assert not tray_app.stop_event.is_set()
        assert not tray_app.pause_event.is_set()
        assert tray_app.game_not_found_consecutive_count == 0
        assert tray_app.ml_prediction_failure_consecutive_count == 0
        assert not tray_app.was_auto_paused_due_to_game_not_found
        mock_logger.info.assert_called_with("SprintManagerApp initialized.")

    def test_apply_active_profile_settings_no_active_profile(self, tray_app, mock_config_manager, mock_logger):
        """Test applying settings when no active profile is set."""
        global_settings = AppSettings()
        global_settings.active_profile_id = None
        mock_config_manager.load_settings.return_value = global_settings

        tray_app._apply_active_profile_settings()

        assert tray_app.current_profile is None
        assert tray_app.app_settings == global_settings
        mock_logger.info.assert_any_call("No active profile set. Using global settings.")

    def test_apply_active_profile_settings_with_active_profile(self, tray_app, mock_config_manager, mock_profile_io_manager):
        """Test applying settings with an active profile."""
        # Setup test data
        active_profile = Profile(
            profile_id="test-profile-1",
            profile_name="Test Profile",
            app_settings=AppSettings(detection_method="ml")
        )
        global_settings = AppSettings()
        global_settings.active_profile_id = active_profile.profile_id

        mock_config_manager.load_settings.return_value = global_settings
        mock_profile_io_manager.load_profiles.return_value = [active_profile]

        # Apply settings
        tray_app._apply_active_profile_settings()

        # Verify results
        assert tray_app.current_profile == active_profile
        assert tray_app.app_settings == active_profile.app_settings
        assert tray_app.app_settings.active_profile_id == active_profile.profile_id

    def test_update_status(self, tray_app, mock_logger):
        """Test status message updates."""
        test_message = "Test Status"
        tray_app._update_status(test_message)

        assert tray_app.status_message == test_message
        mock_logger.info.assert_called_with(f"Status updated: {test_message}")

    def test_pause_resume_functionality(self, tray_app, mock_logger):
        """Test pause/resume functionality."""
        # Test pause
        tray_app._on_clicked_pause_resume(None, None)
        assert tray_app.pause_event.is_set()
        mock_logger.info.assert_called_with("Application Paused.")

        # Test resume
        tray_app._on_clicked_pause_resume(None, None)
        assert not tray_app.pause_event.is_set()
        mock_logger.info.assert_called_with("Application Resumed.")

    @pytest.mark.asyncio
    async def test_run_detection_logic_game_not_found(self, tray_app, mock_window_manager):
        """Test detection logic behavior when game window is not found."""
        mock_window_manager.find_window.return_value = None
        
        # Start detection thread
        detection_thread = threading.Thread(target=tray_app.run_detection_logic)
        detection_thread.start()
        
        # Wait for auto-pause due to game not found
        time.sleep(1)  # Allow time for multiple detection attempts
        
        # Stop the detection thread
        tray_app.stop_event.set()
        detection_thread.join()
        
        assert tray_app.game_not_found_consecutive_count > 0
        assert tray_app.was_auto_paused_due_to_game_not_found
        assert tray_app.pause_event.is_set()

    def test_profile_selection(self, tray_app, mock_config_manager, mock_profile_io_manager):
        """Test profile selection functionality."""
        # Setup test profile
        test_profile = Profile(
            profile_id="test-profile-1",
            profile_name="Test Profile",
            app_settings=AppSettings(detection_method="ml")
        )
        mock_profile_io_manager.load_profiles.return_value = [test_profile]
        
        # Select profile
        tray_app._select_profile(test_profile)
        
        # Verify profile selection
        assert tray_app.current_profile == test_profile
        assert tray_app.app_settings == test_profile.app_settings
        mock_config_manager.save_settings.assert_called_once()

    def test_auto_profile_switching(self, tray_app, mock_window_manager):
        """Test automatic profile switching based on window title."""
        # Enable auto-switching
        tray_app.app_settings.enable_auto_profile_switching = True
        
        # Setup test profiles
        profile1 = Profile(
            profile_id="profile1",
            profile_name="Profile 1",
            window_title_pattern="Game1",
            app_settings=AppSettings()
        )
        profile2 = Profile(
            profile_id="profile2",
            profile_name="Profile 2",
            window_title_pattern="Game2",
            app_settings=AppSettings()
        )
        
        # Mock window title and profiles
        mock_window = MagicMock()
        mock_window.title = "Game1 Window"
        mock_window_manager.find_window.return_value = mock_window
        tray_app._get_profiles = MagicMock(return_value=[profile1, profile2])
        
        # Test auto-switching
        switched = tray_app._check_and_apply_auto_profile_switch()
        assert switched
        assert tray_app.current_profile == profile1

    @patch('daoc_sprint_manager.ui.tray_app.ConfigGUI')
    def test_open_config_dialog(self, mock_config_gui, tray_app):
        """Test opening configuration dialog."""
        tray_app._on_clicked_open_config(None, None)
        mock_config_gui.assert_called_once()
        
    def test_menu_generation(self, tray_app, mock_pystray):
        """Test system tray menu generation."""
        menu = tray_app.menu
        assert isinstance(menu, MagicMock)  # Since we're using mock pystray
        mock_pystray.Menu.assert_called()
        mock_pystray.MenuItem.assert_called()

    def test_detection_thread_lifecycle(self, tray_app):
        """Test detection thread startup and shutdown."""
        # Start detection thread
        detection_thread = threading.Thread(target=tray_app.run_detection_logic)
        detection_thread.start()
        
        # Verify thread is running
        assert detection_thread.is_alive()
        
        # Stop thread
        tray_app.stop_event.set()
        detection_thread.join(timeout=1)
        
        assert not detection_thread.is_alive()

    def test_profile_manager_dialog(self, tray_app, mock_profile_io_manager):
        """Test profile manager dialog functionality."""
        with patch('daoc_sprint_manager.ui.tray_app.ProfileManagerDialog') as mock_dialog:
            tray_app._open_profile_manager()
            mock_dialog.assert_called_once()
            
            # Test dialog closure
            tray_app._on_profile_manager_closed()
            assert tray_app.profile_manager_dialog_instance is None

    def test_error_handling(self, tray_app, mock_logger):
        """Test error handling in critical operations."""
        # Test config loading error
        with patch.object(tray_app.config_manager, 'load_settings', side_effect=Exception("Test error")):
            tray_app._apply_active_profile_settings()
            mock_logger.error.assert_called()

        # Test profile loading error
        with patch.object(tray_app.profile_io_manager, 'load_profiles', side_effect=Exception("Test error")):
            tray_app._get_profiles()
            mock_logger.error.assert_called()

if __name__ == '__main__':
    pytest.main([__file__]) 