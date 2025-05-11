"""
Simplified test script for the auto-switching feature.
Focuses on the WindowManager's get_all_window_titles() method and the _check_and_apply_auto_profile_switch algorithm.
"""

import os
import sys
import logging
import time
from typing import Tuple, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AutoSwitchTest")

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

try:
    # Import the WindowManager class
    from daoc_sprint_manager.core.window_manager import WindowManager
except ImportError as e:
    logger.error(f"Error importing WindowManager: {e}")
    if os.path.exists(os.path.join(parent_dir, 'daoc_sprint_manager', 'core', 'window_manager.py')):
        logger.info("The file exists but the import failed. This might be a path or environment issue.")
    else:
        logger.info("The file does not exist at the expected location.")
    sys.exit(1)

class MockProfile:
    """Mock Profile class for testing the auto-switching algorithm"""
    
    def __init__(self, profile_id: str, profile_name: str, window_title_pattern: Optional[str] = None):
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.window_title_pattern = window_title_pattern
        
    def __str__(self):
        return f"Profile(id={self.profile_id}, name={self.profile_name}, pattern={self.window_title_pattern})"

class MockAppSettings:
    """Mock AppSettings class for testing"""
    
    def __init__(self, active_profile_id: str = "default", enable_auto_profile_switching: bool = True):
        self.active_profile_id = active_profile_id
        self.enable_auto_profile_switching = enable_auto_profile_switching

def test_window_manager():
    """Test the WindowManager's get_all_window_titles method"""
    logger.info("Testing WindowManager.get_all_window_titles()")
    
    window_manager = WindowManager(logger)
    window_details = window_manager.get_all_window_titles()
    
    if window_details:
        logger.info(f"Found {len(window_details)} windows:")
        for i, (title, window) in enumerate(window_details[:5]):  # Show first 5 windows
            window_type = type(window).__name__
            logger.info(f"  Window {i+1}: '{title}' (Type: {window_type})")
    else:
        logger.warning("No windows found or an error occurred")
    
    return window_details

def test_auto_switch_algorithm(window_titles: List[Tuple[str, object]]):
    """Test the auto profile switching algorithm with the given window titles"""
    logger.info("\nTesting auto-switching algorithm with real window titles")
    
    # Create mock profiles
    profiles = [
        MockProfile("1", "Default Profile"),
        MockProfile("2", "PowerShell Profile", "PowerShell"),
        MockProfile("3", "Firefox Profile", "Firefox"),
        MockProfile("4", "Chrome Profile", "Chrome"),
        MockProfile("5", "DAoC Test", "DAoC"),
        MockProfile("6", "DAoC Specific Character", "DAoC - Character")
    ]
    
    # Create mock app settings
    app_settings = MockAppSettings(active_profile_id="1")
    
    # Test the algorithm with multiple patterns
    logger.info("Testing algorithm with multiple patterns...")
    
    # Filter window titles to 5 for clarity
    visible_windows = window_titles[:5]
    logger.info(f"Testing with these visible windows:")
    for i, (title, _) in enumerate(visible_windows):
        logger.info(f"  {i+1}. {title}")
    
    # Check each profile against these windows
    for profile in profiles:
        if profile.window_title_pattern:
            logger.info(f"\nChecking profile: {profile.profile_name} (pattern: '{profile.window_title_pattern}')")
            found_match = False
            
            for title, _ in visible_windows:
                if profile.window_title_pattern.lower() in title.lower():
                    logger.info(f"  ✅ Match found: '{title}'")
                    found_match = True
                    
            if not found_match:
                logger.info(f"  ❌ No matching windows for this profile")
    
    # Now simulate the actual auto-switch logic
    logger.info("\nSimulating actual auto-switch logic with all profiles")
    
    # Only check profiles with patterns that are not already active
    matching_profiles = []
    for profile in profiles:
        if (profile.window_title_pattern and 
            profile.profile_id != app_settings.active_profile_id):
            pattern = profile.window_title_pattern.lower()
            
            # Check this pattern against all window titles
            for window_title, _ in visible_windows:
                if pattern in window_title.lower():
                    logger.info(f"Found matching window '{window_title}' for profile '{profile.profile_name}'")
                    matching_profiles.append((profile, len(pattern)))
                    break  # Found a match for this profile, move to next profile
    
    if not matching_profiles:
        logger.info("No matching profiles found")
        return None
        
    # If multiple profiles match, select the one with the most specific pattern
    if len(matching_profiles) > 1:
        matching_profiles.sort(key=lambda p: p[1], reverse=True)
        logger.info(f"Multiple matching profiles found, selecting the most specific one: {matching_profiles[0][0].profile_name}")
    
    selected_profile = matching_profiles[0][0]
    logger.info(f"Auto-switching to profile: {selected_profile.profile_name} based on window title match")
    return selected_profile

def test_with_mock_windows():
    """Test with mock window titles"""
    logger.info("\nTesting with mock window titles")
    
    # Create mock window titles (title, window_object)
    mock_windows = [
        ("DAoC - Character1 Window", None),
        ("DAoC - Character2 Window", None),
        ("Firefox Browser", None),
        ("Notepad", None)
    ]
    
    # Create mock profiles
    profiles = [
        MockProfile("1", "Default Profile"),
        MockProfile("2", "DAoC General", "DAoC"),
        MockProfile("3", "Character1 Profile", "Character1"),
        MockProfile("4", "Character2 Profile", "Character2"),
        MockProfile("5", "Firefox Profile", "Firefox")
    ]
    
    # Create mock app settings
    app_settings = MockAppSettings(active_profile_id="1")
    
    # Only check profiles with patterns that are not already active
    matching_profiles = []
    for profile in profiles:
        if (profile.window_title_pattern and 
            profile.profile_id != app_settings.active_profile_id):
            pattern = profile.window_title_pattern.lower()
            
            # Check this pattern against all window titles
            for window_title, _ in mock_windows:
                if pattern in window_title.lower():
                    logger.info(f"Found matching window '{window_title}' for profile '{profile.profile_name}'")
                    matching_profiles.append((profile, len(pattern)))
                    break  # Found a match for this profile, move to next profile
    
    if not matching_profiles:
        logger.info("No matching profiles found")
        return None
        
    # If multiple profiles match, select the one with the most specific pattern
    if len(matching_profiles) > 1:
        matching_profiles.sort(key=lambda p: p[1], reverse=True)
        logger.info(f"Multiple matching profiles found, selecting the most specific one: {matching_profiles[0][0].profile_name}")
    
    selected_profile = matching_profiles[0][0]
    logger.info(f"Auto-switching to profile: {selected_profile.profile_name} based on window title match")
    return selected_profile

if __name__ == "__main__":
    logger.info("Starting auto-switching feature tests")
    
    # Test with real windows
    try:
        window_details = test_window_manager()
        if window_details:
            test_auto_switch_algorithm(window_details)
    except Exception as e:
        logger.error(f"Error testing with real windows: {e}")
    
    # Test with mock windows
    try:
        test_with_mock_windows()
    except Exception as e:
        logger.error(f"Error testing with mock windows: {e}")
    
    logger.info("Auto-switching tests completed") 