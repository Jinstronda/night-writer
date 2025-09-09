"""
Night Writer CLI - Command Line Interface for Terminal Automation

This module provides a user-friendly CLI for configuring and running
the terminal automation system.

Author: João Panizzutti
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from terminal_automation import (
    TerminalAutomationSystem, Configuration, TerminalType, TerminalConnectionMode
)


class NightWriterCLI:
    """Command line interface for Night Writer automation"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description="Night Writer - Terminal Automation System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run with default settings (single session with manual terminal selection)
  python night_writer_cli.py

  # Run with custom tasks file and terminal
  python night_writer_cli.py --tasks my_tasks.json --terminal cmd

  # Run with custom schedule
  python night_writer_cli.py --start-time "22:00" --timezone "Europe/London"

  # Run with custom limits
  python night_writer_cli.py --max-tasks 5 --session-hours 3

  # Show configuration
  python night_writer_cli.py --show-config
            """
        )
        
        # Basic options
        parser.add_argument(
            "--tasks", "-t",
            default="tasks.txt",
            help="Path to tasks file (JSON or text) [default: tasks.txt]"
        )
        
        parser.add_argument(
            "--terminal", "-term",
            choices=[t.value for t in TerminalType],
            default="powershell",
            help="Terminal type to use [default: powershell]"
        )
        
        parser.add_argument(
            "--connection-mode", "-conn",
            choices=[m.value for m in TerminalConnectionMode],
            default="existing_window",
            help="Terminal connection mode: new_window, existing_window, auto_detect [default: existing_window]"
        )
        
        parser.add_argument(
            "--output-dir", "-o",
            default="night_writer_outputs",
            help="Output directory for task results [default: night_writer_outputs]"
        )
        
        # Scheduling options
        parser.add_argument(
            "--start-time",
            default="04:00",
            help="Start time for execution window (HH:MM) [default: 04:00]"
        )
        
        parser.add_argument(
            "--timezone",
            default="America/Sao_Paulo",
            help="Timezone for scheduling [default: America/Sao_Paulo]"
        )
        
        parser.add_argument(
            "--session-hours",
            type=int,
            default=5,
            help="Maximum session duration in hours [default: 5]"
        )
        
        # Task execution options
        parser.add_argument(
            "--max-tasks",
            type=int,
            default=10,
            help="Maximum tasks per session [default: 10]"
        )
        
        parser.add_argument(
            "--inactivity-timeout",
            type=int,
            default=600,
            help="Inactivity timeout in seconds [default: 600]"
        )
        
        # Operation modes (removed test-mode since single session is now default)
        
        parser.add_argument(
            "--show-config",
            action="store_true",
            help="Show current configuration and exit"
        )
        
        parser.add_argument(
            "--validate-tasks",
            action="store_true",
            help="Validate tasks file and exit"
        )
        
        # Logging options
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Logging level [default: INFO]"
        )
        
        parser.add_argument(
            "--log-file",
            help="Log file path [default: terminal_automation.log]"
        )
        
        return parser
    
    def _create_config(self, args) -> Configuration:
        """Create configuration from command line arguments"""
        config = Configuration()
        
        config.terminal_type = TerminalType(args.terminal)
        config.connection_mode = TerminalConnectionMode(args.connection_mode)
        config.start_time = args.start_time
        config.timezone = args.timezone
        config.inactivity_timeout = args.inactivity_timeout
        config.max_tasks_per_session = args.max_tasks
        config.session_duration_hours = args.session_hours
        config.output_directory = args.output_dir
        config.log_level = args.log_level
        config.tasks_file = args.tasks
        
        return config
    
    def _show_config(self, config: Configuration):
        """Display current configuration"""
        print("Night Writer Configuration:")
        print("=" * 40)
        print(f"Tasks File: {config.tasks_file}")
        print(f"Terminal Type: {config.terminal_type.value}")
        print(f"Connection Mode: {config.connection_mode.value}")
        print(f"Start Time: {config.start_time}")
        print(f"Timezone: {config.timezone}")
        print(f"Session Duration: {config.session_duration_hours} hours")
        print(f"Max Tasks per Session: {config.max_tasks_per_session}")
        print(f"Inactivity Timeout: {config.inactivity_timeout} seconds")
        print(f"Output Directory: {config.output_directory}")
        print(f"Log Level: {config.log_level}")
        print("=" * 40)
    
    def _validate_tasks(self, tasks_file: str) -> bool:
        """Validate tasks file"""
        try:
            tasks_path = Path(tasks_file)
            if not tasks_path.exists():
                print(f"Error: Tasks file not found: {tasks_path}")
                return False
            
            content = tasks_path.read_text(encoding="utf-8").strip()
            if not content:
                print("Error: Tasks file is empty")
                return False
            
            # Try to parse as JSON
            if content.lstrip().startswith("["):
                try:
                    tasks = json.loads(content)
                    if not isinstance(tasks, list):
                        print("Error: JSON tasks must be a list")
                        return False
                    if not all(isinstance(task, str) for task in tasks):
                        print("Error: All tasks must be strings")
                        return False
                    print(f"✓ Valid JSON file with {len(tasks)} tasks")
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON format: {e}")
                    return False
            else:
                # Parse as text file
                tasks = [line.strip() for line in content.splitlines() if line.strip()]
                print(f"✓ Valid text file with {len(tasks)} tasks")
            
            # Show first few tasks as preview
            print("\nTask Preview:")
            for i, task in enumerate(tasks[:3]):
                print(f"  {i+1}. {task}")
            if len(tasks) > 3:
                print(f"  ... and {len(tasks) - 3} more tasks")
            
            return True
            
        except Exception as e:
            print(f"Error validating tasks file: {e}")
            return False
    
    
    def _run_single_session(self, config: Configuration) -> bool:
        """Run a single session with manual terminal selection"""
        print("Starting Night Writer...")
        print("You will be prompted to select a terminal window.")
        print()
        
        system = TerminalAutomationSystem(config)
        
        if not system.load_tasks(config.tasks_file):
            print("Failed to load tasks")
            return False
        
        print(f"Loaded {len(system.tasks)} tasks")
        print("Starting session...")
        
        # Run the session (session start time is set automatically)
        result = system.run_session()
        
        if result:
            print("Session completed successfully!")
        else:
            print("Session failed!")
        
        return result
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI"""
        try:
            parsed_args = self.parser.parse_args(args)
            config = self._create_config(parsed_args)
            
            # Handle special modes
            if parsed_args.show_config:
                self._show_config(config)
                return 0
            
            if parsed_args.validate_tasks:
                if self._validate_tasks(config.tasks_file):
                    return 0
                else:
                    return 1
            
            # Validate tasks file before running
            if not self._validate_tasks(config.tasks_file):
                print("Tasks file validation failed")
                return 1
            
            # Always run in single session mode with manual terminal selection
            success = self._run_single_session(config)
            
            return 0 if success else 1
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main():
    """Main entry point"""
    cli = NightWriterCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
