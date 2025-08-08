#!/usr/bin/env python3
"""
Test runner script for SkillSwap application.
This script provides an easy way to run tests with different options.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to run tests."""
    print("🧪 SkillSwap Test Runner")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("tests"):
        print("❌ Error: tests directory not found. Please run this script from the SkillSwap directory.")
        sys.exit(1)
    
    # Check if pytest is installed
    try:
        subprocess.run(["pytest", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: pytest not found. Please install it with: pip install pytest pytest-flask pytest-cov")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        print("\nAvailable test options:")
        print("1. Run all tests")
        print("2. Run tests with coverage")
        print("3. Run tests with verbose output")
        print("4. Run specific test file")
        print("5. Run tests and show coverage report")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            command = "pytest"
        elif choice == "2":
            command = "pytest --cov=app"
        elif choice == "3":
            command = "pytest -v"
        elif choice == "4":
            test_file = input("Enter test file name (e.g., test_models.py): ").strip()
            command = f"pytest tests/{test_file}"
        elif choice == "5":
            command = "pytest --cov=app --cov-report=html --cov-report=term-missing"
        else:
            print("Invalid choice. Running all tests...")
            command = "pytest"
    
    print(f"\n🚀 Running: {command}")
    print("-" * 40)
    
    # Run the test command
    success = run_command(command)
    
    if success:
        print("\n✅ Tests completed successfully!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
