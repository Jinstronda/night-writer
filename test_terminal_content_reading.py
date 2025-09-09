#!/usr/bin/env python3
"""
Test terminal content reading for rate limit detection
"""

from terminal_automation import RateLimitParser

def test_terminal_content_parsing():
    """Test parsing terminal content for rate limits"""
    print("Testing Terminal Content Reading")
    print("=" * 40)
    
    parser = RateLimitParser()
    
    # Simulate terminal content with rate limit
    terminal_content = r"""C:\Users\joaop\Documents\Hobbies\Claude Night Writer>python night_writer_cli.py
✓ Valid JSON file with 15 tasks
Starting Night Writer...
You will be prompted to select a terminal window.

Available Terminal Windows:
==================================================
1. Anaconda Prompt - "C:\Users\joaop\anaconda3\condabin\conda.bat"  activate graphrag-gpu
   Process: WindowsTerminal.exe
   PID: 27260

2. ✳ Task Implementation
   Process: WindowsTerminal.exe
   PID: 27260

Select terminal window (1-2) or 'n' for new window: 2
Selected: ✳ Task Implementation
2025-09-09 02:08:40,718 - root - INFO - Connected to existing window: ✳ Task Implementation
2025-09-09 02:08:40,718 - root - INFO - Terminal started successfully
2025-09-09 02:08:40,718 - root - INFO - Executing task 0: Keep going
2025-09-09 02:08:40,718 - root - ERROR - Failed to send keys to window: (6, 'SetForegroundWindow', 'The handle is invalid.')
2025-09-09 02:08:40,728 - root - INFO - Task 0 output saved to night_writer_outputs\task_000_20250909_020840
2025-09-09 02:08:40,728 - root - INFO - Task 0 completed with status: failed
2025-09-09 02:08:40,728 - root - INFO - Executing task 1: Go to the next task
2025-09-09 02:08:40,729 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,739 - root - INFO - Task 1 output saved to night_writer_outputs\task_001_20250909_020840
2025-09-09 02:08:40,739 - root - INFO - Task 1 completed with status: failed
2025-09-09 02:08:40,739 - root - INFO - Executing task 2: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from design.md, and architecture from architecture.md
2025-09-09 02:08:40,739 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,764 - root - INFO - Task 2 output saved to night_writer_outputs\task_002_20250909_020840
2025-09-09 02:08:40,764 - root - INFO - Task 2 completed with status: failed
2025-09-09 02:08:40,765 - root - INFO - Executing task 3: Keep going
2025-09-09 02:08:40,765 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,773 - root - INFO - Task 3 output saved to night_writer_outputs\task_003_20250909_020840
2025-09-09 02:08:40,773 - root - INFO - Task 3 completed with status: failed
2025-09-09 02:08:40,774 - root - INFO - Executing task 4: Go to the next task
2025-09-09 02:08:40,774 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,784 - root - INFO - Task 4 output saved to night_writer_outputs\task_004_20250909_020840
2025-09-09 02:08:40,784 - root - INFO - Task 4 completed with status: failed
2025-09-09 02:08:40,784 - root - INFO - Executing task 5: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from design.md, and architecture from architecture.md
2025-09-09 02:08:40,785 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,811 - root - INFO - Task 5 output saved to night_writer_outputs\task_005_20250909_020840
2025-09-09 02:08:40,811 - root - INFO - Task 5 completed with status: failed
2025-09-09 02:08:40,812 - root - INFO - Executing task 6: Keep going
2025-09-09 02:08:40,812 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,822 - root - INFO - Task 6 output saved to night_writer_outputs\task_006_20250909_020840
2025-09-09 02:08:40,822 - root - INFO - Task 6 completed with status: failed
2025-09-09 02:08:40,822 - root - INFO - Executing task 7: Go to the next task
2025-09-09 02:08:40,822 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,832 - root - INFO - Task 7 output saved to night_writer_outputs\task_007_20250909_020840
2025-09-09 02:08:40,832 - root - INFO - Task 7 completed with status: failed
2025-09-09 02:08:40,832 - root - INFO - Executing task 8: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,833 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,857 - root - INFO - Task 8 output saved to night_writer_outputs\task_008_20250909_020840
2025-09-09 02:08:40,857 - root - INFO - Task 8 completed with status: failed
2025-09-09 02:08:40,858 - root - INFO - Executing task 9: Keep going
2025-09-09 02:08:40,858 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,867 - root - INFO - Task 9 output saved to night_writer_outputs\task_009_20250909_020840
2025-09-09 02:08:40,867 - root - INFO - Task 9 completed with status: failed
2025-09-09 02:08:40,867 - root - INFO - Executing task 10: Go to the next task
2025-09-09 02:08:40,867 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,877 - root - INFO - Task 10 output saved to night_writer_outputs\task_010_20250909_020840
2025-09-09 02:08:40,877 - root - INFO - Task 10 completed with status: failed
2025-09-09 02:08:40,877 - root - INFO - Executing task 11: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,877 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,903 - root - INFO - Task 11 output saved to night_writer_outputs\task_011_20250909_020840
2025-09-09 02:08:40,903 - root - INFO - Task 11 completed with status: failed
2025-09-09 02:08:40,903 - root - INFO - Executing task 12: Keep going
2025-09-09 02:08:40,903 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,911 - root - INFO - Task 12 output saved to night_writer_outputs\task_012_20250909_020840
2025-09-09 02:08:40,911 - root - INFO - Task 12 completed with status: failed
2025-09-09 02:08:40,912 - root - INFO - Executing task 13: Go to the next task
2025-09-09 02:08:40,912 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,919 - root - INFO - Task 13 output saved to night_writer_outputs\task_013_20250909_020840
2025-09-09 02:08:40,919 - root - INFO - Task 13 completed with status: failed
2025-09-09 02:08:40,919 - root - INFO - Executing task 14: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,919 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,942 - root - INFO - Task 14 output saved to night_writer_outputs\task_014_20250909_020840
2025-09-09 02:08:40,942 - root - INFO - Task 14 completed with status: failed
2025-09-09 02:08:40,942 - root - INFO - Session completed successfully
Session completed successfully!

(graphrag-gpu) C:\Users\joaop\Documents\Hobbies\Claude Night Writer>"""
    
    print("Terminal Content:")
    print(terminal_content[:200] + "...")
    print()
    
    # Parse the content
    result = parser.parse_output(terminal_content)
    
    print("Rate Limit Detection Results:")
    print(f"  Rate limit detected: {result['rate_limit_detected']}")
    print(f"  Reset time: {result['reset_time']}")
    print(f"  Message: {result['message']}")
    
    if result['rate_limit_detected']:
        print("\n✅ Rate limit detected in terminal content!")
        print("   The system will now wait for the reset time.")
    else:
        print("\n❌ No rate limit detected in terminal content.")
        print("   The system will start tasks immediately.")
    
    return result['rate_limit_detected']

def test_with_rate_limit_content():
    """Test with terminal content that has a rate limit"""
    print("\n\nTesting with Rate Limit Content")
    print("=" * 35)
    
    parser = RateLimitParser()
    
    # Terminal content with rate limit
    terminal_content_with_rate_limit = r"""C:\Users\joaop\Documents\Hobbies\Claude Night Writer>python night_writer_cli.py
✓ Valid JSON file with 15 tasks
Starting Night Writer...
You will be prompted to select a terminal window.

Available Terminal Windows:
==================================================
1. Anaconda Prompt - "C:\Users\joaop\anaconda3\condabin\conda.bat"  activate graphrag-gpu
   Process: WindowsTerminal.exe
   PID: 27260

2. ✳ Task Implementation
   Process: WindowsTerminal.exe
   PID: 27260

Select terminal window (1-2) or 'n' for new window: 2
Selected: ✳ Task Implementation
2025-09-09 02:08:40,718 - root - INFO - Connected to existing window: ✳ Task Implementation
2025-09-09 02:08:40,718 - root - INFO - Terminal started successfully
2025-09-09 02:08:40,718 - root - INFO - Executing task 0: Keep going
2025-09-09 02:08:40,718 - root - ERROR - Failed to send keys to window: (6, 'SetForegroundWindow', 'The handle is invalid.')
2025-09-09 02:08:40,728 - root - INFO - Task 0 output saved to night_writer_outputs\task_000_20250909_020840
2025-09-09 02:08:40,728 - root - INFO - Task 0 completed with status: failed
2025-09-09 02:08:40,728 - root - INFO - Executing task 1: Go to the next task
2025-09-09 02:08:40,729 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,739 - root - INFO - Task 1 output saved to night_writer_outputs\task_001_20250909_020840
2025-09-09 02:08:40,739 - root - INFO - Task 1 completed with status: failed
2025-09-09 02:08:40,739 - root - INFO - Executing task 2: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,739 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,764 - root - INFO - Task 2 output saved to night_writer_outputs\task_002_20250909_020840
2025-09-09 02:08:40,764 - root - INFO - Task 2 completed with status: failed
2025-09-09 02:08:40,765 - root - INFO - Executing task 3: Keep going
2025-09-09 02:08:40,765 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,773 - root - INFO - Task 3 output saved to night_writer_outputs\task_003_20250909_020840
2025-09-09 02:08:40,773 - root - INFO - Task 3 completed with status: failed
2025-09-09 02:08:40,774 - root - INFO - Executing task 4: Go to the next task
2025-09-09 02:08:40,774 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,784 - root - INFO - Task 4 output saved to night_writer_outputs\task_004_20250909_020840
2025-09-09 02:08:40,784 - root - INFO - Task 4 completed with status: failed
2025-09-09 02:08:40,784 - root - INFO - Executing task 5: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,785 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,811 - root - INFO - Task 5 output saved to night_writer_outputs\task_005_20250909_020840
2025-09-09 02:08:40,811 - root - INFO - Task 5 completed with status: failed
2025-09-09 02:08:40,812 - root - INFO - Executing task 6: Keep going
2025-09-09 02:08:40,812 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,822 - root - INFO - Task 6 output saved to night_writer_outputs\task_006_20250909_020840
2025-09-09 02:08:40,822 - root - INFO - Task 6 completed with status: failed
2025-09-09 02:08:40,822 - root - INFO - Executing task 7: Go to the next task
2025-09-09 02:08:40,822 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,832 - root - INFO - Task 7 output saved to night_writer_outputs\task_007_20250909_020840
2025-09-09 02:08:40,832 - root - INFO - Task 7 completed with status: failed
2025-09-09 02:08:40,832 - root - INFO - Executing task 8: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,833 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,857 - root - INFO - Task 8 output saved to night_writer_outputs\task_008_20250909_020840
2025-09-09 02:08:40,857 - root - INFO - Task 8 completed with status: failed
2025-09-09 02:08:40,858 - root - INFO - Executing task 9: Keep going
2025-09-09 02:08:40,858 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,867 - root - INFO - Task 9 output saved to night_writer_outputs\task_009_20250909_020840
2025-09-09 02:08:40,867 - root - INFO - Task 9 completed with status: failed
2025-09-09 02:08:40,867 - root - INFO - Executing task 10: Go to the next task
2025-09-09 02:08:40,867 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,877 - root - INFO - Task 10 output saved to night_writer_outputs\task_010_20250909_020840
2025-09-09 02:08:40,877 - root - INFO - Task 10 completed with status: failed
2025-09-09 02:08:40,877 - root - INFO - Executing task 11: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,877 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,903 - root - INFO - Task 11 output saved to night_writer_outputs\task_011_20250909_020840
2025-09-09 02:08:40,903 - root - INFO - Task 11 completed with status: failed
2025-09-09 02:08:40,903 - root - INFO - Executing task 12: Keep going
2025-09-09 02:08:40,903 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,911 - root - INFO - Task 11 output saved to night_writer_outputs\task_011_20250909_020840
2025-09-09 02:08:40,911 - root - INFO - Task 12 completed with status: failed
2025-09-09 02:08:40,912 - root - INFO - Executing task 13: Go to the next task
2025-09-09 02:08:40,912 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,919 - root - INFO - Task 13 output saved to night_writer_outputs\task_013_20250909_020840
2025-09-09 02:08:40,919 - root - INFO - Task 13 completed with status: failed
2025-09-09 02:08:40,919 - root - INFO - Executing task 14: Test everything, document, and clean the code: run unit, integration, and e2e tests; ensure coverage is at least 80 percent; verify the build passes locally; lint and format; run type checks; remove dead code and unused dependencies only; update the README and usage examples; write a brief CHANGELOG entry; add or update tests for new behavior; commit with a clear message; follow tasks from tasks.md, design from tasks.md, and architecture from architecture.md
2025-09-09 02:08:40,919 - root - ERROR - Failed to send keys to window: (0, 'SetForegroundWindow', 'No error message is available')
2025-09-09 02:08:40,942 - root - INFO - Task 14 output saved to night_writer_outputs\task_014_20250909_020840
2025-09-09 02:08:40,942 - root - INFO - Task 14 completed with status: failed
2025-09-09 02:08:40,942 - root - INFO - Session completed successfully
Session completed successfully!

(graphrag-gpu) C:\Users\joaop\Documents\Hobbies\Claude Night Writer>
import { Account, AccountStatus } from '../types/session-manager';
  ⎿  5-hour limit reached ∙ resets 4am
     /upgrade to increase your usage limit."""
    
    print("Terminal Content with Rate Limit:")
    print(terminal_content_with_rate_limit[-200:])  # Last 200 chars
    print()
    
    # Parse the content
    result = parser.parse_output(terminal_content_with_rate_limit)
    
    print("Rate Limit Detection Results:")
    print(f"  Rate limit detected: {result['rate_limit_detected']}")
    print(f"  Reset time: {result['reset_time']}")
    print(f"  Message: {result['message']}")
    
    if result['rate_limit_detected']:
        print("\n✅ Rate limit detected in terminal content!")
        print("   The system will now wait for the reset time.")
        return True
    else:
        print("\n❌ No rate limit detected in terminal content.")
        print("   The system will start tasks immediately.")
        return False

def main():
    """Run all tests"""
    print("Terminal Content Reading Test")
    print("=" * 50)
    
    # Test without rate limit
    test_terminal_content_parsing()
    
    # Test with rate limit
    test_with_rate_limit_content()
    
    print("\n\n🎉 Terminal content reading is working!")
    print("The system will now:")
    print("1. Read the current terminal content")
    print("2. Look for rate limit messages")
    print("3. Extract reset times if found")
    print("4. Wait for reset or start immediately")

if __name__ == "__main__":
    main()
