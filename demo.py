"""
Night Writer Terminal Automation System - Demo Script

This script demonstrates the key features of the terminal automation system.

Author: João Panizzutti
"""

import json
import tempfile
from pathlib import Path
from terminal_automation import TerminalAutomationSystem, Configuration, TerminalType


def create_demo_tasks():
    """Create a demo tasks file"""
    demo_tasks = [
        "echo 'Starting Night Writer Demo'",
        "echo 'Task 1: System check'",
        "echo 'Task 2: Code review'",
        "echo 'Task 3: Testing'",
        "echo 'Demo completed successfully'"
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(demo_tasks, f, indent=2)
        return f.name


def run_demo():
    """Run a demonstration of the system"""
    print("Night Writer Terminal Automation System - Demo")
    print("=" * 50)
    
    # Create demo tasks
    tasks_file = create_demo_tasks()
    print(f"Created demo tasks file: {tasks_file}")
    
    # Create configuration
    config = Configuration()
    config.terminal_type = TerminalType.CMD
    config.max_tasks_per_session = 3
    config.inactivity_timeout = 5  # 5 seconds for demo
    config.tasks_file = tasks_file
    config.output_directory = "demo_outputs"
    
    print(f"Configuration:")
    print(f"  Terminal: {config.terminal_type.value}")
    print(f"  Max tasks: {config.max_tasks_per_session}")
    print(f"  Timeout: {config.inactivity_timeout}s")
    print(f"  Output dir: {config.output_directory}")
    print()
    
    # Create and run system
    system = TerminalAutomationSystem(config)
    
    if not system.load_tasks(tasks_file):
        print("Failed to load tasks")
        return False
    
    print(f"Loaded {len(system.tasks)} tasks")
    print("Tasks:")
    for i, task in enumerate(system.tasks, 1):
        print(f"  {i}. {task.content}")
    print()
    
    # Mock the scheduler to start immediately
    import unittest.mock
    with unittest.mock.patch.object(system.scheduler, 'wait_until_window'):
        print("Starting demo session...")
        result = system.run_session()
    
    if result:
        print("Demo session completed successfully!")
        
        # Show output files
        output_dir = Path(config.output_directory)
        if output_dir.exists():
            print(f"\nOutput files created in {output_dir}:")
            for file in output_dir.glob("*"):
                print(f"  - {file.name}")
    else:
        print("Demo session failed!")
    
    # Cleanup
    Path(tasks_file).unlink()
    return result


if __name__ == "__main__":
    success = run_demo()
    print(f"\nDemo {'completed successfully' if success else 'failed'}!")
