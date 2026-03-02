# Monorepo Workspace Package Template

This template defines how to create and configure individual packages/modules within a monorepo.
Each workspace package should follow this structure for EOA orchestrator compatibility.

---

## Table of Contents

This document is split into multiple parts for better maintainability:

### Part 1: Structure and Manifests
**File:** [MONOREPO_WORKSPACE-part1-structure-manifests.md](./MONOREPO_WORKSPACE-part1-structure-manifests.md)

Contents:
- 1.1 Template Variables
- 1.2 Package Directory Structure
  - 1.2.1 JavaScript/TypeScript Package
  - 1.2.2 Rust Package
- 1.3 Package Manifest Templates
  - 1.3.1 JavaScript/TypeScript (package.json)
  - 1.3.2 Local Dependencies Format (pnpm)
  - 1.3.3 Rust (Cargo.toml)
  - 1.3.4 Local Dependencies Format (Cargo)

### Part 2: Configuration and CI
**File:** [MONOREPO_WORKSPACE-part2-config-ci.md](./MONOREPO_WORKSPACE-part2-config-ci.md)

Contents:
- 2.1 TypeScript Configuration
  - 2.1.1 TypeScript References for local dependencies
- 2.2 Scoped Versioning Strategy
  - 2.2.1 Independent Versioning
  - 2.2.2 Fixed Versioning
  - 2.2.3 Version Synchronization
- 2.3 Package-Level CI Triggers
  - 2.3.1 Change Detection (GitHub Actions)

### Part 3: Workflow and Publishing
**File:** [MONOREPO_WORKSPACE-part3-workflow-publishing.md](./MONOREPO_WORKSPACE-part3-workflow-publishing.md)

Contents:
- 3.1 Local Package Development Workflow
  - 3.1.1 Create New Package
  - 3.1.2 Configure Package
  - 3.1.3 Add to Workspace
  - 3.1.4 Verify Package Discovery
  - 3.1.5 Install Dependencies
  - 3.1.6 Build and Test
- 3.2 Package Interdependency Management
  - 3.2.1 Dependency Graph Example
  - 3.2.2 Build Order Determination
  - 3.2.3 Circular Dependency Prevention
- 3.3 Package Publishing Strategy
  - 3.3.1 Private Monorepo (Internal Only)
  - 3.3.2 Public Monorepo (Selective Publishing)
  - 3.3.3 Version Bumping
- 3.4 Verification Checklist
- 3.5 Error Recovery
- 3.6 Best Practices
- 3.7 Template Metadata

---

## Quick Reference

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PACKAGE_NAME}}` | Package name (scoped) | `@monorepo/core`, `core` |
| `{{PACKAGE_TYPE}}` | Package type | `library`, `application`, `cli-tool` |
| `{{LANGUAGE}}` | Package language | `rust`, `javascript`, `typescript` |
| `{{PARENT_WORKSPACE}}` | Parent workspace path | `packages/`, `apps/` |
| `{{LOCAL_DEPS}}` | Local package dependencies | `["@monorepo/utils"]` |
| `{{EXTERNAL_DEPS}}` | External dependencies | `["tokio", "serde"]` |
| `{{VERSION}}` | Package version | `0.1.0` |
| `{{TASK_ID}}` | Associated task ID | `GH-42` |

---

## Usage Guide

### When to read Part 1 (Structure and Manifests)
- Creating a new package directory structure
- Setting up package.json for JavaScript/TypeScript packages
- Setting up Cargo.toml for Rust packages
- Configuring local and external dependencies

### When to read Part 2 (Configuration and CI)
- Configuring TypeScript with workspace references
- Choosing between independent vs fixed versioning
- Setting up CI triggers for package changes
- Implementing change detection in GitHub Actions

### When to read Part 3 (Workflow and Publishing)
- Step-by-step package creation workflow
- Managing package interdependencies
- Preventing circular dependencies
- Publishing packages to registries
- Version bumping strategies
- Verification and testing checklist

---

## Template Metadata

```yaml
template:
  name: MONOREPO_WORKSPACE
  version: 1.0.0
  eoa_compatible: true
  parent_template: MONOREPO_BASE
  requires:
    - monorepo workspace root
    - package manager
  generates:
    - package directory
    - manifest file
    - configuration files
    - CI triggers
  compatible_with:
    - pnpm-workspaces
    - cargo-workspace
    - nx
    - turborepo
```
