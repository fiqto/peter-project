"""
Browser and internet-related commands implementation.
"""

import webbrowser
import re
from typing import Any, Dict, Optional

from .base import Command
from ..core.exceptions import CommandExecutionError


class BrowserCommand(Command):
    """Handler for browser and internet commands."""
    
    def __init__(self, logger: Optional = None):
        super().__init__(logger)
        self.website_shortcuts = {
            'github': 'https://github.com',
            'facebook': 'https://facebook.com',
            'twitter': 'https://twitter.com',
            'instagram': 'https://instagram.com',
            'linkedin': 'https://linkedin.com',
            'stackoverflow': 'https://stackoverflow.com',
            'reddit': 'https://reddit.com',
            'netflix': 'https://netflix.com',
            'amazon': 'https://amazon.com',
            'gmail': 'https://gmail.com',
            'youtube': 'https://youtube.com',
            'google': 'https://google.com'
        }
    
    @property
    def command_patterns(self) -> list[str]:
        return [
            "buka youtube",
            "cari di google *",
            "buka website *"
        ]
    
    @property
    def description(self) -> str:
        return "Handle browser commands: open YouTube, Google search, open websites"
    
    def can_handle(self, command: str) -> bool:
        """Check if this command can handle the given input."""
        patterns = [
            "buka youtube",
            "cari di google",
            "buka website"
        ]
        return any(pattern in command.lower() for pattern in patterns)
    
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute browser command."""
        command_lower = command.lower()
        
        try:
            if "buka youtube" in command_lower:
                return self._open_youtube()
                
            elif "cari di google" in command_lower:
                return self._search_google(command_lower)
                
            elif "buka website" in command_lower:
                return self._open_website(command_lower)
                
            else:
                raise CommandExecutionError(f"Unknown browser command: {command}")
                
        except Exception as e:
            self.logger.error(f"Error executing browser command '{command}': {e}")
            raise CommandExecutionError(f"Failed to execute browser command: {e}")
    
    def _open_youtube(self) -> str:
        """Open YouTube in the default browser."""
        try:
            self.logger.info("Opening YouTube")
            webbrowser.open("https://youtube.com")
            return "YouTube opened"
        except Exception as e:
            raise CommandExecutionError(f"Failed to open YouTube: {e}")
    
    def _search_google(self, command: str) -> str:
        """Perform Google search with extracted keywords."""
        try:
            # Extract search keywords using regex
            search_match = re.search(r'cari di google (.+)', command)
            if not search_match:
                raise CommandExecutionError("Could not extract search keywords")
            
            keywords = search_match.group(1).strip()
            if not keywords:
                raise CommandExecutionError("No search keywords provided")
            
            # Create search URL
            search_url = f"https://www.google.com/search?q={keywords.replace(' ', '+')}"
            
            self.logger.info(f"Searching Google for: {keywords}")
            webbrowser.open(search_url)
            
            return f"Searching Google for: {keywords}"
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to perform Google search: {e}")
    
    def _open_website(self, command: str) -> str:
        """Open website by name."""
        try:
            # Extract website name using regex
            website_match = re.search(r'buka website (.+)', command)
            if not website_match:
                raise CommandExecutionError("Could not extract website name")
            
            website_name = website_match.group(1).strip().lower()
            if not website_name:
                raise CommandExecutionError("No website name provided")
            
            # Get URL from shortcuts
            url = self.website_shortcuts.get(website_name)
            if not url:
                # Try to construct URL if not in shortcuts
                url = f"https://{website_name}.com"
            
            self.logger.info(f"Opening website: {url}")
            webbrowser.open(url)
            
            return f"Opened website: {url}"
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to open website: {e}")
    
    def add_website_shortcut(self, name: str, url: str) -> None:
        """Add a new website shortcut."""
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        self.website_shortcuts[name.lower()] = url
        self.logger.info(f"Added website shortcut: {name} -> {url}")
    
    def remove_website_shortcut(self, name: str) -> None:
        """Remove a website shortcut."""
        if name.lower() in self.website_shortcuts:
            del self.website_shortcuts[name.lower()]
            self.logger.info(f"Removed website shortcut: {name}")
    
    def list_website_shortcuts(self) -> Dict[str, str]:
        """List all available website shortcuts."""
        return self.website_shortcuts.copy()