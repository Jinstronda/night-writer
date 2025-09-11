"""
Build script to create Night Writer executable
"""
import subprocess
import sys
import os
from pathlib import Path

def build_exe():
    """Build the Night Writer exe using PyInstaller"""
    print("Building Night Writer executable...")
    
    # Get current directory
    current_dir = Path.cwd()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single exe file
        "--windowed",  # No console window (GUI only)
        "--name", "Night Writer",  # Name of the exe
        "--add-data", "tasks.txt;.",  # Include tasks.txt
        "--hidden-import", "win32gui",  # Ensure Windows API imports are included
        "--hidden-import", "win32con",
        "--hidden-import", "win32api",
        "--hidden-import", "win32process",
        "--hidden-import", "win32clipboard",
        "--hidden-import", "pygetwindow",
        "--hidden-import", "pyautogui",
        "--hidden-import", "PIL",
        "--hidden-import", "easyocr",
        "night_writer_simple.py"  # Main script
    ]
    if Path("icon.ico").exists():
        cmd.extend(["--icon", "icon.ico"])
    
    print("Running command:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print("\nExecutable created in: dist/Night Writer.exe")
        print("\nYou can now share this exe file with anyone!")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    return True

if __name__ == "__main__":
    build_exe()