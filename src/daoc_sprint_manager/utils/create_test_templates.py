"""
Utility script to generate test template images for development and testing.

This script creates basic icon templates to use when actual game screenshots
are not available. For production use, replace with actual game icons.
"""

import argparse
import os
import pathlib
import sys

try:
    import numpy as np
    import cv2
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Required libraries not installed.")
    print("Install with: pip install opencv-python numpy pillow")
    sys.exit(1)

def create_sprint_on_icon(output_path: pathlib.Path, size: int = 32):
    """Create a simple 'sprint active' icon template."""
    # Create a transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple icon - filled circle with an arrow
    center = size // 2
    radius = (size // 2) - 2
    
    # Draw circle
    draw.ellipse((2, 2, size-2, size-2), fill=(0, 180, 0, 255))
    
    # Draw arrow
    arrow_points = [
        (center - radius//2, center + radius//3),
        (center + radius//2, center),
        (center - radius//2, center - radius//3)
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 255))
    
    # Save the image
    img.save(output_path)
    print(f"Created sprint 'ON' template at {output_path}")
    return output_path

def create_sprint_off_icon(output_path: pathlib.Path, size: int = 32):
    """Create a simple 'sprint inactive' icon template."""
    # Create a transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple icon - empty circle with an arrow
    center = size // 2
    radius = (size // 2) - 2
    
    # Draw circle
    draw.ellipse((2, 2, size-2, size-2), outline=(100, 100, 100, 255), width=2)
    
    # Draw arrow
    arrow_points = [
        (center - radius//2, center + radius//3),
        (center + radius//2, center),
        (center - radius//2, center - radius//3)
    ]
    draw.polygon(arrow_points, outline=(150, 150, 150, 255), fill=(100, 100, 100, 128))
    
    # Save the image
    img.save(output_path)
    print(f"Created sprint 'OFF' template at {output_path}")
    return output_path

def create_app_icon(output_path: pathlib.Path, size: int = 64):
    """Create a simple app icon for the system tray."""
    # Create a transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple icon - circle with 'DS' (DAOC Sprint)
    center = size // 2
    radius = (size // 2) - 2
    
    # Draw circle
    draw.ellipse((2, 2, size-2, size-2), fill=(50, 100, 200, 255))
    
    # Draw text
    try:
        # Try to use a font if available
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", size//3)
        except IOError:
            font = ImageFont.load_default()
        draw.text((center-size//6, center-size//6), "DS", fill=(255, 255, 255, 255), font=font)
    except (ImportError, IOError):
        # Fallback to a simple drawing if font not available
        # Draw "DS" as simple lines
        # D shape
        draw.line([(center-size//4, center-size//6), (center-size//4, center+size//6)], fill=(255, 255, 255, 255), width=2)
        draw.arc([center-size//4, center-size//6, center, center+size//6], 270, 90, fill=(255, 255, 255, 255), width=2)
        # S shape
        draw.arc([center, center-size//6, center+size//4, center], 180, 0, fill=(255, 255, 255, 255), width=2)
        draw.arc([center, center, center+size//4, center+size//6], 0, 180, fill=(255, 255, 255, 255), width=2)
    
    # Save the image
    img.save(output_path)
    print(f"Created app icon at {output_path}")
    return output_path

def create_all_templates(templates_dir: pathlib.Path, data_dir: pathlib.Path, size: int = 32):
    """Create all template images for testing."""
    # Ensure directories exist
    templates_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create templates
    create_sprint_on_icon(templates_dir / "sprint_on.png", size)
    create_sprint_off_icon(templates_dir / "sprint_off.png", size)
    create_app_icon(data_dir / "app_icon.png", size*2)  # App icon slightly larger

def main():
    parser = argparse.ArgumentParser(description='Create test template images for DAOC Sprint Manager')
    parser.add_argument('--size', type=int, default=32, help='Size of template images in pixels')
    parser.add_argument('--output', type=str, default=None, help='Output directory (defaults to project data dir)')
    args = parser.parse_args()
    
    # Get project root directory
    script_dir = pathlib.Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent.parent
    
    # Determine output paths
    templates_dir = project_root / "src" / "daoc_sprint_manager" / "data" / "icon_templates"
    data_dir = project_root / "src" / "daoc_sprint_manager" / "data"
    
    # If custom output directory specified
    if args.output:
        output_dir = pathlib.Path(args.output)
        templates_dir = output_dir / "icon_templates"
        data_dir = output_dir
    
    print(f"Creating template images at size {args.size}x{args.size}")
    create_all_templates(templates_dir, data_dir, args.size)
    print("Template creation complete!")

if __name__ == "__main__":
    main() 