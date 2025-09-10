#!/usr/bin/env python3
"""
Test screenshot OCR functionality for terminal content reading
"""

from PIL import ImageGrab
import easyocr
import pygetwindow as gw
import win32gui
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_screenshot_ocr():
    """Test screenshot OCR on terminal windows"""
    print("Testing Screenshot OCR for Terminal Content Reading")
    print("=" * 55)
    
    # Find terminal windows
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and ("Communication Attempt" in title or "Terminal" in title or "Prompt" in title):
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    print(f"Found {len(windows)} terminal windows:")
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"{i}. {title} (Handle: {hwnd})")
    
    if not windows:
        print("No terminal windows found")
        return
    
    # Test on the terminal window that should have rate limit content
    target_window = None
    for hwnd, title in windows:
        if "Communication Attempt" in title:
            target_window = (hwnd, title)
            break
    
    if not target_window:
        target_window = windows[0]  # Fallback to first window
    
    hwnd, title = target_window
    print(f"\nTesting screenshot OCR on: {title}")
    
    try:
        # Method 1: Try pygetwindow
        print("\n1. Trying pygetwindow approach...")
        try:
            py_windows = gw.getWindowsWithTitle(title)
            if py_windows:
                window = py_windows[0]
                print(f"   Found window: {window.left}, {window.top}, {window.width}, {window.height}")
                
                # Take screenshot
                bbox = (window.left, window.top, window.left + window.width, window.top + window.height)
                screenshot = ImageGrab.grab(bbox=bbox)
                print(f"   Screenshot captured: {screenshot.size}")
                
                # Save screenshot for debugging
                screenshot.save("terminal_screenshot.png")
                print("   Screenshot saved as 'terminal_screenshot.png'")
                
            else:
                print("   Window not found via pygetwindow")
                raise Exception("Window not found")
                
        except Exception as e:
            print(f"   pygetwindow failed: {e}")
            print("   Trying win32gui approach...")
            
            # Method 2: Use win32gui
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            print(f"   Window rect: {left}, {top}, {right}, {bottom}")
            
            # Take screenshot
            bbox = (left, top, right, bottom)
            screenshot = ImageGrab.grab(bbox=bbox)
            print(f"   Screenshot captured: {screenshot.size}")
            
            # Save screenshot for debugging
            screenshot.save("terminal_screenshot.png")
            print("   Screenshot saved as 'terminal_screenshot.png'")
        
        # Initialize EasyOCR
        print("\n2. Initializing EasyOCR...")
        reader = easyocr.Reader(['en'], gpu=False)
        print("   EasyOCR initialized successfully")
        
        # Perform OCR
        print("\n3. Performing OCR...")
        # Convert PIL Image to numpy array for EasyOCR
        import numpy as np
        screenshot_array = np.array(screenshot)
        results = reader.readtext(screenshot_array)
        print(f"   Found {len(results)} text regions")
        
        # Extract text
        extracted_text = []
        for i, (bbox, text, confidence) in enumerate(results):
            print(f"   Text {i+1}: '{text}' (confidence: {confidence:.2f})")
            if confidence > 0.5:
                extracted_text.append(text)
        
        if extracted_text:
            content = "\n".join(extracted_text)
            print(f"\n4. Extracted content ({len(content)} characters):")
            print("-" * 40)
            print(content)
            print("-" * 40)
            
            # Check for rate limit keywords
            if any(keyword in content.lower() for keyword in ['limit', 'resets', 'hour']):
                print("   ✅ Found rate limit keywords!")
            else:
                print("   ℹ️  No rate limit keywords found")
        else:
            print("   ❌ No text extracted")
            
    except Exception as e:
        print(f"❌ Screenshot OCR test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 55)
    print("Screenshot OCR test complete!")

if __name__ == "__main__":
    test_screenshot_ocr()
