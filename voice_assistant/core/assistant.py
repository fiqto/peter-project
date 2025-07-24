"""
Main Voice Assistant implementation with dependency injection.
"""

import threading
import time
from typing import Optional, Dict, Any
import logging

from ..config.settings import ConfigManager
from ..services.speech_service import SpeechRecognitionService
from ..services.logging_service import LoggingService
from ..commands.base import CommandRegistry
from .exceptions import VoiceAssistantError, CommandExecutionError


class VoiceAssistant:
    """Main Voice Assistant class with dependency injection."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        speech_service: SpeechRecognitionService,
        command_registry: CommandRegistry,
        logging_service: LoggingService
    ):
        """Initialize Voice Assistant with injected dependencies."""
        self.config_manager = config_manager
        self.speech_service = speech_service
        self.command_registry = command_registry
        self.logging_service = logging_service
        
        self.logger = logging_service.get_logger('voice_assistant.main')
        self.running = False
        self._main_thread: Optional[threading.Thread] = None
        
        self.logger.info("Voice Assistant initialized with dependency injection")
    
    def start(self) -> None:
        """Start the voice assistant in the main thread.""" 
        if self.running:
            self.logger.warning("Voice Assistant is already running")
            return
        
        self.running = True
        self.logger.info("Starting Voice Assistant...")
        
        try:
            self._run_main_loop()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, stopping...")
            self.stop()
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            self.stop()
            raise VoiceAssistantError(f"Voice Assistant crashed: {e}")
    
    def start_async(self) -> None:
        """Start the voice assistant in a separate thread."""
        if self.running:
            self.logger.warning("Voice Assistant is already running")
            return
        
        self.running = True
        self.logger.info("Starting Voice Assistant in background thread...")
        
        self._main_thread = threading.Thread(target=self._run_main_loop, daemon=True)
        self._main_thread.start()
    
    def stop(self) -> None:
        """Stop the voice assistant."""
        if not self.running:
            return
        
        self.logger.info("Stopping Voice Assistant...")
        self.running = False
        
        # Wait for main thread to finish if running async
        if self._main_thread and self._main_thread.is_alive():
            self._main_thread.join(timeout=5.0)
            if self._main_thread.is_alive():
                self.logger.warning("Main thread did not stop gracefully")
        
        self.logger.info("Voice Assistant stopped")
    
    def _run_main_loop(self) -> None:
        """Main loop - continuously listen for voice commands."""
        self.logger.info("Voice Assistant main loop started. Listening for commands...")
        
        while self.running:
            try:
                # Listen for command
                command = self.speech_service.listen_for_command()
                
                if command and self.running:
                    # Process command in separate thread to avoid blocking
                    command_thread = threading.Thread(
                        target=self._process_command_safely,
                        args=(command,),
                        daemon=True
                    )
                    command_thread.start()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)  # Brief pause before continuing
    
    def _process_command_safely(self, command: str) -> None:
        """Process command with error handling."""
        try:
            self.logger.info(f"Processing command: {command}")
            
            # Execute command through registry
            result = self.command_registry.execute_command(command)
            
            if result:
                self.logger.info(f"Command executed successfully: {result}")
            else:
                self.logger.info("Command executed successfully")
                
        except CommandExecutionError as e:
            self.logger.error(f"Command execution error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing command '{command}': {e}")
    
    def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process a single command (for API/testing usage)."""
        try:
            self.logger.info(f"Processing single command: {command}")
            return self.command_registry.execute_command(command, context)
        except Exception as e:
            self.logger.error(f"Error processing command '{command}': {e}")
            raise
    
    def is_running(self) -> bool:
        """Check if the assistant is currently running."""
        return self.running
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the voice assistant."""
        return {
            'running': self.running,
            'config_loaded': self.config_manager.config is not None,
            'microphone_available': self.speech_service.test_microphone(),
            'registered_commands': len(self.command_registry._commands),
            'command_handlers': list(self.command_registry.list_commands().keys())
        }
    
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered commands."""
        return self.command_registry.list_commands()
    
    def calibrate_microphone(self, duration: float = 2.0) -> None:
        """Calibrate microphone for better speech recognition."""
        try:
            self.logger.info("Calibrating microphone...")
            self.speech_service.calibrate_microphone(duration)
            self.logger.info("Microphone calibration completed")
        except Exception as e:
            self.logger.error(f"Microphone calibration failed: {e}")
            raise VoiceAssistantError(f"Microphone calibration failed: {e}")
    
    def get_microphone_info(self) -> Dict[str, Any]:
        """Get microphone information."""
        try:
            return self.speech_service.get_microphone_info()
        except Exception as e:
            self.logger.error(f"Failed to get microphone info: {e}")
            return {'error': str(e)}
    
    def get_speech_stats(self) -> Dict[str, Any]:
        """Get speech recognition statistics."""
        try:
            return self.speech_service.get_recognition_stats()
        except Exception as e:
            self.logger.error(f"Failed to get speech stats: {e}")
            return {'error': str(e)}
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        try:
            self.logger.info("Reloading configuration...")
            self.config_manager.load_config()
            self.logger.info("Configuration reloaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            raise VoiceAssistantError(f"Configuration reload failed: {e}")
    
    def set_log_level(self, level: str) -> None:
        """Set logging level."""
        try:
            self.logging_service.set_log_level(level)
            self.logger.info(f"Log level set to: {level}")
        except Exception as e:
            self.logger.error(f"Failed to set log level: {e}")
            raise VoiceAssistantError(f"Failed to set log level: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()