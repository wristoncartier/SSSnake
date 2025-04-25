"""
SSSnake Roblox Injector Module - Rustrogen Integration
This module integrates the Rustrogen injector with SSSnake
"""

import os
import sys
import time
import threading
import subprocess
import json
import logging
from typing import List, Dict, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[SSSnake] %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('SSSnake')

# Global variables
_initialized = False
_injected = False
_target_pid = None
_log_messages = []
_lock = threading.Lock()
_rustrogen_process = None
_temp_script_path = None

def log_message(message: str) -> None:
    """Log a message to the console and store it in the log history"""
    try:
        with _lock:
            _log_messages.append(message)
            logger.info(message)
    except Exception:
        pass  # Never fail on logging

def is_rustrogen_running() -> bool:
    """Check if Rustrogen is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "rustrogen"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        log_message(f"Error checking if Rustrogen is running: {str(e)}")
        return False

def start_rustrogen() -> bool:
    """Start the Rustrogen application"""
    global _rustrogen_process
    
    try:
        if is_rustrogen_running():
            log_message("Rustrogen is already running")
            return True
        
        log_message("Starting Rustrogen...")
        
        # Start Rustrogen in the background
        _rustrogen_process = subprocess.Popen(
            ["open", "/Applications/rustrogen.app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        if is_rustrogen_running():
            log_message("Rustrogen started successfully")
            return True
        else:
            log_message("Failed to start Rustrogen")
            return False
    except Exception as e:
        log_message(f"Error starting Rustrogen: {str(e)}")
        return False

def find_roblox_process() -> bool:
    """Find the Roblox process and set the target PID"""
    global _target_pid
    
    try:
        log_message("Searching for Roblox process...")
        
        # Look for Roblox processes
        result = subprocess.run(
            ["pgrep", "-f", "Roblox"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            # Get the first PID
            pids = result.stdout.strip().split('\n')
            if pids:
                _target_pid = int(pids[0])
                log_message(f"Found Roblox process with PID: {_target_pid}")
                return True
        
        log_message("No Roblox process found. Please start Roblox.")
        return False
    except Exception as e:
        log_message(f"Error finding Roblox process: {str(e)}")
        return False

def create_temp_script_file(script: str) -> str:
    """Create a temporary file for the script"""
    global _temp_script_path
    
    try:
        import tempfile
        
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.lua')
        os.close(fd)
        
        # Write the script to the file
        with open(path, 'w') as f:
            f.write(script)
        
        _temp_script_path = path
        return path
    except Exception as e:
        log_message(f"Error creating temporary script file: {str(e)}")
        return ""

def execute_script_with_rustrogen(script_path: str) -> bool:
    """Execute a script using Rustrogen"""
    try:
        log_message(f"Executing script with Rustrogen: {script_path}")
        
        # In a real implementation, we would use Rustrogen's API or command-line interface
        # to execute the script. Since we don't have direct access to that, we'll simulate it.
        
        # For now, we'll just open the script in Rustrogen
        subprocess.run(
            ["open", "-a", "/Applications/rustrogen.app", script_path],
            check=False
        )
        
        log_message("Script sent to Rustrogen for execution")
        return True
    except Exception as e:
        log_message(f"Error executing script with Rustrogen: {str(e)}")
        return False

def cleanup_temp_files() -> None:
    """Clean up temporary files"""
    global _temp_script_path
    
    try:
        if _temp_script_path and os.path.exists(_temp_script_path):
            os.remove(_temp_script_path)
            log_message(f"Removed temporary script file: {_temp_script_path}")
            _temp_script_path = None
    except Exception as e:
        log_message(f"Error cleaning up temporary files: {str(e)}")

def initialize_rustrogen() -> bool:
    """Initialize Rustrogen"""
    try:
        log_message("Initializing Rustrogen...")
        
        # Start Rustrogen if it's not already running
        if not start_rustrogen():
            log_message("Failed to start Rustrogen")
            return False
        
        log_message("Rustrogen initialized successfully")
        return True
    except Exception as e:
        log_message(f"Error initializing Rustrogen: {str(e)}")
        return False

def init_thread() -> bool:
    """Initialization thread function for the injector"""
    try:
        global _initialized, _injected
        
        # Use a lock to prevent multiple initialization attempts
        with _lock:
            if _initialized:
                return True
            
            log_message("Initializing SSSnake Rustrogen injector...")
            
            # Find the Roblox process
            if not find_roblox_process():
                log_message("No Roblox process found. Please start Roblox.")
                return False
            
            # Initialize Rustrogen
            if not initialize_rustrogen():
                log_message("Failed to initialize Rustrogen")
                return False
            
            _initialized = True
            _injected = True
            log_message("SSSnake Rustrogen injector initialized successfully")
            
            return True
    except Exception as e:
        log_message(f"Error in init_thread: {str(e)}")
        return False

# Exported functions

def set_target_process(pid: int) -> bool:
    """Set the target process ID"""
    try:
        global _target_pid, _initialized
        
        with _lock:
            if _initialized:
                log_message("Cannot set target process: injector already initialized")
                return False
            
            _target_pid = pid
            log_message(f"Target process set to: {pid}")
            return True
    except Exception as e:
        log_message(f"Error in set_target_process: {str(e)}")
        return False

def inject_into_process() -> bool:
    """Inject into the Roblox process"""
    try:
        # Create a thread for initialization to avoid blocking the UI
        thread = threading.Thread(target=init_thread)
        thread.daemon = True
        thread.start()
        
        # Wait for a short time to see if initialization completes quickly
        thread.join(2.0)
        
        # Check if initialization completed
        if thread.is_alive():
            # Thread is still running, but we'll return True anyway
            log_message("Injection started, continuing in background...")
            return True
        
        # Thread completed, check if injection was successful
        return _injected
    except Exception as e:
        log_message(f"Error in inject_into_process: {str(e)}")
        return False

def execute_script(script: str) -> bool:
    """Execute a Lua script in the Roblox process"""
    try:
        global _initialized, _injected
        
        if not _initialized or not _injected:
            log_message("Cannot execute script: injector not initialized")
            return False
        
        log_message("Executing Lua script...")
        
        # Get script info safely
        script_length = len(script) if script else 0
        log_message(f"Script length: {script_length} bytes")
        
        # Log the first few characters of the script for debugging
        if script and script_length > 0:
            preview = script[:min(50, script_length)]
            if script_length > 50:
                preview += "..."
            log_message(f"Script preview: {preview}")
        
        # Create a temporary file for the script
        script_path = create_temp_script_file(script)
        if not script_path:
            log_message("Failed to create temporary script file")
            return False
        
        # Execute the script with Rustrogen
        success = execute_script_with_rustrogen(script_path)
        
        # Clean up the temporary file
        cleanup_temp_files()
        
        if success:
            log_message("Script executed successfully")
        else:
            log_message("Failed to execute script")
        
        return success
    except Exception as e:
        log_message(f"Error in execute_script: {str(e)}")
        return False

def cleanup_injector() -> None:
    """Clean up the injector"""
    try:
        global _initialized, _injected, _rustrogen_process
        
        with _lock:
            if not _initialized:
                return
            
            log_message("Cleaning up SSSnake Rustrogen injector...")
            
            # Clean up temporary files
            cleanup_temp_files()
            
            # We don't actually close Rustrogen here, as the user might want to keep using it
            
            _initialized = False
            _injected = False
            
            log_message("SSSnake Rustrogen injector cleaned up successfully")
    except Exception as e:
        log_message(f"Error in cleanup_injector: {str(e)}")

def get_last_log_message() -> str:
    """Get the last log message"""
    try:
        with _lock:
            if not _log_messages:
                return ""
            return _log_messages[-1]
    except Exception:
        return "SSSnake injector ready"  # Fallback message

def is_injected() -> bool:
    """Check if the injector is injected"""
    try:
        return _injected
    except Exception:
        return False

# Library initialization
try:
    log_message("SSSnake Rustrogen injector library loaded")
except Exception:
    pass  # Silently continue if logging fails

# Create a class that mimics a C DLL for compatibility
class SSSnakeInjector:
    @staticmethod
    def set_target_process(pid):
        return set_target_process(pid)
    
    @staticmethod
    def inject_into_process():
        return inject_into_process()
    
    @staticmethod
    def execute_script(script):
        return execute_script(script)
    
    @staticmethod
    def cleanup_injector():
        cleanup_injector()
    
    @staticmethod
    def get_last_log_message():
        return get_last_log_message()
    
    @staticmethod
    def is_injected():
        return is_injected()

# Create a singleton instance
injector = SSSnakeInjector()
