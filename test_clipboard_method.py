#!/usr/bin/env python3
"""
Test the clipboard method directly
"""

from terminal_automation import TerminalAutomationSystem, Configuration
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_clipboard_method():
    """Test the clipboard method directly"""
    print("Testing Clipboard Method")
    print("=" * 30)
    
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
    
    # Find the Communication Attempt window
    windows = system.terminal_manager.window_manager.find_terminal_windows()
    communication_window = None
    
    for window in windows:
        if "Communication Attempt" in window['title']:
            communication_window = window
            break
    
    if not communication_window:
        print("❌ Communication Attempt window not found!")
        return
    
    print(f"✅ Found Communication Attempt window: {communication_window['title']}")
    
    # Set up the terminal manager
    system.terminal_manager.selected_window = communication_window
    system.terminal_manager._is_existing_window = True
    
    # Test the clipboard method directly
    print("\n🧪 Testing clipboard method directly...")
    
    try:
        content = system._try_clipboard_copy_method()
        if content:
            print(f"✅ Clipboard method succeeded! Got {len(content)} characters")
            print("\n📄 Content preview (first 500 characters):")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
            
            # Check for rate limit keywords
            if any(keyword in content.lower() for keyword in ['limit', 'resets', 'hour']):
                print("\n🎯 FOUND RATE LIMIT KEYWORDS!")
                
                # Test rate limit parsing
                from terminal_automation import RateLimitParser
                parser = RateLimitParser()
                result = parser.parse_output(content)
                print(f"   Rate limit detected: {result['rate_limit_detected']}")
                print(f"   Reset time: {result['reset_time']}")
            else:
                print("\n ℹ️  No rate limit keywords found")
        else:
            print("❌ Clipboard method failed - no content returned")
    except Exception as e:
        print(f"❌ Clipboard method failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Make sure the '✳ Communication Attempt' terminal window is visible and contains the rate limit message!")
    print("Press Enter when ready...")
    input()
    test_clipboard_method()
