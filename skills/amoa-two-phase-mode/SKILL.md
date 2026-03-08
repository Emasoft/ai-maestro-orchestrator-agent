---
name: amoa-two-phase-mode
description: "Use when running Plan-then-Execute workflows. Trigger with plan-execute or two-phase requests."
license: Apache-2.0
compatibility: AI Maestro, GitHub CLI (gh), remote agents.
metadata:
  author: Emasoft
  version: 2.6.0
context: fork
user-invocable: false
agent: amoa-main
---

# Two-Phase Mode Skill

## Overview

Separates orchestration into Plan Phase (requirements) and Orchestration Phase (implementation). Stop hook enforces completion; dynamic modifications allowed.

## Prerequisites

- AI Maestro messaging running
- GitHub CLI (gh) authenticated
- Remote agents registered

## Core Principles

1. **Completion Enforcement**: Dynamic changes allowed; stop hook enforces all tasks complete before exit.
2. **Claude Tasks Persistence**: Schedule instructions as Claude Tasks immediately. See [native-task-persistence.md](references/native-task-persistence.md).
<!-- TOC: Task Lifecycle - Creating, tracking, and completing tasks | Best Practices - Effective task management patterns -->

## Instructions

1. Start Plan Phase with `/start-planning` to create state file and document requirements
2. Approve plan with `/approve-plan` to transition to Orchestration Phase and create GitHub Issues
3. Start orchestration, register agents, and assign modules
4. Execute Verification Protocol before authorizing agents
5. Monitor with `/check-agents` every 10-15 min; enforce 4 verification loops per module

Copy this checklist and track your progress:

- [ ] `/start-planning` — create state file, document requirements
- [ ] `/approve-plan` — transition to Orchestration Phase, create GitHub Issues
- [ ] `/start-orchestration`, `/register-agent`, `/assign-module` — assign work
- [ ] Execute Verification Protocol before authorizing agents
- [ ] `/check-agents` every 10-15 min; 4 verification loops per module

Details: [command-reference.md](references/command-reference.md) | [skill-overview-details.md](references/skill-overview-details.md)
<!-- TOC: Plan Phase Commands | Orchestration Phase Commands | Output Types | Instructions | Agent Types | Stop Hook | Examples -->

## Examples

**Input:** `/start-planning` with GitHub repo configured
**Output:** Creates `design/plan-state.yaml` with requirements template

**Input:** `/approve-plan` after requirements documented
**Output:** Transitions to Orchestration Phase, creates GitHub Issues per module

More: [skill-overview-details.md](references/skill-overview-details.md)
<!-- TOC: Output Types | Instructions | Agent Types | Stop Hook | Examples -->


## Output

State files (YAML), GitHub Issues per module, phase transition confirmations. See: [state-file-formats.md](references/state-file-formats.md)
<!-- TOC: Plan Phase State File | Orchestration Phase State File | Agent Assignment Structure | Module Status Structure | Parsing State Files -->

## Error Handling

Plan/orchestration issues, state file corruption, communication failures. See: [troubleshooting.md](references/troubleshooting.md)
<!-- TOC: Plan Phase Issues | Orchestration Phase Issues | State File Issues | Communication Issues | Stop Hook Issues -->

## Resources

- [command-reference.md](references/command-reference.md) — All 16 commands
  <!-- TOC: Plan Phase Commands (6) | Orchestration Phase Commands (10) -->
- [plan-phase-workflow.md](references/plan-phase-workflow.md) — Plan Phase
  <!-- TOC: Entering Plan Phase | Planning Activities | Modifying the Plan | Plan Phase Completion | Stop Hook Behavior -->
- [orchestration-phase-workflow.md](references/orchestration-phase-workflow.md) — Orchestration Phase
  <!-- TOC: Entering Orchestration Phase | Agent Registration | Module Assignment | Monitoring Progress | Modifying During Orchestration | Completion and Exit -->
- [instruction-verification-protocol.md](references/instruction-verification-protocol.md) — 8-step verification
  <!-- TOC: Why This Protocol Exists | The 8-Step Protocol Flow | Message Templates | Tracking Verification Status | Failure Conditions -->
- [state-file-formats.md](references/state-file-formats.md) — State YAML schemas
  <!-- TOC: Plan Phase State File | Orchestration Phase State File | Agent Assignment Structure | Module Status Structure -->
- [troubleshooting.md](references/troubleshooting.md) — Troubleshooting
  <!-- TOC: Plan Phase Issues | Orchestration Phase Issues | State File Issues | Communication Issues | Stop Hook Issues -->
