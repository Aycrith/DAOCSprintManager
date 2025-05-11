"""
pytest configuration file for DAOC Sprint Manager tests
"""

import os
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add the project root and src directories to Python path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "testing")) 