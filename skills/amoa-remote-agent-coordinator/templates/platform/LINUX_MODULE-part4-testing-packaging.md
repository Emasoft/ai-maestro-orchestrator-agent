# Linux Platform Module - Testing, Packaging & CI/CD

This document covers Linux-specific testing configuration, distribution packaging, CI/CD setup, and troubleshooting.

**Parent Document**: [LINUX_MODULE.md](./LINUX_MODULE.md)

---

## Testing Configuration (Linux)

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
      - "mkdir -p {{TEST_TEMP_DIR}}"
      - "chmod 755 {{TEST_TEMP_DIR}}"
    teardown:
      - "rm -rf {{TEST_TEMP_DIR}}"
    environment:
      TEST_FIXTURES_DIR: "{{FIXTURES_PATH}}"
    timeout: {{TIMEOUT_SECONDS}}
```

### Linux-Specific Tests

```yaml
testing:
  platform_specific:
    # inotify File Monitoring
    - name: "inotify-monitoring"
      command: "cargo test --test inotify_tests"
      required: true
      notes: "Tests inotify file system monitoring"

    # D-Bus Integration
    - name: "dbus-integration"
      command: "cargo test --test dbus_tests"
      required: false
      condition: "has_dbus"
      notes: "Tests D-Bus communication"

    # systemd Integration
    - name: "systemd-integration"
      command: "cargo test --test systemd_tests"
      required: false
      condition: "has_systemd"
      notes: "Tests systemd service integration"

    # procfs Access
    - name: "procfs-access"
      command: "cargo test --test procfs_tests"
      required: true
      notes: "Tests /proc filesystem access"

    # Static Binary Verification
    - name: "static-binary-check"
      command: "ldd target/x86_64-unknown-linux-musl/release/{{MODULE_NAME}}"
      required: true
      expected_output: "not a dynamic executable"
      notes: "Verifies binary is fully static"
```

---

## Distribution-Specific Packaging

### Debian/Ubuntu (.deb)

```yaml
packaging:
  deb:
    package_name: "{{PACKAGE_NAME}}"
    version: "{{VERSION}}"
    architecture: "{{ARCH}}"  # amd64, arm64, armhf, i386
    maintainer: "{{MAINTAINER}}"
    description: "{{DESCRIPTION}}"

    dependencies:
      - "libc6 (>= 2.31)"
      - "{{DEPENDENCY_2}}"

    install_path: "/usr/bin/{{MODULE_NAME}}"

    build_command: |
      cargo install cargo-deb
      cargo deb --target={{TARGET_TRIPLE}}
```

**Create with cargo-deb**:
```toml
# Add to Cargo.toml
[package.metadata.deb]
maintainer = "{{MAINTAINER}}"
copyright = "{{COPYRIGHT}}"
license-file = ["LICENSE", "0"]
extended-description = "{{EXTENDED_DESCRIPTION}}"
depends = "$auto"
section = "utils"
priority = "optional"
assets = [
    ["target/release/{{MODULE_NAME}}", "usr/bin/", "755"],
    ["README.md", "usr/share/doc/{{PACKAGE_NAME}}/", "644"],
]
```

### Fedora/RHEL (.rpm)

```yaml
packaging:
  rpm:
    package_name: "{{PACKAGE_NAME}}"
    version: "{{VERSION}}"
    release: "1"
    architecture: "{{ARCH}}"  # x86_64, aarch64, armv7hl, i686
    summary: "{{SUMMARY}}"
    license: "{{LICENSE}}"

    requires:
      - "glibc >= 2.31"
      - "{{DEPENDENCY_2}}"

    build_command: |
      cargo install cargo-rpm
      cargo rpm build --target={{TARGET_TRIPLE}}
```

### Arch Linux (PKGBUILD)

```bash
# PKGBUILD
pkgname={{PACKAGE_NAME}}
pkgver={{VERSION}}
pkgrel=1
pkgdesc="{{DESCRIPTION}}"
arch=('x86_64' 'aarch64' 'armv7h')
url="{{PROJECT_URL}}"
license=('{{LICENSE}}')
depends=('glibc')
makedepends=('rust' 'cargo')
source=("$pkgname-$pkgver.tar.gz::{{SOURCE_URL}}")
sha256sums=('{{SHA256}}')

build() {
    cd "$pkgname-$pkgver"
    cargo build --release --locked
}

package() {
    cd "$pkgname-$pkgver"
    install -Dm755 "target/release/$pkgname" "$pkgdir/usr/bin/$pkgname"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
```

---

## CI/CD Configuration (Linux)

### GitHub Actions Matrix

```yaml
name: Linux Build

on: [push, pull_request]

jobs:
  build-linux:
    strategy:
      matrix:
        os: [ubuntu-20.04, ubuntu-22.04]
        rust: [stable]
        target:
          - x86_64-unknown-linux-gnu
          - x86_64-unknown-linux-musl
          - aarch64-unknown-linux-gnu
          - armv7-unknown-linux-gnueabihf

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: ${{ matrix.rust }}
          targets: ${{ matrix.target }}

      - name: Install Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential

          # Install musl tools for static builds
          if [[ "${{ matrix.target }}" == *"musl"* ]]; then
            sudo apt-get install -y musl-tools
          fi

          # Install cross-compilation tools for ARM
          if [[ "${{ matrix.target }}" == "aarch64"* ]]; then
            sudo apt-get install -y gcc-aarch64-linux-gnu
          fi
          if [[ "${{ matrix.target }}" == "armv7"* ]]; then
            sudo apt-get install -y gcc-arm-linux-gnueabihf
          fi

      - name: Build
        run: |
          cargo build --release --target ${{ matrix.target }}

      - name: Test
        # Only test on native architecture
        if: matrix.target == 'x86_64-unknown-linux-gnu' || matrix.target == 'x86_64-unknown-linux-musl'
        run: |
          cargo test --release --target ${{ matrix.target }}

      - name: Verify Static Binary
        if: matrix.target == 'x86_64-unknown-linux-musl'
        run: |
          ldd target/${{ matrix.target }}/release/{{MODULE_NAME}} && exit 1 || echo "Static binary confirmed"

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: {{MODULE_NAME}}-linux-${{ matrix.target }}
          path: target/${{ matrix.target }}/release/{{MODULE_NAME}}
```

---

## Troubleshooting

### Build Issues

**Problem**: `error: linker 'cc' not found`
**Solution**: Install build tools: `sudo apt-get install build-essential`

**Problem**: `= note: /usr/bin/ld: cannot find -lpthread`
**Solution**: Install development packages: `sudo apt-get install libc6-dev`

**Problem**: `error: failed to run custom build command for 'openssl-sys'`
**Solution**: Install OpenSSL development package: `sudo apt-get install libssl-dev pkg-config`

### Cross-Compilation Issues

**Problem**: ARM cross-compilation fails with `cannot find crt1.o`
**Solution**: Install ARM cross-compiler and libc: `sudo apt-get install gcc-aarch64-linux-gnu libc6-dev-arm64-cross`

**Problem**: `error: linking with 'musl-gcc' failed`
**Solution**: Install musl tools: `sudo apt-get install musl-tools`

### Runtime Issues

**Problem**: `error while loading shared libraries: libfoo.so.1: cannot open shared object file`
**Solution**: Either install the library, or build with static linking using musl

**Problem**: Static binary fails with DNS lookups
**Solution**: musl doesn't support NSS. Use pure Rust DNS resolver or dynamic linking

**Problem**: `Permission denied` when accessing files
**Solution**: Check file permissions with `ls -l`, adjust with `chmod`

---

## Related Documentation

- [LINUX_MODULE.md](./LINUX_MODULE.md) - Main index
- [LINUX_MODULE-part3-platform-apis.md](./LINUX_MODULE-part3-platform-apis.md) - Platform APIs
- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base template
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules
