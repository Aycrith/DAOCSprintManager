import os
import shutil
import json
from pathlib import Path

class TestEnvironmentSetup:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.test_dir = self.base_dir / "test_environment"
        self.config_dir = self.test_dir / "config"
        self.templates_dir = self.test_dir / "templates"
        self.bin_dir = self.test_dir / "bin"
        self.profiles_dir = self.test_dir / "profiles"
        self.resources_dir = self.test_dir / "resources"
        self.test_results_dir = self.test_dir / "test_results"
        
    def setup_directories(self):
        """Create necessary test directories"""
        dirs = [
            self.test_dir,
            self.config_dir,
            self.templates_dir,
            self.bin_dir,
            self.profiles_dir,
            self.resources_dir,
            self.resources_dir / "images",
            self.resources_dir / "sounds",
            self.resources_dir / "icons",
            self.test_results_dir,
            self.test_results_dir / "reports",
            self.test_results_dir / "performance_logs"
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def create_test_config(self):
        """Create test configuration files"""
        # Create settings.json
        default_config = {
            "window": {
                "title": "Dark Age of Camelot",
                "roi": {"x": 100, "y": 100, "width": 50, "height": 50}
            },
            "detection": {
                "method": "template",
                "confidence_threshold": 0.8,
                "temporal_consistency": 3
            },
            "input": {
                "sprint_key": "num1",
                "safety_delay": 0.1
            },
            "performance": {
                "target_fps": 30,
                "adaptive_polling": True
            },
            "profiles": {
                "active_profile": "default",
                "auto_switch": False
            }
        }
        
        with open(self.config_dir / "settings.json", "w") as f:
            json.dump(default_config, f, indent=4)
            
        # Create validation_rules.json
        validation_rules = {
            "window": {
                "title": {"type": "string", "required": True},
                "roi": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "min": 0},
                        "y": {"type": "integer", "min": 0},
                        "width": {"type": "integer", "min": 1},
                        "height": {"type": "integer", "min": 1}
                    },
                    "required": ["x", "y", "width", "height"]
                }
            }
        }
        
        with open(self.config_dir / "validation_rules.json", "w") as f:
            json.dump(validation_rules, f, indent=4)
            
    def create_test_profiles(self):
        """Create test profile configurations"""
        # Create default profile template
        default_template = {
            "name": "Default Profile",
            "window_title": "Dark Age of Camelot",
            "roi": {"x": 100, "y": 100, "width": 50, "height": 50},
            "sprint_key": "num1"
        }
        
        with open(self.templates_dir / "default_profile.json", "w") as f:
            json.dump(default_template, f, indent=4)
            
        # Create actual default profile
        with open(self.profiles_dir / "default.json", "w") as f:
            json.dump(default_template, f, indent=4)
            
    def create_test_executable(self):
        """Create a dummy executable for testing"""
        # Create a simple batch file as a placeholder
        with open(self.bin_dir / "sprint_manager.exe", "w") as f:
            f.write("@echo off\necho Sprint Manager Test Executable")
            
    def create_test_resources(self):
        """Create test resource files"""
        # Create placeholder images
        import numpy as np
        from PIL import Image
        
        # Create test images
        test_image = Image.fromarray(np.full((50, 50, 3), 255, dtype=np.uint8))
        test_image.save(self.resources_dir / "images" / "test.png")
        
        # Create test sound file
        with open(self.resources_dir / "sounds" / "test.wav", "w") as f:
            f.write("Test sound file")
            
        # Create test icon
        test_image.save(self.resources_dir / "icons" / "test.png")
        
    def setup(self):
        """Run complete test environment setup"""
        print("Setting up test environment...")
        self.setup_directories()
        self.create_test_config()
        self.create_test_profiles()
        self.create_test_executable()
        self.create_test_resources()
        print("Test environment setup complete!")

if __name__ == "__main__":
    setup = TestEnvironmentSetup()
    setup.setup() 