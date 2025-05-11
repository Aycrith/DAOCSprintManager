#!/usr/bin/env python3
"""
Build Script for DAOC Sprint Manager
==================================

This script builds the DAOC Sprint Manager executable using PyInstaller.
"""

import os
import sys
from pathlib import Path

import PyInstaller.__main__

def ensure_resources():
    """Ensure required resources exist."""
    project_root = Path(__file__).parent.parent.absolute()
    resources_dir = project_root / 'resources'
    
    # Create resources directory if it doesn't exist
    resources_dir.mkdir(exist_ok=True)
    
    # Create placeholder icon if it doesn't exist
    icon_path = resources_dir / 'icon.ico'
    if not icon_path.exists():
        print("Warning: icon.ico not found, using default PyInstaller icon")
        return None
    return str(icon_path)

def build_executable():
    """Build the DAOC Sprint Manager executable."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.absolute()
    
    # Set the entry point
    entry_point = project_root / 'src' / 'daoc_sprint_manager' / 'main.py'
    
    # Check resources
    icon_path = ensure_resources()
    resources_dir = project_root / 'resources'
    
    # Define PyInstaller arguments
    args = [
        str(entry_point),  # Entry point script
        '--name=DAOCSprintManager',  # Output name
        '--onefile',  # Create a single executable
        '--noconsole',  # Don't show console window
        f'--distpath={project_root / "dist"}',  # Output directory
        f'--workpath={project_root / "build"}',  # Working directory
        f'--specpath={project_root / "build"}',  # Spec file directory
        '--clean',  # Clean PyInstaller cache
    ]
    
    # Add icon if available
    if icon_path:
        args.extend(['--icon', icon_path])
    
    # Add resources directory if it exists and has files
    if resources_dir.exists() and any(resources_dir.iterdir()):
        args.extend(['--add-data', f'{resources_dir};resources'])
    
    print("Building with arguments:", args)
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == '__main__':
    try:
        build_executable()
        sys.exit(0)
    except Exception as e:
        print(f"Error during PyInstaller build:\n{str(e)}", file=sys.stderr)
        sys.exit(1) 