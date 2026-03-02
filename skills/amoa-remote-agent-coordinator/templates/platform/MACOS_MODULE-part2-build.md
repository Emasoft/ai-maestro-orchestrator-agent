# macOS Module: Build Configuration

This document covers macOS-specific build configuration. This is Part 2 of the macOS Platform Module documentation.

**Prerequisites**: Read [Part 1: Dependencies](./MACOS_MODULE-part1-dependencies.md) first.

---

## Build Configuration (macOS)

### Compiler and Toolchain

```yaml
build:
  compiler: "clang"                 # macOS uses clang by default
  toolchain: "stable"               # Rust toolchain
  xcode_version: "{{MIN_XCODE}}"    # Minimum Xcode version
  sdk_version: "{{MIN_SDK}}"        # Minimum SDK version

  optimization: "{{OPT_LEVEL}}"     # 0, 1, 2, 3, s, z
  debug_symbols: {{DEBUG}}          # true for development, false for release
  strip: {{STRIP}}                  # true to strip symbols in release
  lto: {{LTO}}                      # true for link-time optimization
```

**Variables**:
- `{{MIN_XCODE}}`: Minimum Xcode version (e.g., "14.0")
- `{{MIN_SDK}}`: Minimum macOS SDK version (e.g., "13.0")
- `{{OPT_LEVEL}}`: Optimization level (2 or 3 for release, 0 for debug)
- `{{DEBUG}}`: Include debug symbols (true for .dSYM generation)
- `{{STRIP}}`: Strip symbols from binary (true for smaller binaries)
- `{{LTO}}`: Enable link-time optimization (true for better performance)

### Target Configuration

```yaml
build:
  targets:
    # Apple Silicon (arm64)
    - name: "{{MODULE_NAME}}-arm64"
      triple: "aarch64-apple-darwin"
      output: "target/aarch64-apple-darwin/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C target-cpu=apple-m1"
        - "-C link-arg=-mmacosx-version-min={{MIN_MACOS_VERSION}}"

    # Intel (x64)
    - name: "{{MODULE_NAME}}-x64"
      triple: "x86_64-apple-darwin"
      output: "target/x86_64-apple-darwin/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C target-cpu=x86-64-v2"
        - "-C link-arg=-mmacosx-version-min={{MIN_MACOS_VERSION}}"

    # Universal Binary (arm64 + x64)
    - name: "{{MODULE_NAME}}-universal"
      triple: "universal-apple-darwin"
      output: "target/universal-apple-darwin/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      depends_on:
        - "{{MODULE_NAME}}-arm64"
        - "{{MODULE_NAME}}-x64"
```

**Output Types**:
- `dylib`: Dynamic library (.dylib) - can be loaded at runtime
- `staticlib`: Static library (.a) - linked at compile time
- `bin`: Executable binary
- `cdylib`: C-compatible dynamic library for FFI

### Universal Binary Creation

Use `lipo` to combine Intel and Apple Silicon binaries:

```yaml
build:
  universal:
    command: "lipo"
    args:
      - "-create"
      - "-output"
      - "{{UNIVERSAL_OUTPUT}}"
      - "{{ARM64_INPUT}}"
      - "{{X64_INPUT}}"
    verify:
      command: "lipo"
      args:
        - "-info"
        - "{{UNIVERSAL_OUTPUT}}"
```

**Build Script**:
```bash
#!/bin/bash
set -e

# Variables
MODULE_NAME="{{MODULE_NAME}}"
MIN_MACOS_VERSION="{{MIN_MACOS_VERSION}}"

# Install target triples
echo "Installing Rust targets..."
rustup target add aarch64-apple-darwin
rustup target add x86_64-apple-darwin

# Build for Apple Silicon (arm64)
echo "Building for Apple Silicon..."
cargo build --release --target aarch64-apple-darwin

# Build for Intel (x64)
echo "Building for Intel..."
cargo build --release --target x86_64-apple-darwin

# Create output directory
mkdir -p target/universal-apple-darwin/release

# Create universal binary using lipo
echo "Creating universal binary..."
lipo -create \
  -output "target/universal-apple-darwin/release/lib${MODULE_NAME}.dylib" \
  "target/aarch64-apple-darwin/release/lib${MODULE_NAME}.dylib" \
  "target/x86_64-apple-darwin/release/lib${MODULE_NAME}.dylib"

# Verify universal binary
echo "Verifying universal binary..."
lipo -info "target/universal-apple-darwin/release/lib${MODULE_NAME}.dylib"

# Expected output:
# Architectures in the fat file: target/universal-apple-darwin/release/lib${MODULE_NAME}.dylib are: x86_64 arm64

echo "Universal binary created successfully"
```

### Cargo Configuration

Create `.cargo/config.toml` for macOS-specific settings:

```toml
[target.aarch64-apple-darwin]
rustflags = [
  "-C", "target-cpu=apple-m1",
  "-C", "link-arg=-mmacosx-version-min={{MIN_MACOS_VERSION}}",
  {{#if STRIP}}
  "-C", "strip=symbols",
  {{/if}}
  {{#if LTO}}
  "-C", "lto=fat",
  {{/if}}
]

[target.x86_64-apple-darwin]
rustflags = [
  "-C", "target-cpu=x86-64-v2",
  "-C", "link-arg=-mmacosx-version-min={{MIN_MACOS_VERSION}}",
  {{#if STRIP}}
  "-C", "strip=symbols",
  {{/if}}
  {{#if LTO}}
  "-C", "lto=fat",
  {{/if}}
]

[build]
jobs = {{BUILD_JOBS}}  # Number of parallel build jobs
```

### Xcode Project Integration (Optional)

If integrating with Xcode projects:

```yaml
xcode:
  project_file: "{{PROJECT_NAME}}.xcodeproj"
  workspace_file: "{{WORKSPACE_NAME}}.xcworkspace"
  scheme: "{{SCHEME_NAME}}"
  configuration: "{{CONFIGURATION}}"  # Debug or Release

  build_settings:
    MACOSX_DEPLOYMENT_TARGET: "{{MIN_MACOS_VERSION}}"
    CODE_SIGN_IDENTITY: "{{SIGNING_IDENTITY}}"
    DEVELOPMENT_TEAM: "{{TEAM_ID}}"
    PRODUCT_BUNDLE_IDENTIFIER: "{{BUNDLE_ID}}"
```

---

## Next Parts

- [Part 3: Code Signing & Notarization](./MACOS_MODULE-part3-signing.md)
- [Part 4: Testing & Platform APIs](./MACOS_MODULE-part4-testing-apis.md)
- [Part 5: CI/CD & Troubleshooting](./MACOS_MODULE-part5-cicd-troubleshooting.md)
