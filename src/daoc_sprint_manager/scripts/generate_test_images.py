import os
import numpy as np
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_image_generator')

def create_test_image(size=(64, 64), color=(255, 0, 0)):
    """Create a test image with the given size and color."""
    img = Image.new('RGB', size, color)
    return img

def generate_test_images():
    """Generate test images for each category."""
    categories = ['active', 'inactive', 'other']
    base_dir = 'data/ml_training_data'
    
    # Number of images to generate per category
    num_images = 10
    
    for category in categories:
        category_dir = os.path.join(base_dir, category)
        logger.info(f"Generating {num_images} images for category: {category}")
        
        # Generate images with different colors for each category
        if category == 'active':
            color = (255, 0, 0)  # Red for active
        elif category == 'inactive':
            color = (0, 255, 0)  # Green for inactive
        else:
            color = (0, 0, 255)  # Blue for other
        
        for i in range(num_images):
            # Create image with random size between 48x48 and 96x96
            size = np.random.randint(48, 97, size=2)
            img = create_test_image(size=tuple(size), color=color)
            
            # Save the image
            filename = f"{category}_test_{i+1}.png"
            filepath = os.path.join(category_dir, filename)
            img.save(filepath)
            logger.info(f"Created {filepath}")

if __name__ == "__main__":
    generate_test_images() 