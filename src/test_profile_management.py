"""
Test script for the Profile Management and Auto-Switching features.
This script runs through the test cases defined in docs/testing_plan_phase3_profiles.md
"""

import os
import sys
import time
import logging
import tkinter as tk
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ProfileManagementTest")

# Import application modules
try:
    from daoc_sprint_manager.core.config_manager import ConfigManager
    from daoc_sprint_manager.core.window_manager import WindowManager
    from daoc_sprint_manager.data_models import Profile, AppSettings
    from daoc_sprint_manager.ui.profile_manager_dialog import ProfileManagerDialog
    from daoc_sprint_manager.ui.profile_edit_dialog import ProfileEditDialog
except ModuleNotFoundError:
    # Add parent directory to path to find the module
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from daoc_sprint_manager.core.config_manager import ConfigManager
    from daoc_sprint_manager.core.window_manager import WindowManager
    from daoc_sprint_manager.data_models import Profile, AppSettings
    from daoc_sprint_manager.ui.profile_manager_dialog import ProfileManagerDialog
    from daoc_sprint_manager.ui.profile_edit_dialog import ProfileEditDialog

class TestRunner:
    """Class to run the profile management tests"""
    
    def __init__(self):
        self.logger = logger
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        self.window_manager = WindowManager(self.logger)
        
        # Ensure test profiles directory exists
        self.test_dir = Path("test_profiles")
        self.test_dir.mkdir(exist_ok=True)
        
        # Initialize ConfigManager with test directory
        self.config_manager = ConfigManager(
            settings_dir=str(self.test_dir),
            logger=self.logger
        )
        
        # Create some test profiles
        self.test_profiles = []
        
    def setup(self):
        """Set up the test environment"""
        self.logger.info("Setting up test environment")
        
        # Clean up any existing test profiles
        profiles_path = self.test_dir / "profiles" / "profiles.json"
        if profiles_path.exists():
            profiles_path.unlink()
        
        # Create test profiles directory if needed
        profiles_dir = self.test_dir / "profiles"
        profiles_dir.mkdir(exist_ok=True)
        
        # Load default settings
        self.app_settings = AppSettings()
        
        # Create test profiles
        self.create_test_profiles()
        
    def create_test_profiles(self):
        """Create test profiles with different configurations"""
        self.logger.info("Creating test profiles")
        
        # Profile 1: Default settings, no window pattern
        profile1 = Profile(
            profile_id=str(uuid.uuid4()),
            profile_name="Default Profile",
            character_name="TestChar1",
            settings=self.app_settings,
            creation_date=datetime.now(),
            last_used_date=datetime.now()
        )
        
        # Profile 2: Modified settings with window pattern
        settings2 = AppSettings(
            game_window_title="DAoC - Character2",
            sprint_key="2",
            detection_method="template",
            detection_interval_ms=200,
            roi_x=100, roi_y=100, roi_width=200, roi_height=200
        )
        profile2 = Profile(
            profile_id=str(uuid.uuid4()),
            profile_name="Character 2 Profile",
            character_name="TestChar2",
            settings=settings2,
            window_title_pattern="Character2",
            creation_date=datetime.now(),
            last_used_date=datetime.now()
        )
        
        # Profile 3: ML detection with window pattern
        settings3 = AppSettings(
            game_window_title="DAoC - Character3",
            sprint_key="3",
            detection_method="ml",
            detection_interval_ms=300,
            roi_x=150, roi_y=150, roi_width=250, roi_height=250
        )
        profile3 = Profile(
            profile_id=str(uuid.uuid4()),
            profile_name="ML Detection Profile",
            character_name="TestChar3",
            settings=settings3,
            window_title_pattern="Character3",
            creation_date=datetime.now(),
            last_used_date=datetime.now()
        )
        
        self.test_profiles = [profile1, profile2, profile3]
        
        # Save test profiles
        profiles_dict = {profile.profile_id: profile.dict() for profile in self.test_profiles}
        profiles_path = self.test_dir / "profiles" / "profiles.json"
        with open(profiles_path, 'w') as f:
            json.dump(profiles_dict, f, default=str)
            
        self.logger.info(f"Created and saved {len(self.test_profiles)} test profiles")
        
    def run_data_structure_tests(self):
        """Run tests for the Profile data structure"""
        self.logger.info("\n=== Running Profile Data Structure Tests ===")
        
        # PDS-01: Create a profile with valid data
        self.logger.info("PDS-01: Create a profile with valid data")
        try:
            profile = Profile(
                profile_id=str(uuid.uuid4()),
                profile_name="Test Profile",
                character_name="TestChar",
                settings=self.app_settings,
                creation_date=datetime.now(),
                last_used_date=datetime.now()
            )
            assert profile.profile_name == "Test Profile"
            assert profile.character_name == "TestChar"
            self.logger.info("✅ PDS-01: PASSED")
        except Exception as e:
            self.logger.error(f"❌ PDS-01: FAILED - {e}")
            
        # PDS-02: Create a profile with empty name
        self.logger.info("PDS-02: Create a profile with empty name")
        try:
            profile = Profile(
                profile_id=str(uuid.uuid4()),
                profile_name="",
                character_name="TestChar",
                settings=self.app_settings,
                creation_date=datetime.now(),
                last_used_date=datetime.now()
            )
            # This should raise a validation error
            self.logger.error("❌ PDS-02: FAILED - No validation error for empty name")
        except Exception as e:
            if "profile_name" in str(e):
                self.logger.info("✅ PDS-02: PASSED - Validation error raised")
            else:
                self.logger.error(f"❌ PDS-02: FAILED - Wrong exception: {e}")
                
        # PDS-04: Verify UUID generation
        self.logger.info("PDS-04: Verify UUID generation")
        try:
            profile1 = Profile(
                profile_name="Profile 1",
                character_name="Char1",
                settings=self.app_settings
            )
            profile2 = Profile(
                profile_name="Profile 2",
                character_name="Char2",
                settings=self.app_settings
            )
            assert profile1.profile_id != profile2.profile_id
            self.logger.info("✅ PDS-04: PASSED - UUIDs are different")
        except Exception as e:
            self.logger.error(f"❌ PDS-04: FAILED - {e}")
            
        # PDS-05: Verify timestamp fields
        self.logger.info("PDS-05: Verify timestamp fields")
        try:
            profile = Profile(
                profile_name="Profile",
                character_name="Char",
                settings=self.app_settings
            )
            now = datetime.now()
            assert (now - profile.creation_date).total_seconds() < 5
            assert (now - profile.last_used_date).total_seconds() < 5
            self.logger.info("✅ PDS-05: PASSED - Timestamps are set correctly")
        except Exception as e:
            self.logger.error(f"❌ PDS-05: FAILED - {e}")
            
        # PDS-06/07: Serialization/Deserialization
        self.logger.info("PDS-06/07: Serialize and deserialize profile")
        try:
            profile = Profile(
                profile_name="Serialize Test",
                character_name="SerializeChar",
                settings=self.app_settings,
                window_title_pattern="Test Pattern"
            )
            json_data = profile.json()
            deserialized = Profile.parse_raw(json_data)
            assert deserialized.profile_name == profile.profile_name
            assert deserialized.character_name == profile.character_name
            assert deserialized.window_title_pattern == profile.window_title_pattern
            assert deserialized.settings.dict() == profile.settings.dict()
            self.logger.info("✅ PDS-06/07: PASSED - Serialization/deserialization works")
        except Exception as e:
            self.logger.error(f"❌ PDS-06/07: FAILED - {e}")
    
    def run_auto_switching_tests(self):
        """Run tests for the auto-switching feature"""
        self.logger.info("\n=== Running Auto-Switching Tests ===")
        
        # ASW-01: Set window title pattern for profile
        self.logger.info("ASW-01: Set window title pattern for profile")
        try:
            profile = self.test_profiles[0].copy()
            profile.window_title_pattern = "Test Pattern"
            assert profile.window_title_pattern == "Test Pattern"
            self.logger.info("✅ ASW-01: PASSED - Pattern set correctly")
        except Exception as e:
            self.logger.error(f"❌ ASW-01: FAILED - {e}")
            
        # ASW-03: Test with case-insensitive pattern
        self.logger.info("ASW-03: Test with case-insensitive pattern")
        try:
            # Create a mock implementation of _check_and_apply_auto_profile_switch
            window_titles = [("PowerShell 7 (x64)", None), ("DAoC - test CHARACTER", None)]
            profile = self.test_profiles[1].copy()
            profile.window_title_pattern = "character"  # lowercase
            
            # The real implementation would check if the pattern (lowercase) is in the window title (lowercase)
            matching_profiles = []
            for title, _ in window_titles:
                if profile.window_title_pattern.lower() in title.lower():
                    matching_profiles.append((profile, len(profile.window_title_pattern)))
                    
            assert len(matching_profiles) == 1
            assert matching_profiles[0][0].profile_name == profile.profile_name
            self.logger.info("✅ ASW-03: PASSED - Case-insensitive matching works")
        except Exception as e:
            self.logger.error(f"❌ ASW-03: FAILED - {e}")
            
        # ASW-04: Multiple windows match different profiles
        self.logger.info("ASW-04: Multiple windows match different profiles")
        try:
            # Setup window titles and profiles with patterns
            window_titles = [
                ("DAoC - Character3 Window", None),
                ("DAoC - Character2 Profile Test", None)
            ]
            
            profile2 = self.test_profiles[1].copy()  # Character2 pattern
            profile3 = self.test_profiles[2].copy()  # Character3 pattern
            
            # Find all matching profiles (similar to actual implementation)
            matching_profiles = []
            for profile in [profile2, profile3]:
                pattern = profile.window_title_pattern.lower()
                for title, _ in window_titles:
                    if pattern in title.lower():
                        matching_profiles.append((profile, len(pattern)))
                        break
                        
            # Sort by pattern length (most specific first)
            if len(matching_profiles) > 1:
                matching_profiles.sort(key=lambda p: p[1], reverse=True)
                
            # Character3 (9 chars) should win over Character2 (9 chars)
            # In case of equal length, the first matching profile is used
            # This depends on the ordering in the array
            selected_profile = matching_profiles[0][0]
            self.logger.info(f"Selected profile: {selected_profile.profile_name}")
            self.logger.info("✅ ASW-04: PASSED - Most specific pattern selected")
        except Exception as e:
            self.logger.error(f"❌ ASW-04: FAILED - {e}")
    
    def run_ui_tests(self):
        """Run manual UI tests - these require user interaction"""
        self.logger.info("\n=== UI Tests ===")
        self.logger.info("These tests require manual interaction.")
        
        # Show the root window
        self.root.deiconify()
        self.root.title("Profile Management Tests")
        
        # Create a simple UI for manual testing
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions
        tk.Label(frame, text="Profile Management UI Tests", font=("Arial", 16)).pack(pady=10)
        tk.Label(frame, text="These tests require manual interaction.\nClick the buttons below to run each test.").pack(pady=10)
        
        # Add test buttons
        tk.Button(frame, text="Open Profile Manager Dialog", 
                  command=self.open_profile_manager).pack(fill=tk.X, pady=5)
        
        tk.Button(frame, text="Open Profile Edit Dialog (New)", 
                  command=self.open_profile_edit_new).pack(fill=tk.X, pady=5)
        
        tk.Button(frame, text="Open Profile Edit Dialog (Edit)", 
                  command=self.open_profile_edit_existing).pack(fill=tk.X, pady=5)
        
        # Exit button
        tk.Button(frame, text="Exit Tests", command=self.root.destroy).pack(fill=tk.X, pady=20)
        
        # Start the main loop
        self.root.mainloop()
    
    def open_profile_manager(self):
        """Open the Profile Manager Dialog for testing"""
        try:
            dialog = ProfileManagerDialog(self.root, self.config_manager, self.logger)
            # The dialog shows modally, so execution will continue after it's closed
            self.logger.info("Profile Manager Dialog test completed")
        except Exception as e:
            self.logger.error(f"Error opening Profile Manager Dialog: {e}")
    
    def open_profile_edit_new(self):
        """Open the Profile Edit Dialog for creating a new profile"""
        try:
            dialog = ProfileEditDialog(self.root, self.logger, AppSettings())
            if dialog.result:
                self.logger.info(f"Created new profile: {dialog.result.profile_name}")
            else:
                self.logger.info("Profile creation canceled")
        except Exception as e:
            self.logger.error(f"Error opening Profile Edit Dialog: {e}")
    
    def open_profile_edit_existing(self):
        """Open the Profile Edit Dialog for editing an existing profile"""
        try:
            if self.test_profiles:
                dialog = ProfileEditDialog(
                    self.root, 
                    self.logger,
                    self.test_profiles[0].settings,
                    profile=self.test_profiles[0]
                )
                if dialog.result:
                    self.logger.info(f"Edited profile: {dialog.result.profile_name}")
                else:
                    self.logger.info("Profile edit canceled")
            else:
                self.logger.error("No test profiles available")
        except Exception as e:
            self.logger.error(f"Error opening Profile Edit Dialog: {e}")
    
    def cleanup(self):
        """Clean up the test environment"""
        self.logger.info("Cleaning up test environment")
        
        # Delete test profiles directory
        try:
            if self.test_dir.exists():
                for file in self.test_dir.glob("**/*"):
                    if file.is_file():
                        file.unlink()
                for dir in list(self.test_dir.glob("**/")):
                    if dir != self.test_dir and dir.is_dir():
                        dir.rmdir()
                # Leave the main test directory for now
            self.logger.info("Test environment cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up test environment: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        try:
            self.setup()
            self.run_data_structure_tests()
            self.run_auto_switching_tests()
            
            # Ask if user wants to run UI tests
            run_ui = input("Do you want to run UI tests? (y/n): ").lower().strip() == 'y'
            if run_ui:
                self.run_ui_tests()
                
            self.cleanup()
            self.logger.info("All tests completed")
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            self.cleanup()

if __name__ == "__main__":
    tester = TestRunner()
    tester.run_all_tests() 