#!/usr/bin/env python3
"""
Performance Test Results Analyzer

This script analyzes performance test results collected by performance_test_runner.py
and generates reports and visualizations to compare the results.
"""

import argparse
import json
import os
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any
import datetime

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not found. Visualization will be disabled.")
    print("Install it using: pip install matplotlib")

class PerformanceAnalyzer:
    """Analyzes performance test results and generates reports."""
    
    def __init__(self, results_dir: str):
        """Initialize the analyzer.
        
        Args:
            results_dir: Directory containing test results
        """
        self.results_dir = Path(results_dir)
        if not self.results_dir.exists():
            raise ValueError(f"Results directory does not exist: {results_dir}")
        
    def find_test_results(self) -> List[Dict]:
        """Find all test result directories and load their data.
        
        Returns:
            List of dictionaries containing test data
        """
        results = []
        
        # Find all test directories recursively
        for test_dir in self.results_dir.glob("**/*/"):
            results_file = test_dir / "raw_results.json"
            if results_file.exists():
                try:
                    # Load test results
                    with open(results_file, "r") as f:
                        data = json.load(f)
                    
                    # Get test metadata from directory path
                    test_name = test_dir.name
                    parent_dir = test_dir.parent.name
                    
                    # Extract test type and timestamp
                    if "_" in test_name:
                        parts = test_name.split("_")
                        if len(parts) >= 3:
                            test_type = "_".join(parts[:-2])
                            timestamp = "_".join(parts[-2:])
                        else:
                            test_type = parts[0]
                            timestamp = parts[-1]
                    else:
                        test_type = test_name
                        timestamp = "unknown"
                    
                    # Add metadata to results
                    test_data = {
                        "test_type": test_type,
                        "test_name": test_name,
                        "parent_dir": parent_dir,
                        "timestamp": timestamp,
                        "path": str(test_dir),
                        "results": data
                    }
                    
                    results.append(test_data)
                    
                except Exception as e:
                    print(f"Error loading results from {results_file}: {e}")
        
        # Sort results by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
    
    def generate_summary_report(self, results: List[Dict], output_file: str = None) -> str:
        """Generate a summary report from test results.
        
        Args:
            results: List of test results
            output_file: Optional file to write the report to
            
        Returns:
            Report text
        """
        if not results:
            return "No test results found."
        
        report = []
        report.append("PERFORMANCE TEST SUMMARY REPORT")
        report.append("=" * 80)
        report.append(f"Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Number of test results: {len(results)}")
        report.append("")
        
        # Group results by test type
        test_types = {}
        for result in results:
            test_type = result["test_type"]
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(result)
        
        # Generate summary for each test type
        for test_type, type_results in test_types.items():
            report.append(f"TEST TYPE: {test_type}")
            report.append("-" * 80)
            report.append(f"Number of test runs: {len(type_results)}")
            
            # Get latest result for this test type
            latest = type_results[0]
            summary = latest["results"]["summary"]
            
            report.append(f"Latest run: {latest['timestamp']}")
            report.append(f"  Duration: {summary['duration_seconds']:.2f} seconds")
            report.append(f"  CPU Average: {summary['cpu_avg']:.2f}%")
            report.append(f"  CPU Maximum: {summary['cpu_max']:.2f}%")
            report.append(f"  Memory Average: {summary['memory_avg_mb']:.2f} MB")
            report.append(f"  Memory Maximum: {summary['memory_max_mb']:.2f} MB")
            report.append(f"  Number of samples: {summary['num_samples']}")
            
            # Compare with previous run if available
            if len(type_results) > 1:
                previous = type_results[1]
                prev_summary = previous["results"]["summary"]
                
                report.append(f"Comparison with previous run ({previous['timestamp']}):")
                
                # Calculate percent changes
                cpu_avg_change = ((summary['cpu_avg'] - prev_summary['cpu_avg']) / 
                                max(prev_summary['cpu_avg'], 0.001)) * 100
                cpu_max_change = ((summary['cpu_max'] - prev_summary['cpu_max']) / 
                                max(prev_summary['cpu_max'], 0.001)) * 100
                mem_avg_change = ((summary['memory_avg_mb'] - prev_summary['memory_avg_mb']) / 
                                max(prev_summary['memory_avg_mb'], 0.001)) * 100
                mem_max_change = ((summary['memory_max_mb'] - prev_summary['memory_max_mb']) / 
                                max(prev_summary['memory_max_mb'], 0.001)) * 100
                
                report.append(f"  CPU Average: {cpu_avg_change:+.2f}%")
                report.append(f"  CPU Maximum: {cpu_max_change:+.2f}%")
                report.append(f"  Memory Average: {mem_avg_change:+.2f}%")
                report.append(f"  Memory Maximum: {mem_max_change:+.2f}%")
            
            report.append("")
        
        # Output the report
        report_text = "\n".join(report)
        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)
            print(f"Summary report written to {output_file}")
        
        return report_text
    
    def generate_comparison_chart(self, results: List[Dict], output_file: str = None):
        """Generate comparison charts from test results.
        
        Args:
            results: List of test results
            output_file: Optional file to write the chart to
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot generate charts: matplotlib is not installed")
            return
        
        if not results or len(results) < 2:
            print("Not enough test results to generate comparison charts.")
            return
        
        # Group results by test type
        test_types = {}
        for result in results:
            test_type = result["test_type"]
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(result)
        
        # Generate comparison chart for each test type
        for test_type, type_results in test_types.items():
            if len(type_results) < 2:
                continue
            
            # Limit to the 5 most recent results
            type_results = type_results[:5]
            
            # Extract timestamps and metrics
            timestamps = [r["timestamp"] for r in type_results]
            cpu_avgs = [r["results"]["summary"]["cpu_avg"] for r in type_results]
            cpu_maxs = [r["results"]["summary"]["cpu_max"] for r in type_results]
            mem_avgs = [r["results"]["summary"]["memory_avg_mb"] for r in type_results]
            mem_maxs = [r["results"]["summary"]["memory_max_mb"] for r in type_results]
            
            # Shorten timestamps for display
            short_timestamps = []
            for ts in timestamps:
                if len(ts) > 12:
                    short_timestamps.append(ts[-12:])
                else:
                    short_timestamps.append(ts)
            
            # Create a figure with 2 subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
            
            # Plot CPU usage
            ax1.bar(short_timestamps, cpu_avgs, label="CPU Average", alpha=0.7)
            ax1.bar(short_timestamps, cpu_maxs, label="CPU Maximum", alpha=0.4)
            ax1.set_title(f"CPU Usage - {test_type}")
            ax1.set_ylabel("CPU Usage (%)")
            ax1.legend()
            
            # Plot memory usage
            ax2.bar(short_timestamps, mem_avgs, label="Memory Average", alpha=0.7)
            ax2.bar(short_timestamps, mem_maxs, label="Memory Maximum", alpha=0.4)
            ax2.set_title(f"Memory Usage - {test_type}")
            ax2.set_ylabel("Memory Usage (MB)")
            ax2.legend()
            
            # Rotate x-axis labels for readability
            plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
            
            plt.tight_layout()
            
            # Save or show the figure
            if output_file:
                chart_file = f"{os.path.splitext(output_file)[0]}_{test_type}_chart.png"
                plt.savefig(chart_file)
                print(f"Comparison chart for {test_type} written to {chart_file}")
            else:
                plt.show()
    
    def analyze_time_series(self, results: List[Dict], output_dir: str = None):
        """Analyze time series data from test results.
        
        Args:
            results: List of test results
            output_dir: Optional directory to write charts to
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot generate time series charts: matplotlib is not installed")
            return
        
        if not results:
            print("No test results to analyze.")
            return
        
        for result in results:
            test_name = result["test_name"]
            test_type = result["test_type"]
            
            # Get time series data
            time_series = result["results"]["time_series"]
            if not time_series:
                continue
            
            # Extract timestamps and metrics
            timestamps = [datetime.datetime.fromisoformat(d["timestamp"]) for d in time_series]
            cpu_usage = [d["cpu_percent"] for d in time_series]
            memory_usage = [d["memory_rss"] for d in time_series]
            
            # Convert timestamps to relative seconds from start
            start_time = timestamps[0]
            rel_timestamps = [(t - start_time).total_seconds() for t in timestamps]
            
            # Create a figure with 2 subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Plot CPU usage over time
            ax1.plot(rel_timestamps, cpu_usage, 'b-', label="CPU Usage")
            ax1.set_title(f"CPU Usage Over Time - {test_name}")
            ax1.set_xlabel("Time (seconds)")
            ax1.set_ylabel("CPU Usage (%)")
            ax1.grid(True)
            
            # Plot memory usage over time
            ax2.plot(rel_timestamps, memory_usage, 'r-', label="Memory Usage")
            ax2.set_title(f"Memory Usage Over Time - {test_name}")
            ax2.set_xlabel("Time (seconds)")
            ax2.set_ylabel("Memory Usage (MB)")
            ax2.grid(True)
            
            plt.tight_layout()
            
            # Save or show the figure
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                chart_file = os.path.join(output_dir, f"{test_name}_time_series.png")
                plt.savefig(chart_file)
                print(f"Time series chart for {test_name} written to {chart_file}")
            else:
                plt.show()

def main():
    """Main entry point for the analyzer."""
    parser = argparse.ArgumentParser(description="Analyze performance test results")
    parser.add_argument("--results-dir", default="testing/performance_results",
                      help="Directory containing test results")
    parser.add_argument("--output-file", help="Output file for summary report")
    parser.add_argument("--output-dir", help="Output directory for charts")
    parser.add_argument("--compare", action="store_true", help="Generate comparison charts")
    parser.add_argument("--time-series", action="store_true", help="Generate time series charts")
    
    args = parser.parse_args()
    
    try:
        analyzer = PerformanceAnalyzer(args.results_dir)
        results = analyzer.find_test_results()
        
        if not results:
            print(f"No test results found in {args.results_dir}")
            return
        
        # Generate summary report
        report = analyzer.generate_summary_report(results, args.output_file)
        print(report)
        
        # Generate comparison charts if requested
        if args.compare:
            analyzer.generate_comparison_chart(results, args.output_file)
        
        # Generate time series charts if requested
        if args.time_series:
            analyzer.analyze_time_series(results, args.output_dir or "testing/performance_charts")
        
    except Exception as e:
        print(f"Error analyzing performance results: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 