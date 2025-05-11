# Performance Testing Framework for DAOC Sprint Manager

This directory contains tools for performance testing the DAOC Sprint Manager application.

## Overview

The performance testing framework consists of the following components:

- `performance_test_runner.py`: Main script for running performance tests
- `performance_monitor.py`: Module for monitoring CPU and memory usage
- `mock_application.py`: Mock implementation of the application for testing
- `analyze_performance.py`: Script for analyzing test results

## Requirements

- Python 3.7+
- psutil library (`pip install psutil`)
- matplotlib (optional, for visualization: `pip install matplotlib`)

## Running Tests

The performance test runner supports three types of tests:

1. **Baseline Test**: Runs a short baseline performance test
2. **Long Duration Test**: Runs a longer stability test
3. **High FPS Test**: Tests performance with higher frame rates

### Command Line Usage

```bash
# Run a baseline test for 5 minutes
python testing/performance_test_runner.py --test baseline --duration 300 --output-dir testing/performance_results/baseline_test

# Run a long duration test for 1 hour
python testing/performance_test_runner.py --test long_duration --duration 3600 --output-dir testing/performance_results/long_test

# Run a high FPS test for 10 minutes with 60 FPS
python testing/performance_test_runner.py --test high_fps --duration 600 --output-dir testing/performance_results/high_fps_test
```

## Test Output

Each test run creates a directory with:

- `raw_results.json`: Raw performance data in JSON format
- `metrics.csv`: Time series data in CSV format

## Analyzing Results

The `analyze_performance.py` script can be used to analyze test results:

```bash
# Generate a summary report
python testing/analyze_performance.py --results-dir testing/performance_results/ --output-file testing/performance_summary.txt

# Generate comparison charts (requires matplotlib)
python testing/analyze_performance.py --results-dir testing/performance_results/ --compare --output-dir testing/performance_charts

# Generate time series charts (requires matplotlib)
python testing/analyze_performance.py --results-dir testing/performance_results/ --time-series --output-dir testing/performance_charts
```

## Test Implementation Details

### Performance Test Runner

The `PerformanceTestRunner` class handles:

- Setting up test environments
- Launching the application (or mock application)
- Monitoring CPU and memory usage
- Collecting and saving results

### Performance Monitor

The `PerformanceMonitor` class:

- Monitors CPU usage, memory usage, and other metrics
- Collects time series data
- Calculates summary statistics

### Mock Application

The `mock_application.py` script provides a simplified version of the DAOC Sprint Manager for testing. It simulates:

- Basic application behavior
- CPU and memory usage
- Command-line arguments

## Troubleshooting

- If tests fail, check the error messages and logs in the output directory
- Ensure the mock application has appropriate permissions
- For visualization, ensure matplotlib is installed

## Adding New Tests

To add a new test type:

1. Add a new method to the `PerformanceTestRunner` class
2. Update the command-line argument handling in `main()`
3. Implement test-specific configuration and monitoring 