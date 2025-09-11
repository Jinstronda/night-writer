# 🌙 Night Writer - Standalone Executable

## What is Night Writer?

Night Writer is an automation tool that helps you run tasks continuously in Claude Code sessions. It handles rate limits automatically by waiting for resets and continuing with your tasks.

## How to Use

1. **Open Claude Code** in a terminal (PowerShell, Command Prompt, or Windows Terminal)
2. **Run Night Writer.exe** - The GUI will open
3. **Click "🔄 REFRESH WINDOWS"** - This finds all your open terminal windows
4. **Select your Claude Code terminal** from the list
5. **Click "🚀 START AUTOMATION"** - Night Writer will start executing tasks

## What You'll See

The GUI shows real-time progress:
- **🚀 Task 1: [task description]** - When starting each task
- **📄 Claude is working on the task...** - When Claude is actively working
- **💤 Task completed - Claude is idle** - When tasks finish
- **⏱️ Rate limited: waiting until reset** - If rate limits are hit
- **✅ Task completed** - When tasks finish successfully

## Tasks File

Night Writer reads tasks from `tasks.txt` (must be in the same folder as the exe). This file contains a JSON array of tasks like:

```json
[
  "Review the code and fix any bugs",
  "Add error handling to the main functions",
  "Update the README with usage instructions"
]
```

## Features

- ✅ **Automatic Rate Limit Handling** - Waits for resets and continues
- ✅ **Works with Existing Claude Sessions** - No need to restart Claude
- ✅ **Real-time Progress Updates** - See exactly what's happening
- ✅ **No Commands Sent to Existing Windows** - Uses clipboard reading only
- ✅ **Handles Multiple Terminal Types** - PowerShell, CMD, Windows Terminal

## Requirements

- Windows 10/11
- Claude Code running in a terminal
- `tasks.txt` file in the same folder as the exe

## Troubleshooting

- **No terminals found**: Make sure Claude Code is running in a terminal window
- **Tasks not loading**: Check that `tasks.txt` exists and contains valid JSON
- **Rate limit issues**: Night Writer automatically handles these - just wait

---
Built for the Claude Code automation community 🚀