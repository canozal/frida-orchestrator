from .profiler import DeviceProfile
from .device_manager import Device

class FridaManager:
    """
    Resolves, downloads, and installs Frida versions.
    """
    
    def resolve_version(self, profile: DeviceProfile) -> str:
        """
        Determines which Frida version to install.
        Strategy:
        1. Try to detect the version of the local 'frida' client tools.
           It is CRITICAL that Client and Server versions match.
        2. Fallback to a hardcoded stable version if local tools are not found.
        """
        import subprocess
        import re

        try:
            # Try getting version from frida-ps
            # Output format is usually just "16.1.4" or similar
            result = subprocess.run(['frida-ps', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                detected = result.stdout.strip()
                # Basic validation: X.Y.Z
                if re.match(r'^\d+\.\d+\.\d+$', detected):
                    print(f"Detected local Frida client: v{detected}. Installing matching server.")
                    return detected
        except FileNotFoundError:
            pass

        print("Warning: Local 'frida-ps' not found or failed. Defaulting to v16.1.4.")
        print("Tip: Install 'frida-tools' locally to ensure compatibility: pip install frida-tools")
        return "16.1.4"

    def ensure_frida_installed(self, device: Device, profile: DeviceProfile) -> bool:
        """
        Main orchestration method for installation.
        """
        version = self.resolve_version(profile)
        arch = self._map_abi_to_arch(profile.abi)
        
        print(f"Resolving Frida: v{version} for {device.platform} ({arch})")
        
        artifact_path = self._download_artifact(version, device.platform, arch)
        if not artifact_path:
            return False
            
        return self._install_artifact(device, artifact_path)

    def _map_abi_to_arch(self, abi: str) -> str:
        if "arm64" in abi:
            return "arm64"
        elif "armeabi" in abi or "armv7" in abi:
            return "arm"
        elif "x86_64" in abi:
            return "x86_64"
        elif "x86" in abi:
            return "x86"
        return "arm64" # Default fallback

    def _download_artifact(self, version: str, platform: str, arch: str) -> str:
        import requests
        import os
        import lzma
        
        # Setup cache dir
        cache_dir = os.path.expanduser("~/.frida_orchestrator/cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Filename format: frida-server-16.1.4-android-arm64.xz
        filename = f"frida-server-{version}-{platform.lower()}-{arch}.xz"
        local_path = os.path.join(cache_dir, filename)
        extracted_path = local_path.replace(".xz", "")
        
        # Return currently extracted file if exists
        if os.path.exists(extracted_path):
            print(f"Using cached artifact: {extracted_path}")
            return extracted_path

        # Download if XZ doesn't exist either
        if not os.path.exists(local_path):
            base_url = f"https://github.com/frida/frida/releases/download/{version}/"
            url = base_url + filename
            print(f"Downloading from {url}...")
            
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            except Exception as e:
                print(f"Download failed: {e}")
                return ""
        
        # Extract XZ
        print(f"Extracting {filename}...")
        try:
            with lzma.open(local_path) as f_in, open(extracted_path, 'wb') as f_out:
                f_out.write(f_in.read())
            return extracted_path
        except Exception as e:
            print(f"Extraction failed: {e}")
            return ""

    def _install_artifact(self, device: Device, local_path: str) -> bool:
        import subprocess
        
        print("Installing Frida Server...")
        remote_path = "/data/local/tmp/frida-server"
        
        try:
            # 1. Push
            subprocess.check_call(['adb', '-s', device.device_id, 'push', local_path, remote_path])
            
            # 2. Chmod
            subprocess.check_call(['adb', '-s', device.device_id, 'shell', f'chmod 755 {remote_path}'])
            
            # 3. kill existing (ignore error)
            subprocess.run(['adb', '-s', device.device_id, 'shell', 'pkill frida-server'], 
                           stderr=subprocess.DEVNULL)
            
            # 4. Run in background (nohup logic via shell magic)
            # We use subprocess.Popen to avoid waiting
            print("Starting Frida Server...")
            subprocess.Popen(['adb', '-s', device.device_id, 'shell', f'{remote_path} &'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("Frida Server started!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Installation failed: {e}")
            return False
