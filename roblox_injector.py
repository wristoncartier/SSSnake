import ctypes
import os
import sys
import logging
import psutil
from typing import Tuple, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('roblox_injector')

class RobloxInjector:
    def __init__(self):
        self.roblox_pid = None
        self.injector = None
        self.logger = logger
        
        # Load the dylib
        dylib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'roblox_injector.dylib')
        self.logger.info(f"Loading dylib from {dylib_path}")
        
        try:
            self.injector = ctypes.CDLL(dylib_path)
            
            # Set up function prototypes
            self.injector.init_roblox_api.restype = ctypes.c_bool
            self.injector.init_roblox_api.argtypes = [ctypes.c_int]  # pid
            self.injector.cleanup_roblox_api.restype = None
            self.injector.create_lua_state.restype = ctypes.c_bool
            self.injector.install_lua_functions.restype = ctypes.c_bool
            self.injector.execute_lua_script.restype = ctypes.c_bool
            self.injector.execute_lua_script.argtypes = [ctypes.c_char_p]
            
            self.logger.info("Successfully loaded dylib and set function prototypes")
        except Exception as e:
            self.logger.error(f"Failed to load dylib: {e}")
            raise
    
    def find_roblox_process(self) -> Optional[int]:
        """Find the Roblox process ID."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'RobloxPlayer' in proc.info['name']:
                    self.logger.info(f"Found Roblox process: {proc.info['pid']}")
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def inject(self) -> Tuple[bool, str]:
        """Inject into the Roblox process."""
        # Find Roblox process
        self.roblox_pid = self.find_roblox_process()
        if not self.roblox_pid:
            return False, "Roblox process not found"
        
        self.logger.info("Initializing Roblox API...")
        if not self.injector.init_roblox_api(self.roblox_pid):
            return False, "Failed to initialize Roblox API"
        
        self.logger.info("Creating Lua state...")
        if not self.injector.create_lua_state():
            return False, "Failed to create Lua state"
        
        self.logger.info("Installing Lua functions...")
        if not self.injector.install_lua_functions():
            return False, "Failed to install Lua functions"
        
        self.logger.info("Successfully injected into Roblox")
        return True, "Successfully injected"
    
    def execute_script(self, script: str) -> Tuple[bool, str]:
        """Execute a Lua script in the Roblox environment."""
        if not self.roblox_pid:
            return False, "Not injected into Roblox"
        
        try:
            script_bytes = script.encode('utf-8')
            if not self.injector.execute_lua_script(script_bytes):
                return False, "Script execution failed"
            return True, "Script executed successfully"
        except Exception as e:
            return False, f"Error executing script: {e}"
    
    def cleanup(self):
        """Clean up resources."""
        if self.injector:
            self.injector.cleanup_roblox_api()
            self.roblox_pid = None

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
