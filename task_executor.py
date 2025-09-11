"""
🚀 Task Executor - In-GUI Task Execution Engine
Replaces terminal automation with direct Python execution
"""

import subprocess
import threading
import time
import queue
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Callable

class TaskExecutor:
    """Modern task executor that runs tasks within the GUI application"""
    
    def __init__(self, progress_callback: Callable = None, log_callback: Callable = None):
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_running = False
        self.current_task = None
        
    def log(self, message: str, level: str = "INFO"):
        """Send log message to GUI"""
        if self.log_callback:
            self.log_callback(message, level)
            
    def update_progress(self, task_index: int, progress: int):
        """Update task progress"""
        if self.progress_callback:
            self.progress_callback("task_progress", task_index, progress)
            
    def execute_task(self, task: Dict[str, Any], task_index: int) -> bool:
        """Execute a single task"""
        try:
            self.current_task = task
            task_type = task.get("type", "command")
            
            self.log(f"Executing task: {task.get('title', 'Untitled')}")
            
            if task_type == "command":
                return self.execute_command_task(task, task_index)
            elif task_type == "file_operation":
                return self.execute_file_task(task, task_index)
            elif task_type == "api_call":
                return self.execute_api_task(task, task_index)
            elif task_type == "script":
                return self.execute_script_task(task, task_index)
            else:
                self.log(f"Unknown task type: {task_type}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Task execution failed: {str(e)}", "ERROR")
            return False
            
    def execute_command_task(self, task: Dict[str, Any], task_index: int) -> bool:
        """Execute a command-based task"""
        command = task.get("command", "")
        if not command:
            self.log("No command specified", "ERROR")
            return False
            
        try:
            # Update progress to indicate starting
            self.update_progress(task_index, 10)
            
            # Get working directory
            cwd = task.get("working_directory", os.getcwd())
            
            # Execute command
            self.log(f"Running command: {command}")
            
            # Run command with real-time output capture
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress
            output_lines = []
            error_lines = []
            
            # Read output in real-time
            while True:
                if not self.is_running:
                    process.terminate()
                    return False
                    
                output = process.stdout.readline()
                if output:
                    output_lines.append(output.strip())
                    self.log(f"Output: {output.strip()}")
                    
                    # Update progress based on output length (simple heuristic)
                    progress = min(90, 10 + len(output_lines) * 2)
                    self.update_progress(task_index, progress)
                    
                # Check if process is done
                if process.poll() is not None:
                    break
                    
                time.sleep(0.1)
                
            # Get remaining output
            remaining_output, remaining_error = process.communicate()
            if remaining_output:
                self.log(f"Final output: {remaining_output}")
            if remaining_error:
                self.log(f"Error output: {remaining_error}", "WARNING")
                
            # Update progress to complete
            self.update_progress(task_index, 100)
            
            # Check return code
            if process.returncode == 0:
                self.log("Command executed successfully", "SUCCESS")
                return True
            else:
                self.log(f"Command failed with return code: {process.returncode}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Command execution error: {str(e)}", "ERROR")
            return False
            
    def execute_file_task(self, task: Dict[str, Any], task_index: int) -> bool:
        """Execute a file operation task"""
        operation = task.get("operation", "")
        file_path = task.get("file_path", "")
        
        try:
            self.update_progress(task_index, 20)
            
            if operation == "create":
                content = task.get("content", "")
                with open(file_path, 'w') as f:
                    f.write(content)
                self.log(f"Created file: {file_path}", "SUCCESS")
                
            elif operation == "read":
                with open(file_path, 'r') as f:
                    content = f.read()
                self.log(f"Read file: {file_path} ({len(content)} characters)")
                
            elif operation == "delete":
                os.remove(file_path)
                self.log(f"Deleted file: {file_path}", "SUCCESS")
                
            elif operation == "copy":
                destination = task.get("destination", "")
                import shutil
                shutil.copy2(file_path, destination)
                self.log(f"Copied {file_path} to {destination}", "SUCCESS")
                
            self.update_progress(task_index, 100)
            return True
            
        except Exception as e:
            self.log(f"File operation error: {str(e)}", "ERROR")
            return False
            
    def execute_api_task(self, task: Dict[str, Any], task_index: int) -> bool:
        """Execute an API call task"""
        try:
            import requests
            
            url = task.get("url", "")
            method = task.get("method", "GET")
            headers = task.get("headers", {})
            data = task.get("data", {})
            
            self.update_progress(task_index, 30)
            
            self.log(f"Making {method} request to {url}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                self.log(f"Unsupported HTTP method: {method}", "ERROR")
                return False
                
            self.update_progress(task_index, 80)
            
            if response.status_code < 400:
                self.log(f"API call successful: {response.status_code}", "SUCCESS")
                self.update_progress(task_index, 100)
                return True
            else:
                self.log(f"API call failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"API call error: {str(e)}", "ERROR")
            return False
            
    def execute_script_task(self, task: Dict[str, Any], task_index: int) -> bool:
        """Execute a Python script task"""
        try:
            script_content = task.get("script", "")
            script_file = task.get("script_file", "")
            
            self.update_progress(task_index, 20)
            
            if script_file and Path(script_file).exists():
                self.log(f"Executing script file: {script_file}")
                
                # Execute Python file
                result = subprocess.run(
                    ["python", script_file],
                    capture_output=True,
                    text=True,
                    cwd=task.get("working_directory", os.getcwd())
                )
                
                if result.stdout:
                    self.log(f"Script output: {result.stdout}")
                if result.stderr:
                    self.log(f"Script errors: {result.stderr}", "WARNING")
                    
                self.update_progress(task_index, 100)
                return result.returncode == 0
                
            elif script_content:
                self.log("Executing inline script")
                
                # Execute inline Python code
                # Note: Be careful with exec() in production
                local_vars = {}
                exec(script_content, {"__builtins__": __builtins__}, local_vars)
                
                self.update_progress(task_index, 100)
                self.log("Inline script executed successfully", "SUCCESS")
                return True
                
            else:
                self.log("No script content or file specified", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Script execution error: {str(e)}", "ERROR")
            return False

class InGUIAutomationSystem:
    """Complete automation system that runs within the GUI"""
    
    def __init__(self, progress_callback: Callable = None, log_callback: Callable = None):
        self.task_executor = TaskExecutor(progress_callback, log_callback)
        self.tasks = []
        self.is_running = False
        
    def load_tasks(self, tasks_file: str) -> bool:
        """Load tasks from JSON file"""
        try:
            with open(tasks_file, 'r') as f:
                self.tasks = json.load(f)
            return True
        except Exception as e:
            if self.task_executor.log_callback:
                self.task_executor.log_callback(f"Failed to load tasks: {str(e)}", "ERROR")
            return False
            
    def start_execution(self) -> bool:
        """Start executing all tasks"""
        if not self.tasks:
            if self.task_executor.log_callback:
                self.task_executor.log_callback("No tasks to execute", "WARNING")
            return False
            
        self.is_running = True
        self.task_executor.is_running = True
        
        # Execute tasks in background thread
        threading.Thread(target=self._execute_all_tasks, daemon=True).start()
        return True
        
    def stop_execution(self):
        """Stop task execution"""
        self.is_running = False
        self.task_executor.is_running = False
        
    def _execute_all_tasks(self):
        """Execute all tasks sequentially"""
        try:
            successful_tasks = 0
            
            for i, task in enumerate(self.tasks):
                if not self.is_running:
                    break
                    
                # Notify GUI that task is starting
                if self.task_executor.progress_callback:
                    self.task_executor.progress_callback("start_task", i, None)
                    
                # Execute the task
                success = self.task_executor.execute_task(task, i)
                
                if success:
                    successful_tasks += 1
                    if self.task_executor.progress_callback:
                        self.task_executor.progress_callback("complete_task", i, None)
                else:
                    if self.task_executor.progress_callback:
                        self.task_executor.progress_callback("error_task", i, None)
                        
                # Small delay between tasks
                time.sleep(0.5)
                
            # Notify completion
            if self.is_running:  # Only if not stopped by user
                if self.task_executor.progress_callback:
                    self.task_executor.progress_callback("execution_complete", successful_tasks, len(self.tasks))
                    
        except Exception as e:
            if self.task_executor.log_callback:
                self.task_executor.log_callback(f"Execution error: {str(e)}", "ERROR")
            if self.task_executor.progress_callback:
                self.task_executor.progress_callback("execution_error", str(e), None)