#!/usr/bin/env python3
"""
Test the distribution package.

This script verifies that the executable was built correctly and contains
all required resources.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import psutil
import pytest

# Constants
EXE_NAME = "DAOCSprintManager.exe"
DIST_DIR = Path(__file__).parent.parent / "dist"
EXE_PATH = DIST_DIR / EXE_NAME

def test_exe_exists():
    """Test that the executable exists."""
    assert EXE_PATH.exists(), f"Executable not found at {EXE_PATH}"
    assert EXE_PATH.stat().st_size > 1000000, "Executable is too small"

def test_exe_metadata():
    """Test executable metadata."""
    # Basic file info
    stat = EXE_PATH.stat()
    assert stat.st_mode & 0o111, "Executable is not marked as executable"
    
    # File properties
    assert EXE_PATH.suffix == '.exe', "File extension is not .exe"

def test_exe_launch():
    """Test that the executable can be launched."""
    # Launch the executable
    process = subprocess.Popen([str(EXE_PATH)])
    try:
        # Wait for process to start
        time.sleep(2)
        
        # Check if process is running
        assert process.poll() is None, "Process terminated immediately"
        
        # Check if process has expected name
        found = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == EXE_NAME:
                found = True
                break
        assert found, f"Process {EXE_NAME} not found in running processes"
        
    finally:
        # Clean up
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

def test_config_creation():
    """Test that the application creates configuration files correctly."""
    # Get expected config directory
    home = Path.home()
    config_dir = home / '.daoc_sprint_manager'
    config_file = config_dir / 'config.json'
    
    # Remove existing config if present
    if config_dir.exists():
        for file in config_dir.glob('*'):
            file.unlink()
        config_dir.rmdir()
    
    # Launch the executable
    process = subprocess.Popen([str(EXE_PATH)])
    try:
        # Wait for config creation
        time.sleep(2)
        
        # Verify config directory and file
        assert config_dir.exists(), "Config directory not created"
        assert config_file.exists(), "Config file not created"
        
        # Check config content
        content = config_file.read_text()
        assert '"ml_input_size_wh"' in content, "Config missing ml_input_size_wh"
        
    finally:
        # Clean up
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

def test_package_installation():
    """Test that the package can be installed with pip."""
    venv_dir = Path("test_venv")
    if venv_dir.exists():
        import shutil
        shutil.rmtree(venv_dir)
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        
        # Get pip path
        pip = str(venv_dir / "Scripts" / "pip.exe")
        
        # Install package
        result = subprocess.run([pip, "install", "."], 
                              capture_output=True,
                              text=True)
        assert result.returncode == 0, f"Package installation failed:\n{result.stderr}"
        
        # Verify installation
        result = subprocess.run([pip, "show", "daoc-sprint-manager"],
                              capture_output=True,
                              text=True)
        assert result.returncode == 0, "Package not found after installation"
        
    finally:
        # Cleanup
        if venv_dir.exists():
            import shutil
            shutil.rmtree(venv_dir)

if __name__ == '__main__':
    sys.exit(pytest.main([__file__])) 