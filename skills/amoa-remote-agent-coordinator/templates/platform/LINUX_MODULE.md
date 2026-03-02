# Linux Platform Module Template

This template extends [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) with Linux-specific configuration, build instructions, and platform integration details.

**Read PLATFORM_MODULE_BASE.md first** - This document only covers Linux-specific aspects.

---

## Document Structure

This module is split into multiple parts for easier navigation:

| Part | Document | Contents |
|------|----------|----------|
| Index | This file | Module identification, overview, kernel reference |
| Part 1 | [LINUX_MODULE-part1-dependencies.md](./LINUX_MODULE-part1-dependencies.md) | System libraries, Rust crates, package managers |
| Part 2 | [LINUX_MODULE-part2-build-config.md](./LINUX_MODULE-part2-build-config.md) | Compiler, targets, Cargo config, cross-compilation |
| Part 3 | [LINUX_MODULE-part3-platform-apis.md](./LINUX_MODULE-part3-platform-apis.md) | inotify, D-Bus, systemd, procfs |
| Part 4 | [LINUX_MODULE-part4-testing-packaging.md](./LINUX_MODULE-part4-testing-packaging.md) | Testing, .deb/.rpm/PKGBUILD, CI/CD, troubleshooting |

---

## Module Identification (Linux)

```yaml
module:
  name: "{{MODULE_NAME}}"
  version: "{{MODULE_VERSION}}"
  platform: "linux"
  architecture: "{{ARCH}}"          # x64, arm64, armv7, i686
  min_kernel_version: "{{MIN_KERNEL}}"  # e.g., "5.4" for Ubuntu 20.04
  libc: "{{LIBC_TYPE}}"            # glibc, musl
  type: "{{MODULE_TYPE}}"          # so, a, bin

linux_specific:
  libc_version: "{{LIBC_VERSION}}"
  requires_systemd: {{REQUIRES_SYSTEMD}}
  requires_dbus: {{REQUIRES_DBUS}}
  distribution_targets:
    - "{{DISTRO_1}}"  # ubuntu, debian, fedora, arch, alpine
    - "{{DISTRO_2}}"
```

**Variables**:
- `{{ARCH}}`: Target architecture (x64, arm64, armv7, i686, riscv64)
- `{{MIN_KERNEL}}`: Minimum Linux kernel version (e.g., "5.4", "5.15")
- `{{LIBC_TYPE}}`: C library type (glibc for most distros, musl for Alpine/static builds)
- `{{LIBC_VERSION}}`: Minimum glibc/musl version (e.g., "2.31" for glibc)
- `{{REQUIRES_SYSTEMD}}`: Whether systemd is required (true for service integration)
- `{{REQUIRES_DBUS}}`: Whether D-Bus is required (true for desktop integration)

---

## Kernel Version Reference

| Distribution | Release | Kernel Version |
|--------------|---------|----------------|
| Ubuntu 20.04 LTS | Focal | 5.4 |
| Ubuntu 22.04 LTS | Jammy | 5.15 |
| Ubuntu 24.04 LTS | Noble | 6.8 |
| Debian 11 | Bullseye | 5.10 |
| Debian 12 | Bookworm | 6.1 |
| Fedora 38 | - | 6.2 |
| Fedora 39 | - | 6.5 |
| RHEL 9 | - | 5.14 |

---

## Quick Reference: Part Contents

### Part 1: Dependencies
- System libraries (glibc, pthread, libm, libdl, dbus, systemd)
- Rust crates (libc, nix, inotify, notify, dbus, zbus, systemd, procfs, sysinfo)
- Package manager commands (apt, dnf, pacman, apk)

See: [LINUX_MODULE-part1-dependencies.md](./LINUX_MODULE-part1-dependencies.md)

### Part 2: Build Configuration
- Compiler & toolchain settings (gcc, clang, optimization levels)
- Target configuration (x64-glibc, x64-musl, arm64, armv7, i686)
- Cargo configuration (.cargo/config.toml)
- Static binary creation with musl
- Cross-compilation for ARM64 and ARMv7

See: [LINUX_MODULE-part2-build-config.md](./LINUX_MODULE-part2-build-config.md)

### Part 3: Platform-Specific APIs
- File system monitoring with inotify
- D-Bus integration for IPC
- systemd service integration
- procfs access for process information

See: [LINUX_MODULE-part3-platform-apis.md](./LINUX_MODULE-part3-platform-apis.md)

### Part 4: Testing, Packaging & CI/CD
- Unit and integration test configuration
- Linux-specific tests (inotify, dbus, systemd, procfs)
- Debian/Ubuntu packaging (.deb with cargo-deb)
- Fedora/RHEL packaging (.rpm with cargo-rpm)
- Arch Linux packaging (PKGBUILD)
- GitHub Actions matrix for multi-target builds
- Troubleshooting common build and runtime issues

See: [LINUX_MODULE-part4-testing-packaging.md](./LINUX_MODULE-part4-testing-packaging.md)

---

## Related Documentation

- [PLATFORM_MODULE_BASE.md](./PLATFORM_MODULE_BASE.md) - Base template (read first)
- [CROSS_PLATFORM_SYNC.md](./CROSS_PLATFORM_SYNC.md) - Synchronization rules
- `references/linux/inotify_api.md` - File system monitoring
- `references/linux/dbus_integration.md` - D-Bus communication
- `references/linux/systemd_service.md` - systemd service creation
- `references/linux/procfs_access.md` - /proc filesystem access
- `references/linux/static_linking.md` - Creating static binaries with musl
