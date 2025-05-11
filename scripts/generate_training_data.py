"""Generate training dataset from reference images."""

import logging
from pathlib import Path
import cv2
import numpy as np
from daoc_sprint_manager.training.image_preprocessor import ImagePreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_sprint_icon(image_path: Path, output_dir: Path) -> None:
    """Extract sprint icon from reference image and save variations."""
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
        
    # The sprint icon is in the buff bar - extract it
    # We know it's 24x24 pixels and in the rightmost position when active
    icon_size = 24
    buff_bar_y = 0  # Top of the screen
    buff_bar_height = icon_size
    
    # Create output directories
    active_dir = output_dir / "active"
    inactive_dir = output_dir / "inactive"
    active_dir.mkdir(parents=True, exist_ok=True)
    inactive_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract and save the active icon
    icon = img[buff_bar_y:buff_bar_y+buff_bar_height, -icon_size:]
    cv2.imwrite(str(active_dir / "sprint_icon_original.png"), icon)
    
    # For inactive state, we'll use empty buff bar sections
    empty_icon = np.zeros((icon_size, icon_size, 3), dtype=np.uint8)
    cv2.imwrite(str(inactive_dir / "empty_slot_original.png"), empty_icon)
    
    return icon_size

def generate_training_data():
    """Generate training dataset from reference images."""
    # Setup paths
    data_dir = Path("data")
    ref_dir = data_dir / "buff_bar_references"
    train_dir = data_dir / "training_input"
    
    # Initialize preprocessor with 32x32 input size (slightly larger than icon for padding)
    preprocessor = ImagePreprocessor(
        input_size_wh=[32, 32],
        logger=logger
    )
    
    # Extract sprint icon and create base training images
    icon_size = extract_sprint_icon(
        ref_dir / "sprint_active.png",
        train_dir
    )
    
    # Generate augmented training data
    logger.info("Generating augmented training data...")
    
    # Custom augmentation parameters optimized for our use case
    augmentation_params = {
        "brightness_range": (0.9, 1.1),  # Subtle brightness changes
        "contrast_range": (0.9, 1.1),    # Subtle contrast changes
        "rotation_range": (-2, 2),        # Minimal rotation
        "scale_range": (0.95, 1.05),     # Subtle scaling
        "noise_factor": 0.02,            # Minimal noise
        "erase_prob": 0.3,               # Occasional random erasing
        "erase_ratio": (0.05, 0.1)       # Small erase regions
    }
    
    # Process active class
    active_samples = []
    active_dir = train_dir / "active"
    for img_path in active_dir.glob("*.png"):
        augmented = preprocessor.augment_image(img_path, **augmentation_params)
        for i, aug_img in enumerate(augmented):
            output_path = active_dir / f"aug_{img_path.stem}_{i}.png"
            cv2.imwrite(str(output_path), aug_img)
            active_samples.append(str(output_path))
    
    # Process inactive class
    inactive_samples = []
    inactive_dir = train_dir / "inactive"
    for img_path in inactive_dir.glob("*.png"):
        augmented = preprocessor.augment_image(img_path, **augmentation_params)
        for i, aug_img in enumerate(augmented):
            output_path = inactive_dir / f"aug_{img_path.stem}_{i}.png"
            cv2.imwrite(str(output_path), aug_img)
            inactive_samples.append(str(output_path))
    
    # Prepare final dataset
    dataset = preprocessor.prepare_dataset(
        train_dir,
        split_ratio=(0.7, 0.15, 0.15),
        augment=False  # We've already augmented
    )
    
    # Log dataset statistics
    logger.info(f"Generated dataset statistics:")
    logger.info(f"Active samples: {len(active_samples)}")
    logger.info(f"Inactive samples: {len(inactive_samples)}")
    logger.info(f"Train set: {len(dataset['train'])}")
    logger.info(f"Validation set: {len(dataset['val'])}")
    logger.info(f"Test set: {len(dataset['test'])}")

if __name__ == "__main__":
    generate_training_data() 