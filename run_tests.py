"""
Test Runner for DAOC Sprint Manager
Runs tests and generates coverage reports
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def setup_test_environment():
    """Install test dependencies and prepare environment"""
    print("Setting up test environment...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"], check=True)
        print("Test dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def run_tests():
    """Run the test suite and generate reports"""
    report_dir = Path("test_environment/test_results/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure HTML report directory exists
    html_dir = report_dir / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    
    # Run tests with coverage
    print("\nRunning tests with coverage...")
    test_report = report_dir / "test_report.txt"
    
    try:
        # Run the test suite with coverage
        with open(test_report, "w") as report:
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    "--cov=src.daoc_sprint_manager",  # Cover main package
                    "--cov=testing",  # Cover testing utilities
                    "--cov-config=.coveragerc",  # Use coverage config file
                    "--cov-report=term-missing",  # Console output with missing lines
                    "--cov-report=html",  # HTML report
                    "--cov-report=xml",  # XML report
                    "--cov-report=json",  # JSON report
                    "-v",  # Verbose output
                    "test_suite.py"  # Test file to run
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            report.write(result.stdout)
            
        print(f"\nTest report saved to: {test_report}")
        print(f"Coverage reports generated in: {report_dir}")
        print("\nCoverage report locations:")
        print(f"- HTML: {html_dir}/index.html")
        print(f"- XML: {report_dir}/coverage.xml")
        print(f"- JSON: {report_dir}/coverage.json")
        
        # Return test success status
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main test runner function"""
    print("DAOC Sprint Manager Test Runner")
    print("==============================")
    
    # Setup test environment
    setup_test_environment()
    
    # Run tests and get results
    success = run_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 