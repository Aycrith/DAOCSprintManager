"""
Utility for monitoring script performance metrics.

Provides methods to time code sections and retrieve system resource usage
(CPU, Memory) for the current process.
"""

import logging
import os
import time
from typing import Dict, List, Optional, Tuple

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Logger might not be available here, warning logged in __init__

class PerformanceMonitor:
    """
    Monitors script performance including execution time and resource usage.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initializes the PerformanceMonitor.

        Args:
            logger: Logger instance for recording operations and errors.

        Raises:
            RuntimeError: If psutil is not installed.
        """
        self.logger = logger
        self.timers: Dict[str, float] = {}
        self.last_lap_times: Dict[str, float] = {}
        self.timed_stats: Dict[str, List[float]] = {}
        self.timed_stats_counts: Dict[str, int] = {}

        if not PSUTIL_AVAILABLE:
            self.logger.critical(
                "psutil library is not installed. Resource monitoring is disabled. "
                "Install it using: pip install psutil"
            )
            self.process = None # Mark process as unavailable
            # raise RuntimeError("psutil is required for PerformanceMonitor") # Option: Fail hard
        else:
            try:
                self.process = psutil.Process(os.getpid())
                # Prime the cpu_percent call as the first call returns 0 or requires interval
                self.process.cpu_percent(interval=None)
                self.logger.debug("PerformanceMonitor initialized with psutil.")
            except psutil.NoSuchProcess:
                 self.logger.error("Could not get current process information. Resource monitoring might fail.")
                 self.process = None
            except Exception as e:
                 self.logger.exception(f"Error initializing psutil process: {e}")
                 self.process = None


    def start_timer(self, name: str) -> None:
        """
        Starts a performance timer with the given name.

        Args:
            name: An identifier for the timer.
        """
        self.timers[name] = time.perf_counter()
        self.logger.debug(f"Timer '{name}' started.")

    def stop_timer(self, name: str) -> Optional[float]:
        """
        Stops the performance timer with the given name and returns the duration.

        Args:
            name: The identifier of the timer to stop.

        Returns:
            The elapsed time in seconds since the timer was started,
            or None if the timer name was not found.
        """
        if name not in self.timers:
            self.logger.error(f"Timer '{name}' was stopped but never started.")
            return None

        start_time = self.timers.pop(name) # Remove timer after stopping
        end_time = time.perf_counter()
        duration = end_time - start_time
        self.last_lap_times[name] = duration # Store the duration
        self.logger.debug(f"Timer '{name}' stopped. Duration: {duration:.6f} seconds.")
        return duration

    def record_metric_time(self, name: str, duration_ms: float) -> None:
        """
        Records a performance metric duration for the specified name.
        
        This is useful for tracking and comparing performance of different operations
        over time, like ML detection vs. template matching.
        
        Args:
            name: An identifier for the metric.
            duration_ms: The duration in milliseconds to record.
        """
        if name not in self.timed_stats:
            self.timed_stats[name] = []
            self.timed_stats_counts[name] = 0
            
        self.timed_stats[name].append(duration_ms)
        self.timed_stats_counts[name] += 1
        self.logger.debug(f"Recorded metric '{name}': {duration_ms:.2f}ms (Count: {self.timed_stats_counts[name]})")

    def get_average_metric_time(self, name: str) -> Optional[float]:
        """
        Calculates the average duration for the specified metric.
        
        Args:
            name: The identifier of the metric.
            
        Returns:
            The average duration in milliseconds, or None if no data exists.
        """
        if name in self.timed_stats and self.timed_stats[name]:
            avg = sum(self.timed_stats[name]) / len(self.timed_stats[name])
            self.logger.debug(f"Average metric time for '{name}': {avg:.2f}ms (Count: {self.timed_stats_counts[name]})")
            return avg
        return None
    
    def reset_metric(self, name: str) -> None:
        """
        Resets the collected metrics for the specified name.
        
        Args:
            name: The identifier of the metric to reset.
        """
        if name in self.timed_stats:
            self.timed_stats[name].clear()
            self.timed_stats_counts[name] = 0
            self.logger.debug(f"Reset metrics for '{name}'")

    def get_fps(self, cycle_time_s: float) -> float:
        """
        Calculates Frames Per Second (FPS) based on a cycle time.

        Args:
            cycle_time_s: The duration of one cycle in seconds.

        Returns:
            The calculated FPS, or 0.0 if cycle time is non-positive.
        """
        if cycle_time_s > 0.00001: # Avoid division by zero or near-zero
            return 1.0 / cycle_time_s
        else:
            return 0.0

    def get_script_resource_usage(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Gets the current CPU and Memory usage for the script's process.

        Returns:
            A tuple containing:
            - float or None: CPU usage percentage (since last call or process start).
            - float or None: Memory usage in MB (Resident Set Size).
            Returns (None, None) if psutil is unavailable or fails.
        """
        if self.process is None:
             self.logger.warning("Cannot get resource usage: psutil process not available.")
             return None, None

        try:
            # cpu_percent(interval=None) returns the usage since the last call
            cpu_percent: Optional[float] = self.process.cpu_percent(interval=None)

            # memory_info().rss gives the Resident Set Size in bytes
            memory_bytes = self.process.memory_info().rss
            memory_mb: Optional[float] = memory_bytes / (1024 * 1024) if memory_bytes is not None else None

            self.logger.debug(f"Resource usage: CPU={cpu_percent}%, Memory={memory_mb:.2f}MB")
            return cpu_percent, memory_mb

        except psutil.NoSuchProcess:
             self.logger.error("Process not found while getting resource usage.")
             self.process = None # Mark as unavailable
             return None, None
        except Exception as e:
             self.logger.exception(f"Error getting resource usage: {e}")
             return None, None


if __name__ == "__main__":
    import sys
    # Set up a basic logger for testing
    test_logger = logging.getLogger("PerfMonTest")
    test_logger.setLevel(logging.DEBUG)
    if not test_logger.handlers: # Avoid adding multiple handlers if run again
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'))
        test_logger.addHandler(handler)

    monitor = PerformanceMonitor(test_logger)

    print("\n--- Testing PerformanceMonitor ---")

    # Test Timer functionality
    print("\nTest 1: Timing a short task...")
    monitor.start_timer("short_sleep")
    time.sleep(0.15) # Sleep for 150ms
    duration = monitor.stop_timer("short_sleep")
    if duration is not None:
        print(f" -> Measured duration: {duration:.4f} seconds (expected ~0.15s)")
        print(f" -> Stored lap time: {monitor.last_lap_times.get('short_sleep'):.4f} seconds")
    else:
        print(" -> Failed to get duration.")

    print("\nTest 2: Trying to stop a non-existent timer...")
    duration_fail = monitor.stop_timer("non_existent")
    print(f" -> Result: {duration_fail} (expected None)")
    assert duration_fail is None

    # Test the new metrics functionality
    print("\nTest 3: Testing metrics recording...")
    monitor.record_metric_time("ml_detection", 5.2)
    monitor.record_metric_time("ml_detection", 6.1)
    monitor.record_metric_time("ml_detection", 4.8)
    monitor.record_metric_time("template_detection", 2.3)
    monitor.record_metric_time("template_detection", 2.1)
    
    ml_avg = monitor.get_average_metric_time("ml_detection")
    template_avg = monitor.get_average_metric_time("template_detection")
    nonexistent_avg = monitor.get_average_metric_time("nonexistent")
    
    print(f" -> ML Detection Average: {ml_avg:.2f}ms (expected ~5.37ms)")
    print(f" -> Template Detection Average: {template_avg:.2f}ms (expected ~2.20ms)")
    print(f" -> Nonexistent Average: {nonexistent_avg} (expected None)")
    
    print("\nTest 4: Testing metrics reset...")
    monitor.reset_metric("ml_detection")
    ml_avg_after_reset = monitor.get_average_metric_time("ml_detection")
    print(f" -> ML Detection Average after reset: {ml_avg_after_reset} (expected None)")
    
    # Continue with existing tests
    print("\nTest 5: Calculating FPS...")
    cycle_time_1 = 0.1 # 10 FPS
    cycle_time_2 = 1.0 / 60.0 # 60 FPS
    fps1 = monitor.get_fps(cycle_time_1)
    fps2 = monitor.get_fps(cycle_time_2)
    print(f" -> FPS for cycle time {cycle_time_1:.4f}s: {fps1:.1f} FPS")
    print(f" -> FPS for cycle time {cycle_time_2:.4f}s: {fps2:.1f} FPS")
    assert abs(fps1 - 10.0) < 0.1
    assert abs(fps2 - 60.0) < 0.1

    # Test Resource Usage (if psutil is available)
    print("\nTest 6: Getting resource usage...")
    if monitor.process:
        # Call multiple times to see cpu_percent change
        for i in range(3):
            cpu, mem = monitor.get_script_resource_usage()
            print(f" -> Usage {i+1}: CPU = {cpu if cpu is not None else 'N/A'}%, Memory = {f'{mem:.2f}' if mem is not None else 'N/A'} MB")
            time.sleep(0.1) # Allow some time for CPU usage to register difference

        # Simulate some CPU work
        print(" -> Simulating CPU work...")
        list_comp = [x*x for x in range(1000000)] # Example work
        cpu_after_work, mem_after_work = monitor.get_script_resource_usage()
        print(f" -> Usage after work: CPU = {cpu_after_work if cpu_after_work is not None else 'N/A'}%, Memory = {f'{mem_after_work:.2f}' if mem_after_work is not None else 'N/A'} MB")

    else:
        print(" -> Skipping resource usage test because psutil is not available or failed to initialize.")

    print("\n--- PerformanceMonitor Test Complete ---") 