#!/usr/bin/env python3
"""
Main entry point for the Voice Assistant application.
"""

import sys
import argparse
from pathlib import Path

# Add the package to sys.path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from voice_assistant.core.factory import AssistantFactory
from voice_assistant.core.exceptions import VoiceAssistantError


def main():
    """Main entry point for the Voice Assistant."""
    parser = argparse.ArgumentParser(
        description="Voice-Controlled Personal Assistant for Windows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with default config
  python main.py -c custom.json     # Start with custom config
  python main.py --calibrate        # Calibrate microphone and exit
  python main.py --test-config      # Test configuration and exit
  python main.py --list-commands    # List all available commands
        """
    )
    
    parser.add_argument(
        "-c", "--config",
        default="config/devices.json",
        help="Path to configuration file (default: config/devices.json)"
    )
    
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Calibrate microphone for ambient noise and exit"
    )
    
    parser.add_argument(
        "--test-config",
        action="store_true",
        help="Test configuration file and exit"
    )
    
    parser.add_argument(
        "--list-commands",
        action="store_true",
        help="List all available voice commands and exit"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Voice Assistant 1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Create assistant factory
        factory = AssistantFactory(args.config)
        
        # Handle special actions
        if args.test_config:
            return test_configuration(factory)
        
        if args.calibrate:
            return calibrate_microphone(factory)
        
        if args.list_commands:
            return list_commands(factory)
        
        # Set log level if specified
        if args.log_level:
            factory.logging_service.set_log_level(args.log_level)
        
        # Create and start assistant
        print("Starting Voice Assistant...")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        with factory.create_assistant() as assistant:
            assistant.start()
    
    except KeyboardInterrupt:
        print("\nShutting down Voice Assistant...")
        return 0
    
    except VoiceAssistantError as e:
        print(f"Voice Assistant Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def test_configuration(factory: AssistantFactory) -> int:
    """Test configuration file."""
    try:
        print("Testing configuration...")
        
        if factory.validate_configuration():
            print("✓ Configuration is valid")
            
            # Display configuration summary
            config = factory.config_manager.config
            print(f"✓ Smart devices configured: {len(config.smart_devices)}")
            print(f"✓ Application shortcuts: {len(config.application_shortcuts)}")
            print(f"✓ Speech timeout: {config.settings.speech_timeout}s")
            print(f"✓ Language: {config.settings.language}")
            
            return 0
        else:
            print("✗ Configuration validation failed")
            return 1
    
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return 1


def calibrate_microphone(factory: AssistantFactory) -> int:
    """Calibrate microphone."""
    try:
        print("Calibrating microphone...")
        print("Please stay quiet for a few seconds...")
        
        assistant = factory.create_assistant()
        assistant.calibrate_microphone(duration=3.0)
        
        print("✓ Microphone calibration completed")
        
        # Test microphone
        print("Testing microphone...")
        mic_info = assistant.get_microphone_info()
        if 'error' not in mic_info:
            print(f"✓ Available microphones: {len(mic_info['available_microphones'])}")
            print(f"✓ Default microphone: {mic_info['default_microphone']}")
        else:
            print(f"✗ Microphone test failed: {mic_info['error']}")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"✗ Microphone calibration failed: {e}")
        return 1


def list_commands(factory: AssistantFactory) -> int:
    """List all available commands."""
    try:
        print("Available Voice Commands:")
        print("=" * 50)
        
        assistant = factory.create_assistant()
        commands_info = assistant.get_commands_info()
        
        for handler_name, info in commands_info.items():
            print(f"\n{handler_name}:")
            print(f"  Description: {info['description']}")
            print("  Patterns:")
            for pattern in info['patterns']:
                print(f"    - {pattern}")
        
        print("\nNote: Use commands in Bahasa Indonesia as shown above.")
        return 0
    
    except Exception as e:
        print(f"✗ Failed to list commands: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())