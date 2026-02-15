# ADB Cheat Sheet

A comprehensive collection of Android Debug Bridge (ADB) commands for mobile security testing, development, and debugging.

## 🚀 Basics & Setup

| Command | Description |
| :--- | :--- |
| `adb devices` | List connected devices |
| `adb devices -l` | List connected devices with details |
| `adb start-server` | Start the ADB server manually |
| `adb kill-server` | Kill the ADB server |
| `adb connect <ip>:<port>` | Connect to a device via WiFi (default port 5555) |
| `adb disconnect` | Disconnect from all TCP/IP devices |
| `adb usb` | Restart ADB in USB mode |
| `adb tcpip 5555` | Restart ADB in TCP/IP mode (port 5555) |

---

## 📱 Device Management

| Command | Description |
| :--- | :--- |
| `adb reboot` | Reboot device |
| `adb reboot recovery` | Reboot mainly into recovery mode |
| `adb reboot bootloader` | Reboot into bootloader/fastboot mode |
| `adb root` | Restart adbd with root permissions |
| `adb unroot` | Restart adbd without root permissions |
| `adb shell` | Open interactive shell |
| `adb shell <command>` | Execute a single shell command |

---

## 📦 App Management

| Command | Description |
| :--- | :--- |
| `adb install <apk>` | Install an APK from computer |
| `adb install -r <apk>` | Reinstall/Update an existing app (keep data) |
| `adb install -g <apk>` | Grant all permissions on install |
| `adb uninstall <package>` | Uninstall an app |
| `adb shell pm list packages` | List all installed packages |
| `adb shell pm list packages -f` | List packages with their associated APK path |
| `adb shell pm list packages -3` | List only 3rd party (installed) packages |
| `adb shell pm path <package>` | Print the path to the APK for a package |
| `adb shell pm clear <package>` | Clear app data and cache |
| `adb shell am force-stop <package>` | Force stop an application |

---

## 📂 File Transfer

| Command | Description |
| :--- | :--- |
| `adb push <local> <remote>` | Copy file/dir from computer to device |
| `adb pull <remote> <local>` | Copy file/dir from device to computer |

**Example:**
```bash
adb push burp.cer /sdcard/Download/
adb pull /data/anr/traces.txt ./
```

---

## 🔍 Logcat (Logging)

| Command | Description |
| :--- | :--- |
| `adb logcat` | View device logs in real-time |
| `adb logcat -d > log.txt` | Dump current logs to a file and exit |
| `adb logcat -c` | Clear the current logs |
| `adb logcat *:E` | Filter logs to show Error level and above |
| `adb logcat <TAG>:V *:S` | Filter by specific tag (Verbose) and silence others |
| `adb logcat --pid=<pid>` | Filter logs for a specific Process ID |

---

## 🛠️ Advanced & Debugging

| Command | Description |
| :--- | :--- |
| `adb shell dumpsys` | Dump all system service info (huge output) |
| `adb shell dumpsys activity` | Dump activity manager state |
| `adb shell dumpsys package <package>` | specialized info about a specific package |
| `adb shell screencap -p /sdcard/s.png` | Take a screenshot |
| `adb shell screenrecord /sdcard/v.mp4` | Record screen video (Ctrl+C to stop) |
| `adb shell input text "<string>"` | Send text input to the device |
| `adb shell input keyevent <keycode>` | Send a key press (e.g., 66 for ENTER, 4 for BACK) |
| `adb shell ip addr` | Show network interfaces and IP addresses |
| `adb shell netstat` | Show network connections |
| `adb shell getprop` | List all system properties |
| `adb shell getprop ro.build.version.release` | Get Android version |

---

## 🔐 Frida Related

| Command | Description |
| :--- | :--- |
| `adb push frida-server /data/local/tmp/` | Push frida-server to device |
| `adb shell chmod 755 /data/local/tmp/frida-server` | Make frida-server executable |
| `adb shell "/data/local/tmp/frida-server &"` | Run frida-server in background |

> [!TIP]
> Use `frida-orchestrator` to automate the Frida server setup!
