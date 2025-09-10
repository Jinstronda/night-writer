# 🌙 Night Writer - Automated Claude Code Assistant

**Automate your Claude Code sessions with intelligent task scheduling and rate limit management**

## 🚀 Overview

Night Writer is a sophisticated Python automation system that manages Claude Code sessions, automatically executing tasks from a JSON file while intelligently handling rate limits and scheduling. It's designed to maximize your Claude usage by working around the 5-hour daily limits.

### ✨ Key Features

- 🎯 **Smart Rate Limit Detection** - Automatically detects "5-hour limit reached ∙ resets Xpm" messages
- ⏰ **Intelligent Scheduling** - Waits for rate limit resets and continues automatically
- 🖥️ **Multi-Terminal Support** - Works with existing or new terminal windows
- 📋 **Clipboard-Based Reading** - Reads exactly what you see on screen for maximum reliability
- 🔄 **Continuous Operation** - Never stops due to rate limits, just waits and continues
- 📝 **Comprehensive Logging** - Detailed logs with emojis for easy monitoring
- 🛡️ **Robust Error Handling** - Gracefully handles window closures, network issues, etc.

## 🏗️ Architecture

### Core Components

1. **TerminalAutomationSystem** 🧠 - Main orchestrator that coordinates everything
2. **TerminalManager** 🖥️ - Handles terminal connections and command sending
3. **TaskExecutor** 🚀 - Executes individual tasks and monitors completion
4. **RateLimitParser** 🔍 - Detects rate limit messages in terminal output
5. **Scheduler** ⏰ - Manages timing, resets, and session limits
6. **InactivityMonitor** 👀 - Detects when Claude finishes working (10min silence)

### How It Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Tasks    │───▶│  Connect to     │───▶│  Check Rate     │
│   from JSON     │    │  Terminal       │    │  Limits         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Wait for Reset │◀───│  Rate Limited?  │◀───│  Send Task to   │
│  Time & Resume  │    │  (5hr limit)    │    │  Claude         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Task Complete? │◀───│  Monitor for    │
                       │  (10min quiet)  │    │  Inactivity     │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │  Next Task or   │
                       │  Session End    │
                       └─────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.9+
- Windows 10/11 (uses Windows-specific APIs)
- Claude Code installed and accessible via `claude` command

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

```
psutil>=5.9.0
pywin32>=306
Pillow>=10.0.0
easyocr>=1.7.0
pygetwindow>=0.0.9
pyautogui>=0.9.54
```

## 🎮 Usage

### Quick Start

1. **Create your tasks file** (`tasks.txt`):
```json
[
    "Implement user authentication system",
    "Add error handling to API endpoints", 
    "Create unit tests for core functions",
    "Optimize database queries",
    "Update documentation"
]
```

2. **Run the system**:
```bash
python night_writer_cli.py
```

3. **Follow the interactive setup**:
   - Choose terminal type (PowerShell recommended)
   - Select connection mode (existing window recommended)
   - Enter your project folder path
   - Select your terminal window

### Configuration Options

#### Terminal Types
- **PowerShell** (recommended) - Full feature support
- **CMD** - Basic support
- **Bash/Zsh/Fish** - Linux/WSL support

#### Connection Modes
- **Existing Window** (recommended) - Connect to your current Claude session
- **New Window** - Create a fresh terminal with transcript logging
- **Auto Detect** - Let the system choose

### Advanced Usage

#### Custom Configuration

```python
config = Configuration(
    terminal_type=TerminalType.POWERSHELL,
    connection_mode=TerminalConnectionMode.EXISTING_WINDOW,
    tasks_file="my_tasks.json",
    inactivity_timeout=600,  # 10 minutes
    timezone="America/New_York"
)
```

#### Command Line Arguments

```bash
python night_writer_cli.py --project-path "C:\MyProject" --tasks custom_tasks.json
```

## 🔧 Configuration

### Default Settings

```python
@dataclass
class Configuration:
    terminal_type: TerminalType = TerminalType.POWERSHELL
    connection_mode: TerminalConnectionMode = TerminalConnectionMode.EXISTING_WINDOW
    tasks_file: str = "tasks.txt"
    inactivity_timeout: int = 600  # 10 minutes
    session_limit_hours: int = 5
    reset_time_hour: int = 4  # 4 AM
    timezone: str = "America/New_York"
    log_level: str = "INFO"
    auto_launch_claude: bool = True
    transcript_enabled: bool = True
    claude_command: str = "claude --dangerously-skip-permissions"
```

## 🔍 Rate Limit Detection

The system uses multiple strategies to detect Claude's rate limits:

### Primary Method: Clipboard Reading
- 📋 Captures exactly what you see on screen
- ⚡ Real-time, no timing delays
- 🎯 Most reliable for existing windows

### Fallback Method: Transcript Files
- 📄 Reads PowerShell transcript logs
- 🔄 Good for new windows
- ⏱️ May have slight delays

### Detection Patterns
The system looks for messages like:
- `5-hour limit reached ∙ resets 7pm`
- `Usage limit reached ∙ resets at 4am`
- `Rate limit exceeded ∙ resets 11pm`

## 📊 Logging

Comprehensive logging with visual indicators:

```
🚀 NIGHT WRITER AUTOMATION SYSTEM STARTING
📋 Configuration Details:
   • Terminal Type: powershell
   • Connection Mode: existing_window
   • Tasks File: tasks.txt

🔍 STARTING RATE LIMIT DETECTION
📋 Using EXISTING WINDOW strategy - clipboard method
✅ Clipboard method success: 2847 characters
📝 Content to analyze: '> Implement user authentication...'

🎯 PARSING CONTENT FOR RATE LIMIT PATTERNS...
📋 Rate limit detected: false

🚀 STARTING TASK EXECUTION
📋 Task Details:
   • ID: 0
   • Content: Implement user authentication system
   • Status: running
```

### Log Files
- `night_writer_detailed.log` - Comprehensive logs with rotation (10MB max)
- Includes function names, line numbers, and timestamps
- 5 backup files maintained automatically

## 🛠️ Troubleshooting

### Common Issues

#### "No terminal windows found"
- Ensure you have a terminal open (PowerShell, CMD, etc.)
- Try running as administrator
- Check Windows permissions

#### "Rate limit not detected"
- Verify the terminal content is visible
- Try the clipboard method manually (Ctrl+A, Ctrl+C)
- Check if Claude is actually showing rate limit messages

#### "Window activation failed"
- Try clicking on the terminal manually first
- Ensure no other applications are blocking window focus
- Run with administrator privileges

#### "Clipboard method failed"
- Some terminals may not support Ctrl+A properly
- Try switching terminal types
- Manually test Ctrl+A, Ctrl+C in your terminal

### Debug Mode

Enable verbose logging:

```python
config.log_level = "DEBUG"
```

Or set environment variable:
```bash
set LOG_LEVEL=DEBUG
python night_writer_cli.py
```

## 🔒 Security Considerations

- Uses `--dangerously-skip-permissions` flag for Claude (required for automation)
- Reads clipboard content (only from selected terminal)
- Accesses Windows API for window management
- All operations are local to your machine

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive logging and comments
4. Test with different terminal types
5. Submit a pull request

### Code Style

- Use emoji comments for major sections (🚀, 📋, 🔍, etc.)
- Comprehensive docstrings for all methods
- Detailed logging with context
- Type hints for all functions

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built for the Claude Code community
- Inspired by the need for automated AI assistance
- Special thanks to all beta testers

---

**Happy Automating! 🌙✨**

*Night Writer - Because your code doesn't sleep*