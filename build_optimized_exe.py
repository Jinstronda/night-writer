"""
Optimized build script for Night Writer executable - excludes heavy ML dependencies
"""
import subprocess
import sys
import os
from pathlib import Path

def build_optimized_exe():
    """Build optimized Night Writer exe excluding heavy dependencies"""
    print("🌙 Building OPTIMIZED Night Writer executable...")
    
    # PyInstaller command with aggressive exclusions
    cmd = [
        "pyinstaller",
        "--onefile",  # Single exe file
        "--windowed",  # No console window (GUI only)
        "--name", "Night Writer",  # Name of the exe
        "--add-data", "tasks.txt;.",  # Include tasks.txt
        
        # Exclude heavy ML/computer vision libraries
        "--exclude-module", "cv2",
        "--exclude-module", "opencv-python",
        "--exclude-module", "numpy", 
        "--exclude-module", "scipy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "pandas",
        "--exclude-module", "torch",
        "--exclude-module", "tensorflow",
        "--exclude-module", "easyocr",
        "--exclude-module", "keras",
        "--exclude-module", "sklearn",
        "--exclude-module", "skimage",
        
        # Exclude other heavy packages
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        "--exclude-module", "notebook",
        "--exclude-module", "sphinx",
        
        # Hidden imports for required packages
        "--hidden-import", "win32gui",
        "--hidden-import", "win32con", 
        "--hidden-import", "win32api",
        "--hidden-import", "win32process",
        "--hidden-import", "win32clipboard",
        "--hidden-import", "pygetwindow",
        "--hidden-import", "pyautogui",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageGrab",
        "--hidden-import", "psutil",
        
        "night_writer_simple.py"  # Main script
    ]
    
    print("Running optimized command:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Optimized build successful!")
        
        # Check file size
        exe_path = Path("dist/Night Writer.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📁 Executable created: {exe_path}")
            print(f"📏 File size: {size_mb:.1f} MB")
            print("\n🚀 You can now share this exe file with anyone!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Optimized build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    return True

if __name__ == "__main__":
    build_optimized_exe()