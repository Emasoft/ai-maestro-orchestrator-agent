# Central Configuration - Part 1: Overview and Directory Structure


## Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
  - [Why Central Configuration Matters](#why-central-configuration-matters)
- [Directory Structure](#directory-structure)
  - [The `design/` Hierarchy](#the-design-hierarchy)
  - [Purpose of Each Directory](#purpose-of-each-directory)
- [Related Parts](#related-parts)

---

## Table of Contents

1. [If you need to understand why central configuration matters](#overview)
   - [Why Central Configuration Matters](#why-central-configuration-matters)
2. [If you need to set up the `design/` directory structure](#directory-structure)
   - [The `design/` Hierarchy](#the-design-hierarchy)
   - [Purpose of Each Directory](#purpose-of-each-directory)

---

## Overview

### Why Central Configuration Matters

In multi-agent orchestrated workflows, configuration drift is the primary cause of coordination failures:

- **Consistency**: Multiple agents need identical understanding of toolchain, standards, and requirements
- **Synchronization**: When specs change, all agents must receive updates simultaneously
- **Traceability**: Every decision must be documented with rationale and timestamp
- **Efficiency**: Referencing centralized configs reduces message payload size by 10-100x
- **Conflict Prevention**: Single source of truth eliminates conflicting instructions
- **Audit Trail**: Changes to configs are tracked, enabling rollback and review

**Critical Principle**: Configuration is NEVER embedded in task messages. Messages contain REFERENCES to config files that agents read from the shared `design/` directory.

---

## Directory Structure

### The `design/` Hierarchy

```
design/
├── config/                     # Canonical project configuration
│   ├── toolchain.md           # Tools, versions, commands, build system
│   ├── standards.md           # Code standards, formatting, naming conventions
│   ├── environment.md         # Environment variables specification
│   └── decisions.md           # Architecture Decision Records (ADRs)
├── specs/                      # Functional specifications
│   ├── requirements.md        # Business/functional requirements
│   ├── architecture.md        # System architecture and design
│   └── interfaces.md          # API contracts, function signatures
└── memory/                     # Orchestrator working memory
    ├── activeContext.md       # Current working state and focus
    ├── patterns.md            # Learned patterns from this project
    ├── progress.md            # Task tracking and completion status
    └── config-snapshot.md     # Snapshot of config state at session start
```

### Purpose of Each Directory

**`config/`** - The authoritative source for HOW things are done:
- Tools and their versions
- Code formatting rules
- Testing frameworks
- Deployment procedures
- Development workflow

**`specs/`** - The authoritative source for WHAT is being built:
- Features and requirements
- System architecture
- Module interfaces
- Data schemas
- API contracts

**`memory/`** - Orchestrator-specific working state (NOT shared with agents):
- Current task focus
- Session context
- Progress tracking
- Detected patterns

---

## Related Parts

- **Part 2**: [Tooling Templates](central-configuration-part2-tooling-templates.md) - toolchain.md, standards.md, environment.md templates
- **Part 3**: [Spec Templates](central-configuration-part3-spec-templates.md) - decisions.md, requirements.md, architecture.md, interfaces.md templates
- **Part 4**: [Workflows and Protocols](central-configuration-part4-workflows-protocols.md) - Reference-based sharing, update protocols, troubleshooting
