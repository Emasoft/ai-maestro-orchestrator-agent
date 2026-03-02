# macOS Module: CI/CD & Troubleshooting

This document covers macOS-specific CI/CD configuration and troubleshooting. This is Part 5 of the macOS Platform Module documentation.

**Prerequisites**: Read [Part 4: Testing & Platform APIs](./MACOS_MODULE-part4-testing-apis.md) first.

---

## CI/CD Configuration (macOS)

### GitHub Actions Matrix

```yaml
name: macOS Build

on: [push, pull_request]

jobs:
  build-macos:
    strategy:
      matrix:
        os: [macos-13, macos-14]  # Intel and Apple Silicon
        rust: [stable]
        target:
          - x86_64-apple-darwin
          - aarch64-apple-darwin

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: ${{ matrix.rust }}
          targets: ${{ matrix.target }}

      - name: Install dependencies
        run: |
          brew install cmake pkg-config

      - name: Build
        run: |
          cargo build --release --target ${{ matrix.target }}

      - name: Test
        run: |
          cargo test --release --target ${{ matrix.target }}

      - name: Create Universal Binary
        if: matrix.os == 'macos-14'  # Only on Apple Silicon runner
        run: |
          ./scripts/create_universal_binary.sh

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: {{MODULE_NAME}}-macos-${{ matrix.target }}
          path: target/${{ matrix.target }}/release/{{OUTPUT_NAME}}
```

### Cross-Compilation from Linux

Compile macOS binaries on Linux using osxcross:

```yaml
build:
  cross_compile:
    toolchain: "osxcross"
    sdk_version: "{{MACOS_SDK_VERSION}}"

    setup:
      - "git clone https://github.com/tpoechtrager/osxcross"
      - "cd osxcross && ./build.sh"
      - "export PATH=$PATH:$(pwd)/target/bin"

    targets:
      - triple: "x86_64-apple-darwin"
        cc: "o64-clang"
        cxx: "o64-clang++"

      - triple: "aarch64-apple-darwin"
        cc: "oa64-clang"
        cxx: "oa64-clang++"
```

---

## Troubleshooting

### Build Issues

**Problem**: `ld: framework not found Foundation`
**Solution**: Install Xcode Command Line Tools: `xcode-select --install`

**Problem**: `error: linking with 'cc' failed`
**Solution**: Set deployment target: `export MACOSX_DEPLOYMENT_TARGET={{MIN_MACOS_VERSION}}`

**Problem**: Universal binary creation fails with `lipo: can't create universal file`
**Solution**: Ensure both arm64 and x64 binaries exist and are the same file type (both dylib or both bin)

### Code Signing Issues

**Problem**: `errSecInternalComponent` during signing
**Solution**: Unlock keychain first: `security unlock-keychain ~/Library/Keychains/login.keychain-db`

**Problem**: `code object is not signed at all`
**Solution**: Sign with hardened runtime: `codesign --sign "{{IDENTITY}}" --options runtime --timestamp "{{BINARY}}"`

### Notarization Issues

**Problem**: `Invalid notarization format`
**Solution**: Submit as ZIP or PKG, not raw binary: `ditto -c -k --keepParent app.dylib app.zip`

**Problem**: `The binary uses restricted entitlements`
**Solution**: Remove unnecessary entitlements from entitlements.plist

### Runtime Issues

**Problem**: `dyld: Library not loaded`
**Solution**: Use `@rpath` and set `install_name`: `install_name_tool -id @rpath/{{LIB}}.dylib {{LIB}}.dylib`

**Problem**: `Operation not permitted` when accessing files
**Solution**: Grant Full Disk Access in System Preferences > Security & Privacy

**Problem**: App crashes on Apple Silicon
**Solution**: Rebuild for arm64 target, don't use Rosetta translation

---

## Related Documentation

- [MACOS_MODULE.md](./MACOS_MODULE.md) - Index/Overview (this document's parent)
- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base template (read first)
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules
- `references/macos/fsevent_api.md` - FSEvents file monitoring
- `references/macos/appkit_integration.md` - AppKit framework usage
- `references/macos/keychain_api.md` - Keychain access
- `references/macos/metal_acceleration.md` - Metal GPU acceleration
- `references/macos/code_signing.md` - Code signing and notarization details
