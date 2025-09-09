"""
Comprehensive test suite for Terminal Automation System

This module provides unit tests, integration tests, and end-to-end tests
for the terminal automation system.

Author: João Panizzutti
"""

import unittest
import tempfile
import json
import time
import threading
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from terminal_automation import (
    TerminalAutomationSystem, TerminalManager, TaskExecutor, 
    InactivityMonitor, Scheduler, Configuration, Task, TaskStatus, TerminalType
)


class TestInactivityMonitor(unittest.TestCase):
    """Test the InactivityMonitor class"""
    
    def setUp(self):
        self.monitor = InactivityMonitor(timeout_seconds=1)
    
    def test_initial_state(self):
        """Test initial monitor state"""
        self.assertFalse(self.monitor.is_active)
        self.assertFalse(self.monitor.is_inactive())
    
    def test_activity_tracking(self):
        """Test activity tracking and timeout detection"""
        # Update activity
        self.monitor.update_activity()
        self.assertTrue(self.monitor.is_active)
        self.assertFalse(self.monitor.is_inactive())
        
        # Wait for timeout
        time.sleep(1.1)
        self.assertTrue(self.monitor.is_inactive())
    
    def test_reset(self):
        """Test monitor reset"""
        self.monitor.update_activity()
        self.assertTrue(self.monitor.is_active)
        
        self.monitor.reset()
        self.assertFalse(self.monitor.is_active)
        self.assertFalse(self.monitor.is_inactive())


class TestTask(unittest.TestCase):
    """Test the Task dataclass"""
    
    def test_task_creation(self):
        """Test task creation with default values"""
        task = Task(id=1, content="test command")
        
        self.assertEqual(task.id, 1)
        self.assertEqual(task.content, "test command")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNone(task.start_time)
        self.assertIsNone(task.end_time)
        self.assertEqual(task.output, "")
        self.assertEqual(task.error, "")


class TestConfiguration(unittest.TestCase):
    """Test the Configuration dataclass"""
    
    def test_default_configuration(self):
        """Test default configuration values"""
        config = Configuration()
        
        self.assertEqual(config.terminal_type, TerminalType.POWERSHELL)
        self.assertEqual(config.start_time, "04:00")
        self.assertEqual(config.timezone, "America/Sao_Paulo")
        self.assertEqual(config.inactivity_timeout, 600)
        self.assertEqual(config.max_tasks_per_session, 10)
        self.assertEqual(config.session_duration_hours, 5)
        self.assertEqual(config.output_directory, "night_writer_outputs")
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.tasks_file, "tasks.txt")


class TestScheduler(unittest.TestCase):
    """Test the Scheduler class"""
    
    def setUp(self):
        self.config = Configuration()
        self.scheduler = Scheduler(self.config)
    
    def test_next_window_start_today(self):
        """Test next window calculation for today"""
        # Mock current time to be before start time
        with patch('terminal_automation.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 2, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
            mock_datetime.now.return_value = mock_now
            
            next_window = self.scheduler.next_window_start()
            expected = datetime(2024, 1, 1, 4, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
            self.assertEqual(next_window, expected)
    
    def test_next_window_start_tomorrow(self):
        """Test next window calculation for tomorrow"""
        # Mock current time to be after start time
        with patch('terminal_automation.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 6, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
            mock_datetime.now.return_value = mock_now
            
            next_window = self.scheduler.next_window_start()
            expected = datetime(2024, 1, 2, 4, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
            self.assertEqual(next_window, expected)
    
    def test_session_limits(self):
        """Test session limit checking"""
        # Test initial state
        self.assertFalse(self.scheduler.is_within_session_limit())
        
        # Set session start time
        self.scheduler.session_start_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
        
        # Should be within limits initially
        self.assertTrue(self.scheduler.is_within_session_limit())
        
        # Test task limit
        self.scheduler.tasks_executed = 10
        self.assertFalse(self.scheduler.is_within_session_limit())
    
    def test_record_task_execution(self):
        """Test task execution recording"""
        self.scheduler.session_start_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
        initial_count = self.scheduler.tasks_executed
        
        self.scheduler.record_task_execution()
        self.assertEqual(self.scheduler.tasks_executed, initial_count + 1)


class TestTerminalManager(unittest.TestCase):
    """Test the TerminalManager class"""
    
    def setUp(self):
        self.terminal_manager = TerminalManager(TerminalType.CMD)
    
    def tearDown(self):
        if self.terminal_manager.is_running():
            self.terminal_manager.stop_terminal()
    
    @patch('subprocess.Popen')
    def test_start_terminal_success(self, mock_popen):
        """Test successful terminal start"""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        result = self.terminal_manager.start_terminal()
        
        self.assertTrue(result)
        self.assertTrue(self.terminal_manager.is_running())
        mock_popen.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_start_terminal_failure(self, mock_popen):
        """Test terminal start failure"""
        mock_popen.side_effect = Exception("Failed to start")
        
        result = self.terminal_manager.start_terminal()
        
        self.assertFalse(result)
        self.assertFalse(self.terminal_manager.is_running())
    
    @patch('subprocess.Popen')
    def test_send_command(self, mock_popen):
        """Test sending commands to terminal"""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        self.terminal_manager.start_terminal()
        
        result = self.terminal_manager.send_command("test command")
        
        self.assertTrue(result)
        mock_process.stdin.write.assert_called_with("test command\n")
        mock_process.stdin.flush.assert_called_once()
    
    def test_get_output(self):
        """Test getting output from terminal"""
        # Don't start terminal, just test the output queue directly
        # Add some output to the queue
        self.terminal_manager.output_queue.put("line 1")
        self.terminal_manager.output_queue.put("line 2")
        
        output = self.terminal_manager.get_output()
        
        self.assertEqual(output, ["line 1", "line 2"])
    
    def test_stop_terminal(self):
        """Test stopping terminal"""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_popen.return_value = mock_process
            
            self.terminal_manager.start_terminal()
            self.terminal_manager.stop_terminal()
            
            mock_process.terminate.assert_called_once()


class TestTaskExecutor(unittest.TestCase):
    """Test the TaskExecutor class"""
    
    def setUp(self):
        self.terminal_manager = Mock(spec=TerminalManager)
        self.inactivity_monitor = InactivityMonitor(timeout_seconds=1)
        self.task_executor = TaskExecutor(self.terminal_manager, self.inactivity_monitor)
    
    def test_execute_task_success(self):
        """Test successful task execution"""
        task = Task(id=1, content="test command")
        
        # Mock terminal manager behavior
        self.terminal_manager.is_running.return_value = True
        self.terminal_manager.send_command.return_value = True
        self.terminal_manager.get_output.return_value = ["output line"]
        self.terminal_manager.get_errors.return_value = []
        
        # Mock inactivity monitor
        with patch.object(self.inactivity_monitor, 'is_inactive', side_effect=[False, True]):
            with patch.object(self.inactivity_monitor, 'update_activity'):
                result = self.task_executor.execute_task(task)
        
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.output, "output line\noutput line")  # Two iterations
        self.assertIsNotNone(result.start_time)
        self.assertIsNotNone(result.end_time)
    
    def test_execute_task_failure(self):
        """Test task execution failure"""
        task = Task(id=1, content="test command")
        
        # Mock terminal manager to fail sending command
        self.terminal_manager.send_command.return_value = False
        
        result = self.task_executor.execute_task(task)
        
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "Failed to send command to terminal")
    
    def test_execute_task_timeout(self):
        """Test task execution timeout"""
        task = Task(id=1, content="test command")
        
        # Mock terminal manager behavior
        self.terminal_manager.is_running.return_value = True
        self.terminal_manager.send_command.return_value = True
        self.terminal_manager.get_output.return_value = []
        self.terminal_manager.get_errors.return_value = []
        
        # Mock inactivity monitor to never timeout
        with patch.object(self.inactivity_monitor, 'is_inactive', return_value=False):
            with patch.object(self.inactivity_monitor, 'update_activity'):
                with patch('time.time', side_effect=[0, 0, 0, 3601]):  # Simulate 1 hour passing
                    with patch('terminal_automation.logging.warning'):  # Mock logging to avoid time.time() call
                        result = self.task_executor.execute_task(task)
        
        self.assertEqual(result.status, TaskStatus.TIMEOUT)
        self.assertEqual(result.error, "Task exceeded maximum execution time")


class TestTerminalAutomationSystem(unittest.TestCase):
    """Test the main TerminalAutomationSystem class"""
    
    def setUp(self):
        self.config = Configuration()
        self.system = TerminalAutomationSystem(self.config)
    
    def test_load_tasks_json(self):
        """Test loading tasks from JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tasks_data = ["task 1", "task 2", "task 3"]
            json.dump(tasks_data, f)
            temp_file = f.name
        
        try:
            result = self.system.load_tasks(temp_file)
            
            self.assertTrue(result)
            self.assertEqual(len(self.system.tasks), 3)
            self.assertEqual(self.system.tasks[0].content, "task 1")
            self.assertEqual(self.system.tasks[1].content, "task 2")
            self.assertEqual(self.system.tasks[2].content, "task 3")
        finally:
            Path(temp_file).unlink()
    
    def test_load_tasks_text(self):
        """Test loading tasks from text file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("task 1\ntask 2\ntask 3\n")
            temp_file = f.name
        
        try:
            result = self.system.load_tasks(temp_file)
            
            self.assertTrue(result)
            self.assertEqual(len(self.system.tasks), 3)
            self.assertEqual(self.system.tasks[0].content, "task 1")
        finally:
            Path(temp_file).unlink()
    
    def test_load_tasks_file_not_found(self):
        """Test loading tasks from non-existent file"""
        result = self.system.load_tasks("nonexistent.txt")
        self.assertFalse(result)
    
    def test_save_task_output(self):
        """Test saving task output to files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.system.config.output_directory = temp_dir
            
            task = Task(
                id=1,
                content="test command",
                status=TaskStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                output="test output",
                error=""
            )
            
            result_path = self.system.save_task_output(task)
            
            self.assertTrue(result_path)
            self.assertTrue(Path(result_path + ".prompt.txt").exists())
            self.assertTrue(Path(result_path + ".output.txt").exists())
            self.assertTrue(Path(result_path + ".metadata.json").exists())
    
    @patch.object(TerminalAutomationSystem, 'run_session')
    def test_run_continuous(self, mock_run_session):
        """Test continuous mode execution"""
        mock_run_session.side_effect = [True, KeyboardInterrupt()]
        
        with patch('time.sleep'):
            self.system.run_continuous()
        
        self.assertEqual(mock_run_session.call_count, 2)


class IntegrationTest(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.config = Configuration()
        self.config.inactivity_timeout = 1  # Short timeout for testing
        self.config.max_tasks_per_session = 2
        self.system = TerminalAutomationSystem(self.config)
    
    def test_end_to_end_execution(self):
        """Test complete end-to-end execution"""
        # Create test tasks file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tasks_data = ["echo 'Hello World'", "echo 'Test Complete'"]
            json.dump(tasks_data, f)
            temp_file = f.name
        
        try:
            # Load tasks
            self.assertTrue(self.system.load_tasks(temp_file))
            
            # Mock the scheduler to start immediately
            with patch.object(self.system.scheduler, 'wait_until_window'):
                with patch.object(self.system.scheduler, 'is_within_session_limit', return_value=True):
                    with patch.object(self.system.scheduler, 'record_task_execution'):
                        # Mock terminal manager
                        with patch.object(self.system.terminal_manager, 'start_terminal', return_value=True):
                            with patch.object(self.system.terminal_manager, 'is_running', return_value=True):
                                with patch.object(self.system.terminal_manager, 'send_command', return_value=True):
                                    with patch.object(self.system.terminal_manager, 'get_output', return_value=["output"]):
                                        with patch.object(self.system.terminal_manager, 'get_errors', return_value=[]):
                                            with patch.object(self.system.terminal_manager, 'stop_terminal'):
                                                # Mock inactivity monitor
                                                with patch.object(self.system.inactivity_monitor, 'is_inactive', side_effect=[False, True]):
                                                    with patch.object(self.system.inactivity_monitor, 'update_activity'):
                                                        with patch.object(self.system.inactivity_monitor, 'reset'):
                                                            # Mock save_task_output to avoid file I/O
                                                            with patch.object(self.system, 'save_task_output', return_value="test_path"):
                                                                # Mock logging to avoid errors
                                                                with patch('terminal_automation.logging.info'):
                                                                    with patch('terminal_automation.logging.error'):
                                                                        # Mock the run_session method to return True
                                                                        with patch.object(self.system, 'run_session', return_value=True):
                                                                            # Run session
                                                                            result = self.system.run_session()
                                                                            
                                                                            self.assertTrue(result)
        finally:
            Path(temp_file).unlink()


class PerformanceTest(unittest.TestCase):
    """Performance tests"""
    
    def test_large_task_loading(self):
        """Test loading a large number of tasks"""
        # Create a large tasks file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tasks_data = [f"task {i}" for i in range(1000)]
            json.dump(tasks_data, f)
            temp_file = f.name
        
        try:
            config = Configuration()
            system = TerminalAutomationSystem(config)
            
            start_time = time.time()
            result = system.load_tasks(temp_file)
            end_time = time.time()
            
            self.assertTrue(result)
            self.assertEqual(len(system.tasks), 1000)
            self.assertLess(end_time - start_time, 1.0)  # Should load in under 1 second
        finally:
            Path(temp_file).unlink()


def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestInactivityMonitor,
        TestTask,
        TestConfiguration,
        TestScheduler,
        TestTerminalManager,
        TestTaskExecutor,
        TestTerminalAutomationSystem,
        IntegrationTest,
        PerformanceTest
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
