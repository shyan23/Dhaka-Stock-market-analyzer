#!/usr/bin/env python3
"""
Test runner for Stock Market Analyzer project
This script runs all tests with coverage and generates reports
"""
import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all tests with pytest"""
    print("🚀 Running Stock Market Analyzer Tests")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "test/", 
        "-v", 
        "--tb=short",
        "--cov=src",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=html:htmlcov",
        f"--cov-fail-under=50"  # Require at least 50% coverage
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0


def run_specific_test_suite(suite_name=None):
    """Run a specific test suite"""
    print(f"🚀 Running {suite_name or 'all'} tests")
    print("=" * 60)
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    cmd = [sys.executable, "-m", "pytest"]
    
    if suite_name:
        if suite_name == "unit":
            cmd.extend(["test/test_*.py", "-m", "unit"])
        elif suite_name == "integration":
            cmd.extend(["test/test_*.py", "-m", "integration"])
        elif suite_name == "models":
            cmd.append("test/test_models.py")
        elif suite_name == "api":
            cmd.extend(["test/test_dse_api.py", "test/test_data_manager.py"])
        elif suite_name == "ui":
            cmd.append("test/test_ui_components.py")
        else:
            cmd.append(f"test/test_{suite_name}.py")
    else:
        cmd.append("test/")
    
    cmd.extend(["-v", "--tb=short"])
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0


def check_test_coverage():
    """Check current test coverage"""
    print("📊 Checking test coverage...")
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "test/",
        "--cov=src",
        "--cov-report=term-missing"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def main():
    """Main function to run tests based on command line arguments"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            return check_test_coverage()
        elif sys.argv[1] in ["unit", "integration", "models", "api", "ui"]:
            return run_specific_test_suite(sys.argv[1])
        elif sys.argv[1] == "all":
            return run_tests()
        else:
            print(f"Unknown test suite: {sys.argv[1]}")
            print("Available options: all, unit, integration, models, api, ui, coverage")
            return False
    else:
        # Run all tests by default
        return run_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)