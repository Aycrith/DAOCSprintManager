"""Model training pipeline for sprint icon classifier.

This module provides functionality to train a CNN model for classifying
sprint icon states (active/inactive) using TensorFlow/Keras.
"""

import logging
from pathlib import Path
import json
from typing import Tuple, Dict, Any, Optional, List
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, optimizers, losses, metrics, callbacks
from sklearn.metrics import classification_report, confusion_matrix
import shutil

class SprintIconClassifierTrainer:
    """Trains a CNN model for sprint icon state classification."""
    
    def __init__(
        self,
        processed_dataset_dir: Path,
        model_output_dir: Path,
        input_shape: Tuple[int, int, int],
        num_classes: int = 2,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the trainer.
        
        Args:
            processed_dataset_dir: Path to preprocessed dataset directory
            model_output_dir: Path to save trained models and reports
            input_shape: Model input shape (height, width, channels)
            num_classes: Number of output classes (default: 2 for binary)
            logger: Optional logger instance
        """
        self.processed_dataset_dir = Path(processed_dataset_dir)
        self.model_output_dir = Path(model_output_dir)
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.logger = logger or logging.getLogger(__name__)
        
        # Create output directory
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_dataset_from_processed_dir(
        self,
        subset_name: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Load images and labels from a dataset subset directory.
        
        Args:
            subset_name: Name of the subset ("train", "validation", or "test")
            
        Returns:
            Tuple of (images array, labels array)
        """
        subset_dir = self.processed_dataset_dir / subset_name
        if not subset_dir.exists():
            raise ValueError(f"Dataset subset directory not found: {subset_dir}")
            
        # Use Keras utility for efficient loading
        dataset = tf.keras.utils.image_dataset_from_directory(
            subset_dir,
            labels='inferred',
            label_mode='categorical',  # One-hot encoded labels
            class_names=['inactive', 'active'],  # Ensure consistent class order
            color_mode='rgb',
            batch_size=None,  # Load all at once
            image_size=(self.input_shape[0], self.input_shape[1]),
            shuffle=False  # No need to shuffle here
        )
        
        # Convert to numpy arrays
        images_list = []
        labels_list = []
        
        for images, labels in dataset:
            images_list.append(images.numpy())
            labels_list.append(labels.numpy())
            
        images_array = np.concatenate(images_list, axis=0)
        labels_array = np.concatenate(labels_list, axis=0)
        
        # Normalize images to [0, 1] range if not already done
        if images_array.dtype != np.float32 or images_array.max() > 1.0:
            images_array = images_array.astype(np.float32) / 255.0
            
        self.logger.info(
            f"Loaded {len(images_array)} images from {subset_name} set "
            f"with shape {images_array.shape}"
        )
        
        return images_array, labels_array
        
    def _build_model(self) -> tf.keras.Model:
        """Build and compile the CNN model architecture.
        
        Returns:
            Compiled Keras model
        """
        model = tf.keras.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),
            
            # First convolutional block
            layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Second convolutional block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Third convolutional block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Flatten and dense layers
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.4),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss=losses.CategoricalCrossentropy(),
            metrics=['accuracy']
        )
        
        # Log model summary
        model.summary(print_fn=self.logger.info)
        
        return model
        
    def train(
        self,
        epochs: int = 25,
        batch_size: int = 32
    ) -> tf.keras.callbacks.History:
        """Train the model on the preprocessed dataset.
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        # Load datasets
        train_images, train_labels = self._load_dataset_from_processed_dir("train")
        val_images, val_labels = self._load_dataset_from_processed_dir("validation")
        
        # Build model
        model = self._build_model()
        
        # Define callbacks
        callbacks_list = [
            # Save best model
            callbacks.ModelCheckpoint(
                str(self.model_output_dir / 'best_sprint_icon_model.keras'),
                monitor='val_accuracy',
                mode='max',
                save_best_only=True,
                verbose=1
            ),
            # Early stopping
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=7,
                restore_best_weights=True,
                verbose=1
            ),
            # Reduce learning rate on plateau
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=3,
                min_lr=1e-6,
                verbose=1
            ),
            # TensorBoard logging
            callbacks.TensorBoard(
                log_dir=str(self.model_output_dir / 'tensorboard_logs'),
                histogram_freq=1
            )
        ]
        
        # Train the model
        history = model.fit(
            train_images,
            train_labels,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(val_images, val_labels),
            callbacks=callbacks_list,
            verbose=1
        )
        
        # Save final model
        model.save(str(self.model_output_dir / 'final_sprint_icon_model.keras'))
        
        # Save training history
        history_dict = history.history
        history_path = self.model_output_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(history_dict, f, indent=2)
            
        self.logger.info(f"Training history saved to {history_path}")
        
        return history
        
    def evaluate_model(
        self,
        model_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Evaluate the trained model on the test set.
        
        Args:
            model_path: Optional path to a specific model to evaluate
            
        Returns:
            Dictionary containing evaluation metrics
        """
        # Load the model
        if model_path is None:
            model_path = self.model_output_dir / 'best_sprint_icon_model.keras'
            
        if not model_path.exists():
            raise ValueError(f"Model not found at {model_path}")
            
        model = tf.keras.models.load_model(str(model_path))
        self.logger.info(f"Loaded model from {model_path}")
        
        # Load test data if available
        try:
            test_images, test_labels = self._load_dataset_from_processed_dir("test")
        except ValueError:
            self.logger.warning("No test set found, skipping evaluation")
            return {'error': 'No test set available'}
            
        # Evaluate model
        loss, accuracy = model.evaluate(test_images, test_labels, verbose=0)
        
        # Get predictions
        y_pred_probs = model.predict(test_images, verbose=0)
        y_pred_classes = np.argmax(y_pred_probs, axis=1)
        y_true_classes = np.argmax(test_labels, axis=1)
        
        # Calculate metrics
        report = classification_report(
            y_true_classes,
            y_pred_classes,
            target_names=['inactive', 'active'],
            output_dict=True
        )
        
        cm = confusion_matrix(y_true_classes, y_pred_classes)
        
        # Log results
        self.logger.info(f"Test Loss: {loss:.4f}")
        self.logger.info(f"Test Accuracy: {accuracy:.4f}")
        self.logger.info("\nClassification Report:")
        self.logger.info(classification_report(
            y_true_classes,
            y_pred_classes,
            target_names=['inactive', 'active']
        ))
        self.logger.info("\nConfusion Matrix:")
        self.logger.info(f"\n{cm}")
        
        # Save evaluation results
        results = {
            'loss': float(loss),
            'accuracy': float(accuracy),
            'classification_report': report,
            'confusion_matrix': cm.tolist()
        }
        
        results_path = self.model_output_dir / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        self.logger.info(f"Evaluation results saved to {results_path}")
        
        return results


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info(
        "\nSelf-test for SprintIconClassifierTrainer\n"
        "----------------------------------------\n"
        "This test requires a pre-existing processed dataset created by ImagePreprocessor.\n"
        "Before running this test:\n"
        "1. Run image_preprocessor.py on a sample of labeled images\n"
        "   (ensure 'active' and 'inactive' folders exist in the input)\n"
        "2. This will create output directories like:\n"
        "   data/ml_processed_output/train/active/\n"
        "   data/ml_processed_output/train/inactive/\n"
        "   etc.\n"
    )
    
    # Test configuration
    processed_dataset_dir_test = Path("data/ml_processed_output")
    model_output_dir_test = Path("temp_model_training_output")
    input_shape_test = (32, 32, 3)  # Should match AppSettings.ml_input_size_wh
    
    if not processed_dataset_dir_test.exists():
        logger.error(
            f"Processed dataset directory not found at {processed_dataset_dir_test}\n"
            "Please run image_preprocessor.py first to create the processed dataset."
        )
        exit(1)
        
    try:
        # Create trainer instance
        trainer = SprintIconClassifierTrainer(
            processed_dataset_dir=processed_dataset_dir_test,
            model_output_dir=model_output_dir_test,
            input_shape=input_shape_test,
            logger=logger
        )
        
        # Run a very short training session
        logger.info("Running quick training test (1 epoch)...")
        trainer.train(epochs=1, batch_size=4)
        
        # Evaluate
        logger.info("Running evaluation test...")
        eval_results = trainer.evaluate_model()
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        
    finally:
        # Clean up test output directory
        if model_output_dir_test.exists():
            shutil.rmtree(model_output_dir_test)
            logger.info(f"Cleaned up test directory: {model_output_dir_test}") 