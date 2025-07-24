"""
Utility commands implementation (screenshots, etc.).
"""

import os
import pyautogui
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .base import Command
from ..core.exceptions import CommandExecutionError
from ..config.settings import ConfigManager


class UtilityCommand(Command):
    """Handler for utility commands like screenshots."""
    
    def __init__(self, config_manager: ConfigManager, logger: Optional = None):
        super().__init__(logger)
        self.config_manager = config_manager
    
    @property
    def command_patterns(self) -> list[str]:
        return [
            "ambil screenshot",
            "screenshot",
            "tangkap layar"
        ]
    
    @property
    def description(self) -> str:
        return "Utility commands: take screenshots"
    
    def can_handle(self, command: str) -> bool:
        """Check if this command can handle the given input."""
        patterns = [
            "ambil screenshot",
            "screenshot",
            "tangkap layar"
        ]
        return any(pattern in command.lower() for pattern in patterns)
    
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute utility command."""
        command_lower = command.lower()
        
        try:
            if any(pattern in command_lower for pattern in ["ambil screenshot", "screenshot", "tangkap layar"]):
                return self._take_screenshot()
            else:
                raise CommandExecutionError(f"Unknown utility command: {command}")
                
        except Exception as e:
            self.logger.error(f"Error executing utility command '{command}': {e}")
            raise CommandExecutionError(f"Failed to execute utility command: {e}")
    
    def _take_screenshot(self) -> str:
        """Take a screenshot and save it."""
        try:
            # Get screenshots folder from config
            screenshots_folder = self.config_manager.config.settings.screenshots_folder
            
            # Create screenshots directory if it doesn't exist
            screenshots_path = Path(screenshots_folder)
            screenshots_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_path / filename
            
            # Take screenshot
            self.logger.info(f"Taking screenshot: {filepath}")
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            
            # Verify file was created
            if filepath.exists():
                file_size = filepath.stat().st_size
                self.logger.info(f"Screenshot saved: {filepath} ({file_size} bytes)")
                return f"Screenshot saved: {filepath}"
            else:
                raise CommandExecutionError("Screenshot file was not created")
                
        except Exception as e:
            raise CommandExecutionError(f"Failed to take screenshot: {e}")
    
    def _take_partial_screenshot(self, x: int, y: int, width: int, height: int) -> str:
        """Take a partial screenshot of specified region."""
        try:
            # Get screenshots folder from config
            screenshots_folder = self.config_manager.config.settings.screenshots_folder
            screenshots_path = Path(screenshots_folder)
            screenshots_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_partial_{timestamp}.png"
            filepath = screenshots_path / filename
            
            # Take partial screenshot
            self.logger.info(f"Taking partial screenshot: {filepath} (region: {x},{y},{width},{height})")
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(str(filepath))
            
            if filepath.exists():
                file_size = filepath.stat().st_size
                self.logger.info(f"Partial screenshot saved: {filepath} ({file_size} bytes)")
                return f"Partial screenshot saved: {filepath}"
            else:
                raise CommandExecutionError("Partial screenshot file was not created")
                
        except Exception as e:
            raise CommandExecutionError(f"Failed to take partial screenshot: {e}")
    
    def get_screen_info(self) -> Dict[str, Any]:
        """Get screen information."""
        try:
            screen_size = pyautogui.size()
            return {
                'width': screen_size.width,
                'height': screen_size.height,
                'total_pixels': screen_size.width * screen_size.height
            }
        except Exception as e:
            raise CommandExecutionError(f"Failed to get screen info: {e}")
    
    def list_screenshots(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """List existing screenshots."""
        try:
            screenshots_folder = self.config_manager.config.settings.screenshots_folder
            screenshots_path = Path(screenshots_folder)
            
            if not screenshots_path.exists():
                return []
            
            # Get all PNG files in screenshots folder
            screenshot_files = list(screenshots_path.glob("screenshot_*.png"))
            
            # Sort by modification time (newest first)
            screenshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Apply limit if specified
            if limit:
                screenshot_files = screenshot_files[:limit]
            
            # Build file info list
            screenshots = []
            for file_path in screenshot_files:
                stat = file_path.stat()
                screenshots.append({
                    'filename': file_path.name,
                    'filepath': str(file_path),
                    'size_bytes': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return screenshots
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to list screenshots: {e}")
    
    def delete_screenshot(self, filename: str) -> str:
        """Delete a specific screenshot."""
        try:
            screenshots_folder = self.config_manager.config.settings.screenshots_folder
            filepath = Path(screenshots_folder) / filename
            
            if not filepath.exists():
                raise CommandExecutionError(f"Screenshot not found: {filename}")
            
            filepath.unlink()
            self.logger.info(f"Deleted screenshot: {filepath}")
            return f"Deleted screenshot: {filename}"
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to delete screenshot: {e}")
    
    def cleanup_old_screenshots(self, days_old: int = 30) -> str:
        """Delete screenshots older than specified days."""
        try:
            screenshots_folder = self.config_manager.config.settings.screenshots_folder
            screenshots_path = Path(screenshots_folder)
            
            if not screenshots_path.exists():
                return "No screenshots folder found"
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in screenshots_path.glob("screenshot_*.png"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            self.logger.info(f"Deleted {deleted_count} screenshots older than {days_old} days")
            return f"Deleted {deleted_count} old screenshots"
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to cleanup screenshots: {e}")