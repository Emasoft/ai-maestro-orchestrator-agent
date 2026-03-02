# Linux Platform Module - Build Configuration

This document covers Linux-specific build configuration including compiler settings, target configuration, and Cargo setup.

**Parent Document**: [LINUX_MODULE.md](./LINUX_MODULE.md)

---

## Compiler & Toolchain

```yaml
build:
  compiler: "gcc"                   # gcc or clang
  toolchain: "stable"               # Rust toolchain
  gcc_version: "{{MIN_GCC}}"        # Minimum GCC version

  optimization: "{{OPT_LEVEL}}"     # 0, 1, 2, 3, s, z
  debug_symbols: {{DEBUG}}          # true for debugging
  strip: {{STRIP}}                  # true to strip symbols
  lto: {{LTO}}                      # true for link-time optimization
  static_linking: {{STATIC}}        # true for static binary (with musl)
```

**Variables**:
- `{{MIN_GCC}}`: Minimum GCC version (e.g., "9.4", "11.2")
- `{{STATIC}}`: Whether to create fully static binary (requires musl libc)

---

## Target Configuration

```yaml
build:
  targets:
    # x86_64 (glibc) - Most common
    - name: "{{MODULE_NAME}}-x64-glibc"
      triple: "x86_64-unknown-linux-gnu"
      output: "target/x86_64-unknown-linux-gnu/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C link-arg=-Wl,-rpath,$ORIGIN"

    # x86_64 (musl) - Static linking
    - name: "{{MODULE_NAME}}-x64-musl"
      triple: "x86_64-unknown-linux-musl"
      output: "target/x86_64-unknown-linux-musl/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C target-feature=+crt-static"
        - "-C link-arg=-static"

    # ARM64 (aarch64) - Raspberry Pi 4, ARM servers
    - name: "{{MODULE_NAME}}-arm64"
      triple: "aarch64-unknown-linux-gnu"
      output: "target/aarch64-unknown-linux-gnu/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C link-arg=-Wl,-rpath,$ORIGIN"

    # ARMv7 - Raspberry Pi 3, older ARM devices
    - name: "{{MODULE_NAME}}-armv7"
      triple: "armv7-unknown-linux-gnueabihf"
      output: "target/armv7-unknown-linux-gnueabihf/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C link-arg=-Wl,-rpath,$ORIGIN"

    # i686 (32-bit) - Legacy support
    - name: "{{MODULE_NAME}}-i686"
      triple: "i686-unknown-linux-gnu"
      output: "target/i686-unknown-linux-gnu/release/{{OUTPUT_NAME}}"
      type: "{{OUTPUT_TYPE}}"
      rustflags:
        - "-C link-arg=-Wl,-rpath,$ORIGIN"
```

**Output Types**:
- `so`: Shared object (.so) - dynamic library
- `a`: Archive (.a) - static library
- `bin`: Executable binary
- `cdylib`: C-compatible shared library for FFI

**RPATH Explanation**:
- `-Wl,-rpath,$ORIGIN`: Tells dynamic linker to look for shared libraries in same directory as executable
- Enables portable binaries that can be moved without breaking library references

---

## Cargo Configuration

Create `.cargo/config.toml` for Linux-specific settings:

```toml
[target.x86_64-unknown-linux-gnu]
linker = "gcc"
rustflags = [
  "-C", "link-arg=-Wl,-rpath,$ORIGIN",
  {{#if DEBUG}}
  "-C", "debuginfo=2",
  {{else}}
  "-C", "strip=symbols",
  {{/if}}
]

[target.x86_64-unknown-linux-musl]
linker = "musl-gcc"
rustflags = [
  "-C", "target-feature=+crt-static",
  "-C", "link-arg=-static",
  {{#if LTO}}
  "-C", "lto=fat",
  {{/if}}
]

[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
rustflags = [
  "-C", "link-arg=-Wl,-rpath,$ORIGIN",
]

[target.armv7-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"
rustflags = [
  "-C", "link-arg=-Wl,-rpath,$ORIGIN",
]

[build]
jobs = {{BUILD_JOBS}}
target-dir = "target"
```

---

## Static Binary with musl

For fully portable static binaries:

```bash
#!/bin/bash
set -e

# Install musl toolchain
rustup target add x86_64-unknown-linux-musl

# Install musl-tools (Ubuntu/Debian)
sudo apt-get install -y musl-tools

# Build static binary
cargo build --release --target x86_64-unknown-linux-musl

# Verify it's static
ldd target/x86_64-unknown-linux-musl/release/{{MODULE_NAME}}
# Should output: "not a dynamic executable"

echo "Static binary created"
```

**Advantages of Static Binaries**:
- Single file, no dependency issues
- Works on any Linux distro (even without glibc)
- Ideal for containers and embedded systems

**Disadvantages**:
- Larger binary size
- Can't use dynamic features (plugins, hot reload)
- NSS (Name Service Switch) doesn't work (affects DNS, user lookup)

---

## Cross-Compilation

### ARM64 Cross-Compilation (from x64)

```bash
#!/bin/bash
set -e

# Install cross-compilation tools
sudo apt-get install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# Install Rust target
rustup target add aarch64-unknown-linux-gnu

# Configure Cargo
cat >> .cargo/config.toml <<EOF
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
EOF

# Build
cargo build --release --target aarch64-unknown-linux-gnu

echo "ARM64 binary created"
```

### ARMv7 Cross-Compilation (from x64)

```bash
#!/bin/bash
set -e

# Install cross-compilation tools
sudo apt-get install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# Install Rust target
rustup target add armv7-unknown-linux-gnueabihf

# Configure Cargo
cat >> .cargo/config.toml <<EOF
[target.armv7-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"
EOF

# Build
cargo build --release --target armv7-unknown-linux-gnueabihf

echo "ARMv7 binary created"
```

---

## Related Documentation

- [LINUX_MODULE.md](./LINUX_MODULE.md) - Main index
- [LINUX_MODULE-part1-dependencies.md](./LINUX_MODULE-part1-dependencies.md) - Dependencies
- [LINUX_MODULE-part3-platform-apis.md](./LINUX_MODULE-part3-platform-apis.md) - Platform APIs
