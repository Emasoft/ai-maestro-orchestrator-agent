---
name: eoa-messaging-templates
description: AI Maestro message templates for emasoft plugins. Use when sending task assignments, status reports, or escalations between agents. Trigger with messaging requests.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Step 20"
procedure: "proc-request-pr-review"
---

# EOA Shared Communication Templates

## Overview

This skill provides shared AI Maestro message templates and communication protocols used across all emasoft plugins for agent coordination, task assignment, status reporting, and escalation.

## Prerequisites

1. AI Maestro messaging system (AMP) running
2. Understanding of emasoft agent roles (EOA, ECOS, EIA, EAMA)
3. Access to AI Maestro API for sending/receiving messages
4. Read **eoa-label-taxonomy** for GitHub label usage
5. Understanding of communication hierarchy and authority rules

## Instructions

1. Identify the communication scenario (task assignment, status report, approval request, etc.)
2. Select the appropriate message template from section 2
3. Fill in the template with task-specific details
4. Send the message via AI Maestro using the `agent-messaging` skill
5. Wait for response according to the message type and priority
6. Log the message exchange in the appropriate delegation/coordination log

### Checklist

Copy this checklist and track your progress:

**Message Sending Workflow:**
- [ ] Identify the communication scenario (task assignment, status report, approval, escalation, etc.)
- [ ] Select the appropriate message template from section 2
- [ ] Fill in all required template fields (from, to, subject, priority, content)
- [ ] Verify AI Maestro messaging system (AMP) is running
- [ ] Send the message via AI Maestro using the `agent-messaging` skill
- [ ] Wait for response according to message type and priority
- [ ] Log the message exchange in the appropriate delegation/coordination log
- [ ] If no response, follow escalation order from section 3.6

## Table of Contents

- [1. AI Maestro Message Format](#1-ai-maestro-message-format)
- [2. Message Templates by Scenario](#2-message-templates-by-scenario)
- [3. Cross-Plugin Protocol Reference](#3-cross-plugin-protocol-reference)
- [4. Record-Keeping Standards](#4-record-keeping-standards)

---

## 1. AI Maestro Message Format

### Standard Message Structure

All AI Maestro messages use this format:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<sender-agent-name>",
  "to": "<recipient-agent-name>",
  "subject": "<short-subject-line>",
  "priority": "high|normal|low",
  "content": {
    "type": "request|response|notification|acknowledgment",
    "message": "<human-readable-message>",
    "data": {
      "task_id": "<optional-task-identifier>",
      "pr_number": "<optional-pr-number>",
      "issue_number": "<optional-issue-number>",
      "status": "<optional-status>"
    }
  }
}
```

### Sending Messages

Send messages using the `agent-messaging` skill. Provide the JSON payload with recipient, subject, priority, and content fields as described above.

### Checking Inbox

Check your inbox using the `agent-messaging` skill. Retrieve all unread messages for your session and process the content of each message.

**Verify**: confirm all messages are delivered or received as expected.

---

## 2. Message Templates by Scenario

For complete JSON templates with all fields, see **[references/message-templates.md](references/message-templates.md)**:

- **2.1 Task Assignment (EOA → Remote Agent)** - Assigning implementation task to remote agent
- **2.2 Task Completion Report (Agent → EOA)** - Agent reporting task completion
- **2.3 Status Request (EOA → Agent)** - Orchestrator polling agent for status
- **2.4 Status Response (Agent → EOA)** - Agent responding to status request
- **2.5 Approval Request (ECOS → EAMA)** - Chief of Staff requesting approval
- **2.6 Approval Response (EAMA → ECOS)** - Assistant Manager responding to approval
- **2.7 Escalation (Any Agent → ECOS/EAMA)** - Agent encountering blocker requiring escalation
- **2.8 Acknowledgment (Any Agent)** - Acknowledging receipt of message
- **2.9 Design Handoff (EAA → EOA)** - Architect handing off design to Orchestrator
- **2.10 Integration Request (EOA → EIA)** - Orchestrator requesting code integration/review
- **2.11 Integration Result (EIA → EOA)** - Integrator reporting integration/review result

For AI Maestro curl command templates with all message types, see **[references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md)**:

- Ready-to-use curl commands for each message type
- Complete JSON payloads with all required fields
- Copy-paste templates for quick messaging

### Extended Communication Templates

For response templates FROM other agents TO EOA, see **[references/ecos-response-templates.md](references/ecos-response-templates.md)**:

- ECOS response to EOA Task Completion Report (accept/rework/clarify)
- EAMA response to EOA Blocker Escalation (user decision delivered/deferred/rejected)
- EAA response to Design Issue Escalation (guidance/revised design/investigate)
- Decision trees for each response type

For session lifecycle messages (wake/hibernate/terminate), see **[references/session-lifecycle-templates.md](references/session-lifecycle-templates.md)**:

- ECOS Wake message to EOA + EOA Wake ACK
- ECOS Hibernate directive + EOA Hibernate ACK
- ECOS Terminate directive + EOA Final Termination Report
- EOA Periodic Status Report (30-min scheduled summary)
- Decision trees for each lifecycle event

For task lifecycle commands (cancel/pause/resume/broadcast/stop), see **[references/task-lifecycle-templates.md](references/task-lifecycle-templates.md)**:

- Task Cancellation send + agent work-summary response
- Task Pause/Resume send + agent state-checkpoint ACK
- Broadcast Message send + individual ACKs
- Agent Stop Work Notification + response
- Decision trees: Cancel vs Pause vs Reassign; Broadcast vs Targeted

For agent resource and skill requests, see **[references/resource-request-templates.md](references/resource-request-templates.md)**:

- Agent Resource Request (tools/access/credentials) → EOA response (grant/deny/escalate)
- Agent Skill Request (different capability) → EOA response
- EOA formal ACK of ECOS Task assignment (JSON template)
- Decision tree: Grant directly / Escalate to ECOS / Deny with alternative

---

## 3. Cross-Plugin Protocol Reference

### 3.1 Communication Hierarchy

```
USER
  ↓
EAMA (Assistant Manager) - User's interface, approval authority
  ↓
ECOS (Chief of Staff) - Agent lifecycle, team management
  ↓ ↓ ↓
EAA (Architect)  EOA (Orchestrator)  EIA (Integrator)
```

### 3.2 Who Messages Whom

| From | To | Purpose |
|------|-----|---------|
| EAMA | ECOS | Project creation, approval decisions, status requests |
| ECOS | EAMA | Approval requests, status reports, escalations |
| ECOS | EOA | Agent availability notifications, team assignments |
| ECOS | EAA | Design requests (via EOA typically) |
| EOA | EAA | Design requests, requirements handoff |
| EOA | EIA | Integration/review requests |
| EOA | Remote Agents | Task assignments, status requests |
| EAA | EOA | Design handoffs |
| EIA | EOA | Integration results, quality reports |
| Any Agent | ECOS | Escalations, resource requests |

### 3.3 Label Prefix for GitHub (Single-Account Mode)

All plugins use `assign:` prefix for agent assignment labels:

```bash
# Assign task to agent
gh issue edit <number> --add-label "assign:<agent-name>"

# Query agent's tasks
gh issue list --label "assign:<agent-name>"
```

### 3.4 Status Labels

| Label | Meaning |
|-------|---------|
| `status:todo` | Not started |
| `status:in-progress` | Being worked on |
| `status:blocked` | Blocked, needs attention |
| `status:review` | Ready for review |
| `status:done` | Complete |

### 3.5 Cross-Plugin Conflict Resolution

When multiple agents need to modify the same resources (labels, issues), follow conflict resolution protocol.

**See [references/conflict-resolution.md](references/conflict-resolution.md) for:**
- Authority hierarchy (EAMA > ECOS > EOA > EIA > EAA)
- Label conflict resolution rules
- Label change request protocol with message template
- Emergency override cases (agent terminated, unresponsive, critical blocker)

### 3.6 Escalation Order and Priority

Escalation is based on **order**, **priority**, and **state transitions** - not fixed time intervals (agents may hibernate for days).

**See [references/escalation-protocol.md](references/escalation-protocol.md) for:**
- 4-step escalation order (Send → First Reminder → Urgent Reminder → Escalate/Reassign)
- State-based triggers (No ACK, No Progress, Stale, Unresponsive)
- Priority escalation rules (Normal → High → Urgent → User)
- Deployment-specific timing considerations

---

## 4. Record-Keeping Standards

All emasoft plugins follow consistent record-keeping standards for delegation logs, status reports, and handoff documents.

**See [references/record-keeping.md](references/record-keeping.md) for:**
- Standard `docs_dev/` directory structure for each plugin (orchestration, integration, design, chief-of-staff, projects, reports)
- Filename conventions (timestamped, task-based, PR-based, date-based)
- Log entry markdown format with timestamp, agent, action, status, details, output

---

## Examples

**See [references/examples.md](references/examples.md) for:**
- Full task assignment flow (13-step workflow from user request to completion)
- Complete curl command examples for task assignment, status request, and escalation
- Working code snippets you can copy and modify

---

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| AI Maestro message | JSON | Task assignment, status request, approval |
| Message confirmation | API response | `{"status": "sent", "message_id": "xyz"}` |
| Message history | JSON array | All messages for an agent |
| Delegation log entry | Markdown | Timestamped record of message sent |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Message not delivered | AI Maestro offline or agent not found | Check AI Maestro health, verify agent session name |
| No response from agent | Agent hibernated, offline, or unresponsive | Follow escalation order from section 3.6 |
| Invalid JSON | Malformed message content | Validate JSON syntax before sending |
| Wrong recipient | Incorrect agent name or session ID | Verify agent name from roster or AI Maestro |
| Label conflict | Multiple agents modifying same issue | Follow conflict resolution protocol from section 3.5 |

---

## Quick Reference Card

| Scenario | Template | Priority |
|----------|----------|----------|
| Assign task | 2.1 | high |
| Task complete | 2.2 | normal |
| Status request | 2.3 | normal |
| Status response | 2.4 | normal |
| Approval request | 2.5 | high |
| Approval response | 2.6 | high |
| Escalation | 2.7 | high |
| Acknowledgment | 2.8 | low |
| Design handoff | 2.9 | high |
| Integration request | 2.10 | high |
| Integration result | 2.11 | high |

---

## Resources

- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **eoa-label-taxonomy** - GitHub label usage
- **eoa-task-distribution** - Task assignment protocol
- **eoa-progress-monitoring** - Agent state tracking
- **AI Maestro AMP messaging**
- [AI Maestro Message Templates](./references/ai-maestro-message-templates.md) - Curl command templates
