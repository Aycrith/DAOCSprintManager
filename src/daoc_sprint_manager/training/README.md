# Training Data Collection and Management

This module provides tools for collecting, labeling, and managing training data for the sprint detection model.

## Directory Structure

```
data/ml_training_data/
├── unsorted/        # Raw captured images awaiting labeling
├── active/         # Images labeled as "sprint active"
├── inactive/       # Images labeled as "sprint inactive"
└── other/          # Background/other images
```

## Data Collection Tool

The Data Collection Tool (`DataCollectorTool`) provides a graphical interface for:

1. Capturing game screenshots
2. Selecting regions of interest (ROI)
3. Labeling captured images
4. Managing the dataset

### Capturing Images

- Use "Select ROI" to define the capture region
- "Capture Single" for individual screenshots
- "Start Sequence" for continuous capture at specified intervals
- Images are initially saved to the `unsorted` directory

### Image Labeling

1. Navigate through unsorted images using:
   - "Previous" button or Left Arrow (←)
   - "Next" button or Right Arrow (→)
   - Counter shows current position in unsorted images

2. Label images using:
   - Select category: "Sprint Active", "Sprint Inactive", or "Other/Background"
   - Click "Save Label" or press Space to move image to appropriate directory
   - Images are automatically moved from `unsorted` to their labeled directories

3. Batch Processing:
   - Set batch size and select category
   - Process multiple images quickly with the same label
   - Use keyboard shortcuts:
     - Ctrl+1: Start Active batch
     - Ctrl+2: Start Inactive batch
     - Ctrl+3: Start Other batch
     - Esc: Cancel batch

### Dataset Management

The tool maintains a structured dataset organization:
- Newly captured images go to `unsorted/`
- Labeled images are moved to their respective directories
- Use "Extract Dataset" to generate a manifest file (`dataset_manifest.csv`)

The manifest file contains:
- `filepath`: Relative path to the image
- `label`: Category ("sprint_active", "sprint_inactive", "other")

## Usage Example

1. Start a new session:
   ```bash
   python -m daoc_sprint_manager.training.data_collector_ui
   ```

2. Configure capture:
   - Enter session name
   - Click "Select ROI" to define capture region
   - Set capture interval if using sequence mode

3. Capture images:
   - Use "Capture Single" or "Start Sequence"
   - Images appear in the `unsorted` directory

4. Label images:
   - Navigate through unsorted images
   - Select appropriate label
   - Click "Save Label" or use Space key
   - Images move to labeled directories

5. Generate dataset:
   - Click "Extract Dataset"
   - Review manifest file for data distribution

## API Reference

### DataCollector

Main class for managing data collection sessions and dataset organization.

```python
from daoc_sprint_manager.training.data_collector import DataCollector

collector = DataCollector()
collector.create_session("my_session")
collector.extract_dataset("output_dir")
```

### DataCollectorTool

GUI interface for data collection and labeling.

```python
from daoc_sprint_manager.training.data_collector_ui import DataCollectorTool
import tkinter as tk

root = tk.Tk()
tool = DataCollectorTool(root)
root.mainloop()
```

## Notes

- Images are stored as PNG files
- ROI selection is preserved across captures in a session
- Use keyboard shortcuts for faster labeling
- Regular backups of the dataset are recommended

## Data Collection Tool

### Getting Started

1. Launch the Data Collection Tool:
   ```bash
   python -m daoc_sprint_manager.training.data_collector_ui
   ```

2. The tool will open with two main panels:
   - Left panel: Session management
   - Right panel: Capture settings and controls

### Creating a New Session

1. Click "New Session" in the left panel
2. Enter a session name (optional, defaults to timestamp)
3. The session will be created with its own directory for organizing captured images

### Setting Up ROI (Region of Interest)

The ROI defines the area of the game window where the sprint indicator appears. You can set it in two ways:

#### Visual Selection (Recommended)
1. Click "Select ROI" button
2. A fullscreen window will appear showing your screen
3. Click and drag to select the sprint icon
4. A preview window will show your selection in real-time
5. Press Enter to confirm or Escape to cancel
6. The tool will validate your selection and warn if it's too small

#### Manual Entry
1. Enter coordinates (X, Y) and dimensions (Width, Height) in the spinboxes
2. The tool will validate your input and show warnings if:
   - Dimensions are too small (< 10x10 pixels)
   - Dimensions are too large (> 500x500 pixels)
   - Position is outside the game window
   - ROI extends beyond window bounds

### Capturing Training Data

#### Single Captures
1. Set the label (e.g., "sprint_active" or "sprint_inactive")
2. Click "Capture Single" to take one screenshot
3. The image will be saved in both full and ROI-cropped versions

#### Sequence Captures
1. Set the number of screenshots to capture
2. Set the interval between captures (in seconds)
3. Click "Start Sequence" to begin
4. The tool will capture the specified number of screenshots
5. Click "Stop Sequence" to end early if needed

### Best Practices for Data Collection

#### ROI Selection
- Select an area that tightly bounds the sprint icon
- Include a small margin around the icon (1-2 pixels)
- Ensure the selection is at least 10x10 pixels
- Keep the selection consistent across sessions

#### Capturing Diverse Data
1. Capture in different in-game conditions:
   - Different times of day
   - Various weather conditions
   - Different character locations
   - Different UI scales if applicable

2. Include edge cases:
   - Sprint icon partially obscured
   - UI overlapping the icon
   - Different game window sizes
   - Both windowed and fullscreen modes

3. Balance your dataset:
   - Capture roughly equal numbers of "active" and "inactive" states
   - Include transitions between states
   - Capture during actual gameplay for realistic conditions

### Data Organization

The tool organizes data in the following structure:
```
training_data/
├── sessions/
│   ├── session_20240320_123456/
│   │   ├── raw/         # Full screenshots
│   │   ├── roi/         # Cropped ROI images
│   │   └── metadata.json
│   └── ...
└── datasets/            # Processed datasets for training
    ├── train/
    ├── validation/
    └── test/
```

### Exporting Datasets

1. Click "Extract Dataset" to prepare data for training
2. Choose an output directory
3. Set split ratios (default: 70% train, 15% validation, 15% test)
4. The tool will:
   - Copy and organize images
   - Generate a manifest file with labels
   - Create train/validation/test splits

## Troubleshooting

### Common Issues

1. **Game Window Not Found**
   - Check the window title in the settings
   - Ensure the game is running and visible
   - Try with both the full window title and partial matches

2. **ROI Selection Issues**
   - If visual selection fails, try manual entry
   - Ensure the game window hasn't moved since ROI selection
   - Check that the ROI is within window bounds

3. **Capture Failures**
   - Verify the game window is not minimized
   - Check if the window is partially off-screen
   - Ensure sufficient disk space for captures

### Data Quality Checks

The tool performs several validations:
- ROI dimensions and position
- Image capture success
- File saving operations
- Dataset organization

Error messages and warnings will guide you through fixing issues.

## Advanced Features

### Data Augmentation

The tool supports basic augmentations:
- Brightness/contrast adjustment
- Slight rotations
- Noise addition
- Color variations

Use these to increase dataset diversity and model robustness.

### Session Management

- Sessions can be loaded and continued later
- Metadata is preserved between sessions
- Multiple sessions can use different ROIs
- Export functionality combines multiple sessions

## Contributing

When adding features or fixing bugs:
1. Follow the existing code structure
2. Add appropriate validation
3. Update this documentation
4. Add tests for new functionality

## License

This module is part of the DAOC Sprint Manager project.
See the main project LICENSE file for terms. 