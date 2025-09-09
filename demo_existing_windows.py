"""
Demo script showing how to use existing terminal windows

Author: João Panizzutti
"""

import sys
from terminal_automation import TerminalWindowManager

def demo_existing_windows():
    """Demonstrate finding and selecting existing terminal windows"""
    print("Night Writer - Existing Terminal Windows Demo")
    print("=" * 50)
    
    # Create window manager
    window_manager = TerminalWindowManager()
    
    # Find all terminal windows
    print("Scanning for terminal windows...")
    windows = window_manager.find_terminal_windows()
    
    if not windows:
        print("No terminal windows found.")
        return
    
    print(f"\nFound {len(windows)} terminal windows:")
    print("-" * 30)
    
    for i, window in enumerate(windows, 1):
        print(f"{i}. {window['title']}")
        print(f"   Process: {window['process_name']}")
        print(f"   PID: {window['pid']}")
        print(f"   Class: {window['class_name']}")
        print()
    
    # Let user select a window
    print("You can now use the CLI with --connection-mode existing_window")
    print("to connect to any of these windows!")
    print()
    print("Example commands:")
    print("  python night_writer_cli.py --connection-mode existing_window --test-mode")
    print("  python night_writer_cli.py --connection-mode auto_detect --test-mode")
    print("  python night_writer_cli.py --connection-mode new_window --test-mode")

if __name__ == "__main__":
    demo_existing_windows()
