"""Test script for verifying the preprocessing pipeline functionality."""

import logging
import pathlib
from typing import Dict, List

from daoc_sprint_manager.training.image_preprocessor import ImagePreprocessor

def setup_logger() -> logging.Logger:
    """Set up a logger for the test script."""
    logger = logging.getLogger("preprocessing_test")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(ch)
    
    return logger

def print_dataset_stats(splits: Dict[str, List[Dict[str, str]]]) -> None:
    """Print statistics about the dataset splits."""
    print("\nDataset Statistics:")
    print("-" * 20)
    
    for split_name, split_data in splits.items():
        # Count images per label
        label_counts = {}
        for item in split_data:
            label = item["label"]
            label_counts[label] = label_counts.get(label, 0) + 1
        
        print(f"\n{split_name.upper()} Set:")
        print(f"Total images: {len(split_data)}")
        print("Label distribution:")
        for label, count in label_counts.items():
            print(f"  - {label}: {count} images")

def main():
    """Run preprocessing pipeline test."""
    # Set up logger
    logger = setup_logger()
    
    # Define paths
    data_dir = pathlib.Path("data/ml_training_data")
    
    # Initialize preprocessor with 32x32 input size
    preprocessor = ImagePreprocessor(
        input_size_wh=[32, 32],
        logger=logger,
        batch_size=32
    )
    
    logger.info("Starting preprocessing test...")
    
    try:
        # Prepare dataset with default split ratios and augmentation
        splits = preprocessor.prepare_dataset(
            data_dir=data_dir,
            split_ratio=(0.7, 0.15, 0.15),
            augment=True
        )
        
        # Print dataset statistics
        print_dataset_stats(splits)
        
        logger.info("Preprocessing test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during preprocessing test: {e}")
        raise

if __name__ == "__main__":
    main() 