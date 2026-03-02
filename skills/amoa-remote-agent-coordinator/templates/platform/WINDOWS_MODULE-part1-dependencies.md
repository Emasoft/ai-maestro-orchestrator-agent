# Windows Module Part 1: Identification and Dependencies

This document covers Windows-specific module identification and dependency configuration.

**Parent document**: [WINDOWS_MODULE.md](./WINDOWS_MODULE.md)
**Read first**: [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md)

---

## Module Identification (Windows)

```yaml
module:
  name: "{{MODULE_NAME}}"
  version: "{{MODULE_VERSION}}"
  platform: "windows"
  architecture: "{{ARCH}}"          # x64, x86, arm64
  min_windows_version: "{{MIN_WIN_VERSION}}"  # e.g., "10.0.19041" (Windows 10 2004)
  type: "{{MODULE_TYPE}}"           # dll, lib, exe

windows_specific:
  subsystem: "{{SUBSYSTEM}}"        # console, windows, native
  manifest_file: "{{MANIFEST_PATH}}"
  resource_file: "{{RC_FILE_PATH}}"
  requires_visual_cpp_redist: {{REQUIRES_VCREDIST}}
  requires_dotnet: {{REQUIRES_DOTNET}}
```

**Variables**:
- `{{ARCH}}`: Target architecture (x64 for 64-bit, x86 for 32-bit, arm64 for ARM)
- `{{MIN_WIN_VERSION}}`: Minimum Windows version (build number format)
- `{{SUBSYSTEM}}`: Windows subsystem (console for CLI apps, windows for GUI apps)
- `{{MANIFEST_PATH}}`: Path to application manifest (for UAC, DPI awareness, etc.)
- `{{RC_FILE_PATH}}`: Path to resource file (.rc) for version info and icons
- `{{REQUIRES_VCREDIST}}`: Whether Visual C++ Redistributable is required
- `{{REQUIRES_DOTNET}}`: Whether .NET runtime is required

**Windows Version Reference**:
- Windows 10 1809 (October 2018 Update): `10.0.17763`
- Windows 10 1903 (May 2019 Update): `10.0.18362`
- Windows 10 2004 (May 2020 Update): `10.0.19041`
- Windows 10 21H2: `10.0.19044`
- Windows 11 21H2: `10.0.22000`
- Windows 11 22H2: `10.0.22621`
- Windows 11 23H2: `10.0.22631`

---

## Windows-Specific Dependencies

### Windows SDK

```yaml
dependencies:
  windows_sdk:
    version: "{{SDK_VERSION}}"
    components:
      - "{{COMPONENT_1}}"
      - "{{COMPONENT_2}}"
```

**Example**:
```yaml
dependencies:
  windows_sdk:
    version: "10.0.22621.0"  # Windows 11 SDK
    components:
      - "Windows.Win32.Foundation"
      - "Windows.Win32.System.Threading"
      - "Windows.Win32.Storage.FileSystem"
      - "Windows.Win32.UI.WindowsAndMessaging"
```

### Visual C++ Runtime

```yaml
dependencies:
  vcredist:
    version: "{{VC_VERSION}}"  # e.g., "14.38" (VS 2022)
    architecture: "{{ARCH}}"
    link_type: "{{LINK_TYPE}}"  # dynamic, static
```

**Link Types**:
- `dynamic`: Requires Visual C++ Redistributable installed on target system
- `static`: Statically links CRT, no redistributable required (larger binary)

### Rust Crates for Windows

```yaml
dependencies:
  crates:
    # Windows API Bindings
    - name: "windows"
      version: "0.52"
      features:
        - "Win32_Foundation"
        - "Win32_System_Threading"
        - "Win32_Storage_FileSystem"
        - "Win32_UI_WindowsAndMessaging"
      notes: "Official Microsoft Windows API bindings"

    - name: "windows-sys"
      version: "0.52"
      features:
        - "Win32_Foundation"
        - "Win32_System_Threading"
      notes: "Lightweight Windows API bindings (no metadata)"

    # File System Monitoring
    - name: "notify"
      version: "6.1"
      features: ["windows-ffi"]
      notes: "Cross-platform file watching (uses ReadDirectoryChangesW on Windows)"

    # COM Interop
    - name: "windows-implement"
      version: "0.52"
      features: []
      notes: "Required for implementing COM interfaces"

    - name: "windows-interface"
      version: "0.52"
      features: []
      notes: "Required for defining COM interfaces"

    # Registry Access
    - name: "winreg"
      version: "0.52"
      features: []
      notes: "Windows Registry access"

    # Process Management
    - name: "sysinfo"
      version: "0.30"
      features: []
      notes: "Cross-platform system information"

    # Service Integration
    - name: "windows-service"
      version: "0.6"
      features: []
      notes: "Windows Service integration"
```

### System Libraries

```yaml
dependencies:
  system_libs:
    - name: "{{LIB_NAME}}"
      link_type: "{{LINK_TYPE}}"  # static, dynamic
      search_path: "{{SEARCH_PATH}}"
```

**Common System Libraries**:
```yaml
dependencies:
  system_libs:
    - name: "kernel32"
      link_type: "dynamic"
      notes: "Core Windows API"

    - name: "user32"
      link_type: "dynamic"
      notes: "Windows UI API"

    - name: "shell32"
      link_type: "dynamic"
      notes: "Shell functions"

    - name: "ole32"
      link_type: "dynamic"
      notes: "COM libraries"

    - name: "advapi32"
      link_type: "dynamic"
      notes: "Advanced Windows API (registry, security)"
```

---

**Next**: [WINDOWS_MODULE-part2-build.md](./WINDOWS_MODULE-part2-build.md) - Build Configuration
