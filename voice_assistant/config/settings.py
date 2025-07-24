"""
Configuration management with validation for the Voice Assistant.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.exceptions import ConfigurationError


@dataclass
class SmartDevice:
    """Configuration for a smart device."""
    name: str
    device_id: str
    ip_address: str
    local_key: str
    device_type: str = "outlet"
    
    def __post_init__(self) -> None:
        """Validate device configuration."""
        if not all([self.name, self.device_id, self.ip_address, self.local_key]):
            raise ConfigurationError("All device fields are required")


@dataclass
class AssistantSettings:
    """General settings for the voice assistant."""
    speech_timeout: int = 5
    phrase_time_limit: int = 5
    language: str = "id-ID"
    log_level: str = "INFO"
    screenshots_folder: str = "screenshots"
    wake_word: str = "peter"
    
    def __post_init__(self) -> None:
        """Validate settings."""
        if self.speech_timeout <= 0 or self.phrase_time_limit <= 0:
            raise ConfigurationError("Timeout values must be positive")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ConfigurationError("Invalid log level")


@dataclass
class Configuration:
    """Main configuration class."""
    smart_devices: List[SmartDevice] = field(default_factory=list)
    settings: AssistantSettings = field(default_factory=AssistantSettings)
    application_shortcuts: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Configuration':
        """Load configuration from JSON file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with config_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error reading config file: {e}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Configuration':
        """Create configuration from dictionary."""
        try:
            # Parse smart devices
            devices_data = data.get('smart_devices', [])
            smart_devices = [SmartDevice(**device) for device in devices_data]
            
            # Parse settings
            settings_data = data.get('settings', {})
            settings = AssistantSettings(**settings_data)
            
            # Parse application shortcuts
            app_shortcuts = data.get('application_shortcuts', {})
            
            return cls(
                smart_devices=smart_devices,
                settings=settings,
                application_shortcuts=app_shortcuts
            )
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration format: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'smart_devices': [
                {
                    'name': device.name,
                    'device_id': device.device_id,
                    'ip_address': device.ip_address,
                    'local_key': device.local_key,
                    'device_type': device.device_type
                }
                for device in self.smart_devices
            ],
            'settings': {
                'speech_timeout': self.settings.speech_timeout,
                'phrase_time_limit': self.settings.phrase_time_limit,
                'language': self.settings.language,
                'log_level': self.settings.log_level,
                'screenshots_folder': self.settings.screenshots_folder
            },
            'application_shortcuts': self.application_shortcuts
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with config_file.open('w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(f"Error saving config file: {e}")
    
    def validate(self) -> None:
        """Validate the entire configuration."""
        for device in self.smart_devices:
            device.__post_init__()
        
        self.settings.__post_init__()


class ConfigManager:
    """Manages configuration loading, validation, and saving."""
    
    def __init__(self, config_path: str = "config/devices.json"):
        self.config_path = config_path
        self._config: Optional[Configuration] = None
    
    @property
    def config(self) -> Configuration:
        """Get the current configuration, loading if necessary."""
        if self._config is None:
            self.load_config()
        return self._config
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                self._config = Configuration.from_file(self.config_path)
            else:
                self._config = Configuration()
                self.create_default_config()
            
            self._config.validate()
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        if self._config is None:
            raise ConfigurationError("No configuration to save")
        
        self._config.save_to_file(self.config_path)
    
    def create_default_config(self) -> None:
        """Create and save default configuration."""
        default_config = Configuration(
            smart_devices=[
                SmartDevice(
                    name="Smart Plug 1",
                    device_id="your_device_id_here",
                    ip_address="192.168.1.100",
                    local_key="your_local_key_here",
                    device_type="outlet"
                ),
                SmartDevice(
                    name="Smart Lamp",
                    device_id="another_device_id_here",
                    ip_address="192.168.1.101",
                    local_key="another_local_key_here",
                    device_type="light"
                )
            ],
            settings=AssistantSettings(),
            application_shortcuts={
                "vs code": "code",
                "visual studio code": "code",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe"
            }
        )
        
        self._config = default_config
        self.save_config()
    
    def get_device_by_name(self, name: str) -> Optional[SmartDevice]:
        """Get a smart device by name."""
        for device in self.config.smart_devices:
            if device.name.lower() == name.lower():
                return device
        return None
    
    def get_application_command(self, app_name: str) -> Optional[str]:
        """Get application command by name."""
        return self.config.application_shortcuts.get(app_name.lower())