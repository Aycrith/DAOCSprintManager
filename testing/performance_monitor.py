"""
Performance Monitoring Tool for Testing
Tracks CPU, memory usage and other performance metrics
"""

import psutil
import time
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

class PerformanceMonitor:
    def __init__(self, pid: int = None, output_dir: str = "testing/performance_logs"):
        """Initialize the performance monitor.
        
        Args:
            pid: Process ID to monitor (optional)
            output_dir: Directory to save performance logs
        """
        self.pid = pid
        self.process = None
        if pid:
            try:
                self.process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                logging.error(f"Process with PID {pid} not found")
        
        self.output_dir = output_dir
        self.ensure_output_dir()
        self.setup_logging()
        self.metrics: List[Dict] = []
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.interval = 1  # Default sampling interval in seconds
        
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def setup_logging(self):
        """Configure logging."""
        log_file = os.path.join(self.output_dir, "monitor.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def find_process(self, app_name: str = None):
        """Find process by name or use the already set PID"""
        if self.process:
            return self.process
            
        try:
            if app_name:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower().startswith(app_name.lower()):
                        self.process = proc
                        self.pid = proc.pid
                        return proc
            elif self.pid:
                self.process = psutil.Process(self.pid)
                return self.process
        except (psutil.NoSuchProcess, psutil.AccessDenied, TimeoutError) as e:
            logging.error(f"Error finding process: {e}")
            return None
        return None
        
    def collect_metrics(self, proc: psutil.Process) -> Dict:
        """Collect current performance metrics.
        
        Args:
            proc: Process to monitor
            
        Returns:
            Dict containing current metrics
        """
        try:
            cpu_percent = proc.cpu_percent()
            memory_info = proc.memory_info()
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_rss": memory_info.rss / 1024 / 1024,  # MB
                "memory_vms": memory_info.vms / 1024 / 1024,  # MB
                "num_threads": proc.num_threads(),
                "num_handles": proc.num_handles() if os.name == 'nt' else None
            }
            
            return metrics
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Error collecting metrics: {e}")
            return {}
    
    def _monitoring_thread_func(self):
        """Background thread function for continuous monitoring."""
        proc = self.find_process()
        if not proc:
            logging.error(f"Could not find process to monitor")
            return
            
        logging.info(f"Started monitoring process {proc.pid}")
        
        try:
            while not self.stop_event.is_set():
                metrics = self.collect_metrics(proc)
                if metrics:
                    self.metrics.append(metrics)
                    logging.info(f"Collected metrics: CPU={metrics.get('cpu_percent', 'N/A')}%, "
                               f"Memory={metrics.get('memory_rss', 'N/A')}MB")
                self.stop_event.wait(self.interval)
        except Exception as e:
            logging.error(f"Error in monitoring thread: {e}")
        finally:
            logging.info("Monitoring thread stopped")
            
    def start(self, interval: int = 1):
        """Start monitoring in a background thread.
        
        Args:
            interval: Sampling interval in seconds
        """
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logging.warning("Monitoring thread already running")
            return
            
        self.interval = interval
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_thread_func)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logging.info("Performance monitoring started")
        
    def stop(self):
        """Stop the monitoring thread and save results."""
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            logging.warning("No monitoring thread is running")
            return
            
        self.stop_event.set()
        self.monitoring_thread.join(timeout=5)
        logging.info("Performance monitoring stopped")
        self.save_metrics()
        
    def get_results(self) -> Dict:
        """Get the current results of monitoring.
        
        Returns:
            Dict containing time series data and summary statistics
        """
        summary = self.generate_summary()
        return {
            "time_series": self.metrics,
            "summary": summary
        }
            
    def start_monitoring(self, duration: int = 3600, interval: int = 1):
        """Start monitoring performance metrics.
        
        Args:
            duration: How long to monitor in seconds (default: 1 hour)
            interval: Sampling interval in seconds
        """
        start_time = time.time()
        proc = self.find_process()
        
        if not proc:
            logging.error(f"Could not find process to monitor")
            return
            
        logging.info(f"Started monitoring process {proc.pid}")
        
        try:
            while time.time() - start_time < duration:
                metrics = self.collect_metrics(proc)
                if metrics:
                    self.metrics.append(metrics)
                    logging.info(f"Collected metrics: CPU={metrics.get('cpu_percent', 'N/A')}%, "
                               f"Memory={metrics.get('memory_rss', 'N/A')}MB")
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
        finally:
            self.save_metrics()
            
    def save_metrics(self):
        """Save collected metrics to a JSON file."""
        if not self.metrics:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_metrics_{timestamp}.json"
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            json.dump({
                "process_id": self.pid,
                "start_time": self.metrics[0].get("timestamp") if self.metrics else None,
                "end_time": self.metrics[-1].get("timestamp") if self.metrics else None,
                "metrics": self.metrics
            }, f, indent=4)
            
        logging.info(f"Saved metrics to {output_path}")
        
    def _get_valid_timestamps(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the first and last valid timestamps from metrics.
        
        Returns:
            Tuple of (start_time, end_time) as datetime objects, or (None, None) if no valid timestamps.
        """
        valid_metrics = [m for m in self.metrics if "timestamp" in m]
        if not valid_metrics:
            logging.warning("No valid timestamps found in metrics")
            return None, None
            
        try:
            start_time = datetime.fromisoformat(valid_metrics[0]["timestamp"])
            end_time = datetime.fromisoformat(valid_metrics[-1]["timestamp"])
            return start_time, end_time
        except (ValueError, IndexError) as e:
            logging.error(f"Error parsing timestamps: {e}")
            return None, None
        
    def generate_summary(self) -> Dict:
        """Generate a summary of collected metrics.
        
        Returns:
            Dict containing performance summary with the following keys:
            - duration_seconds: Total duration of monitoring in seconds
            - cpu_avg: Average CPU usage percentage
            - cpu_max: Maximum CPU usage percentage
            - memory_avg_mb: Average memory usage in MB
            - memory_max_mb: Maximum memory usage in MB
            - num_samples: Number of valid samples collected
        """
        if not self.metrics:
            logging.info("No metrics collected, returning empty summary")
            return {
                "duration_seconds": 0,
                "cpu_avg": 0,
                "cpu_max": 0,
                "memory_avg_mb": 0,
                "memory_max_mb": 0,
                "num_samples": 0
            }
            
        # Get valid timestamps
        start_time, end_time = self._get_valid_timestamps()
        duration_seconds = (end_time - start_time).total_seconds() if start_time and end_time else 0
        
        # Extract valid metric values
        cpu_values = [m.get("cpu_percent", 0) for m in self.metrics if "cpu_percent" in m]
        memory_values = [m.get("memory_rss", 0) for m in self.metrics if "memory_rss" in m]
        
        # Calculate summary statistics
        summary = {
            "duration_seconds": duration_seconds,
            "cpu_avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "cpu_max": max(cpu_values) if cpu_values else 0,
            "memory_avg_mb": sum(memory_values) / len(memory_values) if memory_values else 0,
            "memory_max_mb": max(memory_values) if memory_values else 0,
            "num_samples": len(self.metrics)
        }
        
        logging.info(f"Generated summary: Duration={duration_seconds}s, "
                    f"Avg CPU={summary['cpu_avg']:.1f}%, "
                    f"Max CPU={summary['cpu_max']:.1f}%, "
                    f"Avg Memory={summary['memory_avg_mb']:.1f}MB")
        
        return summary
        
def main():
    """Main function to run performance monitoring."""
    monitor = PerformanceMonitor()
    
    print("Starting performance monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        monitor.start()
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        monitor.stop()
    
    summary = monitor.generate_summary()
    if summary["num_samples"] > 0:
        print("\nPerformance Summary:")
        print(f"Duration: {summary['duration_seconds']} seconds")
        print(f"Average CPU: {summary['cpu_avg']:.2f}%")
        print(f"Peak CPU: {summary['cpu_max']:.2f}%")
        print(f"Average Memory: {summary['memory_avg_mb']:.2f} MB")
        print(f"Peak Memory: {summary['memory_max_mb']:.2f} MB")
    else:
        print("\nNo metrics collected. Make sure the application is running.")
    
if __name__ == "__main__":
    main() 