import hashlib
import os

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    file_path = os.path.join("dist", "DAOCSprintManager_v0.3.0.zip")
    if os.path.exists(file_path):
        checksum = calculate_sha256(file_path)
        print(f"\nSHA256 Checksum for {file_path}:")
        print(checksum)
    else:
        print(f"Error: File not found at {file_path}") 