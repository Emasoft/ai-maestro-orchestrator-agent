---
name: amoa-task-distribution
description: "Use when distributing tasks. Trigger with task assignment requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Task Distribution Skill

## Overview

Distributes tasks to agents by priority, dependencies, and agent state.

## Prerequisites

Requires `gh` CLI (with `--repo` on ALL commands), AI Maestro API, and familiarity with **amoa-label-taxonomy** and **amoa-messaging-templates**.

## Instructions

**Multi-Repo Rule:** Every gh command MUST include `--repo "$OWNER/$REPO"`. Identify the target repo BEFORE any operation. All subagent prompts MUST include the target repo path (`$AGENT_DIR/repos/<repo-name>`) and report output path (`$AGENT_DIR/reports/`).

1. Query `status:ready` tasks (with `--repo`), sort by priority (critical > high > normal > low), skip tasks with unresolved blockedBy deps
2. Select agent by availability, skill match, and load — see [op-select-agent.md](references/op-select-agent.md)
<!-- TOC: Purpose | Selection Criteria | Procedure | Specialization Preferences | Error Handling -->
3. Assign: add `assign:<agent>` + `status:in-progress` labels, send message via `agent-messaging` — see [op-assign-task.md](references/op-assign-task.md)
<!-- TOC: Purpose | Procedure | Commands | Message Format | Post-Assignment | Error Handling -->
4. Wait for ACK; if timeout, reassign per [op-reassign-task.md](references/op-reassign-task.md)
<!-- TOC: When to Reassign | Procedure | Commands | Partial Progress Gathering | Error Handling -->

Dependency types: Hard (block), Soft (assign with note), None (parallel). Circular deps → escalate. See [dependency-management.md](references/dependency-management.md)
<!-- TOC: Dependency Types | Dependency Resolution | Circular Dependency Detection -->

Load balancing: prefer lowest-load agent. See [load-balancing.md](references/load-balancing.md)
<!-- TOC: Even Distribution | Specialization -->

Blocked tasks: acknowledge, record, move to Blocked column, escalate. See [blocked-task-handling.md](references/blocked-task-handling.md)
<!-- TOC: Blocker Response Steps | Verification Before Escalation -->

Copy this checklist and track your progress:

- [ ] Query and sort ready tasks; assign best-match agent
- [ ] Update labels and send AI Maestro message; wait for ACK
- [ ] If no ACK or blocked, reassign per [op-reassign-task.md](references/op-reassign-task.md)
  <!-- TOC: Reassign | Procedure | Commands | Partial Progress | Errors -->

Full checklist: [distribution-workflow-checklist.md](references/distribution-workflow-checklist.md)
<!-- TOC: Step-by-Step Instructions | Distribution Checklist -->

## Output

Assignment confirmation (label + ACK) and delegation log.

## Examples

**Input:** 3 ready tasks, 2 agents — **Output:** Critical task assigned, labels updated, ACK received. See [examples.md](references/examples.md)
<!-- TOC: Query and Sort Ready Tasks | Check Agent Availability -->

## Error Handling

See [error-handling.md](references/error-handling.md)
<!-- TOC: Error Table -->

## Resources

- [references/](references/) — procedures, examples, error handling, checklist

