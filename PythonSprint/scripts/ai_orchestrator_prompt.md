# AI Orchestrator Prompt: PyDAOC Sprint Manager

## Project Context

The PyDAOC Sprint Manager is a Python-based tool for automating sprint icon detection in Dark Age of Camelot (DAOC). The project is currently in Phase 3, focusing on machine learning implementation and GUI development. Tasks 4.1 (Data Collection Module) and 4.2 (Annotation Tools) have been completed successfully.

## Current Development Status

### Completed Components

1. **Data Collection Module (Task 4.1)**
   - Core logic for capturing and organizing game screenshots
   - Enhanced ROI selection with visual feedback
   - Data validation for captures
   - Session management system

2. **Annotation Tools (Task 4.2)**
   - Comprehensive labeling interface in DataCollectorUI
   - Batch processing for efficient labeling
   - Review and verification tools
   - Progress tracking and manifest generation

### Next Focus: Task 4.3 - Preprocessing Pipeline

The project requires a preprocessing pipeline to prepare labeled data for model training. This involves:
1. Image preprocessing workflow
2. Data augmentation strategies
3. Normalization techniques
4. Dataset preparation for training

## Technical Framework

### Core Components

1. **DataCollector Class** (`training/data_collector.py`)
   - Manages data organization and sessions
   - Handles manifest generation
   - Supports dataset extraction with train/val/test splits

2. **DataCollectorUI Class** (`training/data_collector_ui.py`)
   - Provides annotation interface
   - Manages user interactions
   - Integrates with DataCollector for data management

### Data Organization

- Structured directory hierarchy for labeled data:
  - `unsorted/`: New captures
  - `active/`: Sprint active icons
  - `inactive/`: Sprint inactive icons
  - `other/`: Background/non-sprint images

## Development Guidelines

1. **Code Quality**
   - Maintain modular design
   - Implement comprehensive error handling
   - Follow PEP 8 style guidelines
   - Add detailed docstrings and comments

2. **User Experience**
   - Prioritize efficient workflows
   - Provide clear feedback
   - Implement keyboard shortcuts
   - Display progress indicators

3. **Data Management**
   - Ensure data integrity
   - Implement validation checks
   - Support flexible dataset organization
   - Generate detailed manifests

## Next Steps

1. **Task 4.3: Preprocessing Pipeline**
   - Design preprocessing workflow
   - Implement augmentation strategies
   - Develop normalization techniques
   - Create dataset preparation pipeline

2. **Future Tasks**
   - Task 4.4: Model Architecture Selection & Training
   - Task 4.5: ONNX Model Export

## Key Considerations

1. **Performance**
   - Optimize image processing operations
   - Consider batch processing efficiency
   - Minimize disk I/O operations

2. **Maintainability**
   - Document preprocessing steps
   - Create modular pipeline components
   - Support configuration flexibility

3. **Integration**
   - Ensure compatibility with existing components
   - Prepare data format for model training
   - Support ONNX export requirements

## Success Criteria

1. **Preprocessing Pipeline**
   - Efficient image processing workflow
   - Configurable augmentation options
   - Consistent normalization
   - Clear documentation

2. **Code Quality**
   - Comprehensive test coverage
   - Clear error handling
   - PEP 8 compliance
   - Detailed documentation

3. **User Experience**
   - Intuitive interface
   - Clear progress feedback
   - Efficient workflow
   - Helpful error messages

## Resources

- Project repository structure
- Existing implementation in `training/` directory
- Documentation in `README.md` and related files
- Task tracking in `TASK.md` 