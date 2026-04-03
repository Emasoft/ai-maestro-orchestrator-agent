---
name: amoa-module-management
description: "Use when managing modules during Orchestration Phase. Trigger with module add, modify, or reassign requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
license: Apache-2.0
compatibility: Python 3.8+, PyYAML, gh CLI, AI Maestro.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: false
context: fork
agent: amoa-main
---

# Module Management Commands Skill

## Overview

Manages modules during Orchestration Phase. Each module maps 1:1 to a GitHub Issue. This skill has been split into focused sub-skills:

- **amoa-module-lifecycle** -- Core CRUD: add, modify, remove, prioritize, reassign modules
- **amoa-module-sync** -- GitHub Issue sync, troubleshooting, usage examples

## Prerequisites

Orchestration Phase active, gh CLI authenticated, AI Maestro running.

## Output

Module ID, Issue number, state update, and agent notification status.

## Instructions

1. For module CRUD operations, see skill `amoa-module-lifecycle`
2. For GitHub Issue sync and troubleshooting, see skill `amoa-module-sync`

Copy this checklist and track your progress:

- [ ] Identify action and verify prerequisites
- [ ] Execute command via the appropriate sub-skill
- [ ] Confirm Issue sync and notify agents

## Examples

**Input:** `/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical`
**Output:** Module `two-factor-auth` created, Issue #43 opened, pending

## Error Handling

Module not found: run `/orchestration-status`. Cannot remove: status not pending.

## Resources

- See skill `amoa-module-lifecycle` for command details and module CRUD
- See skill `amoa-module-sync` for GitHub sync and troubleshooting
