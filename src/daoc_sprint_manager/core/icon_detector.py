"""
Icon detection module using template matching techniques.

Provides functionality to load icon templates and perform detection
with temporal consistency checks for improved reliability.
"""

import logging
import pathlib
import time
from collections import deque
from typing import Deque, List, Optional, Tuple

import cv2
import numpy as np

class IconDetector:
    """
    Detects icons in images using template matching with temporal consistency checks.
    
    Uses OpenCV's template matching to find icon templates within captured frames.
    Implements temporal consistency to reduce false positives/negatives by considering
    multiple consecutive frames before confirming a state change.
    """

    def __init__(self, logger: logging.Logger, temporal_consistency_frames: int = 3):
        """
        Initializes the IconDetector with logging and temporal consistency settings.

        Args:
            logger: Logger instance for recording operations and errors.
            temporal_consistency_frames: Number of consecutive frames required
                to confirm a state change (default: 3).
        """
        self.logger = logger
        self.temporal_consistency_frames = max(1, temporal_consistency_frames)
        # Maintains history of detection results for temporal consistency
        self.detection_history: Deque[bool] = deque(maxlen=self.temporal_consistency_frames + 1)
        # Initialize with False detections
        self.detection_history.extend([False] * self.temporal_consistency_frames)
        self.confirmed_active = False
        self.logger.debug(f"IconDetector initialized with temporal consistency frames={self.temporal_consistency_frames}")

    def load_template(self, template_path: pathlib.Path) -> Optional[np.ndarray]:
        """
        Loads and preprocesses an icon template image from a file.

        Args:
            template_path: Path to the template image file.

        Returns:
            Loaded template as a NumPy array or None if loading fails.
        """
        try:
            self.logger.debug(f"Loading template from {template_path}")
            # Use OpenCV to read the image
            template = cv2.imread(str(template_path))
            
            if template is None:
                self.logger.error(f"Failed to load template image: {template_path}")
                return None
                
            if template.shape[0] == 0 or template.shape[1] == 0:
                self.logger.error(f"Loaded template has invalid dimensions: {template.shape}")
                return None
                
            self.logger.info(f"Template loaded successfully: {template_path} (Shape: {template.shape})")
            return template
            
        except Exception as e:
            self.logger.exception(f"Error loading template {template_path}: {e}")
            return None

    def detect_icon(self, 
                   frame: np.ndarray, 
                   template: np.ndarray,
                   match_threshold: float = 0.8) -> Tuple[bool, float, Optional[Tuple[int, int, int, int]]]:
        """
        Detects if the template icon is present in the provided frame.

        Uses template matching to locate the icon and compares the match score
        against the threshold to determine if a match is found.

        Args:
            frame: The image frame to search within (NumPy array from capture).
            template: The template image to search for.
            match_threshold: Confidence threshold for match detection (0.0-1.0).
                Higher values require closer matches.

        Returns:
            Tuple containing:
            - bool: True if icon is detected, False otherwise.
            - float: Match confidence score (0.0-1.0).
            - Optional[Tuple[int, int, int, int]]: Bounding box of detection (x, y, w, h) or None.

        Raises:
            ValueError: If frame or template is invalid.
        """
        # Validate inputs
        if frame is None or template is None:
            self.logger.error("Cannot detect icon: frame or template is None")
            return False, 0.0, None
            
        if len(frame.shape) < 2 or len(template.shape) < 2:
            self.logger.error(f"Invalid frame or template shape: frame={frame.shape}, template={template.shape}")
            return False, 0.0, None
            
        # Check if template is larger than frame
        if template.shape[0] > frame.shape[0] or template.shape[1] > frame.shape[1]:
            self.logger.warning(
                f"Template ({template.shape[:2]}) is larger than frame ({frame.shape[:2]}). "
                "Cannot perform detection."
            )
            return False, 0.0, None

        try:
            # Convert to grayscale if the images are color (for more robust matching)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
            
            # Perform template matching
            result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # Get the best match location and score
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # TM_CCOEFF_NORMED returns highest value as best match
            match_score = max_val
            match_loc = max_loc
            w, h = template_gray.shape[1], template_gray.shape[0]
            
            # Determine if the match is valid based on threshold
            is_detected = match_score >= match_threshold
            
            # Create bounding box if detected
            detection_box = (match_loc[0], match_loc[1], w, h) if is_detected else None
            
            self.logger.debug(f"Match result: detected={is_detected}, score={match_score:.4f}")
            return is_detected, match_score, detection_box
            
        except Exception as e:
            self.logger.exception(f"Error during template detection: {e}")
            return False, 0.0, None

    def update_consistent_detection_state(self, current_detection: bool) -> bool:
        """
        Updates the detection history and determines the consistent detection state.
        
        Implements temporal consistency checking by requiring consecutive consistent
        detections before confirming a state change.

        Args:
            current_detection: The current frame's detection result (True/False).
            
        Returns:
            The confirmed detection state after temporal consistency checking.
        """
        # Add the current detection to history
        self.detection_history.append(current_detection)
        
        # Count true and false detections in the history
        true_count = sum(1 for detected in self.detection_history if detected)
        
        # If all or most recent frames show detection, confirm active
        if true_count >= self.temporal_consistency_frames:
            if not self.confirmed_active:
                self.logger.info(f"Icon state changed: ACTIVE (after {self.temporal_consistency_frames} consistent frames)")
            self.confirmed_active = True
        # If none or very few recent frames show detection, confirm inactive
        elif true_count == 0:
            if self.confirmed_active:
                self.logger.info(f"Icon state changed: INACTIVE (after {self.temporal_consistency_frames} consistent frames)")
            self.confirmed_active = False
        # Otherwise, state remains unchanged (requires consistency to change)
        
        self.logger.debug(f"Detection update: current={current_detection}, history={list(self.detection_history)}, confirmed={self.confirmed_active}")
        return self.confirmed_active

    def get_detection_confidence(self) -> float:
        """
        Calculates the current detection confidence based on history.
        
        Returns:
            Float between 0.0 and 1.0 representing the confidence level
            based on the proportion of positive detections in history.
        """
        if not self.detection_history:
            return 0.0
            
        # Calculate the proportion of True detections in the history
        true_count = sum(1 for detected in self.detection_history if detected)
        confidence = true_count / len(self.detection_history)
        
        self.logger.debug(f"Detection confidence: {confidence:.2f}")
        return confidence


if __name__ == "__main__":
    import sys
    import tempfile
    # Set up a basic logger for testing
    test_logger = logging.getLogger("IconDetectorTest")
    test_logger.setLevel(logging.DEBUG)
    if not test_logger.handlers:  # Avoid adding multiple handlers if run again
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'))
        test_logger.addHandler(handler)

    detector = IconDetector(test_logger, temporal_consistency_frames=3)

    print("\n--- Testing IconDetector ---")

    # Test 1: Create a synthetic "frame" with a simple pattern
    print("\nTest 1: Testing exact match detection...")
    # Create a black frame
    frame_size = (100, 100)
    frame = np.zeros((frame_size[0], frame_size[1], 3), dtype=np.uint8)
    # Add a white square pattern
    square_pos = (40, 40)
    square_size = 20
    frame[square_pos[1]:square_pos[1]+square_size, square_pos[0]:square_pos[0]+square_size] = (255, 255, 255)
    
    # Create a template from the same pattern
    template = frame[square_pos[1]:square_pos[1]+square_size, square_pos[0]:square_pos[0]+square_size].copy()
    
    # Detect the template in the frame
    detected, score, bbox = detector.detect_icon(frame, template, 0.9)
    print(f" -> Match result: detected={detected}, score={score:.4f}")
    assert detected, "Exact match should be detected"
    assert score > 0.99, "Exact match should have near-perfect score"
    assert bbox == (square_pos[0], square_pos[1], square_size, square_size), f"Bounding box should match pattern position. Got {bbox}"

    # Test 2: Test with frame and random template that shouldn't match
    print("\nTest 2: Testing non-matching template...")
    random_template = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
    detected, score, bbox = detector.detect_icon(frame, random_template, 0.8)
    print(f" -> Match result: detected={detected}, score={score:.4f}")
    assert not detected, "Random template should not match"
    
    # Test 3: Test template larger than frame (should fail gracefully)
    print("\nTest 3: Testing template larger than frame...")
    large_template = np.zeros((frame_size[0]+10, frame_size[1]+10, 3), dtype=np.uint8)
    detected, score, bbox = detector.detect_icon(frame, large_template, 0.8)
    print(f" -> Match result: detected={detected}, score={score:.4f}")
    assert not detected, "Template larger than frame should not match"
    
    # Test 4: Test temporal consistency
    print("\nTest 4: Testing temporal consistency...")
    # Initialize with all False
    detector = IconDetector(test_logger, temporal_consistency_frames=3)
    print(" -> Starting with all inactive state")
    assert not detector.confirmed_active, "Should start inactive"
    
    # Add two true detections (not enough to change state)
    for i in range(2):
        confirmed = detector.update_consistent_detection_state(True)
        print(f" -> Added True detection {i+1}, confirmed state: {confirmed}")
    assert not detector.confirmed_active, "Should still be inactive with only 2 True detections"
    
    # Add a third true detection (should now confirm active)
    confirmed = detector.update_consistent_detection_state(True)
    print(f" -> Added True detection 3, confirmed state: {confirmed}")
    assert detector.confirmed_active, "Should be active after 3 consecutive True detections"
    
    # Add a single false detection (not enough to change state)
    confirmed = detector.update_consistent_detection_state(False)
    print(f" -> Added False detection, confirmed state: {confirmed}")
    assert detector.confirmed_active, "Should still be active with just 1 False detection"
    
    # Add two more false detections (now should be inactive)
    for i in range(2):
        confirmed = detector.update_consistent_detection_state(False)
        print(f" -> Added False detection {i+2}, confirmed state: {confirmed}")
        
    # Test if the state changed to inactive after 3 consecutive False detections
    assert not detector.confirmed_active, "Should be inactive after 3 consecutive False detections"
    
    print("\n--- IconDetector Tests Completed Successfully! ---") 