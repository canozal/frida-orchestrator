from typing import List, Optional
import subprocess

class Device:
    def __init__(self, device_id: str, platform: str, connection_type: str = 'usb', model: str = "Unknown"):
        self.device_id = device_id
        self.platform = platform
        self.connection_type = connection_type
        self.model = model

    def __repr__(self):
        return f"<Device {self.platform}:{self.device_id} ({self.model})>"

class DeviceManager:
    """
    Handles detection of Android and iOS devices.
    """
    
    def list_devices(self) -> List[Device]:
        devices = []
        devices.extend(self._scan_android())
        devices.extend(self._scan_ios())
        return devices

    def _scan_android(self) -> List[Device]:
        """
        Scans for Android devices using `adb devices -l`.
        """
        try:
            # Run adb command
            result = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            devices = []
            # Skip the first line usually "List of devices attached"
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                parts = line.split()
                # Format: "Serial DeviceInfo..."
                # Example: "12345678 device product:flame model:Pixel_4 device:flame transport_id:1"
                
                if len(parts) >= 2:
                    serial = parts[0]
                    state = parts[1]
                    
                    if state == 'device':
                        # Try to extract model from extra info
                        model = "Android Device"
                        for part in parts[2:]:
                            if part.startswith("model:"):
                                model = part.split(":")[1].replace("_", " ")
                        
                        device = Device(device_id=serial, platform="android", connection_type="usb")
                        # We can attach the model to the device object dynamically or update the class
                        device.model = model 
                        devices.append(device)
            
            return devices

        except FileNotFoundError:
            # ADB not installed or not in PATH
            # In a real app we might log a warning or return specific error state
            return []
        except subprocess.CalledProcessError:
            return []

    def _scan_ios(self) -> List[Device]:
        # TODO: Implement 'idevice_id -l' parsing
        return []
