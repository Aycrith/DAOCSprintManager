"""Performance test runner for DAOC Sprint Manager.

This script provides functionality to run various performance tests
as defined in performance_test_plan.md. It uses the PerformanceMonitor
to collect metrics and generates reports for analysis.
"""

import argparse
import csv
import json
import logging
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the project root to the Python path
project_root = pathlib.Path(__file__).parent.parent
sys.path.append(str(project_root))

from testing.performance_monitor import PerformanceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceTestRunner:
    """Manages and executes performance tests for the DAOC Sprint Manager."""
    
    def __init__(self, output_dir: str = "test_results"):
        """Initialize the test runner.
        
        Args:
            output_dir: Directory to store test results and reports
        """
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.app_process: Optional[subprocess.Popen] = None
        self.monitor: Optional[PerformanceMonitor] = None
        
    def _generate_test_id(self) -> str:
        """Generate a unique test ID based on timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _prepare_test_directory(self, test_name: str) -> pathlib.Path:
        """Create and return a directory for test results.
        
        Args:
            test_name: Name of the test being run
            
        Returns:
            Path to the test results directory
        """
        test_id = self._generate_test_id()
        test_dir = self.output_dir / f"{test_name}_{test_id}"
        test_dir.mkdir(parents=True, exist_ok=True)
        return test_dir
    
    def launch_app(self, config: Dict) -> subprocess.Popen:
        """Launch the mock application for performance testing.
        
        Args:
            config: Dictionary containing application configuration
            
        Returns:
            Process object for the launched application
            
        Raises:
            RuntimeError: If application fails to start
        """
        try:
            # Use the mock application script instead of the real one
            mock_script = project_root / "testing" / "mock_application.py"
            print(f"Using mock application script: {mock_script}")
            
            cmd = [sys.executable, str(mock_script)]
            for key, value in config.items():
                # Handle boolean flags properly
                if key == "test_mode" and value is True:
                    cmd.append(f"--{key.replace('_', '-')}")
                else:
                    cmd.extend([f"--{key.replace('_', '-')}", str(value)])
            
            print(f"Launching mock application with command: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait briefly to ensure process starts
            print("Waiting for process to start...")
            time.sleep(2)
            
            if process.poll() is not None:
                return_code = process.poll()
                stdout, stderr = process.communicate()
                print(f"Process failed to start. Return code: {return_code}")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                raise RuntimeError(f"Application failed to start. Return code: {return_code}, STDERR: {stderr}")
                
            print(f"Process started with PID: {process.pid}")
            self.app_process = process
            return process
            
        except Exception as e:
            print(f"ERROR: Failed to launch application: {e}")
            logger.error(f"Failed to launch application: {e}")
            raise
    
    def start_monitoring(self, process: subprocess.Popen) -> None:
        """Start performance monitoring for the given process.
        
        Args:
            process: Process to monitor
        """
        try:
            self.monitor = PerformanceMonitor(process.pid)
            self.monitor.start()
            logger.info(f"Started monitoring process {process.pid}")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            raise
    
    def stop_monitoring(self) -> Dict:
        """Stop monitoring and return collected metrics.
        
        Returns:
            Dictionary containing collected metrics
        """
        if self.monitor:
            results = self.monitor.get_results()
            self.monitor.stop()
            logger.info("Monitoring stopped")
            return results
        return {}
    
    def cleanup(self) -> None:
        """Clean up resources and processes."""
        if self.monitor:
            self.monitor.stop()
            
        if self.app_process:
            logger.info("Terminating application process")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
    
    def save_results(self, results: Dict, test_dir: pathlib.Path) -> None:
        """Save test results to files.
        
        Args:
            results: Dictionary containing test results
            test_dir: Directory to save results in
        """
        # Save raw JSON data
        with open(test_dir / "raw_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        # Save CSV for time series data
        if "time_series" in results:
            with open(test_dir / "metrics.csv", "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=results["time_series"][0].keys())
                writer.writeheader()
                writer.writerows(results["time_series"])
    
    def run_baseline_test(self, duration: int = 1800) -> Dict:
        """Run baseline performance test.
        
        Args:
            duration: Test duration in seconds (default: 30 minutes)
            
        Returns:
            Dictionary containing test results
        """
        print(f"Starting baseline_test with duration={duration}s")
        test_name = "baseline_test"
        test_dir = self._prepare_test_directory(test_name)
        print(f"Test directory created: {test_dir}")
        
        try:
            # Configure application
            config = {
                "detection_method": "template",
                "capture_fps": 30,
                "window_title": "MOCK_GAME_BASELINE",
                "test_mode": True  # Important: This needs to be explicitly set to True
            }
            print(f"Application config: {config}")
            
            # Launch and monitor
            print("Launching application...")
            process = self.launch_app(config)
            print(f"Application launched with PID: {process.pid}")
            
            print("Starting performance monitoring...")
            self.start_monitoring(process)
            print("Monitoring started")
            
            # Run test
            print(f"Running baseline test for {duration} seconds")
            time.sleep(duration)
            print("Test duration completed")
            
            # Collect results
            print("Collecting monitoring results...")
            results = self.stop_monitoring()
            print(f"Results collected: {len(results.get('time_series', []))} data points")
            
            print(f"Saving results to {test_dir}")
            self.save_results(results, test_dir)
            print("Results saved")
            
            return results
            
        except Exception as e:
            print(f"ERROR: Baseline test failed: {e}")
            logger.error(f"Baseline test failed: {e}", exc_info=True)
            raise
        finally:
            print("Cleaning up resources...")
            self.cleanup()
            print("Cleanup complete")
    
    def run_long_duration_test(self, duration: int = 14400) -> Dict:
        """Run long duration stability test.
        
        Args:
            duration: Test duration in seconds (default: 4 hours)
            
        Returns:
            Dictionary containing test results
        """
        print(f"Starting long_duration_test with duration={duration}s")
        test_name = "long_duration_test"
        test_dir = self._prepare_test_directory(test_name)
        print(f"Test directory created: {test_dir}")
        
        try:
            # Configure application
            config = {
                "detection_method": "template",
                "capture_fps": 30,
                "window_title": "MOCK_GAME",
                "test_mode": True
            }
            print(f"Application config: {config}")
            
            # Launch and monitor
            print("Launching application...")
            process = self.launch_app(config)
            print(f"Application launched with PID: {process.pid}")
            
            print("Starting performance monitoring...")
            self.start_monitoring(process)
            print("Monitoring started")
            
            # Run test with periodic checks
            print(f"Running long duration test for {duration} seconds")
            check_interval = 300  # Check every 5 minutes
            elapsed = 0
            
            while elapsed < duration:
                time.sleep(min(check_interval, duration - elapsed))
                elapsed += min(check_interval, duration - elapsed)
                print(f"Test in progress: {elapsed}/{duration} seconds elapsed")
                
                # Get intermediate results for monitoring
                if self.monitor:
                    summary = self.monitor.generate_summary()
                    print(f"Current metrics - CPU avg: {summary.get('cpu_avg', 0):.2f}%, Memory: {summary.get('memory_avg_mb', 0):.2f} MB")
            
            # Collect final results
            print("Collecting monitoring results...")
            results = self.stop_monitoring()
            print(f"Results collected: {len(results.get('time_series', []))} data points")
            
            print(f"Saving results to {test_dir}")
            self.save_results(results, test_dir)
            print("Results saved")
            
            return results
            
        except Exception as e:
            print(f"ERROR: Long duration test failed: {e}")
            logger.error(f"Long duration test failed: {e}", exc_info=True)
            raise
        finally:
            print("Cleaning up resources...")
            self.cleanup()
            print("Cleanup complete")
    
    def run_high_fps_test(self, duration: int = 3600, fps: int = 60) -> Dict:
        """Run high FPS stress test.
        
        Args:
            duration: Test duration in seconds (default: 1 hour)
            fps: Target FPS (default: 60)
            
        Returns:
            Dictionary containing test results
        """
        print(f"Starting high_fps_test with duration={duration}s, fps={fps}")
        test_name = "high_fps_test"
        test_dir = self._prepare_test_directory(test_name)
        print(f"Test directory created: {test_dir}")
        
        try:
            # Configure application
            config = {
                "detection_method": "template",
                "capture_fps": fps,
                "window_title": "MOCK_GAME",
                "test_mode": True
            }
            print(f"Application config: {config}")
            
            # Launch and monitor
            print("Launching application...")
            process = self.launch_app(config)
            print(f"Application launched with PID: {process.pid}")
            
            print("Starting performance monitoring...")
            self.start_monitoring(process)
            print("Monitoring started")
            
            # Run test
            print(f"Running high FPS test at {fps} FPS for {duration} seconds")
            
            # Run test with updates every minute
            check_interval = 60  # Check every minute
            elapsed = 0
            
            while elapsed < duration:
                time.sleep(min(check_interval, duration - elapsed))
                elapsed += min(check_interval, duration - elapsed)
                print(f"Test in progress: {elapsed}/{duration} seconds elapsed")
                
                # Get intermediate results for monitoring
                if self.monitor:
                    summary = self.monitor.generate_summary()
                    print(f"Current metrics - CPU avg: {summary.get('cpu_avg', 0):.2f}%, Memory: {summary.get('memory_avg_mb', 0):.2f} MB")
            
            # Collect results
            print("Collecting monitoring results...")
            results = self.stop_monitoring()
            print(f"Results collected: {len(results.get('time_series', []))} data points")
            
            print(f"Saving results to {test_dir}")
            self.save_results(results, test_dir)
            print("Results saved")
            
            return results
            
        except Exception as e:
            print(f"ERROR: High FPS test failed: {e}")
            logger.error(f"High FPS test failed: {e}", exc_info=True)
            raise
        finally:
            print("Cleaning up resources...")
            self.cleanup()
            print("Cleanup complete")

def main():
    """Main entry point for running performance tests."""
    print("Starting performance test runner...")
    parser = argparse.ArgumentParser(description="Run performance tests for DAOC Sprint Manager")
    parser.add_argument("--test", choices=["baseline", "long_duration", "high_fps"], required=True,
                      help="Type of test to run")
    parser.add_argument("--duration", type=int, help="Test duration in seconds")
    parser.add_argument("--output-dir", default="test_results",
                      help="Directory to store test results")
    
    args = parser.parse_args()
    print(f"Args parsed: test={args.test}, duration={args.duration}, output_dir={args.output_dir}")
    
    try:
        print(f"Creating output directory: {args.output_dir}")
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Creating PerformanceTestRunner with output_dir={args.output_dir}")
        runner = PerformanceTestRunner(output_dir=args.output_dir)
        
        if args.test == "baseline":
            duration = args.duration or 1800  # 30 minutes default
            print(f"Running baseline test with duration={duration}")
            runner.run_baseline_test(duration=duration)
        elif args.test == "long_duration":
            duration = args.duration or 14400  # 4 hours default
            print(f"Running long duration test with duration={duration}")
            runner.run_long_duration_test(duration=duration)
        elif args.test == "high_fps":
            duration = args.duration or 3600  # 1 hour default
            print(f"Running high FPS test with duration={duration}")
            runner.run_high_fps_test(duration=duration)
            
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        logger.error(f"Test execution failed: {e}", exc_info=True)
        sys.exit(1)
    print("Performance test completed.")

if __name__ == "__main__":
    main() 