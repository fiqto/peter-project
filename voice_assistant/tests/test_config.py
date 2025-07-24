"""
Tests for configuration management.
"""

import pytest
import json
import tempfile
from pathlib import Path

from voice_assistant.config.settings import (
    Configuration, 
    ConfigManager, 
    SmartDevice, 
    AssistantSettings
)
from voice_assistant.core.exceptions import ConfigurationError


class TestSmartDevice:
    """Test SmartDevice dataclass."""
    
    def test_valid_device_creation(self):
        """Test creating a valid smart device."""
        device = SmartDevice(
            name="Test Device",
            device_id="test123",
            ip_address="192.168.1.100",
            local_key="testkey123"
        )
        
        assert device.name == "Test Device"
        assert device.device_id == "test123"
        assert device.ip_address == "192.168.1.100"
        assert device.local_key == "testkey123"
        assert device.device_type == "outlet"  # default value
    
    def test_invalid_device_creation(self):
        """Test creating device with missing fields."""
        with pytest.raises(ConfigurationError):
            SmartDevice(
                name="",
                device_id="test123",  
                ip_address="192.168.1.100",
                local_key="testkey123"
            )


class TestAssistantSettings:
    """Test AssistantSettings dataclass."""
    
    def test_default_settings(self):
        """Test default settings creation."""
        settings = AssistantSettings()
        
        assert settings.speech_timeout == 5
        assert settings.phrase_time_limit == 5
        assert settings.language == "id-ID"
        assert settings.log_level == "INFO"
        assert settings.screenshots_folder == "screenshots"
    
    def test_invalid_timeout_values(self):
        """Test invalid timeout values."""
        with pytest.raises(ConfigurationError):
            AssistantSettings(speech_timeout=0)
        
        with pytest.raises(ConfigurationError):
            AssistantSettings(phrase_time_limit=-1)
    
    def test_invalid_log_level(self):
        """Test invalid log level."""
        with pytest.raises(ConfigurationError):
            AssistantSettings(log_level="INVALID")


class TestConfiguration:
    """Test Configuration class."""
    
    def test_default_configuration(self):
        """Test creating default configuration."""
        config = Configuration()
        
        assert config.smart_devices == []
        assert isinstance(config.settings, AssistantSettings)
        assert config.application_shortcuts == {}
    
    def test_from_dict_valid(self):
        """Test creating configuration from valid dictionary."""
        data = {
            "smart_devices": [
                {
                    "name": "Test Device",
                    "device_id": "test123",
                    "ip_address": "192.168.1.100",
                    "local_key": "testkey123",
                    "device_type": "light"
                }
            ],
            "settings": {
                "speech_timeout": 10,
                "language": "en-US"
            },
            "application_shortcuts": {
                "notepad": "notepad.exe"
            }
        }
        
        config = Configuration.from_dict(data)
        
        assert len(config.smart_devices) == 1
        assert config.smart_devices[0].name == "Test Device"
        assert config.settings.speech_timeout == 10
        assert config.settings.language == "en-US"
        assert config.application_shortcuts["notepad"] == "notepad.exe"
    
    def test_from_dict_invalid(self):
        """Test creating configuration from invalid dictionary."""
        data = {
            "smart_devices": [
                {
                    "name": "",  # Invalid empty name
                    "device_id": "test123",
                    "ip_address": "192.168.1.100",
                    "local_key": "testkey123"
                }
            ]
        }
        
        with pytest.raises(ConfigurationError):
            Configuration.from_dict(data)
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        device = SmartDevice(
            name="Test Device",
            device_id="test123",
            ip_address="192.168.1.100",
            local_key="testkey123"
        )
        
        config = Configuration(
            smart_devices=[device],
            application_shortcuts={"notepad": "notepad.exe"}
        )
        
        data = config.to_dict()
        
        assert "smart_devices" in data
        assert "settings" in data
        assert "application_shortcuts" in data
        assert len(data["smart_devices"]) == 1
        assert data["smart_devices"][0]["name"] == "Test Device"


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_config_manager_with_nonexistent_file(self):
        """Test config manager with non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_path))
            
            # Should create default config
            assert isinstance(manager.config, Configuration)
            assert config_path.exists()
    
    def test_config_manager_with_valid_file(self):
        """Test config manager with valid config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            
            # Create test config file
            test_data = {
                "smart_devices": [],
                "settings": {"speech_timeout": 3},
                "application_shortcuts": {}
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_data, f)
            
            manager = ConfigManager(str(config_path))
            assert manager.config.settings.speech_timeout == 3
    
    def test_config_manager_with_invalid_json(self):
        """Test config manager with invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            
            # Create invalid JSON file
            with open(config_path, 'w') as f:
                f.write("invalid json content")
            
            with pytest.raises(ConfigurationError):
                ConfigManager(str(config_path))
    
    def test_save_config(self):
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_path))
            
            # Modify config
            manager.config.settings.speech_timeout = 15
            manager.save_config()
            
            # Load again and verify
            manager2 = ConfigManager(str(config_path))
            assert manager2.config.settings.speech_timeout == 15
    
    def test_get_device_by_name(self):
        """Test getting device by name."""
        device = SmartDevice(
            name="Test Device",
            device_id="test123",
            ip_address="192.168.1.100",
            local_key="testkey123"
        )
        
        config = Configuration(smart_devices=[device])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config.save_to_file(str(config_path))
            
            manager = ConfigManager(str(config_path))
            found_device = manager.get_device_by_name("Test Device")
            
            assert found_device is not None
            assert found_device.name == "Test Device"
            assert found_device.device_id == "test123"
    
    def test_get_application_command(self):
        """Test getting application command."""
        config = Configuration(
            application_shortcuts={"notepad": "notepad.exe"}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config.save_to_file(str(config_path))
            
            manager = ConfigManager(str(config_path))
            command = manager.get_application_command("notepad")
            
            assert command == "notepad.exe"
            assert manager.get_application_command("nonexistent") is None