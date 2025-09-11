"""
🌙 NIGHT WRITER - Modern GUI Redesign
Complete redesign with SOTA UI principles and in-GUI execution
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from pathlib import Path
from datetime import datetime
import queue
from task_executor import InGUIAutomationSystem

class DesignSystem:
    """SOTA Design System with modern tokens"""
    
    # Typography Scale (Type Scale: 1.125 - Major Second)
    FONT_DISPLAY = ("Segoe UI", 32, "bold")    # Display/Hero
    FONT_H1 = ("Segoe UI", 28, "bold")         # Main headers
    FONT_H2 = ("Segoe UI", 24, "bold")         # Section headers
    FONT_H3 = ("Segoe UI", 20, "bold")         # Subsection headers
    FONT_BODY_LG = ("Segoe UI", 16)            # Large body text
    FONT_BODY = ("Segoe UI", 14)               # Regular body text
    FONT_BODY_SM = ("Segoe UI", 12)            # Small body text
    FONT_CAPTION = ("Segoe UI", 11)            # Captions
    FONT_CODE = ("JetBrains Mono", 12)         # Code/monospace
    
    # Spacing Scale (8px base unit)
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    SPACE_2XL = 48
    SPACE_3XL = 64
    
    # Color System (Modern, accessible palette)
    # Primary Brand Colors
    PRIMARY_50 = "#f0f9ff"
    PRIMARY_100 = "#e0f2fe"
    PRIMARY_500 = "#0ea5e9"    # Main primary
    PRIMARY_600 = "#0284c7"    # Primary hover
    PRIMARY_700 = "#0369a1"    # Primary active
    PRIMARY_900 = "#0c4a6e"    # Primary dark
    
    # Semantic Colors
    SUCCESS_50 = "#f0fdf4"
    SUCCESS_500 = "#22c55e"
    SUCCESS_600 = "#16a34a"
    
    WARNING_50 = "#fffbeb"
    WARNING_500 = "#f59e0b"
    WARNING_600 = "#d97706"
    
    ERROR_50 = "#fef2f2"
    ERROR_500 = "#ef4444"
    ERROR_600 = "#dc2626"
    
    # Neutral Colors (Dark Theme)
    GRAY_50 = "#f9fafb"
    GRAY_100 = "#f3f4f6"
    GRAY_200 = "#e5e7eb"
    GRAY_300 = "#d1d5db"
    GRAY_400 = "#9ca3af"
    GRAY_500 = "#6b7280"
    GRAY_600 = "#4b5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1f2937"
    GRAY_900 = "#111827"
    GRAY_950 = "#030712"
    
    # Dark Theme Surface Colors
    BG_PRIMARY = "#0f172a"      # Main background
    BG_SECONDARY = "#1e293b"    # Card backgrounds
    BG_TERTIARY = "#334155"     # Elevated surfaces
    
    # Text Colors
    TEXT_PRIMARY = "#f8fafc"    # Main text
    TEXT_SECONDARY = "#cbd5e1"  # Secondary text
    TEXT_MUTED = "#64748b"      # Muted text
    
    # Border and Shadow
    BORDER_COLOR = "#334155"
    SHADOW_SM = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgb(0 0 0 / 0.1)"
    
    # Border Radius
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16

class ModernCard(tk.Frame):
    """Modern card component with proper elevation"""
    
    def __init__(self, parent, padding=None, **kwargs):
        padding = padding or DesignSystem.SPACE_LG
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, relief="flat", **kwargs)
        
        # Inner content frame with padding
        self.content_frame = tk.Frame(self, bg=DesignSystem.BG_SECONDARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

class ModernButton(tk.Button):
    """Modern button with proper states and variants"""
    
    def __init__(self, parent, text="", variant="primary", size="md", icon="", **kwargs):
        # Button configurations
        variants = {
            "primary": {
                "bg": DesignSystem.PRIMARY_500,
                "fg": "white",
                "activebackground": DesignSystem.PRIMARY_600,
                "relief": "flat",
                "borderwidth": 0
            },
            "secondary": {
                "bg": DesignSystem.BG_TERTIARY,
                "fg": DesignSystem.TEXT_PRIMARY,
                "activebackground": DesignSystem.GRAY_600,
                "relief": "flat",
                "borderwidth": 0
            },
            "success": {
                "bg": DesignSystem.SUCCESS_500,
                "fg": "white",
                "activebackground": DesignSystem.SUCCESS_600,
                "relief": "flat",
                "borderwidth": 0
            },
            "danger": {
                "bg": DesignSystem.ERROR_500,
                "fg": "white",
                "activebackground": DesignSystem.ERROR_600,
                "relief": "flat",
                "borderwidth": 0
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
            **variant_config,
            **size_config,
            **kwargs
        )

class ProgressBar(tk.Frame):
    """Modern progress bar with animations"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_PRIMARY, **kwargs)
        
        # Progress track
        self.track = tk.Frame(self, bg=DesignSystem.GRAY_700, height=8)
        self.track.pack(fill=tk.X, pady=DesignSystem.SPACE_SM)
        
        # Progress fill
        self.fill = tk.Frame(self.track, bg=DesignSystem.PRIMARY_500, height=8)
        self.fill.place(x=0, y=0, relheight=1, width=0)
        
    def set_progress(self, percentage):
        """Set progress percentage (0-100)"""
        self.fill.place(relwidth=percentage/100)

class StatusIndicator(tk.Frame):
    """Modern status indicator with colors and icons"""
    
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

class TaskCard(ModernCard):
    """Individual task card with progress tracking"""
    
    def __init__(self, parent, task_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.task_data = task_data
        self.status = "pending"  # pending, running, completed, error
        
        # Task header
        header_frame = tk.Frame(self.content_frame, bg=DesignSystem.BG_SECONDARY)
        header_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_SM))
        
        # Task title
        self.title_label = tk.Label(
            header_frame,
            text=task_data.get("title", "Untitled Task"),
            font=DesignSystem.FONT_H3,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY,
            anchor="w"
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Task status
        self.status_indicator = StatusIndicator(header_frame)
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Task description
        if task_data.get("description"):
            self.desc_label = tk.Label(
                self.content_frame,
                text=task_data["description"],
                font=DesignSystem.FONT_BODY,
                fg=DesignSystem.TEXT_SECONDARY,
                bg=DesignSystem.BG_SECONDARY,
                anchor="w",
                justify="left",
                wraplength=400
            )
            self.desc_label.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_SM))
        
        # Progress bar
        self.progress = ProgressBar(self.content_frame)
        self.progress.pack(fill=tk.X)
        
    def set_status(self, status, progress=None):
        """Update task status and progress"""
        self.status = status
        
        status_map = {
            "pending": ("idle", "Pending"),
            "running": ("working", "Running..."),
            "completed": ("success", "Completed"),
            "error": ("error", "Error")
        }
        
        icon_status, text = status_map.get(status, ("idle", "Unknown"))
        self.status_indicator.set_status(icon_status, text)
        
        if progress is not None:
            self.progress.set_progress(progress)

class LogViewer(tk.Frame):
    """Modern log viewer with syntax highlighting"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, **kwargs)
        
        # Log text area with scrollbar
        self.text_frame = tk.Frame(self, bg=DesignSystem.BG_SECONDARY)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_MD, pady=DesignSystem.SPACE_MD)
        
        self.text_area = tk.Text(
            self.text_frame,
            bg=DesignSystem.GRAY_900,
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

class NightWriterModern:
    """Modern Night Writer GUI with SOTA design"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 Night Writer")
        self.root.geometry("1400x900")
        self.root.configure(bg=DesignSystem.BG_PRIMARY)
        
        # Application state
        self.tasks = []
        self.current_task_index = 0
        self.is_running = False
        self.gui_queue = queue.Queue()
        
        # Initialize automation system
        self.automation_system = InGUIAutomationSystem(
            progress_callback=self.handle_progress_update,
            log_callback=self.handle_log_message
        )
        
        self.setup_gui()
        self.check_queue()
        
    def setup_gui(self):
        """Setup the modern GUI layout"""
        # Main container with proper spacing
        main_container = tk.Frame(self.root, bg=DesignSystem.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_LG, pady=DesignSystem.SPACE_LG)
        
        # Header section
        self.setup_header(main_container)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=DesignSystem.BG_PRIMARY)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(DesignSystem.SPACE_LG, 0))
        
        # Left panel - Task configuration
        left_panel = tk.Frame(content_frame, bg=DesignSystem.BG_PRIMARY, width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, DesignSystem.SPACE_LG))
        left_panel.pack_propagate(False)
        
        # Right panel - Execution and monitoring
        right_panel = tk.Frame(content_frame, bg=DesignSystem.BG_PRIMARY)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup panels
        self.setup_configuration_panel(left_panel)
        self.setup_execution_panel(right_panel)
        
    def setup_header(self, parent):
        """Setup modern header with branding"""
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
            text="Modern Task Automation Suite",
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
        """Setup task configuration panel"""
        # Configuration card
        config_card = ModernCard(parent)
        config_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        # Section title
        tk.Label(
            config_card.content_frame,
            text="📋 Task Configuration",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Tasks file selection
        file_frame = tk.Frame(config_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        file_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        tk.Label(
            file_frame,
            text="Tasks File:",
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W)
        
        file_input_frame = tk.Frame(file_frame, bg=DesignSystem.BG_SECONDARY)
        file_input_frame.pack(fill=tk.X, pady=(DesignSystem.SPACE_SM, 0))
        
        self.tasks_file_var = tk.StringVar(value="sample_tasks.json")
        self.tasks_file_entry = tk.Entry(
            file_input_frame,
            textvariable=self.tasks_file_var,
            font=DesignSystem.FONT_BODY,
            bg=DesignSystem.GRAY_800,
            fg=DesignSystem.TEXT_PRIMARY,
            relief="flat",
            borderwidth=0
        )
        self.tasks_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, DesignSystem.SPACE_SM))
        
        ModernButton(
            file_input_frame,
            text="Browse",
            size="sm",
            variant="secondary",
            command=self.browse_tasks_file
        ).pack(side=tk.RIGHT)
        
        # Load tasks button
        ModernButton(
            config_card.content_frame,
            text="🔄 Load Tasks",
            size="md",
            variant="secondary",
            command=self.load_tasks
        ).pack(pady=(DesignSystem.SPACE_LG, 0))
        
        # Tasks preview card
        self.tasks_card = ModernCard(parent)
        self.tasks_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            self.tasks_card.content_frame,
            text="📝 Tasks Preview",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Scrollable tasks container
        self.tasks_scroll_frame = tk.Frame(self.tasks_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        self.tasks_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
    def setup_execution_panel(self, parent):
        """Setup execution monitoring panel"""
        # Control buttons
        control_card = ModernCard(parent)
        control_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        tk.Label(
            control_card.content_frame,
            text="🎯 Execution Control",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        button_frame = tk.Frame(control_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ModernButton(
            button_frame,
            text="🚀 Start Execution",
            size="lg",
            variant="primary",
            command=self.start_execution
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_MD))
        
        self.stop_button = ModernButton(
            button_frame,
            text="⏹️ Stop",
            size="lg",
            variant="danger",
            command=self.stop_execution,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # Progress overview
        progress_card = ModernCard(parent)
        progress_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        tk.Label(
            progress_card.content_frame,
            text="📊 Progress Overview",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        self.overall_progress = ProgressBar(progress_card.content_frame)
        self.overall_progress.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        self.progress_label = tk.Label(
            progress_card.content_frame,
            text="0 of 0 tasks completed",
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_SECONDARY
        )
        self.progress_label.pack()
        
        # Log viewer
        log_card = ModernCard(parent)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_card.content_frame,
            text="📋 Execution Log",
            font=DesignSystem.FONT_H2,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        ).pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        self.log_viewer = LogViewer(log_card.content_frame)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
    def browse_tasks_file(self):
        """Browse for tasks file"""
        filename = filedialog.askopenfilename(
            title="Select Tasks File",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.tasks_file_var.set(filename)
            
    def load_tasks(self):
        """Load tasks from file"""
        try:
            tasks_file = self.tasks_file_var.get()
            if not Path(tasks_file).exists():
                messagebox.showerror("Error", f"Tasks file not found: {tasks_file}")
                return
                
            with open(tasks_file, 'r') as f:
                self.tasks = json.load(f)
                
            self.display_tasks()
            self.log_viewer.add_log(f"Loaded {len(self.tasks)} tasks from {tasks_file}", "SUCCESS")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
            self.log_viewer.add_log(f"Error loading tasks: {str(e)}", "ERROR")
            
    def display_tasks(self):
        """Display loaded tasks in the preview"""
        # Clear existing task widgets
        for widget in self.tasks_scroll_frame.winfo_children():
            widget.destroy()
            
        self.task_cards = []
        for i, task in enumerate(self.tasks):
            task_card = TaskCard(self.tasks_scroll_frame, task)
            task_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
            self.task_cards.append(task_card)
            
    def start_execution(self):
        """Start task execution"""
        if not self.tasks:
            messagebox.showwarning("No Tasks", "Please load tasks first.")
            return
            
        self.is_running = True
        self.current_task_index = 0
        
        # Update UI state
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.main_status.set_status("working", "Executing tasks...")
        
        # Load tasks into automation system and start
        self.automation_system.tasks = self.tasks
        self.automation_system.start_execution()
        
        self.log_viewer.add_log("Starting task execution...", "INFO")
        
    def stop_execution(self):
        """Stop task execution"""
        self.is_running = False
        self.automation_system.stop_execution()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.main_status.set_status("idle", "Execution stopped")
        self.log_viewer.add_log("Execution stopped by user", "WARNING")
        
    def handle_progress_update(self, event_type: str, task_index: int, data):
        """Handle progress updates from automation system"""
        # Use queue to ensure thread safety
        self.gui_queue.put((event_type, task_index, data))
        
    def handle_log_message(self, message: str, level: str):
        """Handle log messages from automation system"""
        self.gui_queue.put(("log", message, level))
            
    def check_queue(self):
        """Check GUI queue for updates from background thread"""
        try:
            while True:
                event, data, extra = self.gui_queue.get_nowait()
                
                if event == "start_task":
                    if data < len(self.task_cards):
                        self.task_cards[data].set_status("running", 0)
                elif event == "task_progress":
                    if data < len(self.task_cards):
                        self.task_cards[data].set_status("running", extra)
                elif event == "complete_task":
                    if data < len(self.task_cards):
                        self.task_cards[data].set_status("completed", 100)
                    self.update_overall_progress()
                elif event == "error_task":
                    if data < len(self.task_cards):
                        self.task_cards[data].set_status("error", 100)
                    self.update_overall_progress()
                elif event == "log":
                    self.log_viewer.add_log(data, extra)
                elif event == "execution_complete":
                    self.execution_finished(success=True, completed=data, total=extra)
                elif event == "execution_error":
                    self.execution_finished(success=False)
                    
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.check_queue)
        
    def update_overall_progress(self):
        """Update overall progress bar and label"""
        if not self.tasks:
            return
            
        completed = sum(1 for card in self.task_cards if card.status == "completed")
        failed = sum(1 for card in self.task_cards if card.status == "error")
        total = len(self.tasks)
        progress = ((completed + failed) / total) * 100
        
        self.overall_progress.set_progress(progress)
        if failed > 0:
            self.progress_label.config(text=f"{completed} completed, {failed} failed of {total} tasks")
        else:
            self.progress_label.config(text=f"{completed} of {total} tasks completed")
        
    def execution_finished(self, success=True, completed=None, total=None):
        """Handle execution completion"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if success and completed is not None and total is not None:
            self.main_status.set_status("success", f"Execution completed! {completed}/{total} successful")
            self.log_viewer.add_log(f"Execution completed: {completed} of {total} tasks successful", "SUCCESS")
        elif success:
            self.main_status.set_status("success", "All tasks completed!")
            self.log_viewer.add_log("All tasks completed successfully!", "SUCCESS")
        else:
            self.main_status.set_status("error", "Execution failed")
            self.log_viewer.add_log("Execution failed", "ERROR")

def main():
    root = tk.Tk()
    app = NightWriterModern(root)
    root.mainloop()

if __name__ == "__main__":
    main()