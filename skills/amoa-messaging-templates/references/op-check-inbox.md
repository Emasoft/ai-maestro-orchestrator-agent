# Operation: Check AI Maestro Inbox

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-check-inbox
---

## Purpose

Check for unread messages in your AI Maestro inbox.

## When to Use

- At start of any workflow to check for pending messages
- After delegating tasks to check for responses
- Periodically during long-running operations
- When notification banner appears

## Prerequisites

- AI Maestro messaging system (AMP) running
- `$SESSION_NAME` environment variable set (or known agent name)

## Steps

1. **Check your inbox** using the `agent-messaging` skill to retrieve all unread messages for your session.

2. **Process messages by priority**: URGENT > HIGH > NORMAL

3. **Respond to messages** that require acknowledgment using the `agent-messaging` skill.

4. **Mark messages as read** after processing using the `agent-messaging` skill.

**Verify**: confirm all unread messages have been processed.

## Output

JSON array of messages with fields:
- `from`: Sender agent name
- `subject`: Message subject
- `priority`: Message priority level
- `content.type`: Message type
- `content.message`: Message body
- `timestamp`: When message was sent

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Empty result | No unread messages | Continue with workflow |
| Connection refused | AI Maestro offline | Start AI Maestro service |
| Agent not found | Invalid session name | Verify $SESSION_NAME |

## Example

Check your inbox using the `agent-messaging` skill:
- **Retrieve unread messages**: list all unread messages for session `eoa-main`
- **Get unread count**: query the unread count for session `eoa-main`

**Verify**: confirm messages were retrieved successfully.

## Critical Rule

When unread messages exist, STOP current work and process them first. Messages may contain corrections, bug reports, or blocking issues.
