# Central Configuration Architecture


## Contents

- [Document Structure](#document-structure)
- [Quick Navigation](#quick-navigation)
  - [If you need to understand why central configuration matters](#if-you-need-to-understand-why-central-configuration-matters)
  - [If you need to set up the `design/` directory structure](#if-you-need-to-set-up-the-design-directory-structure)
  - [If you need to create toolchain.md](#if-you-need-to-create-toolchainmd)
  - [If you need to create standards.md](#if-you-need-to-create-standardsmd)
  - [If you need to create environment.md](#if-you-need-to-create-environmentmd)
  - [If you need to create decisions.md (ADRs)](#if-you-need-to-create-decisionsmd-adrs)
  - [If you need to create requirements.md](#if-you-need-to-create-requirementsmd)
  - [If you need to create architecture.md](#if-you-need-to-create-architecturemd)
  - [If you need to create interfaces.md](#if-you-need-to-create-interfacesmd)
  - [If you need to reference configs in task messages](#if-you-need-to-reference-configs-in-task-messages)
  - [If you need to update a configuration file](#if-you-need-to-update-a-configuration-file)
  - [If config changes affect active agents](#if-config-changes-affect-active-agents)
  - [If you want to follow best practices for config management](#if-you-want-to-follow-best-practices-for-config-management)
  - [If config management is not working as expected](#if-config-management-is-not-working-as-expected)
- [Quick Reference](#quick-reference)
- [Related Documentation](#related-documentation)

---

This document has been split into multiple parts for easier reading. Each part focuses on a specific aspect of central configuration management.

## Document Structure

| Part | File | Content | Lines |
|------|------|---------|-------|
| 1 | [Overview & Structure](central-configuration-part1-overview-structure.md) | Why config matters, `design/` directory layout | ~80 |
| 2 | [Tooling Templates](central-configuration-part2-tooling-templates.md) | toolchain.md, standards.md, environment.md | ~280 |
| 3 | [Spec Templates](central-configuration-part3-spec-templates.md) | decisions.md, requirements.md, architecture.md, interfaces.md | ~335 |
| 4 | [Workflows & Protocols](central-configuration-part4-workflows-protocols.md) | Reference-based sharing, update protocols, troubleshooting | ~280 |

---

## Quick Navigation

### If you need to understand why central configuration matters
Read: [Part 1 - Overview](central-configuration-part1-overview-structure.md#overview)
- Why Central Configuration Matters
- Critical Principle: Reference, don't embed

### If you need to set up the `design/` directory structure
Read: [Part 1 - Directory Structure](central-configuration-part1-overview-structure.md#directory-structure)
- The `design/` Hierarchy
- Purpose of Each Directory (config/, specs/, memory/)

### If you need to create toolchain.md
Read: [Part 2 - Tooling Templates](central-configuration-part2-tooling-templates.md#toolchainmd-template)
- Python Environment setup
- Code Formatting (ruff)
- Testing Framework (pytest)
- Git Workflow conventions

### If you need to create standards.md
Read: [Part 2 - Tooling Templates](central-configuration-part2-tooling-templates.md#standardsmd-template)
- Naming Conventions
- Documentation Requirements
- FAIL-FAST Error Handling
- Prohibited Patterns

### If you need to create environment.md
Read: [Part 2 - Tooling Templates](central-configuration-part2-tooling-templates.md#environmentmd-template)
- Git Configuration
- AI Maestro Configuration
- CI/CD Environment

### If you need to create decisions.md (ADRs)
Read: [Part 3 - Spec Templates](central-configuration-part3-spec-templates.md#decisionsmd-template)
- ADR Format
- Example ADRs
- Template for New Decisions

### If you need to create requirements.md
Read: [Part 3 - Spec Templates](central-configuration-part3-spec-templates.md#requirementsmd-template)
- Feature specification format
- Acceptance Criteria
- Non-Functional Requirements

### If you need to create architecture.md
Read: [Part 3 - Spec Templates](central-configuration-part3-spec-templates.md#architecturemd-template)
- System Overview
- Component documentation
- Data Flow

### If you need to create interfaces.md
Read: [Part 3 - Spec Templates](central-configuration-part3-spec-templates.md#interfacesmd-template)
- REST API Endpoints
- Function Signatures
- Database Schema
- Message Contracts

### If you need to reference configs in task messages
Read: [Part 4 - Workflows](central-configuration-part4-workflows-protocols.md#reference-based-sharing)
- How Task Instructions Reference Configs (WRONG vs CORRECT)
- Agent Workflow for Reading Configs
- Example Agent Flow

### If you need to update a configuration file
Read: [Part 4 - Workflows](central-configuration-part4-workflows-protocols.md#config-update-protocol)
- When Configuration Changes
- Change Notification Message format
- Agent Response to Config Change
- Handling Config Update Conflicts

### If config changes affect active agents
Read: [Part 4 - Workflows](central-configuration-part4-workflows-protocols.md#integration-with-change-notification)
- Config Changes Trigger Notifications
- Orchestrator workflow for broadcasting updates

### If you want to follow best practices for config management
Read: [Part 4 - Workflows](central-configuration-part4-workflows-protocols.md#best-practices)
- DO: Keep configs small, document changes, reference don't embed
- DON'T: Embed in messages, skip notifications, allow drift

### If config management is not working as expected
Read: [Part 4 - Workflows](central-configuration-part4-workflows-protocols.md#troubleshooting)
- Agent uses outdated configuration
- Config files grow too large
- Multiple agents report same conflict
- Config changes not reflected

---

## Quick Reference

| File | Purpose | Location |
|------|---------|----------|
| `toolchain.md` | Tools, versions, build commands | `design/config/` |
| `standards.md` | Code conventions, formatting | `design/config/` |
| `environment.md` | Environment variables | `design/config/` |
| `decisions.md` | Architecture Decision Records | `design/config/` |
| `requirements.md` | Feature requirements | `design/specs/` |
| `architecture.md` | System design | `design/specs/` |
| `interfaces.md` | API contracts | `design/specs/` |

---

## Related Documentation

- `change-notification-protocol.md` - How to broadcast config updates
- `echo-acknowledgment-protocol.md` - How agents confirm receipt
- `messaging-protocol.md` - Base messaging system
- `task-instruction-format.md` - How to reference configs in tasks
