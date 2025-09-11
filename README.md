# 🌙 Night Writer v1.1 - Intelligent Terminal Automation

**Automate your Claude.ai tasks with smart file management and auto-advance features**

## 🚀 What is Night Writer?

Night Writer is an intelligent terminal automation system that monitors your clipboard, detects when you copy tasks from Claude.ai, automatically executes them in your selected terminal window, and manages your task list by removing completed items. It features smart auto-advance to prevent getting stuck and comprehensive task file management.

### ✨ Key Features

- 🗑️ **Automatic Task File Management** - Completed tasks automatically deleted from tasks.txt
- ⏰ **Smart Auto-Advance** - 2-minute rule prevents getting stuck on unresponsive tasks
- 🎯 **Intelligent Rate Limit Detection** - Distinguishes old vs current rate limits using timestamps
- 📋 **Terminal Content Monitoring** - Detects when Claude starts working and continues monitoring
- 📝 **Comprehensive Task Logging** - Clear visibility of task initiation, progress, and completion
- 🖥️ **Multi-Terminal Support** - Works with existing terminal windows (PowerShell, CMD, etc.)
- 🔄 **Real-Time Progress Updates** - Live status updates in GUI with detailed logging
- 💿 **Standalone Executable** - 62MB optimized build, no Python installation required

## 🔄 How It Works

Night Writer automates your Claude.ai workflow with intelligent monitoring and management:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Tasks    │───▶│  Select Terminal│───▶│  Send Task to   │
│   from tasks.txt│    │  Window         │    │  Claude         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Remove from    │◀───│  Task Complete? │◀───│  Monitor Terminal│
│  tasks.txt      │    │  (10min/2min)   │    │  Content Changes│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │  Next Task or   │
                       │  All Done       │
                       └─────────────────┘
```

### Smart Features

- **Terminal Change Detection**: Knows Claude is working when content changes
- **2-Minute Auto-Advance**: Prevents getting stuck on unresponsive tasks  
- **Rate Limit Intelligence**: Only waits for future reset times, ignores expired ones
- **File Management**: Automatically removes completed tasks from tasks.txt

## 📦 Installation

### 🚀 Option 1: Standalone Executable (Recommended)

**No installation required!**

1. **Download the distribution package**:
   - Get the `Night Writer Distribution/` folder
   - Contains: `Night Writer Optimized.exe`, `tasks.txt`, `README.txt`

2. **Run immediately**:
   ```
   Double-click "Night Writer Optimized.exe"
   ```

3. **Requirements**:
   - Windows 10/11
   - No Python installation needed
   - No dependencies to install

### 🐍 Option 2: Python Source (Advanced Users)

**For developers who want to modify the code:**

#### Prerequisites
- Python 3.9+
- Windows 10/11 (uses Windows-specific APIs)
- Claude Code installed and accessible via `claude` command

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Required Packages
```
psutil>=5.9.0
pywin32>=306
Pillow>=10.0.0
easyocr>=1.7.0  # Optional - for OCR features
pygetwindow>=0.0.9
pyautogui>=0.9.54
```

## 🎮 Usage

### 🚀 Standalone Executable (Recommended)

**The easiest way to use Night Writer:**

1. **Launch the application**:
   ```
   Double-click "Night Writer Optimized.exe"
   ```

2. **Simple 2-button interface**:
   - 🔄 Click "REFRESH WINDOWS" to scan for terminals
   - 🖥️ Select your terminal window from the list
   - 🚀 Click "START AUTOMATION" to begin

3. **Features**:
   - Real-time task progress updates
   - Live status monitoring in log area
   - Current task execution display
   - Rate limit detection and waiting
   - Idle state monitoring

### 🖥️ Python GUI Version (Advanced)

**For developers using the Python source:**

1. **Launch via Python**:
   ```bash
   python night_writer_simple.py
   ```

2. **Advanced configuration options**:
   - 📁 Custom project folder selection
   - 📄 Different tasks file
   - 🔧 Terminal type selection

### 📝 Command Line Version

For advanced users who prefer terminal interfaces:

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

### Standalone Executable Issues

#### "No terminal windows found"
- Ensure you have a terminal open (PowerShell, CMD, Windows Terminal, etc.)
- Click "REFRESH WINDOWS" button to scan again
- Try running the exe as administrator

#### "Application won't start"
- Check Windows permissions - exe needs access to clipboard and window management
- Some antivirus software may block the executable (false positive)
- Try moving the exe to a different folder

#### "Tasks file not found"
- Ensure `tasks.txt` is in the same folder as the exe
- Edit `tasks.txt` with your own tasks in JSON format

### General Issues

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

## 🚀 Performance & Optimization

### Executable Optimization

The standalone executable has been heavily optimized:

- **Original build**: 3.09 GB 
- **Optimized build**: 62 MB
- **95% size reduction achieved!**

#### Optimization Techniques Used:
- 🔥 Conditional imports for heavy ML dependencies
- 📦 Excluded unnecessary packages (PyTorch, TensorFlow, etc.)
- 🎯 Retained all core functionality
- ⚡ Fast startup and minimal resource usage

### Performance Features:
- 🚀 Real-time progress updates
- 📊 Efficient clipboard monitoring
- 🔄 Smart rate limit detection
- 💾 Minimal memory footprint

## 🔒 Security Considerations

- Uses `--dangerously-skip-permissions` flag for Claude (required for automation)
- Reads clipboard content (only from selected terminal)
- Accesses Windows API for window management
- All operations are local to your machine
- Standalone executable is self-contained with no external dependencies

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