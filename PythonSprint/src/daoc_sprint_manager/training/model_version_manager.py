"""
Model versioning and update management system.

This module provides functionality to manage ONNX model versions,
track metadata, and handle model updates.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import onnx
import onnxruntime as ort
import numpy as np

class ModelVersionManager:
    """
    Manages model versions, metadata, and updates.
    
    This class handles:
    - Model version tracking
    - Metadata storage
    - Update detection
    - Version comparison
    - Storage management
    """
    
    VERSION_FILE = "model_versions.json"
    METADATA_FILE = "model_metadata.json"
    
    def __init__(
        self,
        models_dir: Path,
        max_versions: int = 5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the version manager.
        
        Args:
            models_dir: Directory to store model versions
            max_versions: Maximum number of versions to keep (default: 5)
            logger: Optional logger instance
        """
        self.models_dir = Path(models_dir)
        self.max_versions = max_versions
        self.logger = logger or logging.getLogger(__name__)
        
        # Create models directory if it doesn't exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize version tracking
        self.versions_file = self.models_dir / self.VERSION_FILE
        self.metadata_file = self.models_dir / self.METADATA_FILE
        
        # Load or create version tracking files
        self._init_version_tracking()
    
    def _init_version_tracking(self) -> None:
        """Initialize or load version tracking files."""
        if not self.versions_file.exists():
            self._save_versions({
                "current_version": None,
                "versions": []
            })
        
        if not self.metadata_file.exists():
            self._save_metadata({})
    
    def _save_versions(self, versions_data: Dict[str, Any]) -> None:
        """Save versions data to file."""
        with open(self.versions_file, 'w') as f:
            json.dump(versions_data, f, indent=2)
    
    def _load_versions(self) -> Dict[str, Any]:
        """Load versions data from file."""
        with open(self.versions_file, 'r') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file."""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def add_model_version(
        self,
        model_path: Path,
        version_info: Dict[str, Any],
        make_current: bool = True
    ) -> str:
        """
        Add a new model version.
        
        Args:
            model_path: Path to the ONNX model file
            version_info: Dictionary containing model information:
                - accuracy: Validation accuracy
                - training_date: Training completion date
                - dataset_info: Information about training dataset
                - architecture: Model architecture details
            make_current: Whether to make this the current version
            
        Returns:
            Version ID of the added model
        """
        # Generate version ID based on timestamp
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create version directory
        version_dir = self.models_dir / version_id
        version_dir.mkdir(exist_ok=True)
        
        # Copy model file
        model_filename = model_path.name
        shutil.copy2(model_path, version_dir / model_filename)
        
        # Update version tracking
        versions_data = self._load_versions()
        
        new_version = {
            "id": version_id,
            "model_file": model_filename,
            "added_date": datetime.now().isoformat(),
            **version_info
        }
        
        versions_data["versions"].append(new_version)
        
        # Update current version if requested
        if make_current:
            versions_data["current_version"] = version_id
        
        self._save_versions(versions_data)
        
        # Update metadata
        metadata = self._load_metadata()
        metadata[version_id] = {
            "performance_metrics": version_info.get("accuracy", {}),
            "training_info": {
                "date": version_info.get("training_date"),
                "dataset": version_info.get("dataset_info", {})
            },
            "architecture": version_info.get("architecture", {})
        }
        self._save_metadata(metadata)
        
        # Clean up old versions if needed
        self._cleanup_old_versions()
        
        return version_id
    
    def get_current_version(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current model version.
        
        Returns:
            Dictionary with current version info or None if no version is set
        """
        versions_data = self._load_versions()
        current_id = versions_data.get("current_version")
        
        if not current_id:
            return None
            
        for version in versions_data["versions"]:
            if version["id"] == current_id:
                return version
        
        return None
    
    def get_model_path(self, version_id: Optional[str] = None) -> Path:
        """
        Get the path to a specific model version.
        
        Args:
            version_id: Version ID or None for current version
            
        Returns:
            Path to the model file
            
        Raises:
            ValueError: If version not found
        """
        if version_id is None:
            current = self.get_current_version()
            if not current:
                raise ValueError("No current version set")
            version_id = current["id"]
        
        versions_data = self._load_versions()
        for version in versions_data["versions"]:
            if version["id"] == version_id:
                return self.models_dir / version_id / version["model_file"]
        
        raise ValueError(f"Version {version_id} not found")
    
    def set_current_version(self, version_id: str) -> None:
        """
        Set the current model version.
        
        Args:
            version_id: Version ID to set as current
            
        Raises:
            ValueError: If version not found
        """
        versions_data = self._load_versions()
        
        # Verify version exists
        version_exists = False
        for version in versions_data["versions"]:
            if version["id"] == version_id:
                version_exists = True
                break
        
        if not version_exists:
            raise ValueError(f"Version {version_id} not found")
        
        # Update current version
        versions_data["current_version"] = version_id
        self._save_versions(versions_data)
        
        self.logger.info(f"Current version set to {version_id}")
    
    def compare_versions(
        self,
        version_id1: str,
        version_id2: str
    ) -> Dict[str, Any]:
        """
        Compare two model versions.
        
        Args:
            version_id1: First version ID
            version_id2: Second version ID
            
        Returns:
            Dictionary containing comparison results
        """
        metadata = self._load_metadata()
        
        if version_id1 not in metadata or version_id2 not in metadata:
            raise ValueError("One or both versions not found")
        
        v1_data = metadata[version_id1]
        v2_data = metadata[version_id2]
        
        # Compare metrics
        comparison = {
            "accuracy_diff": (
                v2_data["performance_metrics"].get("accuracy", 0) -
                v1_data["performance_metrics"].get("accuracy", 0)
            ),
            "training_dates": {
                "v1": v1_data["training_info"]["date"],
                "v2": v2_data["training_info"]["date"]
            },
            "dataset_changes": self._compare_datasets(
                v1_data["training_info"]["dataset"],
                v2_data["training_info"]["dataset"]
            ),
            "architecture_changes": self._compare_architectures(
                v1_data["architecture"],
                v2_data["architecture"]
            )
        }
        
        return comparison
    
    def _compare_datasets(
        self,
        dataset1: Dict[str, Any],
        dataset2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare dataset information between versions."""
        return {
            "size_change": dataset2.get("size", 0) - dataset1.get("size", 0),
            "distribution_changes": {
                k: dataset2.get(k, 0) - dataset1.get(k, 0)
                for k in set(dataset1) | set(dataset2)
                if k != "size"
            }
        }
    
    def _compare_architectures(
        self,
        arch1: Dict[str, Any],
        arch2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare model architectures between versions."""
        return {
            "layer_changes": bool(arch1 != arch2),
            "parameter_count_change": arch2.get("params", 0) - arch1.get("params", 0)
        }
    
    def _cleanup_old_versions(self) -> None:
        """Remove old versions if maximum is exceeded."""
        versions_data = self._load_versions()
        versions = versions_data["versions"]
        
        if len(versions) <= self.max_versions:
            return
            
        # Sort versions by date
        versions.sort(key=lambda x: x["added_date"])
        
        # Remove oldest versions
        versions_to_remove = versions[:-self.max_versions]
        
        for version in versions_to_remove:
            version_id = version["id"]
            version_dir = self.models_dir / version_id
            
            # Don't remove if it's the current version
            if version_id == versions_data["current_version"]:
                continue
            
            # Remove version directory and files
            if version_dir.exists():
                shutil.rmtree(version_dir)
            
            # Update tracking files
            metadata = self._load_metadata()
            if version_id in metadata:
                del metadata[version_id]
            self._save_metadata(metadata)
            
            self.logger.info(f"Removed old version: {version_id}")
        
        # Update versions list
        versions_data["versions"] = versions[-self.max_versions:]
        self._save_versions(versions_data)
    
    def create_backup(self, backup_dir: Path) -> Path:
        """
        Create a backup of all model versions and metadata.
        
        Args:
            backup_dir: Directory to store the backup
            
        Returns:
            Path to the created backup directory
        """
        backup_dir = Path(backup_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"model_backup_{timestamp}"
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all version directories
        versions_data = self._load_versions()
        for version in versions_data["versions"]:
            version_dir = self.models_dir / version["id"]
            if version_dir.exists():
                shutil.copytree(
                    version_dir,
                    backup_path / version["id"],
                    dirs_exist_ok=True
                )
        
        # Copy tracking files
        shutil.copy2(self.versions_file, backup_path / self.VERSION_FILE)
        shutil.copy2(self.metadata_file, backup_path / self.METADATA_FILE)
        
        self.logger.info(f"Created backup at {backup_path}")
        return backup_path
    
    def restore_from_backup(self, backup_path: Path) -> None:
        """
        Restore model versions from a backup.
        
        Args:
            backup_path: Path to the backup directory
            
        Raises:
            ValueError: If backup is invalid or incomplete
        """
        backup_path = Path(backup_path)
        
        # Verify backup contains required files
        if not (backup_path / self.VERSION_FILE).exists():
            raise ValueError("Invalid backup: version file missing")
        if not (backup_path / self.METADATA_FILE).exists():
            raise ValueError("Invalid backup: metadata file missing")
        
        # Clear current models directory
        if self.models_dir.exists():
            shutil.rmtree(self.models_dir)
        self.models_dir.mkdir(parents=True)
        
        # Copy version directories
        with open(backup_path / self.VERSION_FILE, 'r') as f:
            versions_data = json.load(f)
            
        for version in versions_data["versions"]:
            version_dir = backup_path / version["id"]
            if version_dir.exists():
                shutil.copytree(
                    version_dir,
                    self.models_dir / version["id"],
                    dirs_exist_ok=True
                )
        
        # Copy tracking files
        shutil.copy2(backup_path / self.VERSION_FILE, self.versions_file)
        shutil.copy2(backup_path / self.METADATA_FILE, self.metadata_file)
        
        self.logger.info(f"Restored from backup at {backup_path}") 