#!/usr/bin/env python3
"""
Debug script specifically for the Communication Attempt window
"""

from terminal_automation import TerminalAutomationSystem, Configuration
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_communication_window():
    """Debug the Communication Attempt window specifically"""
    print("Debugging Communication Attempt Window")
    print("=" * 45)
    
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
    
    # Find the Communication Attempt window
    communication_window = None
    for window in windows:
        if "Communication Attempt" in window['title']:
            communication_window = window
            break
    
    if not communication_window:
        print("   ❌ Communication Attempt window not found!")
        return
    
    print(f"\n2. Found Communication Attempt window: {communication_window['title']}")
    print(f"   Handle: {communication_window['hwnd']}")
    
    # Set up the terminal manager
    system.terminal_manager.selected_window = communication_window
    system.terminal_manager._is_existing_window = True
    
    # Test content reading
    print("\n3. Testing content reading on Communication Attempt window...")
    
    # Test the main content reading method
    print("\n   Testing main content reading method...")
    try:
        content = system._get_terminal_content()
        if content:
            print(f"   ✅ Got content: {len(content)} characters")
            print(f"   Content preview:")
            print("   " + "="*50)
            print("   " + content[:500])
            print("   " + "="*50)
            
            # Check for rate limit keywords
            if any(keyword in content.lower() for keyword in ['limit', 'resets', 'hour']):
                print("   ✅ Found rate limit keywords!")
                
                # Test rate limit parsing
                from terminal_automation import RateLimitParser
                parser = RateLimitParser()
                result = parser.parse_output(content)
                print(f"   Rate limit detected: {result['rate_limit_detected']}")
                print(f"   Reset time: {result['reset_time']}")
            else:
                print("   ℹ️  No rate limit keywords found")
        else:
            print("   ❌ No content from main method")
    except Exception as e:
        print(f"   ❌ Main method failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test screenshot OCR specifically
    print("\n4. Testing screenshot OCR on Communication Attempt window...")
    try:
        content = system._try_screenshot_ocr()
        if content:
            print(f"   ✅ Screenshot OCR got content: {len(content)} characters")
            print(f"   Content preview:")
            print("   " + "="*50)
            print("   " + content[:500])
            print("   " + "="*50)
            
            # Check for rate limit keywords
            if any(keyword in content.lower() for keyword in ['limit', 'resets', 'hour']):
                print("   ✅ Screenshot OCR found rate limit keywords!")
            else:
                print("   ℹ️  Screenshot OCR found no rate limit keywords")
        else:
            print("   ❌ Screenshot OCR got no content")
    except Exception as e:
        print(f"   ❌ Screenshot OCR failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_communication_window()
