# Task Instruction Format

## Contents

This document is the **index** for task instruction format documentation. Each section below links to detailed reference files.

### Quick Reference

- **[Overview](#overview)** - Critical principle: teach agents in every message
- **[Agent Response Templates](#agent-response-templates)** - Templates to link in task delegations
- **[Mandatory ACK Block](#mandatory-ack-block)** - Include this in EVERY task delegation

### Detailed References

| Reference File | Contents |
|----------------|----------|
| [task-instruction-format-part1-template.md](task-instruction-format-part1-template.md) | Complete task instruction template with all sections |
| [task-instruction-format-part2-config-monitoring.md](task-instruction-format-part2-config-monitoring.md) | Project configuration patterns and progress monitoring |
| [task-instruction-format-part3-errors-integration.md](task-instruction-format-part3-errors-integration.md) | Error handling, blockers, protocol integration, examples |

---

## Overview

This document provides the complete template for task instructions sent to remote developer agents. Following this format ensures tasks are executed EXACTLY as planned with NO deviations.

**CRITICAL PRINCIPLE**: Remote agents DO NOT have access to the emasoft-orchestrator-agent skill. They do not know any protocols, formats, or expectations unless the orchestrator EXPLICITLY TEACHES them in each message. Every task delegation MUST include:
1. Complete instructions on HOW to respond
2. Template references the agent can download
3. Exact format for ACK, progress updates, and completion reports

---

## Agent Response Templates

Link these templates in EVERY task delegation so agents know exactly how to respond:

| Template | Path | When Agent Uses It |
|----------|------|-------------------|
| ACK Response | `templates/ack-response.md` | Immediately after receiving task |
| Progress Update | `templates/status-update.md` | At each checkpoint during work |
| Completion Report | `templates/completion-report.md` | When task is done or failed |
| Task Checklist | `templates/task-checklist.md` | Throughout task execution |
| GitHub Projects | `templates/github-projects-guide.md` | When updating issue status |

---

## Mandatory ACK Block

**EVERY task delegation MUST start with this block:**

```
================================================================================
ACKNOWLEDGMENT REQUIRED (MANDATORY)
================================================================================

Before starting work, you MUST reply with an acknowledgment in this exact format:

[ACK] {task_id} - {status}
Understanding: {1-line summary of what you will do}

Status options:
- RECEIVED - Task received, will begin work immediately
- CLARIFICATION_NEEDED - Need more info (list your questions)
- REJECTED - Cannot accept task (explain why)
- QUEUED - Have prior tasks, will start after them

Example:
[ACK] GH-42-password-reset - RECEIVED
Understanding: Will implement password reset flow with email tokens

DO NOT begin work until you have sent this acknowledgment.
================================================================================
```

---

## Part File Contents

### Part 1: Task Template ([task-instruction-format-part1-template.md](task-instruction-format-part1-template.md))

Complete task instruction template including:
- 1.1 Full template structure with all required sections
- 1.2 Metadata section format
- 1.3 Context section (problem statement, background, related issues)
- 1.4 Scope section (DO, DO NOT, boundaries)
- 1.5 Interface contract (inputs, outputs, function signatures, API contracts)
- 1.6 Project configuration reference block
- 1.7 Files to modify table and file-specific instructions
- 1.8 Test requirements (TDD sequence, required tests, coverage)
- 1.9 Completion criteria checklist
- 1.10 Constraints (MUST follow, MUST NOT do)
- 1.11 Escalation rules and how to escalate
- 1.12 Agent response instructions (mandatory section)
- 1.13 Report format for completion

### Part 2: Config and Monitoring ([task-instruction-format-part2-config-monitoring.md](task-instruction-format-part2-config-monitoring.md))

Project configuration and progress monitoring:
- 2.1 Configuration reference pattern (reference-based approach)
- 2.2 Required reading before starting task
- 2.3 How to access config files
- 2.4 Config snapshot format
- 2.5 Getting secrets securely
- 2.6 Config update notifications
- 2.7 Progress update requirements (frequency by priority)
- 2.8 Timeout protocol and flow
- 2.9 Timeout extension request format

### Part 3: Errors and Integration ([task-instruction-format-part3-errors-integration.md](task-instruction-format-part3-errors-integration.md))

Error handling and protocol integration:
- 3.1 Error states table (blocked, failed, tests-failing, etc.)
- 3.2 Blocked report format with JSON example
- 3.3 Integration with other protocols
- 3.4 Protocol flow diagram
- 3.5 Example of completed task instruction

---

## Navigation

- **Parent**: [SKILL.md](../SKILL.md)
- **Related**: [messaging-protocol.md](messaging-protocol.md), [echo-acknowledgment-protocol.md](echo-acknowledgment-protocol.md)
