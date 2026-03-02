# macOS Module: Dependencies

This document covers macOS-specific dependencies for the module. This is Part 1 of the macOS Platform Module documentation.

**Prerequisites**: Read [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) first.

---

## Module Identification (macOS)

```yaml
module:
  name: "{{MODULE_NAME}}"
  version: "{{MODULE_VERSION}}"
  platform: "macos"
  architecture: "universal"        # Supports both x64 and arm64
  deployment_target: "{{MIN_MACOS_VERSION}}"  # Minimum macOS version
  type: "{{MODULE_TYPE}}"          # dylib, staticlib, bin

macos_specific:
  bundle_identifier: "{{BUNDLE_ID}}"  # e.g., "com.example.module"
  code_signing: {{REQUIRES_SIGNING}}   # true if requires code signature
  notarization: {{REQUIRES_NOTARIZE}}  # true if requires Apple notarization
  sandbox: {{REQUIRES_SANDBOX}}        # true if runs in App Sandbox
```

**Variables**:
- `{{MIN_MACOS_VERSION}}`: Minimum macOS version (e.g., "10.15" for Catalina, "11.0" for Big Sur)
- `{{BUNDLE_ID}}`: Reverse-DNS bundle identifier for code signing
- `{{REQUIRES_SIGNING}}`: Whether module requires code signature (true for distribution)
- `{{REQUIRES_NOTARIZE}}`: Whether module requires notarization by Apple (true for distribution outside App Store)
- `{{REQUIRES_SANDBOX}}`: Whether module runs in App Sandbox environment

---

## macOS-Specific Dependencies

### Apple Frameworks

Native macOS frameworks required by this module:

```yaml
dependencies:
  frameworks:
    - name: "{{FRAMEWORK_NAME}}"
      type: "system"                # system or local
      weak: {{WEAK_LINK}}           # true for optional frameworks
      required_version: "{{MIN_VERSION}}"
```

**Common Frameworks**:
```yaml
dependencies:
  frameworks:
    # Core System Frameworks
    - name: "Foundation"
      type: "system"
      weak: false
      required_version: "10.15"

    - name: "AppKit"
      type: "system"
      weak: false
      required_version: "10.15"

    - name: "CoreFoundation"
      type: "system"
      weak: false
      required_version: "10.15"

    # File System
    - name: "CoreServices"
      type: "system"
      weak: false
      required_version: "10.15"
      notes: "Required for FSEvents file system monitoring"

    # Metal GPU Acceleration (Optional)
    - name: "Metal"
      type: "system"
      weak: true
      required_version: "10.15"
      notes: "Optional GPU acceleration support"

    - name: "MetalKit"
      type: "system"
      weak: true
      required_version: "10.15"

    # Security & Keychain
    - name: "Security"
      type: "system"
      weak: false
      required_version: "10.15"
      notes: "Required for Keychain access"
```

### Rust Crates for macOS

```yaml
dependencies:
  crates:
    # Objective-C/Swift Interop
    - name: "objc"
      version: "0.2"
      features: []
      notes: "Objective-C runtime bindings"

    - name: "cocoa"
      version: "0.25"
      features: []
      notes: "AppKit and Foundation bindings"

    - name: "core-foundation"
      version: "0.9"
      features: []
      notes: "Core Foundation bindings"

    - name: "core-graphics"
      version: "0.23"
      features: []
      notes: "Core Graphics bindings"

    # File System Events
    - name: "fsevent-sys"
      version: "4.1"
      features: []
      notes: "Low-level FSEvents bindings"

    # System APIs
    - name: "mach2"
      version: "0.4"
      features: []
      notes: "Mach kernel interface"

    - name: "libc"
      version: "0.2"
      features: []
      notes: "POSIX C bindings"
```

### Homebrew Dependencies (Optional)

If module requires Homebrew packages:

```yaml
dependencies:
  homebrew:
    - formula: "{{FORMULA_NAME}}"
      version: "{{VERSION}}"
      required: {{REQUIRED}}
```

**Example**:
```yaml
dependencies:
  homebrew:
    - formula: "cmake"
      version: "3.28"
      required: true
      notes: "Required for building native extensions"

    - formula: "pkg-config"
      version: "0.29"
      required: true
      notes: "Required for finding system libraries"
```

---

## Next Parts

- [Part 2: Build Configuration](./MACOS_MODULE-part2-build.md)
- [Part 3: Code Signing & Notarization](./MACOS_MODULE-part3-signing.md)
- [Part 4: Testing & Platform APIs](./MACOS_MODULE-part4-testing-apis.md)
- [Part 5: CI/CD & Troubleshooting](./MACOS_MODULE-part5-cicd-troubleshooting.md)
