# Agent Environment Setup

## Overview

Complete guide for setting up a remote agent's development environment, including toolchain installation, LSP server configuration, Claude Code skills, and project-specific `.claude/` directory.

This document serves as the **index** to the full environment setup guide. Each phase is detailed in separate part files for easier navigation and maintenance.

---

## Setup Phases Summary

The environment setup consists of 5 phases, executed in order:

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Toolchain Installation | Install language-specific development tools |
| 2 | LSP Server Installation | Install and configure Language Server Protocol servers |
| 3 | Claude Code Skills Installation | Install project-specific skills |
| 4 | Project Configuration | Configure `.claude/` directory |
| 5 | Environment Verification | Verify all components working correctly |

---

## Table of Contents

### Part 1: Toolchain & LSP Installation

**File**: [AGENT_ENVIRONMENT_SETUP-part1-toolchain-lsp.md](./AGENT_ENVIRONMENT_SETUP-part1-toolchain-lsp.md)

Contents:
- **Phase 1: Toolchain Installation**
  - 1.1 Detect Required Toolchain - Auto-detect language from project
  - 1.2 Install Toolchain - Run language-specific installation scripts
  - 1.3 Verify Toolchain - Confirm toolchain commands available
- **Phase 2: LSP Server Installation**
  - 2.1 Select LSP Server - Choose appropriate LSP for language
  - 2.2 Install LSP Server - Install via package manager
  - 2.3 Verify LSP Server - Confirm LSP command available

### Part 2: Skills & Project Configuration

**File**: [AGENT_ENVIRONMENT_SETUP-part2-skills-config.md](./AGENT_ENVIRONMENT_SETUP-part2-skills-config.md)

Contents:
- **Phase 3: Claude Code Skills Installation**
  - 3.1 Determine Required Skills - Match skills to toolchain
  - 3.2 Install Skills - Create symlinks to orchestrator skills
  - 3.3 Verify Skills - Check skill structure validity
- **Phase 4: Project Configuration**
  - 4.1 Create .claude/ Directory Structure - Set up directories
  - 4.2 Generate settings.json - Configure agent settings
  - 4.3 Configure LSP Plugin - Create plugin files
  - 4.4 Create Project-Specific CLAUDE.md - Generate project docs

### Part 3: Verification & Reference

**File**: [AGENT_ENVIRONMENT_SETUP-part3-verification-reference.md](./AGENT_ENVIRONMENT_SETUP-part3-verification-reference.md)

Contents:
- **Phase 5: Environment Verification**
  - 5.1 Comprehensive Verification Script - Full environment check
  - 5.2 Quick Verification Checklist - Fast validation commands
- **Complete Setup Script** - All-in-one automated setup
- **Variables Reference** - Template variable documentation
- **Troubleshooting**
  - Toolchain Installation Fails
  - LSP Server Not Found After Installation
  - Skills Symlinks Broken
  - settings.json Invalid
- **Related Files** - Links to additional documentation

---

## Quick Start

To set up an agent environment, run the complete setup script:

```bash
bash complete-setup.sh {{PROJECT_ROOT}} {{ORCHESTRATOR_SKILLS_DIR}}
```

Or execute phases individually:

```bash
# Phase 1: Install toolchain
TOOLCHAIN=$(python3 detect_language.py {{PROJECT_ROOT}})
bash ../toolchain/install-scripts/install_${TOOLCHAIN}.sh

# Phase 2: Install LSP server
python3 ../references/scripts/install_lsp.py --language $TOOLCHAIN

# Phase 3: Install skills
bash install-skills.sh "$TOOLCHAIN" "{{PROJECT_ROOT}}" "{{ORCHESTRATOR_SKILLS_DIR}}"

# Phase 4: Configure .claude/
bash setup-claude-config.sh "{{PROJECT_ROOT}}" "$TOOLCHAIN" "$LSP_COMMAND"

# Phase 5: Verify
bash verify-environment.sh "{{PROJECT_ROOT}}" "$TOOLCHAIN"
```

---

## Variables Quick Reference

| Variable | Description |
|----------|-------------|
| `{{PROJECT_ROOT}}` | Project root directory |
| `{{PROJECT_NAME}}` | Project name |
| `{{TOOLCHAIN_TYPE}}` | Language: python, nodejs, rust, go, cpp |
| `{{LSP_COMMAND}}` | LSP server command |
| `{{LSP_ARGS}}` | LSP server arguments (JSON array) |
| `{{ORCHESTRATOR_SKILLS_DIR}}` | Path to orchestrator skills |

See [Part 3](./AGENT_ENVIRONMENT_SETUP-part3-verification-reference.md#variables-reference) for complete variable documentation.

---

## Related Documentation

- [PROJECT_CLAUDE_CONFIG.md](./PROJECT_CLAUDE_CONFIG.md) - .claude/ directory template
- [TOOLCHAIN_SKILLS_MATRIX.md](./TOOLCHAIN_SKILLS_MATRIX.md) - Skills per toolchain mapping
- [LSP_SELECTION_GUIDE.md](./LSP_SELECTION_GUIDE.md) - LSP server selection criteria
- [../toolchain/TOOLCHAIN_DETECTION.md](../toolchain/TOOLCHAIN_DETECTION.md) - Language detection
- [../toolchain/TOOLCHAIN_INSTALLATION.md](../toolchain/TOOLCHAIN_INSTALLATION.md) - Toolchain installation
- [../references/lsp-installation-guide.md](../references/lsp-installation-guide.md) - LSP installation
- [../references/lsp-plugin-template.md](../references/lsp-plugin-template.md) - LSP plugin structure
