---
name: amoa-two-phase-mode
description: "Use when running Plan-then-Execute workflows with formal approval and GitHub Issue-backed modules. Trigger with two-phase or plan phase requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed, GitHub CLI (gh), remote agents.
metadata:
  author: Emasoft
  version: 2.6.0
context: fork
user-invocable: false
agent: amoa-main
---

# Two-Phase Mode Skill

## Overview

Two-Phase Mode separates orchestration into Plan Phase (requirements) and Orchestration Phase (implementation). The orchestrator enforces completion of current tasks while allowing dynamic modifications.

## Prerequisites

- AI Maestro messaging system running
- GitHub CLI (gh) authenticated
- Remote agents registered by user

## Core Principles

1. **Dynamic Flexibility with Completion Enforcement**: User can add/change/remove requirements; stop hook enforces all CURRENT tasks complete before exit.
2. **Claude Tasks Scheduling (CRITICAL)**: All instructions must be immediately scheduled as Claude Tasks for persistence across compacting. See: [references/native-task-persistence.md](references/native-task-persistence.md)

## Quick Start

1. `/start-planning` - Create state file, document requirements
2. `/approve-plan` - Transition to Orchestration Phase, create GitHub Issues
3. `/start-orchestration` - Initialize orchestration state
4. `/register-agent` + `/assign-module` - Assign work to agents
5. Execute Instruction Verification Protocol before authorizing
6. `/check-agents` every 10-15 min to poll progress
7. Complete 4 verification loops per module

For full step-by-step instructions, output types, agent types, stop hook details, and examples, see: [references/skill-overview-details.md](references/skill-overview-details.md)

## Reference Files

| Reference | Description |
|-----------|-------------|
| [plan-phase-workflow.md](references/plan-phase-workflow.md) | Plan Phase workflow |
| [orchestration-phase-workflow.md](references/orchestration-phase-workflow.md) | Orchestration Phase workflow |
| [instruction-verification-protocol.md](references/instruction-verification-protocol.md) | **MANDATORY** 8-step pre-implementation protocol |
| [proactive-progress-polling.md](references/proactive-progress-polling.md) | **MANDATORY** 6-question polling |
| [instruction-update-verification-protocol.md](references/instruction-update-verification-protocol.md) | **MANDATORY** mid-implementation updates |
| [native-task-persistence.md](references/native-task-persistence.md) | **CRITICAL** Claude Tasks persistence |
| [issue-handling-workflow.md](references/issue-handling-workflow.md) | Issue handling workflows |
| [state-file-formats.md](references/state-file-formats.md) | State file YAML schemas |
| [design-folder-structure.md](references/design-folder-structure.md) | Design folder structure |
| [command-reference.md](references/command-reference.md) | All 16 commands |
| [script-reference.md](references/script-reference.md) | Python scripts |
| [workflow-diagram.md](references/workflow-diagram.md) | Workflow flowcharts |
| [quick-reference-checklist.md](references/quick-reference-checklist.md) | Phase checklists |
| [troubleshooting.md](references/troubleshooting.md) | Troubleshooting |
| [skill-overview-details.md](references/skill-overview-details.md) | Full details and examples |

## Instructions

1. Run `/start-planning` to create the state file and document requirements.
2. Run `/approve-plan` to transition to Orchestration Phase and create GitHub Issues.
3. Run `/start-orchestration` then `/register-agent` and `/assign-module` to assign work.
4. Execute the Instruction Verification Protocol before authorizing any agent to begin.
5. Poll agents with `/check-agents` every 10-15 minutes and complete 4 verification loops per module.

Details: [skill-overview-details.md](references/skill-overview-details.md) and [command-reference.md](references/command-reference.md).

## Examples

See [skill-overview-details.md](references/skill-overview-details.md) for usage examples.

## Output

See [state-file-formats.md](references/state-file-formats.md) and [skill-overview-details.md](references/skill-overview-details.md).

## Error Handling

See [troubleshooting.md](references/troubleshooting.md) and [issue-handling-workflow.md](references/issue-handling-workflow.md).

## Resources

See Reference Files table above and [script-reference.md](references/script-reference.md).

## Script Output Rules

All scripts MUST follow the token-efficient output protocol:
1. Verbose output goes to a timestamped report file in `docs_dev/reports/`
2. Stdout emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (hook requirement)
