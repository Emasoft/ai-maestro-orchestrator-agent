# Cross-Platform Synchronization: CI/CD Matrix

This document covers CI/CD configuration for cross-platform builds.

**Parent document**: [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md)

---

## Contents

1. [Multi-Platform Build Matrix](#multi-platform-build-matrix)
2. [Platform-Specific Test Suites](#platform-specific-test-suites)

---

## Multi-Platform Build Matrix

```yaml
# .github/workflows/cross-platform-build.yml
name: Cross-Platform Build

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build-matrix:
    strategy:
      fail-fast: false  # Continue even if one platform fails
      matrix:
        include:
          # macOS Builds
          - os: macos-13
            platform: macos
            target: x86_64-apple-darwin
            runner_arch: x64

          - os: macos-14
            platform: macos
            target: aarch64-apple-darwin
            runner_arch: arm64

          # Windows Builds
          - os: windows-2022
            platform: windows
            target: x86_64-pc-windows-msvc
            runner_arch: x64

          - os: windows-2022
            platform: windows
            target: i686-pc-windows-msvc
            runner_arch: x86

          # Linux Builds
          - os: ubuntu-22.04
            platform: linux
            target: x86_64-unknown-linux-gnu
            runner_arch: x64

          - os: ubuntu-22.04
            platform: linux
            target: x86_64-unknown-linux-musl
            runner_arch: x64

    runs-on: ${{ matrix.os }}

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Cache Dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/bin/
            ~/.cargo/registry/index/
            ~/.cargo/registry/cache/
            ~/.cargo/git/db/
            target/
          key: ${{ matrix.os }}-${{ matrix.target }}-cargo-${{ hashFiles('**/Cargo.lock') }}

      - name: Build
        run: |
          cd platform-${{ matrix.platform }}
          cargo build --release --target ${{ matrix.target }}

      - name: Test
        # Only test on native architectures
        if: |
          (matrix.platform == 'macos' && matrix.runner_arch == 'x64' && matrix.target == 'x86_64-apple-darwin') ||
          (matrix.platform == 'macos' && matrix.runner_arch == 'arm64' && matrix.target == 'aarch64-apple-darwin') ||
          (matrix.platform == 'windows' && matrix.target == 'x86_64-pc-windows-msvc') ||
          (matrix.platform == 'linux' && matrix.target == 'x86_64-unknown-linux-gnu')
        run: |
          cd platform-${{ matrix.platform }}
          cargo test --release --target ${{ matrix.target }}

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.platform }}-${{ matrix.target }}
          path: platform-${{ matrix.platform }}/target/${{ matrix.target }}/release/*

  # Combine artifacts for release
  create-release:
    needs: build-matrix
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Download All Artifacts
        uses: actions/download-artifact@v4

      - name: Create Release Archive
        run: |
          mkdir -p release
          # Combine all platform builds
          cp macos-*/* release/
          cp windows-*/* release/
          cp linux-*/* release/

      - name: Upload Release
        uses: actions/upload-artifact@v4
        with:
          name: cross-platform-release
          path: release/
```

---

## Platform-Specific Test Suites

```yaml
# .github/workflows/platform-tests.yml
name: Platform-Specific Tests

on: [push, pull_request]

jobs:
  macos-tests:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - name: Run macOS-specific tests
        run: |
          cd platform-macos
          cargo test --test fsevent_tests
          cargo test --test appkit_tests

  windows-tests:
    runs-on: windows-2022
    steps:
      - uses: actions/checkout@v4
      - name: Run Windows-specific tests
        run: |
          cd platform-windows
          cargo test --test file_monitoring_tests
          cargo test --test registry_tests

  linux-tests:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - name: Run Linux-specific tests
        run: |
          cd platform-linux
          cargo test --test inotify_tests
          cargo test --test systemd_tests
```

---

## Related Documentation

- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Main index
- [CROSS_PLATFORM_SYNC-part3-feature-parity.md](./CROSS_PLATFORM_SYNC-part3-feature-parity.md) - Feature parity
- [CROSS_PLATFORM_SYNC-part5-release.md](./CROSS_PLATFORM_SYNC-part5-release.md) - Release coordination
