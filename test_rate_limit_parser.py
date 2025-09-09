#!/usr/bin/env python3
"""
Test script for the rate limit parser to verify it detects the specific format
"""

from terminal_automation import RateLimitParser

def test_rate_limit_parser():
    """Test the rate limit parser with the specific format"""
    parser = RateLimitParser()
    
    # Test the exact format you provided
    test_output = "5-hour limit reached ∙ resets 4am /upgrade to increase your usage limit."
    
    print("Testing Rate Limit Parser")
    print("=" * 50)
    print(f"Input: {test_output}")
    print()
    
    result = parser.parse_output(test_output)
    
    print("Results:")
    print(f"  Rate limit detected: {result['rate_limit_detected']}")
    print(f"  Reset time: {result['reset_time']}")
    print(f"  Message: {result['message']}")
    print()
    
    if result['rate_limit_detected'] and result['reset_time']:
        print("✅ SUCCESS: Rate limit and reset time detected correctly!")
    else:
        print("❌ FAILED: Rate limit or reset time not detected")
    
    # Test other variations
    test_cases = [
        "5-hour limit reached ∙ resets 4pm /upgrade to increase your usage limit.",
        "5-hour limit reached ∙ resets 12am /upgrade to increase your usage limit.",
        "5-hour limit reached ∙ resets 11pm /upgrade to increase your usage limit.",
        "rate limit reached ∙ resets 6am /upgrade to increase your usage limit.",
    ]
    
    print("\nTesting other variations:")
    print("-" * 30)
    
    for i, test_case in enumerate(test_cases, 1):
        result = parser.parse_output(test_case)
        print(f"{i}. {test_case}")
        print(f"   Detected: {result['rate_limit_detected']}, Reset: {result['reset_time']}")
        print()

if __name__ == "__main__":
    test_rate_limit_parser()
