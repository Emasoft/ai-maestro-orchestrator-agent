# LSP Selection Guide

## Overview

This guide extends the existing LSP system with automatic language detection and LSP server selection for remote agent workspaces. It integrates with toolchain templates and project-specific Claude Code configurations.

## Related Documentation

This guide builds upon:
- [../references/lsp-servers-overview.md](../references/lsp-servers-overview.md) - Comprehensive LSP server comparison
- [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md) - Installation procedures for all LSP servers
- [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) - LSP plugin structure

---

## Table of Contents

### [Part 1: Language Detection](./LSP_SELECTION_GUIDE-part1-language-detection.md)

- Automatic Detection
  - Detection methods (priority order)
  - .toolchain file
  - Build system files detection
  - File extension analysis
  - GitHub API language query
- Detection Script
  - Complete Python script: `detect_language.py`
  - Usage examples
- LSP Server Selection Matrix
  - Language to LSP server mapping table
  - Primary and alternative LSP servers
  - Installation commands per language

### [Part 2: LSP Selection Scripts](./LSP_SELECTION_GUIDE-part2-selection-scripts.md)

- LSP Selection Script
  - Complete Bash script: `select_lsp.sh`
  - Language-specific LSP configuration
  - Installation command generation
  - JSON configuration output
- Integration with Toolchain Templates
  - 5-step integration workflow
  - Language detection
  - LSP selection
  - Installation
  - Configuration merge
- LSP Installation Reference
  - Wrapper script for install_lsp.py
  - Reference to lsp-installation-guide.md
- LSP Plugin Configuration
  - Plugin directory structure setup
  - plugin.json creation
  - hooks.json for SessionStart/SessionStop
  - start-lsp.sh script template

### [Part 3: Configuration and Troubleshooting](./LSP_SELECTION_GUIDE-part3-config-troubleshooting.md)

- Per-Project Override Configuration
  - Override via .toolchain file
  - Override via settings.json
  - Override via environment variable (CLAUDE_LSP_OVERRIDE)
  - Override precedence order
- Multi-Language Project LSP Configuration
  - Configuring multiple LSP servers
  - workspaceFolder isolation
  - Example: fullstack-app with Python/TypeScript/Rust
- LSP Server Verification
  - Complete Bash script: `verify-lsp.sh`
  - Installation check
  - Version check
  - LSP initialization test
- Troubleshooting
  - LSP Server Not Found
  - LSP Server Not Starting
  - Wrong LSP Server Selected
  - Multiple Languages Conflict

---

## Quick Reference

| Task | Go To |
|------|-------|
| Detect project language | [Part 1](./LSP_SELECTION_GUIDE-part1-language-detection.md) |
| Select LSP server for language | [Part 1](./LSP_SELECTION_GUIDE-part1-language-detection.md) |
| Run LSP selection script | [Part 2](./LSP_SELECTION_GUIDE-part2-selection-scripts.md) |
| Set up LSP plugin | [Part 2](./LSP_SELECTION_GUIDE-part2-selection-scripts.md) |
| Override auto-detection | [Part 3](./LSP_SELECTION_GUIDE-part3-config-troubleshooting.md) |
| Configure multi-language project | [Part 3](./LSP_SELECTION_GUIDE-part3-config-troubleshooting.md) |
| Verify LSP installation | [Part 3](./LSP_SELECTION_GUIDE-part3-config-troubleshooting.md) |
| Fix LSP issues | [Part 3](./LSP_SELECTION_GUIDE-part3-config-troubleshooting.md) |

---

## Related Files

- [PROJECT_CLAUDE_CONFIG.md](./PROJECT_CLAUDE_CONFIG.md) - Project .claude/ structure
- [TOOLCHAIN_SKILLS_MATRIX.md](./TOOLCHAIN_SKILLS_MATRIX.md) - Skills per toolchain
- [AGENT_ENVIRONMENT_SETUP.md](./AGENT_ENVIRONMENT_SETUP.md) - Complete setup guide
- [../references/lsp-servers-overview.md](../references/lsp-servers-overview.md) - LSP comparison
- [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md) - Installation guide
- [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) - Plugin structure
