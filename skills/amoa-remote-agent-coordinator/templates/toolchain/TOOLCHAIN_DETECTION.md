---
name: toolchain-detection
description: Methods and scripts for detecting installed development toolchains, compilers, and build systems on the current system
---

# Toolchain Detection

## Purpose

This reference document provides methods for detecting installed development toolchains on the current system. Use this guide when you need to:

- Automatically discover available compilers and build tools
- Verify toolchain versions and compatibility
- Generate environment reports for remote agents
- Determine which language runtimes are available for task execution

> **TODO**: This is a stub file that needs comprehensive detection scripts, cross-platform support, and version parsing logic for all supported toolchains.

## Detection Methods

### Command-Line Detection

Detect toolchains by checking for known executables:

```bash
# Python detection
which python3 && python3 --version

# Node.js detection
which node && node --version

# Rust detection
which rustc && rustc --version

# Go detection
which go && go version
```

### Environment Variable Detection

Check standard environment variables:

- `JAVA_HOME` - Java Development Kit location
- `GOPATH` / `GOROOT` - Go workspace and installation
- `CARGO_HOME` - Rust/Cargo installation
- `NVM_DIR` - Node Version Manager

### Package Manager Detection

Detect installed package managers:

```bash
# Check for common package managers
which brew && echo "Homebrew available"
which apt && echo "APT available"
which dnf && echo "DNF available"
which pacman && echo "Pacman available"
```

## Toolchain Report Format

Standard JSON format for reporting detected toolchains:

```json
{
  "detected_at": "2025-01-16T00:00:00Z",
  "toolchains": {
    "python": {
      "available": true,
      "version": "3.12.0",
      "path": "/usr/bin/python3"
    }
  }
}
```

## Cross-Platform Considerations

Detection strategies for:
- macOS (Darwin)
- Linux (various distributions)
- Windows (PowerShell/CMD)

## Related References

- See [TOOLCHAIN_INSTALLATION.md](./TOOLCHAIN_INSTALLATION.md) for installing missing toolchains
