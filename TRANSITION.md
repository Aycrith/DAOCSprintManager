# DAOC Sprint Manager - AI Agent Transition Document

## Current Status

The DAOC Sprint Manager project has successfully completed Phase 3, Step 1 implementation: ML-Based Detection (ONNX Integration). The core ML detection functionality has been implemented, alongside the existing template matching capability. The application now includes:

1. ONNX Runtime integration for machine learning-based detection
2. ML settings in the data models and configuration template
3. A robust MLDetector class with preprocessing capabilities
4. Graceful fallback to template matching when ONNX is unavailable

We are now transitioning to Phase 3, Step 2, which focuses on implementing the Configuration GUI. This is the highest priority task according to the project's task prioritization.

## Project Context

The DAOC Sprint Manager is a Python application designed to:
- Detect the sprint icon status in the Dark Age of Camelot game
- Automatically press the sprint key when needed
- Run unobtrusively in the system tray
- Provide user feedback and control options

The application uses computer vision techniques (currently template matching with the new option for ML-based detection) to identify the sprint icon in a specific region of the game window.

## Memory Bank Updates

The following entities have been added to the Memory Bank:
1. MLDetector Class Implementation - Details of the ML detection functionality
2. ML Settings Configuration - Configuration changes for ML support
3. Phase 3 Step 1 Completion - Summary of completed work

## Memory Bank Access

All project details are stored in the Memory Bank files, which should be read at the beginning of your session:

1. `projectbrief.md` - Overall project goals and scope
2. `techContext.md` - Technical stack and architecture
3. `systemPatterns.md` - Design patterns and coding standards
4. `productContext.md` - User perspective and features
5. `progress.md` - Development progress and current status
6. `activeContext.md` - Current focus and immediate next steps

## AI Coding Workflow

The development workflow is documented in:

1. `PLANNING.md` - Project architecture and development plan
2. `TASK.md` - Current tasks and progress tracking
3. `README.md` - User-facing documentation

## Phase 3 Development Focus

### Immediate Next Task: Configuration GUI Implementation

The next priority task is to implement a graphical configuration interface using Tkinter. This will make it easier for users to configure the application without editing JSON files directly.

The configuration GUI should:
1. Allow editing of all settings currently in settings.json, including the new ML settings
2. Provide a visual interface for ROI selection
3. Include validation for input values
4. Connect to the existing ConfigManager for loading/saving settings

Start with `Task 1.1: GUI Framework Setup` from the TASK.md file:
- Create basic tkinter window structure
- Implement tabbed interface layout
- Add OK, Cancel, Apply buttons
- Connect to ConfigManager for loading/saving

### User Task Reminder: ML Model Training

A user task reminder has been documented that explains the process for collecting training data and generating an ML model for the ML-based detection feature. This should be included in user-facing documentation.

### Development Guidelines

1. Follow the design patterns and coding standards in `systemPatterns.md`
2. Maintain backward compatibility with existing configurations
3. Implement comprehensive error handling
4. Keep resource usage minimal
5. Add appropriate logging for troubleshooting
6. Write self-tests for new components
7. Update documentation as you implement features

### Project Architecture Considerations

The existing code follows a modular structure. The new GUI components should be added to the `ui/` directory, following the established patterns:

```
src/daoc_sprint_manager/
├── core/          # Core functionality (window, detection, input, ML)
├── ui/            # User interface components (add GUI here)
├── utils/         # Utility functions and helpers
├── config/        # Configuration files
└── data/          # Template images and resources
```

## Tools and Resources

Review these specific code sections before beginning implementation:

1. `config_manager.py` and `data_models.py` - For understanding the current configuration system
2. `utils/roi_helper.py` - For understanding the current ROI selection approach
3. `ui/tray_app.py` - For integration with the system tray interface

Use the CONTEXT7 tool to search for similar Tkinter-based configuration UI examples when designing the new interface.

## Next Steps After Configuration GUI

After completing the Configuration GUI, the next priorities are:

1. Continue ML-Based Detection with Dataset Collection Utility
2. Profile Management System - For supporting multiple character configurations
3. Quality of Life Improvements - For better user experience

## Handover Notes

1. All core components are functioning correctly through Phase 3, Step 1
2. ML detection is implemented but requires user-provided models
3. Configuration is still JSON-based and needs GUI implementation
4. The system tray application uses threading to separate UI from detection logic
5. Consider thread safety when adding new UI components
6. The ROI helper utility provides a foundation for the visual ROI selection

## Instructions for Next AI Agent

1. Start by reading all Memory Bank files to understand the full context
2. Review the PLANNING.md and TASK.md files for the development roadmap
3. Focus on implementing the Configuration GUI as the first priority
4. When committing code, always ensure it follows the established patterns
5. Update the TASK.md file as tasks are completed
6. Consider using tkinter best practices for a good user experience

## Command for Starting Next AI Agent Session

```
Using our MCP Tools(Memory, CLI, Context7 for code examples, Sequential-Thinking, Git) continue development of the DAOC Sprint Manager. Start by reviewing the Memory Bank and AI Coding Workflow documents to understand the project context. Then focus on implementing the Configuration GUI as detailed in TASK.md. Follow the design patterns in systemPatterns.md and ensure backward compatibility with existing configurations. After each significant development milestone, update the progress tracking in TASK.md. 