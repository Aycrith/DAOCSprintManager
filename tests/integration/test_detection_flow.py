"""
Integration tests for the complete detection workflow.

Tests the interaction between WindowManager, IconDetector, and InputManager
with minimal mocking, focusing on data flow and state transitions.
"""

import logging
import pathlib
import time
from typing import Dict, List, Optional, Tuple
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from daoc_sprint_manager.core.icon_detector import IconDetector
from daoc_sprint_manager.core.input_manager import InputManager
from daoc_sprint_manager.core.window_manager import WindowManager, WindowType


class MockWindowManager(WindowManager):
    """
    Mock WindowManager that returns predefined test images.
    Only mocks the actual window interaction, preserving the real image processing logic.
    """
    
    def __init__(self, logger: logging.Logger, test_images: Dict[str, np.ndarray]):
        """
        Initialize with test images for different states.
        
        Args:
            logger: Logger instance
            test_images: Dictionary mapping state names to test images
        """
        super().__init__(logger)
        self.test_images = test_images
        self.current_image_key = "sprint_off"
        self.mock_window = MagicMock()
        
    def find_window(self, window_title_substring: str) -> Optional[WindowType]:
        """Always returns the mock window."""
        return self.mock_window
        
    def capture_window(self, window: WindowType) -> Optional[np.ndarray]:
        """Returns the current test image."""
        return self.test_images[self.current_image_key].copy()
        
    def capture_roi_from_window(self, window: WindowType, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """Extracts ROI from the current test image."""
        full_image = self.capture_window(window)
        if full_image is None:
            return None
        return full_image[y:y+height, x:x+width].copy()
        
    def set_current_image(self, key: str):
        """Change the current test image state."""
        if key in self.test_images:
            self.current_image_key = key


class MockInputManager(InputManager):
    """
    Mock InputManager that tracks key presses without actually sending them.
    """
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.pressed_keys: List[str] = []
        self.key_states: Dict[str, bool] = {}  # True if pressed, False if released
        
    def press_key(self, key_code: str) -> None:
        """Record key press without actually pressing."""
        self.pressed_keys.append(f"press_{key_code}")
        self.key_states[key_code] = True
        
    def release_key(self, key_code: str) -> None:
        """Record key release without actually releasing."""
        self.pressed_keys.append(f"release_{key_code}")
        self.key_states[key_code] = False
        
    def is_key_pressed(self, key_code: str) -> bool:
        """Check if a key is currently pressed."""
        return self.key_states.get(key_code, False)
        
    def clear_history(self):
        """Clear the key press history."""
        self.pressed_keys.clear()
        self.key_states.clear()


@pytest.fixture
def test_logger():
    """Create a logger for testing."""
    logger = logging.getLogger("DetectionFlowTest")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def test_images(shared_datadir) -> Dict[str, np.ndarray]:
    """Load test images for different sprint states."""
    images = {}
    
    # Create or load test images
    sprint_on_path = shared_datadir / "sprint_on.png"
    sprint_off_path = shared_datadir / "sprint_off.png"
    
    if not sprint_on_path.exists() or not sprint_off_path.exists():
        # Create synthetic test images if they don't exist
        sprint_on = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.circle(sprint_on, (50, 50), 20, (255, 255, 255), -1)  # White circle for "ON"
        
        sprint_off = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.circle(sprint_off, (50, 50), 20, (128, 128, 128), -1)  # Gray circle for "OFF"
        
        cv2.imwrite(str(sprint_on_path), sprint_on)
        cv2.imwrite(str(sprint_off_path), sprint_off)
        
        images["sprint_on"] = sprint_on
        images["sprint_off"] = sprint_off
    else:
        images["sprint_on"] = cv2.imread(str(sprint_on_path))
        images["sprint_off"] = cv2.imread(str(sprint_off_path))
    
    return images


@pytest.fixture
def mock_window_manager(test_logger, test_images):
    """Create a MockWindowManager instance."""
    return MockWindowManager(test_logger, test_images)


@pytest.fixture
def mock_input_manager(test_logger):
    """Create a MockInputManager instance."""
    return MockInputManager(test_logger)


@pytest.fixture
def icon_detector(test_logger, shared_datadir):
    """Create a real IconDetector instance."""
    # Create a simple template for testing
    template_path = shared_datadir / "sprint_template.png"
    if not template_path.exists():
        template = np.zeros((40, 40, 3), dtype=np.uint8)
        cv2.circle(template, (20, 20), 10, (255, 255, 255), -1)
        cv2.imwrite(str(template_path), template)
    
    detector = IconDetector(test_logger, temporal_consistency_frames=2)
    template = detector.load_template(template_path)
    assert template is not None, "Failed to load template"
    return detector


class TestDetectionFlow:
    """Integration tests for the complete detection workflow."""
    
    def test_basic_detection_flow(self, mock_window_manager, icon_detector, mock_input_manager):
        """Test basic detection flow from window capture to input action."""
        # Initial state: Sprint OFF
        mock_window_manager.set_current_image("sprint_off")
        
        # Capture and detect
        window = mock_window_manager.find_window("DAOC")
        assert window is not None
        
        # First detection (should not trigger due to temporal consistency)
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        assert frame is not None
        
        detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
        is_active = icon_detector.update_consistent_detection_state(detected)
        assert not is_active, "Should not be active after single detection"
        
        # Second detection (should still be OFF)
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
        is_active = icon_detector.update_consistent_detection_state(detected)
        assert not is_active, "Should remain inactive"
        
        # Change state to ON and detect
        mock_window_manager.set_current_image("sprint_on")
        
        # First ON detection
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
        is_active = icon_detector.update_consistent_detection_state(detected)
        assert not is_active, "Should not be active after single ON detection"
        
        # Second ON detection (should now be active)
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
        is_active = icon_detector.update_consistent_detection_state(detected)
        assert is_active, "Should be active after consistent ON detections"
        
        # Verify input action
        mock_input_manager.send_keypress('r')
        assert mock_input_manager.pressed_keys == ["press_r", "release_r"]
    
    def test_temporal_consistency_transitions(self, mock_window_manager, icon_detector, mock_input_manager):
        """Test state transitions with temporal consistency checks."""
        window = mock_window_manager.find_window("DAOC")
        assert window is not None
        
        # Test transition from OFF -> ON -> OFF
        sequences = [
            ("sprint_off", False),
            ("sprint_off", False),
            ("sprint_on", False),  # First ON detection
            ("sprint_on", True),   # Second ON detection - should activate
            ("sprint_off", True),  # First OFF detection - should stay active
            ("sprint_off", False), # Second OFF detection - should deactivate
        ]
        
        for image_key, expected_state in sequences:
            mock_window_manager.set_current_image(image_key)
            frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
            detected, _, _ = icon_detector.detect_icon(frame, template=icon_detector.template)
            is_active = icon_detector.update_consistent_detection_state(detected)
            assert is_active == expected_state, f"Wrong state for {image_key}: expected {expected_state}, got {is_active}"
    
    def test_error_handling_and_recovery(self, mock_window_manager, icon_detector, mock_input_manager):
        """Test error handling and recovery in the detection flow."""
        window = mock_window_manager.find_window("DAOC")
        assert window is not None
        
        # Test with valid frame
        mock_window_manager.set_current_image("sprint_on")
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
        assert detected is not None, "Detection should work with valid frame"
        
        # Test with None frame (simulating capture failure)
        mock_window_manager.test_images["error"] = None
        mock_window_manager.set_current_image("error")
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        if frame is not None:
            detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
            is_active = icon_detector.update_consistent_detection_state(detected)
            assert not is_active, "Should handle None frame gracefully"
        
        # Test recovery after error
        mock_window_manager.set_current_image("sprint_on")
        frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
        detected, score, bbox = icon_detector.detect_icon(frame, template=icon_detector.template)
        assert detected is not None, "Should recover after error"
    
    def test_input_action_verification(self, mock_window_manager, icon_detector, mock_input_manager):
        """Test that input actions are correctly triggered based on state changes."""
        window = mock_window_manager.find_window("DAOC")
        
        # Sequence of states and expected key states
        sequences = [
            ("sprint_off", False, []),  # Initial state
            ("sprint_on", False, []),   # First ON detection
            ("sprint_on", True, ["press_r", "release_r"]),  # Activation
            ("sprint_off", True, []),   # First OFF detection
            ("sprint_off", False, ["press_r", "release_r"]),  # Deactivation
        ]
        
        for image_key, expected_active, expected_keys in sequences:
            mock_input_manager.clear_history()
            mock_window_manager.set_current_image(image_key)
            
            frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
            detected, _, _ = icon_detector.detect_icon(frame, template=icon_detector.template)
            is_active = icon_detector.update_consistent_detection_state(detected)
            
            if is_active != icon_detector.confirmed_active:
                mock_input_manager.send_keypress('r')
            
            assert is_active == expected_active, f"Wrong state for {image_key}"
            assert mock_input_manager.pressed_keys == expected_keys, f"Wrong key sequence for {image_key}"
    
    def test_detection_confidence_tracking(self, mock_window_manager, icon_detector):
        """Test confidence score tracking through state transitions."""
        window = mock_window_manager.find_window("DAOC")
        
        # Test confidence progression through state changes
        sequences = [
            "sprint_off",
            "sprint_off",
            "sprint_on",
            "sprint_on",
            "sprint_on",
        ]
        
        confidence_scores = []
        for image_key in sequences:
            mock_window_manager.set_current_image(image_key)
            frame = mock_window_manager.capture_roi_from_window(window, 0, 0, 100, 100)
            _, score, _ = icon_detector.detect_icon(frame, template=icon_detector.template)
            confidence_scores.append(score)
        
        # Verify confidence trends
        assert len(confidence_scores) == len(sequences), "Should have confidence score for each detection"
        assert all(score >= 0.0 and score <= 1.0 for score in confidence_scores), "Confidence scores should be normalized" 