#!/usr/bin/env python3
"""
Resume Analysis Runner
======================

Simple script to run the resume analysis system.
"""

import os
import sys
import subprocess

# Resolve project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    """Main runner function."""
    print("[System] Resume Dataset Analysis & Skill Demand Visualization System")
    print("=" * 60)

    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[OK] Virtual environment is active")
    else:
        print("[Warning] No virtual environment detected. Consider activating one.")

    # Check if required files exist
    required_files = [
        "requirements.txt",
        "src/resume_analyzer.py",
        "src/app.py",
        "Dataset/Resume/Resume.csv"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(os.path.join(SCRIPT_DIR, file_path)):
            missing_files.append(file_path)

    if missing_files:
        print("[Error] Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are present before running.")
        return

    print("[OK] All required files found")

    # Menu for user choice
    while True:
        print("\n[Menu] Choose an option:")
        print("1. Run core analysis (generates reports and visualizations)")
        print("2. Launch interactive web dashboard")
        print("3. Open Jupyter notebook for exploration")
        print("4. Install/update dependencies")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\n[Info] Running core analysis...")
            try:
                subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, "src/resume_analyzer.py")], check=True, cwd=SCRIPT_DIR)
                print("[OK] Analysis complete! Check generated files.")
            except subprocess.CalledProcessError as e:
                print(f"[Error] Analysis failed: {e}")
            except KeyboardInterrupt:
                print("\n[Stop] Analysis interrupted by user")

        elif choice == "2":
            print("\n[Info] Launching Streamlit dashboard...")
            print("The dashboard will open in your default web browser.")
            print("Press Ctrl+C in the terminal to stop the server.")
            try:
                subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.join(SCRIPT_DIR, "src/app.py")], check=True, cwd=SCRIPT_DIR)
            except subprocess.CalledProcessError as e:
                print(f"[Error] Failed to launch dashboard: {e}")
            except KeyboardInterrupt:
                print("\n[Stop] Dashboard server stopped")

        elif choice == "3":
            print("\n[Info] Opening Jupyter notebook...")
            try:
                subprocess.run([sys.executable, "-m", "jupyter", "notebook", os.path.join(SCRIPT_DIR, "src/resume_analysis.ipynb")], check=True, cwd=SCRIPT_DIR)
            except subprocess.CalledProcessError as e:
                print(f"[Error] Failed to open notebook: {e}")
                print("Make sure Jupyter is installed: pip install jupyter")

        elif choice == "4":
            print("\n[Info] Installing/updating dependencies...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(SCRIPT_DIR, "requirements.txt")], check=True)
                print("[OK] Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"[Error] Failed to install dependencies: {e}")

        elif choice == "5":
            print("\n[Exit] Goodbye!")
            break

        else:
            print("[Error] Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()