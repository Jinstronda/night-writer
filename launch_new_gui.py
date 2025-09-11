"""
🚀 Launch New Night Writer GUI
Simple launcher for the redesigned interface
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the new GUI
from night_writer_gui_redesign import main

if __name__ == "__main__":
    print("🌙 Starting Night Writer - Modern Edition...")
    main()