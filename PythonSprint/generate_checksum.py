import hashlib
import os
from pathlib import Path # Import Path

def calculate_sha256(file_path: Path) -> str: # Use Path type hint
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    # This script assumes it is located in the PythonSprint project root directory,
    # or that the Current Working Directory (CWD) is PythonSprint when it's executed.
    
    project_root_when_run = Path.cwd()
    
    print(f"DEBUG: Current working directory for generate_checksum.py: {project_root_when_run}")
    
    file_name = "DAOCSprintManager_v0.3.0.zip"
    # Path for the ZIP file relative to the project root (PythonSprint)
    relative_zip_path = Path("dist") / file_name
    
    # Absolute path to the zip file based on CWD
    zip_file_full_path = project_root_when_run / relative_zip_path
    
    print(f"DEBUG: Attempting to hash file at absolute path: {zip_file_full_path}")

    if zip_file_full_path.exists() and zip_file_full_path.is_file():
        try:
            checksum = calculate_sha256(zip_file_full_path)
            print(f"\nSHA256 Checksum for {file_name}:")
            print(checksum)
        except Exception as e:
            print(f"Error calculating checksum for {zip_file_full_path}: {e}")
    else:
        print(f"Error: File not found or is not a file at the path: {zip_file_full_path}")
        print(f"DEBUG: Project root (CWD) was: {project_root_when_run}")
        print(f"DEBUG: Assumed relative path to ZIP was: {relative_zip_path}")
        
        # Help debug by listing contents of 'dist' directory based on CWD
        dist_dir_path = project_root_when_run / "dist"
        if dist_dir_path.exists() and dist_dir_path.is_dir():
            print(f"DEBUG: Contents of directory '{dist_dir_path}':")
            for item in dist_dir_path.iterdir():
                print(f"  - {item.name}")
        else:
            print(f"DEBUG: Directory '{dist_dir_path}' does not exist or is not a directory.") 