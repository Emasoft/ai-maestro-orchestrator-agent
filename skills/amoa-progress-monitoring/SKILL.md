---
name: amoa-progress-monitoring
description: "Use when monitoring agent progress. Trigger with status check or stall detection requests."
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

Monitors agent progress via **state transitions** and **response order**. Tracks states, detects stalls, escalates issues.

## Prerequisites

1. **AGENT_OPERATIONS.md**, **amoa-label-taxonomy**, **amoa-messaging-templates**
2. Access to AI Maestro API and GitHub CLI

---

## 1. Agent States

| State | Definition | Action |
|-------|------------|--------|
| **Acknowledged** | Agent sent ACK | Normal monitoring |
| **No ACK** | No acknowledgment | Send reminder |
| **Active** | Sending updates | Continue monitoring |
| **No Progress** | ACK but no updates | Send status request |
| **Stale** | Outdated last update | Escalate priority |
| **Unresponsive** | No response to reminders | Consider reassignment |
| **Blocked** | Reported blocker | Address blocker |
| **Complete** | Task done reported | Verify and close |

## 2. State Detection

Via `agent-messaging` timestamps. Transitions: Assigned→Acknowledged→Active→Complete. Stalls: No Progress→Stale→Unresponsive. Any→Blocked on blocker.

## 3. Escalation

(1) First reminder, (2) Urgent reminder, (3) User notification + reassignment. See: `references/escalation-and-messaging.md`
<!-- TOC: Escalation|Reminders|Reassignment|Progress|Completion -->

## 4. Progress Report Format

Agents use `[IN_PROGRESS]`, `[DONE]`, or `[BLOCKED]` prefixed messages. See: `references/escalation-and-messaging.md`
<!-- TOC: Escalation|Reminders|Reassignment|Progress|Completion -->

## 5. Blocker Handling

**IRON RULE**: User informed of blockers immediately. Verify, create `type:blocker` issue, escalate. See: `references/blocker-handling-protocol.md`
<!-- TOC: IronRule|BlockerDef|Protocol|Labels|Resolution|Lifecycle -->

## 6. Completion Verification

Verify: PR exists, tests pass, review approved, docs updated. See: `references/escalation-and-messaging.md`
<!-- TOC: Escalation|Reminders|Reassignment|Progress|Completion -->

---

## Instructions

1. Query all issues with `status:in-progress` label
2. For each task, determine agent state and check last message timestamp
3. Send reminders or status requests based on state (No ACK, No Progress, Stale)
4. Escalate unresponsive agents; handle blockers immediately
5. Verify completion for tasks marked complete; update issue labels
6. Log all state transitions and escalations

Copy this checklist and track your progress:

- [ ] Query all issues with `status:in-progress` label
- [ ] For each task: determine agent state, check last message timestamp
- [ ] No ACK → reminder; No Progress/Stale → status request
- [ ] Unresponsive → urgent escalation
- [ ] Blocked → handle blocker; Complete → verify completion
- [ ] Update issue labels to reflect current state
- [ ] Log all state transitions and escalations

## Output

- **State report**: Table (task, agent, state, last update)
- **Escalation**: AI Maestro JSON message
- **Dashboard**: Table of in-progress tasks
- **Blocker report**: Issue comment
- **Completion**: Boolean + checklist

## Error Handling

Unresponsive agents escalate: reminder→urgent→reassignment. Blockers create `type:blocker` issues. See `references/monitoring-examples.md`.
<!-- TOC: QueryState|Reminder|Escalate|Blocker|Completion|Dashboard|Errors -->

## Resources

- `references/blocker-handling-protocol.md` - Blocker handling and lifecycle
  <!-- TOC: Iron Rule | Blocker Definition | Response Protocol | Update Labels | Resolution | When Resolved | Lifecycle Checklist -->
- `references/escalation-and-messaging.md` - Escalation, templates, completion
  <!-- TOC: Escalation Order | First Reminder | Urgent Reminder | Reassignment Decision | Progress Report Format | Completion Verification -->
- `references/monitoring-examples.md` - Examples and error handling
  <!-- TOC: Query Agent State | Send First Reminder | Escalate to Urgent | Handle Blocker Report | Verify Completion | Dashboard Queries | Error Handling -->
- **AGENT_OPERATIONS.md**, **amoa-label-taxonomy**, **amoa-messaging-templates**

## Examples

**Input:** Query agent state for task #42 assigned to `libs-svg-svgbbox`
**Output:** `| #42 | libs-svg-svgbbox | Stale | 2h ago |` → sends status request message

**Input:** Agent reports `[BLOCKED] #42 - missing API credentials`
**Output:** Creates `type:blocker` issue, escalates to user immediately

See `references/monitoring-examples.md` for full worked examples.
<!-- TOC: QueryState|Reminder|Escalate|Blocker|Completion|Dashboard|Errors -->

## Script Output Rules

Verbose output to `docs_dev/reports/`. Stdout: `[OK/ERROR] name - summary`. `scripts/amoa_stop_check/` outputs JSON (hook).
