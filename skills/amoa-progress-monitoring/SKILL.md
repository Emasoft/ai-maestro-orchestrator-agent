---
name: amoa-progress-monitoring
description: Agent progress monitoring via state-based detection. Use when tracking task completion, detecting stalls, or escalating unresponsive agents. Trigger with progress checks.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Progress Monitoring Skill

## Overview

Monitors agent progress using **state transitions** and **response order** (not fixed time intervals). Agents collaborate asynchronously and may be hibernated. The orchestrator tracks agent states and escalates through ordered steps when issues are detected.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **amoa-label-taxonomy** for status labels and workflow states
3. Read **amoa-messaging-templates** for message formats and escalation templates
4. Access to AI Maestro API and GitHub CLI

---

## 1. Agent States

| State | Definition | Action |
|-------|------------|--------|
| **Acknowledged** | Agent sent ACK for assigned task | Normal monitoring |
| **No ACK** | Task assigned but no acknowledgment | Send reminder |
| **Active** | Agent sending progress updates | Continue monitoring |
| **No Progress** | Agent acknowledged but no updates | Send status request |
| **Stale** | Last update predates significant events | Escalate priority |
| **Unresponsive** | Multiple reminders without response | Consider reassignment |
| **Blocked** | Agent reported blocker | Address blocker |
| **Complete** | Agent reported task done | Verify and close |

## 2. State Detection

Use `agent-messaging` skill to retrieve last message timestamp. State transitions:

```
Assigned → (ACK received) → Acknowledged → (progress) → Active
Acknowledged → (no updates) → No Progress
Active → (no updates) → Stale → (no response) → Unresponsive
Any → (blocker reported) → Blocked
Active → (completion reported) → Complete
```

## 3. Escalation

Three-step escalation: (1) First reminder at Normal priority, (2) Urgent reminder if no response, (3) User notification and reassignment consideration. See: `references/escalation-and-messaging.md`

## 4. Progress Report Format

Agents report using `[IN_PROGRESS]`, `[DONE]`, or `[BLOCKED]` prefixed messages with task-id, progress, blockers, and next steps. See: `references/escalation-and-messaging.md`

## 5. Blocker Handling

**IRON RULE**: User must ALWAYS be informed of blockers immediately. Verify blocker is real, create a separate GitHub issue (`type:blocker`), escalate to AMAMA immediately, and restore previous status when resolved. See: `references/blocker-handling-protocol.md`

## 6. Completion Verification

Verify: PR exists, tests pass, code review approved, docs updated, checklist complete. Update labels and close issue on pass; send clarification request on fail. See: `references/escalation-and-messaging.md`

---

## Instructions

1. Query all issues with `status:in-progress` label
2. For each assigned task:
   1. Determine current agent state (section 1)
   2. Check AI Maestro for agent's last message timestamp
   3. Compare task assignment time vs. last agent update
   4. If No ACK → send first reminder; if No Progress/Stale → send status request
   5. If Unresponsive → send urgent escalation
   6. If Blocked → handle blocker (section 5)
   7. If Complete → verify completion (section 6)
3. Update issue labels to reflect current state
4. Log all state transitions and escalations

## Output

| Output Type | Format |
|-------------|--------|
| Agent state report | Markdown table (task, agent, state, last update) |
| Escalation message | AI Maestro JSON message |
| Dashboard view | Markdown table of all in-progress tasks |
| Blocker report | Issue comment with blocker details |
| Completion verification | Boolean + checklist |

## References

- `references/blocker-handling-protocol.md` - Full blocker handling, labels, lifecycle checklists
- `references/escalation-and-messaging.md` - Escalation steps, message templates, report formats, completion verification
- `references/monitoring-examples.md` - Worked examples, dashboard queries, error handling
- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **amoa-label-taxonomy** - Status labels and workflow states
- **amoa-messaging-templates** - Escalation message templates
- **amoa-task-distribution** - Assignment protocol and agent states
- **amoa-implementer-interview-protocol** - Post-task verification protocol

## Error Handling

See `references/monitoring-examples.md`.

## Examples

See same reference file above.

## Script Output Rules

Scripts MUST follow the token-efficient output protocol:

1. Verbose output goes to `docs_dev/reports/` (timestamped)
2. Stdout: only `[OK/ERROR] script_name - summary` + `Report: path`
3. **EXCEPTION**: `scripts/amoa_stop_check/` MUST output JSON to stdout (hook requirement)

## Resources

See References.
