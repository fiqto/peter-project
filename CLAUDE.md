# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a voice-controlled personal assistant for Windows with Bahasa Indonesia support. It uses speech recognition to process voice commands and execute system operations, web browsing, application launching, smart device control, and utility functions.

## Development Commands

### Running the Application
```bash
# Start voice assistant with default config
python main.py

# Start with custom configuration
python main.py -c config/my_config.json

# Test configuration validity
python main.py --test-config

# Calibrate microphone for ambient noise
python main.py --calibrate

# List all available voice commands
python main.py --list-commands
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=voice_assistant

# Run specific test file
pytest voice_assistant/tests/test_config.py

# Run specific test method
pytest voice_assistant/tests/test_commands.py::TestBrowserCommand::test_open_youtube
```

### Code Quality
```bash
# Format code
black voice_assistant/

# Sort imports
isort voice_assistant/

# Lint code
flake8 voice_assistant/

# Type checking
mypy voice_assistant/
```

### Package Management
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

### Core Design Pattern: Dependency Injection with Factory Pattern

The application is built around a central `AssistantFactory` that manages all component creation and dependency injection. This factory creates:

- **ConfigManager**: Handles JSON configuration with validation using dataclasses
- **SpeechRecognitionService**: Manages microphone input and Google Speech API
- **LoggingService**: Provides structured logging with rotation
- **CommandRegistry**: Registry pattern for extensible command handling
- **VoiceAssistant**: Main orchestrator that ties everything together

### Command Pattern Implementation

All voice commands inherit from the abstract `Command` base class and must implement:
- `can_handle(command: str) -> bool`: Pattern matching for command recognition
- `execute(command: str, context=None) -> Any`: Command execution logic
- `command_patterns`: List of supported command patterns
- `description`: Human-readable description

Commands are automatically registered in the `CommandRegistry` via the factory pattern.

### Configuration Architecture

Uses a hierarchical dataclass-based configuration system:
- `Configuration`: Root configuration container
- `SmartDevice`: Individual smart device settings with validation
- `AssistantSettings`: General application settings (timeouts, language, logging)

Configuration is validated at load time using `__post_init__` methods in dataclasses.

### Service Layer Pattern

Services provide abstracted interfaces for:
- **SpeechRecognitionService**: Microphone management and speech-to-text conversion
- **LoggingService**: Centralized logging with configurable levels and rotation

### Error Handling Strategy

Custom exception hierarchy rooted at `VoiceAssistantError`:
- `ConfigurationError`: Config loading/validation issues
- `SpeechRecognitionError`: Speech processing problems
- `CommandExecutionError`: Command execution failures
- `DeviceConnectionError`: Smart device connectivity issues
- `ApplicationLaunchError`: App launching problems
- `SystemCommandError`: System operation failures

## Key Implementation Details

### Command Registration Flow
1. Factory creates individual command instances (SystemControlCommand, BrowserCommand, etc.)
2. Each command receives injected dependencies (ConfigManager, logger)
3. CommandRegistry is created with wake word from configuration (default: "peter")
4. Commands are registered in CommandRegistry during factory initialization
5. Registry validates wake word presence before routing commands to handlers

### Speech Recognition Pipeline
1. SpeechRecognitionService continuously listens via Google Speech API
2. Recognized text is passed to CommandRegistry
3. Registry validates wake word presence (configurable, default: "peter")
4. Wake word is stripped from command before handler matching
5. Registry finds matching command handler via `can_handle()` method
6. Command executes in separate thread to avoid blocking main loop

### Configuration Management Flow
1. ConfigManager loads JSON configuration on startup
2. Creates default config if none exists
3. Validates configuration using dataclass validation
4. Provides type-safe access to configuration throughout application

### Smart Device Integration
Uses TinyTuya library for Tuya-compatible smart device control. Device configuration includes:
- `device_id`: Tuya device identifier
- `ip_address`: Local network IP
- `local_key`: Device-specific encryption key
- `device_type`: Type classification (outlet, light, etc.)

## Adding New Voice Commands

1. **Create Command Handler**: Inherit from `Command` base class in `voice_assistant/commands/`
2. **Implement Required Methods**: `can_handle()`, `execute()`, `command_patterns`, `description`
3. **Register in Factory**: Add command instantiation and registration in `voice_assistant/core/factory.py`
4. **Add Tests**: Create corresponding test class in `voice_assistant/tests/`

Example:
```python
class NewCommand(Command):
    def can_handle(self, command: str) -> bool:
        return "trigger phrase" in command.lower()
    
    def execute(self, command: str, context=None):
        # Implementation
        return "Success message"
```

## Configuration File Structure

The `config/devices.json` file uses this structure:
- `smart_devices[]`: Array of smart device configurations
- `settings`: Application-wide settings (speech timeouts, language, logging)
- `application_shortcuts`: Mapping of voice commands to executable names

## Voice Command Language

All voice commands must start with the wake word "peter" (configurable) and are in Bahasa Indonesia:
- System: "Peter matikan komputer", "Peter tutup semua aplikasi"
- Browser: "Peter buka YouTube", "Peter cari di Google [query]"
- Applications: "Peter jalankan aplikasi [app name]"
- Smart devices: "Peter nyalakan lampu", "Peter matikan lampu"
- Utilities: "Peter ambil screenshot"

Wake word features:
- Case insensitive: "Peter", "peter", "PETER" all work
- Configurable via `settings.wake_word` in configuration
- Commands without wake word are rejected

## Testing Architecture

Uses pytest with fixtures defined in `conftest.py`:
- `temp_config_file`: Temporary configuration for isolated testing
- `config_manager`: ConfigManager instance with test config
- `mock_speech_service`: Mocked speech recognition for unit tests
- `assistant_factory`: Factory instance for integration testing

Tests are organized by component (config, commands) with comprehensive mocking of external dependencies (subprocess, webbrowser, pyautogui, etc.).