"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from voice_assistant.config.settings import ConfigManager, Configuration
from voice_assistant.core.factory import AssistantFactory


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.json"
        
        # Create default configuration
        config = Configuration()
        config.save_to_file(str(config_path))
        
        yield str(config_path)


@pytest.fixture
def config_manager(temp_config_file):
    """Create a ConfigManager instance for testing."""
    return ConfigManager(temp_config_file)


@pytest.fixture
def mock_speech_service():
    """Create a mock speech recognition service."""
    mock_service = Mock()
    mock_service.listen_for_command.return_value = None
    mock_service.test_microphone.return_value = True
    mock_service.calibrate_microphone.return_value = None
    mock_service.get_microphone_info.return_value = {
        'available_microphones': ['Default Microphone'],
        'default_microphone': 'Default Microphone',
        'total_count': 1
    }
    mock_service.get_recognition_stats.return_value = {
        'energy_threshold': 300,
        'dynamic_energy_threshold': True
    }
    return mock_service


@pytest.fixture
def mock_logging_service():
    """Create a mock logging service."""
    mock_service = Mock()
    mock_logger = Mock()
    mock_service.get_logger.return_value = mock_logger
    return mock_service


@pytest.fixture
def assistant_factory(temp_config_file):
    """Create an AssistantFactory for testing."""
    return AssistantFactory(temp_config_file)


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        "smart_devices": [
            {
                "name": "Test Smart Plug",
                "device_id": "test123",
                "ip_address": "192.168.1.100",
                "local_key": "testkey123",
                "device_type": "outlet"
            }
        ],
        "settings": {
            "speech_timeout": 5,
            "phrase_time_limit": 5,
            "language": "id-ID",
            "log_level": "INFO",
            "screenshots_folder": "screenshots"
        },
        "application_shortcuts": {
            "notepad": "notepad.exe",
            "calculator": "calc.exe"
        }
    }