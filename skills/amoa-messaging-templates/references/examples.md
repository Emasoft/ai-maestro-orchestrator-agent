# AI Maestro Communication Examples

This document provides intent-based examples for common AI Maestro messaging scenarios. Use the `agent-messaging` skill for all message operations.

## Table of Contents

- [Full Task Assignment Flow](#full-task-assignment-flow)
- [Example 1: Send Task Assignment](#example-1-send-task-assignment)
- [Example 2: Send Status Request](#example-2-send-status-request)
- [Example 3: Escalate to Assistant Manager](#example-3-escalate-to-assistant-manager)

---

## Full Task Assignment Flow

```
1. EAMA receives user request
2. EAMA creates project, spawns ECOS
3. ECOS spawns EOA for project
4. EOA receives requirements from EAA (via ECOS)
5. EOA breaks down into tasks
6. EOA assigns tasks to agents using message template 2.1
7. Agents report progress using template 2.4
8. Agents report completion using template 2.2
9. EOA requests EIA verification using template 2.10
10. EIA reports result using template 2.11
11. EOA reports to ECOS
12. ECOS reports to EAMA
13. EAMA reports to user
```

---

## Example 1: Send Task Assignment

Send a task assignment message using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Task Assignment: Implement auth module"
- **Content**: "You are assigned: Implement authentication module. Success criteria: JWT tokens, session management, tests passing."
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `task_id` ("auth-core"), `issue_number` ("42"), `handoff_doc` path

**Verify**: confirm message delivery.

---

## Example 2: Send Status Request

Send a status request message using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Status Request: #42"
- **Content**: "What is your current status on #42? Report progress, blockers, and next steps."
- **Type**: `request`
- **Priority**: `normal`
- **Data**: include `task_id` ("42")

**Verify**: confirm message delivery.

---

## Example 3: Escalate to Assistant Manager

Send an escalation message using the `agent-messaging` skill:
- **Recipient**: `assistant-manager`
- **Subject**: "Approval Required: Requirement Change"
- **Content**: "Implementer identified issue with immutable requirement. User decision required."
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `operation` ("requirement_change"), `risk_level` ("high"), `justification`

**Verify**: confirm message delivery.
