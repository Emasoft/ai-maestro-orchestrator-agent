---
procedure: support-skill
workflow-instruction: support
---

# Operation: Send Handoff to New Agent


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Upload Handoff to GitHub](#step-1-upload-handoff-to-github)
  - [Step 2: Get Handoff URL](#step-2-get-handoff-url)
  - [Step 3: Send AI Maestro Notification](#step-3-send-ai-maestro-notification)
  - [Step 4: Include Urgency and Timeout](#step-4-include-urgency-and-timeout)
  - [Step 5: Request Acknowledgment](#step-5-request-acknowledgment)
- [Required Response](#required-response)
  - [Step 6: Set ACK Timeout Monitor](#step-6-set-ack-timeout-monitor)
  - [Step 7: Handle Missing ACK](#step-7-handle-missing-ack)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation after kanban tasks are reassigned to deliver the handoff document to the replacement agent.

## Prerequisites

- Handoff document generated (op-generate-handoff-document)
- Kanban tasks reassigned (op-reassign-kanban-tasks)
- Replacement agent session active
- AI Maestro accessible

## Procedure

### Step 1: Upload Handoff to GitHub

```bash
# Option A: Add to GitHub issue as comment
gh issue comment <PRIMARY_ISSUE_NUM> --body "$(cat handoff-document.md)"

# Option B: Add to dedicated handoff issue
gh issue create \
  --title "Handoff: $FAILED_AGENT -> $REPLACEMENT_AGENT" \
  --body "$(cat handoff-document.md)" \
  --label "type:handoff,assign:$REPLACEMENT_AGENT"

# Option C: Add to repository file
cp handoff-document.md docs/handoffs/handoff-$FAILED_AGENT-$REPLACEMENT_AGENT-$(date +%Y%m%d).md
git add docs/handoffs/
git commit -m "Add handoff document for $REPLACEMENT_AGENT"
git push
```

### Step 2: Get Handoff URL

```bash
# If using issue comment, get URL
HANDOFF_URL=$(gh issue view <ISSUE_NUM> --json url --jq '.url')

# If using file, get raw URL
HANDOFF_URL="https://github.com/<OWNER>/<REPO>/blob/main/docs/handoffs/handoff-*.md"
```

### Step 3: Send AI Maestro Notification

Send the handoff notification using the `agent-messaging` skill:
- **Recipient**: the replacement agent session name
- **Subject**: "URGENT: Task Handoff from <FAILED_AGENT>"
- **Content**: "You are receiving tasks from <FAILED_AGENT> due to <FAILURE_REASON>. Please review the handoff document and acknowledge receipt."
- **Type**: `task_handoff`, **Priority**: `urgent`
- **Data**: include `handoff_url`, `failed_agent`, `tasks` list, `ack_required: true`, `ack_timeout_minutes: 30`

**Verify**: confirm message delivery and note the message ID for tracking.

### Step 4: Include Urgency and Timeout

| Urgency Level | Timeout | Action if No ACK |
|---------------|---------|------------------|
| immediate | 15 minutes | Escalate to user |
| high | 30 minutes | Retry notification |
| normal | 60 minutes | Queue for retry |

### Step 5: Request Acknowledgment

The handoff message should explicitly request:

```markdown
## Required Response

Please respond with:
1. **ACK** - Confirm you received and read the handoff
2. **UNDERSTOOD** - Confirm you understand the tasks
3. **QUESTIONS** - List any questions or clarifications needed
4. **ETA** - Estimated time to resume work

Reply format:
```
ACK: Handoff received
UNDERSTOOD: Tasks #42 and #45 clear
QUESTIONS: None / [list questions]
ETA: Will resume within 30 minutes
```
```

### Step 6: Set ACK Timeout Monitor

```bash
# Record handoff send time
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) HANDOFF_SENT to=$REPLACEMENT_AGENT" >> orchestrator.log

# Set timeout alarm (external monitoring)
# After timeout, check for ACK and escalate if missing
```

### Step 7: Handle Missing ACK

If no ACK within timeout:

Send a retry reminder using the `agent-messaging` skill:
- **Recipient**: the replacement agent session name
- **Subject**: "REMINDER: Task Handoff Acknowledgment Needed"
- **Content**: "Please acknowledge the task handoff sent at <SEND_TIME>. Tasks are waiting."
- **Type**: `ack_reminder`, **Priority**: `urgent`
- **Data**: include `original_handoff_url`

**Verify**: confirm message delivery.

If still no response, escalate to user:
```bash
gh issue comment <ISSUE_NUM> --body "@USER: Replacement agent $REPLACEMENT_AGENT has not acknowledged handoff. Manual intervention may be needed."
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Handoff URL | String | URL to handoff document |
| Message Sent | Boolean | Whether AI Maestro message sent |
| ACK Timeout | Timestamp | When ACK is expected |
| Notification ID | String | AI Maestro message ID for tracking |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Upload failed | GitHub API error | Retry or use alternative method |
| AI Maestro unreachable | Service down | Restart service or use backup |
| Agent session not found | Session ended | Request new session from ECOS |
| ACK timeout | Agent unresponsive | Escalate to user |

## Example

```bash
#!/bin/bash
# Complete handoff delivery

FAILED_AGENT="implementer-1"
REPLACEMENT_AGENT="implementer-2"
REPLACEMENT_SESSION="helper-agent-generic"
FAILURE_REASON="context_loss"
HANDOFF_FILE="handoff-document.md"
PRIMARY_ISSUE=42

# 1. Upload to GitHub issue
echo "Uploading handoff to issue #$PRIMARY_ISSUE..."
gh issue comment "$PRIMARY_ISSUE" --body "$(cat $HANDOFF_FILE)"
HANDOFF_URL=$(gh issue view "$PRIMARY_ISSUE" --json url --jq '.url')

# 2. Send AI Maestro notification
echo "Sending notification to $REPLACEMENT_SESSION..."
# Use the agent-messaging skill to send the handoff notification:
# - Recipient: $REPLACEMENT_SESSION
# - Subject: "URGENT: Task Handoff from $FAILED_AGENT"
# - Content: "You are receiving tasks from $FAILED_AGENT. Review handoff at: $HANDOFF_URL"
# - Type: task_handoff, Priority: urgent
# - Data: handoff_url, failed_agent, ack_required: true, ack_timeout_minutes: 30
# Verify: confirm delivery and capture message ID

# 3. Log for timeout tracking
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) HANDOFF_SENT msg_id=$MSG_ID to=$REPLACEMENT_SESSION" >> orchestrator.log

echo "Handoff delivery complete. Awaiting ACK within 30 minutes."
```

## Checklist

- [ ] Upload handoff document to GitHub
- [ ] Get URL for handoff document
- [ ] Send AI Maestro notification to replacement agent using the `agent-messaging` skill
- [ ] Include urgency level
- [ ] Specify ACK requirements
- [ ] Set ACK timeout
- [ ] Log handoff send time
- [ ] Monitor for ACK response
- [ ] Handle timeout if no ACK
