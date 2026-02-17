# Frida Cheat Sheet

A comprehensive guide to Frida's CLI tools, JavaScript API, and common snippets for mobile application security testing.

## 🚀 Installation & Setup

```bash
# Install Frida tools via pip
pip install frida-tools

# Install specific version
pip install frida-tools==12.0.0

# Install Frida server on Android device (requires root)
# 1. Download frida-server from GitHub releases (match your architecture)
# 2. Push to device
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

---

## 🛠 CLI Tools

### frida-ps (Process List)
```bash
# List local processes
frida-ps

# List processes on USB device
frida-ps -U

# List applications (with icons/names) on USB device
frida-ps -U -a

# List installed applications
frida-ps -U -ai
```

### frida-trace (Auto-tracing)
```bash
# Trace all functions matching "open" in "com.example.app"
frida-trace -U -f com.example.app -i "open*"

# Trace specific Objective-C method on iOS
frida-trace -U -f com.example.app -m "-[NSURLRequest initWithURL:]"

# Trace Java method on Android
frida-trace -U -f com.example.app -j "*!*certificate*"
```

### frida (REPL)
```bash
# Attach to running process
frida -U com.example.app

# Spawn process with script
frida -U -f com.example.app -l script.js --no-pause
```

---

## 📜 JavaScript API

### General
```javascript
console.log("Message");
console.error("Error");

// Send data to python script
send({ type: "data", payload: "value" });

// Receive data from python script
recv("poke", function onMessage(message) { ... }).wait();
```

### 🤖 Android (Java)

**Basics**
```javascript
Java.perform(function() {
    // Code that uses Java API must be inside here
});
```

**Hooking a Method**

**Java Code (Target):**
```java
package com.example.app;

public class MainActivity {
    // Basic boolean method
    public boolean isPremium() {
        return false;
    }

    // Method with arguments (Overloads) 
    public void login(String username, String password) {
        if (checkCreds(username, password)) {
            // success
        }
    }
}
```

**Frida Script:**
```javascript
Java.perform(function() {
    var MainActivity = Java.use("com.example.app.MainActivity");
    
    // Hook 'isPremium' method
    MainActivity.isPremium.implementation = function() {
        console.log("isPremium called! Returning true.");
        return true;
    };
    
    // Hook method with arguments (Overloads)
    MainActivity.login.overload('java.lang.String', 'java.lang.String').implementation = function(user, pass) {
        console.log("Login captured: " + user + " / " + pass);
        return this.login(user, pass); // Call original
    };
});
```

**Finding Instances (Java.choose)**

**Java Code (Target):**
```java
// User object instance exists in heap
// package com.example.app;
public class UserManager {
    public void setAdmin(boolean value) {
        this.isAdmin = value;
    }
}
```

**Frida Script:**
```javascript
Java.choose("com.example.app.UserManager", {
    onMatch: function(instance) {
        console.log("Found instance: " + instance);
        // Call method on live instance
        instance.setAdmin(true); 
    },
    onComplete: function() {
        console.log("Scan complete");
    }
});
```

**Creating Objects / Casting**
```javascript
var String = Java.use("java.lang.String");
var str = String.$new("Hello World");
var CastedObj = Java.cast(somePtr, Java.use("com.example.Class"));
```

### 🍎 iOS (Objective-C)

**Hooking a Method**

**Objective-C Code (Target):**
```objective-c
@interface UserContext : NSObject
- (BOOL)isLoggedIn; 
@end

@implementation UserContext
- (BOOL)isLoggedIn { return NO; }
@end
```

**Frida Script:**
```javascript
if (ObjC.available) {
    // -[ClassName methodName:arg1]
    var className = "UserContext";
    var methodName = "-[UserContext isLoggedIn]";
    
    var hook = eval('ObjC.classes.' + className + '["' + methodName + '"]');
    
    Interceptor.attach(hook.implementation, {
        onEnter: function(args) {
            // args[0] = self, args[1] = selector, args[2+] = arguments
            console.log("isLoggedIn called");
        },
        onLeave: function(retval) {
            console.log("Original ret: " + retval);
            retval.replace(1); // Return true (1)
        }
    });
}
```

**Reading Arguments (ObjC)**

**Objective-C Code (Target):**
```objective-c
// Example Logger Class
- (void)logMessage:(NSString *)msg {
    NSLog(@"%@", msg);
}
```

**Frida Script:**
```javascript
// method: - (void)logMessage:(NSString *)msg;
onEnter: function(args) {
    // Read NSString*
    var msg = new ObjC.Object(args[2]); 
    console.log("Message: " + msg.toString());
}
```

### 💾 Native / Memory

#### 🧠 Native Hooking Explained
Unlike Java, Native code (C/C++) runs directly on the CPU. We don't have "Classes" to hook easily; we hook **Memory Addresses**.

- **Exports:** Public functions (e.g. `open`, `malloc`) in system libraries (`libc.so`). Easy to hook by name.
- **Stripped / Private Functions:** Internal game/app logic. No names, only addresses. You must find the **Offset** using tools like Ghidra/IDA.
- **Pointers (`NativePointer`):** `args[0]` is just a number (address). You must tell Frida how to read it:
    - `args[0].readUtf8String()` -> Read as text (char*)
    - `args[0].readInt()` -> Read as integer
    - `args[0].readByteArray(16)` -> Read raw bytes (structs/buffers)

**Base Address & modules**
```javascript
var baseAddr = Module.findBaseAddress("libnative-lib.so");
console.log("Base Address: " + baseAddr);

var exportAddr = Module.findExportByName("libc.so", "open");
```

**Interceptor (Native Hooks)**

**C Code (Target):**
```c
// extern "C" int open(const char *path, int oflag, ...);
int fd = open("/etc/hosts", O_RDONLY);
```

**Frida Script:**
```javascript
Interceptor.attach(exportAddr, {
    // onEnter: Called BEFORE the native function executes
    onEnter: function(args) {
        // args[0] = 1st argument (const char *path) - Address of the string
        // args[1] = 2nd argument (int oflag) - Integer flags
        
        // We must READ the memory at the address args[0] to get the string
        try {
            var path = args[0].readUtf8String();
            console.log("open() called for file: " + path);
        } catch (e) {
            console.log("Could not read string arg");
        }
        
        // You can Modify arguments logic here if needed
        // args[1] = ptr(0); // Force O_RDONLY
    },
    
    // onLeave: Called AFTER original function finishes
    onLeave: function(retval) {
        // retval = Return Value (File Descriptor - int)
        console.log("open() returned FD: " + retval.toInt32());
        
        // You can Modify return value here
        // retval.replace(-1); // Return -1 (Error) to the app
    }
});
```

**Memory operations**
```javascript
// Scan memory for pattern
Memory.scan(baseAddr, size, "DE AD BE EF", {
    onMatch: function(address, size) { ... },
    onComplete: function() { ... }
});

// Write to memory
ptr(0x12345678).writeInt(1337);
ptr(0x12345678).writeByteArray([0x90, 0x90, 0x90]); // NOP
```

---

## 🧪 Common Snippets

### SSL Pinning Bypass (Generic Java)

**Java Code (Target):**
```java
// TrustManagerImpl.java (Android Framework)
public List<X509Certificate> checkTrustedRecursive(X509Certificate[] certs, String str, String str2, boolean bool) {
    // Verify certificate chain...
    throw new CertificateException("Not trusted");
}
```

**Frida Script:**
```javascript
Java.perform(function() {
    var array_list = Java.use("java.util.ArrayList");
    var ApiClient = Java.use('com.android.org.conscrypt.TrustManagerImpl');
    
    ApiClient.checkTrustedRecursive.implementation = function(a1, a2, a3, a4, a5, a6) {
        console.log('Bypassing SSL Pinning');
        return array_list.$new();
    }
});
```

### Root Detection Bypass (File Check)

**C Code (Target):**
```c
// Checks if 'su' binary exists
FILE *f = fopen("/system/bin/su", "r");
if (f != NULL) {
    // Root detected!
    fclose(f);
}
```

**Frida Script:**
```javascript
var openPtr = Module.findExportByName(null, "open");
var suPaths = ["/system/bin/su", "/system/xbin/su"];

Interceptor.attach(openPtr, {
    onEnter: function(args) {
        var path = args[0].readUtf8String();
        if (suPaths.indexOf(path) !== -1) {
            console.log("Root detection blocked: " + path);
            this.fake = true;
            args[0].writeUtf8String("/system/bin/fakesu"); // Redirect
        }
    }
});
```

### String Decrypt / Logger

**Java Code (Target):**
```java
package com.example;
public class Encryption {
    public byte[] encrypt(byte[] data) {
         // AES/RSA encryption...
        return encryptedData;
    }
}
```

**Frida Script:**
```javascript
// Useful for hooking encryption functions
// void encrypt(byte[] data)
var EncClass = Java.use("com.example.Encryption");
EncClass.encrypt.implementation = function(data) {
    // print input byte array as string
    var str = Java.use("java.lang.String").$new(data);
    console.log("Encrypting: " + str);
    return this.encrypt(data);
};
```

### Stack Trace (Java)
```javascript
function printStack() {
    var Exception = Java.use("java.lang.Exception");
    var ins = Exception.$new("Exception");
    var strace = ins.getStackTrace();
    if (strace != undefined && strace != null) {
        for (var i = 0; i < strace.length; i++) {
            var str = "   " + strace[i].toString();
            console.log(str);
        }
    }
}
```

### Dump Classes
```javascript
Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.includes("com.example")) {
                console.log(className);
            }
        },
        onComplete: function() {}
    });
});
```

### 🏗 Constructor Hooking (Real World: License Bypass)
**Scenario:** An app checks license status immediately upon object creation.

**Java Code (Target):**
```java
// package com.premium.app;
public class LicenseManager {
    private String key;
    private int type; // 0=Free, 1=Pro

    public LicenseManager(String licenseKey, int type) {
        this.key = licenseKey;
        this.type = type;
        if (type == 0) {
            checkOnlineValidation(licenseKey); 
        }
    }
}
```

**Frida Script:**
```javascript
Java.perform(function() {
    // Target class: com.premium.app.LicenseManager
    var LicenseManager = Java.use("com.premium.app.LicenseManager");
    
    // Hook the constructor ($init)
    LicenseManager.$init.overload("java.lang.String", "int").implementation = function(licenseKey, type) {
        console.log("[*] LicenseManager initialized with Key: " + licenseKey);
        
        // Force the app to think a valid "Pro" license (type 1) is used, regardless of input
        // Original call: new LicenseManager("invalid_key", 0);
        // Modified call: new LicenseManager("invalid_key", 1);
        this.$init(licenseKey, 1); 
        console.log("[+] Modified to PRO license type!");
    };
});
```

### ⏱ Timing / Anti-Debug Bypass
**Scenario:** App crashes if a function takes too long (detecting debugging/hooking latency).

**C Code (Target):**
```c
// libsecurity.so
void check_debugger_timing() {
    long start = get_time();
    complex_calculation(); // Should take 1ms
    long end = get_time();
    if ((end - start) > 10) { 
        exit(0); // Debugger detected!
    }
}
```

**Frida Script:**
```javascript
var startTime = 0;
// Hypothetical anti-debug function
var antiDebugPtr = Module.findExportByName("libsecurity.so", "check_debugger_timing");

if (antiDebugPtr) {
    Interceptor.attach(antiDebugPtr, {
        onEnter: function(args) {
            startTime = new Date().getTime();
        },
        onLeave: function(retval) {
            var endTime = new Date().getTime();
            var duration = endTime - startTime;
            console.log("Execution time: " + duration + "ms");
            
            // If the app checks for > 10ms to detect hooks, we can spoof the return value 
            // or replace the function entirely (see Native Replacement) to always succeed.
        }
    }); 
}
```

### 🎨 Manipulating UI Thread (Real World: Update Text)

**Scenario:** Change a "LOCKED" status text to "UNLOCKED" on the screen.

**Critical Concept:**
Android crashes if you touch UI elements (TextViews, Buttons) from a background thread (where Frida hooks run by default). You MUST wrap your code in `Java.scheduleOnMainThread(...)`.

**Java Code (Target):**
```java
// MainActivity.java
public class MainActivity extends Activity {
    TextView statusText; // ID: R.id.status_label
    
    void updateStatus(boolean premium) {
        if (premium) statusText.setText("UNLOCKED");
        else statusText.setText("LOCKED");
    }
}
```

**Frida Script 1: Show Toast (Simple)**
```javascript
Java.perform(function() {
    // Runnable that executes on the UI thread
    Java.scheduleOnMainThread(function() {
        var Toast = Java.use("android.widget.Toast");
        var verify = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
        Toast.makeText(verify, "Hacked by Frida! 🔓", 1).show();
    });
});
```

**Frida Script 2: Modify Existing TextView (Advanced)**
```javascript
Java.perform(function() {
    // 1. Find the Activity instance currently running
    Java.choose("com.example.app.MainActivity", {
        onMatch: function(instance) {
            console.log("[*] Found MainActivity instance");
            
            // 2. Schedule UI update on Main Thread
            Java.scheduleOnMainThread(function() {
                // 3. Find the TextView by ID (need to reverse R.id.status_label or use getIdentifier)
                // Let's assume we know the ID integer or look it up by name:
                var resId = instance.getResources().getIdentifier("status_label", "id", "com.example.app");
                var tv = instance.findViewById(resId);
                
                if (tv != null) {
                    // Check logic
                    var TextView = Java.use("android.widget.TextView");
                    // Cast generic View to TextView
                    var tvCast = Java.cast(tv, TextView);
                    
                    console.log("[*] Old Text: " + tvCast.getText());
                    tvCast.setText("UNLOCKED (Hacked) 🔓");
                    tvCast.setTextColor(0xFF00FF00); // Green
                } else {
                    console.log("[-] TextView not found!");
                }
            });
        },
        onComplete: function() {}
    });
});
```

### 🔧 Native Hooking (Game/Unity)

**Hook via Offset (Unity/Il2cpp Game)**
**Scenario:** Hooking `get_Gold()` method in a Unity game (libil2cpp.so).

**C++ Code (Target):**
```cpp
// Decompiled via Ghidra/IDA
class Player {
    int gold;
public:
    int get_Gold() { return this->gold; } // Offset: 0x123456
};
```

**Frida Script:**
```javascript
var il2cpp = Module.findBaseAddress("libil2cpp.so");
if (il2cpp) {
    // 0x123456 is the offset of get_Gold()
    var getGoldPtr = il2cpp.add(0x123456);
    
    Interceptor.attach(getGoldPtr, {
        onEnter: function(args) {
            // args[0] is 'this' pointer in C++
        },
        onLeave: function(retval) {
            console.log("Original Gold: " + retval.toInt32());
            // Spoof Gold to 999999
            retval.replace(999999);
        }
    });
}
```

**Native Function Replacement (Root Bypass)**
**Scenario:** App uses `fopen` to check for existence of `/system/bin/su`.
```javascript
var openPtr = Module.findExportByName("libc.so", "fopen");
// 1. Prepare the original function so we can call it later if needed
// Define signature: ReturnType, [ArgTypes...] -> 'pointer', ['pointer', 'pointer']
var open = new NativeFunction(openPtr, 'pointer', ['pointer', 'pointer']);

// 2. Replace the function with our own NativeCallback
Interceptor.replace(openPtr, new NativeCallback(function(pathPtr, modePtr) {
    var path = pathPtr.readUtf8String();
    
    // Check if app is trying to open 'su'
    if (path.indexOf("/system/bin/su") >= 0) {
        console.log("[!] Blocked Root Check: " + path);
        // Return NULL (0) to simulate "File not found"
        return ptr(0);
    }
    
    // 3. For all other files, call the ORIGINAL open function
    return open(pathPtr, modePtr);
}, 'pointer', ['pointer', 'pointer'])); // Must match original signature
```

### 🔌 Frida Gadget (Non-Rooted)
**Scenario:** Injecting Frida into an APK without root (e.g. using `objection patchapk`).
1. **Patch APK:** Embed `libfrida-gadget.so` into the APK.
2. **Install & Run on any device.**
3. **Connect:**
```bash
# Verify connection (Gadget usually listens on USB when repackaged properly)
frida-ps -U | grep "Gadget"

# Connect
frida -U Gadget -l my_script.js
```


