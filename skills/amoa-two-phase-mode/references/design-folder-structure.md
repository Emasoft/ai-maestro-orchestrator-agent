# Design Folder Structure

Standardized folder structure for all design documents, customized templates, handoffs, and RDD files per platform.

**This document is an index.** Detailed content is split into parts for efficient progressive disclosure.

---

## Contents

### Part 1: Overview
[design-folder-structure-part1-overview.md](design-folder-structure-part1-overview.md)

- 1. Why a Standardized Structure
  - 1.1 Git tracking of design artifacts
  - 1.2 Per-platform organization
  - 1.3 Single source of truth for implementers
- 2. Folder Structure Specification
  - 2.1 Root location
  - 2.2 Per-platform structure
  - 2.3 Complete directory tree

### Part 2: File Types and Locations
[design-folder-structure-part2-file-types.md](design-folder-structure-part2-file-types.md)

- 3. File Types and Locations
  - 3.1 Templates (compilable documents)
  - 3.2 Handoffs (compiled communication files)
  - 3.3 RDD files (Requirements-Driven Design)
  - 3.4 Config files (implementer configuration)
  - 3.5 Specs (technical specifications)

### Part 3: Usage Workflow and Git Tracking
[design-folder-structure-part3-workflow.md](design-folder-structure-part3-workflow.md)

- 4. Usage Workflow
  - 4.1 Creating design files during Plan Phase
  - 4.2 Compiling templates for implementers
  - 4.3 Storing implementer responses
- 5. Git Tracking Rules
  - 5.1 What to track
  - 5.2 What to gitignore

### Part 4: Multi-Platform and Scripts
[design-folder-structure-part4-multiplatform.md](design-folder-structure-part4-multiplatform.md)

- 6. Multi-Platform Projects
  - 6.1 Shared resources
  - 6.2 Platform-specific customization
- 7. State File Integration
- 8. Script Support
  - 8.1 eoa_init_design_folders.py   - 8.2 eoa_compile_handoff.py - 9. Checklists
  - 9.1 Design Folder Setup Checklist
  - 9.2 Per-Module Design Checklist

---

## Quick Reference

### Root Location

```
design/
```

The `design/` folder is the root for ALL orchestration design artifacts. This folder is **NOT gitignored** - all contents are tracked by git.

### Directory Structure Overview

```
design/
├── designs/                    # All design documents
│   ├── shared/                 # Cross-platform shared resources
│   ├── web/                    # Web platform
│   ├── ios/                    # iOS platform
│   └── android/                # Android platform
├── config/                     # Configuration files for implementers
├── handoffs/                   # Compiled handoff documents (per agent)
└── archive/                    # Superseded design versions
```

### File Types Summary

| Type | Location | Purpose |
|------|----------|---------|
| Templates | `design/requirements/{platform}/templates/` | Compilable documents with placeholders |
| Specs | `design/requirements/{platform}/specs/` | Technical specifications |
| RDD | `design/requirements/{platform}/rdd/` | Requirements-Driven Design docs |
| Handoffs | `design/handoffs/{agent-id}/` | Compiled communication files |
| Config | `design/config/{platform}/` | Implementer configuration |

### Key Scripts

| Script | Purpose |
|--------|---------|
| `eoa_init_design_folders.py <!-- TODO: Script not implemented -->` | Create standardized folder structure |
| `eoa_compile_handoff.py <!-- TODO: Script not implemented -->` | Compile template to handoff |

---

## When to Read Each Part

| If you need to... | Read |
|-------------------|------|
| Understand why this structure exists | Part 1, Section 1 |
| Set up the folder structure | Part 1, Section 2 |
| Create or modify templates | Part 2, Section 3.1 |
| Compile handoffs for agents | Part 2, Section 3.2 |
| Create RDD documents | Part 2, Section 3.3 |
| Understand the workflow | Part 3, Section 4 |
| Configure git tracking | Part 3, Section 5 |
| Work with multi-platform projects | Part 4, Section 6 |
| Use automation scripts | Part 4, Section 8 |
| Follow setup checklists | Part 4, Section 9 |
