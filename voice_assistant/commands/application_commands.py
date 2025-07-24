"""
Application launcher commands implementation.
"""

import subprocess
import re
from typing import Any, Dict, Optional

from .base import Command
from ..core.exceptions import ApplicationLaunchError
from ..config.settings import ConfigManager


class ApplicationCommand(Command):
    """Handler for application launcher commands."""
    
    def __init__(self, config_manager: ConfigManager, logger: Optional = None):
        super().__init__(logger)
        self.config_manager = config_manager
        
        # Default application mappings
        self.default_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'task manager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'registry editor': 'regedit.exe',
            'system information': 'msinfo32.exe',
            'device manager': 'devmgmt.msc',
            'disk management': 'diskmgmt.msc',
            'event viewer': 'eventvwr.msc',
            'services': 'services.msc'
        }
    
    @property
    def command_patterns(self) -> list[str]:
        return ["jalankan aplikasi *"]
    
    @property
    def description(self) -> str:
        return "Launch desktop applications by name"
    
    def can_handle(self, command: str) -> bool:
        """Check if this command can handle the given input."""
        return "jalankan aplikasi" in command.lower()
    
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute application launch command."""
        try:
            # Extract application name using regex
            app_match = re.search(r'jalankan aplikasi (.+)', command.lower())
            if not app_match:
                raise ApplicationLaunchError("Could not extract application name from command")
            
            app_name = app_match.group(1).strip()
            if not app_name:
                raise ApplicationLaunchError("No application name provided")
            
            return self._launch_application(app_name)
            
        except Exception as e:
            self.logger.error(f"Error executing application command '{command}': {e}")
            raise ApplicationLaunchError(f"Failed to execute application command: {e}")
    
    def _launch_application(self, app_name: str) -> str:
        """Launch application by name."""
        try:
            # Get executable name
            executable = self._get_executable_name(app_name)
            
            self.logger.info(f"Launching application: {executable}")
            
            # Try to launch the application
            process = subprocess.Popen(
                executable,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Check if process started successfully
            if process.poll() is None or process.returncode == 0:
                return f"Launched application: {app_name}"
            else:
                raise ApplicationLaunchError(f"Application failed to start: {app_name}")
                
        except FileNotFoundError:
            raise ApplicationLaunchError(f"Application not found: {app_name}")
        except Exception as e:
            raise ApplicationLaunchError(f"Failed to launch application '{app_name}': {e}")
    
    def _get_executable_name(self, app_name: str) -> str:
        """Get executable name for application."""
        app_name_lower = app_name.lower()
        
        # Check config manager shortcuts first
        config_executable = self.config_manager.get_application_command(app_name_lower)
        if config_executable:
            return config_executable
        
        # Check default mappings
        if app_name_lower in self.default_apps:
            return self.default_apps[app_name_lower]
        
        # Handle common application name variations
        name_mappings = {
            'vs code': 'code',
            'visual studio code': 'code',
            'vscode': 'code',
            'chrome': 'chrome.exe',
            'google chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'mozilla firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'microsoft edge': 'msedge.exe',
            'word': 'winword.exe',
            'microsoft word': 'winword.exe',
            'excel': 'excel.exe',
            'microsoft excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'microsoft powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe',
            'microsoft outlook': 'outlook.exe',
            'teams': 'teams.exe',
            'microsoft teams': 'teams.exe',
            'skype': 'skype.exe',
            'discord': 'discord.exe',
            'spotify': 'spotify.exe',
            'steam': 'steam.exe',
            'vlc': 'vlc.exe',
            'media player': 'vlc.exe',
            'photoshop': 'photoshop.exe',
            'adobe photoshop': 'photoshop.exe',
            'illustrator': 'illustrator.exe',
            'adobe illustrator': 'illustrator.exe'
        }
        
        if app_name_lower in name_mappings:
            return name_mappings[app_name_lower]
        
        # Try common executable patterns
        common_patterns = [
            f"{app_name_lower}.exe",
            f"{app_name_lower.replace(' ', '')}.exe",
            f"{app_name_lower.replace(' ', '_')}.exe",
            f"{app_name_lower.replace(' ', '-')}.exe"
        ]
        
        # Return the first pattern (most likely to work)
        return common_patterns[0]
    
    def add_application_shortcut(self, name: str, executable: str) -> None:
        """Add a new application shortcut to config."""
        try:
            self.config_manager.config.application_shortcuts[name.lower()] = executable
            self.config_manager.save_config()
            self.logger.info(f"Added application shortcut: {name} -> {executable}")
        except Exception as e:
            self.logger.error(f"Failed to add application shortcut: {e}")
            raise ApplicationLaunchError(f"Failed to add application shortcut: {e}")
    
    def remove_application_shortcut(self, name: str) -> None:
        """Remove application shortcut from config."""
        try:
            shortcuts = self.config_manager.config.application_shortcuts
            if name.lower() in shortcuts:
                del shortcuts[name.lower()]
                self.config_manager.save_config()
                self.logger.info(f"Removed application shortcut: {name}")
            else:
                raise ApplicationLaunchError(f"Application shortcut not found: {name}")
        except Exception as e:
            self.logger.error(f"Failed to remove application shortcut: {e}")
            raise ApplicationLaunchError(f"Failed to remove application shortcut: {e}")
    
    def list_application_shortcuts(self) -> Dict[str, str]:
        """List all available application shortcuts."""
        shortcuts = self.config_manager.config.application_shortcuts.copy()
        shortcuts.update(self.default_apps)
        return shortcuts