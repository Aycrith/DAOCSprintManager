"""
Machine learning-based icon detector using ONNX Runtime.

This module provides functionality to use an ONNX model for 
detecting icon states in the game interface.
"""

import logging
import pathlib
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

try:
    import onnxruntime as ort
    ONNXRUNTIME_AVAILABLE = True
except ImportError:
    ONNXRUNTIME_AVAILABLE = False

from ..training.model_version_manager import ModelVersionManager

class MLDetector:
    """
    Detects icon states using an ONNX ML model.
    
    This class loads and runs inference with an ONNX model to determine the state
    of the sprint icon in captured frames from the game.
    """
    
    def __init__(
        self,
        model_path: pathlib.Path,
        input_size_wh: List[int],
        confidence_threshold: float,
        logger: logging.Logger,
        version_manager: Optional[ModelVersionManager] = None
    ):
        """
        Initialize the ML detector.
        
        Args:
            model_path: Path to the ONNX model file or models directory.
            input_size_wh: Required input dimensions [width, height] for the model.
            confidence_threshold: Confidence threshold for positive detection (0.0-1.0).
            logger: Logger instance for recording operations and errors.
            version_manager: Optional ModelVersionManager instance for versioned models.
        
        Raises:
            ImportError: If onnxruntime is not installed.
            ValueError: If model_path is invalid or model can't be loaded.
        """
        self.logger = logger
        self.input_size_wh = input_size_wh
        self.confidence_threshold = confidence_threshold
        self.version_manager = version_manager
        
        if not ONNXRUNTIME_AVAILABLE:
            self.logger.error("MLDetector initialization failed: onnxruntime not installed")
            raise ImportError(
                "The onnxruntime package is required for ML-based detection. "
                "Install it using: pip install onnxruntime"
            )
        
        # Initialize version manager if provided
        if version_manager is not None:
            try:
                # Get current version's model path
                model_path = version_manager.get_model_path()
                self.logger.info(f"Using versioned model from {model_path}")
            except ValueError as e:
                self.logger.error(f"Error getting current model version: {e}")
                raise ValueError(f"Failed to get current model version: {e}")
        
        if not model_path.exists():
            self.logger.error(f"Model file does not exist: {model_path}")
            raise ValueError(f"ONNX model not found at {model_path}")
        
        try:
            # Configure ONNX Runtime session options for better performance
            sess_options = ort.SessionOptions()
            # Limit to a single thread to minimize CPU impact
            sess_options.intra_op_num_threads = 1
            # Enable optimization for better performance
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
            
            self.logger.info(f"Loading ONNX model from {model_path} with optimized session options")
            self.logger.debug(f"Using single-threaded execution with extended graph optimizations")
            
            # Create an ONNX inference session with optimized options
            self.session = ort.InferenceSession(
                str(model_path),
                sess_options=sess_options,
                providers=['CPUExecutionProvider']  # Use CPU provider by default for compatibility
            )
            
            # Get input details
            model_inputs = self.session.get_inputs()
            if not model_inputs:
                raise ValueError("Model has no inputs")
            
            self.input_name = model_inputs[0].name
            expected_shape = model_inputs[0].shape
            
            # Check if the shape is compatible
            if len(expected_shape) != 4:  # [batch, channels, height, width]
                self.logger.warning(
                    f"Model input shape {expected_shape} is not the expected NCHW format. "
                    "This might cause prediction errors."
                )
            
            # Get output details
            model_outputs = self.session.get_outputs()
            if not model_outputs:
                raise ValueError("Model has no outputs")
            
            self.output_name = model_outputs[0].name
            self.logger.info(
                f"Model loaded successfully. Input: {self.input_name}, Output: {self.output_name}"
            )
            
        except Exception as e:
            self.logger.error(f"Error initializing ONNX model: {e}", exc_info=True)
            raise ValueError(f"Failed to initialize ONNX model: {e}")
    
    def update_model(self, version_id: Optional[str] = None) -> bool:
        """
        Update to a different model version.
        
        Args:
            version_id: Specific version to use, or None for latest
            
        Returns:
            True if update successful, False otherwise
        """
        if self.version_manager is None:
            self.logger.warning("No version manager available for model updates")
            return False
            
        try:
            if version_id is not None:
                self.version_manager.set_current_version(version_id)
            
            new_model_path = self.version_manager.get_model_path()
            
            # Configure new session
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 1
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
            
            # Create new session
            new_session = ort.InferenceSession(
                str(new_model_path),
                sess_options=sess_options,
                providers=['CPUExecutionProvider']
            )
            
            # Verify input/output compatibility
            new_inputs = new_session.get_inputs()
            new_outputs = new_session.get_outputs()
            
            if not new_inputs or not new_outputs:
                raise ValueError("New model has invalid inputs/outputs")
                
            # Update session and names
            self.session = new_session
            self.input_name = new_inputs[0].name
            self.output_name = new_outputs[0].name
            
            self.logger.info(f"Successfully updated to model version: {version_id or 'latest'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update model: {e}", exc_info=True)
            return False
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the input image for the ML model.
        
        Args:
            image: Input image in BGR format (OpenCV default).
            
        Returns:
            Preprocessed image as a numpy array ready for inference.
        """
        if image.size == 0:
            self.logger.error("Empty image passed to preprocessing")
            raise ValueError("Input image is empty")
        
        try:
            # Resize to required input dimensions
            resized = cv2.resize(
                image,
                (self.input_size_wh[0], self.input_size_wh[1]),
                interpolation=cv2.INTER_AREA
            )
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Normalize to 0-1 range and convert to float32
            normalized = rgb.astype(np.float32) / 255.0
            
            # Move channel dimension to correct position (NCHW format)
            # From (height, width, channels) to (1, channels, height, width)
            transposed = np.transpose(normalized, (2, 0, 1))
            batched = np.expand_dims(transposed, axis=0)
            
            # Ensure the array is C-contiguous for optimal performance with ONNX Runtime
            batched = np.ascontiguousarray(batched, dtype=np.float32)
            
            return batched
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}", exc_info=True)
            raise ValueError(f"Image preprocessing failed: {e}")
    
    def predict(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Perform ML inference on the input image to detect the sprint icon state.
        
        Args:
            image: Input image in BGR format (OpenCV default).
            
        Returns:
            Tuple of (is_detected, confidence_score):
            - is_detected: True if icon is detected with confidence above threshold.
            - confidence_score: The model's confidence value (0.0-1.0).
            
        Raises:
            ValueError: If inference fails or returns invalid results.
        """
        if image is None or image.size == 0:
            self.logger.error("Invalid image passed to predict method")
            return False, 0.0
        
        try:
            # Preprocess the image
            preprocessed = self._preprocess_image(image)
            
            # Run inference
            inputs = {self.input_name: preprocessed}
            outputs = self.session.run([self.output_name], inputs)
            
            if not outputs or len(outputs[0]) == 0:
                self.logger.error("Model returned empty output")
                return False, 0.0
            
            # Parse the output - assuming a binary classification model
            # Output shape is typically [1, 2] or [1, 1] depending on model architecture
            raw_output = outputs[0]
            
            # Handle different output formats
            confidence_score = 0.0
            
            if raw_output.shape[-1] == 2:
                # If output has two values (typical softmax output [not_detected, detected])
                confidence_score = float(raw_output[0, 1])  # Second value represents "detected" class
            elif raw_output.shape[-1] == 1:
                # If output has a single value (sigmoid output for binary classification)
                confidence_score = float(raw_output[0, 0])
            else:
                # For other cases, take the maximum value
                confidence_score = float(np.max(raw_output))
            
            # Apply confidence threshold
            is_detected = confidence_score >= self.confidence_threshold
            
            self.logger.debug(
                f"ML prediction: {'Detected' if is_detected else 'Not detected'} "
                f"with confidence {confidence_score:.4f}"
            )
            
            return is_detected, confidence_score
            
        except Exception as e:
            self.logger.error(f"Error during ML inference: {e}", exc_info=True)
            return False, 0.0 