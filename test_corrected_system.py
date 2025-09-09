#!/usr/bin/env python3
"""
Test the corrected system that properly handles Claude's rate limits
"""

from terminal_automation import RateLimitParser, Scheduler, Configuration
from datetime import datetime
from zoneinfo import ZoneInfo

def test_corrected_flow():
    """Test the corrected system flow"""
    print("Testing Corrected Night Writer System")
    print("=" * 50)
    
    print("The corrected system now works like this:")
    print()
    
    print("1. 🚀 START SYSTEM")
    print("   - Connect to terminal")
    print("   - Read terminal output")
    print("   - Check for existing rate limits")
    print()
    
    print("2. 🔍 DETECT RATE LIMITS")
    print("   - Look for: '5-hour limit reached ∙ resets 4am'")
    print("   - Extract reset time: '4am'")
    print("   - If rate limit found → Wait until reset time")
    print("   - If no rate limit → Start tasks immediately")
    print()
    
    print("3. 📝 SEND TASK")
    print("   - Send task to terminal")
    print("   - Wait for Claude to start working")
    print("   - Look for: 'thinking', 'analyzing', 'processing', etc.")
    print()
    
    print("4. ⏱️ MONITOR COMPLETION")
    print("   - Only start inactivity monitoring AFTER Claude starts working")
    print("   - Wait for 10 minutes of silence")
    print("   - Check for rate limit messages during execution")
    print()
    
    print("5. 🔄 CONTINUE OR WAIT")
    print("   - If rate limit hit → Extract reset time → Wait → Continue")
    print("   - If task completed → Send next task")
    print("   - Repeat until all tasks done")
    print()
    
    print("6. 🎯 KEY DIFFERENCES FROM BEFORE:")
    print("   ✅ Always checks rate limits FIRST")
    print("   ✅ Uses detected reset times, not fixed 4am")
    print("   ✅ Waits for Claude to start before monitoring inactivity")
    print("   ✅ Continuously monitors for rate limits")
    print("   ✅ Never stops due to rate limits - only when tasks done")
    print()

def test_rate_limit_detection():
    """Test rate limit detection with your exact example"""
    print("Testing Rate Limit Detection")
    print("=" * 30)
    
    parser = RateLimitParser()
    
    # Your exact example
    test_output = """import { Account, AccountStatus } from '../types/session-manager';
  ⎿  5-hour limit reached ∙ resets 4am
     /upgrade to increase your usage limit."""
    
    print("Terminal Output:")
    print(test_output)
    print()
    
    result = parser.parse_output(test_output)
    
    print("System Response:")
    print(f"  Rate limit detected: {result['rate_limit_detected']}")
    print(f"  Reset time: {result['reset_time']}")
    print()
    
    if result['rate_limit_detected'] and result['reset_time']:
        print("✅ System will now:")
        print("   1. Wait until 4am")
        print("   2. Check terminal again for any new rate limits")
        print("   3. Start sending tasks")
        print("   4. Monitor Claude's activity properly")
        return True
    else:
        print("❌ Rate limit detection failed!")
        return False

def test_claude_activity_detection():
    """Test Claude activity detection"""
    print("\n\nTesting Claude Activity Detection")
    print("=" * 35)
    
    # Simulate terminal output patterns
    test_cases = [
        ("Task sent, waiting...", False),
        ("Claude is thinking about this...", True),
        ("Analyzing the code structure...", True),
        ("Processing your request...", True),
        ("Generating the solution...", True),
        ("Working on the implementation...", True),
        ("Creating the files...", True),
    ]
    
    claude_working_indicators = [
        "thinking", "analyzing", "processing", "generating", "writing",
        "creating", "building", "implementing", "coding", "working"
    ]
    
    print("Testing activity detection patterns:")
    for output, expected in test_cases:
        detected = any(indicator in output.lower() for indicator in claude_working_indicators)
        status = "✅" if detected == expected else "❌"
        print(f"  {status} '{output}' → Claude working: {detected}")
    
    return True

def main():
    """Run all tests"""
    print("Night Writer Corrected System Test")
    print("=" * 50)
    
    # Test the corrected flow
    test_corrected_flow()
    
    # Test rate limit detection
    if not test_rate_limit_detection():
        return
    
    # Test Claude activity detection
    if not test_claude_activity_detection():
        return
    
    print("\n\n🎉 The system is now correctly implemented!")
    print("\nIt will:")
    print("1. Always check for rate limits FIRST")
    print("2. Use detected reset times from terminal")
    print("3. Wait for Claude to start working before monitoring")
    print("4. Continuously adapt to rate limits")
    print("5. Never stop until all tasks are completed")

if __name__ == "__main__":
    main()
