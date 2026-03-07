---
name: amoa-task-distribution
description: Task distribution based on skills and availability. Use when assigning work to agents, balancing load, or resolving dependencies. Trigger with assignment requests.
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

This skill defines how the Orchestrator (AMOA) distributes tasks to agents. Distribution is based on **order**, **priority**, and **agent state**. Tasks are selected from the ready queue, sorted by priority, filtered by dependencies, matched to agent capabilities, and assigned via labeled issues and AI Maestro messages.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **amoa-label-taxonomy** for label usage and cardinality rules
3. Read **amoa-messaging-templates** for message formats
4. Access to GitHub CLI (`gh`) and AI Maestro API

---

## 1. Task Distribution Order

| Step | Action | Condition |
|------|--------|-----------|
| 1 | Identify ready tasks | Tasks with `status:ready` label |
| 2 | Sort by priority | `priority:critical` > `high` > `normal` > `low` |
| 3 | Check dependencies | Task's blockedBy list is empty |
| 4 | Select agent | Match task requirements to available agents |
| 5 | Assign task | Add `assign:<agent>` label, send AI Maestro message |

## 2. Agent Selection Criteria

Evaluate availability (active > hibernated/offline), skill match (`toolchain:*`, `component:*` labels vs agent capabilities), and capacity (0-2 tasks OK, 3+ at capacity). See: `references/op-select-agent.md`

## 3. Assignment Protocol

Update labels (`assign:<agent>`, `status:in-progress`), send assignment message via `agent-messaging` skill, wait for ACK. See: `references/op-assign-task.md`

## 4. Dependency Management

Three types: Hard (block until resolved), Soft (assign with note), None (parallel). Circular dependencies must be reported to user. See: `references/dependency-management.md`

## 5. Load Balancing

Prefer lowest-load agent. When equal, prefer agent with recent similar task experience. Specialization rules apply for code review and bug fixes. See: `references/load-balancing.md`

## 6. Reassignment

When reassigning (agent unresponsive/blocked): remove old `assign:*`, add new, send context to new agent, notify original. See: `references/op-reassign-task.md`

## 7. Blocked Task Handling

When an agent reports a task is blocked: acknowledge, record previous status, move to Blocked column, create blocker issue, escalate to AMAMA immediately. Verify blocker is real before escalating. See: `references/blocked-task-handling.md`

## Instructions

1. Query tasks with `status:ready` label and sort by priority (critical > high > normal > low).
2. Check each task's dependency list; only tasks with empty blockedBy are assignable.
3. Select the best agent based on availability, skill match, and current load.
4. Assign the task: add `assign:<agent>` and `status:in-progress` labels, send AI Maestro message.
5. Wait for ACK; if no ACK within timeout, reassign per `references/op-reassign-task.md`.

Full checklist: `references/distribution-workflow-checklist.md`

---

## Output

| Output Type | Format |
|-------------|--------|
| Assignment confirmation | GitHub label + AI Maestro ACK |
| Task queue report | Markdown table of ready tasks by priority |
| Agent availability report | JSON with agent load and state |
| Dependency graph | Text showing blocks/blockedBy |
| Delegation log entry | Timestamped assignment record |

## Error Handling

Common errors: no available agents, circular dependencies, agent non-ACK, skill mismatch, stuck dependencies, label conflicts. See: `references/error-handling.md`

## Examples

Query/sort ready tasks, check agent availability, assign with full protocol, handle circular dependencies. See: `references/examples.md`

---

## Resources

- `references/` -- all operational procedure files (op-*.md, dependency, load-balancing, examples, error-handling, checklist)
- Related skills: **amoa-label-taxonomy**, **amoa-messaging-templates**, **amoa-progress-monitoring**
- **AGENT_OPERATIONS.md** -- orchestrator workflow and agent lifecycle

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:
1. Verbose output goes to a timestamped report file in `docs_dev/reports/`
2. Stdout emits only 2-3 lines: status + filepath
3. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
