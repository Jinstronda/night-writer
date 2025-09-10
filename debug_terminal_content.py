#!/usr/bin/env python3
"""
Debug script to test terminal content reading specifically
"""

from terminal_automation import TerminalAutomationSystem, Configuration
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_terminal_content():
    """Debug terminal content reading"""
    print("Debugging Terminal Content Reading")
    print("=" * 40)
    
    # Create a test configuration
    config = Configuration(
        tasks_file="tasks.txt",
        terminal_type="cmd",
        connection_mode="existing_window",
        inactivity_timeout=600,
        max_tasks_per_session=5,
        session_duration_hours=5,
        output_directory="night_writer_outputs"
    )
    
    # Create the system
    system = TerminalAutomationSystem(config)
    
    # Find terminal windows
    print("1. Finding terminal windows...")
    windows = system.terminal_manager.window_manager.find_terminal_windows()
    print(f"   Found {len(windows)} terminal windows:")
    for i, window in enumerate(windows, 1):
        print(f"   {i}. {window['title']} (Handle: {window['hwnd']})")
    
    if not windows:
        print("   No terminal windows found!")
        return
    
    # Select the first window
    selected_window = windows[0]
    print(f"\n2. Selected window: {selected_window['title']}")
    system.terminal_manager.selected_window = selected_window
    system.terminal_manager._is_existing_window = True
    
    # Test content reading
    print("\n3. Testing content reading methods...")
    
    # Test Method 1: Direct window reading
    print("\n   Method 1: Direct window reading...")
    try:
        content = system._read_window_content_directly()
        if content:
            print(f"   ✅ Got content: {len(content)} characters")
            print(f"   Content preview: {content[:100]}...")
        else:
            print("   ❌ No content from direct reading")
    except Exception as e:
        print(f"   ❌ Direct reading failed: {e}")
    
    # Test Method 5: Screenshot OCR
    print("\n   Method 5: Screenshot OCR...")
    try:
        content = system._try_screenshot_ocr()
        if content:
            print(f"   ✅ Got content: {len(content)} characters")
            print(f"   Content preview: {content[:200]}...")
            
            # Check for rate limit keywords
            if any(keyword in content.lower() for keyword in ['limit', 'resets', 'hour']):
                print("   ✅ Found rate limit keywords!")
            else:
                print("   ℹ️  No rate limit keywords found")
        else:
            print("   ❌ No content from screenshot OCR")
    except Exception as e:
        print(f"   ❌ Screenshot OCR failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the main content reading method
    print("\n4. Testing main content reading method...")
    try:
        content = system._get_terminal_content()
        if content:
            print(f"   ✅ Got content: {len(content)} characters")
            print(f"   Content preview: {content[:200]}...")
        else:
            print("   ❌ No content from main method")
    except Exception as e:
        print(f"   ❌ Main method failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_terminal_content()
