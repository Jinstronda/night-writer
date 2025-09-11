"""
Test the complete Night Writer workflow step by step
"""

from terminal_automation import TerminalWindowManager, TerminalAutomationSystem, Configuration

def test_window_detection():
    """Test 1: Window detection"""
    print("Testing window detection...")
    wm = TerminalWindowManager()
    windows = wm.find_terminal_windows()
    print(f"Found {len(windows)} terminal windows")
    for i, window in enumerate(windows, 1):
        try:
            print(f"   {i}. {window['title']} ({window['process_name']})")
        except UnicodeEncodeError:
            print(f"   {i}. [Unicode title] ({window['process_name']})")
    return windows

def test_configuration():
    """Test 2: Configuration creation"""
    print("\nTesting configuration...")
    config = Configuration(
        tasks_file="tasks.txt",
        inactivity_timeout=600,
        auto_launch_claude=True
    )
    print(f"Configuration created: tasks_file={config.tasks_file}")
    return config

def test_automation_system_creation(config):
    """Test 3: Automation system creation"""
    print("\nTesting automation system creation...")
    automation_system = TerminalAutomationSystem(config)
    print("Automation system created successfully")
    return automation_system

def test_manual_window_selection(automation_system, windows):
    """Test 4: Manual window selection (GUI simulation)"""
    print("\nTesting manual window selection...")
    if windows:
        # Simulate GUI selection of first terminal window
        selected_window = windows[0]
        automation_system.terminal_manager.selected_window = selected_window
        automation_system.terminal_manager._is_existing_window = True
        try:
            print(f"Manually selected window: {selected_window['title']}")
        except UnicodeEncodeError:
            print(f"Manually selected window: [Unicode title]")
        return selected_window
    else:
        print("No windows available for selection")
        return None

def test_task_loading(automation_system, config):
    """Test 5: Task loading"""
    print("\nTesting task loading...")
    try:
        success = automation_system.load_tasks(config.tasks_file)
        if success:
            print(f"Tasks loaded successfully from {config.tasks_file}")
            print(f"   Number of tasks: {len(automation_system.tasks)}")
            for i, task in enumerate(automation_system.tasks[:3], 1):  # Show first 3
                print(f"   {i}. {task.content[:50]}...")
        else:
            print(f"Failed to load tasks from {config.tasks_file}")
        return success
    except Exception as e:
        print(f"Error loading tasks: {e}")
        return False

def main():
    """Run all tests"""
    print("Night Writer Workflow Test")
    print("=" * 40)
    
    try:
        # Test each component
        windows = test_window_detection()
        config = test_configuration() 
        automation_system = test_automation_system_creation(config)
        selected_window = test_manual_window_selection(automation_system, windows)
        tasks_loaded = test_task_loading(automation_system, config)
        
        print("\nTest Results:")
        print("=" * 40)
        print(f"Window detection: {len(windows)} windows found")
        print(f"Configuration: Created successfully")
        print(f"Automation system: Created successfully")
        print(f"Window selection: {'Success' if selected_window else 'Failed'}")
        print(f"Task loading: {'Success' if tasks_loaded else 'Failed'}")
        
        if all([windows, selected_window, tasks_loaded]):
            print("\nALL TESTS PASSED! Workflow should work in GUI.")
        else:
            print("\nSome tests failed. Check the issues above.")
            
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()