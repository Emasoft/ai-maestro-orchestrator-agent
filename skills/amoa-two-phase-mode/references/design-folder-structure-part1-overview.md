# Design Folder Structure - Part 1: Overview

Introduction to the standardized folder structure and complete directory specification.

## Contents

- 1. Why a Standardized Structure
  - 1.1 Git tracking of design artifacts
  - 1.2 Per-platform organization
  - 1.3 Single source of truth for implementers
- 2. Folder Structure Specification
  - 2.1 Root location
  - 2.2 Per-platform structure
  - 2.3 Complete directory tree

---

## 1. Why a Standardized Structure

### 1.1 Git tracking of design artifacts

All design documents MUST be tracked by git:
- Ensures version control of requirements
- Enables code review of design changes
- Provides audit trail for decisions
- Allows rollback if design changes cause issues

### 1.2 Per-platform organization

Multi-platform projects (web + iOS + Android, etc.) require:
- Separate design folders per platform
- Shared resources in common folder
- Platform-specific customizations clearly isolated

### 1.3 Single source of truth for implementers

Implementers must know exactly where to find:
- Their customized task handoff
- Technical specifications
- Configuration requirements
- Required templates to follow

---

## 2. Folder Structure Specification

### 2.1 Root location

```
design/
```

The `design/` folder is the root for ALL orchestration design artifacts.

**IMPORTANT**: This folder is **NOT gitignored**. All contents are tracked by git.

### 2.2 Per-platform structure

```
design/
├── designs/                    # All design documents
│   ├── shared/                 # Cross-platform shared resources
│   ├── web/                    # Web platform
│   ├── ios/                    # iOS platform
│   ├── android/                # Android platform
│   └── {platform}/             # Any other platform
├── config/                     # Configuration files for implementers
├── handoffs/                   # Compiled handoff documents (per agent)
└── archive/                    # Superseded design versions
```

### 2.3 Complete directory tree

```
design/
├── designs/
│   ├── shared/
│   │   ├── ARCHITECTURE.md                  # System architecture
│   │   ├── API_SPEC.md                      # API specification
│   │   ├── DATA_MODELS.md                   # Shared data models
│   │   └── SECURITY_REQUIREMENTS.md         # Security specs
│   │
│   ├── web/
│   │   ├── templates/
│   │   │   ├── module-spec-template.md      # Template for module specs
│   │   │   ├── pr-template.md               # PR template
│   │   │   └── test-plan-template.md        # Test plan template
│   │   ├── specs/
│   │   │   ├── auth-core.md                 # Module-specific spec
│   │   │   ├── oauth-google.md              # Module-specific spec
│   │   │   └── ...
│   │   └── rdd/
│   │       ├── auth-core-rdd.md             # Requirements-Driven Design
│   │       └── ...
│   │
│   ├── ios/
│   │   ├── templates/
│   │   ├── specs/
│   │   └── rdd/
│   │
│   └── android/
│       ├── templates/
│       ├── specs/
│       └── rdd/
│
├── config/
│   ├── shared/
│   │   └── env.example                      # Example env vars
│   ├── web/
│   │   ├── tsconfig.json                    # TypeScript config
│   │   └── eslint.config.js                 # Linting config
│   ├── ios/
│   │   └── xcconfig/                        # Xcode configurations
│   └── android/
│       └── gradle.properties                # Gradle config
│
├── handoffs/
│   ├── implementer-1/
│   │   ├── auth-core-handoff.md             # Compiled handoff for agent
│   │   ├── auth-core-checklist.md           # Task checklist
│   │   └── auth-core-config.env             # Config provided to agent
│   └── implementer-2/
│       └── ...
│
└── archive/
    └── 2026-01-08/
        └── auth-core-spec-v1.md             # Superseded spec version
```
