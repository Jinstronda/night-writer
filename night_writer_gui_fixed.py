"""
🌙 NIGHT WRITER - Fixed Modern GUI 
Integrates the EXISTING working automation system with modern UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from pathlib import Path
from datetime import datetime
import queue

# Import the EXISTING working automation system
from terminal_automation import TerminalAutomationSystem, TerminalWindowManager, Configuration

class DesignSystem:
    """SOTA Design System with modern tokens"""
    
    # Typography Scale
    FONT_DISPLAY = ("Segoe UI", 32, "bold")
    FONT_H1 = ("Segoe UI", 28, "bold")
    FONT_H2 = ("Segoe UI", 24, "bold")
    FONT_H3 = ("Segoe UI", 20, "bold")
    FONT_BODY_LG = ("Segoe UI", 16)
    FONT_BODY = ("Segoe UI", 14)
    FONT_BODY_SM = ("Segoe UI", 12)
    FONT_CAPTION = ("Segoe UI", 11)
    FONT_CODE = ("JetBrains Mono", 12)
    
    # Spacing Scale
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    SPACE_2XL = 48
    SPACE_3XL = 64
    
    # Color System
    PRIMARY_500 = "#0ea5e9"
    PRIMARY_600 = "#0284c7"
    
    SUCCESS_500 = "#22c55e"
    WARNING_500 = "#f59e0b"
    ERROR_500 = "#ef4444"
    
    # Dark Theme
    BG_PRIMARY = "#0f172a"
    BG_SECONDARY = "#1e293b"
    BG_TERTIARY = "#334155"
    
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#cbd5e1"
    TEXT_MUTED = "#64748b"
    
    BORDER_COLOR = "#334155"
    RADIUS_MD = 8

class ModernCard(tk.Frame):
    """Modern card component"""
    
    def __init__(self, parent, padding=None, **kwargs):
        padding = padding or DesignSystem.SPACE_LG
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, relief="flat", **kwargs)
        
        self.content_frame = tk.Frame(self, bg=DesignSystem.BG_SECONDARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

class ModernButton(tk.Button):
    """Modern button component"""
    
    def __init__(self, parent, text="", variant="primary", size="md", icon="", **kwargs):
        variants = {
            "primary": {
                "bg": DesignSystem.PRIMARY_500,
                "fg": "white",
                "activebackground": DesignSystem.PRIMARY_600,
            },
            "secondary": {
                "bg": DesignSystem.BG_TERTIARY,
                "fg": DesignSystem.TEXT_PRIMARY,
                "activebackground": DesignSystem.BORDER_COLOR,
            },
            "success": {
                "bg": DesignSystem.SUCCESS_500,
                "fg": "white",
                "activebackground": "#16a34a",
            },
            "danger": {
                "bg": DesignSystem.ERROR_500,
                "fg": "white",
                "activebackground": "#dc2626",
            }
        }
        
        sizes = {
            "sm": {"font": DesignSystem.FONT_BODY_SM, "padx": 12, "pady": 6},
            "md": {"font": DesignSystem.FONT_BODY, "padx": 16, "pady": 8},
            "lg": {"font": DesignSystem.FONT_BODY_LG, "padx": 20, "pady": 12},
            "xl": {"font": DesignSystem.FONT_H3, "padx": 24, "pady": 16}
        }
        
        variant_config = variants[variant]
        size_config = sizes[size]
        
        display_text = f"{icon} {text}" if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            **variant_config,
            **size_config,
            **kwargs
        )

class StatusIndicator(tk.Frame):
    """Status indicator with icons"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, **kwargs)
        
        self.icon_label = tk.Label(
            self, 
            text="⚪", 
            font=DesignSystem.FONT_BODY_LG,
            bg=DesignSystem.BG_SECONDARY,
            fg=DesignSystem.TEXT_SECONDARY
        )
        self.icon_label.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_SM))
        
        self.text_label = tk.Label(
            self,
            text="Ready",
            font=DesignSystem.FONT_BODY,
            bg=DesignSystem.BG_SECONDARY,
            fg=DesignSystem.TEXT_SECONDARY
        )
        self.text_label.pack(side=tk.LEFT)
        
    def set_status(self, status, text):
        """Set status with icon and text"""
        status_config = {
            "idle": {"icon": "⚪", "color": DesignSystem.TEXT_MUTED},
            "working": {"icon": "🔄", "color": DesignSystem.PRIMARY_500},
            "success": {"icon": "✅", "color": DesignSystem.SUCCESS_500},
            "error": {"icon": "❌", "color": DesignSystem.ERROR_500},
            "warning": {"icon": "⚠️", "color": DesignSystem.WARNING_500}
        }
        
        config = status_config.get(status, status_config["idle"])
        self.icon_label.config(text=config["icon"], fg=config["color"])
        self.text_label.config(text=text, fg=config["color"])

class LogViewer(tk.Frame):
    """Log viewer with scrolling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, **kwargs)
        
        self.text_frame = tk.Frame(self, bg=DesignSystem.BG_SECONDARY)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_MD, pady=DesignSystem.SPACE_MD)
        
        self.text_area = tk.Text(
            self.text_frame,
            bg=DesignSystem.BG_PRIMARY,
            fg=DesignSystem.TEXT_PRIMARY,
            font=DesignSystem.FONT_CODE,
            wrap=tk.WORD,
            padx=DesignSystem.SPACE_MD,
            pady=DesignSystem.SPACE_MD,
            relief="flat",
            borderwidth=0,
            state=tk.DISABLED
        )
        
        scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for different log levels
        self.text_area.tag_configure("INFO", foreground=DesignSystem.TEXT_PRIMARY)
        self.text_area.tag_configure("SUCCESS", foreground=DesignSystem.SUCCESS_500)
        self.text_area.tag_configure("WARNING", foreground=DesignSystem.WARNING_500)
        self.text_area.tag_configure("ERROR", foreground=DesignSystem.ERROR_500)
        
    def add_log(self, message, level="INFO"):
        """Add a log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, formatted_message, level)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

class NightWriterFixed:
    """Fixed Night Writer GUI that uses the EXISTING working automation system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 Night Writer - Fixed Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg=DesignSystem.BG_PRIMARY)
        
        # Application state
        self.windows_data = []
        self.selected_window = None
        self.automation_system = None
        self.is_running = False
        self.gui_queue = queue.Queue()
        
        self.setup_gui()
        self.refresh_windows()  # Load windows immediately
        self.check_queue()
        
    def setup_gui(self):
        """Setup the modern GUI layout"""
        # Main container
        main_container = tk.Frame(self.root, bg=DesignSystem.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_LG, pady=DesignSystem.SPACE_LG)
        
        # Header
        self.setup_header(main_container)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=DesignSystem.BG_PRIMARY)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(DesignSystem.SPACE_LG, 0))
        
        # Left panel - Configuration
        left_panel = tk.Frame(content_frame, bg=DesignSystem.BG_PRIMARY, width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, DesignSystem.SPACE_LG))
        left_panel.pack_propagate(False)
        
        # Right panel - Monitoring
        right_panel = tk.Frame(content_frame, bg=DesignSystem.BG_PRIMARY)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup panels
        self.setup_configuration_panel(left_panel)
        self.setup_monitoring_panel(right_panel)
        
    def setup_header(self, parent):
        """Setup header with title and status"""
        header_card = ModernCard(parent, padding=DesignSystem.SPACE_LG)
        header_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        header_content = tk.Frame(header_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        header_content.pack(fill=tk.X)
        
        # Title section
        title_frame = tk.Frame(header_content, bg=DesignSystem.BG_SECONDARY)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(
            title_frame,
            text="🌙 Night Writer",
            font=DesignSystem.FONT_DISPLAY,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Terminal Automation Suite",
            font=DesignSystem.FONT_BODY_LG,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_SECONDARY
        )
        subtitle_label.pack(anchor=tk.W)
        
        # Status section
        status_frame = tk.Frame(header_content, bg=DesignSystem.BG_SECONDARY)
        status_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_status = StatusIndicator(status_frame)
        self.main_status.pack(pady=DesignSystem.SPACE_MD)
        
    def setup_configuration_panel(self, parent):
        """Setup configuration panel with the ACTUAL workflow"""
        # Step 1: Window Selection
        window_card = ModernCard(parent)
        window_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        tk.Label(
            window_card.content_frame,
            text="🖥️ Step 1: Select Terminal Window",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Window list
        list_frame = tk.Frame(window_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        list_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        self.window_listbox = tk.Listbox(
            list_frame,
            height=6,
            bg=DesignSystem.BG_PRIMARY,
            fg=DesignSystem.TEXT_PRIMARY,
            font=DesignSystem.FONT_BODY,
            selectbackground=DesignSystem.PRIMARY_500,
            relief="flat",
            borderwidth=0
        )
        self.window_listbox.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_SM))
        self.window_listbox.bind('<<ListboxSelect>>', self.on_window_select)
        
        # Refresh button
        ModernButton(
            window_card.content_frame,
            text="🔄 Refresh Windows",
            variant="secondary",
            command=self.refresh_windows
        ).pack()
        
        # Step 2: Project Configuration
        project_card = ModernCard(parent)
        project_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        tk.Label(
            project_card.content_frame,
            text="📁 Step 2: Configure Project",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Project path
        path_frame = tk.Frame(project_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        path_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        tk.Label(
            path_frame,
            text="Project Directory:",
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W)
        
        path_input_frame = tk.Frame(path_frame, bg=DesignSystem.BG_SECONDARY)
        path_input_frame.pack(fill=tk.X, pady=(DesignSystem.SPACE_SM, 0))
        
        self.path_var = tk.StringVar(value=str(Path.cwd()))
        self.path_entry = tk.Entry(
            path_input_frame,
            textvariable=self.path_var,
            font=DesignSystem.FONT_BODY,
            bg=DesignSystem.BG_PRIMARY,
            fg=DesignSystem.TEXT_PRIMARY,
            relief="flat",
            borderwidth=0
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, DesignSystem.SPACE_SM))
        
        ModernButton(
            path_input_frame,
            text="Browse",
            size="sm",
            variant="secondary",
            command=self.browse_project
        ).pack(side=tk.RIGHT)
        
        # Tasks file
        tasks_frame = tk.Frame(project_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        tasks_frame.pack(fill=tk.X, pady=(DesignSystem.SPACE_MD, 0))
        
        tk.Label(
            tasks_frame,
            text="Tasks File:",
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W)
        
        tasks_input_frame = tk.Frame(tasks_frame, bg=DesignSystem.BG_SECONDARY)
        tasks_input_frame.pack(fill=tk.X, pady=(DesignSystem.SPACE_SM, 0))
        
        self.tasks_file_var = tk.StringVar(value="tasks.txt")
        self.tasks_file_entry = tk.Entry(
            tasks_input_frame,
            textvariable=self.tasks_file_var,
            font=DesignSystem.FONT_BODY,
            bg=DesignSystem.BG_PRIMARY,
            fg=DesignSystem.TEXT_PRIMARY,
            relief="flat",
            borderwidth=0
        )
        self.tasks_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, DesignSystem.SPACE_SM))
        
        ModernButton(
            tasks_input_frame,
            text="Browse",
            size="sm",
            variant="secondary",
            command=self.browse_tasks_file
        ).pack(side=tk.RIGHT)
        
        # Step 3: Execution
        execution_card = ModernCard(parent)
        execution_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            execution_card.content_frame,
            text="🚀 Step 3: Start Automation",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Control buttons
        button_frame = tk.Frame(execution_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        button_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        self.start_button = ModernButton(
            button_frame,
            text="🚀 START AUTOMATION",
            size="xl",
            variant="primary",
            command=self.start_automation
        )
        self.start_button.pack(pady=(0, DesignSystem.SPACE_MD))
        
        button_row = tk.Frame(button_frame, bg=DesignSystem.BG_SECONDARY)
        button_row.pack(fill=tk.X)
        
        self.stop_button = ModernButton(
            button_row,
            text="⏹️ Stop",
            size="md",
            variant="danger",
            command=self.stop_automation,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_MD))
        
        ModernButton(
            button_row,
            text="⚙️ Settings",
            size="md",
            variant="secondary",
            command=self.show_settings
        ).pack(side=tk.LEFT)
        
    def setup_monitoring_panel(self, parent):
        """Setup monitoring and log panel"""
        # Log viewer
        log_card = ModernCard(parent)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_card.content_frame,
            text="📋 Automation Log",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        self.log_viewer = LogViewer(log_card.content_frame)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
    def refresh_windows(self):
        """Refresh terminal windows list using EXISTING system"""
        try:
            self.log_viewer.add_log("Scanning for terminal windows...", "INFO")
            window_manager = TerminalWindowManager()
            windows = window_manager.find_terminal_windows()
            
            self.window_listbox.delete(0, tk.END)
            self.windows_data = windows
            
            for window in windows:
                display_text = f"🖥️ {window['title']} ({window['process_name']})"
                self.window_listbox.insert(tk.END, display_text)
                
            self.log_viewer.add_log(f"Found {len(windows)} terminal windows", "SUCCESS")
            self.main_status.set_status("success", f"Found {len(windows)} terminal windows")
            
        except Exception as e:
            self.log_viewer.add_log(f"Error scanning windows: {str(e)}", "ERROR")
            self.main_status.set_status("error", f"Scan failed: {str(e)}")
            
    def on_window_select(self, event):
        """Handle window selection"""
        selection = self.window_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_window = self.windows_data[index]
            window_title = self.selected_window['title']
            self.main_status.set_status("success", f"✓ Selected: {window_title}")
            self.log_viewer.add_log(f"Selected terminal: {window_title}", "SUCCESS")
            
    def browse_project(self):
        """Browse for project directory"""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.path_var.set(directory)
            self.log_viewer.add_log(f"Project directory set: {directory}", "INFO")
            
    def browse_tasks_file(self):
        """Browse for tasks file"""
        filename = filedialog.askopenfilename(
            title="Select Tasks File",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.tasks_file_var.set(filename)
            self.log_viewer.add_log(f"Tasks file set: {filename}", "INFO")
            
    def create_config(self):
        """Create automation config using EXISTING system"""
        return Configuration(
            tasks_file=self.tasks_file_var.get(),
            check_interval=30,
            inactivity_timeout=600,
            max_wait_time=3600,
            debug_mode=True
        )
        
    def start_automation(self):
        """Start automation using EXISTING system"""
        if not self.selected_window:
            messagebox.showwarning("Selection Required", 
                                 "Please select a terminal window first.")
            return
            
        try:
            self.log_viewer.add_log("Initializing automation system...", "INFO")
            
            # Create and configure automation system using EXISTING code
            self.config = self.create_config()
            self.automation_system = TerminalAutomationSystem(self.config)
            
            # Configure for existing window
            self.automation_system.terminal_manager.selected_window = self.selected_window
            self.automation_system.terminal_manager._is_existing_window = True
            
            # Set project directory
            project_path = self.path_var.get() or str(Path.cwd())
            self.automation_system._initial_project_dir = project_path
            self.automation_system.terminal_manager.initial_working_dir = project_path
            self.automation_system._auto_open_claude = True
            
            # Load tasks
            if not self.automation_system.load_tasks(self.config.tasks_file):
                messagebox.showerror("Error", "Failed to load tasks file")
                return
                
            # Update UI state
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.main_status.set_status("working", "🚀 Starting automation...")
            
            self.log_viewer.add_log("Starting automation thread...", "INFO")
            
            # Start automation thread
            self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
            self.automation_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {str(e)}")
            self.log_viewer.add_log(f"Startup error: {str(e)}", "ERROR")
            self.reset_ui()
            
    def run_automation(self):
        """Run automation using EXISTING system"""
        try:
            self.gui_queue.put(("log", "🔄 Connecting to terminal...", "INFO"))
            self.gui_queue.put(("status", "working", "🔄 Connecting to terminal..."))
            
            # Use the EXISTING automation system
            success = self.automation_system.run_session()
            
            if success:
                self.gui_queue.put(("log", "✅ Automation completed successfully!", "SUCCESS"))
                self.gui_queue.put(("status", "success", "✅ Automation completed"))
            else:
                self.gui_queue.put(("log", "⏹️ Automation stopped", "WARNING"))
                self.gui_queue.put(("status", "idle", "⏹️ Automation stopped"))
                
        except Exception as e:
            self.gui_queue.put(("log", f"❌ Automation error: {str(e)}", "ERROR"))
            self.gui_queue.put(("status", "error", f"❌ Error: {str(e)}"))
            
        finally:
            self.gui_queue.put(("finished", None, None))
            
    def stop_automation(self):
        """Stop automation"""
        if self.automation_system:
            self.automation_system.terminal_manager.stop_terminal()
            
        self.is_running = False
        self.reset_ui()
        self.main_status.set_status("idle", "⏹️ Automation stopped")
        self.log_viewer.add_log("Automation stopped by user", "WARNING")
        
    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
        
    def check_queue(self):
        """Check GUI queue for updates from background thread"""
        try:
            while True:
                event, data, extra = self.gui_queue.get_nowait()
                
                if event == "log":
                    self.log_viewer.add_log(data, extra)
                elif event == "status":
                    self.main_status.set_status(data, extra)
                elif event == "finished":
                    self.reset_ui()
                    
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = NightWriterFixed(root)
    root.mainloop()

if __name__ == "__main__":
    main()