"""
Test the final optimized workflow with existing Claude window
"""

from terminal_automation import TerminalWindowManager, TerminalAutomationSystem, Configuration
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_optimized_workflow():
    """Test the complete optimized workflow"""
    print("="*60)
    print("NIGHT WRITER - FINAL WORKFLOW TEST")
    print("="*60)
    
    try:
        # Step 1: Find terminal windows
        print("Step 1: Finding terminal windows...")
        wm = TerminalWindowManager()
        windows = wm.find_terminal_windows()
        print(f"Found {len(windows)} terminal windows")
        
        if not windows:
            print("No terminal windows found!")
            return
            
        # Step 2: Select first terminal (simulating GUI selection)
        selected_window = windows[0]
        try:
            print(f"Step 2: Selected window: {selected_window['title']}")
        except UnicodeEncodeError:
            print(f"Step 2: Selected window: [Unicode title] - {selected_window['process_name']}")
        
        # Step 3: Create optimized configuration
        print("Step 3: Creating configuration...")
        config = Configuration(
            tasks_file="tasks.txt",
            inactivity_timeout=600,
            auto_launch_claude=True
        )
        
        # Step 4: Create automation system
        print("Step 4: Creating automation system...")
        automation_system = TerminalAutomationSystem(config)
        
        # Step 5: Configure for existing window (KEY STEP)
        print("Step 5: Configuring for existing window...")
        automation_system.terminal_manager.selected_window = selected_window
        automation_system.terminal_manager._is_existing_window = True
        
        # Step 6: Load tasks
        print("Step 6: Loading tasks...")
        if automation_system.load_tasks(config.tasks_file):
            print(f"Loaded {len(automation_system.tasks)} tasks")
        else:
            print("Failed to load tasks")
            return
            
        # Step 7: Test the rate limit detection WITHOUT commands
        print("Step 7: Testing optimized rate limit detection...")
        print("This should NOT send any commands to the terminal!")
        
        # Start only the rate limit check to see if it sends commands
        automation_system._check_and_wait_for_rate_limits()
        
        print("Rate limit check completed")
        print("If you saw NO commands in your Claude terminal, the fix worked!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimized_workflow()