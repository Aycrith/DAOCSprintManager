"""
ProfileIOManager for handling loading and saving of user profiles.
"""
import json
import logging
import pathlib
from typing import List, Optional, Union, Any
from datetime import datetime
import uuid

try:
    # Assuming data_models.py is in the parent directory relative to core/
    from ..data_models import Profile, AppSettings, PYDANTIC_AVAILABLE
except ImportError:
    # Fallback for testing or if structure is different
    # This assumes data_models.py is accessible in the Python path
    from daoc_sprint_manager.data_models import Profile, AppSettings, PYDANTIC_AVAILABLE


class ProfileIOManager:
    """
    Manages loading and saving of user profiles from/to a JSON file.
    """

    def __init__(self, profiles_dir: Union[str, pathlib.Path], logger: logging.Logger):
        """
        Initializes the ProfileIOManager.

        Args:
            profiles_dir: The directory where profiles.json will be stored.
            logger: The logger instance.
        """
        self.logger = logger
        self.profiles_dir = pathlib.Path(profiles_dir)
        self.profiles_file_path = self.profiles_dir / "profiles.json"

        try:
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"ProfileIOManager initialized. Profiles will be stored in: {self.profiles_file_path}")
        except OSError as e:
            self.logger.error(f"Could not create profiles directory {self.profiles_dir}: {e}", exc_info=True)
            # Depending on desired robustness, could raise an error here or proceed,
            # knowing load/save will likely fail.

    def load_profiles(self) -> List[Profile]:
        """
        Loads all profiles from the profiles.json file.

        Returns:
            A list of Profile objects. Returns an empty list if the file
            doesn't exist, is empty, or contains corrupted data.
        """
        if not self.profiles_file_path.exists():
            self.logger.info(f"Profiles file not found at {self.profiles_file_path}. Returning empty list.")
            return []

        try:
            with open(self.profiles_file_path, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)
            
            if not isinstance(profiles_data, list):
                self.logger.error(f"Profiles file {self.profiles_file_path} does not contain a list. Corrupted data?")
                return []

            loaded_profiles: List[Profile] = []
            for i, profile_data in enumerate(profiles_data):
                try:
                    if PYDANTIC_AVAILABLE:
                        # Pydantic will handle string-to-datetime conversion if dates are ISO strings
                        profile = Profile(**profile_data)
                    else:
                        # Manual instantiation, need to handle datetime strings
                        # Pydantic's BaseModel created for fallback will convert datetime from ISO string
                        # if they are passed as strings. If they are already datetime, it's fine.
                        profile_data_copy = profile_data.copy()
                        for date_field in ['creation_date', 'last_used_date']:
                            if date_field in profile_data_copy and isinstance(profile_data_copy[date_field], str):
                                try:
                                    profile_data_copy[date_field] = datetime.fromisoformat(profile_data_copy[date_field].replace("Z", "+00:00"))
                                except ValueError:
                                    self.logger.warning(f"Could not parse date string '{profile_data_copy[date_field]}' for field '{date_field}' in profile {i}. Using current UTC time.")
                                    profile_data_copy[date_field] = datetime.utcnow()
                        
                        # Ensure app_settings is an AppSettings instance
                        if 'app_settings' in profile_data_copy and isinstance(profile_data_copy['app_settings'], dict):
                            profile_data_copy['app_settings'] = AppSettings(**profile_data_copy['app_settings'])
                        
                        profile = Profile(**profile_data_copy)
                    loaded_profiles.append(profile)
                except Exception as e: # Catch Pydantic ValidationError or other instantiation errors
                    self.logger.error(f"Error deserializing profile at index {i} from {self.profiles_file_path}: {e}", exc_info=True)
                    # Optionally, skip this profile and continue with others
            
            self.logger.info(f"Successfully loaded {len(loaded_profiles)} profiles from {self.profiles_file_path}.")
            return loaded_profiles

        except FileNotFoundError:
            self.logger.info(f"Profiles file not found at {self.profiles_file_path} (should not happen if exists() check passed). Returning empty list.")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from {self.profiles_file_path}: {e}. Returning empty list.", exc_info=False)
            return []
        except (IOError, OSError) as e:
            self.logger.error(f"IOError/OSError reading profiles file {self.profiles_file_path}: {e}. Returning empty list.", exc_info=True)
            return []


    def save_profiles(self, profiles: List[Profile]) -> bool:
        """
        Saves the list of profiles to the profiles.json file.

        Args:
            profiles: A list of Profile objects to save.

        Returns:
            True if saving was successful, False otherwise.
        """
        
        def datetime_serializer(obj: Any) -> Optional[str]:
            """JSON serializer for datetime objects."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            return None # Let default serializer handle other types or raise TypeError

        profiles_data_to_save: List[Dict] = []
        for profile in profiles:
            if PYDANTIC_AVAILABLE:
                # Pydantic's dict method handles datetime via json_encoders in Config
                profiles_data_to_save.append(profile.dict())
            else:
                # Manual serialization
                profile_dict = vars(profile).copy() # shallow copy
                # Ensure app_settings is also a dict
                if isinstance(profile_dict.get('app_settings'), AppSettings):
                     profile_dict['app_settings'] = vars(profile_dict['app_settings']).copy()

                # Convert datetime objects to ISO strings for JSON compatibility
                for key, value in profile_dict.items():
                    if isinstance(value, datetime):
                        profile_dict[key] = value.isoformat()
                profiles_data_to_save.append(profile_dict)


        try:
            with open(self.profiles_file_path, 'w', encoding='utf-8') as f:
                if PYDANTIC_AVAILABLE:
                    # For Pydantic, we can get JSON strings directly that handle datetime
                    json_list = [p.json() for p in profiles]
                    # Since p.json() returns a string, we need to load it back to a dict
                    # to save the whole list as a single JSON array.
                    # This is inefficient. Better to use .dict() and a custom default handler for json.dump
                    profiles_as_dicts_for_json = [p.dict() for p in profiles]
                    json.dump(profiles_as_dicts_for_json, f, indent=4, default=str) # Pydantic's dict should make datetimes serializable
                else:
                    # Non-Pydantic path, datetimes already converted to ISO strings
                    json.dump(profiles_data_to_save, f, indent=4)

            self.logger.info(f"Successfully saved {len(profiles)} profiles to {self.profiles_file_path}.")
            return True
        except (IOError, OSError, PermissionError) as e:
            self.logger.error(f"Error saving profiles to {self.profiles_file_path}: {e}", exc_info=True)
            return False
        except TypeError as e: # For non-serializable types
            self.logger.error(f"TypeError during JSON serialization of profiles: {e}", exc_info=True)
            return False

if __name__ == "__main__":
    # Setup basic logger for testing
    test_logs_dir = pathlib.Path("./temp_profile_io_logs")
    test_logs_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = test_logs_dir / "profile_io_test.log"
    
    test_logger = logging.getLogger("ProfileIOManagerTest")
    test_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers to prevent duplicate logs in interactive sessions
    if test_logger.hasHandlers():
        test_logger.handlers.clear()
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    test_logger.addHandler(console_handler)
    file_handler = logging.FileHandler(log_file_path, mode='w') # Overwrite for each test run
    file_handler.setFormatter(formatter)
    test_logger.addHandler(file_handler)

    test_logger.info("--- Starting ProfileIOManager Self-Test ---")

    # Create a temporary directory for profiles
    import tempfile
    with tempfile.TemporaryDirectory(prefix="pydaoc_profiles_test_") as tmpdir_name:
        profiles_test_dir = pathlib.Path(tmpdir_name)
        test_logger.info(f"Using temporary profiles directory: {profiles_test_dir}")

        io_manager = ProfileIOManager(profiles_dir=profiles_test_dir, logger=test_logger)

        # Test Case 1: Load profiles when file doesn't exist
        test_logger.info("\n--- Test Case 1: Load profiles (file non-existent) ---")
        profiles1 = io_manager.load_profiles()
        assert profiles1 == [], f"Expected empty list, got {profiles1}"
        test_logger.info(f"Result: {profiles1} (Correct)")

        # Test Case 2: Save and load profiles
        test_logger.info("\n--- Test Case 2: Save and Load Profiles ---")
        sample_profiles: List[Profile] = [
            Profile(profile_name="Profile Alpha", app_settings=AppSettings(sprint_key="a")),
            Profile(profile_name="Profile Beta", game_character_name="BetaChar", app_settings=AppSettings(roi_x=10, capture_fps=15.0)),
            Profile(profile_name="Default Profile From Test", app_settings=AppSettings()) # Test with all defaults
        ]
        # Manually update last_used_date for one to test sorting or display later
        sample_profiles[1].last_used_date = datetime.utcnow() - datetime.timedelta(days=1)


        save_success = io_manager.save_profiles(sample_profiles)
        assert save_success, "Failed to save profiles"
        test_logger.info(f"Save success: {save_success}")

        loaded_profiles_2 = io_manager.load_profiles()
        assert len(loaded_profiles_2) == len(sample_profiles), \
            f"Expected {len(sample_profiles)} profiles, loaded {len(loaded_profiles_2)}"
        
        # Basic check (more thorough checks would compare all fields)
        for original, loaded in zip(sample_profiles, loaded_profiles_2):
            assert original.profile_name == loaded.profile_name, "Profile names don't match"
            assert original.profile_id == loaded.profile_id, "Profile IDs don't match"
            assert original.app_settings.sprint_key == loaded.app_settings.sprint_key, "Sprint keys in AppSettings don't match"
            # Datetime comparison needs care due to potential microsecond differences or timezone awareness
            # For Pydantic, if they are parsed back correctly, they should be comparable.
            # If not using Pydantic, ensure ISO format strings are parsed back to offset-aware UTC datetimes.
            if PYDANTIC_AVAILABLE: # Pydantic handles datetime precision well
                 assert abs((original.creation_date - loaded.creation_date).total_seconds()) < 1, "Creation dates don't match closely"
                 assert abs((original.last_used_date - loaded.last_used_date).total_seconds()) < 1, "Last used dates don't match closely"

            test_logger.info(f"Compared original '{original.profile_name}' with loaded '{loaded.profile_name}'.")

        test_logger.info("Save and load test passed.")

        # Test Case 3: Load from a corrupted JSON file
        test_logger.info("\n--- Test Case 3: Load from corrupted JSON ---")
        with open(io_manager.profiles_file_path, 'w', encoding='utf-8') as f:
            f.write("{corrupted_json: [}")
        
        profiles3 = io_manager.load_profiles()
        assert profiles3 == [], f"Expected empty list from corrupted JSON, got {profiles3}"
        test_logger.info(f"Result from corrupted JSON: {profiles3} (Correct)")

        # Test Case 4: Load from file with one corrupted profile entry
        test_logger.info("\n--- Test Case 4: Load with one corrupted profile entry ---")
        valid_profile_dict = sample_profiles[0].dict() if PYDANTIC_AVAILABLE else vars(sample_profiles[0]).copy()
        if not PYDANTIC_AVAILABLE and isinstance(valid_profile_dict.get('app_settings'), AppSettings): # manual dict conversion
            valid_profile_dict['app_settings'] = vars(valid_profile_dict['app_settings']).copy()
        for k, v in valid_profile_dict.items():
            if isinstance(v, datetime): valid_profile_dict[k] = v.isoformat()

        corrupted_entry_list = [
            valid_profile_dict,
            {"profile_name": "Good Profile 2", "app_settings": {"sprint_key": "x"}, "profile_id": str(uuid.uuid4()), "creation_date": datetime.utcnow().isoformat(), "last_used_date": datetime.utcnow().isoformat(), "version": 1}, # Mostly valid
            {"profile_name": None, "app_settings": {}} # Invalid: profile_name is None (or missing)
        ]
        with open(io_manager.profiles_file_path, 'w', encoding='utf-8') as f:
            json.dump(corrupted_entry_list, f, indent=4)
        
        profiles4 = io_manager.load_profiles()
        # Should load 2 profiles if Pydantic is used (as profile_name=None is invalid)
        # If Pydantic is not used, and Profile class allows None name, might load 3.
        # The Profile class has a validator for non-empty name.
        expected_count = 2
        assert len(profiles4) == expected_count, f"Expected {expected_count} profiles from partially corrupted JSON, got {len(profiles4)}"
        test_logger.info(f"Loaded {len(profiles4)} profiles from partially corrupted file (Correct)")

    test_logger.info("--- ProfileIOManager Self-Test Complete ---")

    # Clean up test log directory
    try:
        import shutil
        shutil.rmtree(test_logs_dir)
        print(f"Cleaned up temporary log directory: {test_logs_dir}")
    except Exception as e:
        print(f"Error cleaning up temp log directory: {e}")