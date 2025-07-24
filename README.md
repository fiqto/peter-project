# Voice Assistant - Personal Voice-Controlled Assistant

A sophisticated voice-controlled personal assistant for Windows with Bahasa Indonesia support. Control your computer, browse the internet, manage applications, and control smart devices using natural voice commands.

## Features

### 🖥️ System Control
- **Computer Shutdown**: "Matikan komputer"
- **Close Applications**: "Tutup semua aplikasi"  
- **Scheduled Shutdown**: "Timer 30 menit matikan komputer"

### 🌐 Web Browsing
- **YouTube**: "Buka YouTube"
- **Google Search**: "Cari di Google [keywords]"
- **Website Navigation**: "Buka website [name]" (supports GitHub, Facebook, Twitter, etc.)

### 📱 Application Control
- **Launch Apps**: "Jalankan aplikasi [app name]"
- Supports common applications: VS Code, Chrome, Firefox, Office suite, and more

### 🏠 Smart Home Integration
- **Smart Device Control**: "Nyalakan lampu" / "Matikan lampu"
- **TinyTuya Integration**: Control Tuya-compatible smart plugs and lights
- **Device Discovery**: Automatic network device discovery

### 🛠️ Utilities
- **Screenshots**: "Ambil screenshot"
- **Logging & Monitoring**: Comprehensive activity logging

## Architecture

This project follows modern Python best practices with:

- **Modular Design**: Separated concerns with distinct modules
- **Dependency Injection**: Factory pattern for component creation
- **Command Pattern**: Extensible command handling system
- **Configuration Management**: JSON-based configuration with validation
- **Comprehensive Testing**: Unit tests with pytest
- **Type Safety**: Full type hints throughout codebase
- **Error Handling**: Custom exceptions with detailed error messages

## Project Structure

```
voice_assistant/
├── core/                  # Core application components
│   ├── assistant.py       # Main VoiceAssistant class
│   ├── factory.py         # Dependency injection factory
│   └── exceptions.py      # Custom exception classes
├── commands/              # Command handlers
│   ├── base.py           # Base command interface
│   ├── system_commands.py # System control commands
│   ├── browser_commands.py # Web browsing commands
│   ├── application_commands.py # App launcher commands
│   ├── smart_device_commands.py # Smart device commands
│   └── utility_commands.py # Utility commands
├── services/              # Service layer
│   ├── speech_service.py  # Speech recognition service
│   └── logging_service.py # Logging management
├── config/                # Configuration management
│   └── settings.py        # Configuration classes
└── tests/                 # Test suite
    ├── test_config.py     # Configuration tests
    ├── test_commands.py   # Command handler tests
    └── conftest.py        # Test fixtures
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11
- Microphone access
- Internet connection (for Google Speech Recognition)

### Install Dependencies

```bash
# Install the package
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### Setup Configuration

```bash
# Copy sample configuration and customize it
cp config/devices.sample.json config/devices.json

# Edit config/devices.json with your settings:
# - Update smart device IDs, IP addresses, and local keys
# - Customize application shortcuts
# - Adjust speech recognition settings
# - Change wake word if desired (default: "peter")
```

**Note for PyAudio Installation Issues:**

If you encounter issues installing PyAudio:

**Windows:**
```bash
# Install PyAudio from pre-compiled wheel
pip install pipwin
pipwin install pyaudio

# Or download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

**macOS:**
```bash
# Install portaudio first
brew install portaudio
pip install PyAudio
```

**Linux (Ubuntu/Debian):**
```bash
# Install system dependencies
sudo apt-get install python3-pyaudio portaudio19-dev
pip install PyAudio
```

## Quick Start

### 1. Setup Configuration

```bash
# Copy and customize configuration
python setup_config.py

# Or manually:
cp config/devices.sample.json config/devices.json
# Then edit config/devices.json with your settings
```

### 2. Basic Usage

```bash
# Start the voice assistant
python main.py

# Or with custom configuration
python main.py -c config/my_config.json
```

### 3. Test Setup

```bash
# Test configuration
python main.py --test-config

# Calibrate microphone
python main.py --calibrate

# List available commands
python main.py --list-commands
```

## Usage Examples

### Voice Commands (Bahasa Indonesia)

**⚠️ Important: All commands must start with the wake word "Peter"**

```bash
# System Control
"Peter matikan komputer"              # Shutdown immediately
"Peter tutup semua aplikasi"          # Close all apps
"Peter timer 30 menit matikan komputer" # Shutdown in 30 minutes

# Web Browsing  
"Peter buka YouTube"                  # Open YouTube
"Peter cari di Google machine learning" # Search Google
"Peter buka website GitHub"           # Open GitHub

# Applications
"Peter jalankan aplikasi VS Code"     # Launch VS Code
"Peter jalankan aplikasi Chrome"      # Launch Chrome

# Smart Devices
"Peter nyalakan lampu"                # Turn on lights
"Peter matikan lampu"                 # Turn off lights

# Utilities
"Peter ambil screenshot"              # Take screenshot
```

**Wake Word Features:**
- Case insensitive: "Peter", "peter", "PETER" all work
- Handles extra spaces: "  peter   buka youtube" works
- Prevents accidental activation: Commands without "Peter" are ignored

### Programmatic Usage

```python
from voice_assistant.core.factory import AssistantFactory

# Create assistant
factory = AssistantFactory("config/devices.json")
assistant = factory.create_assistant()

# Process single command (must include wake word)
result = assistant.process_command("peter ambil screenshot")

# Start listening (blocking)
assistant.start()

# Or start in background
assistant.start_async()
```

## Auto-Start on Windows

### Method 1: Task Scheduler
1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task → "Voice Assistant"
3. Trigger: "When I log on"
4. Action: Start program → `python.exe`
5. Arguments: `C:\path\to\main.py`

### Method 2: Startup Folder
1. Press `Win+R`, type: `shell:startup`
2. Create batch file:
   ```batch
   @echo off
   cd /d "C:\path\to\voice-assistant"
   python main.py
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=voice_assistant

# Run specific test file
pytest voice_assistant/tests/test_config.py
```

### Adding New Commands

1. **Create Command Handler**:
   ```python
   from voice_assistant.commands.base import Command
   
   class MyCommand(Command):
       def can_handle(self, command: str) -> bool:
           return "my trigger" in command.lower()
       
       def execute(self, command: str, context=None):
           # Your implementation
           return "Command executed"
   ```

2. **Register in Factory**:
   ```python
   # In factory.py
   my_command = MyCommand(logger)
   registry.register(my_command)
   ```

## License

This project is licensed under the MIT License.

---

**Made with ❤️ for voice-controlled automation**