# Windows Platform Module Template

This template extends [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) with Windows-specific configuration, build instructions, and platform integration details.

**Read PLATFORM_MODULE_BASE.md first** - This document only covers Windows-specific aspects.

---

## Document Structure

This template is split into multiple parts for easier navigation:

| Part | File | Content |
|------|------|---------|
| **Part 1** | [WINDOWS_MODULE-part1-dependencies.md](./WINDOWS_MODULE-part1-dependencies.md) | Module Identification, Dependencies |
| **Part 2** | [WINDOWS_MODULE-part2-build.md](./WINDOWS_MODULE-part2-build.md) | Build Configuration, Manifests, Resources |
| **Part 3** | [WINDOWS_MODULE-part3-apis-testing.md](./WINDOWS_MODULE-part3-apis-testing.md) | Platform APIs, Testing, CI/CD, Troubleshooting |

---

## Part 1: Identification and Dependencies

**File**: [WINDOWS_MODULE-part1-dependencies.md](./WINDOWS_MODULE-part1-dependencies.md)

### Contents
- 1.1 Module Identification (Windows)
  - Platform, architecture, Windows version requirements
  - Subsystem configuration (console, windows, native)
  - Manifest and resource file paths
- 1.2 Windows-Specific Dependencies
  - 1.2.1 Windows SDK configuration
  - 1.2.2 Visual C++ Runtime options (dynamic vs static)
  - 1.2.3 Rust crates for Windows (windows, windows-sys, winreg, etc.)
  - 1.2.4 System libraries (kernel32, user32, shell32, etc.)

---

## Part 2: Build Configuration

**File**: [WINDOWS_MODULE-part2-build.md](./WINDOWS_MODULE-part2-build.md)

### Contents
- 2.1 MSVC Toolchain Configuration
  - Compiler version, platform toolset
  - Optimization and debug settings
  - Incremental builds, whole program optimization
- 2.2 Target Configuration
  - x64 (64-bit) builds
  - x86 (32-bit legacy) builds
  - ARM64 (Windows on ARM) builds
  - Output types: dll, lib, exe, cdylib
- 2.3 Cargo Configuration
  - `.cargo/config.toml` setup
  - Rustflags for Windows targets
- 2.4 Application Manifest
  - UAC execution levels (asInvoker, highestAvailable, requireAdministrator)
  - DPI awareness (PerMonitorV2)
  - Supported OS versions
  - Visual styles and common controls
- 2.5 Resource File
  - Version information
  - Icon embedding
  - File type metadata
- 2.6 Build Script (build.rs)
  - Resource compilation
  - Library linking
  - Subsystem configuration

---

## Part 3: Platform APIs, Testing, and CI/CD

**File**: [WINDOWS_MODULE-part3-apis-testing.md](./WINDOWS_MODULE-part3-apis-testing.md)

### Contents
- 3.1 Platform-Specific APIs
  - 3.1.1 File System Monitoring (ReadDirectoryChangesW)
  - 3.1.2 Registry Access (winreg crate)
  - 3.1.3 COM Interop (windows crate)
  - 3.1.4 Windows Service Integration
- 3.2 Testing Configuration
  - 3.2.1 Unit tests setup
  - 3.2.2 Integration tests with setup/teardown
  - 3.2.3 Windows-specific test categories
- 3.3 Cross-Compilation
  - 3.3.1 From Linux using mingw-w64
  - 3.3.2 From macOS using mingw-w64 via Homebrew
- 3.4 CI/CD Configuration
  - GitHub Actions matrix for Windows builds
  - Multi-architecture builds (x64, x86, ARM64)
- 3.5 Troubleshooting
  - Build issues (linker, SDK)
  - Linking issues (external symbols)
  - Runtime issues (DLL missing, UAC, permissions)

---

## Quick Reference

### Supported Architectures

| Architecture | Target Triple | Notes |
|--------------|---------------|-------|
| x64 (64-bit) | `x86_64-pc-windows-msvc` | Most common |
| x86 (32-bit) | `i686-pc-windows-msvc` | Legacy support |
| ARM64 | `aarch64-pc-windows-msvc` | Windows on ARM |

### Windows Version Reference

| Version | Build Number |
|---------|--------------|
| Windows 10 1809 | `10.0.17763` |
| Windows 10 2004 | `10.0.19041` |
| Windows 10 21H2 | `10.0.19044` |
| Windows 11 21H2 | `10.0.22000` |
| Windows 11 22H2 | `10.0.22621` |
| Windows 11 23H2 | `10.0.22631` |

### Key Crates

| Crate | Version | Purpose |
|-------|---------|---------|
| `windows` | 0.52 | Official Windows API bindings |
| `windows-sys` | 0.52 | Lightweight Windows API bindings |
| `winreg` | 0.52 | Registry access |
| `windows-service` | 0.6 | Windows Service integration |
| `notify` | 6.1 | File system monitoring |

### UAC Levels

| Level | Description |
|-------|-------------|
| `asInvoker` | Run with current user privileges (most common) |
| `highestAvailable` | Run with highest available privileges |
| `requireAdministrator` | Always require administrator |

---

## Related Documentation

- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base template (read first)
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules
- [MACOS_MODULE.md](./MACOS_MODULE.md) - macOS platform template
- [LINUX_MODULE.md](./LINUX_MODULE.md) - Linux platform template

### Reference Documents
- `references/windows/file_monitoring.md` - File system monitoring
- `references/windows/registry_access.md` - Registry operations
- `references/windows/com_interop.md` - COM integration
- `references/windows/windows_service.md` - Service creation
- `references/windows/manifest_guide.md` - Application manifest details
