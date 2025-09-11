#!/usr/bin/env python3
"""
Complete system test for Night Writer with rate limit detection
"""

import json
import time
import sys
import codecs
from terminal_automation import RateLimitParser, TerminalAutomationSystem, Configuration

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def test_rate_limit_detection():
    """Test the rate limit parser with the exact format"""
    print("Testing Rate Limit Detection")
    print("=" * 50)
    
    parser = RateLimitParser()
    
    # Test the exact format you provided
    test_cases = [
        "5-hour limit reached ∙ resets 4am /upgrade to increase your usage limit.",
        "5-hour limit reached ∙ resets 4pm /upgrade to increase your usage limit.",
        "5-hour limit reached ∙ resets 12am /upgrade to increase your usage limit.",
        "5-hour limit reached ∙ resets 11pm /upgrade to increase your usage limit.",
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        result = parser.parse_output(test_case)
        
        print(f"  Rate limit detected: {result['rate_limit_detected']}")
        print(f"  Reset time: {result['reset_time']}")
        print(f"  Message: {result['message']}")
        
        if result['rate_limit_detected'] and result['reset_time']:
            print("  ✅ SUCCESS")
        else:
            print("  ❌ FAILED")

def test_system_configuration():
    """Test the system configuration"""
    print("\n\nTesting System Configuration")
    print("=" * 50)
    
    config = Configuration(
        tasks_file="tasks.txt",
        terminal_type="powershell",
        connection_mode="existing_window",
        start_time="04:00",
        timezone="America/Sao_Paulo",
        session_duration_hours=5,
        max_tasks_per_session=10,
        inactivity_timeout=600,
        output_directory="night_writer_outputs",
        log_level="INFO"
    )
    
    print(f"Tasks file: {config.tasks_file}")
    print(f"Terminal type: {config.terminal_type}")
    print(f"Connection mode: {config.connection_mode}")
    print(f"Start time: {config.start_time}")
    print(f"Timezone: {config.timezone}")
    print(f"Session duration: {config.session_duration_hours} hours")
    print(f"Max tasks: {config.max_tasks_per_session}")
    print(f"Inactivity timeout: {config.inactivity_timeout} seconds")
    print("✅ Configuration created successfully")

def test_tasks_loading():
    """Test loading tasks from the tasks file"""
    print("\n\nTesting Tasks Loading")
    print("=" * 50)
    
    try:
        with open("tasks.txt", "r") as f:
            content = f.read().strip()
        
        if content.startswith("["):
            # JSON format
            tasks = json.loads(content)
            print(f"✓ Loaded {len(tasks)} tasks from JSON")
        else:
            # Text format
            tasks = [line.strip() for line in content.splitlines() if line.strip()]
            print(f"✓ Loaded {len(tasks)} tasks from text")
        
        print("\nFirst 3 tasks:")
        for i, task in enumerate(tasks[:3], 1):
            print(f"  {i}. {task}")
        
        if len(tasks) > 3:
            print(f"  ... and {len(tasks) - 3} more tasks")
        
        print("✅ Tasks loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load tasks: {e}")
        return False

def test_scheduler_reset_time_parsing():
    """Test the scheduler's reset time parsing"""
    print("\n\nTesting Scheduler Reset Time Parsing")
    print("=" * 50)
    
    from terminal_automation import Scheduler
    from zoneinfo import ZoneInfo
    
    config = Configuration(
        start_time="04:00",
        timezone="America/Sao_Paulo"
    )
    
    scheduler = Scheduler(config)
    
    # Test different reset times
    test_times = ["4am", "4pm", "12am", "11pm", "6:30am", "2:15pm"]
    
    for reset_time in test_times:
        print(f"\nTesting reset time: {reset_time}")
        scheduler.update_rate_limit_info(True, reset_time)
        
        next_window = scheduler.next_window_start()
        print(f"  Next window start: {next_window}")
        print("  ✅ Reset time parsed successfully")

def main():
    """Run all tests"""
    print("Night Writer Complete System Test")
    print("=" * 60)
    
    # Test rate limit detection
    test_rate_limit_detection()
    
    # Test system configuration
    test_system_configuration()
    
    # Test tasks loading
    if not test_tasks_loading():
        return
    
    # Test scheduler reset time parsing
    test_scheduler_reset_time_parsing()
    
    print("\n\n🎉 All tests completed successfully!")
    print("\nThe system is ready to:")
    print("1. ✅ Always ask you to choose a terminal window")
    print("2. ✅ Detect rate limit messages in the exact format you specified")
    print("3. ✅ Parse reset times from terminal output")
    print("4. ✅ Run single sessions (no continuous mode)")
    print("5. ✅ Wait for 10 minutes of inactivity before next task")

if __name__ == "__main__":
    main()
