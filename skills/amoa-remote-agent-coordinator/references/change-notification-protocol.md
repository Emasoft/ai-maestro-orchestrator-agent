# Change Notification Protocol


## Contents

- [Table of Contents](#table-of-contents)
- [Purpose](#purpose)
- [Notification Types](#notification-types)
  - [1. Toolchain Update](#1-toolchain-update)
  - [2. Specification Update](#2-specification-update)
  - [3. Priority Change](#3-priority-change)
  - [4. Dependency Update](#4-dependency-update)
- [Agent Response](#agent-response)
- [Urgency Levels](#urgency-levels)
- [Broadcast vs Targeted](#broadcast-vs-targeted)
  - [Broadcast (All Agents)](#broadcast-all-agents)
  - [Targeted (Specific Agents)](#targeted-specific-agents)
- [Integration](#integration)
- [Acknowledgment Flow](#acknowledgment-flow)
  - [Flow Steps](#flow-steps)
  - [Reminder Notification Format](#reminder-notification-format)
  - [Escalation Criteria](#escalation-criteria)
- [Error States](#error-states)
  - [Error Response Format](#error-response-format)
  - [Partial Application Response](#partial-application-response)
- [Expanded Integration](#expanded-integration)
- [Troubleshooting](#troubleshooting)
  - [Problem: Agent Ignores Change Notifications](#problem-agent-ignores-change-notifications)
  - [Problem: Breaking Change Causes Agent Failure](#problem-breaking-change-causes-agent-failure)
  - [Problem: Agent Environment Cannot Support Change](#problem-agent-environment-cannot-support-change)
  - [Problem: Broadcast Notification Overwhelms System](#problem-broadcast-notification-overwhelms-system)
  - [Problem: Notification Lost During Agent Downtime](#problem-notification-lost-during-agent-downtime)
  - [Problem: Conflicting Changes Sent](#problem-conflicting-changes-sent)
  - [Problem: Partial Application With No Resolution](#problem-partial-application-with-no-resolution)

---

## Table of Contents

1. [Purpose](#purpose)
2. [When Your Toolchain Changes](#1-toolchain-update)
3. [When Project Specifications Update](#2-specification-update)
4. [When Task Priorities Shift](#3-priority-change)
5. [When Shared Dependencies Change](#4-dependency-update)
6. [When Agent Must Acknowledge Changes](#agent-response)
7. [When Deciding Notification Urgency](#urgency-levels)
8. [When Sending to All vs Specific Agents](#broadcast-vs-targeted)
9. [When Tracking Agent Acknowledgments](#acknowledgment-flow)
10. [When Agents Cannot Apply Changes](#error-states)
11. [How This Protocol Integrates](#integration)
12. [Complete Integration Map](#expanded-integration)

## Purpose

Notify remote agents of changes to project configuration, toolchain, specifications, or requirements that affect their work.

## Notification Types

### 1. Toolchain Update

When project toolchain changes:

```json
{
  "type": "change-notification",
  "category": "toolchain",
  "urgency": "high",
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"],
  "changes": [
    {
      "tool": "python",
      "old_version": "3.11",
      "new_version": "3.12",
      "action_required": "Update local environment"
    },
    {
      "tool": "ruff",
      "old_version": "0.3.0",
      "new_version": "0.8.0",
      "action_required": "Run ruff check with new rules"
    }
  ],
  "effective_immediately": true
}
```

### 2. Specification Update

When requirements change:

```json
{
  "type": "change-notification",
  "category": "specification",
  "urgency": "medium",
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"],
  "affected_tasks": ["GH-42", "GH-45"],
  "changes": [
    {
      "spec_file": "docs/api-spec.md",
      "section": "Authentication",
      "summary": "JWT expiry changed from 7d to 24h",
      "diff_url": "https://github.com/.../commit/abc123"
    }
  ],
  "action_required": "Review and adjust implementation"
}
```

### 3. Priority Change

When task priorities shift:

```json
{
  "type": "change-notification",
  "category": "priority",
  "urgency": "high",
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"],
  "changes": [
    {
      "task_id": "GH-42",
      "old_priority": "normal",
      "new_priority": "critical",
      "reason": "Security vulnerability discovered"
    }
  ],
  "action_required": "Pause current work, focus on GH-42"
}
```

### 4. Dependency Update

When shared dependencies change:

```json
{
  "type": "change-notification",
  "category": "dependency",
  "urgency": "medium",
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"],
  "changes": [
    {
      "package": "shared-utils",
      "old_version": "1.2.0",
      "new_version": "2.0.0",
      "breaking_changes": true,
      "migration_guide": "See CHANGELOG.md"
    }
  ]
}
```

## Agent Response

Agents acknowledge change notifications:

```json
{
  "type": "change-acknowledgment",
  "notification_id": "notif-123",
  "status": "acknowledged",
  "impact_assessment": "Will need to update 3 test files",
  "questions": []
}
```

## Urgency Levels

| Level | Action |
|-------|--------|
| `critical` | Stop work immediately, apply change before continuing |
| `high` | Complete current task, then apply change before starting next task |
| `medium` | Apply change at next checkpoint (after current file/function/test) |
| `low` | Apply change when convenient (next session or task break) |

## Broadcast vs Targeted

### Broadcast (All Agents)
```json
{
  "type": "change-notification",
  "broadcast": true,
  "target_agents": [],
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"]
}
```

### Targeted (Specific Agents)
```json
{
  "type": "change-notification",
  "broadcast": false,
  "target_agents": ["dev-agent-1", "dev-agent-2"],
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"]
}
```

## Integration

- Link to `echo-acknowledgment-protocol.md` for response handling
- Log all notifications in session memory
- Track which agents acknowledged

## Acknowledgment Flow

Orchestrator tracks agent acknowledgments using event-driven pattern (no fixed timeouts):

### Flow Steps

1. **Send notification** to target agent(s)
2. **Log notification** in session memory with:
   - Notification ID
   - Target agents
   - Urgency level
   - Timestamp sent
   - Acknowledgment status: `pending`
3. **Monitor for acknowledgment** via message inbox
4. **On acknowledgment received**:
   - Update status to `acknowledged`
   - Log agent response
   - Proceed with coordination
5. **If no acknowledgment** after orchestrator checks inbox multiple times:
   - Send **reminder notification** with `reminder: true` flag
   - Log reminder sent
6. **If still no acknowledgment** after second reminder:
   - For `critical`/`high` urgency: **Escalate to user** for manual intervention
   - For `medium`/`low` urgency: **Log warning**, continue with assumption agent will comply

### Reminder Notification Format

```json
{
  "type": "change-notification",
  "notification_id": "notif-123",
  "reminder": true,
  "reminder_count": 1,
  "original_sent_at": "2025-12-31T10:00:00Z",
  "urgency": "high",
  "config_location": "design/config/",
  "affected_files": ["project-context.md", "standards.md"],
  "message": "REMINDER: Acknowledge toolchain update before continuing work"
}
```

### Escalation Criteria

| Urgency | Escalate When |
|---------|---------------|
| `critical` | After 2nd reminder with no acknowledgment |
| `high` | After 2nd reminder with no acknowledgment |
| `medium` | After 3rd reminder with no acknowledgment (optional) |
| `low` | No escalation needed (log warning only) |

## Error States

| State | Meaning | Action |
|-------|---------|--------|
| `cannot-apply-change` | Agent unable to comply | Agent escalates with reason |
| `breaking-change-detected` | Change breaks current work | Agent pauses, requests guidance |
| `incompatible-environment` | Local env can't support change | Agent reports environment details |
| `no-acknowledgment-after-reminders` | No response after multiple reminders | Orchestrator escalates to user (critical/high) or logs warning (medium/low) |
| `partial-application` | Some changes applied, some failed | Report partial status |

### Error Response Format

If agent cannot apply change:

```json
{
  "type": "change-acknowledgment",
  "notification_id": "notif-123",
  "status": "error",
  "error": {
    "code": "cannot-apply-change",
    "reason": "Python 3.12 not available in container",
    "current_environment": {
      "python_version": "3.11.5",
      "os": "Ubuntu 22.04",
      "container": true
    },
    "assistance_needed": true,
    "suggested_action": "Update container image to python:3.12-slim"
  }
}
```

### Partial Application Response

If only some changes could be applied:

```json
{
  "type": "change-acknowledgment",
  "notification_id": "notif-123",
  "status": "partial",
  "applied": [
    "ruff upgraded to 0.8.0",
    "mypy upgraded to 1.14.0"
  ],
  "failed": [
    {
      "change": "Python upgrade to 3.13",
      "reason": "Not available in current package manager"
    }
  ],
  "assistance_needed": true
}
```

## Expanded Integration

This protocol integrates with:

- `echo-acknowledgment-protocol.md` - Acknowledgment pattern for notifications
- `task-instruction-format.md` - Config section (Project Configuration)
- `messaging-protocol.md` - Priority levels and message envelope
- `session-memory/` - Track which agents acknowledged which changes
- `artifact-sharing-protocol.md` - Config files may be shared as artifacts

---

## Troubleshooting

### Problem: Agent Ignores Change Notifications

**Symptoms**: Agent continues work without acknowledging urgent change.

**Solution**:
1. Send explicit reminder with `reminder: true` flag
2. Increase urgency level if appropriate
3. For critical changes, send STOP command until acknowledgment received
4. Check if agent received notification (delivery issues)
5. Escalate to user if agent persistently ignores

### Problem: Breaking Change Causes Agent Failure

**Symptoms**: Agent reports work blocked after applying change.

**Solution**:
1. Assess if change can be rolled back temporarily
2. Provide agent with migration guide or steps
3. If change is mandatory, help agent adapt implementation
4. For dependency changes, provide compatibility shim instructions
5. Update change notification with additional guidance

### Problem: Agent Environment Cannot Support Change

**Symptoms**: Agent reports `incompatible-environment` error.

**Solution**:
1. Determine if environment upgrade is feasible
2. Provide alternative approach if available
3. Consider assigning task to agent with compatible environment
4. For container environments, provide updated image reference
5. Document environment requirements for future assignments

### Problem: Broadcast Notification Overwhelms System

**Symptoms**: Too many agents responding simultaneously, messages delayed.

**Solution**:
1. Stagger broadcast timing across agent groups
2. Use targeted notifications when possible
3. For non-critical changes, use `low` urgency to spread acknowledgments
4. Monitor AI Maestro queue for capacity issues
5. Consider batching non-urgent changes

### Problem: Notification Lost During Agent Downtime

**Symptoms**: Agent comes back online without knowledge of change.

**Solution**:
1. Include change notification in session start checklist
2. Store unacknowledged notifications for replay
3. Send "catch-up" notification on agent reconnection
4. Include `config_version` in task delegations for verification
5. Agent should pull latest config on session start

### Problem: Conflicting Changes Sent

**Symptoms**: Two notifications contradict each other.

**Solution**:
1. Always include timestamp in notifications
2. Agent should apply most recent change only
3. Orchestrator should avoid sending conflicting changes
4. If conflict detected, send clarification notification
5. Use notification IDs to supersede previous notifications

### Problem: Partial Application With No Resolution

**Symptoms**: Agent stuck with partially applied changes, can't proceed.

**Solution**:
1. Prioritize resolving failed changes before new work
2. Provide step-by-step fix for each failed change
3. If change is optional, explicitly mark it as skippable
4. Help agent rollback to known-good state if needed
5. Document which changes are mandatory vs optional

## Decision Trees for Change Notifications

### Module Modification Notification Dispatch Decision Tree

```
Module modification detected (dependency updated / API changed / config changed)
├─ Which agents are currently working on tasks that use this module?
│   ├─ None → Log the change → No notification needed
│   ├─ One agent → Send Module Modification Notification directly
│   │               → Agent ACKs → Agent adjusts work if needed
│   └─ Multiple agents → Send Broadcast notification to all affected agents
│       ├─ All ACK within 5 min → Continue monitoring
│       └─ Some don't ACK → Retry non-responders → If still no ACK, escalate
```

### Priority Change Notification Dispatch Decision Tree

```
Priority change received from ECOS
├─ Is the change an upgrade (e.g., normal → high) or downgrade (high → normal)?
│   ├─ Upgrade → Is affected agent currently idle on this task?
│   │   ├─ Yes → Send Priority Change Notification → Agent resumes immediately
│   │   └─ No (agent working on something else) → Is new priority higher than current work?
│   │       ├─ Yes → Send Priority Override → Agent pauses current, switches to this
│   │       └─ No → Queue notification → Deliver when agent completes current task
│   └─ Downgrade → Send Priority Change Notification (informational)
│       → Agent continues at own pace → No immediate action required
```

**Cross-reference**: For detailed mid-task update message formats, see `mid-task-update-templates.md`.
