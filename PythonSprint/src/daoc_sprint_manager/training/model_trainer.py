"""
Model trainer module for sprint icon classification.

This module provides functionality to train a lightweight CNN model for
binary classification of sprint icons (active/inactive).
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
from sklearn.metrics import classification_report, confusion_matrix
import tf2onnx
import onnx
import onnxruntime as ort

class SprintIconClassifierTrainer:
    """Trainer class for sprint icon classification model."""

    def __init__(
        self,
        processed_dataset_dir: Path,
        model_output_dir: Path,
        input_shape: Tuple[int, int, int],
        num_classes: int = 2,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the trainer.

        Args:
            processed_dataset_dir: Path to preprocessed dataset directory
            model_output_dir: Path to save trained models and history
            input_shape: Model input shape (height, width, channels)
            num_classes: Number of output classes (default: 2)
            logger: Optional logger instance
        """
        self.processed_dataset_dir = Path(processed_dataset_dir)
        self.model_output_dir = Path(model_output_dir)
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.logger = logger or logging.getLogger(__name__)

        # Create model output directory if it doesn't exist
        self.model_output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize model
        self.model = self._build_model()

    def _load_dataset_from_processed_dir(
        self, subset_name: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load and preprocess images from a dataset subset.

        Args:
            subset_name: Name of the subset ("train", "validation", or "test")

        Returns:
            Tuple of (images array, labels array)
        """
        subset_dir = self.processed_dataset_dir / subset_name
        if not subset_dir.exists():
            raise ValueError(f"Dataset subset directory not found: {subset_dir}")

        images = []
        labels = []
        class_dirs = ["active", "inactive"]

        for class_idx, class_name in enumerate(class_dirs):
            class_dir = subset_dir / class_name
            if not class_dir.exists():
                continue

            for img_path in class_dir.glob("*.png"):
                try:
                    # Load and preprocess image
                    img = Image.open(img_path)
                    img = img.resize(self.input_shape[:2], Image.Resampling.LANCZOS)
                    img_array = np.array(img, dtype=np.float32) / 255.0

                    # Add channel dimension if grayscale
                    if len(img_array.shape) == 2:
                        img_array = np.expand_dims(img_array, axis=-1)

                    images.append(img_array)
                    labels.append(class_idx)
                except Exception as e:
                    self.logger.warning(f"Error loading image {img_path}: {e}")

        if not images:
            raise ValueError(f"No images found in {subset_dir}")

        # Convert to numpy arrays
        images_array = np.stack(images)
        labels_array = np.array(labels)

        # Convert labels to one-hot encoding
        labels_one_hot = tf.keras.utils.to_categorical(
            labels_array, num_classes=self.num_classes
        )

        return images_array, labels_one_hot

    def _build_model(self) -> Model:
        """
        Build and compile the CNN model.

        Returns:
            Compiled Keras model
        """
        model = tf.keras.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),

            # First convolutional block
            layers.Conv2D(16, (3, 3), padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),

            # Second convolutional block
            layers.Conv2D(32, (3, 3), padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),

            # Third convolutional block
            layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),

            # Flatten and dense layers
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.num_classes, activation='softmax')
        ])

        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        self.logger.info(f"Model summary:\n{model.summary()}")
        return model

    def train(
        self, epochs: int = 20, batch_size: int = 32
    ) -> tf.keras.callbacks.History:
        """
        Train the model on the processed dataset.

        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training

        Returns:
            Training history
        """
        # Load datasets
        train_images, train_labels = self._load_dataset_from_processed_dir("train")
        val_images, val_labels = self._load_dataset_from_processed_dir("validation")

        # Set up callbacks
        callbacks = [
            ModelCheckpoint(
                str(self.model_output_dir / 'best_sprint_icon_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=3,
                min_lr=1e-6,
                verbose=1
            ),
            TensorBoard(
                log_dir=str(self.model_output_dir / 'logs'),
                histogram_freq=1
            )
        ]

        # Train the model
        history = self.model.fit(
            train_images,
            train_labels,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(val_images, val_labels),
            callbacks=callbacks,
            verbose=1
        )

        # Save final model
        self.model.save(str(self.model_output_dir / 'final_sprint_icon_model.h5'))

        # Save training history
        with open(self.model_output_dir / 'training_history.json', 'w') as f:
            history_dict = {
                key: [float(val) for val in values]
                for key, values in history.history.items()
            }
            json.dump(history_dict, f, indent=4)

        return history

    def evaluate(self, model_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Evaluate the model on the test dataset.

        Args:
            model_path: Optional path to a saved model to evaluate

        Returns:
            Dictionary containing evaluation metrics
        """
        # Load the best model if path provided
        if model_path:
            self.model = tf.keras.models.load_model(str(model_path))
        else:
            best_model_path = self.model_output_dir / 'best_sprint_icon_model.h5'
            if best_model_path.exists():
                self.model = tf.keras.models.load_model(str(best_model_path))

        # Load test dataset
        test_images, test_labels = self._load_dataset_from_processed_dir("test")

        # Evaluate model
        test_loss, test_accuracy = self.model.evaluate(test_images, test_labels)

        # Generate predictions
        y_pred_probs = self.model.predict(test_images)
        y_pred_classes = np.argmax(y_pred_probs, axis=1)
        y_true_classes = np.argmax(test_labels, axis=1)

        # Calculate metrics
        class_names = ["inactive", "active"]  # Map indices to class names
        report = classification_report(
            y_true_classes,
            y_pred_classes,
            target_names=class_names,
            output_dict=True
        )
        conf_matrix = confusion_matrix(y_true_classes, y_pred_classes)

        # Log results
        self.logger.info(f"Test accuracy: {test_accuracy:.4f}")
        self.logger.info(f"Test loss: {test_loss:.4f}")
        self.logger.info("\nClassification Report:")
        self.logger.info(classification_report(y_true_classes, y_pred_classes, target_names=class_names))
        self.logger.info("\nConfusion Matrix:")
        self.logger.info(conf_matrix)

        # Save evaluation results
        results = {
            "test_loss": float(test_loss),
            "test_accuracy": float(test_accuracy),
            "classification_report": report,
            "confusion_matrix": conf_matrix.tolist()
        }

        with open(self.model_output_dir / 'evaluation_results.json', 'w') as f:
            json.dump(results, f, indent=4)

        return results

    def export_to_onnx(
        self,
        keras_model_path: Path,
        onnx_output_path: Path,
        opset_version: int = 13
    ) -> bool:
        """
        Export a trained Keras model to ONNX format.

        Args:
            keras_model_path: Path to the trained Keras model (.h5 file)
            onnx_output_path: Path to save the ONNX model
            opset_version: ONNX opset version to use (default: 13)

        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            self.logger.info(f"Starting ONNX export from {keras_model_path}")

            if not keras_model_path.exists():
                self.logger.error(f"Keras model not found at {keras_model_path}")
                return False

            # Load the trained Keras model
            model = tf.keras.models.load_model(str(keras_model_path))

            # Define input signature for ONNX conversion
            # Note: The input signature uses NHWC format as that's what Keras expects
            # tf2onnx will handle conversion to NCHW format
            input_signature = [
                tf.TensorSpec(
                    [None, self.input_shape[0], self.input_shape[1], self.input_shape[2]],
                    tf.float32,
                    name="input_1"
                )
            ]

            # Convert to ONNX
            self.logger.info("Converting model to ONNX format...")
            onnx_model, _ = tf2onnx.convert.from_keras(
                model,
                input_signature=input_signature,
                opset=opset_version
            )

            # Save the ONNX model
            onnx.save_model(onnx_model, str(onnx_output_path))
            self.logger.info(f"ONNX model saved to {onnx_output_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error during ONNX export: {e}")
            return False

    def validate_onnx_model(
        self,
        onnx_model_path: Path,
        sample_input_data: Optional[np.ndarray] = None
    ) -> bool:
        """
        Validate an exported ONNX model by running test inference.

        Args:
            onnx_model_path: Path to the ONNX model file
            sample_input_data: Optional sample input data for testing.
                If None, random data will be generated.

        Returns:
            bool: True if validation successful, False otherwise
        """
        try:
            self.logger.info(f"Starting ONNX model validation for {onnx_model_path}")

            if not onnx_model_path.exists():
                self.logger.error(f"ONNX model not found at {onnx_model_path}")
                return False

            # Create ONNX Runtime session
            self.logger.info("Creating ONNX Runtime session...")
            ort_session = ort.InferenceSession(
                str(onnx_model_path),
                providers=['CPUExecutionProvider']
            )

            # Log model input/output details
            input_details = ort_session.get_inputs()[0]
            output_details = ort_session.get_outputs()[0]
            self.logger.info(f"Model input: {input_details.name}, shape: {input_details.shape}")
            self.logger.info(f"Model output: {output_details.name}, shape: {output_details.shape}")

            # Create sample input if not provided
            if sample_input_data is None:
                # Create NCHW format input (batch, channels, height, width)
                sample_input_data = np.random.rand(
                    1,  # batch size
                    self.input_shape[2],  # channels
                    self.input_shape[0],  # height
                    self.input_shape[1]   # width
                ).astype(np.float32)

            # Run inference
            self.logger.info("Running test inference...")
            ort_inputs = {input_details.name: sample_input_data}
            ort_outputs = ort_session.run(None, ort_inputs)

            # Validate output
            output_shape = ort_outputs[0].shape
            expected_shape = (1, self.num_classes)  # batch size 1, num_classes outputs
            
            self.logger.info(f"Output shape: {output_shape}")
            if output_shape != expected_shape:
                self.logger.error(
                    f"Unexpected output shape: got {output_shape}, "
                    f"expected {expected_shape}"
                )
                return False

            self.logger.info("ONNX model validation successful!")
            return True

        except Exception as e:
            self.logger.error(f"Error during ONNX model validation: {e}")
            return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Test paths
    processed_dataset_dir = Path("data/ml_processed_output")
    model_output_dir = Path("data/models/temp_training_output")
    onnx_model_output_path = model_output_dir / "sprint_icon_model.onnx"

    try:
        # Ensure test directories exist
        if not processed_dataset_dir.exists():
            logger.error(
                "Please run ImagePreprocessor first to create processed dataset in "
                "data/ml_processed_output with train/, validation/, and test/ subdirectories "
                "containing active/ and inactive/ class folders."
            )
            exit(1)

        # Initialize trainer
        trainer = SprintIconClassifierTrainer(
            processed_dataset_dir=processed_dataset_dir,
            model_output_dir=model_output_dir,
            input_shape=(32, 32, 3),  # Default from AppSettings
            logger=logger
        )

        # Train model
        logger.info("Starting model training...")
        history = trainer.train(epochs=20, batch_size=32)

        # Evaluate model
        logger.info("Evaluating model...")
        evaluation_results = trainer.evaluate()

        # Export to ONNX
        logger.info("Exporting model to ONNX format...")
        keras_model_path = model_output_dir / "best_sprint_icon_model.h5"
        if trainer.export_to_onnx(keras_model_path, onnx_model_output_path):
            # Validate ONNX model
            logger.info("Validating ONNX model...")
            trainer.validate_onnx_model(onnx_model_output_path)

        logger.info("Training, evaluation, and ONNX export complete!")
        logger.info(f"Model and results saved to: {model_output_dir}")

    except Exception as e:
        logger.error(f"Error during training: {e}")
        raise 