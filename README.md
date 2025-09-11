# Night Writer
<img width="1024" height="1024" alt="Generated Image September 11, 2025 - 3_49PM" src="https://github.com/user-attachments/assets/1c9454fc-be64-4d04-9d08-bfb0099c0686" />



A simple tool that automates your Claude tasks. You give it a list of things to do, it sends them to Claude one by one, and marks them as done when Claude finishes.

## How it works

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

The system watches your terminal to see when Claude starts working and when it's done. It's smart enough to know the difference between "Claude is thinking" and "Claude is stuck." If Claude doesn't respond for 2 minutes, it moves to the next task.

## Getting started

1. **Have Claude running** - Open Claude in your browser or terminal
2. **Put your tasks in tasks.txt** - One task per line, or as a JSON array
3. **Run Night Writer v1.1.exe** - Double-click it
4. **Click "Refresh Windows"** - It'll find your terminal
5. **Select your terminal** - Click on it in the list
6. **Click "Start Automation"** - That's it

## Your tasks file

Just put your tasks in `tasks.txt` like this:

```
Fix the login bug
Add error handling to the API
Write tests for the new feature
Update the documentation
```

Or as JSON:
```json
[
  "Fix the login bug",
  "Add error handling to the API", 
  "Write tests for the new feature",
  "Update the documentation"
]
```

## What happens

Night Writer sends the first task to Claude, then watches your terminal. When Claude finishes (you'll see it stop typing for a while), it marks that task as done and moves to the next one. If Claude hits its rate limit, it automatically detects this and waits until the limit resets. If nothing happens for 2 minutes, it assumes the task is done and moves to the next one.

The whole point is you don't have to babysit it. You can walk away and come back later to see how many tasks are done.

## Requirements

- Windows 10/11
- Claude running somewhere (browser or terminal)
- A terminal window open (PowerShell, CMD, whatever)

That's it. No Python, no dependencies, no complicated setup.

## Troubleshooting

**"No terminal windows found"** - Make sure you have a terminal open, then click "Refresh Windows"

**"Tasks file not found"** - Make sure `tasks.txt` is in the same folder as the exe

**Nothing happens when you click start** - Make sure you selected a terminal window from the list first

**Claude seems stuck** - Night Writer will automatically move to the next task after 2 minutes of inactivity

## Bugs

If something breaks, send me a message:
- Instagram: @joaopanizzutti  
- Email: joaopanizzutti@gmail.com

I'll fix it.

---

*Night Writer - Because your code doesn't sleep*
