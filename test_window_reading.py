#!/usr/bin/env python3
"""
Test window reading capabilities to detect rate limits
"""

import win32gui
import win32con
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_window_reading():
    """Test reading content from a specific window"""
    print("Testing Window Reading for Rate Limit Detection")
    print("=" * 50)
    
    # Get all windows
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and "Communication Attempt" in title:
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    print(f"Found {len(windows)} windows with 'Communication Attempt' in title:")
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"{i}. {title} (Handle: {hwnd})")
    
    if not windows:
        print("No windows found with 'Communication Attempt' in title")
        return
    
    # Test reading from the first window
    hwnd, title = windows[0]
    print(f"\nTesting reading from: {title} (Handle: {hwnd})")
    
    # Method 1: GetWindowText
    try:
        print("\n1. Testing GetWindowText...")
        window_text = win32gui.GetWindowText(hwnd)
        print(f"   Result: '{window_text}'")
        print(f"   Length: {len(window_text)}")
        
        if "limit" in window_text.lower() or "resets" in window_text.lower():
            print("   ✅ Found rate limit keywords in window title!")
        else:
            print("   ℹ️  No rate limit keywords in window title")
            
    except Exception as e:
        print(f"   ❌ GetWindowText failed: {e}")
    
    # Method 2: SendMessage approach
    try:
        print("\n2. Testing SendMessage approach...")
        text_length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
        print(f"   Text length: {text_length}")
        
        if text_length > 0:
            text_buffer = win32gui.PyMakeBuffer(text_length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, text_length + 1, text_buffer)
            
            # Try to decode the buffer
            try:
                if hasattr(text_buffer, 'decode'):
                    content = text_buffer[:text_length].decode('utf-8', errors='ignore')
                else:
                    content_bytes = bytes(text_buffer[:text_length])
                    content = content_bytes.decode('utf-8', errors='ignore')
                
                print(f"   Content: '{content}'")
                print(f"   Length: {len(content)}")
                
                if "limit" in content.lower() or "resets" in content.lower():
                    print("   ✅ Found rate limit keywords in window content!")
                else:
                    print("   ℹ️  No rate limit keywords in window content")
                    
            except Exception as decode_error:
                print(f"   ❌ Decode failed: {decode_error}")
                print(f"   Raw buffer type: {type(text_buffer)}")
                print(f"   Raw buffer: {text_buffer[:min(50, text_length)]}")
        else:
            print("   ℹ️  No text content in window")
            
    except Exception as e:
        print(f"   ❌ SendMessage approach failed: {e}")
    
    print("\n" + "=" * 50)
    print("Window reading test complete!")

if __name__ == "__main__":
    test_window_reading()
