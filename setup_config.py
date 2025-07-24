#!/usr/bin/env python3
"""
Setup script to initialize configuration for Voice Assistant.
"""

import shutil
import os
from pathlib import Path


def setup_configuration():
    """Copy sample configuration to actual config file."""
    sample_config = Path("config/devices.sample.json")
    actual_config = Path("config/devices.json") 
    
    if not sample_config.exists():
        print("❌ Error: config/devices.sample.json not found!")
        return False
    
    if actual_config.exists():
        response = input("⚠️  config/devices.json already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    try:
        # Ensure config directory exists
        actual_config.parent.mkdir(exist_ok=True)
        
        # Copy sample to actual config
        shutil.copy2(sample_config, actual_config)
        
        print("✅ Configuration setup complete!")
        print(f"📝 Please edit {actual_config} with your settings:")
        print("   - Update smart device information")
        print("   - Customize application shortcuts")
        print("   - Adjust speech recognition settings")
        print("   - Change wake word if desired")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up configuration: {e}")
        return False


if __name__ == "__main__":
    print("🎤 Voice Assistant Configuration Setup")
    print("=" * 40)
    setup_configuration()