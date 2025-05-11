"""
Build script for creating a distributable executable of DAOC Sprint Manager.

This script handles the complete build process including:
- Cleaning build directories
- Running PyInstaller
- Copying documentation and assets
- Verifying the build
- Creating a distribution archive
"""

import os
import re
import shutil
import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'build_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

def get_version() -> str:
    """Extract version from __init__.py or setup.py."""
    # Try __init__.py first
    init_file = Path('src/daoc_sprint_manager/__init__.py')
    if init_file.exists():
        content = init_file.read_text()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    
    # Try setup.py next
    setup_file = Path('setup.py')
    if setup_file.exists():
        content = setup_file.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    
    # Default version if not found
    logging.warning("Version not found in __init__.py or setup.py, using default")
    return "0.3.0"

def check_prerequisites() -> List[str]:
    """Check if all prerequisites are met."""
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        missing.append("Python 3.9 or later required")
    
    # Check PyInstaller
    try:
        import PyInstaller
    except ImportError:
        missing.append("PyInstaller not installed")
    
    # Check required directories exist
    required_dirs = ['assets/icons', 'models', 'config', 'src']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logging.info(f"Created directory: {dir_name}")
            except Exception as e:
                missing.append(f"Failed to create directory '{dir_name}': {str(e)}")
    
    # Check spec file exists
    if not Path('daoc_sprint_manager.spec').exists():
        missing.append("spec file 'daoc_sprint_manager.spec' not found")
    
    return missing

def clean_build_dirs():
    """Remove existing build and dist directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            logging.info(f"Cleaning {dir_name} directory...")
            try:
                shutil.rmtree(dir_name)
            except Exception as e:
                logging.error(f"Failed to clean {dir_name}: {str(e)}")
                raise

def copy_documentation():
    """Copy documentation files to the distribution directory."""
    dist_dir = Path('dist/DAOC Sprint Manager')
    docs_to_copy = {
        'README.md': dist_dir / 'README.md',
        'LICENSE': dist_dir / 'LICENSE',
        'docs/INSTALLATION.md': dist_dir / 'docs/INSTALLATION.md',
        'docs/DISTRIBUTION_GUIDE.md': dist_dir / 'docs/DISTRIBUTION_GUIDE.md',
        'config/settings.json.template': dist_dir / 'config/settings.json.template'
    }
    
    for src, dest in docs_to_copy.items():
        if os.path.exists(src):
            logging.info(f"Copying {src} to distribution...")
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src, dest)
            except Exception as e:
                logging.warning(f"Failed to copy {src}: {str(e)}")

def copy_assets():
    """Copy asset files to the distribution directory."""
    dist_dir = Path('dist/DAOC Sprint Manager')
    assets_dir = dist_dir / 'assets'
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy icon files
    icon_files = {
        'assets/icons/app_icon.ico': assets_dir / 'app_icon.ico',
        'assets/icons/app_icon.png': assets_dir / 'app_icon.png'
    }
    
    for src, dest in icon_files.items():
        src_path = Path(src)
        if src_path.exists():
            logging.info(f"Copying {src} to {dest}...")
            try:
                shutil.copy2(src_path, dest)
            except Exception as e:
                logging.error(f"Failed to copy {src}: {str(e)}")
                raise

def run_pyinstaller() -> subprocess.CompletedProcess:
    """Run PyInstaller with the spec file."""
    logging.info("Building executable with PyInstaller...")
    
    try:
        result = subprocess.run(
            ['pyinstaller', '--clean', 'daoc_sprint_manager.spec'],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("PyInstaller build completed successfully.")
        return result
    except subprocess.CalledProcessError as e:
        logging.error("Error during PyInstaller build:")
        logging.error(e.stderr)
        raise

def verify_build() -> bool:
    """Verify that all necessary files are present in the dist directory."""
    dist_dir = Path('dist/DAOC Sprint Manager')
    required_files = [
        dist_dir / 'DAOC Sprint Manager.exe',
        dist_dir / 'assets/app_icon.ico',
        dist_dir / 'assets/app_icon.png',
        dist_dir / 'models',
        dist_dir / 'config/settings.json.template',
        dist_dir / '_internal',
        dist_dir / 'README.md',
        dist_dir / 'docs/INSTALLATION.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        logging.error("Missing required files in distribution:")
        for file_path in missing_files:
            logging.error(f"  - {file_path}")
        return False
    
    # Verify executable
    exe_path = dist_dir / 'DAOC Sprint Manager.exe'
    if exe_path.exists():
        size = exe_path.stat().st_size
        if size < 1000000:  # Less than 1MB
            logging.error(f"Executable seems too small: {size} bytes")
            return False
    
    logging.info("Build verification completed successfully.")
    return True

def create_distribution_archive(version: str) -> Optional[Path]:
    """Create a ZIP archive of the distribution."""
    dist_dir = Path('dist/DAOC Sprint Manager')
    if not dist_dir.exists():
        logging.error("Distribution directory not found!")
        return None
    
    archive_name = f'DAOCSprintManager_v{version}'
    archive_path = Path(f'dist/{archive_name}.zip')
    
    logging.info(f"Creating distribution archive: {archive_path}")
    try:
        shutil.make_archive(
            f'dist/{archive_name}',
            'zip',
            'dist/DAOC Sprint Manager'
        )
        logging.info(f"Archive created successfully: {archive_path}")
        return archive_path
    except Exception as e:
        logging.error(f"Failed to create archive: {str(e)}")
        return None

def main():
    """Main build process."""
    try:
        # Check prerequisites
        missing_prereqs = check_prerequisites()
        if missing_prereqs:
            for item in missing_prereqs:
                logging.error(f"Missing prerequisite: {item}")
            sys.exit(1)
        
        # Get version
        version = get_version()
        logging.info(f"Building version: {version}")
        
        # Clean build directories
        clean_build_dirs()
        
        # Run PyInstaller
        run_pyinstaller()
        
        # Copy documentation and assets
        copy_documentation()
        copy_assets()
        
        # Create empty models directory
        models_dir = Path('dist/DAOC Sprint Manager/models')
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify build
        if not verify_build():
            logging.error("Build verification failed!")
            sys.exit(1)
        
        # Create distribution archive
        archive_path = create_distribution_archive(version)
        if not archive_path:
            logging.error("Failed to create distribution archive!")
            sys.exit(1)
        
        logging.info("\nBuild completed successfully!")
        logging.info(f"Executable: dist/DAOC Sprint Manager/DAOC Sprint Manager.exe")
        logging.info(f"Distribution archive: {archive_path}")
        
    except Exception as e:
        logging.error(f"Error during build process: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 