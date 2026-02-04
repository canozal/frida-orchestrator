# MVP Feature Roadmap

## Phase 1: Foundation (CLI Only)
- [ ] **Scaffolding:** Set up project structure, logging, and error handling.
- [ ] **Android Support (Core):**
    - Implement `DeviceManager` for `adb`.
    - Implement `DeviceProfiler` for ABI and OS version detection.
    - Implement simple Root detection (su binary presence).
- [ ] **IO Layer:**
    - Basic CLI to list devices.
    - JSON output for profiling.

## Phase 2: Frida Automation (Android)
- [ ] **GitHub Integration:**
    - Script to fetch latest Frida release assets list.
    - Local caching mechanism for downloaded `.xz` files.
- [ ] **Installer Logic:**
    - Push `frida-server` to `/data/local/tmp/`.
    - Permission fix (`chmod`).
    - Execution logic (background process).
    - Status check (verify process is running).

## Phase 3: iOS Support (Basic)
- [ ] **Device Discovery:** Integrate `idevice_id`.
- [ ] **Profiling:** Integrate `ideviceinfo` parsing.
- [ ] **Installation:**
    - *MVP Limitation:* Support only "SSH-enabled" Jailbroken devices (using `ssh` just like ADB).
    - *Constraint:* Installing debs automatically via `ideviceinstaller` is brittle; stick to SSH/SCP for MVP binary placement.

## Phase 4: Initial GUI (Optional Wrapper)
- [ ] Simple window showing a list widget of devices.
- [ ] "Connect" button.
- [ ] Log viewing pane.

---

# Future Extensions

1.  **Gadget Injection Patcher:**
    - Automate `apktool` -> insert gadget `.so` -> repack -> sign.
    - *Status:* Out of scope for MVP, implies "modification" which requires ethical guardrails.
2.  **Network Transport:**
    - Support remote adb connect (TCP/IP).
3.  **Frida Client Setup:**
    - Automatically create a Python virtual environment for the user on their host machine and `pip install frida-tools==<version>` to match the device server.
4.  **Certificate Pinning helper:**
    - Push Burp/Proxy CA certs to the system store (Magisk module automation).
