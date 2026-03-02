---
name: lsp-installation-guide
description: Step-by-step instructions for installing and configuring LSP servers across different platforms and package managers
---

# LSP Installation Guide

## Purpose

This reference document provides detailed installation instructions for Language Server Protocol (LSP) servers. Use this guide when you need to:

- Install LSP servers on different operating systems
- Configure LSP servers for optimal performance
- Troubleshoot common installation issues
- Set up LSP servers in containerized environments

> **TODO**: This is a stub file that needs comprehensive installation procedures for each supported LSP server, platform-specific instructions, and troubleshooting guides.

## Installation Methods

### Using Package Managers

#### npm/bun (Node.js-based servers)

```bash
# TypeScript Language Server
npm install -g typescript-language-server typescript

# ESLint Language Server
npm install -g vscode-langservers-extracted
```

#### pip/uv (Python-based servers)

```bash
# Python LSP Server
pip install python-lsp-server

# Pyright
pip install pyright
```

#### cargo (Rust-based servers)

```bash
# Rust Analyzer
rustup component add rust-analyzer
```

### Using System Package Managers

Platform-specific installation instructions for:
- macOS (Homebrew)
- Linux (apt, dnf, pacman)
- Windows (chocolatey, scoop)

## Configuration

### Environment Variables

Key environment variables for LSP configuration:

- `LSP_LOG_LEVEL` - Set logging verbosity
- `LSP_CACHE_DIR` - Custom cache directory location

### Configuration Files

Standard configuration file locations and formats for each LSP server.

## Verification

After installation, verify the LSP server is working:

```bash
# Check if binary is accessible
which <lsp-server-name>

# Test basic functionality
<lsp-server-name> --version
```

## Related References

- See [lsp-servers-overview.md](./lsp-servers-overview.md) for server selection guidance
- See [lsp-plugin-template.md](./lsp-plugin-template.md) for integration templates
