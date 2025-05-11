"""
Logging utility module for the DAOC Sprint Manager.

Provides functions for setting up logging with configurable handlers.
"""

import logging
import pathlib
import sys
from typing import Union

def setup_logger(
    name: str,
    log_file: Union[str, pathlib.Path],
    level: int = logging.INFO,
    file_mode: str = 'a',
    console_output: bool = True,
    with_process_id: bool = False
) -> logging.Logger:
    """
    Sets up a logger with file and optional console output.

    Args:
        name: The name of the logger.
        log_file: Path to the log file.
        level: The minimum logging level to record.
        file_mode: The file mode for opening the log file ('a' for append, 'w' for overwrite).
        console_output: Whether to also log to console.
        with_process_id: Whether to include process ID in the log format.

    Returns:
        The configured logger instance.
    """
    # Ensure log_file is a Path object for easier directory creation
    if isinstance(log_file, str):
        log_file = pathlib.Path(log_file)

    # Create log directory if it doesn't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Get or create logger by name (allows reusing existing loggers)
    logger = logging.getLogger(name)
    
    # Only configure if the logger doesn't already have handlers
    # This prevents duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        logger.setLevel(level)
        
        # Format string
        log_format = '%(asctime)s - '
        if with_process_id:
            log_format += '[PID:%(process)d] - '
        log_format += '%(name)s - %(levelname)s - %(message)s'
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # File handler
        try:
            file_handler = logging.FileHandler(log_file, mode=file_mode)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except PermissionError:
            sys.stderr.write(f"WARNING: Permission denied when creating log file: {log_file}\n")
        except (OSError, IOError) as e:
            sys.stderr.write(f"WARNING: Error creating log file {log_file}: {e}\n")
        
        # Console handler (optional)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Prevent propagation to root logger to avoid duplicate logging
        logger.propagate = False
        
        # Log initial message
        logger.debug(f"Logger '{name}' initialized with level={logging.getLevelName(level)}")

    return logger


if __name__ == "__main__":
    """Test the logger setup functionality."""
    import tempfile
    import os
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
        test_log_path = tmp.name
    
    try:
        print(f"Testing logger with file: {test_log_path}")
        
        # Test basic logger setup
        logger1 = setup_logger("test_logger", test_log_path, level=logging.DEBUG)
        logger1.debug("This is a debug message")
        logger1.info("This is an info message")
        logger1.warning("This is a warning message")
        logger1.error("This is an error message")
        logger1.critical("This is a critical message")
        
        # Test reusing the same logger doesn't duplicate handlers
        logger2 = setup_logger("test_logger", test_log_path)
        logger2.info("This message should not create duplicate log entries")
        
        # Test a different logger
        logger3 = setup_logger("another_logger", test_log_path, level=logging.WARNING)
        logger3.debug("This debug message should not appear in the log")
        logger3.warning("This warning message should appear")
        
        # Read the log file and print its contents
        print("\nLog file contents:")
        with open(test_log_path, 'r') as f:
            print(f.read())
            
        print("\nLogger tests completed successfully")
    finally:
        # Clean up the temporary file
        try:
            os.unlink(test_log_path)
            print(f"Cleaned up test log file: {test_log_path}")
        except Exception as e:
            print(f"Failed to clean up log file: {e}") 