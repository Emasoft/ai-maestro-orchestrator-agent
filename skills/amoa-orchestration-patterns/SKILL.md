---
name: amoa-orchestration-patterns
description: "Use when breaking down tasks for human developers. NOT for AI agents or plan-execute workflows. Trigger with task decomposition requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed, task agents, GitHub issues.
metadata:
  author: Emasoft
  version: 2.4.0
context: fork
user-invocable: false
agent: amoa-main
---

# Orchestration Patterns Skill

## Overview

Coordinates work among multiple developers using orchestration patterns: task decomposition, assignment, monitoring, escalation, and verification.

## Output

| Output Type | Description |
|-------------|-------------|
| TaskCreate calls | Task definitions with success criteria |
| Task assignments | Agent assignments via AI Maestro or Task tool |
| Progress reports | Regular status updates from monitoring |
| Completion signals | Verification of all tasks done |
| Escalation requests | Blocked task escalations to user/AMAMA |

## Procedure

1. **Task Decomposition** - Break goal into independent, parallelizable tasks
2. **Task Assignment** - Assign tasks with clear instructions and success criteria
3. **Progress Monitoring** - Track completion, identify blocks proactively
4. **Escalation & Unblocking** - Handle blocked tasks immediately
5. **Integration & Verification** - Combine results, require 4 verification loops before PR

## Key Rules

- **Never block the orchestrator** - Delegate all long-running tasks
- **One task per agent** - Clear boundaries prevent conflicts
- **Minimal reports** - Request 1-2 lines: "[DONE] task-name - result"
- **PROACTIVE monitoring** - Poll agents regularly; never wait passively
- **4 verification loops** before any PR approval
- **Orchestrator-exclusive comms** - Sub-agents NEVER send externally
- **Parallel spawning** - Up to 20 agents for independent tasks

## Quick Reference

See: [references/quick-reference-checklist.md](references/quick-reference-checklist.md)

## Example

See: [references/decomposition-example.md](references/decomposition-example.md)

## Reference Files

| Reference | Purpose |
|-----------|---------|
| [task-complexity-classifier](references/task-complexity-classifier.md) | Task complexity evaluation |
| [agent-selection-guide](references/agent-selection-guide.md) | Agent selection by language/domain |
| [project-setup-menu](references/project-setup-menu.md) | Interactive project setup |
| [language-verification-checklists](references/language-verification-checklists.md) | Code quality checklists |
| [progress-monitoring](references/progress-monitoring.md) | Agent monitoring protocols |
| [verification-loops](references/verification-loops.md) | 4-loop PR verification |
| [orchestrator-no-implementation](references/orchestrator-no-implementation.md) | RULE 15: No code writing |
| [user-requirements-immutable](references/user-requirements-immutable.md) | RULE 14: User approval |
| [rule-14-enforcement](references/rule-14-enforcement.md) | RULE 14 enforcement |
| [orchestrator-exclusive-communications](references/orchestrator-exclusive-communications.md) | RULE 16: Comms control |
| [non-blocking-patterns](references/non-blocking-patterns.md) | RULE 17: Stay responsive |
| [orchestrator-guardrails](references/orchestrator-guardrails.md) | Role boundaries |
| [delegation-checklist](references/delegation-checklist.md) | Delegation procedures |
| [orchestration-examples](references/orchestration-examples.md) | Workflow examples |
| [orchestration-api-commands](references/orchestration-api-commands.md) | API commands |
| [sub-agent-role-boundaries-template](references/sub-agent-role-boundaries-template.md) | Worker role template |
| [workflow-checklists](references/workflow-checklists.md) | Execution checklists |
| [log-formats](references/log-formats.md) | Log format specs |
| [archive-structure](references/archive-structure.md) | Archive structure |
| [script-output-rules](references/script-output-rules.md) | Script output protocol |

## Prerequisites

- AI Maestro running (`http://localhost:23000`)
- GitHub CLI (`gh`) authenticated

## Instructions

1. Decompose the goal into independent, parallelizable tasks with clear success criteria.
2. Assign each task to the appropriate agent (one task per agent, up to 20 in parallel).
3. Monitor agent progress proactively every 10-15 minutes; escalate blocked tasks immediately.
4. Collect results and run 4 verification loops before approving any PR.
5. Integrate verified results and archive completed work.

API details: [orchestration-api-commands](references/orchestration-api-commands.md).

## Error Handling

Blocked tasks escalate per [progress-monitoring](references/progress-monitoring.md). Failed agents respawn once, then escalate to user.

## Examples

See [orchestration-examples](references/orchestration-examples.md) and [decomposition-example](references/decomposition-example.md).

## Resources

See **Reference Files** table above.
