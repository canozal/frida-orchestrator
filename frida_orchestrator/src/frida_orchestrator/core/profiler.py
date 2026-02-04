from dataclasses import dataclass
from .device_manager import Device

@dataclass
class DeviceProfile:
    os_name: str
    os_version: str
    abi: str
    is_rooted: bool
    ro_build_fingerprint: str = ""

class DeviceProfiler:
    """
    Inspects a connected device to gather OS and hardware details.
    """
    
    def profile(self, device: Device) -> DeviceProfile:
        if device.platform == 'android':
            return self._profile_android(device)
        elif device.platform == 'ios':
            return self._profile_ios(device)
        else:
            raise ValueError(f"Unknown platform: {device.platform}")

    def _profile_android(self, device: Device) -> DeviceProfile:
        import subprocess
        
        try:
            # Helper to run adb shell commands
            def adb_shell(cmd):
                full_cmd = ['adb', '-s', device.device_id, 'shell'] + cmd.split()
                return subprocess.check_output(full_cmd, stderr=subprocess.STDOUT, text=True).strip()

            # 1. Get OS Version
            os_version = adb_shell("getprop ro.build.version.release")
            
            # 2. Get ABI (CPU Architecture)
            # Try primary first, then fallback
            abi = adb_shell("getprop ro.product.cpu.abi")
            if not abi:
                abi = adb_shell("getprop ro.product.cpu.abi2")
            
            # 3. Get Build Fingerprint (useful for unique ID)
            fingerprint = adb_shell("getprop ro.build.fingerprint")

            # 4. Check Root
            # Simple heuristic: check if 'su' exists in PATH or if adb is running as root
            is_rooted = False
            try:
                # Check 1: adb root access
                id_out = adb_shell("id")
                if "uid=0(root)" in id_out:
                    is_rooted = True
                else:
                    # Check 2: su binary
                    # 'which' might not be installed, try simple execution
                    try:
                        subprocess.check_call(['adb', '-s', device.device_id, 'shell', 'su -c id'], 
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        is_rooted = True
                    except subprocess.CalledProcessError:
                        pass
            except Exception:
                pass

            return DeviceProfile(
                os_name="Android",
                os_version=os_version,
                abi=abi,
                is_rooted=is_rooted,
                ro_build_fingerprint=fingerprint
            )

        except subprocess.CalledProcessError as e:
            # Fallback if communication fails
            print(f"Error profiling device: {e}")
            return DeviceProfile("Android", "0.0", "unknown", False)

    def _profile_ios(self, device: Device) -> DeviceProfile:
        # TODO: Run ideviceinfo
        return DeviceProfile("iOS", "0.0", "arm64", False)
