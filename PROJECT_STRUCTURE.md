# Project Structure

This document explains the organization and architecture of the Voice Assistant project.

## 📁 Directory Structure

```
voice-assistant/
├── 📄 README.md                    # Main project documentation
├── 📄 CLAUDE.md                    # Development guidance for AI assistants
├── 📄 LICENSE                      # MIT License
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Package installation configuration
├── 📄 main.py                      # CLI entry point
├── 📄 setup_config.py              # Configuration setup helper
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 .gitignore                   # Git ignore rules
├── 📁 config/                      # Configuration files
│   ├── devices.sample.json         # Sample configuration (commit to git)
│   └── devices.json                # Actual configuration (git ignored)
└── 📁 voice_assistant/             # Main Python package
    ├── __init__.py                 # Package initialization
    ├── 📁 core/                    # Core application components
    │   ├── __init__.py
    │   ├── assistant.py            # Main VoiceAssistant class
    │   ├── factory.py              # Dependency injection factory
    │   └── exceptions.py           # Custom exception classes
    ├── 📁 commands/                # Command handlers (extensible)
    │   ├── __init__.py
    │   ├── base.py                 # Base command interface & registry
    │   ├── system_commands.py      # System control commands
    │   ├── browser_commands.py     # Web browsing commands
    │   ├── application_commands.py # Application launcher
    │   ├── smart_device_commands.py # Smart device control
    │   └── utility_commands.py     # Utility functions
    ├── 📁 services/                # Service layer
    │   ├── __init__.py
    │   ├── speech_service.py       # Speech recognition
    │   └── logging_service.py      # Logging management
    ├── 📁 config/                  # Configuration management
    │   ├── __init__.py
    │   └── settings.py             # Configuration classes
    └── 📁 tests/                   # Test suite
        ├── __init__.py
        ├── conftest.py             # Test fixtures
        ├── test_config.py          # Configuration tests
        └── test_commands.py        # Command handler tests
```

## 🏗️ Architecture Overview

### Core Design Patterns

1. **Dependency Injection**: Factory pattern manages component creation
2. **Command Pattern**: Extensible command handling system
3. **Service Layer**: Abstracted services for speech recognition and logging
4. **Configuration Management**: Type-safe configuration with validation

### Key Components

- **AssistantFactory**: Creates and wires all components with dependency injection
- **CommandRegistry**: Manages command handlers with wake word validation
- **VoiceAssistant**: Main orchestrator that coordinates all services
- **ConfigManager**: Handles configuration loading, validation, and saving

## 🔧 Development Files

### Files to Commit to Git
- ✅ All source code (`voice_assistant/`)
- ✅ Documentation (`README.md`, `CLAUDE.md`, `PROJECT_STRUCTURE.md`)
- ✅ Configuration (`requirements.txt`, `setup.py`, `.gitignore`)
- ✅ Sample config (`config/devices.sample.json`)
- ✅ Tests (`voice_assistant/tests/`)
- ✅ License (`LICENSE`)

### Files Ignored by Git
- ❌ Personal configuration (`config/devices.json`)
- ❌ Log files (`logs/`)
- ❌ Screenshots (`screenshots/`)
- ❌ Build artifacts (`*.egg-info/`, `build/`, `dist/`)
- ❌ Python cache (`__pycache__/`, `*.pyc`)
- ❌ Virtual environments (`.venv/`, `env/`)
- ❌ IDE files (`.vscode/`, `.idea/`)

## 🚀 Getting Started

1. **Clone Repository**: `git clone <repo-url>`
2. **Setup Environment**: `python -m venv .venv && source .venv/bin/activate`
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Setup Configuration**: `python setup_config.py`
5. **Configure Settings**: Edit `config/devices.json` with your settings
6. **Test Installation**: `python main.py --test-config`
7. **Start Assistant**: `python main.py`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=voice_assistant

# Run specific test file
pytest voice_assistant/tests/test_config.py
```

## 📚 Adding New Features

### Adding New Voice Commands

1. Create new command class in `voice_assistant/commands/`
2. Inherit from `Command` base class
3. Implement required methods (`can_handle`, `execute`, etc.)
4. Register in `AssistantFactory._create_command_registry()`
5. Add tests in `voice_assistant/tests/`

### Configuration Changes

1. Update dataclasses in `voice_assistant/config/settings.py`
2. Update sample configuration in `config/devices.sample.json`
3. Add validation in `__post_init__` methods
4. Update documentation

This structure provides a clean, maintainable, and extensible foundation for the voice assistant project.