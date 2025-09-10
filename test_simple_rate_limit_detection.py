#!/usr/bin/env python3
"""
Simple test to detect rate limits using the visible terminal content pattern
"""

def test_rate_limit_detection():
    """Test rate limit detection with known terminal content"""
    print("Testing Rate Limit Detection")
    print("=" * 35)
    
    # This is the actual terminal content you showed me
    terminal_content = """
> Go to the next task in the list of pending features or fixes for the financial dashboard
  ⎿  5-hour limit reached ∙ resets 7pm
     /upgrade to increase your usage limit.

> Go to the next task in the list of pending features or fixes for the financial dashboard
  ⎿  5-hour limit reached ∙ resets 7pm
     /upgrade to increase your usage limit.

> Go to the next task in the list of pending features or fixes for the financial dashboard
  ⎿  5-hour limit reached ∙ resets 7pm
     /upgrade to increase your usage limit.

> echo RATE_LIMIT_CHECK
  ⎿  5-hour limit reached ∙ resets 7pm
     /upgrade to increase your usage limit.

> echo TERMINAL_STATE && powershell -Command "Get-Content -Path 'con' -Tail 10"
  ⎿  5-hour limit reached ∙ resets 7pm
     /upgrade to increase your usage limit.

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ >                                                                    
"""
    
    print("🔍 Testing rate limit detection on actual terminal content...")
    
    # Test our rate limit parser
    from terminal_automation import RateLimitParser
    parser = RateLimitParser()
    
    result = parser.parse_output(terminal_content)
    
    print(f"✅ Rate limit detected: {result['rate_limit_detected']}")
    print(f"✅ Reset time: {result['reset_time']}")
    
    if result['rate_limit_detected']:
        print(f"\n🎯 SUCCESS! The parser correctly detected:")
        print(f"   - Rate limit is active")
        print(f"   - Reset time: {result['reset_time']}")
        print(f"\n💡 The system SHOULD wait until 7pm before sending tasks!")
    else:
        print("\n❌ FAILED! The parser did not detect the rate limit.")
    
    print("\n" + "="*50)
    print("The issue is NOT with rate limit detection!")
    print("The issue is that we're not getting this terminal content in the first place.")
    print("We need to fix the terminal content reading methods.")

if __name__ == "__main__":
    test_rate_limit_detection()
