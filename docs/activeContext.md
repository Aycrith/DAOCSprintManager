# Active Context

## Current Focus
Training data generation and preparation for sprint icon detection model.

## Key Considerations
1. Icon Characteristics
   - Size: 24x24 pixels (32x32 with padding)
   - Color: Bright green when active
   - Position: Rightmost in buff bar when active
   - State: Binary (present/absent)

2. Training Data
   - Active class: Sprint icon with augmentations
   - Inactive class: Empty buff bar slot
   - Augmentation parameters optimized for icon preservation
   - Dataset split: 70% train, 15% validation, 15% test

3. Detection Requirements
   - Real-time performance needed
   - Must handle buff bar background variations
   - Should be robust to minor UI scaling changes
   - Need to handle icon blinking behavior

## Technical Decisions
1. Preprocessing
   - 32x32 input size to allow padding
   - Minimal augmentation to preserve icon characteristics
   - Black background for inactive state samples

2. Data Pipeline
   - Separate directories for active/inactive classes
   - Automated extraction from reference images
   - Visualization tools for quality control

3. Model Considerations
   - Binary classification task
   - Need to balance accuracy vs. performance
   - Consider using quantization for runtime efficiency 