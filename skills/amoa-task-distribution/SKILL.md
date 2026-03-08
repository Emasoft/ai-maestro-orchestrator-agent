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

Defines how AMOA distributes tasks to agents based on **priority**, **dependencies**, and **agent state**. Tasks from the ready queue are sorted, filtered, matched to agents, and assigned via labeled issues and AI Maestro messages.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **amoa-label-taxonomy** for label usage and cardinality rules
3. Read **amoa-messaging-templates** for message formats
4. Access to GitHub CLI (`gh`) and AI Maestro API

## 1. Task Distribution Order

| Step | Action | Condition |
|------|--------|-----------|
| 1 | Identify ready tasks | Tasks with `status:ready` label |
| 2 | Sort by priority | `priority:critical` > `high` > `normal` > `low` |
| 3 | Check dependencies | Task's blockedBy list is empty |
| 4 | Select agent | Match task requirements to available agents |
| 5 | Assign task | Add `assign:<agent>` label, send AI Maestro message |

## 2. Agent Selection Criteria

Evaluate availability, skill match (`toolchain:*`, `component:*` labels), and capacity (0-2 OK, 3+ at capacity). See: `references/op-select-agent.md`
<!-- TOC: Purpose | Selection Criteria | Procedure | Specialization Preferences | Error Handling -->

## 3. Assignment Protocol

Update labels (`assign:<agent>`, `status:in-progress`), send assignment message via `agent-messaging` skill, wait for ACK. See: `references/op-assign-task.md`
<!-- TOC: Purpose | Procedure | Commands | Message Format | Post-Assignment | Error Handling -->

## 4. Dependency Management

Hard (block until resolved), Soft (assign with note), None (parallel). Circular deps → report to user. See: `references/dependency-management.md`
<!-- TOC: Dependency Types | Dependency Resolution | Circular Dependency Detection -->

## 5. Load Balancing

Prefer lowest-load agent; if equal, prefer recent similar experience. See: `references/load-balancing.md`
<!-- TOC: Even Distribution | Specialization -->

## 6. Reassignment

When reassigning (agent unresponsive/blocked): remove old `assign:*`, add new, send context to new agent, notify original. See: `references/op-reassign-task.md`
<!-- TOC: When to Reassign | Procedure | Commands | Partial Progress Gathering | Error Handling -->

## 7. Blocked Task Handling

When blocked: acknowledge, record status, move to Blocked column, create blocker issue, escalate to AMAMA. Verify blocker is real first. See: `references/blocked-task-handling.md`
<!-- TOC: Blocker Response Steps | Escalation Message | Verification | Move to Blocked | Restore from Blocked -->

## Instructions

1. Query tasks with `status:ready` label and sort by priority (critical > high > normal > low)
2. Check each task's dependency list; only tasks with empty blockedBy are assignable
3. Select the best agent based on availability, skill match, and current load
4. Assign the task: add `assign:<agent>` and `status:in-progress` labels, send AI Maestro message
5. Wait for ACK; if no ACK within timeout, reassign per reassignment protocol

Copy this checklist and track your progress:

- [ ] Query tasks with `status:ready` label and sort by priority (critical > high > normal > low)
- [ ] Check each task's dependency list; only tasks with empty blockedBy are assignable
- [ ] Select the best agent based on availability, skill match, and current load
- [ ] Assign the task: add `assign:<agent>` and `status:in-progress` labels, send AI Maestro message
- [ ] Wait for ACK; if no ACK within timeout, reassign per `references/op-reassign-task.md`
  <!-- TOC: Reassign | Procedure | Commands | Partial Progress | Errors -->

Full checklist: `references/distribution-workflow-checklist.md`
<!-- TOC: Step-by-Step Instructions | Distribution Checklist -->

## Output

Assignment confirmation (label + ACK), task queue report, agent availability, dependency graph, delegation log.

## Error Handling

No available agents, circular deps, non-ACK, skill mismatch, stuck deps, label conflicts. See: `references/error-handling.md`
<!-- TOC: Error Table -->

## Examples

**Input:** 3 ready tasks (priorities: critical, normal, low), 2 available agents
**Output:** Critical task assigned to best-match agent; labels updated; AI Maestro ACK received

Query/sort ready tasks, check agent availability, assign with full protocol, handle circular dependencies. See: `references/examples.md`
<!-- TOC: Query/Sort Tasks | Check Availability | Assign Task | Handle Circular Deps -->

## Resources

- `references/` -- procedures, examples, error handling, checklist
- Related skills: **amoa-label-taxonomy**, **amoa-messaging-templates**, **amoa-progress-monitoring**
- **AGENT_OPERATIONS.md** -- orchestrator workflow

