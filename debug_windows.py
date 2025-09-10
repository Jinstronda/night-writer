#!/usr/bin/env python3
"""
Debug script to see what windows are being detected
"""

import win32gui
import win32process
import psutil

def debug_windows():
    """Debug window detection"""
    print("Debugging Window Detection")
    print("=" * 30)
    
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            if window_text.strip():
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    windows.append({
                        'hwnd': hwnd,
                        'title': window_text,
                        'class_name': class_name,
                        'pid': pid,
                        'process_name': process.name()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    print(f"Found {len(windows)} visible windows:")
    print()
    
    # Filter for terminal-like windows
    terminal_windows = []
    for window in windows:
        title = window['title'].lower()
        class_name = window['class_name'].lower()
        process_name = window['process_name'].lower()
        
        # Check if it looks like a terminal
        terminal_indicators = [
            'cmd', 'command', 'powershell', 'terminal', 'bash', 'git',
            'anaconda', 'conda', 'python', 'node', 'npm', 'yarn',
            'windows terminal', 'alacritty', 'hyper'
        ]
        
        is_terminal = any(indicator in title or indicator in class_name or indicator in process_name for indicator in terminal_indicators)
        
        if is_terminal:
            terminal_windows.append(window)
            print(f"TERMINAL: {window['title']} (Class: {window['class_name']}, Process: {window['process_name']})")
    
    print(f"\nFound {len(terminal_windows)} terminal windows:")
    for i, window in enumerate(terminal_windows, 1):
        print(f"{i}. {window['title']} (Handle: {window['hwnd']})")
        print(f"   Class: {window['class_name']}")
        print(f"   Process: {window['process_name']} (PID: {window['pid']})")
        print()

if __name__ == "__main__":
    debug_windows()
