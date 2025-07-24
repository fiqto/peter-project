"""
Smart device control commands implementation.
"""

from typing import Any, Dict, Optional

from .base import Command
from ..core.exceptions import DeviceConnectionError
from ..config.settings import ConfigManager

try:
    import tinytuya
except ImportError:
    tinytuya = None


class SmartDeviceCommand(Command):
    """Handler for smart device control commands."""
    
    def __init__(self, config_manager: ConfigManager, logger: Optional = None):
        super().__init__(logger)
        self.config_manager = config_manager
        
        if not tinytuya:
            self.logger.warning("TinyTuya not installed. Smart device features disabled.")
    
    @property
    def command_patterns(self) -> list[str]:
        return [
            "nyalakan lampu",
            "hidupkan lampu", 
            "matikan lampu",
            "tutup lampu"
        ]
    
    @property
    def description(self) -> str:
        return "Control smart devices: turn lights on/off using TinyTuya"
    
    def can_handle(self, command: str) -> bool:
        """Check if this command can handle the given input."""
        if not tinytuya:
            return False
            
        patterns = [
            "nyalakan lampu",
            "hidupkan lampu",
            "matikan lampu", 
            "tutup lampu"
        ]
        return any(pattern in command.lower() for pattern in patterns)
    
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute smart device command."""
        if not tinytuya:
            raise DeviceConnectionError("TinyTuya not available. Install with: pip install tinytuya")
        
        command_lower = command.lower()
        
        try:
            if any(pattern in command_lower for pattern in ["nyalakan lampu", "hidupkan lampu"]):
                return self._control_device("on")
                
            elif any(pattern in command_lower for pattern in ["matikan lampu", "tutup lampu"]):
                return self._control_device("off")
                
            else:
                raise DeviceConnectionError(f"Unknown smart device command: {command}")
                
        except Exception as e:
            self.logger.error(f"Error executing smart device command '{command}': {e}")
            raise DeviceConnectionError(f"Failed to execute smart device command: {e}")
    
    def _control_device(self, action: str, device_name: Optional[str] = None) -> str:
        """Control smart device."""
        try:
            # Get device configuration
            device = self._get_device(device_name)
            if not device:
                raise DeviceConnectionError("No smart devices configured or device not found")
            
            # Create device connection
            tuya_device = tinytuya.OutletDevice(
                device.device_id,
                device.ip_address,
                device.local_key
            )
            tuya_device.set_version(3.3)
            
            # Execute action
            if action == "on":
                result = tuya_device.turn_on()
                self.logger.info(f"Turned ON device: {device.name}")
                return f"Turned ON {device.name}"
                
            elif action == "off":
                result = tuya_device.turn_off()
                self.logger.info(f"Turned OFF device: {device.name}")
                return f"Turned OFF {device.name}"
                
            else:
                raise DeviceConnectionError(f"Unknown action: {action}")
                
        except Exception as e:
            raise DeviceConnectionError(f"Failed to control device: {e}")
    
    def _get_device(self, device_name: Optional[str] = None):
        """Get device configuration."""
        devices = self.config_manager.config.smart_devices
        
        if not devices:
            return None
        
        if device_name:
            # Look for specific device by name
            for device in devices:
                if device.name.lower() == device_name.lower():
                    return device
            return None
        else:
            # Return first device if no specific name provided
            return devices[0]
    
    def get_device_status(self, device_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of smart device."""
        if not tinytuya:
            raise DeviceConnectionError("TinyTuya not available")
        
        try:
            device = self._get_device(device_name)
            if not device:
                raise DeviceConnectionError("Device not found")
            
            tuya_device = tinytuya.OutletDevice(
                device.device_id,
                device.ip_address,
                device.local_key
            )
            tuya_device.set_version(3.3)
            
            status = tuya_device.status()
            self.logger.info(f"Retrieved status for device: {device.name}")
            
            return {
                'device_name': device.name,
                'device_id': device.device_id,
                'status': status
            }
            
        except Exception as e:
            raise DeviceConnectionError(f"Failed to get device status: {e}")
    
    def discover_devices(self) -> list[Dict[str, Any]]:
        """Discover available Tuya devices on the network."""
        if not tinytuya:
            raise DeviceConnectionError("TinyTuya not available")
        
        try:
            self.logger.info("Starting device discovery...")
            devices = tinytuya.deviceScan(False, 20)  # Scan for 20 seconds
            
            discovered = []
            for device_id, device_info in devices.items():
                discovered.append({
                    'device_id': device_id,
                    'ip_address': device_info.get('ip', 'unknown'),
                    'name': device_info.get('name', 'Unknown Device'),
                    'version': device_info.get('version', 'unknown')
                })
            
            self.logger.info(f"Discovered {len(discovered)} devices")
            return discovered
            
        except Exception as e:
            raise DeviceConnectionError(f"Failed to discover devices: {e}")
    
    def test_device_connection(self, device_name: Optional[str] = None) -> bool:
        """Test connection to a smart device."""
        if not tinytuya:
            return False
        
        try:
            device = self._get_device(device_name)
            if not device:
                return False
            
            tuya_device = tinytuya.OutletDevice(
                device.device_id,
                device.ip_address,
                device.local_key
            )
            tuya_device.set_version(3.3)
            
            # Try to get device status to test connection
            status = tuya_device.status()
            return status is not None
            
        except Exception as e:
            self.logger.error(f"Device connection test failed: {e}")
            return False
    
    def list_configured_devices(self) -> list[Dict[str, str]]:
        """List all configured smart devices."""
        devices = []
        for device in self.config_manager.config.smart_devices:
            devices.append({
                'name': device.name,
                'device_id': device.device_id,
                'ip_address': device.ip_address,
                'device_type': device.device_type
            })
        return devices