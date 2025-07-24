"""
Base command interface and abstract classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from ..core.exceptions import CommandExecutionError


class Command(ABC):
    """Abstract base class for all voice commands."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check if this command handler can process the given command."""
        pass
    
    @abstractmethod
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute the command."""
        pass
    
    @property
    @abstractmethod
    def command_patterns(self) -> list[str]:
        """Return list of command patterns this handler supports."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return description of what this command does."""
        pass


class CommandRegistry:
    """Registry for managing command handlers."""
    
    def __init__(self, wake_word: str = "peter"):
        self._commands: list[Command] = []
        self.wake_word = wake_word.lower()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register(self, command: Command) -> None:
        """Register a command handler."""
        self._commands.append(command)
        self.logger.info(f"Registered command handler: {command.__class__.__name__}")
    
    def unregister(self, command: Command) -> None:
        """Unregister a command handler."""
        if command in self._commands:
            self._commands.remove(command)
            self.logger.info(f"Unregistered command handler: {command.__class__.__name__}")
    
    def has_wake_word(self, command: str) -> bool:
        """Check if command starts with the wake word."""
        command_lower = command.lower().strip()
        return command_lower.startswith(self.wake_word)
    
    def remove_wake_word(self, command: str) -> str:
        """Remove wake word from command and return the actual command."""
        command_lower = command.lower().strip()
        if command_lower.startswith(self.wake_word):
            # Remove wake word and any extra spaces
            actual_command = command_lower[len(self.wake_word):].strip()
            return actual_command
        return command_lower
    
    def get_handler(self, command: str) -> Optional[Command]:
        """Get the appropriate command handler for a command."""
        # First check if command has wake word
        if not self.has_wake_word(command):
            return None
            
        # Remove wake word and get actual command
        actual_command = self.remove_wake_word(command)
        
        for cmd_handler in self._commands:
            if cmd_handler.can_handle(actual_command):
                return cmd_handler
        return None
    
    def execute_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a command using the appropriate handler."""
        # Check for wake word first
        if not self.has_wake_word(command):
            raise CommandExecutionError(f"Command must start with wake word '{self.wake_word}': {command}")
            
        handler = self.get_handler(command)
        if handler is None:
            raise CommandExecutionError(f"No handler found for command: {command}")
        
        # Remove wake word before executing
        actual_command = self.remove_wake_word(command)
        
        try:
            return handler.execute(actual_command, context)
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {e}")
            raise CommandExecutionError(f"Failed to execute command: {e}")
    
    def list_commands(self) -> Dict[str, Dict[str, Any]]:
        """List all registered commands with their patterns and descriptions."""
        commands = {}
        for cmd_handler in self._commands:
            # Add wake word to each pattern
            patterns_with_wake_word = [f"{self.wake_word} {pattern}" for pattern in cmd_handler.command_patterns]
            commands[cmd_handler.__class__.__name__] = {
                'patterns': patterns_with_wake_word,
                'description': cmd_handler.description,
                'wake_word': self.wake_word
            }
        return commands