#!/usr/bin/env python
"""
Run the Data Collector UI for gathering training data.

This script provides a convenient way to launch the Data Collector UI
for capturing and managing training data for the DAOC Sprint Manager.
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the package
parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the DataCollectorUI
from daoc_sprint_manager.training.data_collector_ui import main as run_data_collector_ui

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the UI
    run_data_collector_ui() 