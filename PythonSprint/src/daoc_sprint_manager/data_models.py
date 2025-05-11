"""
Data model definitions for the application settings.

Contains Pydantic models for configuration settings with validation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import uuid

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for basic functionality if pydantic is not available
    PYDANTIC_AVAILABLE = False
    # Create minimal BaseModel and Field replacements for compatibility
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
            self.__post_init__()

        def __post_init__(self):
            """Optional initialization hook for subclasses."""
            pass

    def Field(default=None, **kwargs): # type: ignore
        return default

    def validator(*args, **kwargs): # type: ignore
        def decorator(func):
            return func
        return decorator

class AppSettings(BaseModel):
    """
    Application settings model with validation.

    Defines all configurable parameters with defaults and validation.
    """

    # Game Window Settings
    game_window_title: str = Field(
        "Dark Age of Camelot",
        description="Window title to search for. Should match a unique part of the game's window title."
    )

    # Region of Interest Settings
    roi_x: int = Field(
        0,
        description="X-coordinate of the top-left corner of the region of interest in the game window."
    )
    roi_y: int = Field(
        0,
        description="Y-coordinate of the top-left corner of the region of interest in the game window."
    )
    roi_width: int = Field(
        100,
        description="Width of the region of interest in pixels."
    )
    roi_height: int = Field(
        100,
        description="Height of the region of interest in pixels."
    )

    # Icon Template Settings
    sprint_on_icon_path: str = Field(
        "data/icon_templates/sprint_on.png",
        description="Path to the sprint 'ON' icon template image, relative to the project root."
    )
    sprint_off_icon_path: str = Field(
        "data/icon_templates/sprint_off.png",
        description="Path to the sprint 'OFF' icon template image, relative to the project root."
    )
    template_match_threshold: float = Field(
        0.8,
        description="Confidence threshold for template matching (0.0-1.0). Higher values require closer matches."
    )

    # Temporal Consistency Settings
    temporal_consistency_frames: int = Field(
        3,
        description="Number of consecutive consistent frames required to confirm a state change."
    )

    # Input Settings
    sprint_key: str = Field(
        "z",
        description="Keyboard key to press/release for sprint toggle (using pydirectinput key names)."
    )

    # Performance Settings
    capture_fps: float = Field(
        10.0,
        description="Target frames per second for capture and detection loop."
    )
    game_not_found_retry_delay_s: float = Field(
        2.0,
        description="Delay in seconds between retries when game window is not found."
    )
    capture_error_retry_delay_s: float = Field(
        1.0,
        description="Delay in seconds between retries when capture fails."
    )
    show_performance_metrics: bool = Field(
        True,
        description="Whether to periodically log performance metrics."
    )

    # Cache Settings
    enable_detection_cache: bool = Field(
        True,
        description="Whether to cache detection results to reduce redundant processing."
    )
    detection_cache_size: int = Field(
        50,
        description="Maximum number of frames to keep in the detection cache."
    )
    detection_cache_ttl_s: float = Field(
        0.5,
        description="Time-to-live for cache entries in seconds. Entries older than this will be reprocessed."
    )

    # Logging Settings
    log_level: str = Field(
        "INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
    log_file_name: str = Field(
        "daoc_sprint_manager.log",
        description="Name of the log file in the logs directory."
    )

    # UI Settings
    app_icon_path: str = Field(
        "data/app_icon.png",
        description="Path to the application icon image for system tray, relative to the project root."
    )

    # Detection Method Setting
    detection_method: str = Field(
        "template",
        description="Detection method to use: 'template' for template matching or 'ml' for machine learning."
    )

    # ML Detection Settings
    ml_model_path: str = Field(
        "data/models/sprint_classifier.onnx",
        description="Path to the ONNX ML model file, relative to the project root."
    )
    ml_input_size_wh: List[int] = Field(
        default_factory=lambda: [32, 32], # Ensures new list instance
        description="Required input size for the ML model as [width, height] in pixels."
    )
    ml_confidence_threshold: float = Field(
        0.7,
        description="Confidence threshold for ML detection (0.0-1.0). Higher values require higher confidence."
    )
    save_problematic_frames: bool = Field(
        False,
        description="Whether to save frames with uncertain detection scores."
    )
    problematic_frame_save_path: str = Field(
        "data/problem_frames",
        description="Relative path to save problematic frames."
    )
    
    # Active Profile Setting
    active_profile_id: Optional[str] = Field(
        None,
        description="The ID of the currently active profile, if any."
    )
    
    # Auto Profile Switching Setting
    enable_auto_profile_switching: bool = Field(
        True,
        description="Whether to automatically switch profiles based on window title patterns."
    )

    if PYDANTIC_AVAILABLE:
        @validator('template_match_threshold', 'ml_confidence_threshold', allow_reuse=True)
        def validate_threshold_range(cls, v):
            """Validate that the thresholds are within the valid range."""
            if not 0.0 <= v <= 1.0:
                raise ValueError("Threshold values must be between 0.0 and 1.0")
            return v

        @validator('detection_cache_size', allow_reuse=True)
        def validate_cache_size(cls, v):
            """Validate that the cache size is within a reasonable range."""
            if v < 10:
                raise ValueError("Detection cache size must be at least 10")
            if v > 1000: # Increased upper limit
                raise ValueError("Detection cache size must be at most 1000")
            return v

        @validator('detection_cache_ttl_s', allow_reuse=True)
        def validate_cache_ttl(cls, v):
            """Validate that the cache TTL is within a reasonable range."""
            if v < 0.1:
                raise ValueError("Detection cache TTL must be at least 0.1 seconds")
            if v > 10.0: # Increased upper limit slightly
                raise ValueError("Detection cache TTL must be at most 10.0 seconds")
            return v

        @validator('temporal_consistency_frames', allow_reuse=True)
        def validate_consistency_frames(cls, v):
            """Validate that the consistency frames count is reasonable."""
            if v < 1:
                raise ValueError("Temporal consistency frames must be at least 1")
            if v > 20: # Arbitrary upper limit for sanity check
                raise ValueError("Temporal consistency frames value too high, maximum is 20")
            return v

        @validator('capture_fps', allow_reuse=True)
        def validate_fps(cls, v):
            """Validate that the FPS is positive and reasonable."""
            if v <= 0:
                raise ValueError("Capture FPS must be greater than 0")
            if v > 120: # Increased upper limit slightly
                raise ValueError("Capture FPS too high, maximum is 120")
            return v

        @validator('log_level', allow_reuse=True)
        def validate_log_level(cls, v):
            """Validate that the log level is a standard Python logging level."""
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if v.upper() not in valid_levels:
                raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
            return v.upper()

        @validator('ml_input_size_wh', allow_reuse=True)
        def validate_ml_input_size(cls, v):
            """Validate ML input size format and values."""
            if not isinstance(v, list) or len(v) != 2:
                raise ValueError("ML input size must be a list of exactly 2 integers [width, height]")
            if not all(isinstance(dim, int) for dim in v) or v[0] <= 0 or v[1] <= 0:
                raise ValueError("ML input dimensions must be positive integers")
            return v

        @validator('detection_method', allow_reuse=True)
        def validate_detection_method(cls, v):
            """Validate that detection_method is an allowed value."""
            allowed_methods = ["template", "ml"]
            if v not in allowed_methods:
                raise ValueError(f"Detection method must be one of: {', '.join(allowed_methods)}")
            return v
    else: # Basic validation if Pydantic is not available
        def __post_init__(self):
            """Perform additional validation if pydantic is not available."""
            if not 0.0 <= getattr(self, 'template_match_threshold', 0.8) <= 1.0:
                raise ValueError("Template match threshold must be between 0.0 and 1.0")
            if not 0.0 <= getattr(self, 'ml_confidence_threshold', 0.7) <= 1.0:
                raise ValueError("ML confidence threshold must be between 0.0 and 1.0")
            if getattr(self, 'temporal_consistency_frames', 3) < 1:
                raise ValueError("Temporal consistency frames must be at least 1")
            ml_input_size = getattr(self, 'ml_input_size_wh', [32,32])
            if not (isinstance(ml_input_size, list) and len(ml_input_size) == 2 and
                    isinstance(ml_input_size[0], int) and ml_input_size[0] > 0 and
                    isinstance(ml_input_size[1], int) and ml_input_size[1] > 0):
                raise ValueError("ml_input_size_wh must be a list of two positive integers")
            detection_method = getattr(self, 'detection_method', 'template')
            if detection_method not in ["template", "ml"]:
                raise ValueError("Detection method must be one of: template, ml")


class Profile(BaseModel):
    """
    User profile model with validation.

    Defines a user profile that stores profile metadata and application settings.
    Each profile represents a saved configuration that users can switch between.
    """

    # Profile Metadata
    profile_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the profile."
    )
    profile_name: str = Field(
        ...,
        min_length=1, # Pydantic specific validation
        description="User-friendly name for the profile (e.g., 'My Main Character', 'Default Settings')."
    )
    creation_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of when the profile was created."
    )
    last_used_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of when the profile was last used."
    )
    version: int = Field(
        1,
        description="Profile structure version for future migrations."
    )
    game_character_name: Optional[str] = Field(
        None,
        description="Name of the associated in-game character (optional)."
    )
    window_title_pattern: Optional[str] = Field(
        None,
        description="Pattern to match against game window titles for auto-switching to this profile."
    )

    # Application Settings
    app_settings: AppSettings = Field(
        default_factory=AppSettings, # Ensure it's always an AppSettings instance
        description="Application settings associated with this profile."
    )

    if PYDANTIC_AVAILABLE:
        @validator('profile_name')
        def validate_profile_name_not_empty(cls, v):
            """Validate that the profile name is not empty."""
            if not v or not v.strip():
                raise ValueError("Profile name cannot be empty or just whitespace")
            return v.strip() # Return stripped name
    else: # Basic validation if Pydantic is not available
        def __post_init__(self):
            """Perform additional validation if pydantic is not available."""
            profile_name_val = getattr(self, 'profile_name', None)
            if not profile_name_val or not profile_name_val.strip():
                raise ValueError("Profile name cannot be empty or just whitespace")
            
            app_settings_val = getattr(self, 'app_settings', None)
            if not isinstance(app_settings_val, AppSettings):
                # If not Pydantic, app_settings might be a dict, try to coerce
                if isinstance(app_settings_val, dict):
                    try:
                        self.app_settings = AppSettings(**app_settings_val)
                    except Exception as e:
                        raise ValueError(f"app_settings dictionary could not be converted to AppSettings: {e}")
                else:
                    raise ValueError("app_settings must be an instance of AppSettings or a compatible dictionary")
            
            # Ensure dates are datetime objects
            for date_field in ['creation_date', 'last_used_date']:
                date_val = getattr(self, date_field)
                if isinstance(date_val, str):
                    try:
                        setattr(self, date_field, datetime.fromisoformat(date_val.replace("Z", "+00:00")))
                    except ValueError:
                         # Fallback if not perfect ISO, might need to set to now or raise error
                         setattr(self, date_field, datetime.utcnow())
                elif not isinstance(date_val, datetime):
                    setattr(self, date_field, datetime.utcnow())


    # For Pydantic v1 compatibility of dict() and json()
    if PYDANTIC_AVAILABLE:
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }


if __name__ == "__main__":
    """Test the AppSettings and Profile models with sample data."""
    import json
    import sys

    print("Testing AppSettings data model")

    # Test creating with default values
    print("\nCreating with default values:")
    default_settings = AppSettings()
    print(f"Game window title: {default_settings.game_window_title}")
    print(f"ROI: {default_settings.roi_x}, {default_settings.roi_y}, {default_settings.roi_width}x{default_settings.roi_height}")
    print(f"Template threshold: {default_settings.template_match_threshold}")
    print(f"Consistency frames: {default_settings.temporal_consistency_frames}")
    print(f"ML model path: {default_settings.ml_model_path}")
    print(f"ML input size: {default_settings.ml_input_size_wh}")
    print(f"ML threshold: {default_settings.ml_confidence_threshold}")
    print(f"Active Profile ID: {default_settings.active_profile_id}")


    # Test creating with custom values
    print("\nCreating with custom values:")
    custom_settings_data = {
        "game_window_title": "Custom Game Title",
        "roi_x": 100,
        "roi_y": 200,
        "roi_width": 300,
        "roi_height": 150,
        "template_match_threshold": 0.9,
        "temporal_consistency_frames": 5,
        "log_level": "DEBUG",
        "ml_input_size_wh": [64, 64],
        "ml_confidence_threshold": 0.85,
        "active_profile_id": "some-active-id"
    }
    custom_settings = AppSettings(**custom_settings_data)
    print(f"Game window title: {custom_settings.game_window_title}")
    print(f"ROI: {custom_settings.roi_x}, {custom_settings.roi_y}, {custom_settings.roi_width}x{custom_settings.roi_height}")
    print(f"Template threshold: {custom_settings.template_match_threshold}")
    print(f"Consistency frames: {custom_settings.temporal_consistency_frames}")
    print(f"Log level: {custom_settings.log_level}")
    print(f"ML input size: {custom_settings.ml_input_size_wh}")
    print(f"ML threshold: {custom_settings.ml_confidence_threshold}")
    print(f"Active Profile ID: {custom_settings.active_profile_id}")


    # Test JSON serialization if pydantic is available
    if PYDANTIC_AVAILABLE:
        print("\nJSON serialization (requires pydantic):")
        json_str = custom_settings.json(indent=2) # Pydantic v1
        # For Pydantic v2, it would be: json_str = custom_settings.model_dump_json(indent=2)
        print(json_str)

        # Test deserializing from JSON
        print("\nDeserializing from JSON:")
        deserialized = AppSettings.parse_raw(json_str) # Pydantic v1
        # For Pydantic v2: deserialized = AppSettings.model_validate_json(json_str)
        print(f"Deserialized game title: {deserialized.game_window_title}")

        # Test validation errors
        print("\nTesting validation:")
        try:
            invalid_settings = AppSettings(template_match_threshold=1.5)
            print("❌ Validation should have failed but didn't")
        except ValueError as e:
            print(f"✅ Expected validation error: {e}")

        # Test ML-specific validation
        print("\nTesting ML validation:")
        try:
            invalid_ml_settings = AppSettings(ml_input_size_wh=[0, 32])
            print("❌ ML validation should have failed but didn't")
        except ValueError as e:
            print(f"✅ Expected ML validation error: {e}")

        # Test detection_method validation
        print("\nTesting detection_method validation:")
        try:
            invalid_detection_method = AppSettings(detection_method="invalid_method")
            print("❌ Validation for detection_method should have failed but didn't")
        except ValueError as e:
            print(f"✅ Expected validation error for detection_method: {e}")
    else:
        print("\nPydantic not available, skipping JSON serialization tests")

    print("\nAppSettings tests complete")

    # Test Profile data model
    print("\n" + "="*50)
    print("Testing Profile data model")
    print("="*50)

    # Create a default profile with default settings
    print("\nCreating a profile with default settings:")
    default_profile = Profile(
        profile_name="Default Profile",
        app_settings=AppSettings() # Uses default AppSettings
    )
    print(f"Profile ID: {default_profile.profile_id}")
    print(f"Profile Name: {default_profile.profile_name}")
    print(f"Creation Date: {default_profile.creation_date}")
    print(f"Last Used Date: {default_profile.last_used_date}")
    print(f"Version: {default_profile.version}")
    print(f"Game Character Name: {default_profile.game_character_name}")
    print(f"App Settings - Game Window Title: {default_profile.app_settings.game_window_title}")
    print(f"App Settings - Active Profile ID (from profile's app_settings): {default_profile.app_settings.active_profile_id}")


    # Create a custom profile with custom settings
    print("\nCreating a profile with custom settings:")
    custom_profile_app_settings = AppSettings(
            game_window_title="Dark Age of Camelot - CharName",
            sprint_key="s",
            template_match_threshold=0.9,
            active_profile_id="custom-profile-is-active" # Example
        )
    custom_profile = Profile(
        profile_name="My Main Character",
        game_character_name="CharacterName",
        app_settings=custom_profile_app_settings
    )
    print(f"Profile ID: {custom_profile.profile_id}")
    print(f"Profile Name: {custom_profile.profile_name}")
    print(f"Game Character Name: {custom_profile.game_character_name}")
    print(f"App Settings - Game Window Title: {custom_profile.app_settings.game_window_title}")
    print(f"App Settings - Sprint Key: {custom_profile.app_settings.sprint_key}")
    print(f"App Settings - Active Profile ID (from profile's app_settings): {custom_profile.app_settings.active_profile_id}")


    # Test serialization if pydantic is available
    if PYDANTIC_AVAILABLE:
        print("\nProfile serialization to dict:")
        profile_dict = custom_profile.dict() # Pydantic v1
        # For Pydantic v2: profile_dict = custom_profile.model_dump()
        print(json.dumps(profile_dict, indent=2, default=str))

        print("\nDeserializing profile from dict:")
        # For Pydantic, datetime string conversion to datetime objects is handled by default during parsing.
        # So, ensure the string is in ISO format if it was manually created.
        # Pydantic's .dict() often serializes datetime to datetime objects,
        # json.dumps with default=str handles it. For parsing, Pydantic handles ISO strings.
        
        # Example: If profile_dict was from a file and dates were strings:
        # profile_dict_from_json = json.loads(json.dumps(profile_dict, default=str))
        # deserialized_profile = Profile(**profile_dict_from_json) # Pydantic will parse ISO strings
        
        deserialized_profile = Profile(**profile_dict) # Should work directly if dict() keeps datetime objects
        
        print(f"Deserialized Profile Name: {deserialized_profile.profile_name}")
        print(f"Deserialized Game Character: {deserialized_profile.game_character_name}")
        print(f"Deserialized Creation Date type: {type(deserialized_profile.creation_date)}")


        # Test validation
        print("\nTesting profile validation:")
        try:
            invalid_profile = Profile(
                profile_name="   ",  # Empty/whitespace name should fail validation
                app_settings=AppSettings()
            )
            print("❌ Profile validation for name should have failed but didn't")
        except ValueError as e:
            print(f"✅ Expected profile validation error for name: {e}")
    else:
        print("\nPydantic not available, skipping Profile serialization tests")

    print("\nProfile tests complete")
