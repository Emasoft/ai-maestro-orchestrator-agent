# Linux Platform Module - Dependencies

This document covers Linux-specific dependencies including system libraries, Rust crates, and package manager commands.

**Parent Document**: [LINUX_MODULE.md](./LINUX_MODULE.md)

---

## System Libraries

```yaml
dependencies:
  system_libs:
    - name: "{{LIB_NAME}}"
      version: "{{MIN_VERSION}}"
      package_names:
        ubuntu: "{{UBUNTU_PKG}}"
        debian: "{{DEBIAN_PKG}}"
        fedora: "{{FEDORA_PKG}}"
        arch: "{{ARCH_PKG}}"
        alpine: "{{ALPINE_PKG}}"
      link_type: "{{LINK_TYPE}}"  # dynamic, static
```

### Common System Libraries

```yaml
dependencies:
  system_libs:
    # C Standard Library
    - name: "glibc"
      version: "2.31"
      package_names:
        ubuntu: "libc6"
        debian: "libc6"
        fedora: "glibc"
        arch: "glibc"
        alpine: "glibc-compat"  # Or use musl
      link_type: "dynamic"

    # POSIX Threads
    - name: "pthread"
      version: "2.31"
      package_names:
        ubuntu: "libc6"  # Included in glibc
        debian: "libc6"
        fedora: "glibc"
        arch: "glibc"
        alpine: "musl"
      link_type: "dynamic"

    # Math Library
    - name: "libm"
      version: "2.31"
      package_names:
        ubuntu: "libc6"  # Included in glibc
        debian: "libc6"
        fedora: "glibc"
        arch: "glibc"
        alpine: "musl"
      link_type: "dynamic"

    # Dynamic Linker
    - name: "libdl"
      version: "2.31"
      package_names:
        ubuntu: "libc6"  # Included in glibc
        debian: "libc6"
        fedora: "glibc"
        arch: "glibc"
        alpine: "musl"
      link_type: "dynamic"

    # D-Bus (Optional)
    - name: "dbus"
      version: "1.12"
      package_names:
        ubuntu: "libdbus-1-dev"
        debian: "libdbus-1-dev"
        fedora: "dbus-devel"
        arch: "dbus"
        alpine: "dbus-dev"
      link_type: "dynamic"
      required: false

    # systemd (Optional)
    - name: "systemd"
      version: "245"
      package_names:
        ubuntu: "libsystemd-dev"
        debian: "libsystemd-dev"
        fedora: "systemd-devel"
        arch: "systemd"
        alpine: "elogind-dev"  # Alpine uses elogind instead
      link_type: "dynamic"
      required: false
```

---

## Rust Crates for Linux

```yaml
dependencies:
  crates:
    # POSIX APIs
    - name: "libc"
      version: "0.2"
      features: []
      notes: "POSIX C bindings"

    - name: "nix"
      version: "0.27"
      features: ["fs", "signal", "process"]
      notes: "Rust-friendly POSIX wrapper"

    # File System Monitoring
    - name: "inotify"
      version: "0.10"
      features: []
      notes: "Linux inotify file monitoring"

    - name: "notify"
      version: "6.1"
      features: []
      notes: "Cross-platform file watching (uses inotify on Linux)"

    # D-Bus Integration
    - name: "dbus"
      version: "0.9"
      features: []
      notes: "D-Bus protocol implementation"

    - name: "zbus"
      version: "3.14"
      features: []
      notes: "Pure Rust D-Bus implementation"

    # systemd Integration
    - name: "systemd"
      version: "0.10"
      features: []
      notes: "systemd service integration"

    # Process Management
    - name: "procfs"
      version: "0.16"
      features: []
      notes: "Read /proc filesystem"

    - name: "sysinfo"
      version: "0.30"
      features: []
      notes: "Cross-platform system information"
```

---

## Package Manager Commands

```yaml
dependencies:
  install_commands:
    ubuntu: "sudo apt-get update && sudo apt-get install -y {{PACKAGES}}"
    debian: "sudo apt-get update && sudo apt-get install -y {{PACKAGES}}"
    fedora: "sudo dnf install -y {{PACKAGES}}"
    arch: "sudo pacman -Sy --noconfirm {{PACKAGES}}"
    alpine: "sudo apk add --no-cache {{PACKAGES}}"
```

---

## Related Documentation

- [LINUX_MODULE.md](./LINUX_MODULE.md) - Main index
- [LINUX_MODULE-part2-build-config.md](./LINUX_MODULE-part2-build-config.md) - Build configuration
