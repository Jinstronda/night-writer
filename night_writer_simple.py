"""
🌙 NIGHT WRITER - SIMPLE VERSION
ONLY 2 BUTTONS: Refresh Windows + Start Automation
"""

import tkinter as tk
from tkinter import messagebox
import threading
from pathlib import Path
import queue

# Import the EXISTING working automation system
from terminal_automation import TerminalAutomationSystem, TerminalWindowManager, Configuration

class DesignSystem:
    """Simple design system"""
    
    # Colors
    BG_PRIMARY = "#0f172a"
    BG_SECONDARY = "#1e293b"
    PRIMARY_500 = "#0ea5e9"
    PRIMARY_600 = "#0284c7"
    SUCCESS_500 = "#22c55e"
    ERROR_500 = "#ef4444"
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#cbd5e1"
    
    # Fonts
    FONT_TITLE = ("Segoe UI", 32, "bold")
    FONT_BODY = ("Segoe UI", 14)
    FONT_BUTTON = ("Segoe UI", 16, "bold")
    
    # Spacing
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32

class ModernButton(tk.Button):
    """Simple modern button"""
    
    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=DesignSystem.FONT_BUTTON,
            bg=DesignSystem.PRIMARY_500,
            fg="white",
            activebackground=DesignSystem.PRIMARY_600,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=DesignSystem.SPACE_LG,
            pady=DesignSystem.SPACE_MD,
            **kwargs
        )

class NightWriterSimple:
    """Simple Night Writer with ONLY 2 buttons"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 Night Writer - Simple")
        self.root.geometry("800x600")
        self.root.configure(bg=DesignSystem.BG_PRIMARY)
        
        # State
        self.windows_data = []
        self.selected_window = None
        self.automation_system = None
        self.is_running = False
        self.gui_queue = queue.Queue()
        
        self.setup_gui()
        self.refresh_windows()  # Auto-load windows on startup
        self.check_queue()
        
    def setup_gui(self):
        """Setup simple GUI with only 2 buttons"""
        # Main container
        main_frame = tk.Frame(self.root, bg=DesignSystem.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_XL, pady=DesignSystem.SPACE_XL)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🌙 Night Writer",
            font=DesignSystem.FONT_TITLE,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_PRIMARY
        )
        title_label.pack(pady=(0, DesignSystem.SPACE_XL))
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Ready - Select a terminal window",
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_PRIMARY
        )
        self.status_label.pack(pady=(0, DesignSystem.SPACE_LG))
        
        # Window list
        self.window_listbox = tk.Listbox(
            main_frame,
            height=8,
            font=DesignSystem.FONT_BODY,
            bg=DesignSystem.BG_SECONDARY,
            fg=DesignSystem.TEXT_PRIMARY,
            selectbackground=DesignSystem.PRIMARY_500,
            relief="flat",
            borderwidth=0
        )
        self.window_listbox.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        self.window_listbox.bind('<<ListboxSelect>>', self.on_window_select)
        
        # BUTTON 1: Refresh Windows
        self.refresh_button = ModernButton(
            main_frame,
            text="🔄 REFRESH WINDOWS",
            command=self.refresh_windows
        )
        self.refresh_button.pack(pady=(0, DesignSystem.SPACE_MD))
        
        # BUTTON 2: Start Automation
        self.start_button = ModernButton(
            main_frame,
            text="🚀 START AUTOMATION",
            command=self.start_automation
        )
        self.start_button.pack()
        
        # Log area (simple text widget)
        log_frame = tk.Frame(main_frame, bg=DesignSystem.BG_PRIMARY)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(DesignSystem.SPACE_LG, 0))
        
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=("Consolas", 10),
            bg=DesignSystem.BG_SECONDARY,
            fg=DesignSystem.TEXT_PRIMARY,
            relief="flat",
            borderwidth=0,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """Add log message"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def set_status(self, message, color=None):
        """Set status message"""
        if color is None:
            color = DesignSystem.TEXT_SECONDARY
        self.status_label.config(text=message, fg=color)
        
    def refresh_windows(self):
        """BUTTON 1: Refresh terminal windows"""
        try:
            self.log("🔍 Scanning for terminal windows...")
            self.set_status("Scanning for terminals...", DesignSystem.TEXT_SECONDARY)
            
            window_manager = TerminalWindowManager()
            windows = window_manager.find_terminal_windows()
            
            self.window_listbox.delete(0, tk.END)
            self.windows_data = windows
            
            if windows:
                for window in windows:
                    display_text = f"🖥️ {window['title']} ({window['process_name']})"
                    self.window_listbox.insert(tk.END, display_text)
                    
                self.log(f"✅ Found {len(windows)} terminal windows")
                self.set_status(f"Found {len(windows)} terminal windows - Select one", DesignSystem.SUCCESS_500)
            else:
                self.log("❌ No terminal windows found")
                self.set_status("No terminals found - Open a terminal first", DesignSystem.ERROR_500)
                
        except Exception as e:
            self.log(f"❌ Error scanning windows: {str(e)}")
            self.set_status(f"Error: {str(e)}", DesignSystem.ERROR_500)
            
    def on_window_select(self, event):
        """Handle window selection"""
        selection = self.window_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_window = self.windows_data[index]
            window_title = self.selected_window['title']
            self.set_status(f"✓ Selected: {window_title}", DesignSystem.SUCCESS_500)
            self.log(f"✅ Selected terminal: {window_title}")
            
    def start_automation(self):
        """BUTTON 2: Start automation"""
        if not self.selected_window:
            messagebox.showwarning("No Terminal Selected", 
                                 "Please select a terminal window first using 'Refresh Windows'")
            return
            
        if self.is_running:
            messagebox.showinfo("Already Running", "Automation is already running!")
            return
            
        try:
            self.log("🚀 Starting automation...")
            self.set_status("Starting automation...", DesignSystem.PRIMARY_500)
            
            # Create config with defaults
            config = Configuration(
                tasks_file="tasks.txt",  # Default tasks file
                inactivity_timeout=600,
                auto_launch_claude=True
            )
            
            # Create automation system
            self.automation_system = TerminalAutomationSystem(config)
            
            # Configure for existing window
            self.automation_system.terminal_manager.selected_window = self.selected_window
            self.automation_system.terminal_manager._is_existing_window = True
            
            # Set project directory to current directory
            project_path = str(Path.cwd())
            self.automation_system._initial_project_dir = project_path
            self.automation_system.terminal_manager.initial_working_dir = project_path
            self.automation_system._auto_open_claude = True
            
            # Load tasks
            if not self.automation_system.load_tasks(config.tasks_file):
                messagebox.showerror("Error", f"Failed to load tasks from {config.tasks_file}")
                return
                
            # Update UI state
            self.is_running = True
            self.start_button.config(state=tk.DISABLED, text="🚀 RUNNING...", bg=DesignSystem.SUCCESS_500)
            
            self.log(f"📋 Loaded tasks from {config.tasks_file}")
            self.log("🔗 Connecting to terminal...")
            
            # Start automation thread
            self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
            self.automation_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {str(e)}")
            self.log(f"❌ Startup error: {str(e)}")
            self.reset_ui()
            
    def run_automation(self):
        """Run automation in background"""
        try:
            self.gui_queue.put(("log", "🔄 Executing automation...", None))
            self.gui_queue.put(("status", "Running automation...", DesignSystem.PRIMARY_500))
            
            # Run the EXISTING automation system
            success = self.automation_system.run_session()
            
            if success:
                self.gui_queue.put(("log", "✅ Automation completed successfully!", None))
                self.gui_queue.put(("status", "✅ Automation completed!", DesignSystem.SUCCESS_500))
            else:
                self.gui_queue.put(("log", "⏹️ Automation stopped", None))
                self.gui_queue.put(("status", "⏹️ Automation stopped", DesignSystem.TEXT_SECONDARY))
                
        except Exception as e:
            self.gui_queue.put(("log", f"❌ Automation error: {str(e)}", None))
            self.gui_queue.put(("status", f"❌ Error: {str(e)}", DesignSystem.ERROR_500))
            
        finally:
            self.gui_queue.put(("finished", None, None))
            
    def reset_ui(self):
        """Reset UI to initial state"""
        self.is_running = False
        self.start_button.config(
            state=tk.NORMAL, 
            text="🚀 START AUTOMATION", 
            bg=DesignSystem.PRIMARY_500
        )
        
    def check_queue(self):
        """Check for updates from background thread"""
        try:
            while True:
                event, data, color = self.gui_queue.get_nowait()
                
                if event == "log":
                    self.log(data)
                elif event == "status":
                    self.set_status(data, color)
                elif event == "finished":
                    self.reset_ui()
                    
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = NightWriterSimple(root)
    root.mainloop()

if __name__ == "__main__":
    main()