"""
Create a valid icon file for the application.
"""

from pathlib import Path
from PIL import Image, ImageDraw

def create_icon():
    """Create a simple icon for the application."""
    size = 32
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple icon - white background with black border
    draw.rectangle([0, 0, size-1, size-1], fill='white', outline='black')
    
    # Save as ICO
    resources_dir = Path(__file__).parent.parent / 'resources'
    resources_dir.mkdir(exist_ok=True)
    
    icon_path = resources_dir / 'icon.ico'
    image.save(icon_path, format='ICO')
    print(f"Created icon at: {icon_path}")

if __name__ == '__main__':
    create_icon() 