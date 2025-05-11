"""
Data Collection Module for capturing training data.

This module provides tools to capture, process, and organize game screenshots
for training machine learning models to detect sprint states.
"""

import os
import sys
import time
import uuid
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Add parent directory to path to find other modules
parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from daoc_sprint_manager.core.window_manager import WindowManager

class DataCollectionSession:
    """
    Manages a data collection session for capturing game screenshots.
    
    A session contains metadata about the capture environment and organizes
    screenshots into a structured directory.
    """
    
    def __init__(
        self,
        base_dir: Union[str, Path],
        session_name: Optional[str] = None,
        game_window_title: Optional[str] = None,
        roi: Optional[Tuple[int, int, int, int]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize a new data collection session.
        
        Args:
            base_dir: Base directory for storing all data collection sessions
            session_name: Optional name for this session (default: timestamp)
            game_window_title: Title substring to identify the game window
            roi: Region of interest coordinates as (x, y, width, height)
            logger: Optional logger instance
        """
        self.base_dir = Path(base_dir)
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_id = str(uuid.uuid4())
        self.game_window_title = game_window_title
        self.roi = roi
        self.logger = logger or logging.getLogger("DataCollector")
        
        # Set up session directory structure
        self.session_dir = self.base_dir / "sessions" / self.session_name
        self.raw_dir = self.session_dir / "raw"
        self.roi_dir = self.session_dir / "roi"
        self.metadata_file = self.session_dir / "metadata.json"
        
        # Initialize WindowManager for capturing
        self.window_manager = WindowManager(self.logger)
        self.game_window = None
        
        # Screenshot counter
        self.screenshot_count = 0
        
        # Capture state
        self.is_running = False
        self.capture_start_time = None
        
        # Set up directories
        self._setup_directories()
        self._save_metadata()
        
    def _setup_directories(self):
        """Create necessary directories for the session."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.roi_dir.mkdir(exist_ok=True)
        
    def _save_metadata(self):
        """Save session metadata to a JSON file."""
        metadata = {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "created_at": datetime.now().isoformat(),
            "game_window_title": self.game_window_title,
            "roi": self.roi,
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.debug(f"Saved session metadata to {self.metadata_file}")
        
    def start(self):
        """
        Start the data collection session.
        
        This initializes the session and finds the game window.
        """
        self.logger.info(f"Starting data collection session: {self.session_name}")
        
        if self.game_window_title:
            self.game_window = self.window_manager.find_window(self.game_window_title)
            if self.game_window:
                self.logger.info(f"Found game window with title containing '{self.game_window_title}'")
            else:
                self.logger.warning(f"Game window with title containing '{self.game_window_title}' not found")
        
        self.is_running = True
        self.capture_start_time = datetime.now()
        
        return self.is_running
    
    def stop(self):
        """Stop the data collection session."""
        self.is_running = False
        end_time = datetime.now()
        duration = (end_time - self.capture_start_time).total_seconds() if self.capture_start_time else 0
        
        # Update metadata with session stats
        metadata = {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "created_at": self.capture_start_time.isoformat() if self.capture_start_time else None,
            "ended_at": end_time.isoformat(),
            "duration_seconds": duration,
            "screenshot_count": self.screenshot_count,
            "game_window_title": self.game_window_title,
            "roi": self.roi,
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Stopped data collection session: {self.session_name}")
        self.logger.info(f"Captured {self.screenshot_count} screenshots in {duration:.1f} seconds")
        
    def capture_screenshot(self, label: Optional[str] = None) -> bool:
        """
        Capture a screenshot from the game window.
        
        Args:
            label: Optional label for the screenshot (e.g., 'sprint_active', 'sprint_inactive')
            
        Returns:
            bool: True if capture was successful, False otherwise
        """
        if not self.is_running:
            self.logger.warning("Cannot capture: session not started")
            return False
            
        if not self.game_window:
            self.logger.warning("Cannot capture: game window not found")
            return False
            
        try:
            # Capture full window
            full_img = self.window_manager.capture_window(self.game_window)
            if full_img is None:
                self.logger.error("Failed to capture window")
                return False
                
            # Generate screenshot ID and timestamp
            timestamp = datetime.now()
            screenshot_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{self.screenshot_count:04d}"
            
            # Save full screenshot
            full_path = self.raw_dir / f"{screenshot_id}.png"
            cv2.imwrite(str(full_path), full_img)
            
            # Extract and save ROI if specified
            roi_img = None
            if self.roi:
                x, y, w, h = self.roi
                if 0 <= x < full_img.shape[1] and 0 <= y < full_img.shape[0] and w > 0 and h > 0:
                    # Ensure ROI is within image bounds
                    x_end = min(x + w, full_img.shape[1])
                    y_end = min(y + h, full_img.shape[0])
                    roi_img = full_img[y:y_end, x:x_end].copy()
                    
                    # Save ROI
                    roi_path = self.roi_dir / f"{screenshot_id}.png"
                    cv2.imwrite(str(roi_path), roi_img)
                else:
                    self.logger.warning(f"ROI {self.roi} is outside image bounds {full_img.shape[1]}x{full_img.shape[0]}")
            
            # Save metadata for this screenshot
            meta = {
                "id": screenshot_id,
                "timestamp": timestamp.isoformat(),
                "session_id": self.session_id,
                "label": label,
                "roi": self.roi,
                "full_path": str(full_path),
                "roi_path": str(roi_path) if roi_img is not None else None,
            }
            
            # Save screenshot metadata
            meta_path = self.session_dir / "screenshots.jsonl"
            with open(meta_path, 'a') as f:
                f.write(json.dumps(meta) + '\n')
            
            self.screenshot_count += 1
            self.logger.debug(f"Captured screenshot {screenshot_id}{' with label ' + label if label else ''}")
            
            return True
            
        except Exception as e:
            self.logger.exception(f"Error capturing screenshot: {e}")
            return False
            
    def capture_sequence(self, count: int, interval_seconds: float = 1.0, label: Optional[str] = None) -> int:
        """
        Capture a sequence of screenshots at a specified interval.
        
        Args:
            count: Number of screenshots to capture
            interval_seconds: Time between screenshots in seconds
            label: Optional label for all screenshots in this sequence
            
        Returns:
            int: Number of successfully captured screenshots
        """
        self.logger.info(f"Starting capture sequence: {count} screenshots at {interval_seconds}s intervals")
        
        success_count = 0
        for i in range(count):
            if not self.is_running:
                self.logger.warning("Capture sequence stopped: session not running")
                break
                
            if self.capture_screenshot(label):
                success_count += 1
                
            # Sleep for the interval unless it's the last screenshot
            if i < count - 1:
                time.sleep(interval_seconds)
                
        self.logger.info(f"Completed capture sequence: {success_count}/{count} successful")
        return success_count
        
    @classmethod
    def load_session(cls, session_dir: Union[str, Path], logger: Optional[logging.Logger] = None):
        """
        Load an existing data collection session from its directory.
        
        Args:
            session_dir: Path to the session directory
            logger: Optional logger instance
            
        Returns:
            DataCollectionSession: The loaded session
        """
        session_dir = Path(session_dir)
        metadata_file = session_dir / "metadata.json"
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found in {session_dir}")
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            
        # Determine base directory (parent of the "sessions" directory)
        base_dir = session_dir.parent.parent
        
        # Create a new session instance with loaded metadata
        session = cls(
            base_dir=base_dir,
            session_name=metadata.get("session_name"),
            game_window_title=metadata.get("game_window_title"),
            roi=metadata.get("roi"),
            logger=logger
        )
        
        # Set the session ID from the loaded metadata
        session.session_id = metadata.get("session_id")
        
        # Count existing screenshots
        screenshot_meta_path = session_dir / "screenshots.jsonl"
        if screenshot_meta_path.exists():
            with open(screenshot_meta_path, 'r') as f:
                session.screenshot_count = sum(1 for _ in f)
                
        return session


class DataCollector:
    """Manages data collection sessions and dataset organization."""
    
    def __init__(
        self,
        data_dir: Union[str, Path] = "training_data",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the data collector.
        
        Args:
            data_dir: Base directory for storing all training data
            logger: Optional logger instance
        """
        self.data_dir = Path(data_dir)
        self.logger = logger or logging.getLogger("DataCollector")
        
        # Directory structure for labeled data
        self.sessions_dir = self.data_dir / "sessions"
        self.unsorted_dir = self.data_dir / "unsorted"
        self.active_dir = self.data_dir / "active"
        self.inactive_dir = self.data_dir / "inactive"
        self.other_dir = self.data_dir / "other"
        
        # Create all necessary directories
        for dir_path in [
            self.sessions_dir,
            self.unsorted_dir,
            self.active_dir,
            self.inactive_dir,
            self.other_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing sessions
        self.sessions: Dict[str, Dict] = {}
        self._scan_existing_sessions()
        
    def _scan_existing_sessions(self):
        """Scan for and load metadata of existing data collection sessions."""
        sessions_dir = self.data_dir / "sessions"
        if not sessions_dir.exists():
            return
            
        for session_dir in sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue
                
            metadata_file = session_dir / "metadata.json"
            if not metadata_file.exists():
                continue
                
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                session_id = metadata.get("session_id")
                if session_id:
                    self.sessions[session_id] = {
                        "name": metadata.get("session_name"),
                        "created_at": metadata.get("created_at"),
                        "screenshot_count": metadata.get("screenshot_count", 0),
                        "path": session_dir
                    }
                    
            except Exception as e:
                self.logger.warning(f"Error loading session metadata from {metadata_file}: {e}")
                
        self.logger.info(f"Found {len(self.sessions)} existing data collection sessions")
        
    def create_session(
        self,
        session_name: Optional[str] = None,
        game_window_title: Optional[str] = None,
        roi: Optional[Tuple[int, int, int, int]] = None
    ) -> DataCollectionSession:
        """
        Create a new data collection session.
        
        Args:
            session_name: Optional name for the session
            game_window_title: Title substring to identify the game window
            roi: Region of interest coordinates as (x, y, width, height)
            
        Returns:
            DataCollectionSession: The newly created session
        """
        session = DataCollectionSession(
            base_dir=self.data_dir,
            session_name=session_name,
            game_window_title=game_window_title,
            roi=roi,
            logger=self.logger
        )
        
        self.sessions[session.session_id] = {
            "name": session.session_name,
            "created_at": datetime.now().isoformat(),
            "screenshot_count": 0,
            "path": session.session_dir
        }
        
        return session
        
    def load_session(self, session_id: str) -> Optional[DataCollectionSession]:
        """
        Load an existing session by ID.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            DataCollectionSession or None: The loaded session, or None if not found
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session ID {session_id} not found")
            return None
            
        session_info = self.sessions[session_id]
        try:
            session = DataCollectionSession.load_session(
                session_dir=session_info["path"],
                logger=self.logger
            )
            return session
            
        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {e}")
            return None
            
    def get_session_list(self) -> List[Dict]:
        """
        Get a list of all available sessions.
        
        Returns:
            List of session info dictionaries
        """
        return [
            {
                "id": session_id,
                **session_info
            }
            for session_id, session_info in self.sessions.items()
        ]
        
    def extract_dataset(
        self,
        output_dir: Union[str, Path],
        split_ratio: Tuple[float, float, float] = (0.7, 0.15, 0.15),
        include_unlabeled: bool = False
    ) -> Dict[str, int]:
        """
        Extract labeled images into a structured dataset and create a manifest.
        
        Args:
            output_dir: Directory to store the extracted dataset
            split_ratio: Train/val/test split ratio as (train, val, test)
            include_unlabeled: Whether to include unlabeled images
            
        Returns:
            Dict containing counts of images per category
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize counters
        counts = {
            "sprint_active": 0,
            "sprint_inactive": 0,
            "other": 0,
            "unlabeled": 0
        }
        
        # Prepare manifest data
        manifest_data = []
        
        # Process labeled directories
        label_dirs = {
            "sprint_active": self.active_dir,
            "sprint_inactive": self.inactive_dir,
            "other": self.other_dir
        }
        
        for label, src_dir in label_dirs.items():
            if not src_dir.exists():
                self.logger.warning(f"Label directory not found: {src_dir}")
                continue
                
            # Get all PNG files in this label directory
            image_files = list(src_dir.glob("*.png"))
            counts[label] = len(image_files)
            
            # Add to manifest
            for img_path in image_files:
                manifest_data.append({
                    "filepath": str(img_path.relative_to(output_dir)),
                    "label": label
                })
                
        # Process unlabeled images if requested
        if include_unlabeled and self.unsorted_dir.exists():
            unlabeled_files = list(self.unsorted_dir.glob("*.png"))
            counts["unlabeled"] = len(unlabeled_files)
            
            if unlabeled_files:
                # Add to manifest with None label
                for img_path in unlabeled_files:
                    manifest_data.append({
                        "filepath": str(img_path.relative_to(output_dir)),
                        "label": None
                    })
                    
        # Write manifest
        manifest_path = output_dir / "dataset_manifest.csv"
        with open(manifest_path, 'w', newline='') as f:
            import csv
            writer = csv.DictWriter(f, fieldnames=["filepath", "label"])
            writer.writeheader()
            writer.writerows(manifest_data)
            
        # Log summary
        self.logger.info("Dataset extraction complete:")
        for label, count in counts.items():
            if count > 0:
                self.logger.info(f"  {label}: {count} images")
                
        self.logger.info(f"Manifest written to: {manifest_path}")
        
        return counts

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("DataCollectorTest")
    
    # Test the data collector
    collector = DataCollector(logger=logger)
    
    # Create a test session
    session = collector.create_session(
        session_name="test_session",
        game_window_title="PowerShell",  # Captures any visible PowerShell window
        roi=(0, 0, 100, 100)  # Example ROI
    )
    
    if session.start():
        # Capture a single screenshot
        session.capture_screenshot(label="test")
        
        # Capture a sequence
        session.capture_sequence(count=3, interval_seconds=1.0, label="sequence")
        
        # Stop the session
        session.stop()
        
        # List sessions
        for session_info in collector.get_session_list():
            print(f"Session: {session_info['name']} ({session_info['id']})")
            print(f"  Created: {session_info['created_at']}")
            print(f"  Screenshots: {session_info['screenshot_count']}")
            print(f"  Path: {session_info['path']}")
            
    else:
        logger.error("Failed to start session") 