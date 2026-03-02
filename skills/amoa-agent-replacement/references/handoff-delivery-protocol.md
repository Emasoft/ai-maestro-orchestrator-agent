# Handoff Delivery Protocol Reference

## Contents

- [5.1 Document Upload](#51-document-upload)
- [5.2 AI Maestro Notification](#52-ai-maestro-notification)
- [5.3 ACK Requirements](#53-ack-requirements)
- [5.4 Timeout Handling](#54-timeout-handling)

---

## 5.1 Document Upload

### Upload Location

Handoff documents MUST be uploaded to GitHub for persistence and accessibility.

**Primary Method: GitHub Issue Comment**

```bash
ISSUE_NUMBER=42
HANDOFF_FILE="replacement-handoff-implementer-1-to-implementer-2.md"

# Read handoff content
HANDOFF_CONTENT=$(cat "$HANDOFF_FILE")

# Upload as issue comment
gh issue comment "$ISSUE_NUMBER" --body "$HANDOFF_CONTENT"
```

**Alternative: GitHub Gist (for large handoffs)**

```bash
# Create secret gist
gh gist create "$HANDOFF_FILE" --desc "Agent replacement handoff: implementer-1 to implementer-2"

# Get gist URL
GIST_URL=$(gh gist list --limit 1 --json url --jq '.[0].url')
```

### File Naming Convention

```
replacement-handoff-{failed-agent}-to-{new-agent}-{timestamp}.md
```

Example: `replacement-handoff-implementer-1-to-implementer-2-20260131T143000Z.md`

### Local Backup

Always save a local copy before upload:

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/docs_dev/handoffs"
mkdir -p "$HANDOFF_DIR"

cp "$HANDOFF_FILE" "$HANDOFF_DIR/"
```

---

## 5.2 AI Maestro Notification

### Message Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{REPLACEMENT_AGENT_SESSION}}",
  "subject": "[HANDOFF] Agent Replacement - You are replacing {{FAILED_AGENT}}",
  "priority": "urgent",
  "content": {
    "type": "replacement_handoff",
    "message": "You are replacing {{FAILED_AGENT}} due to {{FAILURE_REASON}}. Full handoff document with all context is available at the URL below. Please ACK within 5 minutes and confirm you understand the requirements.",
    "handoff_id": "{{HANDOFF_UUID}}",
    "handoff_url": "{{GITHUB_URL}}",
    "failed_agent": {
      "id": "{{FAILED_AGENT_ID}}",
      "session": "{{FAILED_AGENT_SESSION}}"
    },
    "tasks": {{TASK_LIST_JSON}},
    "urgency": "{{URGENCY_LEVEL}}",
    "ack_required_within": "5 minutes"
  }
}
```

### Send Notification

Send using the `agent-messaging` skill:
- **Recipient**: `helper-agent-2`
- **Subject**: "[HANDOFF] Agent Replacement - You are replacing implementer-1"
- **Content**: "You are replacing implementer-1 due to context_loss. Full handoff: <HANDOFF_URL>"
- **Type**: `replacement_handoff`, **Priority**: `urgent`
- **Data**: include `handoff_id`, `handoff_url`, `failed_agent` (id and session), `tasks` list, `urgency: immediate`, `ack_required_within: 5 minutes`

**Verify**: confirm message delivery.

### Message Priority

| Urgency | Priority | Timeout |
|---------|----------|---------|
| `immediate` | `urgent` | 5 minutes |
| `prepare` | `high` | 15 minutes |
| `when_available` | `normal` | 30 minutes |

---

## 5.3 ACK Requirements

### Expected ACK Format

The replacement agent MUST respond with:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{ORCHESTRATOR_SESSION}}",
  "subject": "[ACK] Handoff {{HANDOFF_ID}} Received",
  "priority": "high",
  "content": {
    "type": "handoff_ack",
    "message": "Handoff received and reviewed",
    "handoff_id": "{{HANDOFF_ID}}",
    "understanding": "{{ONE_LINE_TASK_SUMMARY}}",
    "starting_from": "{{CONTINUATION_POINT}}",
    "questions": {{QUESTIONS_ARRAY}},
    "status": "ready_to_proceed"
  }
}
```

### ACK Status Values

| Status | Meaning | Orchestrator Action |
|--------|---------|---------------------|
| `ready_to_proceed` | Understood, will begin | Mark handoff complete |
| `needs_clarification` | Questions before starting | Answer questions |
| `environment_issue` | Cannot set up environment | Help resolve |
| `rejected` | Cannot accept task | Find alternative agent |

### Required ACK Content

The ACK MUST include:

| Field | Purpose | Verification |
|-------|---------|--------------|
| `handoff_id` | Match to original | Must match sent ID |
| `understanding` | Verify comprehension | Must match task description |
| `starting_from` | Confirm checkpoint | Must match documented checkpoint |
| `questions` | Surface gaps | Must address before authorizing |

### Handling Questions in ACK

If replacement agent has questions:

1. **ANSWER** all questions immediately
2. **UPDATE** handoff document if needed
3. **RE-SEND** notification with updated URL
4. **WAIT** for confirmation ACK

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{REPLACEMENT_AGENT_SESSION}}",
  "subject": "[CLARIFICATION] Re: Handoff {{HANDOFF_ID}}",
  "priority": "high",
  "content": {
    "type": "handoff_clarification",
    "message": "Answers to your questions about the handoff",
    "handoff_id": "{{HANDOFF_ID}}",
    "clarifications": [
      {
        "question": "Which JWT library should I use?",
        "answer": "Use PyJWT version 2.8.0, already in requirements.txt"
      }
    ],
    "updated_handoff_url": "{{URL_IF_UPDATED}}"
  }
}
```

---

## 5.4 Timeout Handling

### ACK Timeout Workflow

```
Send Handoff
    ↓
Wait for ACK (timeout period based on urgency)
    ↓
[ACK Received?]
    ├─ Yes → Process ACK, continue
    └─ No → Send Reminder
              ↓
         Wait again (1/2 original timeout)
              ↓
         [ACK Received?]
              ├─ Yes → Process ACK, continue
              └─ No → Send Final Reminder
                        ↓
                   Wait again (1/2 timeout)
                        ↓
                   [ACK Received?]
                        ├─ Yes → Process ACK, continue
                        └─ No → Escalate to ECOS
```

### Reminder Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{REPLACEMENT_AGENT_SESSION}}",
  "subject": "[REMINDER] ACK Required for Handoff {{HANDOFF_ID}}",
  "priority": "urgent",
  "content": {
    "type": "handoff_reminder",
    "message": "You have not acknowledged the replacement handoff. Please ACK immediately or indicate if you cannot accept this task.",
    "handoff_id": "{{HANDOFF_ID}}",
    "original_sent": "{{ORIGINAL_TIMESTAMP}}",
    "reminder_number": 1,
    "final_deadline": "{{DEADLINE}}"
  }
}
```

### Escalation to ECOS

After 2 reminders with no response:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA-ESCALATE] Replacement Agent Not Responding",
  "priority": "urgent",
  "content": {
    "type": "escalation",
    "message": "Replacement agent has not acknowledged handoff after 2 reminders",
    "failed_agent": "implementer-1",
    "replacement_agent": "implementer-2",
    "handoff_id": "{{HANDOFF_ID}}",
    "reminders_sent": 2,
    "tasks_affected": ["task-uuid-1", "task-uuid-2"],
    "action_required": "provide_alternative_agent"
  }
}
```

### Manual Override

If orchestrator determines replacement agent is online but delayed:

```bash
# Force proceed with documented delay
STATE_UPDATE="replacement_status: acknowledged_with_delay"
```

---

## Delivery Checklist

Before marking delivery complete:

- [ ] Handoff document uploaded to GitHub
- [ ] Local backup saved
- [ ] AI Maestro message sent
- [ ] Message includes correct handoff URL
- [ ] Message includes all task UUIDs
- [ ] Urgency level matches ECOS notification
- [ ] ACK timeout timer started

After ACK received:

- [ ] ACK `handoff_id` matches
- [ ] `understanding` summary is accurate
- [ ] `starting_from` matches documented checkpoint
- [ ] All questions answered
- [ ] State file updated
- [ ] ECOS notified of successful handoff

---

## Troubleshooting

### AI Maestro Message Not Delivered

1. Use the `agent-messaging` skill to verify the replacement agent session exists in the agent registry.

2. Use the `agent-messaging` skill to perform a health check on the AI Maestro service.

3. Retry sending the notification using the `agent-messaging` skill with the full explicit session name.

### GitHub Upload Failed

1. Check GitHub CLI authentication:
   ```bash
   gh auth status
   ```

2. Verify issue exists:
   ```bash
   gh issue view $ISSUE_NUMBER
   ```

3. Fallback to gist:
   ```bash
   gh gist create "$HANDOFF_FILE"
   ```

### ACK Malformed

If ACK doesn't contain required fields:

1. Request proper ACK format
2. Provide ACK template in request
3. Accept partial ACK if agent confirms understanding verbally

---

---

## Decision Trees for Handoff Delivery

### Handoff Delivery Method Decision Tree

```
Handoff document compiled, ready to deliver to new agent
├─ What is the size of the handoff document?
│   ├─ Small (< 500 lines) → Deliver inline via AI Maestro message
│   │   → Include full document in message content.data.handoff_document field
│   │   → Fastest delivery, no external storage needed
│   │
│   ├─ Medium (500-2000 lines) → Create GitHub Gist
│   │   → Use `gh gist create` with handoff document
│   │   → Send AI Maestro message with gist URL in content.data.handoff_url
│   │   → Agent reads gist content directly
│   │
│   └─ Large (> 2000 lines) → Create GitHub Issue on project repo
│       → Attach handoff as issue body with structured sections
│       → Link issue to original task issue
│       → Send AI Maestro message with issue URL in content.data.handoff_url
│       → Agent reads issue content for full context
│
In all cases:
→ Wait for new agent ACK confirming handoff received and understood
→ If no ACK within 5 min → Retry delivery → If still no ACK → Escalate to ECOS
```

### New Agent Handoff ACK Template

```json
{
  "to": "<eoa-session-name>",
  "subject": "Handoff ACK — Task <task_id>",
  "priority": "high",
  "content": {
    "type": "ack",
    "message": "Handoff document received and reviewed.",
    "data": {
      "task_id": "<task-id>",
      "handoff_received": true,
      "understood_scope": "<agent's 1-sentence summary of what it needs to do>",
      "questions": ["<any clarifying questions, or empty array if none>"],
      "estimated_start": "immediate | <reason for delay>"
    }
  }
}
```

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
