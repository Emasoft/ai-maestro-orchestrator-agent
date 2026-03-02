# Windows Module Part 3: Platform APIs, Testing, and CI/CD

This document covers Windows-specific APIs, testing configuration, cross-compilation, and CI/CD.

**Parent document**: [WINDOWS_MODULE.md](./WINDOWS_MODULE.md)
**Previous**: [WINDOWS_MODULE-part2-build.md](./WINDOWS_MODULE-part2-build.md)

---

## Platform-Specific APIs

### File System Monitoring (ReadDirectoryChangesW)

Monitor file system changes using Windows API:

```rust
use windows::Win32::Storage::FileSystem::{
    ReadDirectoryChangesW, FILE_NOTIFY_INFORMATION,
    FILE_NOTIFY_CHANGE_FILE_NAME, FILE_NOTIFY_CHANGE_DIR_NAME,
    FILE_NOTIFY_CHANGE_ATTRIBUTES, FILE_NOTIFY_CHANGE_SIZE,
    FILE_NOTIFY_CHANGE_LAST_WRITE,
};
use windows::Win32::Foundation::{HANDLE, CloseHandle};

pub struct FileWatcher {
    directory_handle: HANDLE,
}

impl FileWatcher {
    pub fn new(path: &Path) -> Result<Self, Error> {
        // ReadDirectoryChangesW implementation
        {{FILE_WATCHER_IMPL}}
    }
}
```

**Reference**: See `references/windows/file_monitoring.md` for complete file monitoring guide.

### Registry Access

Read/write Windows Registry:

```rust
use winreg::RegKey;
use winreg::enums::*;

pub fn read_registry_value(key_path: &str, value_name: &str) -> Result<String, Error> {
    let hklm = RegKey::predef(HKEY_LOCAL_MACHINE);
    let key = hklm.open_subkey(key_path)?;
    let value: String = key.get_value(value_name)?;
    Ok(value)
}

pub fn write_registry_value(key_path: &str, value_name: &str, value: &str) -> Result<(), Error> {
    let hklm = RegKey::predef(HKEY_LOCAL_MACHINE);
    let key = hklm.create_subkey(key_path)?;
    key.set_value(value_name, &value)?;
    Ok(())
}
```

**Reference**: See `references/windows/registry_access.md` for complete registry guide.

### COM Interop

Interact with COM objects:

```rust
use windows::{
    core::*,
    Win32::System::Com::*,
};

pub struct ComObject {
    ptr: IUnknown,
}

impl ComObject {
    pub fn new() -> Result<Self, Error> {
        unsafe {
            CoInitializeEx(None, COINIT_APARTMENTTHREADED)?;
            // COM implementation
            {{COM_IMPL}}
        }
    }
}

impl Drop for ComObject {
    fn drop(&mut self) {
        unsafe {
            CoUninitialize();
        }
    }
}
```

**Reference**: See `references/windows/com_interop.md` for complete COM integration guide.

### Windows Service

Create a Windows Service:

```rust
use windows_service::{
    define_windows_service,
    service::{
        ServiceControl, ServiceControlAccept, ServiceExitCode,
        ServiceState, ServiceStatus, ServiceType,
    },
    service_control_handler::{self, ServiceControlHandlerResult},
    service_dispatcher,
};

define_windows_service!(ffi_service_main, service_main);

fn service_main(arguments: Vec<OsString>) {
    // Service implementation
    {{SERVICE_IMPL}}
}
```

**Reference**: See `references/windows/windows_service.md` for complete service creation guide.

---

## Testing Configuration (Windows)

### Unit Tests

```yaml
testing:
  unit:
    command: "cargo test"
    args:
      - "--release"
      - "--target=x86_64-pc-windows-msvc"
    environment:
      RUST_BACKTRACE: "1"
      RUST_LOG: "{{LOG_LEVEL}}"
    timeout: {{TIMEOUT_SECONDS}}
```

### Integration Tests

```yaml
testing:
  integration:
    command: "cargo test --test {{TEST_NAME}}"
    setup:
      - "mkdir {{TEST_TEMP_DIR}}"
      - "reg import {{TEST_REGISTRY_FILE}}"
    teardown:
      - "rmdir /s /q {{TEST_TEMP_DIR}}"
      - "reg delete {{TEST_REGISTRY_KEY}} /f"
    environment:
      TEST_FIXTURES_DIR: "{{FIXTURES_PATH}}"
    timeout: {{TIMEOUT_SECONDS}}
```

### Windows-Specific Tests

```yaml
testing:
  platform_specific:
    # File System Monitoring
    - name: "file-monitoring-windows"
      command: "cargo test --test file_monitoring_tests"
      required: true
      notes: "Tests ReadDirectoryChangesW file monitoring"

    # Registry Access
    - name: "registry-access"
      command: "cargo test --test registry_tests"
      required: true
      notes: "Tests Windows Registry read/write"

    # COM Interop
    - name: "com-integration"
      command: "cargo test --test com_tests"
      required: false
      notes: "Tests COM object interaction"

    # Windows Service
    - name: "service-integration"
      command: "cargo test --test service_tests"
      required: false
      notes: "Tests Windows Service functionality"

    # UAC Elevation
    - name: "uac-elevation"
      command: "cargo test --test uac_tests"
      required: false
      notes: "Tests UAC elevation behavior"
```

---

## Cross-Compilation from Other Platforms

### From Linux (using mingw-w64)

```yaml
cross_compile:
  from: "linux"
  toolchain: "mingw-w64"

  setup:
    - "sudo apt-get update"
    - "sudo apt-get install -y mingw-w64"
    - "rustup target add x86_64-pc-windows-gnu"

  targets:
    - triple: "x86_64-pc-windows-gnu"
      cc: "x86_64-w64-mingw32-gcc"
      cxx: "x86_64-w64-mingw32-g++"
      ar: "x86_64-w64-mingw32-ar"

  build_command: |
    cargo build --release --target x86_64-pc-windows-gnu
```

### From macOS (using mingw-w64 via Homebrew)

```yaml
cross_compile:
  from: "macos"
  toolchain: "mingw-w64"

  setup:
    - "brew install mingw-w64"
    - "rustup target add x86_64-pc-windows-gnu"

  targets:
    - triple: "x86_64-pc-windows-gnu"
      cc: "x86_64-w64-mingw32-gcc"
      cxx: "x86_64-w64-mingw32-g++"

  build_command: |
    cargo build --release --target x86_64-pc-windows-gnu
```

---

## CI/CD Configuration (Windows)

### GitHub Actions Matrix

```yaml
name: Windows Build

on: [push, pull_request]

jobs:
  build-windows:
    strategy:
      matrix:
        os: [windows-2019, windows-2022]
        rust: [stable]
        target:
          - x86_64-pc-windows-msvc
          - i686-pc-windows-msvc
          - aarch64-pc-windows-msvc

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: ${{ matrix.rust }}
          targets: ${{ matrix.target }}

      - name: Build
        run: |
          cargo build --release --target ${{ matrix.target }}

      - name: Test
        if: matrix.target != 'aarch64-pc-windows-msvc'  # Can't test ARM64 on x64
        run: |
          cargo test --release --target ${{ matrix.target }}

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: {{MODULE_NAME}}-windows-${{ matrix.target }}
          path: target/${{ matrix.target }}/release/{{OUTPUT_NAME}}
```

---

## Troubleshooting

### Build Issues

**Problem**: `error: linker 'link.exe' not found`
**Solution**: Install Visual Studio Build Tools or Visual Studio with C++ workload

**Problem**: `LNK1181: cannot open input file 'msvcrt.lib'`
**Solution**: Ensure Windows SDK is installed. Run `rustup toolchain list` to verify MSVC toolchain

**Problem**: `error: failed to run custom build command for 'windows-sys'`
**Solution**: Update `windows` crate to latest version: `cargo update -p windows`

### Linking Issues

**Problem**: `unresolved external symbol __imp_LoadLibraryA`
**Solution**: Link kernel32: `println!("cargo:rustc-link-lib=kernel32");` in build.rs

**Problem**: `LNK2019: unresolved external symbol` for C++ functions
**Solution**: Use `extern "C"` in C++ code or link the C++ standard library

### Runtime Issues

**Problem**: `The code execution cannot proceed because VCRUNTIME140.dll was not found`
**Solution**: Either install Visual C++ Redistributable on target system, or build with static CRT: `-C target-feature=+crt-static`

**Problem**: `Application requires administrator privileges`
**Solution**: Update manifest with `<requestedExecutionLevel level="asInvoker">`

**Problem**: `Access denied` when accessing files/registry
**Solution**: Check UAC elevation level in manifest and file/registry permissions

---

## Related Documentation

- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base template (read first)
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules
- `references/windows/file_monitoring.md` - File system monitoring
- `references/windows/registry_access.md` - Registry operations
- `references/windows/com_interop.md` - COM integration
- `references/windows/windows_service.md` - Service creation
- `references/windows/manifest_guide.md` - Application manifest details
