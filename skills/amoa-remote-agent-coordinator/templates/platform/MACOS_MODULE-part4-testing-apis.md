# macOS Module: Testing & Platform APIs

This document covers macOS-specific testing configuration and platform APIs. This is Part 4 of the macOS Platform Module documentation.

**Prerequisites**: Read [Part 3: Code Signing & Notarization](./MACOS_MODULE-part3-signing.md) first.

---

## Testing Configuration (macOS)

### Unit Tests

```yaml
testing:
  unit:
    command: "cargo test"
    args:
      - "--release"
      - "--target={{HOST_TRIPLE}}"
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
      # Grant necessary permissions for testing
      - "tccutil reset SystemPolicyAllFiles"
      - "mkdir -p {{TEST_TEMP_DIR}}"
    teardown:
      - "rm -rf {{TEST_TEMP_DIR}}"
    environment:
      TEST_FIXTURES_DIR: "{{FIXTURES_PATH}}"
    timeout: {{TIMEOUT_SECONDS}}
```

### macOS-Specific Tests

```yaml
testing:
  platform_specific:
    # FSEvents File Watching
    - name: "fsevent-monitoring"
      command: "cargo test --test fsevent_tests"
      required: true
      notes: "Tests FSEvents file system monitoring"

    # AppKit Integration
    - name: "appkit-integration"
      command: "cargo test --test appkit_tests"
      required: false
      notes: "Tests AppKit framework integration"

    # Metal GPU Tests
    - name: "metal-acceleration"
      command: "cargo test --test metal_tests"
      required: false
      condition: "has_metal_gpu"
      notes: "Tests Metal GPU acceleration (requires Metal-capable GPU)"

    # Keychain Access
    - name: "keychain-integration"
      command: "cargo test --test keychain_tests"
      required: true
      notes: "Tests Keychain access APIs"

    # Code Signing Verification
    - name: "code-signature-validation"
      command: "cargo test --test codesign_tests"
      required: true
      notes: "Validates code signature after build"
```

### Performance Benchmarks

```yaml
testing:
  benchmarks:
    command: "cargo bench"
    output_dir: "target/criterion"
    baseline: "{{BASELINE_NAME}}"
```

---

## Platform-Specific APIs

### File System Events (FSEvents)

Monitor file system changes using FSEvents:

```rust
use fsevent_sys as fsevent;
use std::path::Path;

pub struct FileWatcher {
    stream: fsevent::FSEventStreamRef,
}

impl FileWatcher {
    pub fn new(path: &Path) -> Result<Self, Error> {
        // FSEvents implementation
        {{FSEVENT_IMPL}}
    }
}
```

**Reference**: See `references/macos/fsevent_api.md` for complete FSEvents integration guide.

### AppKit Integration

Access macOS UI frameworks:

```rust
use cocoa::appkit::{NSApplication, NSWindow};
use cocoa::base::{id, nil};

pub fn create_window() -> id {
    unsafe {
        // AppKit implementation
        {{APPKIT_IMPL}}
    }
}
```

**Reference**: See `references/macos/appkit_integration.md` for complete AppKit usage guide.

### Keychain Access

Store/retrieve credentials from macOS Keychain:

```rust
use security_framework::keychain::{SecKeychain, KeychainSettings};

pub fn store_credential(service: &str, account: &str, password: &str) -> Result<(), Error> {
    // Keychain implementation
    {{KEYCHAIN_IMPL}}
}
```

**Reference**: See `references/macos/keychain_api.md` for complete Keychain integration guide.

### Metal GPU Acceleration

Use Metal for GPU-accelerated operations:

```rust
use metal::{Device, Library, CommandQueue};

pub struct MetalAccelerator {
    device: Device,
    queue: CommandQueue,
}

impl MetalAccelerator {
    pub fn new() -> Result<Self, Error> {
        // Metal implementation
        {{METAL_IMPL}}
    }
}
```

**Reference**: See `references/macos/metal_acceleration.md` for complete Metal usage guide.

---

## Next Part

- [Part 5: CI/CD & Troubleshooting](./MACOS_MODULE-part5-cicd-troubleshooting.md)
