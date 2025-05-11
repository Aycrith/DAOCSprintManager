"""Image preprocessing and augmentation utilities for training."""

import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union, Callable
import numpy as np
import cv2
from PIL import Image, ImageEnhance
import random
from tqdm import tqdm

class ImagePreprocessor:
    """Handles image preprocessing and augmentation for training.
    
    This class provides utilities for:
    1. Resizing images to model input dimensions
    2. Normalizing pixel values
    3. Data augmentation (brightness, contrast, rotation, scaling, random erasing, noise)
    4. Dataset splitting into train/val/test sets
    5. Validation of augmented images
    6. Memory-efficient batch processing
    """
    
    def __init__(
        self,
        input_size_wh: List[int],
        logger: Optional[logging.Logger] = None,
        batch_size: int = 32
    ):
        """Initialize the preprocessor.
        
        Args:
            input_size_wh: Required input size as [width, height] in pixels
            logger: Optional logger instance
            batch_size: Size of batches for memory-efficient processing
        """
        self.input_size_wh = input_size_wh
        self.logger = logger or logging.getLogger(__name__)
        self.batch_size = batch_size
        
    def preprocess_image(
        self,
        image: Union[np.ndarray, Path, str],
        normalize: bool = True
    ) -> np.ndarray:
        """Preprocess a single image for training or inference.
        
        Args:
            image: Input image as numpy array (BGR) or path to image file
            normalize: Whether to normalize pixel values to [0,1] range
            
        Returns:
            Preprocessed image as numpy array in NCHW format
            
        Raises:
            ValueError: If image loading or preprocessing fails
        """
        try:
            # Load image if path provided
            if isinstance(image, (str, Path)):
                image = cv2.imread(str(image))
                if image is None:
                    raise ValueError(f"Failed to load image from {image}")
            
            # Ensure image is not empty
            if image.size == 0:
                raise ValueError("Empty image provided")
            
            # Resize to required dimensions
            resized = cv2.resize(
                image,
                (self.input_size_wh[0], self.input_size_wh[1]),
                interpolation=cv2.INTER_AREA
            )
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Normalize if requested
            if normalize:
                rgb = rgb.astype(np.float32) / 255.0
            
            # Convert to NCHW format
            # From (height, width, channels) to (1, channels, height, width)
            transposed = np.transpose(rgb, (2, 0, 1))
            batched = np.expand_dims(transposed, axis=0)
            
            # Ensure C-contiguous memory layout
            return np.ascontiguousarray(batched, dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            raise ValueError(f"Image preprocessing failed: {e}")

    def validate_image(self, image: np.ndarray) -> bool:
        """Validate an image after augmentation.
        
        Args:
            image: Image to validate as numpy array
            
        Returns:
            True if image is valid, False otherwise
        """
        try:
            # Check image dimensions
            if image.shape[0] == 0 or image.shape[1] == 0:
                return False
                
            # Check for NaN or Inf values
            if np.isnan(image).any() or np.isinf(image).any():
                return False
                
            # Check if image is too dark or too bright
            if image.mean() < 10 or image.mean() > 245:
                return False
                
            # Check if image has enough variation
            if image.std() < 5:
                return False
                
            return True
        except Exception:
            return False
            
    def augment_image(
        self,
        image: Union[np.ndarray, Path, str],
        brightness_range: Tuple[float, float] = (0.8, 1.2),
        contrast_range: Tuple[float, float] = (0.8, 1.2),
        rotation_range: Tuple[float, float] = (-5, 5),
        scale_range: Tuple[float, float] = (0.9, 1.1),
        noise_factor: float = 0.05,
        erase_prob: float = 0.5,
        erase_ratio: Tuple[float, float] = (0.02, 0.2)
    ) -> List[np.ndarray]:
        """Apply augmentations to an image.
        
        Args:
            image: Input image as numpy array (BGR) or path to image file
            brightness_range: Range for brightness adjustment
            contrast_range: Range for contrast adjustment
            rotation_range: Range for rotation in degrees
            scale_range: Range for scaling factor
            noise_factor: Standard deviation for Gaussian noise
            erase_prob: Probability of random erasing
            erase_ratio: Range for erasing area ratio
            
        Returns:
            List of augmented images as numpy arrays
        """
        try:
            # Load image if path provided
            if isinstance(image, (str, Path)):
                image = cv2.imread(str(image))
                if image is None:
                    raise ValueError(f"Failed to load image from {image}")
            
            # Convert to PIL Image for augmentation
            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            augmented_images = []
            
            # Brightness augmentation
            enhancer = ImageEnhance.Brightness(image_pil)
            for factor in [brightness_range[0], brightness_range[1]]:
                aug_img = enhancer.enhance(factor)
                aug_array = cv2.cvtColor(np.array(aug_img), cv2.COLOR_RGB2BGR)
                augmented_images.append(aug_array)
            
            # Contrast augmentation
            enhancer = ImageEnhance.Contrast(image_pil)
            for factor in [contrast_range[0], contrast_range[1]]:
                aug_img = enhancer.enhance(factor)
                aug_array = cv2.cvtColor(np.array(aug_img), cv2.COLOR_RGB2BGR)
                augmented_images.append(aug_array)
            
            # Rotation augmentation
            for angle in [rotation_range[0], rotation_range[1]]:
                aug_img = image_pil.rotate(angle, resample=Image.BICUBIC, expand=False)
                aug_array = cv2.cvtColor(np.array(aug_img), cv2.COLOR_RGB2BGR)
                augmented_images.append(aug_array)
            
            # Scale augmentation
            height, width = image.shape[:2]
            for scale in [scale_range[0], scale_range[1]]:
                # Scale dimensions
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # Resize image
                scaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                if scale > 1.0:
                    # Crop center if scaled up
                    start_x = (new_width - width) // 2
                    start_y = (new_height - height) // 2
                    scaled = scaled[start_y:start_y+height, start_x:start_x+width]
                else:
                    # Pad if scaled down
                    pad_x = (width - new_width) // 2
                    pad_y = (height - new_height) // 2
                    scaled = cv2.copyMakeBorder(
                        scaled,
                        pad_y,
                        height - new_height - pad_y,
                        pad_x,
                        width - new_width - pad_x,
                        cv2.BORDER_CONSTANT,
                        value=[0, 0, 0]
                    )
                
                augmented_images.append(scaled)
            
            # Add Gaussian noise
            noisy = image.copy()
            noise = np.random.normal(0, noise_factor * 255, image.shape)
            noisy = np.clip(noisy + noise, 0, 255).astype(np.uint8)
            if self.validate_image(noisy):
                augmented_images.append(noisy)
            
            # Random erasing
            if random.random() < erase_prob:
                erased = image.copy()
                h, w = image.shape[:2]
                
                # Calculate erasing area
                area_ratio = random.uniform(erase_ratio[0], erase_ratio[1])
                aspect_ratio = random.uniform(0.3, 3.3)
                
                erase_h = int(np.sqrt(h * w * area_ratio / aspect_ratio))
                erase_w = int(erase_h * aspect_ratio)
                
                if erase_h < h and erase_w < w:
                    x = random.randint(0, w - erase_w)
                    y = random.randint(0, h - erase_h)
                    
                    # Fill with random color or mean color
                    if random.random() < 0.5:
                        fill_val = np.mean(image, axis=(0, 1)).astype(np.uint8)
                    else:
                        fill_val = np.random.randint(0, 255, size=3, dtype=np.uint8)
                    
                    erased[y:y+erase_h, x:x+erase_w] = fill_val
                    
                    if self.validate_image(erased):
                        augmented_images.append(erased)
            
            return [img for img in augmented_images if self.validate_image(img)]
            
        except Exception as e:
            self.logger.error(f"Error augmenting image: {e}")
            raise ValueError(f"Image augmentation failed: {e}")
    
    def prepare_dataset(
        self,
        data_dir: Union[str, Path],
        split_ratio: Tuple[float, float, float] = (0.7, 0.15, 0.15),
        augment: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        """Prepare a dataset by splitting and preprocessing images.
        
        Args:
            data_dir: Directory containing labeled image subdirectories
            split_ratio: Ratio for train/val/test split as (train, val, test)
            augment: Whether to apply augmentation to training set
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with 'train', 'val', 'test' splits, each containing
            a list of dicts with 'path' and 'label' keys
            
        Raises:
            ValueError: If data directory is invalid or empty
        """
        data_dir = Path(data_dir)
        if not data_dir.exists():
            raise ValueError(f"Data directory not found: {data_dir}")
        
        # Collect all images and labels
        image_data = []
        for label_dir in data_dir.iterdir():
            if not label_dir.is_dir():
                continue
                
            label = label_dir.name
            for img_path in label_dir.glob("*.png"):
                image_data.append({
                    "path": str(img_path),
                    "label": label
                })
        
        if not image_data:
            raise ValueError(f"No images found in {data_dir}")
        
        # Shuffle data
        random.shuffle(image_data)
        
        # Split data
        total = len(image_data)
        train_size = int(total * split_ratio[0])
        val_size = int(total * split_ratio[1])
        
        splits = {
            "train": image_data[:train_size],
            "val": image_data[train_size:train_size + val_size],
            "test": image_data[train_size + val_size:]
        }
        
        # Apply augmentation to training set if requested
        if augment:
            augmented_train = []
            total_train = len(splits["train"])
            
            # Process in batches for memory efficiency
            for batch_start in tqdm(range(0, total_train, self.batch_size), desc="Augmenting"):
                batch_end = min(batch_start + self.batch_size, total_train)
                batch = splits["train"][batch_start:batch_end]
                
                for item in batch:
                    # Keep original
                    augmented_train.append(item)
                    
                    # Add augmented versions
                    try:
                        aug_images = self.augment_image(item["path"])
                        for i, aug_img in enumerate(aug_images):
                            # Save augmented image
                            aug_path = Path(item["path"])
                            aug_name = f"{aug_path.stem}_aug{i}{aug_path.suffix}"
                            aug_path = aug_path.parent / aug_name
                            cv2.imwrite(str(aug_path), aug_img)
                            
                            # Add to dataset
                            augmented_train.append({
                                "path": str(aug_path),
                                "label": item["label"]
                            })
                    except Exception as e:
                        self.logger.warning(f"Failed to augment {item['path']}: {e}")
                        continue
                
                if progress_callback:
                    progress_callback(batch_end, total_train)
            
            splits["train"] = augmented_train
        
        return splits 