#!/usr/bin/env python3
"""
🌙 Night Writer GUI - SOTA Design Implementation

A state-of-the-art graphical interface following modern design principles:
- Clean, minimalist layout with proper visual hierarchy
- Card-based design system with consistent spacing
- Clear workflow progression with numbered steps
- Prominent call-to-action buttons
- Professional color palette and typography
- Smooth animations and micro-interactions

Author: João Panizzutti
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

# Import our automation system
from terminal_automation import (
    TerminalAutomationSystem, Configuration, TerminalType, 
    TerminalConnectionMode, TerminalWindowManager
)


class DesignSystem:
    """Modern design system with consistent tokens"""
    
    # Spacing scale (8px base unit)
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    SPACE_XXL = 48
    SPACE_XXXL = 64
    
    # Typography scale
    FONT_DISPLAY = ("Segoe UI", 28, "bold")
    FONT_H1 = ("Segoe UI", 24, "bold")
    FONT_H2 = ("Segoe UI", 18, "bold")
    FONT_H3 = ("Segoe UI", 16, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_CAPTION = ("Segoe UI", 10)
    FONT_CODE = ("JetBrains Mono", 10)
    
    # Modern color palette
    PRIMARY = "#6366f1"        # Indigo
    PRIMARY_HOVER = "#4f46e5"
    PRIMARY_LIGHT = "#a5b4fc"
    
    SUCCESS = "#10b981"        # Emerald
    SUCCESS_LIGHT = "#6ee7b7"
    
    WARNING = "#f59e0b"        # Amber
    WARNING_LIGHT = "#fcd34d"
    
    DANGER = "#ef4444"         # Red
    DANGER_LIGHT = "#fca5a5"
    
    # Neutral colors
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
    
    # Dark theme colors
    BG_PRIMARY = "#0f172a"     # Slate 900
    BG_SECONDARY = "#1e293b"   # Slate 800
    BG_TERTIARY = "#334155"    # Slate 700
    
    TEXT_PRIMARY = "#f8fafc"   # Slate 50
    TEXT_SECONDARY = "#cbd5e1" # Slate 300
    TEXT_MUTED = "#64748b"     # Slate 500
    
    # Elevation shadows
    SHADOW_SM = "#D0D0D0"
    SHADOW_MD = "#B0B0B0"
    SHADOW_LG = "#909090"
    
    # Border radius
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16


class ModernButton(tk.Canvas):
    """Modern button component with SOTA design"""
    
    def __init__(self, parent, text, command=None, variant="primary", size="md", icon=None, **kwargs):
        # Size configurations
        sizes = {
            "sm": {"width": 120, "height": 36, "font": DesignSystem.FONT_CAPTION, "padding": 12},
            "md": {"width": 160, "height": 44, "font": DesignSystem.FONT_BODY_BOLD, "padding": 16},
            "lg": {"width": 200, "height": 52, "font": DesignSystem.FONT_H3, "padding": 20},
            "xl": {"width": 280, "height": 60, "font": DesignSystem.FONT_H2, "padding": 24}
        }
        
        size_config = sizes[size]
        super().__init__(parent, width=size_config["width"], height=size_config["height"], 
                        highlightthickness=0, **kwargs)
        
        self.text = text
        self.icon = icon
        self.command = command
        self.variant = variant
        self.size_config = size_config
        self.state = "normal"  # normal, hover, active, disabled
        
        # Variant configurations
        self.variants = {
            "primary": {
                "bg": DesignSystem.PRIMARY,
                "bg_hover": DesignSystem.PRIMARY_HOVER,
                "text": DesignSystem.TEXT_PRIMARY,
                "border": DesignSystem.PRIMARY
            },
            "secondary": {
                "bg": DesignSystem.BG_TERTIARY,
                "bg_hover": DesignSystem.GRAY_600,
                "text": DesignSystem.TEXT_PRIMARY,
                "border": DesignSystem.GRAY_600
            },
            "success": {
                "bg": DesignSystem.SUCCESS,
                "bg_hover": "#059669",
                "text": DesignSystem.TEXT_PRIMARY,
                "border": DesignSystem.SUCCESS
            },
            "danger": {
                "bg": DesignSystem.DANGER,
                "bg_hover": "#dc2626",
                "text": DesignSystem.TEXT_PRIMARY,
                "border": DesignSystem.DANGER
            }
        }
        
        self.configure(bg=DesignSystem.BG_PRIMARY)
        self.draw_button()
        self.bind_events()
        
    def draw_button(self):
        """Draw button with current state"""
        self.delete("all")
        
        variant_config = self.variants[self.variant]
        
        # Determine colors based on state
        if self.state == "disabled":
            bg_color = DesignSystem.GRAY_700
            text_color = DesignSystem.TEXT_MUTED
        elif self.state == "hover":
            bg_color = variant_config["bg_hover"]
            text_color = variant_config["text"]
        else:
            bg_color = variant_config["bg"]
            text_color = variant_config["text"]
        
        # Draw rounded rectangle
        self.create_rounded_rect(
            2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2,
            radius=DesignSystem.RADIUS_MD,
            fill=bg_color,
            outline=""
        )
        
        # Add subtle shadow for depth
        if self.state != "disabled":
            self.create_rounded_rect(
                0, 4, self.winfo_reqwidth(), self.winfo_reqheight()+2,
                radius=DesignSystem.RADIUS_MD,
                fill=DesignSystem.SHADOW_SM,
                outline=""
            )
            # Move main button on top
            self.tag_lower("all")
            self.create_rounded_rect(
                2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2,
                radius=DesignSystem.RADIUS_MD,
                fill=bg_color,
                outline=""
            )
        
        # Draw text with icon
        text_y = self.winfo_reqheight() // 2
        if self.icon:
            full_text = f"{self.icon} {self.text}"
        else:
            full_text = self.text
            
        self.create_text(
            self.winfo_reqwidth() // 2, text_y,
            text=full_text,
            fill=text_color,
            font=self.size_config["font"]
        )
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=8, **kwargs):
        """Create rounded rectangle"""
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def bind_events(self):
        """Bind interaction events"""
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, event):
        if self.state != "disabled":
            self.state = "hover"
            self.draw_button()
            self.config(cursor="hand2")
        
    def on_leave(self, event):
        if self.state != "disabled":
            self.state = "normal"
            self.draw_button()
            self.config(cursor="")
        
    def on_click(self, event):
        if self.state != "disabled" and self.command:
            self.command()
            
    def configure_state(self, state):
        """Configure button state"""
        self.state = state
        self.draw_button()


class ModernCard(tk.Frame):
    """Modern card component with proper elevation"""
    
    def __init__(self, parent, title="", subtitle="", **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, **kwargs)
        
        # Configure card styling
        self.configure(
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=DesignSystem.GRAY_700,
            highlightcolor=DesignSystem.PRIMARY
        )
        
        # Add padding frame
        self.content_frame = tk.Frame(self, bg=DesignSystem.BG_SECONDARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_LG, 
                               pady=DesignSystem.SPACE_LG)
        
        if title:
            self.setup_header(title, subtitle)
            
    def setup_header(self, title, subtitle=""):
        """Setup card header"""
        header_frame = tk.Frame(self.content_frame, bg=DesignSystem.BG_SECONDARY)
        header_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=title,
            font=DesignSystem.FONT_H3,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        )
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        if subtitle:
            subtitle_label = tk.Label(
                header_frame,
                text=subtitle,
                font=DesignSystem.FONT_BODY,
                fg=DesignSystem.TEXT_SECONDARY,
                bg=DesignSystem.BG_SECONDARY
            )
            subtitle_label.pack(anchor=tk.W, pady=(DesignSystem.SPACE_XS, 0))


class WorkflowStep(tk.Frame):
    """Workflow step component with number indicator"""
    
    def __init__(self, parent, step_number, title, description, **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_PRIMARY, **kwargs)
        
        # Main container
        container = tk.Frame(self, bg=DesignSystem.BG_PRIMARY)
        container.pack(fill=tk.X, pady=DesignSystem.SPACE_SM)
        
        # Step number circle
        number_frame = tk.Frame(container, bg=DesignSystem.BG_PRIMARY, width=40, height=40)
        number_frame.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_MD))
        number_frame.pack_propagate(False)
        
        # Create circular number indicator
        self.number_canvas = tk.Canvas(
            number_frame, width=32, height=32,
            bg=DesignSystem.BG_PRIMARY, highlightthickness=0
        )
        self.number_canvas.pack(expand=True)
        
        # Draw circle
        self.number_canvas.create_oval(
            2, 2, 30, 30,
            fill=DesignSystem.PRIMARY,
            outline=""
        )
        
        # Add number
        self.number_canvas.create_text(
            16, 16,
            text=str(step_number),
            fill=DesignSystem.TEXT_PRIMARY,
            font=DesignSystem.FONT_BODY_BOLD
        )
        
        # Content area
        content_frame = tk.Frame(container, bg=DesignSystem.BG_PRIMARY)
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=title,
            font=DesignSystem.FONT_H3,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_PRIMARY
        )
        title_label.pack(anchor=tk.W)
        
        # Description
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_PRIMARY,
            wraplength=400
        )
        desc_label.pack(anchor=tk.W, pady=(DesignSystem.SPACE_XS, 0))
        
    def set_completed(self, completed=True):
        """Mark step as completed"""
        if completed:
            self.number_canvas.delete("all")
            self.number_canvas.create_oval(
                2, 2, 30, 30,
                fill=DesignSystem.SUCCESS,
                outline=""
            )
            self.number_canvas.create_text(
                16, 16,
                text="✓",
                fill=DesignSystem.TEXT_PRIMARY,
                font=DesignSystem.FONT_BODY_BOLD
            )


class StatusBar(tk.Frame):
    """Modern status bar with indicator"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=DesignSystem.BG_SECONDARY, height=60, **kwargs)
        self.pack_propagate(False)
        
        # Container with padding
        container = tk.Frame(self, bg=DesignSystem.BG_SECONDARY)
        container.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_LG, 
                      pady=DesignSystem.SPACE_MD)
        
        # Status indicator
        self.indicator_canvas = tk.Canvas(
            container, width=12, height=12,
            bg=DesignSystem.BG_SECONDARY, highlightthickness=0
        )
        self.indicator_canvas.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_MD))
        
        # Status text
        self.status_var = tk.StringVar(value="Ready to start automation")
        self.status_label = tk.Label(
            container,
            textvariable=self.status_var,
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.set_status("idle")
        
    def set_status(self, status, message=None):
        """Update status indicator and message"""
        colors = {
            "idle": DesignSystem.GRAY_500,
            "working": DesignSystem.PRIMARY,
            "success": DesignSystem.SUCCESS,
            "error": DesignSystem.DANGER
        }
        
        # Update indicator
        self.indicator_canvas.delete("all")
        self.indicator_canvas.create_oval(
            2, 2, 10, 10,
            fill=colors.get(status, DesignSystem.GRAY_500),
            outline=""
        )
        
        # Update message if provided
        if message:
            self.status_var.set(message)


class NightWriterGUI:
    """🌙 SOTA Night Writer GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 Night Writer - Premium Terminal Automation")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(bg=DesignSystem.BG_PRIMARY)
        
        # Application state
        self.automation_system: Optional[TerminalAutomationSystem] = None
        self.automation_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.config = Configuration()
        self.selected_window: Optional[Dict[str, Any]] = None
        self.project_path = ""
        self.tasks_file = "tasks.txt"
        
        # GUI update queue
        self.gui_queue = queue.Queue()
        
        self.setup_gui()
        self.setup_logging()
        self.refresh_windows()
        
        # Start GUI update loop
        self.root.after(100, self.process_gui_queue)
        
    def setup_gui(self):
        """Setup the SOTA GUI layout"""
        # Main container with proper spacing
        main_container = tk.Frame(self.root, bg=DesignSystem.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=DesignSystem.SPACE_XXXL, 
                           pady=DesignSystem.SPACE_XL)
        
        # Header section
        self.setup_header(main_container)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=DesignSystem.BG_PRIMARY)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(DesignSystem.SPACE_XL, 0))
        
        # Left panel - Workflow (wider for better UX)
        left_panel = tk.Frame(content_frame, bg=DesignSystem.BG_PRIMARY, width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, DesignSystem.SPACE_LG))
        left_panel.pack_propagate(False)
        
        # Right panel - Monitoring
        right_panel = tk.Frame(content_frame, bg=DesignSystem.BG_PRIMARY)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, 
                        padx=(DesignSystem.SPACE_LG, 0))
        
        # Setup panels
        self.setup_workflow_panel(left_panel)
        self.setup_monitoring_panel(right_panel)
        
    def setup_header(self, parent):
        """Setup modern header with branding and status"""
        header_frame = tk.Frame(parent, bg=DesignSystem.BG_PRIMARY, height=100)
        header_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_XL))
        header_frame.pack_propagate(False)
        
        # Title section
        title_frame = tk.Frame(header_frame, bg=DesignSystem.BG_PRIMARY)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(
            title_frame,
            text="🌙 Night Writer",
            font=DesignSystem.FONT_DISPLAY,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_PRIMARY
        )
        title_label.pack(anchor=tk.W, pady=(DesignSystem.SPACE_MD, 0))
        
        subtitle_label = tk.Label(
            title_frame,
            text="Premium Terminal Automation Suite",
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_PRIMARY
        )
        subtitle_label.pack(anchor=tk.W)
        
        # Start button in header for visibility
        button_frame = tk.Frame(header_frame, bg=DesignSystem.BG_PRIMARY)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=DesignSystem.SPACE_LG)
        
        self.header_start_btn = ModernButton(
            button_frame,
            text="🚀 START AUTOMATION",
            command=self.start_automation,
            variant="primary",
            size="lg"
        )
        self.header_start_btn.pack(pady=DesignSystem.SPACE_MD)
        
        # Status section
        status_frame = tk.Frame(header_frame, bg=DesignSystem.BG_PRIMARY)
        status_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(DesignSystem.SPACE_XL, 0))
        
        self.status_bar = StatusBar(status_frame)
        self.status_bar.pack(expand=True)
        
    def setup_workflow_panel(self, parent):
        """Setup workflow panel with clear steps"""
        # Workflow title
        workflow_title = tk.Label(
            parent,
            text="🚀 Automation Workflow",
            font=DesignSystem.FONT_H1,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_PRIMARY
        )
        workflow_title.pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Step 1: Terminal Selection
        self.step1 = WorkflowStep(
            parent, 1,
            "Select Terminal Window",
            "Choose an existing terminal window to automate"
        )
        self.step1.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        # Terminal selection card
        terminal_card = ModernCard(parent)
        terminal_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        # Terminal listbox with modern styling
        listbox_frame = tk.Frame(terminal_card.content_frame, bg=DesignSystem.BG_TERTIARY, 
                                relief="flat", bd=1)
        listbox_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        self.window_listbox = tk.Listbox(
            listbox_frame,
            font=DesignSystem.FONT_BODY,
            height=4,
            bg=DesignSystem.BG_TERTIARY,
            fg=DesignSystem.TEXT_PRIMARY,
            selectbackground=DesignSystem.PRIMARY,
            selectforeground=DesignSystem.TEXT_PRIMARY,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.window_listbox.pack(fill=tk.X, padx=DesignSystem.SPACE_MD, 
                                pady=DesignSystem.SPACE_MD)
        self.window_listbox.bind('<<ListboxSelect>>', self.on_window_select)
        
        # Refresh button
        refresh_btn = ModernButton(
            terminal_card.content_frame,
            text="Refresh Windows",
            icon="🔄",
            command=self.refresh_windows,
            variant="secondary",
            size="md"
        )
        refresh_btn.pack()
        
        # Step 2: Project Configuration
        self.step2 = WorkflowStep(
            parent, 2,
            "Configure Project",
            "Set your project folder and tasks file"
        )
        self.step2.pack(fill=tk.X, pady=(DesignSystem.SPACE_LG, DesignSystem.SPACE_MD))
        
        # Project configuration card
        project_card = ModernCard(parent)
        project_card.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_LG))
        
        # Project path
        self.setup_input_field(
            project_card.content_frame,
            "Project Directory (Optional):",
            "Select your project folder",
            self.browse_project,
            "📁 Browse"
        )
        
        # Tasks file
        self.tasks_entry = self.setup_input_field(
            project_card.content_frame,
            "Tasks File:",
            "tasks.txt",
            self.browse_tasks,
            "📄 Select"
        )
        
        # Step 3: Start Automation
        self.step3 = WorkflowStep(
            parent, 3,
            "Start Automation",
            "Begin the automated terminal workflow"
        )
        self.step3.pack(fill=tk.X, pady=(DesignSystem.SPACE_LG, DesignSystem.SPACE_MD))
        
        # Action buttons card
        action_card = ModernCard(parent)
        action_card.pack(fill=tk.X)
        
        # Button container
        button_frame = tk.Frame(action_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        button_frame.pack(fill=tk.X, pady=DesignSystem.SPACE_MD)
        
        # Primary action button (LARGE and prominent)
        self.start_btn = ModernButton(
            button_frame,
            text="Start Automation",
            icon="🚀",
            command=self.start_automation,
            variant="primary",
            size="xl"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_MD))
        
        # Secondary buttons
        self.stop_btn = ModernButton(
            button_frame,
            text="Stop",
            icon="⏹️",
            command=self.stop_automation,
            variant="danger",
            size="md"
        )
        self.stop_btn.configure_state("disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_MD))
        
        settings_btn = ModernButton(
            button_frame,
            text="Settings",
            icon="⚙️",
            command=self.show_settings,
            variant="secondary",
            size="md"
        )
        settings_btn.pack(side=tk.RIGHT)
        
    def setup_input_field(self, parent, label_text, placeholder, browse_command, button_text):
        """Setup modern input field with label and button"""
        # Container
        field_frame = tk.Frame(parent, bg=DesignSystem.BG_SECONDARY)
        field_frame.pack(fill=tk.X, pady=(0, DesignSystem.SPACE_MD))
        
        # Label
        label = tk.Label(
            field_frame,
            text=label_text,
            font=DesignSystem.FONT_BODY_BOLD,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_SECONDARY
        )
        label.pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_XS))
        
        # Input row
        input_row = tk.Frame(field_frame, bg=DesignSystem.BG_SECONDARY)
        input_row.pack(fill=tk.X)
        
        # Entry field
        entry = tk.Entry(
            input_row,
            font=DesignSystem.FONT_BODY,
            bg=DesignSystem.BG_TERTIARY,
            fg=DesignSystem.TEXT_PRIMARY,
            insertbackground=DesignSystem.PRIMARY,
            bd=0,
            highlightthickness=1,
            highlightcolor=DesignSystem.PRIMARY,
            highlightbackground=DesignSystem.GRAY_600
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, DesignSystem.SPACE_MD),
                  ipady=DesignSystem.SPACE_SM)
        entry.insert(0, placeholder)
        
        # Browse button
        browse_btn = ModernButton(
            input_row,
            text=button_text.split()[-1],  # Just the action word
            icon=button_text.split()[0],   # Just the emoji
            command=browse_command,
            variant="secondary",
            size="sm"
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Store reference for project path
        if "Project" in label_text:
            self.path_entry = entry
            
        return entry
        
    def setup_monitoring_panel(self, parent):
        """Setup monitoring panel with live logs"""
        # Panel title
        monitor_title = tk.Label(
            parent,
            text="📊 Live Activity Monitor",
            font=DesignSystem.FONT_H1,
            fg=DesignSystem.TEXT_PRIMARY,
            bg=DesignSystem.BG_PRIMARY
        )
        monitor_title.pack(anchor=tk.W, pady=(0, DesignSystem.SPACE_LG))
        
        # Monitoring card
        monitor_card = ModernCard(parent)
        monitor_card.pack(fill=tk.BOTH, expand=True)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            monitor_card.content_frame,
            wrap=tk.WORD,
            font=DesignSystem.FONT_CODE,
            bg=DesignSystem.GRAY_900,
            fg=DesignSystem.TEXT_SECONDARY,
            insertbackground=DesignSystem.PRIMARY,
            selectbackground=DesignSystem.PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=DesignSystem.PRIMARY,
            highlightbackground=DesignSystem.GRAY_700
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, DesignSystem.SPACE_MD))
        
        # Log controls
        controls_frame = tk.Frame(monitor_card.content_frame, bg=DesignSystem.BG_SECONDARY)
        controls_frame.pack(fill=tk.X)
        
        clear_btn = ModernButton(
            controls_frame,
            text="Clear",
            icon="🗑️",
            command=self.clear_logs,
            variant="secondary",
            size="sm"
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, DesignSystem.SPACE_SM))
        
        export_btn = ModernButton(
            controls_frame,
            text="Export",
            icon="💾",
            command=self.save_logs,
            variant="secondary",
            size="sm"
        )
        export_btn.pack(side=tk.LEFT)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_cb = tk.Checkbutton(
            controls_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            font=DesignSystem.FONT_BODY,
            fg=DesignSystem.TEXT_SECONDARY,
            bg=DesignSystem.BG_SECONDARY,
            selectcolor=DesignSystem.BG_TERTIARY,
            activebackground=DesignSystem.BG_SECONDARY,
            activeforeground=DesignSystem.TEXT_PRIMARY,
            bd=0,
            highlightthickness=0
        )
        auto_scroll_cb.pack(side=tk.RIGHT)
        
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Advanced settings panel coming soon!")
        
    def setup_logging(self):
        """Setup logging system"""
        self.log_handler = GUILogHandler(self.gui_queue)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
        
    def refresh_windows(self):
        """Refresh terminal windows list"""
        try:
            window_manager = TerminalWindowManager()
            windows = window_manager.find_terminal_windows()
            
            self.window_listbox.delete(0, tk.END)
            self.windows_data = windows
            
            for window in windows:
                display_text = f"🖥️ {window['title']} ({window['process_name']})"
                self.window_listbox.insert(tk.END, display_text)
                
            if windows:
                self.status_bar.set_status("success", f"Found {len(windows)} terminal windows")
                self.step1.set_completed(False)  # Reset until user selects
            else:
                self.status_bar.set_status("error", "No terminal windows found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh windows: {e}")
            self.status_bar.set_status("error", "Error scanning terminals")
            
    def on_window_select(self, event):
        """Handle window selection"""
        selection = self.window_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_window = self.windows_data[index]
            window_title = self.selected_window['title']
            self.status_bar.set_status("success", f"✓ Selected: {window_title}")
            self.step1.set_completed(True)
            
    def browse_project(self):
        """Browse for project folder"""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
            self.project_path = folder
            self.step2.set_completed(True)
            
    def browse_tasks(self):
        """Browse for tasks file"""
        file_path = filedialog.askopenfilename(
            title="Select Tasks File",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.tasks_entry.delete(0, tk.END)
            self.tasks_entry.insert(0, file_path)
            self.tasks_file = file_path
            
    def create_config(self) -> Configuration:
        """Create configuration for existing window mode"""
        config = Configuration()
        config.tasks_file = self.tasks_entry.get() or "tasks.txt"
        config.terminal_type = TerminalType.POWERSHELL
        config.connection_mode = TerminalConnectionMode.EXISTING_WINDOW
        config.auto_launch_claude = True
        config.transcript_enabled = True
        config.inactivity_timeout = 600
        config.timezone = "America/Sao_Paulo"
        config.log_level = "INFO"
        config.gui_mode = False
        return config
        
    def start_automation(self):
        """Start automation process"""
        if not self.selected_window:
            messagebox.showwarning("Selection Required", 
                                 "Please select a terminal window first.")
            return
            
        try:
            # Create and configure automation system
            self.config = self.create_config()
            self.automation_system = TerminalAutomationSystem(self.config)
            
            # Configure for existing window
            self.automation_system.terminal_manager.selected_window = self.selected_window
            self.automation_system.terminal_manager._is_existing_window = True
            
            # Set project directory
            project_path = self.path_entry.get() or str(Path.cwd())
            self.automation_system._initial_project_dir = project_path
            self.automation_system.terminal_manager.initial_working_dir = project_path
            self.automation_system._auto_open_claude = True
            
            # Load tasks
            if not self.automation_system.load_tasks(self.config.tasks_file):
                messagebox.showerror("Error", "Failed to load tasks file")
                return
                
            # Update UI state
            self.is_running = True
            self.start_btn.configure_state("disabled")
            self.stop_btn.configure_state("normal")
            self.status_bar.set_status("working", "🚀 Starting automation...")
            self.step3.set_completed(True)
            
            # Start automation thread
            self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
            self.automation_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {str(e)}")
            self.reset_ui()
            
    def run_automation(self):
        """Run automation in background thread"""
        try:
            self.gui_queue.put(("status", "working", "🔄 Connecting to terminal..."))
            success = self.automation_system.run_session()
            
            if success:
                self.gui_queue.put(("status", "success", "✅ Automation completed"))
            else:
                self.gui_queue.put(("status", "idle", "⏹️ Automation stopped"))
                
        except Exception as e:
            self.gui_queue.put(("status", "error", f"❌ Error: {str(e)}"))
            self.gui_queue.put(("log", f"ERROR: {e}"))
            
        finally:
            self.gui_queue.put(("finished", None, None))
            
    def stop_automation(self):
        """Stop automation"""
        if self.automation_system:
            self.automation_system.terminal_manager.stop_terminal()
            
        self.is_running = False
        self.reset_ui()
        self.status_bar.set_status("idle", "⏹️ Automation stopped")
        
    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_btn.configure_state("normal")
        self.stop_btn.configure_state("disabled")
        self.is_running = False
        
    def process_gui_queue(self):
        """Process GUI update messages"""
        try:
            while True:
                message = self.gui_queue.get_nowait()
                
                if message[0] == "status":
                    self.status_bar.set_status(message[1], message[2])
                elif message[0] == "log":
                    self.add_log(message[1])
                elif message[0] == "finished":
                    self.reset_ui()
                    
        except queue.Empty:
            pass
            
        self.root.after(100, self.process_gui_queue)
        
    def add_log(self, message: str):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        # Color coding
        if "ERROR" in message:
            color = DesignSystem.DANGER
        elif "WARNING" in message:
            color = DesignSystem.WARNING
        elif "INFO" in message:
            color = DesignSystem.PRIMARY_LIGHT
        else:
            color = DesignSystem.TEXT_SECONDARY
            
        # Insert with color
        self.log_text.insert(tk.END, log_line)
        
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
            
    def clear_logs(self):
        """Clear log display"""
        if messagebox.askyesno("Clear Logs", "Clear all log entries?"):
            self.log_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Export logs to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".txt",
            initialname=f"night_writer_logs_{timestamp}.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs:\n{str(e)}")


class GUILogHandler(logging.Handler):
    """Custom logging handler for GUI"""
    
    def __init__(self, gui_queue):
        super().__init__()
        self.gui_queue = gui_queue
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.gui_queue.put(("log", msg))
        except Exception:
            pass


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = NightWriterGUI(root)
    
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Quit", "Stop automation and quit?"):
                app.stop_automation()
                root.destroy()
        else:
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()