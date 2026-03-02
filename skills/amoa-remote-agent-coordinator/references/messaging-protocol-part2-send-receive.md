# Messaging Protocol Part 2: Sending and Receiving Messages


## Contents

- [2.1 Basic Send Syntax](#21-basic-send-syntax)
  - [Command Syntax](#command-syntax)
  - [Parameters](#parameters)
  - [Basic Example](#basic-example)
- [2.2 Send with Task Assignment](#22-send-with-task-assignment)
  - [Simple Task Assignment](#simple-task-assignment)
  - [Using Heredoc for Complex Content](#using-heredoc-for-complex-content)
- [2.3 Check Inbox Command](#23-check-inbox-command)
  - [List All Unread Messages](#list-all-unread-messages)
  - [Example Output](#example-output)
- [2.4 Read and Mark Message as Read](#24-read-and-mark-message-as-read)
  - [Command Syntax](#command-syntax)
  - [Example](#example)
  - [Example Output](#example-output)
- [2.5 Workflow Example](#25-workflow-example)
  - [Complete Send-Receive-Respond Flow](#complete-send-receive-respond-flow)
- [Related Sections](#related-sections)

---

**Parent document**: [messaging-protocol.md](messaging-protocol.md)

---

## 2.1 Basic Send Syntax

Use the `agent-messaging` skill to send messages (see `~/.claude/skills/agent-messaging/SKILL.md`).

### Required Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| Recipient | YES | Recipient's full session name |
| Subject | YES | Brief subject line |
| Message | YES | Message content (string or JSON) |
| Priority | NO | `low`, `normal`, `high`, or `urgent` (default: `normal`) |
| Type | NO | Message type (default: `task`) |

### Basic Example

Send a status request using the `agent-messaging` skill:
- **Recipient**: `dev-agent-1`
- **Subject**: "Status check"
- **Content**: "How is GH-42 progressing?"
- **Type**: `status-request`
- **Priority**: `normal`

**Verify**: confirm message delivery.

---

## 2.2 Send with Task Assignment

For complex JSON content, use a variable or heredoc:

### Simple Task Assignment

Send a task assignment message using the `agent-messaging` skill:
- **Recipient**: `dev-agent-1`
- **Subject**: "Implement Feature GH-42"
- **Content**: JSON with `task_id` ("GH-42"), `instructions`, `completion_criteria`, `report_back` (true)
- **Type**: `task`
- **Priority**: `high`

### Complex Task Assignment

For complex task assignments, prepare the content JSON with all required fields and send using the `agent-messaging` skill:
- **Recipient**: `dev-agent-1`
- **Subject**: "Implement Auth GH-42"
- **Content**: JSON with `task_id`, `instructions`, `completion_criteria` (array), `test_requirements` (array), `report_back` (true)
- **Type**: `task`
- **Priority**: `high`

**Verify**: confirm message delivery in both cases.

---

## 2.3 Check Inbox

Check your inbox using the `agent-messaging` skill to retrieve all unread messages.

### List All Unread Messages

Use the `agent-messaging` skill to list all unread messages for your session.

### Example Output

```
Unread messages (3):
  1. msg-1767802409759-h3x4ajo from orchestrator-master: "GH-42 Task Assignment" (high)
  2. msg-1767802512345-abc1234 from reviewer-security: "Security Review Request" (normal)
  3. msg-1767802601234-xyz5678 from dev-agent-2: "Dependency Question" (low)
```

---

## 2.4 Read and Mark Message as Read

Use the `agent-messaging` skill to read a specific message by its ID and mark it as read.

### Example

Read message `msg-1767802409759-h3x4ajo` using the `agent-messaging` skill. This retrieves the full message content and marks it as read.

### Example Output

```
Message: msg-1767802409759-h3x4ajo
From: orchestrator-master
Subject: GH-42 Task Assignment
Priority: high
Sent: 2025-12-30T10:00:00Z

Content:
{
  "type": "task",
  "task_id": "GH-42",
  "instructions": "Implement user authentication with OAuth2 support",
  "completion_criteria": ["All tests pass", "PR created"],
  "report_back": true
}

[Message marked as read]
```

---

## 2.5 Workflow Example

### Complete Send-Receive-Respond Flow

**Step 1: Orchestrator sends task** using the `agent-messaging` skill:
- **Recipient**: `dev-agent-1`
- **Subject**: "GH-42 Implementation"
- **Content**: task assignment with `task_id`, `instructions`
- **Type**: `task`, **Priority**: `high`

**Step 2: Agent checks inbox** using the `agent-messaging` skill to list unread messages.

**Step 3: Agent reads message** using the `agent-messaging` skill with the specific message ID. This displays full content and marks it as read.

**Step 4: Agent sends acknowledgment** using the `agent-messaging` skill:
- **Recipient**: `orchestrator-master`
- **Subject**: "ACK: GH-42"
- **Content**: acknowledgment with `task_id`, `understood` (true), `estimated_completion`
- **Type**: `ack`, **Priority**: `normal`

**Verify**: confirm each step completes successfully.

---

## Related Sections

- [Part 1: API and Schema](messaging-protocol-part1-api-schema.md) - Message format details
- [Part 3: Message Types](messaging-protocol-part3-message-types.md) - Content schemas for each message type
- [Part 5: Response Expectations](messaging-protocol-part5-notifications-responses.md) - What responses are expected
