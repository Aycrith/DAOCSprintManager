"""
Mock application for performance testing.

This is a simple application that simulates the behavior of the 
real DAOC Sprint Manager but only for testing purposes.
"""

import argparse
import logging
import sys
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockSprintManager:
    """Mock implementation of SprintManager for testing."""
    
    def __init__(self):
        self.is_active = False
        self.stop_event = threading.Event()
        self.logger = logger
        self.logger.info("Mock SprintManager initialized")
        
    def run(self):
        """Run the mock application."""
        self.logger.info("Starting mock application")
        
        # Use up a small amount of CPU and memory to simulate the real application
        counter = 0
        data = []
        
        while not self.stop_event.is_set():
            # Simulate some work
            counter += 1
            if counter % 100 == 0:
                data.append("x" * 1000)  # Add some memory usage
                counter = 0
                
            # Simulate frame processing delay
            time.sleep(0.01)
            
            # Log occasionally
            if counter % 50 == 0:
                self.logger.info(f"Processing frame: {counter}, memory blocks: {len(data)}")
                
    def stop(self):
        """Stop the mock application."""
        self.logger.info("Stopping mock application")
        self.stop_event.set()

def main():
    """Main entry point for the mock application."""
    parser = argparse.ArgumentParser(description="Mock DAOC Sprint Manager for performance testing")
    parser.add_argument("--detection-method", default="template", help="Detection method")
    parser.add_argument("--capture-fps", type=int, default=30, help="Capture FPS")
    parser.add_argument("--window-title", default="MOCK_GAME", help="Game window title")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    logger.info(f"Starting mock application with args: {vars(args)}")
    
    app = MockSprintManager()
    
    # Start the application in a separate thread
    thread = threading.Thread(target=app.run)
    thread.daemon = True
    thread.start()
    
    try:
        # Run until interrupted
        while thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        app.stop()
        logger.info("Mock application stopped")

if __name__ == "__main__":
    main() 