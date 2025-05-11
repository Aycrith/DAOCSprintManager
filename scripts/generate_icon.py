from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_app_icon():
    # Create base image with transparency
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Define colors
    primary_color = (65, 105, 225)  # Royal Blue
    secondary_color = (255, 255, 255)  # White
    
    # Draw a filled circle for the background
    margin = size // 8
    circle_bbox = (margin, margin, size - margin, size - margin)
    draw.ellipse(circle_bbox, fill=primary_color)
    
    # Draw "S" for Sprint
    try:
        # Try to use a system font
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Center the text
    text = "S"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    # Draw the text
    draw.text((text_x, text_y), text, fill=secondary_color, font=font)
    
    # Ensure the assets directory exists
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Save as PNG first
    png_path = assets_dir / "app_icon.png"
    image.save(png_path, "PNG")
    
    # Convert to ICO with multiple sizes
    ico_path = assets_dir / "app_icon.ico"
    # Create different size versions
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    for size in sizes:
        resized_img = image.resize(size, Image.Resampling.LANCZOS)
        images.append(resized_img)
    
    # Save as ICO with all sizes
    images[0].save(
        ico_path,
        format='ICO',
        sizes=sizes,
        append_images=images[1:]
    )
    
    return png_path, ico_path

if __name__ == "__main__":
    png_path, ico_path = create_app_icon()
    print(f"Icon files created successfully:")
    print(f"PNG: {png_path}")
    print(f"ICO: {ico_path}") 