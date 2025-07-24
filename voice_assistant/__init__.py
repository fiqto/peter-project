"""
Voice Assistant Package

A voice-controlled personal assistant for Windows with Bahasa Indonesia support.
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "assistant@example.com"

from .core.assistant import VoiceAssistant
from .core.exceptions import VoiceAssistantError

__all__ = ["VoiceAssistant", "VoiceAssistantError"]