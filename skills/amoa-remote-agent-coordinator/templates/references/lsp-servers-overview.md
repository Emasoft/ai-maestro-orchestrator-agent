---
name: lsp-servers-overview
description: Overview of Language Server Protocol (LSP) servers available for different programming languages and how to select the right one for your project
---

# LSP Servers Overview

## Purpose

This reference document provides an overview of Language Server Protocol (LSP) servers available for various programming languages. Use this guide when you need to:

- Select an appropriate LSP server for a specific programming language
- Understand the capabilities and limitations of different LSP implementations
- Compare performance characteristics of LSP servers
- Make informed decisions about LSP infrastructure for remote agent coordination

> **TODO**: This is a stub file that needs comprehensive content about LSP server selection criteria, language-specific recommendations, and integration patterns.

## Available LSP Servers by Language

### Python

- **pylsp** (python-lsp-server) - Community-maintained, extensible
- **pyright** - Microsoft's static type checker with LSP support
- **jedi-language-server** - Lightweight, Jedi-based

### JavaScript/TypeScript

- **typescript-language-server** - Official TypeScript/JavaScript support
- **vscode-eslint-language-server** - ESLint integration

### Rust

- **rust-analyzer** - The recommended LSP for Rust development

## Selection Criteria

When choosing an LSP server, consider:

1. **Feature completeness** - Code completion, diagnostics, refactoring support
2. **Performance** - Memory usage, response latency
3. **Maintenance status** - Active development, community support
4. **Integration requirements** - Compatibility with your toolchain

## Related References

- See [lsp-installation-guide.md](./lsp-installation-guide.md) for installation instructions
- See [lsp-plugin-template.md](./lsp-plugin-template.md) for plugin configuration templates
