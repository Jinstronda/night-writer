"""
Terminal Automation System for Night Writer

This module provides a comprehensive terminal automation system that can:
1. Select and interact with different terminal types
2. Execute tasks from JSON with inactivity monitoring
3. Handle scheduling and rate limiting (5-hour windows, 4am resets)
4. Monitor CLI activity and detect completion

Author: João Panizzutti
"""

import os
import sys
import json
import time
import subprocess
import threading
import queue
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import signal
import psutil
import win32gui
import win32con
import win32api
import win32process


class TerminalType(Enum):
    """Supported terminal types"""
    CMD = "cmd"
    POWERSHELL = "powershell"
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"


class TerminalConnectionMode(Enum):
    """Terminal connection modes"""
    NEW_WINDOW = "new_window"
    EXISTING_WINDOW = "existing_window"
    AUTO_DETECT = "auto_detect"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """Represents a single task to execute"""
    id: int
    content: str
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: str = ""
    error: str = ""


@dataclass
class Configuration:
    """System configuration"""
    terminal_type: TerminalType = TerminalType.POWERSHELL
    connection_mode: TerminalConnectionMode = TerminalConnectionMode.AUTO_DETECT
    start_time: str = "04:00"
    timezone: str = "America/Sao_Paulo"
    inactivity_timeout: int = 600  # 10 minutes in seconds
    max_tasks_per_session: int = 10
    session_duration_hours: int = 5
    output_directory: str = "night_writer_outputs"
    log_level: str = "INFO"
    tasks_file: str = "tasks.txt"


class TerminalWindowManager:
    """Finds and controls existing terminal windows on Windows"""
    
    def __init__(self):
        self.terminal_windows = []
    
    def find_terminal_windows(self) -> List[Dict[str, Any]]:
        """Scans for all open terminal windows - the magic happens here"""
        windows = []
        
        def enum_windows_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # Check for common terminal window classes
                terminal_classes = [
                    "ConsoleWindowClass",  # Windows Console
                    "CASCADIA_HOSTING_WINDOW_CLASS",  # Windows Terminal
                    "Windows.UI.Core.CoreWindow",  # Windows Terminal (newer)
                    "Mintty",  # Git Bash
                    "PuTTY",  # PuTTY
                    "VTE",  # Some Linux terminals
                ]
                
                # Check for terminal-related window titles
                terminal_titles = [
                    "cmd", "Command Prompt", "PowerShell", "Windows PowerShell",
                    "Git Bash", "MINGW64", "Ubuntu", "WSL", "Terminal",
                    "Windows Terminal", "Alacritty", "Hyper"
                ]
                
                is_terminal = (
                    any(term_class in class_name for term_class in terminal_classes) or
                    any(term_title.lower() in window_text.lower() for term_title in terminal_titles)
                )
                
                if is_terminal and window_text.strip():
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        windows_list.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'class_name': class_name,
                            'pid': pid,
                            'process_name': process.name(),
                            'exe_path': process.exe()
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        
        win32gui.EnumWindows(enum_windows_callback, windows)
        self.terminal_windows = windows
        return windows
    
    def select_terminal_window(self) -> Optional[Dict[str, Any]]:
        """Shows you all your open terminals and lets you pick one"""
        windows = self.find_terminal_windows()
        
        if not windows:
            print("No terminal windows found.")
            return None
        
        print("\nAvailable Terminal Windows:")
        print("=" * 50)
        for i, window in enumerate(windows, 1):
            print(f"{i}. {window['title']}")
            print(f"   Process: {window['process_name']}")
            print(f"   PID: {window['pid']}")
            print()
        
        while True:
            try:
                choice = input(f"Select terminal window (1-{len(windows)}) or 'n' for new window: ").strip()
                
                if choice.lower() == 'n':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(windows):
                    return windows[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(windows)}")
            except ValueError:
                print("Please enter a valid number or 'n'")
            except KeyboardInterrupt:
                return None
    
    def send_keys_to_window(self, hwnd: int, text: str) -> bool:
        """Types text into a specific window - this is how it talks to your terminal"""
        try:
            # Activate the window
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)  # Small delay to ensure window is active
            
            # Send the text
            for char in text:
                win32api.keybd_event(ord(char.upper()), 0, 0, 0)  # Key down
                win32api.keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
                time.sleep(0.01)  # Small delay between characters
            
            # Send Enter
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            return True
        except Exception as e:
            logging.error(f"Failed to send keys to window: {e}")
            return False
    
    def is_window_active(self, hwnd: int) -> bool:
        """Check if a window is still active"""
        try:
            return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)
        except:
            return False


class InactivityMonitor:
    """Listens for silence - when your terminal stops talking, it knows you're done"""
    
    def __init__(self, timeout_seconds: int = 600):
        self.timeout_seconds = timeout_seconds
        self.last_activity = time.time()
        self.is_active = False
        self._lock = threading.Lock()
    
    def update_activity(self):
        """Update the last activity timestamp"""
        with self._lock:
            self.last_activity = time.time()
            self.is_active = True
    
    def is_inactive(self) -> bool:
        """Check if terminal has been inactive for the timeout period"""
        with self._lock:
            if not self.is_active:
                return False
            return (time.time() - self.last_activity) >= self.timeout_seconds
    
    def reset(self):
        """Reset the monitor"""
        with self._lock:
            self.last_activity = time.time()
            self.is_active = False


class TerminalManager:
    """Handles all the terminal stuff - finding, connecting, and talking to terminals"""
    
    def __init__(self, terminal_type: TerminalType, connection_mode: TerminalConnectionMode = TerminalConnectionMode.NEW_WINDOW):
        self.terminal_type = terminal_type
        self.connection_mode = connection_mode
        self.process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self._output_thread: Optional[threading.Thread] = None
        self._error_thread: Optional[threading.Thread] = None
        self._running = False
        self.window_manager = TerminalWindowManager()
        self.selected_window: Optional[Dict[str, Any]] = None
        self._is_existing_window = False
    
    def start_terminal(self) -> bool:
        """Start a terminal session (new or existing)"""
        try:
            # Handle existing window connection
            if self.connection_mode == TerminalConnectionMode.EXISTING_WINDOW:
                return self._connect_to_existing_window()
            elif self.connection_mode == TerminalConnectionMode.AUTO_DETECT:
                # Try to find existing windows first, fall back to new window
                if self._connect_to_existing_window():
                    return True
                # Fall through to create new window
            
            # Create new terminal window
            return self._create_new_terminal()
            
        except Exception as e:
            logging.error(f"Failed to start terminal: {e}")
            return False
    
    def _connect_to_existing_window(self) -> bool:
        """Connect to an existing terminal window"""
        if sys.platform != "win32":
            logging.warning("Existing window connection only supported on Windows")
            return False
        
        # Let user select a window
        self.selected_window = self.window_manager.select_terminal_window()
        
        if self.selected_window is None:
            logging.info("No existing window selected, will create new window")
            return False
        
        self._is_existing_window = True
        self._running = True
        
        logging.info(f"Connected to existing window: {self.selected_window['title']}")
        return True
    
    def _create_new_terminal(self) -> bool:
        """Create a new terminal window"""
        try:
            if self.terminal_type == TerminalType.CMD:
                self.process = subprocess.Popen(
                    ["cmd"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
            elif self.terminal_type == TerminalType.POWERSHELL:
                self.process = subprocess.Popen(
                    ["powershell", "-NoExit", "-Command", "-"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
            elif self.terminal_type in [TerminalType.BASH, TerminalType.ZSH, TerminalType.FISH]:
                shell_cmd = self.terminal_type.value
                self.process = subprocess.Popen(
                    [shell_cmd],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
            else:
                raise ValueError(f"Unsupported terminal type: {self.terminal_type}")
            
            self._is_existing_window = False
            self._running = True
            self._start_output_threads()
            logging.info("Created new terminal window")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create new terminal: {e}")
            return False
    
    def _start_output_threads(self):
        """Start threads to monitor terminal output"""
        def read_output():
            while self._running and self.process and self.process.poll() is None:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        self.output_queue.put(line.strip())
                except Exception as e:
                    logging.error(f"Error reading stdout: {e}")
                    break
        
        def read_error():
            while self._running and self.process and self.process.poll() is None:
                try:
                    line = self.process.stderr.readline()
                    if line:
                        self.error_queue.put(line.strip())
                except Exception as e:
                    logging.error(f"Error reading stderr: {e}")
                    break
        
        self._output_thread = threading.Thread(target=read_output, daemon=True)
        self._error_thread = threading.Thread(target=read_error, daemon=True)
        self._output_thread.start()
        self._error_thread.start()
    
    def send_command(self, command: str) -> bool:
        """Send a command to the terminal"""
        if self._is_existing_window:
            return self._send_command_to_existing_window(command)
        else:
            return self._send_command_to_new_window(command)
    
    def _send_command_to_existing_window(self, command: str) -> bool:
        """Send command to existing window"""
        if not self.selected_window:
            return False
        
        try:
            # Check if window is still active
            if not self.window_manager.is_window_active(self.selected_window['hwnd']):
                logging.error("Selected terminal window is no longer active")
                return False
            
            # Send the command
            success = self.window_manager.send_keys_to_window(
                self.selected_window['hwnd'], 
                command
            )
            
            if success:
                logging.info(f"Sent command to existing window: {command}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to send command to existing window: {e}")
            return False
    
    def _send_command_to_new_window(self, command: str) -> bool:
        """Send command to new window"""
        if not self.process or self.process.poll() is not None:
            return False
        
        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            return True
        except Exception as e:
            logging.error(f"Failed to send command: {e}")
            return False
    
    def get_output(self) -> List[str]:
        """Get all available output lines"""
        output_lines = []
        while not self.output_queue.empty():
            try:
                line = self.output_queue.get_nowait()
                output_lines.append(line)
            except queue.Empty:
                break
        return output_lines
    
    def get_errors(self) -> List[str]:
        """Get all available error lines"""
        error_lines = []
        while not self.error_queue.empty():
            try:
                line = self.error_queue.get_nowait()
                error_lines.append(line)
            except queue.Empty:
                break
        return error_lines
    
    def is_running(self) -> bool:
        """Check if terminal is still running"""
        if self._is_existing_window:
            return (self._running and 
                   self.selected_window and 
                   self.window_manager.is_window_active(self.selected_window['hwnd']))
        else:
            return self._running and self.process and self.process.poll() is None
    
    def stop_terminal(self):
        """Stop the terminal session"""
        self._running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logging.error(f"Error stopping terminal: {e}")
        
        if self._output_thread:
            self._output_thread.join(timeout=1)
        if self._error_thread:
            self._error_thread.join(timeout=1)


class TaskExecutor:
    """The worker that types your tasks and waits for them to finish"""
    
    def __init__(self, terminal_manager: TerminalManager, inactivity_monitor: InactivityMonitor):
        self.terminal_manager = terminal_manager
        self.inactivity_monitor = inactivity_monitor
        self.current_task: Optional[Task] = None
    
    def execute_task(self, task: Task) -> Task:
        """Execute a single task and monitor for completion"""
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        
        logging.info(f"Executing task {task.id}: {task.content}")
        
        # Send the task to the terminal
        if not self.terminal_manager.send_command(task.content):
            task.status = TaskStatus.FAILED
            task.error = "Failed to send command to terminal"
            return task
        
        # Monitor for completion
        start_time = time.time()
        output_lines = []
        error_lines = []
        
        while True:
            # Check if terminal is still running
            if not self.terminal_manager.is_running():
                task.status = TaskStatus.FAILED
                task.error = "Terminal process terminated unexpectedly"
                break
            
            # Collect output
            new_output = self.terminal_manager.get_output()
            new_errors = self.terminal_manager.get_errors()
            
            if new_output:
                output_lines.extend(new_output)
                self.inactivity_monitor.update_activity()
                logging.debug(f"Task {task.id} output: {new_output}")
            
            if new_errors:
                error_lines.extend(new_errors)
                self.inactivity_monitor.update_activity()
                logging.debug(f"Task {task.id} errors: {new_errors}")
            
            # Check for inactivity timeout
            if self.inactivity_monitor.is_inactive():
                task.status = TaskStatus.COMPLETED
                task.output = "\n".join(output_lines)
                if error_lines:
                    task.error = "\n".join(error_lines)
                logging.info(f"Task {task.id} completed due to inactivity timeout")
                break
            
            # Check for maximum execution time (safety timeout)
            if time.time() - start_time > 3600:  # 1 hour max per task
                task.status = TaskStatus.TIMEOUT
                task.output = "\n".join(output_lines)
                task.error = "Task exceeded maximum execution time"
                logging.warning(f"Task {task.id} timed out after 1 hour")
                break
            
            time.sleep(1)  # Check every second
        
        task.end_time = datetime.now()
        self.current_task = None
        return task


class Scheduler:
    """Keeps track of time and makes sure we don't hit the 5-hour limit"""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.tz = ZoneInfo(config.timezone)
        self.session_start_time: Optional[datetime] = None
        self.tasks_executed = 0
    
    def next_window_start(self) -> datetime:
        """Calculate the next execution window start time"""
        now = datetime.now(self.tz)
        hh, mm = [int(x) for x in self.config.start_time.split(":")]
        today_start = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        
        if now < today_start:
            return today_start
        return today_start + timedelta(days=1)
    
    def wait_until_window(self):
        """Wait until the next execution window starts"""
        window_start = self.next_window_start()
        logging.info(f"Waiting until next window starts at {window_start.isoformat()}")
        
        while True:
            now = datetime.now(self.tz)
            if now >= window_start:
                self.session_start_time = now
                self.tasks_executed = 0
                logging.info("Execution window started")
                return
            time.sleep(60)  # Check every minute
    
    def is_within_session_limit(self) -> bool:
        """Check if we're still within the session limits"""
        if not self.session_start_time:
            return False
        
        # Check time limit
        elapsed = datetime.now(self.tz) - self.session_start_time
        if elapsed.total_seconds() > (self.config.session_duration_hours * 3600):
            logging.info("Session time limit reached")
            return False
        
        # Check task limit
        if self.tasks_executed >= self.config.max_tasks_per_session:
            logging.info("Session task limit reached")
            return False
        
        return True
    
    def record_task_execution(self):
        """Record that a task was executed"""
        self.tasks_executed += 1


class TerminalAutomationSystem:
    """The main thing that ties everything together and makes it work"""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.terminal_manager = TerminalManager(config.terminal_type, config.connection_mode)
        self.inactivity_monitor = InactivityMonitor(config.inactivity_timeout)
        self.task_executor = TaskExecutor(self.terminal_manager, self.inactivity_monitor)
        self.scheduler = Scheduler(config)
        self.tasks: List[Task] = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('terminal_automation.log'),
                logging.StreamHandler()
            ]
        )
    
    def load_tasks(self, tasks_file: str) -> bool:
        """Load tasks from JSON file"""
        try:
            tasks_path = Path(tasks_file)
            if not tasks_path.exists():
                logging.error(f"Tasks file not found: {tasks_path}")
                return False
            
            content = tasks_path.read_text(encoding="utf-8").strip()
            if not content:
                logging.error("Tasks file is empty")
                return False
            
            # Parse JSON or plain text
            if content.lstrip().startswith("["):
                task_strings = json.loads(content)
            else:
                task_strings = [line.strip() for line in content.splitlines() if line.strip()]
            
            self.tasks = [
                Task(id=i, content=task_str) 
                for i, task_str in enumerate(task_strings)
            ]
            
            logging.info(f"Loaded {len(self.tasks)} tasks")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load tasks: {e}")
            return False
    
    def save_task_output(self, task: Task) -> str:
        """Save task output to file"""
        try:
            output_dir = Path(self.config.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = output_dir / f"task_{task.id:03d}_{timestamp}"
            
            # Save task content
            prompt_file = base_name.with_suffix(".prompt.txt")
            prompt_file.write_text(task.content, encoding="utf-8")
            
            # Save output
            output_file = base_name.with_suffix(".output.txt")
            output_file.write_text(task.output, encoding="utf-8")
            
            # Save errors if any
            if task.error:
                error_file = base_name.with_suffix(".error.txt")
                error_file.write_text(task.error, encoding="utf-8")
            
            # Save metadata
            metadata = {
                "task_id": task.id,
                "content": task.content,
                "status": task.status.value,
                "start_time": task.start_time.isoformat() if task.start_time else None,
                "end_time": task.end_time.isoformat() if task.end_time else None,
                "duration_seconds": (task.end_time - task.start_time).total_seconds() if task.start_time and task.end_time else None
            }
            metadata_file = base_name.with_suffix(".metadata.json")
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            
            return str(base_name)
            
        except Exception as e:
            logging.error(f"Failed to save task output: {e}")
            return ""
    
    def run_session(self) -> bool:
        """Run a complete automation session"""
        try:
            # Wait for execution window
            self.scheduler.wait_until_window()
            
            # Start terminal
            if not self.terminal_manager.start_terminal():
                logging.error("Failed to start terminal")
                return False
            
            logging.info("Terminal started successfully")
            
            # Execute tasks
            for task in self.tasks:
                if not self.scheduler.is_within_session_limit():
                    logging.info("Session limits reached, stopping execution")
                    break
                
                # Execute task
                completed_task = self.task_executor.execute_task(task)
                
                # Save output
                output_path = self.save_task_output(completed_task)
                if output_path:
                    logging.info(f"Task {completed_task.id} output saved to {output_path}")
                
                # Record execution
                self.scheduler.record_task_execution()
                
                # Reset inactivity monitor for next task
                self.inactivity_monitor.reset()
                
                logging.info(f"Task {completed_task.id} completed with status: {completed_task.status.value}")
            
            logging.info("Session completed successfully")
            return True
            
        except KeyboardInterrupt:
            logging.info("Session interrupted by user")
            return False
        except Exception as e:
            logging.error(f"Session failed: {e}")
            return False
        finally:
            self.terminal_manager.stop_terminal()
    
    def run_continuous(self):
        """Run continuously, waiting for next execution windows"""
        logging.info("Starting continuous automation mode")
        
        while True:
            try:
                self.run_session()
                logging.info("Waiting for next execution window...")
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logging.info("Automation stopped by user")
                break
            except Exception as e:
                logging.error(f"Continuous mode error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying


def main():
    """Main entry point"""
    # Default configuration
    config = Configuration()
    
    # Load configuration from command line or config file
    if len(sys.argv) > 1:
        config.tasks_file = sys.argv[1]
    if len(sys.argv) > 2:
        config.terminal_type = TerminalType(sys.argv[2])
    
    # Create and run automation system
    system = TerminalAutomationSystem(config)
    
    if not system.load_tasks(config.tasks_file):
        sys.exit(1)
    
    # Run in continuous mode
    system.run_continuous()


if __name__ == "__main__":
    main()
