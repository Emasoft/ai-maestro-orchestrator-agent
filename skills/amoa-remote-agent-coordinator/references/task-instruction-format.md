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

Canonical copy: maintained in [task-instruction-format-part1-core-template.md](task-instruction-format-part1-core-template.md) §Overview — read that file for the CRITICAL PRINCIPLE (remote agents know NO protocols unless the orchestrator explicitly teaches them in each message).

---

## Agent Response Templates

Canonical copy: maintained in [task-instruction-format-part1-core-template.md](task-instruction-format-part1-core-template.md) §Agent Response Templates — read that file for the table of templates to link in EVERY task delegation.

---

## Mandatory ACK Block

Canonical copy: maintained in [task-instruction-format-part1-core-template.md](task-instruction-format-part1-core-template.md) §Mandatory ACK Block — read that file for the acknowledgment block that EVERY task delegation MUST start with.

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
