# Toolchain Integration with EOA Pipeline

**Version**: 1.0.0
**Last Updated**: 2026-01-05
**Purpose**: Define how toolchain templates integrate with EOA pipeline stages and remote agent workflows.

---

## Executive Summary

This document bridges toolchain templates (language-specific development environments) with EOA pipeline stages. It specifies WHEN to apply toolchains, WHICH toolchain to use, and HOW to configure them for remote agents.

**Key Principle**: Every remote agent receives a COMPILED toolchain configuration (no template variables) matching the project's language and target platforms.

---

## Document Structure

This document has been split into 3 parts for better navigation. Each part is under 500 lines and focuses on a specific aspect of toolchain integration.

---

## Part 1: Pipeline & Variables

**File**: [TOOLCHAIN_INTEGRATION-part1-pipeline-variables.md](./TOOLCHAIN_INTEGRATION-part1-pipeline-variables.md)

**Contents**:
- Pipeline Stage to Toolchain Mapping
  - When each pipeline stage uses toolchain actions
  - Required checklists per stage
  - Template types per stage
- Toolchain Lifecycle in EOA
  - Phase 1: Detection (Design/Specification Stage)
  - Phase 2: Compilation (Task Handoff Stage)
  - Phase 3: Setup (Remote Agent)
  - Phase 4: Verification (Code Review & Pre-Merge Stages)
- Variable Substitution Rules
  - Core Variables (Required)
  - Tool Variables (Language-Specific)
  - Installation Variables (Platform-Specific)
  - Verification Variables

**When to read**: Start here to understand the overall pipeline integration and variable system.

---

## Part 2: Language Detection & Platform

**File**: [TOOLCHAIN_INTEGRATION-part2-language-platform.md](./TOOLCHAIN_INTEGRATION-part2-language-platform.md)

**Contents**:
- Language Detection Rules
  - File Pattern to Language Mapping
  - Multi-Language Projects
  - Mixed Language Toolchain Structure
- Toolchain Selection Matrix
  - Project Type to Toolchain mapping
  - Checklist File Locations
- Platform-Specific Toolchain Extensions
  - When to Include Platform Sections
  - Platform Section Structure
  - Example: Rust Cross-Platform Toolchain
- Integration Commands
  - Compile Toolchain for Remote Agent
  - Verify Toolchain Setup
  - Validate Language Mapping Files
  - Generate Language Mapping Template
- Toolchain Compilation Flow (diagram)

**When to read**: Read this when detecting project language, selecting toolchains, or configuring cross-platform builds.

---

## Part 3: Operations & Reference

**File**: [TOOLCHAIN_INTEGRATION-part3-operations-reference.md](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md)

**Contents**:
- Error Handling
  - Compilation Errors
  - Setup Errors (Remote Agent)
- Checklist Integration
  - Checklist Types in Toolchain Workflow
  - Checklist Status Tracking
- Multiplatform Toolchain Strategy
  - Strategy 1: Single Unified Toolchain
  - Strategy 2: Platform-Specific Toolchains
  - Strategy 3: Mixed Language Toolchains
- Toolchain Caching Strategy
  - Cache Key Generation
  - Cache Storage
  - Cache Invalidation
- Testing Toolchain Integration
  - Unit Tests
  - Integration Tests
- Future Enhancements
- Quick Reference
  - Common Commands
  - File Locations
- Version History

**When to read**: Read this for troubleshooting, multiplatform strategies, caching, testing, and quick command reference.

---

## Quick Navigation

| Task | Go To |
|------|-------|
| Understand pipeline stages | [Part 1 - Pipeline Mapping](./TOOLCHAIN_INTEGRATION-part1-pipeline-variables.md#pipeline-stage-to-toolchain-mapping) |
| Learn toolchain lifecycle | [Part 1 - Lifecycle](./TOOLCHAIN_INTEGRATION-part1-pipeline-variables.md#toolchain-lifecycle-in-eoa) |
| Understand variables | [Part 1 - Variables](./TOOLCHAIN_INTEGRATION-part1-pipeline-variables.md#variable-substitution-rules) |
| Detect project language | [Part 2 - Language Detection](./TOOLCHAIN_INTEGRATION-part2-language-platform.md#language-detection-rules) |
| Select toolchain | [Part 2 - Selection Matrix](./TOOLCHAIN_INTEGRATION-part2-language-platform.md#toolchain-selection-matrix) |
| Configure platforms | [Part 2 - Platform Extensions](./TOOLCHAIN_INTEGRATION-part2-language-platform.md#platform-specific-toolchain-extensions) |
| Run integration commands | [Part 2 - Commands](./TOOLCHAIN_INTEGRATION-part2-language-platform.md#integration-commands) |
| Fix errors | [Part 3 - Error Handling](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md#error-handling) |
| Integrate checklists | [Part 3 - Checklists](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md#checklist-integration) |
| Handle multiplatform | [Part 3 - Multiplatform](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md#multiplatform-toolchain-strategy) |
| Configure caching | [Part 3 - Caching](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md#toolchain-caching-strategy) |
| Run tests | [Part 3 - Testing](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md#testing-toolchain-integration) |
| Quick commands | [Part 3 - Quick Reference](./TOOLCHAIN_INTEGRATION-part3-operations-reference.md#quick-reference) |

---

## Key Concepts Summary

- **Toolchains bridge orchestrator and remote agents**: Language-agnostic EOA workflow connects to language-specific execution environments via compiled toolchain configurations
- **Four-phase lifecycle**: Detection (analyze project) → Compilation (fill template variables) → Setup (remote agent executes) → Verification (review/pre-merge validation)
- **No template variables reach remote agents**: Orchestrator MUST compile all `{{VARIABLE}}` placeholders before handoff; remote agents receive ready-to-execute configurations
- **Language detection drives toolchain selection**: File patterns (e.g., `Cargo.toml` → Rust, `pyproject.toml` → Python) automatically select the appropriate toolchain template
- **Platform-specific extensions optional**: Base toolchains work cross-platform; add platform sections only when OS-specific tools/paths are required

### Pipeline Stage to Toolchain Actions

| Stage | Action |
|-------|--------|
| Design/Specification | Detect language requirements |
| Task Handoff | Compile and send toolchain |
| Code Implementation | Use compiled toolchain |
| Code Review | Run toolchain verification |
| Pre-Merge | Full toolchain validation |
| Testing | Run test suite via toolchain |
| Release | Cross-platform toolchain tests |

### Toolchain Lifecycle

1. **Detection** - Orchestrator analyzes project for language requirements
2. **Compilation** - Orchestrator compiles template with language-specific values
3. **Setup** - Remote agent executes toolchain setup script
4. **Verification** - Run verification at review and pre-merge stages

### Supported Languages

- Rust (1.75+)
- Python (3.12+)
- JavaScript (Node 20+)
- TypeScript (Node 20+)
- Go (1.21+)
- Elixir
- Ruby

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial release |
| 1.0.1 | 2026-01-10 | Split into 3 parts for better navigation |

---

**REMEMBER**: Toolchains are the bridge between EOA orchestrator's language-agnostic workflow and remote agents' language-specific execution. A well-compiled toolchain eliminates ambiguity and ensures consistent development environments across all agents.
