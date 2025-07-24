"""
System control commands implementation.
"""

import subprocess
import threading
import psutil
import re
from typing import Any, Dict, Optional

from .base import Command
from ..core.exceptions import SystemCommandError


class SystemControlCommand(Command):
    """Handler for system control commands."""
    
    def __init__(self, logger: Optional = None):
        super().__init__(logger)
        self.shutdown_timer: Optional[threading.Timer] = None
    
    @property
    def command_patterns(self) -> list[str]:
        return [
            "matikan komputer",
            "tutup semua aplikasi", 
            "timer * menit matikan komputer"
        ]
    
    @property
    def description(self) -> str:
        return "Handle system control commands: shutdown, close apps, timer shutdown"
    
    def can_handle(self, command: str) -> bool:
        """Check if this command can handle the given input."""
        patterns = [
            "matikan komputer",
            "tutup semua aplikasi",
            "timer",
            "menit"
        ]
        return any(pattern in command.lower() for pattern in patterns)
    
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute system control command."""
        command_lower = command.lower()
        
        try:
            if "matikan komputer" in command_lower and "timer" not in command_lower:
                return self._shutdown_computer()
                
            elif "tutup semua aplikasi" in command_lower:
                return self._close_all_applications()
                
            elif "timer" in command_lower and "menit" in command_lower and "matikan komputer" in command_lower:
                return self._schedule_shutdown(command_lower)
                
            else:
                raise SystemCommandError(f"Unknown system command: {command}")
                
        except Exception as e:
            self.logger.error(f"Error executing system command '{command}': {e}")
            raise SystemCommandError(f"Failed to execute system command: {e}")
    
    def _shutdown_computer(self) -> str:
        """Shutdown the computer immediately."""
        try:
            self.logger.info("Initiating computer shutdown")
            subprocess.run(["shutdown", "/s", "/t", "0"], shell=True, check=True)
            return "Computer shutdown initiated"
        except subprocess.CalledProcessError as e:
            raise SystemCommandError(f"Failed to shutdown computer: {e}")
    
    def _close_all_applications(self) -> str:
        """Close all user applications."""
        try:
            self.logger.info("Closing all applications")
            closed_count = 0
            
            # List of system processes to skip
            system_processes = {
                'system', 'registry', 'csrss.exe', 'winlogon.exe',
                'services.exe', 'lsass.exe', 'svchost.exe', 'python.exe',
                'dwm.exe', 'explorer.exe'  # Keep explorer running
            }
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Skip system processes and current process
                    if proc_name in system_processes:
                        continue
                    
                    # Terminate the process gracefully
                    proc.terminate()
                    closed_count += 1
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            self.logger.info(f"Attempted to close {closed_count} applications")
            return f"Closed {closed_count} applications"
            
        except Exception as e:
            raise SystemCommandError(f"Failed to close applications: {e}")
    
    def _schedule_shutdown(self, command: str) -> str:
        """Schedule computer shutdown after specified minutes."""
        try:
            # Extract minutes from command
            minutes_match = re.search(r'(\d+)\s*menit', command)
            if not minutes_match:
                raise SystemCommandError("Could not extract timer duration from command")
            
            minutes = int(minutes_match.group(1))
            if minutes <= 0:
                raise SystemCommandError("Timer duration must be positive")
            
            # Cancel any existing timer
            if self.shutdown_timer:
                self.shutdown_timer.cancel()
            
            seconds = minutes * 60
            self.logger.info(f"Scheduling shutdown in {minutes} minutes ({seconds} seconds)")
            
            # Schedule the shutdown
            self.shutdown_timer = threading.Timer(seconds, self._delayed_shutdown)
            self.shutdown_timer.start()
            
            return f"Computer will shutdown in {minutes} minutes"
            
        except ValueError as e:
            raise SystemCommandError(f"Invalid timer duration: {e}")
        except Exception as e:
            raise SystemCommandError(f"Failed to schedule shutdown: {e}")
    
    def _delayed_shutdown(self) -> None:
        """Execute delayed shutdown."""
        try:
            self.logger.info("Executing scheduled shutdown")
            subprocess.run(["shutdown", "/s", "/t", "0"], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to execute scheduled shutdown: {e}")
    
    def cancel_shutdown_timer(self) -> None:
        """Cancel any pending shutdown timer."""
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None
            self.logger.info("Shutdown timer cancelled")