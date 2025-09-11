#!/usr/bin/env python3
"""
🌙 Night Writer GUI Launcher

Simple launcher script for the Night Writer GUI application.
Just double-click to run!
"""

import sys
import os
import subprocess

def main():
    """Launch the Night Writer GUI"""
    try:
        # Ensure we're in the right directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Try to run the GUI
        if sys.platform == "win32":
            # On Windows, use pythonw to avoid console window
            try:
                subprocess.run([sys.executable.replace('python.exe', 'pythonw.exe'), 'night_writer_gui.py'], 
                             check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Fallback to regular python
                subprocess.run([sys.executable, 'night_writer_gui.py'], check=True)
        else:
            # On other platforms, use regular python
            subprocess.run([sys.executable, 'night_writer_gui.py'], check=True)
            
    except KeyboardInterrupt:
        print("Cancelled by user")
    except Exception as e:
        print(f"Error launching GUI: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
