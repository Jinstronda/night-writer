#!/usr/bin/env python3
"""
Test rate limit detection during task execution
"""

from terminal_automation import RateLimitParser

def test_rate_limit_detection():
    """Test rate limit detection with various formats"""
    print("Testing Rate Limit Detection")
    print("=" * 40)
    
    parser = RateLimitParser()
    
    # Test cases
    test_cases = [
        {
            "name": "Standard format with bullet",
            "output": "5-hour limit reached ∙ resets 2pm /upgrade to increase your usage limit.",
            "should_detect": True,
            "expected_reset": "2pm"
        },
        {
            "name": "Standard format with 4am",
            "output": "5-hour limit reached ∙ resets 4am /upgrade to increase your usage limit.",
            "should_detect": True,
            "expected_reset": "4am"
        },
        {
            "name": "Format with 6pm",
            "output": "5-hour limit reached ∙ resets 6pm /upgrade to increase your usage limit.",
            "should_detect": True,
            "expected_reset": "6pm"
        },
        {
            "name": "Format with 12pm",
            "output": "5-hour limit reached ∙ resets 12pm /upgrade to increase your usage limit.",
            "should_detect": True,
            "expected_reset": "12pm"
        },
        {
            "name": "Format with 12am",
            "output": "5-hour limit reached ∙ resets 12am /upgrade to increase your usage limit.",
            "should_detect": True,
            "expected_reset": "12am"
        },
        {
            "name": "No rate limit",
            "output": "Keep going with your tasks",
            "should_detect": False,
            "expected_reset": None
        },
        {
            "name": "Mixed content with rate limit",
            "output": "import { Account, AccountStatus } from '../types/session-manager';\n  ⎿  5-hour limit reached ∙ resets 2pm\n     /upgrade to increase your usage limit.",
            "should_detect": True,
            "expected_reset": "2pm"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['output'][:50]}...")
        
        result = parser.parse_output(test_case['output'])
        
        print(f"   Rate limit detected: {result['rate_limit_detected']}")
        print(f"   Reset time: {result['reset_time']}")
        print(f"   Message: {result['message'][:50] if result['message'] else 'None'}...")
        
        # Check results
        if result['rate_limit_detected'] == test_case['should_detect']:
            print("   ✅ Detection correct")
        else:
            print("   ❌ Detection incorrect")
        
        if result['reset_time'] == test_case['expected_reset']:
            print("   ✅ Reset time correct")
        else:
            print("   ❌ Reset time incorrect")
    
    print("\n" + "=" * 40)
    print("Rate limit detection test completed!")

if __name__ == "__main__":
    test_rate_limit_detection()
