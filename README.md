# Frida Orchestrator

**Frida Orchestrator** is a cross-platform desktop tool designed for security researchers and mobile pentesters. It automates the tedious process of setting up the Frida instrumentation environment on Android devices.

## 🚀 Features

*   **Automated Device Discovery:** Automatically detects connected Android devices via ADB.
*   **Intelligent Profiling:** Identifies device architecture (ARM64, x86, etc.), Android version, and Root status.
*   **Version Matching:** Automatically detects your local `frida-tools` version and installs the *exact matching* `frida-server` binary to the device.
*   **One-Click Setup:** Downloads, pushes, sets permissions, and starts the Frida server in the background with a single command.
*   **Self-Healing:** If you restart the device, simply run the command again to restart the server instantly (cached binaries are reused).

## 🛠 Installation

### Prerequisites
*   Python 3.10+
*   `adb` (Android Debug Bridge) installed and in your PATH.
*   **`frida-tools`** (Frida Client) installed on your computer.
    *   *Why?* The tool detects your local `frida-client` version to ensure it installs the exactly matching `frida-server` on the device.
    *   To install: `pip install frida-tools`

### Install from Source

```bash
git clone https://github.com/yourusername/frida-orchestrator.git
cd frida-orchestrator
pip install -e .
```

## 📖 Usage

### 1. Scan for Devices
List all connected Android devices with their model names.

```bash
frida-orch scan
```

**Output:**
```text
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃      ID       ┃ Model                       ┃ Platform ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ emulator-5554 │ Android SDK built for arm64 │  Android │
└───────────────┴─────────────────────────────┴──────────┘
```

### 2. Profile a Device
Get detailed information about the device's OS and architecture.

```bash
frida-orch profile <device_id>
```

### 3. Prepare Environment (The Magic Command)
This command handles everything: fetching the binary, installation, and execution.

```bash
frida-orch prepare <device_id>
```

**Output:**
```text
Preparing Frida for device emulator-5554...
Detected: Android 9 (arm64-v8a)
Detected local Frida client: v16.1.4. Installing matching server.
Downloading...
Installing Frida Server...
Frida Server started!
```

## 📚 Documentation
- [Frida Cheat Sheet](docs/frida_cheatsheet.md): A comprehensive guide to Frida CLI, JavaScript API, and useful snippets.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT License
