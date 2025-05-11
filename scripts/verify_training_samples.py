"""Verify generated training samples."""

import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

def display_samples(base_dir: Path, num_samples: int = 5):
    """Display samples from both active and inactive classes."""
    active_dir = base_dir / "active"
    inactive_dir = base_dir / "inactive"
    
    # Create figure
    plt.figure(figsize=(15, 5))
    
    # Display original active icon
    plt.subplot(2, num_samples + 1, 1)
    img = cv2.imread(str(active_dir / "sprint_icon_original.png"))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.title("Original Active")
    plt.axis('off')
    
    # Display original inactive icon
    plt.subplot(2, num_samples + 1, num_samples + 2)
    img = cv2.imread(str(inactive_dir / "empty_slot_original.png"))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.title("Original Inactive")
    plt.axis('off')
    
    # Display augmented active samples
    active_samples = list(active_dir.glob("aug_*.png"))[:num_samples]
    for i, sample_path in enumerate(active_samples, 1):
        plt.subplot(2, num_samples + 1, i + 1)
        img = cv2.imread(str(sample_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img)
        plt.title(f"Aug Active {i}")
        plt.axis('off')
    
    # Display augmented inactive samples
    inactive_samples = list(inactive_dir.glob("aug_*.png"))[:num_samples]
    for i, sample_path in enumerate(inactive_samples, 1):
        plt.subplot(2, num_samples + 1, i + num_samples + 3)
        img = cv2.imread(str(sample_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img)
        plt.title(f"Aug Inactive {i}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.savefig("data/training_samples_visualization.png")
    plt.close()

if __name__ == "__main__":
    display_samples(Path("data/training_input")) 