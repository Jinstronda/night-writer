# Night Writer - The Script That Codes While You Sleep

I wanted to run Claude Code 24/7, but there's this annoying 5-hour limit that resets at 4am. So I built this thing that automatically feeds tasks to my terminal while I'm sleeping.

## The Problem I Solved

You know how you have this brilliant idea at 2am but Claude's rate limit kicks in? Or you want to keep coding through the night but you can't stay awake to manually send the next task? That was me. I needed something that would:

- Keep my terminal running tasks all night
- Automatically detect when a task is done (no more manual "next task" clicking)
- Respect the 5-hour limits and 4am resets
- Work with whatever terminal I already have open
- Just work without me babysitting it

## What This Actually Does

This script is basically a robot that types commands into your terminal and waits for them to finish. It's smarter than it sounds:

- **Finds your existing terminal** - No need to close what you're working on
- **Types tasks automatically** - Reads from a simple JSON file
- **Knows when you're done** - Waits for silence, then moves to the next task
- **Respects limits** - Stops at 5 hours, waits until 4am, then starts again
- **Works with anything** - PowerShell, CMD, Bash, whatever you're using

## Getting Started (It's Actually Simple)

### Install the Thing

```bash
pip install -r requirements.txt
```

That's it. The script needs `psutil` and `pywin32` (on Windows) to work.

### Set Up Your Tasks

Create a `tasks.txt` file with your commands. I use JSON because it's clean:

```json
[
  "Keep going",
  "Go to the next task", 
  "Test everything, document, and clean the code",
  "Keep going",
  "Go to the next task"
]
```

Or just plain text - one command per line. Whatever works for you.

### Run It

**The lazy way** (uses your existing terminal):
```bash
python night_writer_cli.py --test-mode
```

**The "I want to see what it does" way**:
```bash
python night_writer_cli.py --connection-mode existing_window --test-mode
```

This will show you all your open terminals and let you pick which one to use.

## The Options (You Probably Don't Need Most of These)

The script has a bunch of options, but honestly, the defaults work fine. Here are the ones you might actually care about:

```bash
# Use your existing terminal (recommended)
python night_writer_cli.py --connection-mode existing_window

# Run just one session to test it
python night_writer_cli.py --test-mode

# Change when it starts (default is 4am)
python night_writer_cli.py --start-time "22:00"

# Make it wait longer before moving to next task (default is 10 minutes)
python night_writer_cli.py --inactivity-timeout 300

# See what it's configured to do
python night_writer_cli.py --show-config
```

The full list is there if you need it, but I've never used most of these options. The script just works.

## How It Actually Works

The script is pretty straightforward once you understand what it's doing:

1. **Finds your terminal** - Either creates a new one or connects to what you already have open
2. **Waits for the right time** - Default is 4am (when Claude's limits reset)
3. **Types your tasks** - One by one, from your JSON file
4. **Listens for silence** - When your terminal stops outputting stuff for 10 minutes, it assumes you're done
5. **Moves to the next task** - Rinse and repeat
6. **Stops at 5 hours** - Respects the rate limit, then waits until 4am again

The clever part is that it doesn't need to understand what your commands do. It just types them and waits for quiet. Simple but effective.

## Your Task File

Put your commands in `tasks.txt`. I use JSON because it's clean:

```json
[
  "Keep going",
  "Go to the next task",
  "Test everything, document, and clean the code",
  "Keep going"
]
```

Or just plain text if you prefer:
```
Keep going
Go to the next task  
Test everything, document, and clean the code
Keep going
```

## The Code (If You're Curious)

I built this with a few main pieces:

- **TerminalManager** - Handles finding and talking to your terminal
- **TaskExecutor** - Types commands and waits for them to finish  
- **InactivityMonitor** - Knows when you're done (listens for silence)
- **Scheduler** - Handles the 4am resets and 5-hour limits
- **TerminalAutomationSystem** - The main thing that ties it all together

The cool part is that it works with existing terminals. On Windows, it uses the Windows API to find your open terminal windows and send keystrokes to them. No need to close what you're working on.

### Connection Modes

- **`existing_window`** - Uses whatever terminal you already have open (recommended)
- **`new_window`** - Creates a fresh terminal (old behavior)
- **`auto_detect`** - Tries existing first, falls back to new (default)

## What It Saves

The script saves everything it does in the `night_writer_outputs` folder:

- **Your original tasks** - What it typed
- **Terminal output** - What your terminal responded with
- **Errors** - If something went wrong
- **Timing info** - How long each task took

Useful for debugging, but honestly I rarely look at these files. The script just works.

## Testing (If You Want to Be Sure)

I wrote a bunch of tests because I'm paranoid about things breaking:

```bash
python test_terminal_automation.py
```

24 tests covering everything from basic functionality to edge cases. They all pass, which means the script actually works.

## Real Examples

**The most common way I use it:**
```bash
python night_writer_cli.py --connection-mode existing_window --test-mode
```

**When I want to start earlier (like 10pm instead of 4am):**
```bash
python night_writer_cli.py --start-time "22:00"
```

**When I'm impatient and want it to move faster between tasks:**
```bash
python night_writer_cli.py --inactivity-timeout 300  # 5 minutes instead of 10
```

**When I want to see what it's going to do:**
```bash
python night_writer_cli.py --show-config
```

That's it. I don't really use the other options. The defaults work fine for my use case.

## When Things Go Wrong

**"It can't find my terminal"**
- Make sure you have a terminal open before running the script
- Try `--connection-mode new_window` to force a new terminal

**"It's not waiting long enough"**
- Your tasks might take longer than 10 minutes. Try `--inactivity-timeout 1800` (30 minutes)

**"It's not starting at the right time"**
- Check your timezone with `--show-config`
- The default is 4am, which is when Claude's limits reset

**"Something's broken"**
- Run with `--log-level DEBUG` to see what's happening
- Check the `terminal_automation.log` file

Most issues are just configuration problems. The script is pretty robust.

## The Files

```
night-writer/
├── terminal_automation.py    # The main script that does the work
├── night_writer_cli.py       # Command line interface (what you actually run)
├── test_terminal_automation.py # Tests (because I'm paranoid)
├── tasks.txt                # Your tasks go here
├── requirements.txt         # What you need to install
└── README.md               # This file
```

## Why I Built This

I was tired of manually clicking "next task" every few minutes when working with Claude Code. The 5-hour limit was annoying, and I wanted to keep coding through the night without staying awake.

So I built this script that:
- Automatically types commands into my terminal
- Waits for them to finish (by listening for silence)
- Moves to the next task
- Respects the rate limits and resets

It's not fancy, but it works. Now I can set it up before bed and wake up to a bunch of completed tasks.

## License

MIT License - use it however you want.

---

*Built by João Panizzutti because I wanted to code while sleeping.*
