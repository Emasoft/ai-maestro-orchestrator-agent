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

Monitors agent progress via state transitions, detects stalls, and escalates issues.

## Prerequisites

Requires **AGENT_OPERATIONS.md**, **amoa-label-taxonomy**, **amoa-messaging-templates**, AI Maestro API, GitHub CLI.

## Instructions

States: Acknowledged, No ACK, Active, No Progress, Stale, Unresponsive, Blocked, Complete. Transitions: Assigned→Acknowledged→Active→Complete. Stalls: No Progress→Stale→Unresponsive.
<!-- TOC: Escalation|Reminders|Reassignment|Progress|Completion -->

1. Query `status:in-progress` issues; determine each agent's state via timestamps
2. No ACK/No Progress/Stale → send reminder or status request
3. Unresponsive → escalate; Blocked → create `type:blocker` issue, notify user
4. Complete → verify PR, tests, review, docs; update labels
<!-- TOC: IronRule|BlockerDef|Protocol|Labels|Resolution|Lifecycle -->

Copy this checklist and track your progress:

- [ ] Query in-progress issues and determine agent states
- [ ] Send reminders/escalate as needed per state
- [ ] Verify completions and update labels

## Output

State report table (task, agent, state, last update) + escalation messages + blocker issues.

## Examples

**Input:** Query state for task #42 assigned to `libs-svg-svgbbox`
**Output:** `| #42 | libs-svg-svgbbox | Stale | 2h ago |` → sends status request

## Error Handling

Escalate: reminder→urgent→reassignment. Blockers→`type:blocker` issues. See [references/monitoring-examples.md](references/monitoring-examples.md).
<!-- TOC: Example 1: Query Agent State via AI Maestro | Example 2: Send First Reminder | Example 3: Escalate to Urgent | Example 4: Handle Blocker Report | Example 5: Verify Completion | Dashboard Queries | Error Handling -->

## Resources

- [references/blocker-handling-protocol.md](references/blocker-handling-protocol.md)
  - Iron Rule for Blockers
  - Comprehensive Blocker Definition
  - Blocker Response Protocol
  - Update Labels and Create Blocker Issue
  - Resolution
  - When Blocker Resolved
  - Blocker Lifecycle Checklist
- [references/escalation-and-messaging.md](references/escalation-and-messaging.md)
  - Escalation Order
  - First Reminder
  - Urgent Reminder
  - Reassignment Decision
  - Progress Report Format
    - Status Update
    - Completion Report
    - Blocker Report
  - Completion Verification
    - Verification Checklist
    - If Verification Passes
    - If Verification Fails
- [references/monitoring-examples.md](references/monitoring-examples.md)
  - Example 1: Query Agent State via AI Maestro
  - Example 2: Send First Reminder
  - Example 3: Escalate to Urgent
  - Example 4: Handle Blocker Report
  - Example 5: Verify Completion
  - Dashboard Queries
  - Error Handling
