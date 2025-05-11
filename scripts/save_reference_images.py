import shutil
from pathlib import Path

SOURCE_IMAGES = {
    "sprint_active": "Sprint-Active.PNG",
    "buff_bar_empty": "Sprint-InActive.PNG",
    "buff_bar_default": "DaocDefaultView.PNG"
}

def save_images():
    # Create directories if they don't exist
    data_dir = Path("data")
    buff_bar_dir = data_dir / "buff_bar_references"
    icon_templates_dir = data_dir / "icon_templates"
    
    for dir_path in [buff_bar_dir, icon_templates_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Save each image
    for name, source_file in SOURCE_IMAGES.items():
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                print(f"Warning: Source file {source_file} not found")
                continue
                
            # Copy to buff bar references
            output_path = buff_bar_dir / f"{name}.png"
            shutil.copy2(source_path, output_path)
            print(f"Saved {name} to {output_path}")
            
            # If this is the sprint icon, also save to templates
            if name == "sprint_active":
                template_path = icon_templates_dir / "sprint_icon.png"
                shutil.copy2(source_path, template_path)
                print(f"Saved sprint icon template to {template_path}")
                
        except Exception as e:
            print(f"Error saving {name}: {e}")

if __name__ == "__main__":
    save_images() 