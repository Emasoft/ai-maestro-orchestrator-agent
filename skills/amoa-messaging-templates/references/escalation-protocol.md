# Escalation Order and Priority Protocol

AI agents collaborate asynchronously across unpredictable timeframes. Agents may be hibernated for days and resume later. Therefore, escalation is based on **order**, **priority**, and **state transitions** - not fixed time intervals.

## Table of Contents

- [Escalation Order](#escalation-order)
- [State-Based Triggers](#state-based-triggers)
- [Priority Escalation](#priority-escalation)
- [Important Notes](#important-notes)

---

## Escalation Order

All emasoft plugins follow this escalation sequence:

| Step | Action | Trigger Condition | Priority |
|------|--------|-------------------|----------|
| 1 | Send task/request | Initial assignment | As specified |
| 2 | First Reminder | No ACK received | Normal |
| 3 | Urgent Reminder | No response to first reminder | High |
| 4 | Escalate or Reassign | No response to urgent reminder | Urgent |

---

## State-Based Triggers

Escalation is triggered by **agent state changes**, not time intervals:

- **No ACK**: Agent has not acknowledged task receipt
- **No Progress**: Agent acknowledged but no status update since
- **Stale**: Agent's last update predates significant system events (e.g., new requirements, blocked dependencies now resolved)
- **Unresponsive**: Multiple reminders sent without response

---

## Priority Escalation

As escalation progresses, priority increases:

- **Normal → High**: After first reminder without response
- **High → Urgent**: After urgent reminder without response
- **Urgent → User**: When reassignment cannot resolve the blocker

---

## Important Notes

**Polling intervals and retry counts are deployment-specific.** The sequence and priority order are what matter, not exact durations.

**Example deployment variations:**
- Fast iteration: 5 minutes between reminders
- Async collaboration: 1 day between reminders
- Hibernated agents: Check state on resume, not elapsed time

The protocol adapts to the workflow, not the other way around.
