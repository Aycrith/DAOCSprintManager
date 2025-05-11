"""
Manages keyboard input simulation using pydirectinput.

Provides methods to safely press, release, and send keypresses, primarily
for interacting with game clients or other applications. Includes validation
for supported key codes.
"""

import logging
import time
from typing import Set

try:
    import pydirectinput
    # Populate VALID_KEYS once at import time
    VALID_KEYS: Set[str] = set(pydirectinput.KEY_NAMES)
    PYDIRECTINPUT_AVAILABLE = True
except ImportError:
    # Create a dummy set if pydirectinput is not installed, allowing basic testing
    # In a real scenario, this module would likely fail later if not available.
    VALID_KEYS: Set[str] = set(['a', 'b', 'c', 'space', 'enter', 'f1', 'f6', 'r', 'z']) # Example keys
    PYDIRECTINPUT_AVAILABLE = False
    # We should log this, but a logger might not be available at import time.
    # A warning will be logged in the __init__ if needed.

class InputManager:
    """
    Handles sending keyboard inputs using pydirectinput.

    Encapsulates key press and release actions, including validation and delays.

    CRITICAL USER RESPONSIBILITY: Automated input may violate game End User
    License Agreements (EULA). Use of this module is at the user's own risk.
    Ensure compliance with all game rules to avoid account penalties.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initializes the InputManager.

        Args:
            logger: Logger instance for recording operations and errors.
        """
        self.logger = logger
        if not PYDIRECTINPUT_AVAILABLE:
            self.logger.critical(
                "pydirectinput library is not installed. Input functionality will not work. "
                "Install it using: pip install pydirectinput"
            )
        self.logger.debug("InputManager initialized.")

    def _is_valid_key(self, key_code: str) -> bool:
        """
        Checks if the given key code is valid according to pydirectinput.

        Args:
            key_code: The key code string (e.g., 'a', 'f6', 'space').

        Returns:
            True if the key code is valid, False otherwise.
        """
        is_valid = key_code.lower() in VALID_KEYS
        if not is_valid:
            self.logger.warning(f"Invalid key code '{key_code}' specified. Input will not be sent.")
        return is_valid

    def press_key(self, key_code: str) -> None:
        """
        Simulates pressing and holding down a key.

        Args:
            key_code: The key code to press (must be a valid pydirectinput key).

        Raises:
            RuntimeError: If pydirectinput is not available.
            pydirectinput.PyDirectInputException: If pydirectinput fails.
        """
        if not PYDIRECTINPUT_AVAILABLE:
            self.logger.error("Cannot press key: pydirectinput is not available.")
            raise RuntimeError("pydirectinput is not installed")

        if not self._is_valid_key(key_code):
            return

        try:
            self.logger.debug(f"Pressing key: '{key_code}'")
            pydirectinput.keyDown(key_code) # Use keyDown for press
        except pydirectinput.PyDirectInputException as e:
            self.logger.error(f"pydirectinput error pressing key '{key_code}': {e}")
            raise # Re-raise the exception to signal failure
        except Exception as e:
            self.logger.exception(f"Unexpected error pressing key '{key_code}': {e}")
            raise

    def release_key(self, key_code: str) -> None:
        """
        Simulates releasing a key.

        Args:
            key_code: The key code to release (must be a valid pydirectinput key).

        Raises:
            RuntimeError: If pydirectinput is not available.
            pydirectinput.PyDirectInputException: If pydirectinput fails.
        """
        if not PYDIRECTINPUT_AVAILABLE:
            self.logger.error("Cannot release key: pydirectinput is not available.")
            raise RuntimeError("pydirectinput is not installed")

        if not self._is_valid_key(key_code):
            return

        try:
            self.logger.debug(f"Releasing key: '{key_code}'")
            pydirectinput.keyUp(key_code) # Use keyUp for release
        except pydirectinput.PyDirectInputException as e:
            self.logger.error(f"pydirectinput error releasing key '{key_code}': {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error releasing key '{key_code}': {e}")
            raise

    def send_keypress(self, key_code: str, press_duration_ms: int = 50) -> None:
        """
        Simulates a full keypress (press, wait, release).

        Args:
            key_code: The key code to send (must be a valid pydirectinput key).
            press_duration_ms: The duration to hold the key down in milliseconds.

        Raises:
            RuntimeError: If pydirectinput is not available.
            pydirectinput.PyDirectInputException: If pydirectinput fails.
        """
        if not PYDIRECTINPUT_AVAILABLE:
            self.logger.error("Cannot send keypress: pydirectinput is not available.")
            raise RuntimeError("pydirectinput is not installed")

        if not self._is_valid_key(key_code):
            self.logger.warning(f"Skipping send_keypress for invalid key: {key_code}")
            return

        try:
            self.logger.info(f"Sending keypress: '{key_code}' (duration: {press_duration_ms}ms)")
            # Use pydirectinput.press for simplified press/release
            # Note: pydirectinput.press doesn't inherently support duration control.
            # For controlled duration, we manually press and release.
            pydirectinput.keyDown(key_code)
            time.sleep(max(0.01, press_duration_ms / 1000.0)) # Ensure a minimum sleep
            pydirectinput.keyUp(key_code)
            self.logger.debug(f"Keypress '{key_code}' completed.")

        except pydirectinput.PyDirectInputException as e:
            self.logger.error(f"pydirectinput error sending keypress '{key_code}': {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error sending keypress '{key_code}': {e}")
            raise


if __name__ == "__main__":
    import sys
    # Set up a basic logger for testing
    test_logger = logging.getLogger("InputManagerTest")
    test_logger.setLevel(logging.DEBUG)
    if not test_logger.handlers: # Avoid adding multiple handlers if run again
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'))
        test_logger.addHandler(handler)

    input_manager = InputManager(test_logger)

    if not PYDIRECTINPUT_AVAILABLE:
        test_logger.warning("pydirectinput not installed, testing is limited.")
        sys.exit(1)

    print("\n--- Testing InputManager ---")
    print("CRITICAL: This test will send a keypress.")
    print("Please focus a text editor (like Notepad) within the next 5 seconds.")
    print("A 'z' keypress will be sent.")
    time.sleep(5)

    try:
        print("\nTest 1: Sending 'z' keypress (duration 100ms)...")
        input_manager.send_keypress('z', press_duration_ms=100)
        print("-> Check your text editor for the 'z' character.")
    except Exception as e:
        print(f"   ERROR during keypress: {e}")

    time.sleep(2)

    try:
        print("\nTest 2: Sending an invalid key ('invalidkeyname')...")
        input_manager.send_keypress('invalidkeyname', press_duration_ms=50)
        print("-> This should log a warning and not send anything.")
    except Exception as e:
        # We don't expect an exception here normally, as validation should prevent it
        print(f"   UNEXPECTED ERROR during invalid keypress: {e}")

    # Test press/release separately (difficult to verify without external tools)
    try:
        print("\nTest 3: Testing press/release separately ('b' key)...")
        print("   Pressing 'b'...")
        input_manager.press_key('b')
        time.sleep(0.5) # Hold for 0.5 sec
        print("   Releasing 'b'...")
        input_manager.release_key('b')
        print("-> If focus was on text editor, 'b' might appear.")
    except Exception as e:
        print(f"   ERROR during press/release test: {e}")


    print("\n--- InputManager Test Complete ---")
    print("Please verify the output in your text editor.") 