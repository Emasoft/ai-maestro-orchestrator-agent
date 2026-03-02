# Operation: Send AI Maestro Message

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-send-message
---

## Purpose

Send a message to another agent via AI Maestro messaging system.

## When to Use

- Assigning tasks to remote agents
- Requesting status updates
- Sending integration/review requests
- Escalating issues
- Acknowledging received messages

## Prerequisites

- AI Maestro messaging system (AMP) running
- Valid sender and recipient agent names
- JSON payload prepared

## Steps

1. **Prepare the message payload** with required fields:
   - `from`: Your agent session name
   - `to`: Recipient agent session name (full name, e.g., `libs-svg-svgbbox`)
   - `subject`: Short subject line
   - `priority`: `high`, `normal`, or `low`
   - `content`: Object with `type` and `message` fields

2. **Send the message** using the `agent-messaging` skill with the prepared payload.

3. **Verify**: confirm the response indicates successful delivery (status "sent" with a message ID).

4. **Log the message** in delegation/coordination log

## Output

| Field | Type | Description |
|-------|------|-------------|
| status | string | "sent" on success |
| message_id | string | Unique message identifier |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | AI Maestro offline | Start AI Maestro service |
| Agent not found | Invalid recipient name | Verify agent session name |
| Invalid JSON | Malformed payload | Validate JSON syntax |

## Example

Send a review request message using the `agent-messaging` skill:
- **Recipient**: `eia-main`
- **Subject**: "PR #123 Review Request"
- **Content**: "Please review PR #123 for code quality and CI compliance."
- **Type**: `request`
- **Priority**: `high`

**Verify**: confirm message delivery.
