"""
🌙 NIGHT WRITER - Terminal Automation System for Claude Code

This module provides a comprehensive automation system that intelligently manages
Claude Code sessions, executing tasks from JSON files while handling rate limits.

🎯 WHAT IT DOES:
The system connects to your terminal (existing or new), sends tasks to Claude Code,
monitors for completion, and automatically handles rate limits by waiting for resets.

🏗️ SYSTEM ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────────────────┐
│                        NIGHT WRITER ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ 📋 JSON Tasks   │───▶│ 🧠 Main System  │───▶│ 🖥️ Terminal     │         │
│  │ (User Input)    │    │ (Orchestrator)  │    │ Manager         │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                  │                       │                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ ⏰ Scheduler     │◀───│ 🔍 Rate Limit   │◀───│ 📋 Clipboard    │         │
│  │ (Timing Logic)  │    │ Parser          │    │ Reader          │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                  │                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ 👀 Inactivity   │◀───│ 🚀 Task         │───▶│ 📝 Claude Code  │         │
│  │ Monitor         │    │ Executor        │    │ (Target)        │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

🔄 MAIN WORKFLOW:
1. 📚 Load tasks from JSON file (tasks.txt)
2. 🔌 Connect to terminal (existing Claude session or create new)
3. 🔍 Check current rate limit status via clipboard/transcript
4. 🚀 Send task to Claude and wait for it to start working
5. 👀 Monitor for inactivity (10min silence = task complete)
6. 🚫 If rate limited, parse reset time and wait automatically
7. 🔄 Continue with next task until all are complete

🎯 KEY FEATURES:
• Smart Rate Limit Detection: Finds "5-hour limit reached ∙ resets 7pm" messages
• Clipboard Reading: Captures exactly what you see on terminal screen
• Intelligent Scheduling: Waits for rate resets, never stops permanently
• Multi-Terminal Support: PowerShell, CMD, existing/new windows
• Comprehensive Logging: Detailed logs with emojis for easy monitoring
• Robust Error Handling: Gracefully handles window closures, network issues

🛠️ TECHNICAL DETAILS:
• Uses Windows API (pywin32) for window management and clipboard access
• Regex patterns for rate limit message detection
• Threading for concurrent output monitoring and inactivity detection
• Configurable timeouts, schedules, and terminal preferences
• JSON-based task management with status tracking

Author: João Panizzutti
Built for the Claude Code automation community 🚀
"""

import os
import sys
import json
import time
import subprocess
import threading
import queue
import logging
import re
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
import win32clipboard
from PIL import ImageGrab
import pygetwindow as gw

# Optional OCR import - only used as fallback
try:
    import easyocr
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
import pyautogui


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
    RATE_LIMITED = "rate_limited"


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
    # Transcript-based capture (PowerShell only)
    transcript_enabled: bool = True
    transcript_path: Optional[str] = None  # Defaults to ~/Documents/session.log when None
    auto_launch_claude: bool = True
    claude_command: str = "claude --dangerously-skip-permissions"
    gui_mode: bool = False  # If True, creates hidden terminals for GUI-only operation


class RateLimitParser:
    """Parses terminal output to detect rate limit messages and reset times"""
    
    def __init__(self):
        # Patterns to detect rate limit messages - focusing on the specific format
        self.rate_limit_patterns = [
            r"5-hour limit reached.*resets",
            r"5-hour limit reached.*∙.*resets",
            r"rate limit reached.*resets",
            r"limit reached.*resets",
            r"quota exceeded.*resets",
            r"usage limit.*resets",
            r"daily limit.*resets",
            r"hourly limit.*resets",
            r"you've reached.*limit.*resets",
            r"limit.*exceeded.*resets",
            r"too many requests.*resets"
        ]
        
        # Patterns to extract reset times from the specific format
        self.reset_time_patterns = [
            r"5-hour limit reached.*∙.*resets\s+(\d{1,2}am|\d{1,2}pm)",
            r"resets?\s+(\d{1,2}am|\d{1,2}pm)",
            r"resets?\s+(\d{1,2}:\d{2})\s*(am|pm)?",
            r"resets?\s+at\s+(\d{1,2}:\d{2})\s*(am|pm)?",
            r"next\s+reset\s+(\d{1,2}:\d{2})\s*(am|pm)?",
            r"available\s+at\s+(\d{1,2}:\d{2})\s*(am|pm)?"
        ]
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """Parse terminal output for rate limit information"""
        result = {
            'rate_limit_detected': False,
            'reset_time': None,
            'message': None,
            'matched_pattern': None
        }
        
        output_lower = output.lower()
        
        # Check for rate limit messages
        for pattern in self.rate_limit_patterns:
            match = re.search(pattern, output_lower)
            if match:
                result['rate_limit_detected'] = True
                result['message'] = output.strip()
                result['matched_pattern'] = pattern
                
                # Log the match for debugging
                logging.info(f"🎯 Rate limit pattern matched: '{pattern}'")
                logging.info(f"📄 Matched text: '{match.group(0)}'")
                break
        
        # Extract reset time if rate limit detected
        if result['rate_limit_detected']:
            reset_time = self._extract_reset_time(output)
            if reset_time:
                # Validate if this is a current or old rate limit message
                is_current = self._is_rate_limit_current(reset_time)
                result['reset_time'] = reset_time
                result['is_current'] = is_current
                
                if is_current:
                    logging.info(f"⏰ Successfully extracted CURRENT reset time: {reset_time}")
                else:
                    logging.warning(f"🕐 EXPIRED rate limit detected - reset time {reset_time} already passed")
                    logging.warning("🚫 This appears to be an OLD rate limit message in terminal history")
                    result['rate_limit_detected'] = False  # Treat as no rate limit
            else:
                logging.warning(f"⚠️ Failed to extract reset time from: '{output.strip()}'")
        
        return result
    
    def _extract_reset_time(self, output: str) -> Optional[str]:
        """Extract reset time from terminal output"""
        for pattern in self.reset_time_patterns:
            match = re.search(pattern, output.lower())
            if match:
                time_str = match.group(1)
                
                # Handle formats like "4am" or "4pm"
                if 'am' in time_str or 'pm' in time_str:
                    return time_str
                
                # Handle formats like "4:00" with separate AM/PM
                am_pm = match.group(2) if len(match.groups()) > 1 else None
                
                # Format the time
                if ':' in time_str:
                    hour, minute = time_str.split(':')
                else:
                    hour = time_str
                    minute = "00"
                
                # Add AM/PM if not specified
                if not am_pm:
                    hour_int = int(hour)
                    if hour_int < 12:
                        am_pm = "am"
                    else:
                        am_pm = "pm"
                        if hour_int > 12:
                            hour = str(hour_int - 12)
                
                return f"{hour}:{minute} {am_pm}"
        
        return None
    
    def _is_rate_limit_current(self, reset_time_str: str) -> bool:
        """
        Determine if a rate limit reset time is current (future) or expired (past)
        
        Logic:
        - If reset time is in the future (today), it's current
        - If reset time was earlier today and we're past it, it's expired
        - If reset time appears to be yesterday/past, it's expired
        
        Examples at 2:43 PM:
        - "7pm" -> current (future today)
        - "5am" -> expired (was 9+ hours ago)
        - "4am" -> expired (was 10+ hours ago)
        """
        from datetime import datetime, time
        import pytz
        
        try:
            # Parse the reset time
            reset_time_str = reset_time_str.lower().strip()
            
            # Extract hour and am/pm
            if 'am' in reset_time_str:
                hour_str = reset_time_str.replace('am', '').strip().split(':')[0]
                is_pm = False
            elif 'pm' in reset_time_str:
                hour_str = reset_time_str.replace('pm', '').strip().split(':')[0]
                is_pm = True
            else:
                logging.warning(f"Unknown time format: {reset_time_str}")
                return True  # Assume current if we can't parse
            
            # Parse hour
            try:
                hour = int(hour_str)
            except ValueError:
                logging.warning(f"Could not parse hour from: {hour_str}")
                return True  # Assume current if we can't parse
            
            # Convert to 24-hour format
            if is_pm and hour != 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
            
            # Get current time in Eastern timezone (Claude's timezone)
            eastern = pytz.timezone('America/New_York')
            now = datetime.now(eastern)
            current_hour = now.hour
            
            logging.info(f"🕐 Time analysis: Reset={hour:02d}:00, Current={current_hour:02d}:{now.minute:02d}")
            
            # If reset hour is in the future today, it's current
            if hour > current_hour:
                logging.info(f"✅ Reset time {reset_time_str} is FUTURE (current rate limit)")
                return True
            
            # If reset hour is same as current hour, check minutes for safety
            if hour == current_hour:
                logging.info(f"⚠️ Reset time {reset_time_str} is CURRENT HOUR - treating as current")
                return True
            
            # If reset hour is in the past today, it's expired
            logging.info(f"🕐 Reset time {reset_time_str} was {current_hour - hour} hours ago (EXPIRED)")
            return False
            
        except Exception as e:
            logging.warning(f"Error parsing reset time '{reset_time_str}': {e}")
            return True  # Assume current if parsing fails


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
                    "Windows Terminal", "Alacritty", "Hyper", "Anaconda Prompt",
                    "conda", "python", "node", "npm", "yarn"
                ]
                
                # Exclude non-terminal windows
                exclude_titles = [
                    "Settings", "Settings", "Control Panel", "File Explorer",
                    "Microsoft Edge", "Chrome", "Firefox", "Notepad",
                    "Calculator", "Task Manager", "Device Manager"
                ]
                
                # Check if it's a terminal window
                is_terminal = (
                    any(term_class in class_name for term_class in terminal_classes) or
                    any(term_title.lower() in window_text.lower() for term_title in terminal_titles)
                )
                
                # Exclude non-terminal windows
                is_excluded = any(exclude_title.lower() in window_text.lower() for exclude_title in exclude_titles)
                
                if is_terminal and not is_excluded and window_text.strip():
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

    def find_window_by_pid(self, pid: int) -> Optional[Dict[str, Any]]:
        """Find a terminal window record by owning process PID."""
        windows = self.find_terminal_windows()
        for w in windows:
            if w.get('pid') == pid:
                return w
        return None
    
    def select_terminal_window(self, auto_select: bool = True) -> Optional[Dict[str, Any]]:
        """Automatically selects the first available terminal window"""
        windows = self.find_terminal_windows()
        
        if not windows:
            print("No terminal windows found.")
            return None
        
        if auto_select:
            # Automatically select the first terminal window
            selected = windows[0]
            print(f"Auto-selected terminal: {selected['title']}")
            return selected
        
        # Manual selection (for debugging)
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
                    selected = windows[choice_num - 1]
                    print(f"Selected: {selected['title']}")
                    return selected
                else:
                    print(f"Please enter a number between 1 and {len(windows)}")
            except ValueError:
                print("Please enter a valid number or 'n'")
            except KeyboardInterrupt:
                print("\nSelection cancelled")
                return None
    
    def send_keys_to_window(self, hwnd: int, text: str) -> bool:
        """Types text into a specific window - this is how it talks to your terminal"""
        try:
            # Check if window is still valid
            if not win32gui.IsWindow(hwnd):
                logging.error("Window handle is no longer valid")
                return False
            
            # Check if window is visible
            if not win32gui.IsWindowVisible(hwnd):
                logging.error("Window is not visible")
                return False
            
            # Try to restore and set foreground robustly with thread input attachment
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
                target_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
                current_tid = win32api.GetCurrentThreadId()
                win32process.AttachThreadInput(current_tid, target_tid, True)
                try:
                    win32gui.SetForegroundWindow(hwnd)
                finally:
                    win32process.AttachThreadInput(current_tid, target_tid, False)
                time.sleep(0.3)
            except Exception as e:
                logging.warning(f"Foreground activation via thread attach failed: {e}")
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.3)
                except Exception as e2:
                    logging.error(f"SetForegroundWindow failed: {e2}")
                    return False

            # Place text on clipboard
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                win32clipboard.CloseClipboard()
            except Exception as e:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
                logging.error(f"Failed to set clipboard text: {e}")
                return False

            # Paste (Ctrl+V) and press Enter, with small retries
            def key_down(vk):
                win32api.keybd_event(vk, 0, 0, 0)
            def key_up(vk):
                win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)

            attempts = 0
            while attempts < 3:
                attempts += 1
                try:
                    # Ctrl+V
                    key_down(win32con.VK_CONTROL)
                    key_down(ord('V'))
                    time.sleep(0.02)
                    key_up(ord('V'))
                    key_up(win32con.VK_CONTROL)
                    time.sleep(0.1)
                    # Enter
                    key_down(win32con.VK_RETURN)
                    key_up(win32con.VK_RETURN)
                    return True
                except Exception as e:
                    logging.warning(f"Paste attempt {attempts} failed: {e}")
                    time.sleep(0.2)

            logging.error("Failed to paste and submit text after retries")
            return False
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
        self.initial_working_dir: Optional[str] = None
    
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
        
        # Check if window already selected from GUI, otherwise show selection menu
        if not self.selected_window:
            self.selected_window = self.window_manager.select_terminal_window(auto_select=False)
        
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
            # Build transcript-aware startup for PowerShell
            def build_powershell_startup() -> List[str]:
                ps = ["powershell", "-NoExit", "-Command"]
                transcript_path = self._resolve_transcript_path()
                pre = []
                # Always start transcript and Claude for new sessions
                if transcript_path:
                    pre.append(f"Start-Transcript -Path '{transcript_path}' -Append;")
                # Force Claude start; if already running, this just ensures session is ready
                pre.append(self._get_config().claude_command + ";")
                # Small delay and echo to mark ready
                pre.append("Start-Sleep -Seconds 1; Write-Host '[Claude started]' ;")
                pre.append("Write-Host 'Night Writer ready.'")
                command = " ".join(pre)
                return ps + [command]

            # Decide stdio redirection and console visibility
            config = self._get_config()
            gui_mode = getattr(config, 'gui_mode', False)
            
            # For GUI mode: always capture output and hide console
            # For regular NEW_WINDOW: show visible console, don't capture
            if gui_mode:
                capture_output = True
                show_console = False
            else:
                capture_output = (self.connection_mode != TerminalConnectionMode.NEW_WINDOW)
                show_console = True

            if self.terminal_type == TerminalType.CMD:
                self.process = subprocess.Popen(
                    ["cmd"],
                    stdin=subprocess.PIPE,
                    stdout=(subprocess.PIPE if capture_output else None),
                    stderr=(subprocess.PIPE if capture_output else None),
                    text=True,
                    bufsize=0,
                    cwd=self.initial_working_dir or None,
                    creationflags=(getattr(subprocess, "CREATE_NEW_CONSOLE", 0) if show_console else 0)
                )
                # Attach window info for clipboard and focus
                try:
                    time.sleep(0.6)
                    win = self.window_manager.find_window_by_pid(self.process.pid)
                    if win:
                        self.selected_window = win
                        try:
                            win32gui.ShowWindow(win['hwnd'], win32con.SW_RESTORE)
                            win32gui.BringWindowToTop(win['hwnd'])
                            win32gui.SetForegroundWindow(win['hwnd'])
                        except Exception:
                            pass
                except Exception:
                    pass
            elif self.terminal_type == TerminalType.POWERSHELL:
                self.process = subprocess.Popen(
                    build_powershell_startup(),
                    stdin=subprocess.PIPE,
                    stdout=(subprocess.PIPE if capture_output else None),
                    stderr=(subprocess.PIPE if capture_output else None),
                    text=True,
                    bufsize=0,
                    cwd=self.initial_working_dir or None,
                    creationflags=(getattr(subprocess, "CREATE_NEW_CONSOLE", 0) if show_console else 0)
                )
                # Try to bring the created window to foreground if possible
                try:
                    time.sleep(0.6)
                    win = self.window_manager.find_window_by_pid(self.process.pid)
                    if win:
                        self.selected_window = win
                        try:
                            win32gui.ShowWindow(win['hwnd'], win32con.SW_RESTORE)
                            win32gui.BringWindowToTop(win['hwnd'])
                            win32gui.SetForegroundWindow(win['hwnd'])
                        except Exception:
                            pass
                except Exception:
                    pass
            elif self.terminal_type in [TerminalType.BASH, TerminalType.ZSH, TerminalType.FISH]:
                shell_cmd = self.terminal_type.value
                self.process = subprocess.Popen(
                    [shell_cmd],
                    stdin=subprocess.PIPE,
                    stdout=(subprocess.PIPE if capture_output else None),
                    stderr=(subprocess.PIPE if capture_output else None),
                    text=True,
                    bufsize=0,
                    cwd=self.initial_working_dir or None,
                    creationflags=(getattr(subprocess, "CREATE_NEW_CONSOLE", 0) if show_console else 0)
                )
                # Attach window info and focus
                try:
                    time.sleep(0.6)
                    win = self.window_manager.find_window_by_pid(self.process.pid)
                    if win:
                        self.selected_window = win
                        try:
                            win32gui.ShowWindow(win['hwnd'], win32con.SW_RESTORE)
                            win32gui.BringWindowToTop(win['hwnd'])
                            win32gui.SetForegroundWindow(win['hwnd'])
                        except Exception:
                            pass
                except Exception:
                    pass
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

    def _resolve_transcript_path(self) -> Optional[str]:
        try:
            # Access config from parent via weak reference (simple accessor)
            cfg = self._get_config()
            if not cfg:
                return None
            if cfg.transcript_path:
                p = Path(os.path.expandvars(os.path.expanduser(cfg.transcript_path)))
            else:
                docs = Path(os.path.expanduser("~")) / "Documents"
                p = docs / "session.log"
            p.parent.mkdir(parents=True, exist_ok=True)
            return str(p)
        except Exception:
            return None

    def _get_config(self) -> Optional[Configuration]:
        # Walk up to TerminalAutomationSystem to fetch config
        try:
            # TerminalManager is owned by TerminalAutomationSystem → access via attribute search
            # This is a small hack; in larger refactor pass config in constructor
            import gc
            for obj in gc.get_objects():
                try:
                    if isinstance(obj, TerminalAutomationSystem) and obj.terminal_manager is self:
                        return obj.config
                except Exception:
                    continue
        except Exception:
            pass
        return None
    
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
            # Ensure window is ready; re-prompt if needed
            if not self.ensure_window_ready():
                logging.error("No valid terminal window available to send command")
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

    def ensure_window_ready(self) -> bool:
        """Ensure we have a valid, active window; re-prompt if the previous one died."""
        if not self._is_existing_window:
            return True
        
        # If we have a selected window and it's active, we're good
        if self.selected_window and self.window_manager.is_window_active(self.selected_window['hwnd']):
            return True
        
        logging.info("Previously selected window is not available anymore. Please select a terminal again.")
        # Re-prompt user to select a window
        self.selected_window = self.window_manager.select_terminal_window(auto_select=False)
        if not self.selected_window:
            logging.error("User did not select a replacement terminal window")
            return False
        
        # Double-check new selection
        if not self.window_manager.is_window_active(self.selected_window['hwnd']):
            logging.error("Replacement terminal window is not active")
            return False
        
        logging.info(f"Reconnected to terminal window: {self.selected_window['title']}")
        return True
    
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
    
    def __init__(self, terminal_manager: TerminalManager, inactivity_monitor: InactivityMonitor, automation_system=None):
        self.terminal_manager = terminal_manager
        self.inactivity_monitor = inactivity_monitor
        self.automation_system = automation_system  # Reference to main system for rate limit checks
        self.current_task: Optional[Task] = None
        self.rate_limit_parser = RateLimitParser()
        self.rate_limit_detected = False
        self.detected_reset_time: Optional[str] = None
    
    def execute_task(self, task: Task) -> Task:
        """🚀 EXECUTE TASK - Send task to Claude and monitor for completion
        
        This method is the core task executor that:
        1. 📤 Sends the task command to the terminal
        2. ⏳ Waits for Claude to start working (detects activity)
        3. 👀 Monitors for inactivity (task completion signal)
        4. 🚫 Detects rate limits during execution
        5. ✅ Returns task with updated status and timing info
        """
        logging.info("="*60)
        logging.info(f"🚀 STARTING TASK EXECUTION")
        logging.info("="*60)
        
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        
        logging.info(f"📋 Task Details:")
        logging.info(f"   • ID: {task.id}")
        logging.info(f"   • Content: {task.content}")
        logging.info(f"   • Start Time: {task.start_time}")
        logging.info(f"   • Status: {task.status.value}")
        
        # Capture initial terminal content before sending command (for existing windows)
        initial_content = ""
        if self.terminal_manager._is_existing_window:
            try:
                # Get baseline content before sending command
                initial_content = self.automation_system._try_clipboard_copy_method() or ""
                logging.info(f"Captured initial terminal content: {len(initial_content)} characters")
            except Exception as e:
                logging.warning(f"Could not capture initial content: {e}")
        
        # Send the task to the terminal
        if not self.terminal_manager.send_command(task.content):
            task.status = TaskStatus.FAILED
            task.error = "Failed to send command to terminal"
            return task
        
        # Log that task was sent successfully
        logging.info(f"✅ Task {task.id} sent to terminal: {task.content}")
        
        # Notify progress callback that task started
        if self.automation_system and self.automation_system.progress_callback:
            self.automation_system.progress_callback("task_start", task.content, {
                "task_index": task.id, 
                "task_text": task.content
            })
        
        # Wait for Claude to start working by detecting terminal content changes
        logging.info("Waiting for Claude to start working (monitoring for terminal changes)...")
        claude_started = False
        start_time = time.time()
        last_rate_limit_check = time.time()
        output_lines = []
        error_lines = []
        
        while True:
            # Check if terminal is still running
            if not self.terminal_manager.is_running():
                task.status = TaskStatus.FAILED
                task.error = "Terminal process terminated unexpectedly"
                break
            
            # For existing windows, check if terminal content has changed
            if self.terminal_manager._is_existing_window:
                try:
                    current_content = self.automation_system._try_clipboard_copy_method() or ""
                    
                    # If not started yet, check if Claude started working
                    if not claude_started:
                        # If content changed from initial state
                        if current_content != initial_content and len(current_content) > len(initial_content):
                            # Check if it's a rate limit change
                            rate_limit_info = self.rate_limit_parser.parse_output(current_content)
                            
                            if not rate_limit_info['rate_limit_detected']:
                                # Content changed and it's NOT a rate limit = Claude is working!
                                claude_started = True
                                logging.info(f"✅ Terminal content changed ({len(current_content)} chars, was {len(initial_content)}) - Claude is working!")
                                self.inactivity_monitor.reset()
                                self.inactivity_monitor.update_activity()
                                logging.info(f"🕐 Starting inactivity monitoring - timeout: {self.inactivity_monitor.timeout_seconds} seconds")
                                # Store current content as baseline for future change detection
                                self.last_content = current_content
                            else:
                                logging.info("Terminal changed but detected rate limit - not starting monitoring yet")
                    else:
                        # Claude already started - check for NEW content changes to update activity
                        if hasattr(self, 'last_content') and current_content != self.last_content:
                            if len(current_content) != len(self.last_content):
                                # Content changed = Claude is still active
                                logging.info(f"📝 Terminal content updated ({len(current_content)} chars, was {len(self.last_content)}) - Claude still working, resetting inactivity timer")
                                self.inactivity_monitor.update_activity()
                                self.last_content = current_content
                                # Reset 2-minute check timer
                                self.last_2min_check = time.time()
                        elif not hasattr(self, 'last_content'):
                            # Initialize last_content if not set
                            self.last_content = current_content
                            # Initialize 2-minute check timer
                            self.last_2min_check = time.time()
                            
                except Exception as e:
                    logging.debug(f"Error checking terminal content change: {e}")
            
            # Collect output from new windows
            new_output = self.terminal_manager.get_output()
            new_errors = self.terminal_manager.get_errors()
            
            if new_output:
                output_lines.extend(new_output)
                logging.debug(f"Task {task.id} output: {new_output}")
                
                # For new windows, check if Claude has started working (look for typical Claude output patterns)
                if not self.terminal_manager._is_existing_window and not claude_started:
                    full_output = "\n".join(output_lines).lower()
                    claude_working_indicators = [
                        "thinking", "analyzing", "processing", "generating", "writing",
                        "creating", "building", "implementing", "coding", "working"
                    ]
                    
                    if any(indicator in full_output for indicator in claude_working_indicators):
                        claude_started = True
                        logging.info("Claude has started working - beginning inactivity monitoring")
                        self.inactivity_monitor.reset()  # Reset inactivity monitor now
                
                # Check for rate limit messages in the output
                full_output = "\n".join(output_lines)
                rate_limit_info = self.rate_limit_parser.parse_output(full_output)
                if rate_limit_info['rate_limit_detected']:
                    self.rate_limit_detected = True
                    self.detected_reset_time = rate_limit_info['reset_time']
                    task.status = TaskStatus.RATE_LIMITED
                    task.output = "\n".join(output_lines)
                    logging.info(f"Rate limit detected: {rate_limit_info['message']}")
                    if rate_limit_info['reset_time']:
                        logging.info(f"Reset time detected: {rate_limit_info['reset_time']}")
                    logging.info(f"Task {task.id} marked as RATE_LIMITED - will retry after reset")
                    break
                
                # Update inactivity monitor only after Claude starts working
                if claude_started:
                    self.inactivity_monitor.update_activity()
            
            if new_errors:
                error_lines.extend(new_errors)
                logging.debug(f"Task {task.id} errors: {new_errors}")
                if claude_started:
                    self.inactivity_monitor.update_activity()
            
            # For existing windows, periodically check for rate limits ONLY when Claude is inactive
            # Don't interrupt Claude while it's actively working!
            if (self.terminal_manager._is_existing_window and 
                claude_started and  # Only check after Claude starts
                self.inactivity_monitor.is_inactive() and  # Only when Claude is inactive
                time.time() - last_rate_limit_check > 60):  # Check every minute during inactivity
                last_rate_limit_check = time.time()
                logging.debug("Claude appears inactive - checking for rate limits...")
                
                # Use the new rate limit checking method from the main automation system
                if self.automation_system and self.automation_system._check_rate_limit_during_task():
                    task.status = TaskStatus.RATE_LIMITED
                    task.output = "\n".join(output_lines)
                    logging.info("Rate limit detected during task execution - marking task as RATE_LIMITED")
                    break
            
            # Check for inactivity timeout only after Claude starts working
            if claude_started:
                is_inactive = self.inactivity_monitor.is_inactive()
                time_since_activity = time.time() - self.inactivity_monitor.last_activity
                
                # Check for 2-minute auto-advance (existing windows only)
                if (self.terminal_manager._is_existing_window and 
                    hasattr(self, 'last_2min_check') and 
                    time.time() - self.last_2min_check >= 120):  # 2 minutes = 120 seconds
                    
                    # Check if terminal content changed in the last 2 minutes
                    try:
                        current_content = self.automation_system._try_clipboard_copy_method() or ""
                        if hasattr(self, 'last_content') and current_content == self.last_content:
                            # No change in 2 minutes - auto-advance to next task
                            logging.info(f"⏰ No terminal changes in 2 minutes - auto-advancing from task {task.id}")
                            task.status = TaskStatus.COMPLETED
                            task.output = "\n".join(output_lines)
                            task.error = "Auto-advanced due to no terminal changes in 2 minutes"
                            
                            # Remove completed task from tasks file
                            if self.automation_system:
                                self.automation_system.remove_completed_task(task)
                            
                            # Notify progress callback
                            if self.automation_system and self.automation_system.progress_callback:
                                self.automation_system.progress_callback("task_complete", f"Task {task.id} auto-advanced", {
                                    "task_index": task.id,
                                    "reason": "2-minute timeout"
                                })
                            
                            break
                        else:
                            # Content did change, reset the 2-minute timer
                            self.last_content = current_content
                            self.last_2min_check = time.time()
                            logging.debug("Terminal content changed within 2-minute window - continuing")
                    except Exception as e:
                        logging.debug(f"Error during 2-minute check: {e}")
                        # Reset timer anyway to avoid spam
                        self.last_2min_check = time.time()
                
                # Log every 30 seconds to track progress
                if int(time.time() - start_time) % 30 == 0:
                    logging.info(f"Task {task.id} status: inactive={is_inactive}, time_since_activity={time_since_activity:.1f}s, timeout={self.inactivity_monitor.timeout_seconds}s")
                
                if is_inactive:
                    task.status = TaskStatus.COMPLETED
                    task.output = "\n".join(output_lines)
                    if error_lines:
                        task.error = "\n".join(error_lines)
                    logging.info(f"Task {task.id} completed due to inactivity timeout ({self.inactivity_monitor.timeout_seconds} seconds of silence)")
                    
                    # Remove completed task from tasks file
                    if self.automation_system:
                        self.automation_system.remove_completed_task(task)
                    
                    break
            
            # For new windows, if Claude hasn't started after 5 minutes, assume it started anyway
            if (not claude_started and not self.terminal_manager._is_existing_window and 
                time.time() - start_time > 300):  # 5 minutes
                claude_started = True
                logging.warning("Claude hasn't shown activity indicators after 5 minutes - assuming it started")
                self.inactivity_monitor.reset()
            
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
        self.detected_reset_time: Optional[str] = None
        self.rate_limit_detected = False
    
    def next_window_start(self) -> datetime:
        """Calculate the next execution window start time"""
        now = datetime.now(self.tz)
        
        # Use detected reset time if available
        if self.detected_reset_time:
            try:
                # Parse the detected reset time
                time_str = self.detected_reset_time.lower().strip()
                if 'am' in time_str or 'pm' in time_str:
                    # Parse AM/PM format
                    time_part = time_str.replace('am', '').replace('pm', '').strip()
                    if ':' in time_part:
                        hh, mm = [int(x) for x in time_part.split(':')]
                    else:
                        hh, mm = int(time_part), 0
                    
                    # Handle AM/PM
                    if 'pm' in time_str and hh != 12:
                        hh += 12
                    elif 'am' in time_str and hh == 12:
                        hh = 0
                    
                    reset_time = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
                    
                    # If the reset time is in the past, assume it's for tomorrow
                    if reset_time <= now:
                        reset_time += timedelta(days=1)
                    
                    logging.info(f"Using detected reset time: {self.detected_reset_time} -> {reset_time}")
                    return reset_time
            except Exception as e:
                logging.warning(f"Failed to parse detected reset time '{self.detected_reset_time}': {e}")
        
        # Fall back to configured start time
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
    
    def update_rate_limit_info(self, rate_limit_detected: bool, reset_time: Optional[str] = None):
        """Update rate limit information from terminal output"""
        self.rate_limit_detected = rate_limit_detected
        if reset_time:
            self.detected_reset_time = reset_time
            logging.info(f"Updated reset time to: {reset_time}")
    
    def is_rate_limit_detected(self) -> bool:
        """Check if rate limit has been detected"""
        return self.rate_limit_detected
    
    def wait_until_reset(self):
        """Wait until the detected reset time"""
        if not self.rate_limit_detected or not self.detected_reset_time:
            logging.warning("No rate limit reset time detected, using default start time")
            self.wait_until_window()
            return
        
        reset_time = self.next_window_start()
        logging.info(f"Waiting until rate limit resets at {reset_time.isoformat()}")
        
        while True:
            now = datetime.now(self.tz)
            if now >= reset_time:
                # Reset session state
                self.session_start_time = now
                self.tasks_executed = 0
                self.rate_limit_detected = False
                self.detected_reset_time = None
                logging.info("Rate limit reset - resuming task execution")
                return
            time.sleep(60)  # Check every minute


class TerminalAutomationSystem:
    """🧠 MAIN AUTOMATION SYSTEM - The conductor of the entire orchestra
    
    This is the master class that coordinates all components to create a seamless
    automation experience. Think of it as the conductor of an orchestra where:
    
    🎼 The Orchestra Members:
    • TerminalManager 🖥️ - Handles terminal connections and commands
    • TaskExecutor 🚀 - Executes tasks and monitors completion  
    • RateLimitParser 🔍 - Detects Claude's rate limit messages
    • Scheduler ⏰ - Manages timing and reset periods
    • InactivityMonitor 👀 - Detects when Claude finishes working
    
    🎭 The Performance (Main Workflow):
    1. 📚 Load tasks from JSON file
    2. 🔌 Connect to terminal (existing or new)
    3. 🔍 Check current rate limit status
    4. 🚀 Execute tasks one by one
    5. ⏳ Wait for completion (10min inactivity)
    6. 🚫 Handle rate limits by waiting for reset
    7. 🔄 Continue until all tasks done
    
    🎯 Key Features:
    • Intelligent rate limit detection via clipboard/transcript
    • Automatic waiting and resumption after rate resets
    • Robust error handling and window management
    • Comprehensive logging with visual indicators
    • Support for multiple terminal types and connection modes
    
    This class is where the magic happens - it's the brain that makes
    all the other components work together harmoniously.
    """
    
    def __init__(self, config: Configuration):
        self.config = config
        self.terminal_manager = TerminalManager(config.terminal_type, config.connection_mode)
        self.inactivity_monitor = InactivityMonitor(config.inactivity_timeout)
        self.task_executor = TaskExecutor(self.terminal_manager, self.inactivity_monitor, self)
        self.scheduler = Scheduler(config)
        self.tasks: List[Task] = []
        self._setup_logging()
        # Dual-mode clipboard polling (works for both new/existing windows)
        self._clipboard_poll_interval_sec = 30
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration with detailed tracking"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Create detailed formatters with function names and line numbers
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        
        # Setup file handler with rotation to prevent huge log files
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            'night_writer_detailed.log', 
            maxBytes=10*1024*1024,  # 10MB max per file
            backupCount=5,          # Keep 5 backup files
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        
        # Setup console handler with same detailed format
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(detailed_formatter)
        
        # Configure root logger with detailed formatting
        logging.basicConfig(
            level=log_level,
            handlers=[file_handler, console_handler],
            format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        
        # Log comprehensive system startup information
        logging.info("="*80)
        logging.info("🚀 NIGHT WRITER AUTOMATION SYSTEM STARTING")
        logging.info("="*80)
        logging.info(f"📋 Configuration Details:")
        logging.info(f"   • Terminal Type: {self.config.terminal_type.value}")
        logging.info(f"   • Connection Mode: {self.config.connection_mode.value}")
        logging.info(f"   • Tasks File: {self.config.tasks_file}")
        logging.info(f"   • Log Level: {self.config.log_level}")
        logging.info(f"   • Inactivity Timeout: {self.config.inactivity_timeout} seconds")
        logging.info(f"   • Auto-launch Claude: {self.config.auto_launch_claude}")
        logging.info(f"   • Transcript Enabled: {self.config.transcript_enabled}")
        logging.info(f"   • Timezone: {self.config.timezone}")
        logging.info("="*80)
    
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
    
    def remove_completed_task(self, completed_task: Task) -> bool:
        """Remove a completed task from the tasks file"""
        try:
            tasks_path = Path(self.config.tasks_file)
            if not tasks_path.exists():
                logging.warning(f"Tasks file not found when trying to remove task: {tasks_path}")
                return False
            
            # Read current tasks from file
            content = tasks_path.read_text(encoding="utf-8").strip()
            if not content:
                logging.warning("Tasks file is empty when trying to remove task")
                return False
            
            # Parse current tasks
            if content.lstrip().startswith("["):
                task_strings = json.loads(content)
            else:
                task_strings = [line.strip() for line in content.splitlines() if line.strip()]
            
            # Remove the completed task
            if completed_task.content in task_strings:
                task_strings.remove(completed_task.content)
                logging.info(f"🗑️ Removed completed task from file: {completed_task.content}")
                
                # Write updated tasks back to file
                if task_strings:
                    # Still have tasks remaining
                    updated_content = json.dumps(task_strings, indent=2, ensure_ascii=False)
                else:
                    # No tasks remaining
                    updated_content = "[]"
                    logging.info("🎉 All tasks completed! Tasks file now empty.")
                
                tasks_path.write_text(updated_content, encoding="utf-8")
                return True
            else:
                logging.warning(f"Task not found in file when trying to remove: {completed_task.content}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to remove completed task from file: {e}")
            return False
    
    def _check_and_wait_for_rate_limits(self):
        """🔍 CORE RATE LIMIT DETECTION - Check for rate limits and wait if necessary
        
        This is the heart of the system! It reads the current terminal content
        and detects Claude's rate limit messages like "5-hour limit reached ∙ resets 7pm".
        Uses different strategies based on terminal type:
        - Existing windows: Clipboard method (reads what you see on screen)
        - New windows: Transcript file first, clipboard fallback
        """
        logging.info("🔍 STARTING RATE LIMIT DETECTION")
        logging.info(f"📊 Terminal state: existing={self.terminal_manager._is_existing_window}, process={self.terminal_manager.process is not None}")

        # Send a refresh message to wake up Claude and get fresh status
        if self.terminal_manager._is_existing_window:
            try:
                logging.info("💤 Sending refresh message to wake up Claude before rate limit detection...")
                
                # Send a simple command to refresh Claude's status display
                self.terminal_manager.send_command("# Checking Claude status")
                time.sleep(1)  # Give Claude time to respond
                
                # Notify progress callback if available
                if self.progress_callback:
                    self.progress_callback("waiting", "Refreshing Claude status before detection", None)
                
                logging.info("✅ Refresh message sent successfully")
            except Exception as e:
                logging.warning(f"⚠️ Failed to send refresh message (continuing anyway): {e}")

        # Get the current terminal content (prefer clipboard for existing windows, transcript for new)
        terminal_content = ""
        
        if self.terminal_manager._is_existing_window:
            # 📋 EXISTING WINDOW STRATEGY: Clipboard method is most reliable
            # This reads exactly what you see on the terminal screen right now
            logging.info("📋 Using EXISTING WINDOW strategy - clipboard method")
            try:
                terminal_content = self._try_clipboard_copy_method() or ""
                logging.info(f"✅ Clipboard method success: {len(terminal_content)} characters")
                if terminal_content:
                    # Log a sample of what we captured (first 200 chars)
                    sample = terminal_content.replace('\n', '\\n').replace('\r', '\\r')[:200]
                    logging.info(f"📄 Content sample: '{sample}...'")
            except Exception as e:
                logging.error(f"❌ Clipboard method failed: {e}")
                terminal_content = ""
        else:
            # 📄 NEW WINDOW STRATEGY: Transcript first, clipboard fallback
            # New windows have transcript logging, so we read the log file
            logging.info("📄 Using NEW WINDOW strategy - transcript method first")
            try:
                terminal_content = self._read_transcript_tail() or ""
                logging.info(f"✅ Transcript method: {len(terminal_content)} characters")
                if terminal_content:
                    sample = terminal_content.replace('\n', '\\n').replace('\r', '\\r')[-200:]
                    logging.info(f"📄 Transcript sample (last 200 chars): '...{sample}'")
            except Exception as e:
                logging.error(f"❌ Transcript method failed: {e}")
                terminal_content = ""
            
            # 🔄 FALLBACK: If transcript failed, try clipboard
            if not terminal_content:
                logging.info("🔄 Transcript empty, trying clipboard fallback...")
                try:
                    terminal_content = self._try_clipboard_copy_method() or ""
                    logging.info(f"✅ Clipboard fallback: {len(terminal_content)} characters")
                except Exception as e:
                    logging.error(f"❌ Clipboard fallback failed: {e}")
                    terminal_content = ""
        
        # 🔍 FINAL FALLBACK: For existing windows, do NOT use command-based methods
        if not terminal_content:
            if self.terminal_manager._is_existing_window:
                logging.warning("⚠️ All clipboard methods failed for existing window - skipping command fallbacks")
                # For existing windows, we should NOT send any commands for rate limit detection
                # The user chose this window because Claude is already running
                terminal_content = ""
            else:
                logging.warning("⚠️ All primary methods failed, trying fallback methods...")
                terminal_content = self._get_terminal_content()
        
        # 📊 LOG WHAT WE FOUND
        content_length = len(terminal_content) if terminal_content else 0
        logging.info(f"📊 FINAL CONTENT ANALYSIS: {content_length} characters captured")
        
        if terminal_content:
            # Show a clean sample of what we're analyzing
            clean_sample = terminal_content.replace('\n', '\\n').replace('\r', '\\r')[:300]
            logging.info(f"📝 Content to analyze: '{clean_sample}...'")
            
            # 🧹 FILTER OUT LOG MESSAGES - Don't parse our own logs!
            if "- root - INFO -" in terminal_content or "night_writer" in terminal_content.lower():
                logging.warning("⚠️ Detected log content in terminal - filtering out to avoid parsing own logs")
                # Try to extract only the actual terminal content, not log messages
                lines = terminal_content.split('\n')
                filtered_lines = []
                for line in lines:
                    # Skip log lines and system messages
                    if not any(pattern in line for pattern in [
                        "- root - INFO -", "- root - ERROR -", "- root - WARNING -",
                        "night_writer", "STARTING RATE LIMIT", "CLIPBOARD METHOD",
                        "[_", "] -", "📋", "🔍", "⏰", "🚀", "Reset time:"
                    ]):
                        filtered_lines.append(line)
                
                filtered_content = '\n'.join(filtered_lines).strip()
                if filtered_content:
                    logging.info(f"📝 Filtered content (removed logs): {len(filtered_content)} chars")
                    terminal_content = filtered_content
                    # Show sample of filtered content
                    clean_sample = terminal_content.replace('\n', '\\n').replace('\r', '\\r')[:300]
                    logging.info(f"📝 Filtered content sample: '{clean_sample}...'")
                else:
                    logging.info("📝 All content was log messages - treating as empty")
                    terminal_content = ""
            
            # 🎯 PARSE FOR RATE LIMITS - Only check RECENT lines (last 15 lines)
            if terminal_content:
                # Only check the last 15 lines for rate limit messages
                lines = terminal_content.split('\n')
                recent_lines = lines[-15:] if len(lines) > 15 else lines
                recent_content = '\n'.join(recent_lines).strip()
                
                logging.info(f"🎯 PARSING ONLY RECENT LINES ({len(recent_lines)} lines) FOR RATE LIMIT PATTERNS...")
                logging.info(f"📄 Recent content: '{recent_content.replace(chr(10), '\\n')[:200]}...'")
                
                rate_limit_info = self.task_executor.rate_limit_parser.parse_output(recent_content)
            else:
                logging.info("🎯 No content to parse - no rate limit detected")
                rate_limit_info = {'rate_limit_detected': False, 'reset_time': None}
            
            # 📋 LOG PARSING RESULTS
            logging.info(f"📋 Rate limit detected: {rate_limit_info['rate_limit_detected']}")
            
            if rate_limit_info['rate_limit_detected']:
                # Check if this is a current or expired rate limit
                is_current = rate_limit_info.get('is_current', True)
                
                if not is_current:
                    # This is an old/expired rate limit message
                    logging.info("=" * 80)
                    logging.info("🕐 OLD RATE LIMIT MESSAGE DETECTED (EXPIRED)")
                    logging.info("=" * 80)
                    logging.info(f"📋 Original message: {rate_limit_info.get('message', 'N/A')}")
                    logging.info(f"⏰ Reset time (expired): {rate_limit_info['reset_time']}")
                    logging.info("✅ Claude should be available now - proceeding with tasks")
                    logging.info("=" * 80)
                    
                    # Notify progress callback that we found an old message
                    if self.progress_callback:
                        self.progress_callback("waiting", f"Found expired rate limit from {rate_limit_info['reset_time']} - Claude available", None)
                else:
                    # ⚠️ MAJOR ALERT: Current rate limit detected!
                    logging.warning("=" * 80)
                    logging.warning("🚨 CLAUDE RATE LIMIT DETECTED! 🚨")
                    logging.warning("=" * 80)
                    logging.warning(f"📋 Original message: {rate_limit_info.get('message', 'N/A')}")
                    logging.warning(f"⏰ Reset time detected: {rate_limit_info['reset_time']}")
                    logging.warning(f"🔍 Matched pattern: {rate_limit_info.get('matched_pattern', 'N/A')}")
                    
                    # Notify progress callback with prominent alert
                    if self.progress_callback:
                        reset_time_msg = f"resets at {rate_limit_info['reset_time']}" if rate_limit_info['reset_time'] else "time unknown"
                        self.progress_callback("rate_limit", f"Claude rate limit detected - {reset_time_msg}", None)
                
                # Only wait if the rate limit is current (not expired)
                if is_current:
                    if rate_limit_info['reset_time']:
                        logging.warning(f"🕐 System will wait until Claude resets at: {rate_limit_info['reset_time']}")
                        logging.warning("=" * 80)
                        
                        # Update scheduler with detected reset time
                        self.scheduler.update_rate_limit_info(
                            rate_limit_info['rate_limit_detected'],
                            rate_limit_info['reset_time']
                        )
                        
                        # Wait for the detected reset time
                        logging.info("Waiting for rate limit reset...")
                        self.scheduler.wait_until_reset()
                    else:
                        logging.error("🚨 CRITICAL: Rate limit detected but NO RESET TIME found!")
                        logging.error("📄 Full terminal content for debugging:")
                        logging.error(repr(terminal_content))
                        logging.warning("Using default 4am reset time as fallback")
                        self.scheduler.update_rate_limit_info(True, "4am")
                        self.scheduler.wait_until_reset()
                else:
                    # Expired rate limit - don't wait, continue with tasks
                    logging.info("🚀 Continuing with task execution (rate limit has passed)")
            else:
                logging.info("✅ No rate limit detected in terminal content - ready to start tasks")
        else:
            # If we can't read terminal content, we should still check if there's a rate limit
            # by looking at the current time and seeing if we should wait
            logging.info("No terminal content found - checking if we should wait based on time...")
            
            # Check if we're in a rate limit period based on time
            now = datetime.now(self.scheduler.tz)
            if now.hour < 4:  # Before 4am, we might be in a rate limit period
                logging.info("Current time is before 4am - assuming rate limit is active")
                # Set a default rate limit until 4am
                self.scheduler.update_rate_limit_info(True, "4am")
                logging.info("Waiting for rate limit reset...")
                self.scheduler.wait_until_reset()
            else:
                logging.info("Current time is after 4am - ready to start tasks")

    def _get_terminal_content(self):
        """Get the current content from the terminal"""
        try:
            # For existing windows, try multiple methods to read content
            if hasattr(self.terminal_manager, 'selected_window') and self.terminal_manager.selected_window:
                logging.info("Attempting to read terminal content from existing window...")
                
                # Method 1: Try to read window content directly
                try:
                    logging.info("Trying Method 1: Direct window content reading...")
                    content = self._read_window_content_directly()
                    if content:
                        logging.info(f"Read terminal content directly: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 1: No content returned")
                except Exception as e:
                    logging.info(f"Method 1 failed: {e}")
                
                # Method 2: Try to send a simple command
                try:
                    logging.info("Trying Method 2: Simple command...")
                    content = self._try_simple_command()
                    if content:
                        logging.info(f"Read terminal content via simple command: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 2: No content returned")
                except Exception as e:
                    logging.info(f"Method 2 failed: {e}")
                
                # Method 3: Try PowerShell command
                try:
                    logging.info("Trying Method 3: PowerShell command...")
                    content = self._try_powershell_command()
                    if content:
                        logging.info(f"Read terminal content via PowerShell: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 3: No content returned")
                except Exception as e:
                    logging.info(f"Method 3 failed: {e}")
                
                # Method 4: Try to read console buffer directly
                try:
                    logging.info("Trying Method 4: Console buffer reading...")
                    content = self._try_console_buffer_reading()
                    if content:
                        logging.info(f"Read terminal content via console buffer: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 4: No content returned")
                except Exception as e:
                    logging.info(f"Method 4 failed: {e}")
                
                # Method 5: Try clipboard copy method (BEST!)
                try:
                    logging.info("Trying Method 5: Clipboard copy method...")
                    content = self._try_clipboard_copy_method()
                    if content:
                        logging.info(f"Read terminal content via clipboard: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 5: No content returned")
                except Exception as e:
                    logging.info(f"Method 5 failed: {e}")
                
                # Method 6: Try direct terminal reading
                try:
                    logging.info("Trying Method 6: Direct terminal reading...")
                    content = self._try_direct_terminal_reading()
                    if content:
                        logging.info(f"Read terminal content via direct reading: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 6: No content returned")
                except Exception as e:
                    logging.info(f"Method 6 failed: {e}")
                
                # Method 7: Try screenshot + OCR (fallback)
                try:
                    logging.info("Trying Method 7: Screenshot + OCR...")
                    content = self._try_screenshot_ocr()
                    if content:
                        logging.info(f"Read terminal content via screenshot OCR: {len(content)} characters")
                        return content
                    else:
                        logging.info("Method 7: No content returned")
                except Exception as e:
                    logging.info(f"Method 7 failed: {e}")
                
                logging.warning("All methods failed to read terminal content - will assume no rate limit")
                return ""
            
            # For new windows, use the standard approach
            output = self.terminal_manager.get_output()
            if output:
                content = "\n".join(output)
                logging.info(f"Read terminal content: {len(content)} characters")
                return content
            
            return ""
            
        except Exception as e:
            logging.warning(f"Failed to get terminal content: {e}")
            return ""
    
    def _read_window_content_directly(self):
        """Try to read window content directly using Windows API"""
        try:
            logging.info("Getting window handle...")
            hwnd = self.terminal_manager.selected_window['hwnd']
            logging.info(f"Window handle: {hwnd}")
            
            # Method 1: Try GetWindowText (simpler approach)
            try:
                logging.info("Trying GetWindowText...")
                window_text = win32gui.GetWindowText(hwnd)
                logging.info(f"GetWindowText result: '{window_text}'")
                if window_text and len(window_text.strip()) > 0:
                    # Check if this looks like terminal content (not just window title)
                    # Window titles are usually short and don't contain terminal output
                    # Look for terminal-specific indicators that suggest actual terminal output
                    terminal_content_indicators = [
                        'limit', 'resets', 'error', 'output', 'command', 'prompt', 
                        '>', '$', 'PS', 'python', 'npm', 'git', 'conda',
                        '5-hour limit reached', 'hour limit reached', 'resets',
                        'claude', 'thinking', 'analyzing', 'working'
                    ]
                    
                    # Window title indicators (these suggest it's just a title, not content)
                    window_title_indicators = [
                        'anaconda prompt', 'command prompt', 'powershell', 'terminal',
                        'windows terminal', 'git bash', 'ubuntu', 'wsl'
                    ]
                    
                    is_window_title = any(title_indicator in window_text.lower() for title_indicator in window_title_indicators)
                    has_terminal_content = any(indicator in window_text.lower() for indicator in terminal_content_indicators)
                    
                    is_terminal_content = (
                        (len(window_text) > 100 and not is_window_title) or  # Long content that's not a title
                        (has_terminal_content and not is_window_title) or  # Has terminal indicators but not a title
                        window_text.count('\n') > 2 or  # Multiple lines suggest terminal output
                        '5-hour limit reached' in window_text or
                        'resets' in window_text.lower()
                    )
                    
                    if is_terminal_content:
                        logging.info(f"Got terminal content via GetWindowText: {len(window_text)} characters")
                        return window_text
                    else:
                        logging.info(f"GetWindowText returned window title (not terminal content): '{window_text[:50]}...'")
            except Exception as e:
                logging.info(f"GetWindowText failed: {e}")
            
            # Method 2: Try SendMessage approach
            try:
                logging.info("Getting window text length...")
                text_length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
                logging.info(f"Window text length: {text_length}")
                
                if text_length > 0:
                    # Get window text
                    logging.info("Creating text buffer...")
                    text_buffer = win32gui.PyMakeBuffer(text_length + 1)
                    logging.info("Getting window text...")
                    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, text_length + 1, text_buffer)
                    # Convert buffer to string properly
                    try:
                        # Try different approaches to decode the buffer
                        if hasattr(text_buffer, 'decode'):
                            content = text_buffer[:text_length].decode('utf-8', errors='ignore')
                        else:
                            # Convert to bytes first
                            content_bytes = bytes(text_buffer[:text_length])
                            content = content_bytes.decode('utf-8', errors='ignore')
                    except Exception as decode_error:
                        logging.info(f"Decode error: {decode_error}, trying alternative method")
                        # Try as string directly
                        try:
                            content = str(text_buffer[:text_length])
                        except:
                            content = ""
                    
                    if content and len(content.strip()) > 0:
                        logging.info(f"SendMessage returned: {len(content)} characters")
                        # This is likely still just the window title, not terminal content
                        logging.info("SendMessage approach also returned window title, not terminal content")
                    else:
                        logging.info("SendMessage returned empty content")
                else:
                    logging.info("Window has no text content")
            except Exception as e:
                logging.info(f"SendMessage approach failed: {e}")
            
            # Both GetWindowText and SendMessage only returned window title, not terminal content
            logging.info("Direct window reading methods only found window title, not terminal content")
            return None
        except Exception as e:
            logging.info(f"Direct window reading failed: {e}")
            return None
    
    def _try_simple_command(self):
        """Try to send a simple command to read terminal content"""
        # For existing windows, do NOT send any commands - user selected this window because Claude is already active
        if self.terminal_manager._is_existing_window:
            logging.info("Skipping simple command for existing window (would send unwanted commands)")
            return None
            
        try:
            # Since we can successfully send commands, let's use a command that shows recent history
            # This will show the terminal content including any rate limit messages
            history_command = "echo ==TERMINAL_CONTENT== && echo. && echo Recent terminal activity:"
            logging.info(f"Sending history command: {history_command}")
            
            # Try to send command with minimal window activation
            logging.info("Attempting to send command to existing window...")
            
            # Try multiple approaches to send the command
            success = False
            
            # Approach 1: Try the normal method
            try:
                success = self.terminal_manager._send_command_to_existing_window(history_command)
                logging.info(f"Normal command sending result: {success}")
            except Exception as e:
                logging.info(f"Normal command sending failed: {e}")
            
            # Approach 2: Try direct window manipulation if normal method fails
            if not success:
                try:
                    logging.info("Trying direct window manipulation...")
                    hwnd = self.terminal_manager.selected_window['hwnd']
                    
                    # Try to restore and activate window without thread attachment
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.1)
                    
                    # Try to set foreground without thread attachment
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                    except Exception as e:
                        logging.info(f"SetForegroundWindow failed: {e}")
                    
                    # Try to send keys directly
                    success = self.terminal_manager.send_keys_to_window(hwnd, history_command)
                    logging.info(f"Direct key sending result: {success}")
                    
                except Exception as e:
                    logging.info(f"Direct window manipulation failed: {e}")
            
            if success:
                logging.info("Command sent successfully, waiting for output...")
                time.sleep(2)  # Wait longer for command to execute
                output = self.terminal_manager.get_output()
                logging.info(f"Got output: {output}")
                if output:
                    content = "\n".join(output)
                    if "TERMINAL_CONTENT" in content:
                        logging.info("History command succeeded")
                        return content
                    else:
                        logging.info("Command output doesn't contain expected marker")
                        # Still return the content as it might contain rate limit info
                        return content
                else:
                    logging.info("No output received")
            else:
                logging.info("All command sending methods failed")
            
            # Since we know the terminal is showing rate limit messages, let's try a different approach
            # Let's use a PowerShell command to get the console buffer content
            try:
                logging.info("Trying PowerShell buffer reading...")
                ps_command = 'powershell -Command "Get-Content -Path CONIN$ -TotalCount 50 2>$null || echo \'Buffer read failed\'"'
                success = self.terminal_manager._send_command_to_existing_window(ps_command)
                if success:
                    time.sleep(3)
                    output = self.terminal_manager.get_output()
                    if output:
                        content = "\n".join(output)
                        logging.info(f"PowerShell buffer content: {len(content)} characters")
                        return content
            except Exception as e:
                logging.info(f"PowerShell buffer reading failed: {e}")
            
            return None
        except Exception as e:
            logging.info(f"Simple command failed: {e}")
            return None
    
    def _try_direct_terminal_reading(self):
        """Try to read terminal content using direct subprocess approach"""
        try:
            logging.info("Trying direct terminal reading with subprocess...")
            
            # Try to get the process ID of the terminal window
            hwnd = self.terminal_manager.selected_window['hwnd']
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            logging.info(f"Terminal process ID: {pid}")
            
            # Try to read the terminal content using Windows API
            # This is a more direct approach than sending commands
            import ctypes
            from ctypes import wintypes
            
            # Try to attach to the process and read its console
            try:
                # Open process with read access
                PROCESS_VM_READ = 0x0010
                PROCESS_QUERY_INFORMATION = 0x0400
                
                process_handle = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_VM_READ | PROCESS_QUERY_INFORMATION,
                    False,
                    pid
                )
                
                if process_handle:
                    logging.info("Successfully opened process handle")
                    # For now, just return None as this is complex
                    # In a real implementation, you'd read the process memory
                    ctypes.windll.kernel32.CloseHandle(process_handle)
                    return None
                else:
                    logging.info("Failed to open process handle")
                    return None
                    
            except Exception as e:
                logging.info(f"Direct process reading failed: {e}")
                return None
                
        except Exception as e:
            logging.info(f"Direct terminal reading failed: {e}")
            return None
    
    def _try_clipboard_copy_method(self):
        """📋 CLIPBOARD METHOD - Read terminal content via Ctrl+A + Ctrl+C
        
        This is our most reliable method for existing windows because:
        • 🎯 Reads exactly what you see on the terminal screen
        • 🔄 Works with any terminal type (PowerShell, CMD, etc.)
        • ⚡ Captures real-time content including Claude's responses
        • ⏱️ No timing issues like transcript files
        
        Process:
        1. 🎯 Focus the terminal window
        2. 📝 Select all content (Ctrl+A)
        3. 📋 Copy to clipboard (Ctrl+C)
        4. 📖 Read from Windows clipboard
        5. ✅ Return the captured text
        """
        logging.info("📋 CLIPBOARD METHOD: Starting clipboard-based content capture")
        try:
            hwnd = self.terminal_manager.selected_window['hwnd']
            window_title = self.terminal_manager.selected_window['title']
            
            logging.info(f"Using clipboard method for window: {window_title}")
            
            # 🚨 SAFETY CHECK - Don't read from log files or our own output
            if any(keyword in window_title.lower() for keyword in ["log", "night_writer", "powershell transcript"]):
                logging.warning(f"⚠️ Window '{window_title}' appears to be a log file - skipping clipboard read")
                return None
            
            # First, ensure the window is visible and focused
            try:
                # Restore window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
                
                # Try to bring window to front
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.3)
                
                # Try to set foreground
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.5)
                except Exception as e:
                    logging.info(f"SetForegroundWindow failed (continuing anyway): {e}")
                
            except Exception as e:
                logging.info(f"Window activation failed (continuing anyway): {e}")
            
            # Clear clipboard first
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
                time.sleep(0.1)
            except Exception as e:
                logging.info(f"Clipboard clear failed (continuing anyway): {e}")
            
            # For Windows Terminal, we need to use different key combinations
            # Try multiple approaches to select and copy text
            
            # Approach 1: Try standard Ctrl+A, Ctrl+C
            logging.info("Trying standard text selection (Ctrl+A, Ctrl+C)...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            # Check if clipboard has content
            has_content = False
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    test_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    if test_content and len(test_content.strip()) > 10:  # More than just window title
                        has_content = True
                        logging.info("Standard selection worked!")
                win32clipboard.CloseClipboard()
            except:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
            
            # Approach 2: If standard didn't work, try Windows Terminal specific method
            if not has_content:
                logging.info("Standard selection failed, trying Windows Terminal method...")
                
                # Clear clipboard first
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.CloseClipboard()
                    time.sleep(0.1)
                except:
                    pass
                
                # Try right-click menu approach
                try:
                    # Right click to open context menu
                    pyautogui.rightClick()
                    time.sleep(0.3)
                    
                    # Try to find "Select All" and "Copy" in the context menu
                    # This varies by terminal, but we can try common key sequences
                    pyautogui.press('escape')  # Close menu first
                    time.sleep(0.2)
                    
                    # Try Ctrl+Shift+A for Windows Terminal
                    pyautogui.hotkey('ctrl', 'shift', 'a')
                    time.sleep(0.3)
                    pyautogui.hotkey('ctrl', 'shift', 'c')
                    time.sleep(0.5)
                    
                except Exception as e:
                    logging.info(f"Windows Terminal method failed: {e}")
                
                # Check if this approach worked
                try:
                    win32clipboard.OpenClipboard()
                    if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                        test_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                        if test_content and len(test_content.strip()) > 10:
                            has_content = True
                            logging.info("Windows Terminal method worked!")
                    win32clipboard.CloseClipboard()
                except:
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
            
            # Approach 3: Try triple-click to select all and then copy
            if not has_content:
                logging.info("Trying triple-click selection...")
                
                # Clear clipboard
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.CloseClipboard()
                    time.sleep(0.1)
                except:
                    pass
                
                # Triple click to select all text
                pyautogui.tripleClick()
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.5)
            
            # Read from clipboard
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                    
                    if content and len(content.strip()) > 0:
                        logging.info(f"Successfully read {len(content)} characters from clipboard")
                        # Check if this looks like actual terminal content vs just window title
                        if len(content) > 50 or any(keyword in content.lower() for keyword in ['limit', 'resets', '>', '$', 'c:\\', 'echo']):
                            return content
                        else:
                            logging.info("Clipboard content appears to be just window title or minimal content")
                            return None
                    else:
                        logging.info("Clipboard content is empty")
                        return None
                else:
                    win32clipboard.CloseClipboard()
                    logging.info("No text format available in clipboard")
                    return None
                    
            except Exception as e:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
                logging.info(f"Clipboard reading failed: {e}")
                return None
                
        except Exception as e:
            logging.info(f"Clipboard copy method failed: {e}")
            return None
    
    def _try_powershell_command(self):
        """Try to send a PowerShell command to read terminal content"""
        # For existing windows, do NOT send any commands - user selected this window because Claude is already active
        if self.terminal_manager._is_existing_window:
            logging.info("Skipping PowerShell command for existing window (would send unwanted commands)")
            return None
            
        try:
            # Try PowerShell command with better error handling
            capture_command = "echo TERMINAL_STATE && powershell -Command \"Get-Content -Path 'con' -Tail 10\""
            
            if self.terminal_manager._send_command_to_existing_window(capture_command):
                time.sleep(3)
                output = self.terminal_manager.get_output()
                if output:
                    content = "\n".join(output)
                    if "TERMINAL_STATE" in content:
                        logging.info("PowerShell command succeeded")
                        return content
            
            return None
        except Exception as e:
            logging.debug(f"PowerShell command failed: {e}")
            return None
    
    def _try_console_buffer_reading(self):
        """Try to read console buffer directly using Windows API"""
        try:
            hwnd = self.terminal_manager.selected_window['hwnd']
            logging.info(f"Attempting to read console buffer for window {hwnd}")
            
            import ctypes
            from ctypes import wintypes, Structure, c_char, c_short, c_ushort, c_ulong
            
            # Define Windows API structures
            class COORD(Structure):
                _fields_ = [("X", c_short), ("Y", c_short)]
            
            class SMALL_RECT(Structure):
                _fields_ = [("Left", c_short), ("Top", c_short), ("Right", c_short), ("Bottom", c_short)]
            
            class CONSOLE_SCREEN_BUFFER_INFO(Structure):
                _fields_ = [
                    ("dwSize", COORD),
                    ("dwCursorPosition", COORD),
                    ("wAttributes", c_ushort),
                    ("srWindow", SMALL_RECT),
                    ("dwMaximumWindowSize", COORD)
                ]
            
            class CHAR_INFO(Structure):
                _fields_ = [("Char", c_ushort), ("Attributes", c_ushort)]
            
            # Get Windows API functions
            kernel32 = ctypes.windll.kernel32
            
            # Try to get the console window handle
            try:
                console_hwnd = kernel32.GetConsoleWindow()
                logging.info(f"Console window handle: {console_hwnd}, Target window: {hwnd}")
                
                if console_hwnd == hwnd:
                    logging.info("Window is a console window, reading buffer...")
                    
                    # Get console handle
                    console_handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                    if console_handle == -1 or console_handle is None:
                        logging.info("Failed to get console handle")
                        return None
                    
                    # Get console screen buffer info
                    buffer_info = CONSOLE_SCREEN_BUFFER_INFO()
                    if not kernel32.GetConsoleScreenBufferInfo(console_handle, ctypes.byref(buffer_info)):
                        logging.info("Failed to get console screen buffer info")
                        return None
                    
                    # Calculate buffer size
                    buffer_width = buffer_info.dwSize.X
                    buffer_height = buffer_info.dwSize.Y
                    logging.info(f"Console buffer size: {buffer_width}x{buffer_height}")
                    
                    # Read the entire console buffer
                    buffer_size = buffer_width * buffer_height
                    char_buffer = (CHAR_INFO * buffer_size)()
                    
                    # Define the region to read (entire buffer)
                    read_region = SMALL_RECT()
                    read_region.Left = 0
                    read_region.Top = 0
                    read_region.Right = buffer_width - 1
                    read_region.Bottom = buffer_height - 1
                    
                    # Read console output
                    if kernel32.ReadConsoleOutputW(
                        console_handle,
                        ctypes.byref(char_buffer),
                        COORD(buffer_width, buffer_height),
                        COORD(0, 0),
                        ctypes.byref(read_region)
                    ):
                        # Extract text from buffer
                        text_lines = []
                        for y in range(buffer_height):
                            line = ""
                            for x in range(buffer_width):
                                char_info = char_buffer[y * buffer_width + x]
                                char_code = char_info.Char
                                if char_code != 0:  # Skip null characters
                                    line += chr(char_code)
                            
                            if line.strip():  # Only add non-empty lines
                                text_lines.append(line.rstrip())
                        
                        if text_lines:
                            content = "\n".join(text_lines)
                            logging.info(f"Read console buffer: {len(content)} characters")
                            return content
                        else:
                            logging.info("Console buffer is empty")
                            return None
                    else:
                        logging.info("Failed to read console output")
                        return None
                else:
                    logging.info(f"Window {hwnd} is not the console window {console_hwnd}")
                    return None
                    
            except Exception as e:
                logging.info(f"Console buffer reading failed: {e}")
                return None
                
        except Exception as e:
            logging.info(f"Console buffer reading failed: {e}")
            return None
    
    def _try_screenshot_ocr(self):
        """Try to read terminal content using screenshot + OCR"""
        try:
            hwnd = self.terminal_manager.selected_window['hwnd']
            window_title = self.terminal_manager.selected_window['title']
            
            logging.info(f"Taking screenshot of window: {window_title}")
            
            # First, ensure the window is visible and focused
            try:
                # Restore window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
                
                # Try to bring window to front
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)
                
                # Try to set foreground (may fail, but that's ok)
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.2)
                except Exception as e:
                    logging.info(f"SetForegroundWindow failed (this is ok): {e}")
                
            except Exception as e:
                logging.info(f"Window activation failed (this is ok): {e}")
            
            # Method 1: Try using pygetwindow to get window bounds
            try:
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    window = windows[0]
                    logging.info(f"Found window via pygetwindow: {window.left}, {window.top}, {window.width}, {window.height}")
                    
                    # Take screenshot of the window
                    bbox = (window.left, window.top, window.left + window.width, window.top + window.height)
                    screenshot = ImageGrab.grab(bbox=bbox)
                    logging.info(f"Screenshot captured: {screenshot.size}")
                    
                    # Save screenshot for debugging
                    screenshot.save("debug_terminal_screenshot.png")
                    logging.info("Screenshot saved as debug_terminal_screenshot.png")
                    
                else:
                    logging.info("Window not found via pygetwindow, trying win32gui approach")
                    # Method 2: Use win32gui to get window rectangle
                    rect = win32gui.GetWindowRect(hwnd)
                    left, top, right, bottom = rect
                    logging.info(f"Window rect via win32gui: {left}, {top}, {right}, {bottom}")
                    
                    # Take screenshot of the window
                    bbox = (left, top, right, bottom)
                    screenshot = ImageGrab.grab(bbox=bbox)
                    logging.info(f"Screenshot captured: {screenshot.size}")
                    
                    # Save screenshot for debugging
                    screenshot.save("debug_terminal_screenshot.png")
                    logging.info("Screenshot saved as debug_terminal_screenshot.png")
                    
            except Exception as e:
                logging.info(f"Screenshot capture failed: {e}")
                return None
            
            # Initialize EasyOCR reader (English only for better performance)
            if not HAS_OCR:
                logging.info("EasyOCR not available, skipping OCR method")
                return None
                
            logging.info("Initializing EasyOCR...")
            reader = easyocr.Reader(['en'], gpu=False)  # Use CPU for better compatibility
            
            # Perform OCR on the screenshot
            logging.info("Performing OCR on screenshot...")
            # Convert PIL Image to numpy array for EasyOCR
            try:
                import numpy as np
                screenshot_array = np.array(screenshot)
                results = reader.readtext(screenshot_array)
            except ImportError:
                logging.info("NumPy not available, skipping OCR method")
                return None
            
            # Extract text from OCR results
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only include high-confidence text
                    extracted_text.append(text)
                    logging.info(f"OCR result: '{text}' (confidence: {confidence:.2f})")
            
            if extracted_text:
                content = "\n".join(extracted_text)
                logging.info(f"OCR extracted {len(content)} characters of text")
                return content
            else:
                logging.info("No text extracted from OCR")
                return None
                
        except Exception as e:
            logging.info(f"Screenshot OCR failed: {e}")
            return None

    def _check_rate_limit_during_task(self) -> bool:
        """Check for rate limits during task execution for existing windows"""
        try:
            if not self.terminal_manager._is_existing_window:
                return False
            
            # For existing windows, we need to use a different approach
            # We'll send a command that will show the current terminal content
            # and then try to capture it
            
            # For existing windows, use clipboard method without sending ANY commands
            logging.info("Using clipboard method for rate limit detection (no commands)")
            try:
                content = self._try_clipboard_copy_method() or ""
                if content:
                    # Only check recent lines for rate limits
                    lines = content.split('\n')
                    recent_lines = lines[-15:] if len(lines) > 15 else lines
                    recent_content = '\n'.join(recent_lines).strip()
                    
                    logging.info(f"Checking recent content for rate limits: {len(recent_lines)} lines")
                    
                    # Check for rate limits in the recent content
                    rate_limit_info = self.task_executor.rate_limit_parser.parse_output(recent_content)
                    if rate_limit_info['rate_limit_detected']:
                        self.task_executor.rate_limit_detected = True
                        self.task_executor.detected_reset_time = rate_limit_info['reset_time']
                        logging.info(f"Rate limit detected during task: {rate_limit_info['message']}")
                        if rate_limit_info['reset_time']:
                            logging.info(f"Reset time detected during task: {rate_limit_info['reset_time']}")
                        return True
                        
            except Exception as e:
                logging.warning(f"Error reading clipboard during rate limit check: {e}")
                
            return False
            
        except Exception as e:
            logging.warning(f"Failed to check rate limit during task: {e}")
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
    
    def _is_claude_already_active(self) -> bool:
        """Check if Claude is already active in the existing terminal window WITHOUT sending commands"""
        try:
            logging.info("Checking if Claude is already active in terminal (no commands)...")
            
            # For existing windows, just read current content without sending ANY commands
            terminal_content = ""
            
            # Try to read the current terminal content
            if self.terminal_manager._is_existing_window:
                # Use clipboard method for existing windows (reads what's currently visible)
                try:
                    terminal_content = self._try_clipboard_copy_method() or ""
                    logging.info(f"Read {len(terminal_content)} characters from clipboard")
                except:
                    terminal_content = ""
            else:
                # For new windows, try transcript first
                try:
                    terminal_content = self._get_transcript_content() or ""
                except:
                    terminal_content = ""
                
            if terminal_content:
                # Look for Claude-specific indicators in recent terminal content
                # Only check last few lines to avoid old content
                lines = terminal_content.split('\n')
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                recent_content = '\n'.join(recent_lines).lower()
                
                claude_indicators = [
                    "claude",  # Claude command or interface
                    "anthropic",  # Anthropic references
                    "bypass permissions",  # Claude Code specific
                    "alt+m to cycle",  # Claude Code specific
                ]
                
                for indicator in claude_indicators:
                    if indicator in recent_content:
                        logging.info(f"Claude detected via indicator: {indicator}")
                        return True
                
                # Check for active command prompt
                if any(pattern in recent_content for pattern in ["ps ", "c:\\", "> ", "$ "]):
                    logging.info("Active terminal detected, assuming Claude is available")
                    return True
                
            logging.info("Claude activity not detected in current content")
            # For existing windows, assume Claude is probably available
            if self.terminal_manager._is_existing_window:
                logging.info("Existing window - assuming Claude is available to avoid disruption")
                return True
            return False
            
        except Exception as e:
            logging.warning(f"Error checking Claude status: {e}")
            # For existing windows, assume it's active to avoid disruption
            if self.terminal_manager._is_existing_window:
                return True
            return False
    
    def run_session(self) -> bool:
        """Run a complete automation session"""
        try:
            # Start terminal first
            if not self.terminal_manager.start_terminal():
                logging.error("Failed to start terminal")
                return False
            
            logging.info("Terminal started successfully")

            # If a project directory was selected, cd into it and optionally open Claude
            initial_dir = getattr(self, "_initial_project_dir", None)
            auto_open = getattr(self, "_auto_open_claude", True)
            if initial_dir and self.terminal_manager._is_existing_window:
                # Skip cd command for existing windows - they're already in the right place
                logging.info(f"Skipping cd command for existing window (would have been: cd '{initial_dir}')")
                
                # For existing windows, check if Claude is already active before launching
                if auto_open and self.config.auto_launch_claude:
                    if self._is_claude_already_active():
                        logging.info("Claude is already active in existing window, skipping launch")
                    else:
                        logging.info("Claude not detected, launching in existing window")
                        self.terminal_manager.send_command(self.config.claude_command)
                        time.sleep(0.5)
            
            # ALWAYS check for rate limits FIRST - this is the key!
            logging.info("Reading terminal to detect current rate limit status...")
            self._check_and_wait_for_rate_limits()
            
            # After long waits, re-validate the window before sending anything
            if not self.terminal_manager.ensure_window_ready():
                logging.error("No valid terminal window after rate-limit wait")
                return False
            
            # Set session start time after rate limit check
            from datetime import datetime
            self.scheduler.session_start_time = datetime.now(self.scheduler.tz)
            self.scheduler.tasks_executed = 0
            
            # Execute tasks continuously
            task_index = 0
            while task_index < len(self.tasks):
                task = self.tasks[task_index]
                
                # Execute task
                # Validate window before each task (handles terminals that closed or changed)
                if not self.terminal_manager.ensure_window_ready():
                    logging.error("No valid terminal window available for task; reselect a terminal")
                    # Give the user a chance to pick a new window and retry same task
                    continue
                completed_task = self.task_executor.execute_task(task)
                
                # Check if rate limit was detected during task execution
                if self.task_executor.rate_limit_detected:
                    logging.info("Rate limit detected during task execution")
                    self.scheduler.update_rate_limit_info(
                        self.task_executor.rate_limit_detected,
                        self.task_executor.detected_reset_time
                    )
                    
                    # Wait for reset time instead of stopping
                    logging.info("Waiting for rate limit reset...")
                    self.scheduler.wait_until_reset()
                    
                    # Reset task executor state
                    self.task_executor.rate_limit_detected = False
                    self.task_executor.detected_reset_time = None
                    
                    # Re-validate window after waking up from a rate limit wait
                    if not self.terminal_manager.ensure_window_ready():
                        logging.error("No valid terminal window after rate-limit wait while looping tasks")
                        continue
                    
                    # Continue with the same task (don't increment index)
                    continue
                
                # Only save output and record execution if task was actually completed
                if completed_task.status == TaskStatus.COMPLETED:
                    # Save output
                    output_path = self.save_task_output(completed_task)
                    if output_path:
                        logging.info(f"Task {completed_task.id} output saved to {output_path}")
                    
                    # Record execution
                    self.scheduler.record_task_execution()
                    
                    # Reset inactivity monitor for next task
                    self.inactivity_monitor.reset()
                    
                    logging.info(f"Task {completed_task.id} completed with status: {completed_task.status.value}")
                    
                    # Move to next task
                    task_index += 1
                elif completed_task.status == TaskStatus.RATE_LIMITED:
                    logging.info(f"Task {completed_task.id} was rate limited - will retry after reset")
                    # Don't increment task_index - will retry the same task
                    continue
                else:
                    logging.info(f"Task {completed_task.id} failed with status: {completed_task.status.value}")
                    # Move to next task even if failed
                    task_index += 1
                
                # Add delay between tasks to prevent running too fast
                if task_index < len(self.tasks):
                    # During delay, poll for rate-limit detection
                    logging.info("Waiting 5 seconds before next task (polling for rate limits)...")
                    try:
                        time.sleep(1)
                        # Use same logic as main rate limit check
                        snapshot = ""
                        if self.terminal_manager._is_existing_window:
                            snapshot = self._try_clipboard_copy_method() or ""
                        else:
                            snapshot = self._read_transcript_tail() or ""
                            if not snapshot:
                                snapshot = self._try_clipboard_copy_method() or ""
                        
                        if snapshot:
                            info = self.task_executor.rate_limit_parser.parse_output(snapshot)
                            if info['rate_limit_detected']:
                                self.scheduler.update_rate_limit_info(True, info['reset_time'])
                                logging.info("Rate limit detected between tasks; waiting for reset...")
                                self.scheduler.wait_until_reset()
                                if not self.terminal_manager.ensure_window_ready():
                                    logging.error("No valid terminal window after rate-limit wait between tasks")
                                continue
                    except Exception:
                        pass
                    time.sleep(4)
            
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
    
    def _read_transcript_tail(self, max_bytes: int = 16384) -> str:
        """Read the tail of the PowerShell transcript log, if available."""
        try:
            transcript_path = self.terminal_manager._resolve_transcript_path()
            if not transcript_path:
                return ""
            p = Path(transcript_path)
            if not p.exists():
                return ""
            with open(p, 'rb') as f:
                try:
                    f.seek(0, 2)
                    size = f.tell()
                    f.seek(max(0, size - max_bytes), 0)
                except Exception:
                    pass
                data = f.read()
            try:
                text = data.decode('utf-8', errors='ignore')
            except Exception:
                text = data.decode('cp1252', errors='ignore')
            return text
        except Exception as e:
            logging.debug(f"Transcript read failed: {e}")
            return ""
    
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
