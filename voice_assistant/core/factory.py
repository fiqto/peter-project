"""
Factory pattern implementation for creating Voice Assistant components.
"""

from typing import Optional
import logging

from ..config.settings import ConfigManager
from ..services.speech_service import SpeechRecognitionService
from ..services.logging_service import LoggingService
from ..commands import (
    CommandRegistry,
    SystemControlCommand,
    BrowserCommand,
    ApplicationCommand,
    SmartDeviceCommand,
    UtilityCommand
)
from .exceptions import ConfigurationError


class AssistantFactory:
    """Factory for creating Voice Assistant components with dependency injection."""
    
    def __init__(self, config_path: str = "config/devices.json"):
        self.config_path = config_path
        self._config_manager: Optional[ConfigManager] = None
        self._logging_service: Optional[LoggingService] = None
        self._speech_service: Optional[SpeechRecognitionService] = None
        self._command_registry: Optional[CommandRegistry] = None
    
    @property
    def config_manager(self) -> ConfigManager:
        """Get or create config manager instance."""
        if self._config_manager is None:
            try:
                self._config_manager = ConfigManager(self.config_path)
            except Exception as e:
                raise ConfigurationError(f"Failed to create config manager: {e}")
        return self._config_manager
    
    @property
    def logging_service(self) -> LoggingService:
        """Get or create logging service instance."""
        if self._logging_service is None:
            try:
                self._logging_service = LoggingService(self.config_manager)
            except Exception as e:
                raise ConfigurationError(f"Failed to create logging service: {e}")
        return self._logging_service
    
    @property
    def speech_service(self) -> SpeechRecognitionService:
        """Get or create speech recognition service instance."""
        if self._speech_service is None:
            try:
                self._speech_service = SpeechRecognitionService(self.config_manager)
            except Exception as e:
                raise ConfigurationError(f"Failed to create speech service: {e}")
        return self._speech_service
    
    @property
    def command_registry(self) -> CommandRegistry:
        """Get or create command registry with all commands registered."""
        if self._command_registry is None:
            try:
                self._command_registry = self._create_command_registry()
            except Exception as e:
                raise ConfigurationError(f"Failed to create command registry: {e}")
        return self._command_registry
    
    def _create_command_registry(self) -> CommandRegistry:
        """Create and configure command registry with all command handlers."""
        # Get wake word from configuration
        wake_word = self.config_manager.config.settings.wake_word
        registry = CommandRegistry(wake_word=wake_word)
        logger = self.logging_service.get_logger('voice_assistant.factory')
        
        try:
            # Create command handlers with dependency injection
            system_command = SystemControlCommand(logger)
            browser_command = BrowserCommand(logger)
            app_command = ApplicationCommand(self.config_manager, logger)
            device_command = SmartDeviceCommand(self.config_manager, logger)
            utility_command = UtilityCommand(self.config_manager, logger)
            
            # Register all commands
            registry.register(system_command)
            registry.register(browser_command)
            registry.register(app_command)
            registry.register(device_command)
            registry.register(utility_command)
            
            logger.info("Command registry created with all handlers registered")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to create command registry: {e}")
            raise
    
    def create_assistant(self) -> 'VoiceAssistant':
        """Create a fully configured Voice Assistant instance."""
        # Import here to avoid circular imports
        from .assistant import VoiceAssistant
        
        try:
            # Ensure all services are initialized
            config_manager = self.config_manager
            logging_service = self.logging_service
            speech_service = self.speech_service
            command_registry = self.command_registry
            
            # Create assistant with injected dependencies
            assistant = VoiceAssistant(
                config_manager=config_manager,
                speech_service=speech_service,
                command_registry=command_registry,
                logging_service=logging_service
            )
            
            logger = logging_service.get_logger('voice_assistant.factory')
            logger.info("Voice Assistant created successfully")
            
            return assistant
            
        except Exception as e:
            raise ConfigurationError(f"Failed to create Voice Assistant: {e}")
    
    def reset_services(self) -> None:
        """Reset all service instances (useful for testing or reconfiguration)."""
        self._config_manager = None
        self._logging_service = None
        self._speech_service = None
        self._command_registry = None
    
    def validate_configuration(self) -> bool:
        """Validate the current configuration."""
        try:
            config = self.config_manager.config
            config.validate()
            return True
        except Exception as e:
            logger = logging.getLogger('voice_assistant.factory')
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_service_status(self) -> dict:
        """Get status of all services."""
        status = {
            'config_manager': self._config_manager is not None,
            'logging_service': self._logging_service is not None,
            'speech_service': self._speech_service is not None,
            'command_registry': self._command_registry is not None
        }
        
        # Test speech service if available
        if self._speech_service:
            status['microphone_available'] = self._speech_service.test_microphone()
        
        return status