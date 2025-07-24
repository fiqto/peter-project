"""
Custom exceptions for the Voice Assistant application.
"""

from typing import Optional


class VoiceAssistantError(Exception):
    """Base exception for all Voice Assistant errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ConfigurationError(VoiceAssistantError):
    """Raised when there's an error with configuration loading or validation."""
    pass


class SpeechRecognitionError(VoiceAssistantError):
    """Raised when there's an error with speech recognition."""
    pass


class CommandExecutionError(VoiceAssistantError):
    """Raised when there's an error executing a command."""
    pass


class DeviceConnectionError(VoiceAssistantError):
    """Raised when there's an error connecting to smart devices."""
    pass


class ApplicationLaunchError(VoiceAssistantError):
    """Raised when there's an error launching an application."""
    pass


class SystemCommandError(VoiceAssistantError):
    """Raised when there's an error executing system commands."""
    pass