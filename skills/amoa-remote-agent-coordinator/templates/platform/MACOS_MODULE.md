# macOS Platform Module Template

This template extends [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) with macOS-specific configuration, build instructions, and platform integration details.

**Read PLATFORM_MODULE_BASE.md first** - This document serves as an index to macOS-specific documentation.

---

## Document Structure

This macOS module documentation is split into 5 parts for easier navigation:

| Part | File | Content | Lines |
|------|------|---------|-------|
| 1 | [MACOS_MODULE-part1-dependencies.md](./MACOS_MODULE-part1-dependencies.md) | Module identification, Apple frameworks, Rust crates, Homebrew deps | ~150 |
| 2 | [MACOS_MODULE-part2-build.md](./MACOS_MODULE-part2-build.md) | Compiler config, targets, universal binaries, Cargo config, Xcode | ~180 |
| 3 | [MACOS_MODULE-part3-signing.md](./MACOS_MODULE-part3-signing.md) | Code signing, entitlements, notarization workflow | ~125 |
| 4 | [MACOS_MODULE-part4-testing-apis.md](./MACOS_MODULE-part4-testing-apis.md) | Unit/integration tests, FSEvents, AppKit, Keychain, Metal APIs | ~145 |
| 5 | [MACOS_MODULE-part5-cicd-troubleshooting.md](./MACOS_MODULE-part5-cicd-troubleshooting.md) | GitHub Actions, cross-compilation, troubleshooting | ~130 |

---

## Quick Reference

### Part 1: Dependencies
- [Module Identification](./MACOS_MODULE-part1-dependencies.md#module-identification-macos)
- [Apple Frameworks](./MACOS_MODULE-part1-dependencies.md#apple-frameworks)
- [Rust Crates for macOS](./MACOS_MODULE-part1-dependencies.md#rust-crates-for-macos)
- [Homebrew Dependencies](./MACOS_MODULE-part1-dependencies.md#homebrew-dependencies-optional)

### Part 2: Build Configuration
- [Compiler and Toolchain](./MACOS_MODULE-part2-build.md#compiler-and-toolchain)
- [Target Configuration](./MACOS_MODULE-part2-build.md#target-configuration)
- [Universal Binary Creation](./MACOS_MODULE-part2-build.md#universal-binary-creation)
- [Cargo Configuration](./MACOS_MODULE-part2-build.md#cargo-configuration)
- [Xcode Project Integration](./MACOS_MODULE-part2-build.md#xcode-project-integration-optional)

### Part 3: Code Signing & Notarization
- [Code Signing](./MACOS_MODULE-part3-signing.md#code-signing)
- [Entitlements File](./MACOS_MODULE-part3-signing.md#code-signing)
- [Notarization](./MACOS_MODULE-part3-signing.md#notarization)
- [Notarization Workflow Script](./MACOS_MODULE-part3-signing.md#notarization)

### Part 4: Testing & Platform APIs
- [Unit Tests](./MACOS_MODULE-part4-testing-apis.md#unit-tests)
- [Integration Tests](./MACOS_MODULE-part4-testing-apis.md#integration-tests)
- [macOS-Specific Tests](./MACOS_MODULE-part4-testing-apis.md#macos-specific-tests)
- [Performance Benchmarks](./MACOS_MODULE-part4-testing-apis.md#performance-benchmarks)
- [FSEvents API](./MACOS_MODULE-part4-testing-apis.md#file-system-events-fsevents)
- [AppKit Integration](./MACOS_MODULE-part4-testing-apis.md#appkit-integration)
- [Keychain Access](./MACOS_MODULE-part4-testing-apis.md#keychain-access)
- [Metal GPU Acceleration](./MACOS_MODULE-part4-testing-apis.md#metal-gpu-acceleration)

### Part 5: CI/CD & Troubleshooting
- [GitHub Actions Matrix](./MACOS_MODULE-part5-cicd-troubleshooting.md#github-actions-matrix)
- [Cross-Compilation from Linux](./MACOS_MODULE-part5-cicd-troubleshooting.md#cross-compilation-from-linux)
- [Build Issues](./MACOS_MODULE-part5-cicd-troubleshooting.md#build-issues)
- [Code Signing Issues](./MACOS_MODULE-part5-cicd-troubleshooting.md#code-signing-issues)
- [Notarization Issues](./MACOS_MODULE-part5-cicd-troubleshooting.md#notarization-issues)
- [Runtime Issues](./MACOS_MODULE-part5-cicd-troubleshooting.md#runtime-issues)

---

## Module Overview

### Supported Architectures

| Architecture | Target Triple | CPU Flag | Notes |
|--------------|---------------|----------|-------|
| Apple Silicon | `aarch64-apple-darwin` | `apple-m1` | M1/M2/M3 chips |
| Intel | `x86_64-apple-darwin` | `x86-64-v2` | Intel Macs |
| Universal | `universal-apple-darwin` | N/A | Combined via `lipo` |

### Key macOS Dependencies

**System Frameworks**:
- Foundation, AppKit, CoreFoundation (core)
- CoreServices (FSEvents file monitoring)
- Security (Keychain access)
- Metal, MetalKit (GPU acceleration - optional)

**Rust Crates**:
- `objc`, `cocoa` (Objective-C/AppKit bindings)
- `core-foundation`, `core-graphics` (CF bindings)
- `fsevent-sys` (FSEvents)
- `mach2` (Mach kernel interface)

### Build Requirements

| Requirement | Minimum Version |
|-------------|-----------------|
| macOS | 10.15 (Catalina) |
| Xcode | 14.0 |
| Rust | stable |

### Distribution Checklist

- [ ] Build for both arm64 and x64 targets
- [ ] Create universal binary with `lipo`
- [ ] Sign with Developer ID certificate
- [ ] Add required entitlements
- [ ] Submit for notarization
- [ ] Staple notarization ticket
- [ ] Verify with `spctl -a -v`

---

## Common Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MODULE_NAME}}` | Module name | `my_module` |
| `{{MODULE_VERSION}}` | Semantic version | `1.0.0` |
| `{{MIN_MACOS_VERSION}}` | Deployment target | `10.15` |
| `{{BUNDLE_ID}}` | Bundle identifier | `com.example.module` |
| `{{SIGNING_IDENTITY}}` | Code signing cert | `Developer ID Application: ...` |
| `{{TEAM_ID}}` | Apple Team ID | `XXXXXXXXXX` |
| `{{APPLE_ID}}` | Apple ID email | `dev@example.com` |

---

## Related Documentation

- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base template (read first)
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules
- `references/macos/fsevent_api.md` - FSEvents file monitoring
- `references/macos/appkit_integration.md` - AppKit framework usage
- `references/macos/keychain_api.md` - Keychain access
- `references/macos/metal_acceleration.md` - Metal GPU acceleration
- `references/macos/code_signing.md` - Code signing and notarization details
