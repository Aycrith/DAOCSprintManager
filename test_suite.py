"""
Test suite for DAOC Sprint Manager
"""

import unittest
import sys
import os
import json
import time
import logging
import shutil
import signal
import threading
import tempfile
from pathlib import Path
import psutil

# Add source and testing directories to Python path
sys.path.append(os.path.dirname(__file__))  # For test_environment_setup
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))  # For daoc_sprint_manager package

from test_environment_setup import TestEnvironmentSetup
from performance_monitor import PerformanceMonitor

class DAOCSprintManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_env = TestEnvironmentSetup()
        cls.test_env.setup()
        
        # Set up logging for tests
        cls.logger = logging.getLogger("test_logger")
        cls.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        cls.logger.addHandler(handler)

    def setUp(self):
        """Set up before each test"""
        self.config_file = self.test_env.config_dir / "settings.json"
        self.profiles_file = self.test_env.config_dir / "profiles.json"
        
    def test_01_installation_structure(self):
        """Test if installation structure is correct"""
        self.assertTrue(os.path.exists("test_environment"))
        self.assertTrue(os.path.exists("test_environment/test_results"))
        self.assertTrue(os.path.exists("test_environment/test_results/reports"))

    def test_02_configuration_files(self):
        """Test if configuration files are present"""
        self.assertTrue(os.path.exists("test_environment/config"))
        self.assertTrue(os.path.exists("test_environment/config/settings.json"))

    def test_03_template_files(self):
        """Test if template files are present"""
        self.assertTrue(os.path.exists("test_environment/templates"))
        self.assertTrue(os.path.exists("test_environment/templates/default_profile.json"))

    def test_04_executable_presence(self):
        """Test if executable files are present"""
        self.assertTrue(os.path.exists("test_environment/bin"))
        self.assertTrue(os.path.exists("test_environment/bin/sprint_manager.exe"))

    def test_05_profile_management(self):
        """Test profile management functionality"""
        self.assertTrue(os.path.exists("test_environment/profiles"))
        self.assertTrue(os.path.exists("test_environment/profiles/default.json"))

    def test_06_settings_validation(self):
        """Test settings validation"""
        self.assertTrue(os.path.exists("test_environment/config/validation_rules.json"))

    def test_07_resource_paths(self):
        """Test resource file paths"""
        resource_paths = [
            "test_environment/resources",
            "test_environment/resources/images",
            "test_environment/resources/sounds",
            "test_environment/resources/icons"
        ]
        for path in resource_paths:
            self.assertTrue(os.path.exists(path), f"Resource path {path} does not exist")

    def test_08_performance_monitor(self):
        """Test performance monitor functionality"""
        # Create a test directory for performance logs
        test_output_dir = "test_environment/test_results/performance_logs"
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Test 1: Basic monitoring functionality
        monitor = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
        monitor.start_monitoring(duration=2, interval=0.5)
        
        # Generate and verify summary
        summary = monitor.generate_summary()
        
        # Verify summary contains expected keys
        expected_keys = ["duration_seconds", "cpu_avg", "cpu_max", "memory_avg_mb", "memory_max_mb", "num_samples"]
        for key in expected_keys:
            self.assertIn(key, summary, f"Summary missing key: {key}")
        
        # Verify metrics were collected
        self.assertGreater(len(monitor.metrics), 0, "No metrics were collected")
        
        # Verify metric structure
        first_metric = monitor.metrics[0]
        self.assertIn("timestamp", first_metric)
        self.assertIn("cpu_percent", first_metric)
        self.assertIn("memory_rss", first_metric)
        
        # Verify values are within expected ranges
        self.assertGreaterEqual(first_metric["cpu_percent"], 0)
        self.assertLessEqual(first_metric["cpu_percent"], 100)
        self.assertGreater(first_metric["memory_rss"], 0)
        
        # Test 2: Non-existent process monitoring
        monitor_nonexistent = PerformanceMonitor(app_name="nonexistent_app", output_dir=test_output_dir)
        monitor_nonexistent.start_monitoring(duration=1, interval=0.5)
        
        # Verify empty metrics for non-existent process
        summary_nonexistent = monitor_nonexistent.generate_summary()
        self.assertEqual(summary_nonexistent["num_samples"], 0)
        self.assertEqual(summary_nonexistent["cpu_avg"], 0)
        
        # Test 3: Invalid timestamps handling
        monitor_invalid = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
        monitor_invalid.metrics = [
            {"timestamp": "invalid_time", "cpu_percent": 50},
            {"timestamp": "2024-01-01T00:00:00", "cpu_percent": 60}
        ]
        summary_invalid = monitor_invalid.generate_summary()
        self.assertEqual(summary_invalid["duration_seconds"], 0)
        
        # Test 4: Save metrics functionality
        monitor = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
        monitor.metrics = [
            {
                "timestamp": "2024-01-01T00:00:00",
                "cpu_percent": 50,
                "memory_rss": 1000
            }
        ]
        monitor.save_metrics()
        
        # Verify metrics file was created and contains valid JSON
        metrics_files = [f for f in os.listdir(test_output_dir) if f.startswith("performance_metrics_")]
        self.assertGreater(len(metrics_files), 0)
        
        latest_metrics_file = sorted(metrics_files)[-1]
        with open(os.path.join(test_output_dir, latest_metrics_file)) as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data["app_name"], "python")
            self.assertEqual(len(saved_data["metrics"]), 1)
            
        # Test 5: Empty metrics handling
        empty_monitor = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
        empty_monitor.save_metrics()  # Should not create a file
        empty_summary = empty_monitor.generate_summary()
        self.assertEqual(empty_summary["num_samples"], 0)
        
        # Test 6: Output directory error handling
        with tempfile.NamedTemporaryFile() as tmp_file:
            # Try to create monitor with a file path as output directory
            monitor_bad_dir = PerformanceMonitor(app_name="python", output_dir=tmp_file.name)
            self.assertIsNotNone(monitor_bad_dir)  # Should handle error gracefully
            
        # Test with non-existent parent directory
        bad_dir = "/nonexistent/path/performance_logs"
        monitor_nonexistent_dir = PerformanceMonitor(app_name="python", output_dir=bad_dir)
        self.assertIsNotNone(monitor_nonexistent_dir)  # Should handle error gracefully
            
        # Test 7: Process access error handling
        def mock_process_error(*args, **kwargs):
            raise psutil.AccessDenied()

        original_process_iter = psutil.process_iter
        psutil.process_iter = mock_process_error

        try:
            monitor_access_error = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
            proc = monitor_access_error.find_process()
            self.assertIsNone(proc)  # Should return None when access is denied
            
            # Test monitoring with access denied
            monitor_access_error.start_monitoring(duration=1, interval=0.5)
            self.assertEqual(len(monitor_access_error.metrics), 0)  # No metrics should be collected
            
            summary = monitor_access_error.generate_summary()
            self.assertEqual(summary["num_samples"], 0)  # Summary should show no samples
        finally:
            psutil.process_iter = original_process_iter  # Restore original function
            
        # Test 8: Main function coverage
        import sys
        original_argv = sys.argv.copy()
        
        try:
            # Test with valid arguments
            sys.argv = ['performance_monitor.py', '--app', 'python', '--duration', '1', '--interval', '0.5', '--output', test_output_dir]
            from performance_monitor import main
            main()
            
            # Verify metrics file was created
            metrics_files = [f for f in os.listdir(test_output_dir) if f.startswith('performance_metrics_')]
            self.assertGreater(len(metrics_files), 0)
            
            # Test with invalid arguments
            sys.argv = ['performance_monitor.py']  # Missing required arguments
            with self.assertRaises(SystemExit):
                main()
            
            # Test with invalid duration
            sys.argv = ['performance_monitor.py', '--app', 'python', '--duration', 'invalid', '--interval', '0.5']
            with self.assertRaises(SystemExit):
                main()
                
            # Test with invalid interval
            sys.argv = ['performance_monitor.py', '--app', 'python', '--duration', '1', '--interval', 'invalid']
            with self.assertRaises(SystemExit):
                main()
                
        finally:
            sys.argv = original_argv  # Restore original arguments
            
        # Test 9: Error handling coverage
        # Test directory creation error
        with tempfile.NamedTemporaryFile() as tmp_file:
            monitor = PerformanceMonitor(app_name="python", output_dir=tmp_file.name)
            self.assertIsNotNone(monitor)  # Should handle error gracefully
            monitor.save_metrics()  # Test saving metrics to invalid directory
            
        # Test process error handling
        def mock_process_error(*args, **kwargs):
            raise psutil.NoSuchProcess(123)
            
        psutil.process_iter = mock_process_error
        try:
            monitor = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
            proc = monitor.find_process()
            self.assertIsNone(proc)
            monitor.start_monitoring(duration=1, interval=0.5)  # Test monitoring with no process
            self.assertEqual(len(monitor.metrics), 0)
        finally:
            psutil.process_iter = original_process_iter
            
        # Test invalid timestamp handling
        monitor = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
        monitor.metrics = [{"timestamp": "invalid"}]
        summary = monitor.generate_summary()
        self.assertEqual(summary["duration_seconds"], 0)
        
        # Test keyboard interrupt handling
        def mock_keyboard_interrupt(*args, **kwargs):
            raise KeyboardInterrupt()
            
        original_sleep = time.sleep
        time.sleep = mock_keyboard_interrupt
        try:
            monitor = PerformanceMonitor(app_name="python", output_dir=test_output_dir)
            monitor.start_monitoring(duration=1, interval=0.5)
        finally:
            time.sleep = original_sleep

def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(DAOCSprintManagerTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 