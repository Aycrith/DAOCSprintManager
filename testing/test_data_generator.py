"""
Test Data Generator for Profile Management System
Generates test profiles with various configurations for testing
"""

import json
import os
import random
from typing import Dict, List, Optional

class TestProfileGenerator:
    def __init__(self, output_dir: str = "test_data"):
        """Initialize the test profile generator.
        
        Args:
            output_dir: Directory to save generated profiles
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def generate_window_pattern(self) -> Dict[str, str]:
        """Generate a test window pattern configuration."""
        patterns = [
            {"title": "Dark Age of Camelot", "class": "DAoCMWC"},
            {"title": "Character Name - Dark Age of Camelot", "class": "DAoCMWC"},
            {"title": "Eden - Character Name", "class": "DAoCMWC"}
        ]
        return random.choice(patterns)
        
    def generate_roi_config(self) -> Dict[str, int]:
        """Generate test ROI coordinates."""
        return {
            "x": random.randint(100, 500),
            "y": random.randint(100, 300),
            "width": random.randint(50, 100),
            "height": random.randint(50, 100)
        }
        
    def generate_profile(self, name: str, valid: bool = True) -> Dict:
        """Generate a single test profile.
        
        Args:
            name: Profile name
            valid: Whether to generate valid or invalid data
            
        Returns:
            Dict containing profile data
        """
        profile = {
            "name": name,
            "window_pattern": self.generate_window_pattern(),
            "roi_config": self.generate_roi_config(),
            "enabled": random.choice([True, False]),
            "auto_switch": random.choice([True, False]),
            "priority": random.randint(1, 5)
        }
        
        if not valid:
            # Introduce invalid data for testing error handling
            if random.choice([True, False]):
                profile["roi_config"]["x"] = -1
            if random.choice([True, False]):
                del profile["window_pattern"]["class"]
                
        return profile
        
    def generate_test_suite(self, num_profiles: int = 5) -> List[Dict]:
        """Generate a suite of test profiles.
        
        Args:
            num_profiles: Number of profiles to generate
            
        Returns:
            List of generated profile dictionaries
        """
        profiles = []
        
        # Generate valid profiles
        for i in range(num_profiles):
            profile = self.generate_profile(f"Test Profile {i+1}")
            profiles.append(profile)
            
        # Generate some invalid profiles
        for i in range(2):
            profile = self.generate_profile(f"Invalid Profile {i+1}", valid=False)
            profiles.append(profile)
            
        return profiles
        
    def save_profiles(self, profiles: List[Dict], filename: str):
        """Save generated profiles to a JSON file.
        
        Args:
            profiles: List of profile dictionaries
            filename: Output filename
        """
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w') as f:
            json.dump(profiles, f, indent=4)
            
def main():
    """Main function to generate test data."""
    generator = TestProfileGenerator("testing/test_data")
    
    # Generate main test suite
    profiles = generator.generate_test_suite(5)
    generator.save_profiles(profiles, "test_profiles.json")
    
    # Generate edge cases
    edge_cases = [
        generator.generate_profile("Empty Pattern", valid=False),
        generator.generate_profile("Negative ROI", valid=False),
        generator.generate_profile("Missing Fields", valid=False)
    ]
    generator.save_profiles(edge_cases, "edge_case_profiles.json")
    
if __name__ == "__main__":
    main() 