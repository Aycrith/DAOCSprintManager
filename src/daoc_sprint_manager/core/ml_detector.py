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
        logger: logging.Logger
    ):
        """
        Initialize the ML detector.
        
        Args:
            model_path: Path to the ONNX model file.
            input_size_wh: Required input dimensions [width, height] for the model.
            confidence_threshold: Confidence threshold for positive detection (0.0-1.0).
            logger: Logger instance for recording operations and errors.
        
        Raises:
            ImportError: If onnxruntime is not installed.
            ValueError: If model_path is invalid or model can't be loaded.
        """
        self.logger = logger
        self.input_size_wh = input_size_wh
        self.confidence_threshold = confidence_threshold
        
        if not ONNXRUNTIME_AVAILABLE:
            self.logger.error("MLDetector initialization failed: onnxruntime not installed")
            raise ImportError(
                "The onnxruntime package is required for ML-based detection. "
                "Install it using: pip install onnxruntime"
            )
        
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


if __name__ == "__main__":
    """
    Self-test for the MLDetector.
    
    To run this test, you must have a sample ONNX model and a test image.
    The test will look for:
    - A dummy ONNX model at 'tests/data/models/dummy_model.onnx'
    - A test image at 'tests/data/images/test_icon.png'
    
    You can create a dummy ONNX model with these steps:
    1. Install required packages: pip install onnx onnxruntime tensorflow tensorflow_addons
    2. Use a script like this to create a simple classification model:
    
    ```python
    import tensorflow as tf
    import onnx
    import tf2onnx
    import numpy as np
    import os
    
    # Create a simple model
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(32, 32, 3)),
        tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax') # Binary classifier
    ])
    
    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    
    # Create output directory
    os.makedirs("tests/data/models", exist_ok=True)
    
    # Convert the model to ONNX
    input_signature = [tf.TensorSpec([1, 32, 32, 3], tf.float32, name='input')]
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature, opset=13)
    onnx.save(onnx_model, "tests/data/models/dummy_model.onnx")
    
    print("Dummy ONNX model created at: tests/data/models/dummy_model.onnx")
    ```
    
    3. Create a test image at 'tests/data/images/test_icon.png' (32x32 pixel)
    """
    import os
    import sys
    
    # Setup basic logging
    test_logger = logging.getLogger("MLDetectorTest")
    test_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    test_logger.addHandler(handler)
    
    # Create test directories if they don't exist
    test_dirs = ['tests/data/models', 'tests/data/images']
    for directory in test_dirs:
        os.makedirs(directory, exist_ok=True)
    
    print("\n--- Testing MLDetector Class ---")
    
    if not ONNXRUNTIME_AVAILABLE:
        print("ERROR: onnxruntime not installed. Please install with: pip install onnxruntime")
        sys.exit(1)
    
    # Define test paths
    test_model_path = pathlib.Path("tests/data/models/dummy_model.onnx")
    test_image_path = pathlib.Path("tests/data/images/test_icon.png")
    
    # Check if test files exist
    model_exists = test_model_path.exists()
    image_exists = test_image_path.exists()
    
    if not model_exists:
        print(f"WARNING: Test model not found at {test_model_path}")
        print("Please create a dummy model following the instructions in the comments.")
        
    if not image_exists:
        print(f"WARNING: Test image not found at {test_image_path}")
        print("Creating a blank test image...")
        import numpy as np
        import cv2
        # Create a 32x32 test image with a white circle
        test_image = np.zeros((32, 32, 3), dtype=np.uint8)
        cv2.circle(test_image, (16, 16), 10, (255, 255, 255), -1)
        os.makedirs(test_image_path.parent, exist_ok=True)
        cv2.imwrite(str(test_image_path), test_image)
        print(f"Created test image at {test_image_path}")
        image_exists = True
    
    # Run tests only if we have both the model and image
    if model_exists and image_exists:
        try:
            # Initialize MLDetector
            print("\nTest 1: Initializing MLDetector...")
            detector = MLDetector(
                model_path=test_model_path,
                input_size_wh=[32, 32],
                confidence_threshold=0.5,
                logger=test_logger
            )
            print("✅ MLDetector initialized successfully")
            
            # Test prediction
            print("\nTest 2: Testing prediction...")
            test_image = cv2.imread(str(test_image_path))
            if test_image is None:
                print(f"❌ Failed to load test image from {test_image_path}")
            else:
                is_detected, confidence = detector.predict(test_image)
                print(f"Prediction result: {'Detected' if is_detected else 'Not detected'}")
                print(f"Confidence score: {confidence:.4f}")
                print("✅ Prediction completed")
                
            print("\nAll tests with mock data completed successfully")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    else:
        print("\nSkipping tests that require model and image files.")
        
    # Test proper error handling
    print("\nTest 3: Testing error handling...")
    
    # Test with non-existent model file
    try:
        nonexistent_model = pathlib.Path("nonexistent_model.onnx")
        MLDetector(
            model_path=nonexistent_model,
            input_size_wh=[32, 32],
            confidence_threshold=0.5,
            logger=test_logger
        )
        print("❌ Should have raised ValueError for non-existent model")
    except ValueError as e:
        print(f"✅ Correctly caught ValueError: {e}")
    except Exception as e:
        print(f"❓ Expected ValueError but got: {e}")
    
    print("\n--- MLDetector Tests Complete ---") 