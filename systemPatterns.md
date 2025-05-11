# DAOC Sprint Manager - System Patterns & Coding Standards

## Design Patterns

### Module Pattern

The application follows a modular design with clear boundaries between components. Each module is responsible for a specific aspect of functionality:

- **Core Modules**: Focused on fundamental operations (window capture, detection, input)
- **Application Modules**: Orchestrate the components and handle lifecycle
- **Utility Modules**: Provide cross-cutting support functionality

### Observer Pattern

The tray application uses an observer-like pattern where:
- The detection thread updates shared state variables
- The UI observes and displays these updates
- Status changes trigger UI updates through thread-safe mechanisms

### Factory Pattern

The configuration manager acts as a factory for settings, creating and validating AppSettings objects from JSON data.

### Strategy Pattern

The detection system is designed to support multiple strategies:
- Template matching is the current primary strategy
- ML-based detection will be added as an alternative strategy in Phase 3
- Strategies can be switched at runtime based on configuration

### Singleton Pattern (Limited Use)

Some components are effectively singletons within the application scope:
- Main logger instance
- Configuration manager
- Performance monitor

## Coding Standards

### General Guidelines

1. **PEP 8 Compliance**: Follow Python style guide for naming and formatting
2. **Type Hinting**: Use Python 3.8+ type hints for all functions and methods
3. **Docstrings**: Google-style docstrings for all modules, classes, methods
4. **Error Handling**: Explicit error handling with specific exception types
5. **Logging**: Consistent logging at appropriate levels
6. **Comments**: Use comments for complex logic or non-obvious implementations

### Naming Conventions

- **CamelCase** for class names: `WindowManager`, `IconDetector`
- **snake_case** for functions, methods, variables: `find_window()`, `update_status()`
- **UPPER_CASE** for constants: `DEFAULT_THRESHOLD`, `VALID_KEYS`
- **_leading_underscore** for private/internal methods: `_load_config()`

### File Structure

Each Python module follows a standard structure:
```python
"""
Module docstring explaining purpose and usage.
"""

# Standard library imports
import logging
import pathlib

# Third-party imports
import cv2
import numpy as np

# Local imports
from .utils import logger

# Constants
DEFAULT_TIMEOUT = 10.0

# Classes and functions
class SomeClass:
    """Class docstring."""
    
    def __init__(self, param: str):
        """Constructor docstring."""
        self.param = param
        
    def some_method(self) -> bool:
        """Method docstring."""
        return True

# Main execution block (if applicable)
if __name__ == "__main__":
    # Self-test or example usage
    pass
```

### Error Handling Patterns

1. **Specific Exceptions**: Catch specific exceptions rather than general `Exception`
2. **Graceful Degradation**: Return sensible defaults on failure
3. **Logging with Context**: Include context in error logs
4. **Operation Continuation**: When possible, continue operation despite errors
5. **User Feedback**: Provide meaningful error messages for user-facing issues

### Code Organization

1. **Class Responsibility**: Each class has a single responsibility
2. **Method Size**: Methods should be short and focused on a single task
3. **Dependency Injection**: Dependencies passed as constructor parameters
4. **Avoid Global State**: Use proper passing of dependencies
5. **Lazy Initialization**: Initialize resources when needed

## Testing Patterns

1. **Self-Testing Modules**: `if __name__ == "__main__"` blocks contain self-tests
2. **Assertion Patterns**: Pre-condition and post-condition assertions
3. **Isolated Component Testing**: Components can be tested independently
4. **Known State Setup**: Tests start from a known state

## Threading Patterns

1. **UI/Background Separation**: UI runs in main thread, detection in background
2. **Thread Safety**: Use thread-safe mechanisms for shared state
3. **Clean Shutdown**: Proper signal handling and thread joining
4. **Status Updates**: Thread-safe status propagation to UI

## Extension Patterns (Phase 3)

1. **Plugin Loading**: Dynamic loading of detection plugins
2. **Configuration Extensions**: Extensible configuration system
3. **Profile Management**: Serialization/deserialization of profiles
4. **UI Composition**: Modular UI components 

## Testing and Error Handling Patterns (2024-06)
- Test suite uses Python's unittest, pytest, and coverage for robust, automated testing.
- Tests are organized by feature: installation, configuration, templates, executables, resources, profiles, settings, and performance monitoring.
- Error handling patterns:
  - Process monitoring: Handles non-existent processes, access denied, and keyboard interrupts gracefully.
  - File operations: Handles invalid directories and file access errors without crashing.
- Main function and CLI argument parsing are covered by tests, ensuring end-to-end reliability. 