# Frida Orchestrator - Module Specification

This document breaks down the internal modules and their proposed API surfaces.

## 1. `frida_orchestrator.core.device_manager`

Handles low-level device communication and discovery.

### Classes

*   `DeviceManager`
    *   `list_devices() -> List[Device]`
    *   `wait_for_device(device_id: str, timeout: int)`
*   `Device` (Abstract Base Class)
    *   `id: str`
    *   `platform: str` ('android', 'ios')
    *   `connection_type: str` ('usb', 'network')
    *   `push_file(local_path, remote_path)`
    *   `execute_command(cmd) -> (stdout, stderr)`

## 2. `frida_orchestrator.core.profiler`

Responsible for interrogating a connected device to build a profile.

### Classes

*   `DeviceProfiler`
    *   `profile(device: Device) -> DeviceProfile`
*   `DeviceProfile` (Dataclass)
    *   `os_name: str` (e.g., "Android", "iOS")
    *   `os_version: str` (e.g., "14.0", "16.2")
    *   `abi: str` (e.g., "arm64-v8a", "x86_64")
    *   `is_rooted: bool`
    *   `ro_build_fingerprint: str` (Android only - useful for tracking)

### Logic Details
*   **Android:** standard `adb shell getprop ro.product.cpu.abi`, `adb shell getprop ro.build.version.release`. Root check: check for `su` binary or typical root paths.
*   **iOS:** `ideviceinfo` parsing. Jailbreak check: check for Cydia/Sileo URL schemes (if possible via simple means) or filesystem checks if accessible.

## 3. `frida_orchestrator.core.frida_manager`

Manages the valid versions and artifacts.

### Classes

*   `FridaResolver`
    *   `get_compatible_version(profile: DeviceProfile) -> str`
    *   *Logic:* Maintain a local lookup table or query an external JSON (if updated) matching Android versions to recommended Frida versions (though usually "latest" is fine, older Androids might need legacy Frida).
*   `FridaInstaller`
    *   `install(device: Device, version: str, type: 'server'|'gadget')`
    *   *Workflow:*
        1.  Check local cache for `frida-server-{version}-{platform}-{arch}`.
        2.  If missing, download from GitHub Releases.
        3.  Decompress (xz/gz).
        4.  `device.push_file()`.
        5.  **Android:** `adb shell "chmod 755 /data/local/tmp/frida-server"`.
        6.  **iOS:** (More complex, usually involves Cydia/Deb installation or manually placing in `/usr/bin` if SSH is available). *Keep MVP simple: Support SSH-based iOS devices.*

## 4. `frida_orchestrator.cli`

The user entry point.

### Commands
*   `frida-orch scan` : List detected devices.
*   `frida-orch profile <device_id>` : Dump JSON profile.
*   `frida-orch prepare <device_id>` : Auto-install server.
*   `frida-orch cleanup <device_id>` : Kill server, remove temp files.

## Directory Structure Design

```text
frida_orchestrator/
├── __init__.py
├── main.py              # Entry point
├── cli/
│   ├── __init__.py
│   └── commands.py      # Click/Argparse definitions
├── core/
│   ├── __init__.py
│   ├── device_manager.py
│   ├── profiler.py
│   ├── frida_manager.py
│   └── utils.py         # Subprocess wrappers, logging
├── data/
│   └── compatibility.json
└── ui/
    └── (Future GUI code)
```
