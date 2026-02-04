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
```javascript
// method: - (void)logMessage:(NSString *)msg;
onEnter: function(args) {
    // Read NSString*
    var msg = new ObjC.Object(args[2]); 
    console.log("Message: " + msg.toString());
}
```

### 💾 Native / Memory

**Base Address & modules**
```javascript
var baseAddr = Module.findBaseAddress("libnative-lib.so");
console.log("Base Address: " + baseAddr);

var exportAddr = Module.findExportByName("libc.so", "open");
```

**Interceptor (Native Hooks)**
```javascript
Interceptor.attach(exportAddr, {
    onEnter: function(args) {
        // args are NativePointer
        // Use readUtf8String, readInt, etc.
        console.log("open() file: " + args[0].readUtf8String());
    },
    onLeave: function(retval) {
        console.log("open FD: " + retval);
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
