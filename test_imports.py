print("Testing Python path setup...")
import sys
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
try:
    from daoc_sprint_manager.core.icon_detector import IconDetector
    print("Successfully imported IconDetector")
except ImportError as e:
    print(f"Failed to import IconDetector: {e}")

