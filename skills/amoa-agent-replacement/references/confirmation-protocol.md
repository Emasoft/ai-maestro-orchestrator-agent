# Confirmation Protocol Reference

## Contents

- [6.1 ACK Verification](#61-ack-verification)
- [6.2 State File Updates](#62-state-file-updates)
- [6.3 ECOS Notification](#63-ecos-notification)
- [6.4 Audit Logging](#64-audit-logging)

---

## 6.1 ACK Verification

### Verification Checklist

Before considering replacement complete, verify:

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| ACK received | AI Maestro inbox | Message with matching handoff_id |
| Handoff ID matches | Compare fields | ACK handoff_id == sent handoff_id |
| Understanding accurate | Review summary | Summary matches task description |
| Checkpoint correct | Review starting_from | Matches documented checkpoint |
| Questions answered | Review questions | All questions addressed (or none) |
| Environment ready | Review status | status == "ready_to_proceed" |

### ACK Validation Script

```bash
#!/bin/bash
# validate_handoff_ack.sh

HANDOFF_ID="$1"
EXPECTED_CHECKPOINT="$2"

# Fetch ACK message
# Use the agent-messaging skill to check your inbox for unread messages,
# then filter for the message whose content.handoff_id matches $HANDOFF_ID
ACK=$(# retrieve unread messages and filter by handoff_id)

if [ -z "$ACK" ]; then
  echo "ERROR: No ACK received for handoff $HANDOFF_ID"
  exit 1
fi

# Validate fields
ACK_STATUS=$(echo "$ACK" | jq -r '.content.status')
ACK_CHECKPOINT=$(echo "$ACK" | jq -r '.content.starting_from')

if [ "$ACK_STATUS" != "ready_to_proceed" ]; then
  echo "WARNING: Agent status is $ACK_STATUS, not ready_to_proceed"
  exit 2
fi

if [ "$ACK_CHECKPOINT" != "$EXPECTED_CHECKPOINT" ]; then
  echo "WARNING: Agent checkpoint '$ACK_CHECKPOINT' differs from expected '$EXPECTED_CHECKPOINT'"
  exit 3
fi

echo "ACK validated successfully"
exit 0
```

### Handling ACK Discrepancies

| Discrepancy | Action |
|-------------|--------|
| Wrong handoff_id | Request correct ACK |
| Incorrect understanding | Clarify requirements |
| Wrong checkpoint | Correct and confirm |
| Questions present | Answer before proceeding |
| Status not ready | Resolve blockers |

---

## 6.2 State File Updates

### Required State Updates

Update the orchestrator state file with:

```yaml
# Update assignment record
active_assignments:
  - agent: "implementer-2"          # Updated from implementer-1
    agent_type: "ai"
    session: "helper-agent-2"       # New session
    module: "auth-core"
    github_issue: "#42"
    task_uuid: "task-uuid-12345"    # PRESERVE original UUID
    status: "pending_verification"  # Reset status

    # Add replacement tracking
    replacement_info:
      replaced_agent: "implementer-1"
      replaced_session: "helper-agent-generic"
      replacement_reason: "context_loss"
      replacement_timestamp: "2026-01-31T14:30:00Z"
      handoff_id: "handoff-uuid-123"
      handoff_url: "https://github.com/owner/repo/issues/42#issuecomment-123456"

    # Reset instruction verification
    instruction_verification:
      status: "awaiting_repetition"
      attempts: 0
      last_attempt: null
      verified_at: null

    # Preserve progress info for continuity
    progress:
      percentage: 60               # Preserve last known
      at_replacement: true         # Flag this is inherited
      last_update: "2026-01-31T14:00:00Z"
      notes: "Inherited from implementer-1"

# Update agent registry
registered_agents:
  # Mark failed agent as inactive
  - id: "implementer-1"
    type: "ai"
    session: "helper-agent-generic"
    status: "inactive"             # Changed from active
    inactive_reason: "replaced"
    replaced_at: "2026-01-31T14:30:00Z"
    replaced_by: "implementer-2"

  # Ensure replacement agent is registered
  - id: "implementer-2"
    type: "ai"
    session: "helper-agent-2"
    status: "active"
    registered: "2026-01-31T14:30:00Z"
    assigned_from: "implementer-1"

# Add to replacement history
replacement_history:
  - timestamp: "2026-01-31T14:30:00Z"
    failed_agent: "implementer-1"
    replacement_agent: "implementer-2"
    reason: "context_loss"
    tasks_transferred: ["task-uuid-12345"]
    handoff_id: "handoff-uuid-123"
    status: "complete"
```

### State Update Script

```bash
#!/bin/bash
# update_state_for_replacement.sh

STATE_FILE="$CLAUDE_PROJECT_DIR/design/state.yaml"
FAILED_AGENT="$1"
NEW_AGENT="$2"
NEW_SESSION="$3"
REASON="$4"
HANDOFF_ID="$5"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Backup state file
cp "$STATE_FILE" "$STATE_FILE.bak.$(date +%s)"

# Update assignment agent
yq -i "(.active_assignments[] | select(.agent == \"$FAILED_AGENT\")).agent = \"$NEW_AGENT\"" "$STATE_FILE"
yq -i "(.active_assignments[] | select(.agent == \"$NEW_AGENT\")).session = \"$NEW_SESSION\"" "$STATE_FILE"
yq -i "(.active_assignments[] | select(.agent == \"$NEW_AGENT\")).status = \"pending_verification\"" "$STATE_FILE"

# Add replacement info
yq -i "(.active_assignments[] | select(.agent == \"$NEW_AGENT\")).replacement_info = {
  \"replaced_agent\": \"$FAILED_AGENT\",
  \"replacement_reason\": \"$REASON\",
  \"replacement_timestamp\": \"$TIMESTAMP\",
  \"handoff_id\": \"$HANDOFF_ID\"
}" "$STATE_FILE"

# Reset instruction verification
yq -i "(.active_assignments[] | select(.agent == \"$NEW_AGENT\")).instruction_verification.status = \"awaiting_repetition\"" "$STATE_FILE"

# Mark old agent inactive
yq -i "(.registered_agents[] | select(.id == \"$FAILED_AGENT\")).status = \"inactive\"" "$STATE_FILE"
yq -i "(.registered_agents[] | select(.id == \"$FAILED_AGENT\")).replaced_by = \"$NEW_AGENT\"" "$STATE_FILE"

echo "State file updated successfully"
```

---

## 6.3 ECOS Notification

### Success Notification

Send to ECOS when replacement is complete:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA] Agent Replacement Complete",
  "priority": "normal",
  "content": {
    "type": "replacement_confirmation",
    "message": "Agent replacement completed successfully",
    "status": "success",
    "failed_agent": {
      "id": "implementer-1",
      "session": "helper-agent-generic"
    },
    "replacement_agent": {
      "id": "implementer-2",
      "session": "helper-agent-2"
    },
    "details": {
      "tasks_reassigned": 1,
      "tasks_uuids": ["task-uuid-12345"],
      "github_issues_updated": ["#42"],
      "handoff_id": "handoff-uuid-123",
      "handoff_url": "https://github.com/owner/repo/issues/42#issuecomment-123456",
      "ack_received_at": "2026-01-31T14:35:00Z",
      "total_time": "5 minutes"
    }
  }
}
```

### Partial Success Notification

If some tasks could not be reassigned:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA] Agent Replacement Partially Complete",
  "priority": "high",
  "content": {
    "type": "replacement_confirmation",
    "message": "Agent replacement partially completed",
    "status": "partial",
    "failed_agent": {
      "id": "implementer-1"
    },
    "replacement_agent": {
      "id": "implementer-2"
    },
    "details": {
      "tasks_reassigned": 1,
      "tasks_failed": 1,
      "failed_tasks": [{
        "uuid": "task-uuid-67890",
        "reason": "GitHub API rate limit exceeded"
      }],
      "action_required": "manual_reassignment_needed"
    }
  }
}
```

### Failure Notification

If replacement could not be completed:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "ecos-controller",
  "subject": "[EOA] Agent Replacement Failed",
  "priority": "urgent",
  "content": {
    "type": "replacement_confirmation",
    "message": "Agent replacement failed",
    "status": "failed",
    "failed_agent": {
      "id": "implementer-1"
    },
    "replacement_agent": {
      "id": "implementer-2"
    },
    "error": {
      "code": "NO_ACK_RECEIVED",
      "message": "Replacement agent did not acknowledge handoff after 3 attempts",
      "reminders_sent": 3,
      "last_attempt": "2026-01-31T14:45:00Z"
    },
    "action_required": "provide_alternative_agent"
  }
}
```

---

## 6.4 Audit Logging

### Audit Log Entry Format

```yaml
# Append to: $CLAUDE_PROJECT_DIR/logs/replacement_audit.yaml

- timestamp: "2026-01-31T14:30:00Z"
  event: "agent_replacement"
  orchestrator: "orchestrator-master"

  ecos_notification:
    received_at: "2026-01-31T14:25:00Z"
    notification_id: "ecos-notif-uuid"
    urgency: "immediate"

  failed_agent:
    id: "implementer-1"
    session: "helper-agent-generic"
    reason: "context_loss"
    tasks_assigned: ["task-uuid-12345"]
    last_known_progress: 60

  replacement_agent:
    id: "implementer-2"
    session: "helper-agent-2"

  handoff:
    id: "handoff-uuid-123"
    url: "https://github.com/owner/repo/issues/42#issuecomment-123456"
    generated_at: "2026-01-31T14:28:00Z"
    size_bytes: 15234

  github:
    issues_updated: ["#42"]
    labels_changed: ["assigned:implementer-1 -> assigned:implementer-2"]
    comments_added: ["#42 issuecomment-123456"]

  ack:
    received_at: "2026-01-31T14:35:00Z"
    status: "ready_to_proceed"
    understanding_verified: true

  ecos_confirmation:
    sent_at: "2026-01-31T14:36:00Z"
    status: "success"

  total_duration: "11 minutes"
  outcome: "success"
```

### Log Rotation

Maintain audit logs with rotation:

```bash
#!/bin/bash
# rotate_audit_logs.sh

LOG_DIR="$CLAUDE_PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/replacement_audit.yaml"
MAX_SIZE=$((10 * 1024 * 1024))  # 10MB

if [ -f "$LOG_FILE" ]; then
  SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat --format=%s "$LOG_FILE")
  if [ "$SIZE" -gt "$MAX_SIZE" ]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    mv "$LOG_FILE" "$LOG_FILE.$TIMESTAMP"
    gzip "$LOG_FILE.$TIMESTAMP"
  fi
fi
```

### Audit Report Generation

Generate replacement audit report:

```bash
#!/bin/bash
# generate_replacement_report.sh

LOG_FILE="$CLAUDE_PROJECT_DIR/logs/replacement_audit.yaml"

echo "# Agent Replacement Audit Report"
echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Count replacements
TOTAL=$(yq 'length' "$LOG_FILE")
SUCCESS=$(yq '[.[] | select(.outcome == "success")] | length' "$LOG_FILE")
FAILED=$(yq '[.[] | select(.outcome == "failed")] | length' "$LOG_FILE")

echo "## Summary"
echo "- Total replacements: $TOTAL"
echo "- Successful: $SUCCESS"
echo "- Failed: $FAILED"
echo ""

echo "## Recent Replacements"
yq '.[-10:] | .[] | "- " + .timestamp + ": " + .failed_agent.id + " -> " + .replacement_agent.id + " (" + .outcome + ")"' "$LOG_FILE"
```

---

## Final Confirmation Checklist

Complete checklist before marking replacement done:

```markdown
## Replacement Confirmation Checklist

### ACK Verification
- [ ] ACK message received
- [ ] Handoff ID matches
- [ ] Understanding summary accurate
- [ ] Checkpoint matches documented
- [ ] Status is "ready_to_proceed"
- [ ] All questions answered

### State Updates
- [ ] Assignment record updated
- [ ] Agent ID changed to replacement
- [ ] Session updated
- [ ] Status set to pending_verification
- [ ] Replacement info added
- [ ] Instruction verification reset
- [ ] Progress preserved with flag
- [ ] Failed agent marked inactive
- [ ] Replacement agent registered

### GitHub Updates
- [ ] Issue assignee updated
- [ ] Labels updated
- [ ] Audit comment added
- [ ] PR assignee updated (if applicable)

### ECOS Notification
- [ ] Confirmation message sent
- [ ] Status correctly reported
- [ ] All task UUIDs listed
- [ ] Handoff URL included

### Audit Logging
- [ ] Audit log entry created
- [ ] All timestamps recorded
- [ ] Outcome documented
```

---

## Decision Trees for Confirmation Outcomes

### Confirmation Outcome Decision Tree

```
Replacement agent confirmation check completed
├─ Did replacement agent pass all confirmation criteria?
│   ├─ Full pass (all criteria met)
│   │   → Send confirmation success to ECOS
│   │   → Mark replacement as permanent
│   │   → Resume normal task monitoring
│   │
│   ├─ Partial pass (some criteria met, minor gaps)
│   │   → Are gaps addressable with a quick fix?
│   │   ├─ Yes → Send targeted fix instructions to replacement agent
│   │   │         → Re-run confirmation after fix → If pass, proceed as full pass
│   │   └─ No → Escalate to ECOS with gap details
│   │           → ECOS decides: accept partial / spawn another replacement
│   │
│   └─ Fail (critical criteria not met)
│       → Notify ECOS: replacement agent inadequate
│       → Include: which criteria failed, agent's response quality, recommendation
│       → ECOS options: try different agent / simplify task / escalate to EAA
```

### ECOS Confirmation Notification Template

```json
{
  "to": "<ecos-session-name>",
  "subject": "Replacement Agent Confirmation Result — Task <task_id>",
  "priority": "high",
  "content": {
    "type": "report",
    "message": "Replacement agent confirmation check completed.",
    "data": {
      "task_id": "<task-id>",
      "replacement_agent": "<agent-session-name>",
      "result": "FULL_PASS | PARTIAL_PASS | FAIL",
      "criteria_results": {
        "task_understanding": "pass | fail",
        "toolchain_access": "pass | fail",
        "handoff_comprehension": "pass | fail",
        "initial_progress": "pass | fail"
      },
      "gaps": ["<description of any gaps>"],
      "recommendation": "<EOA's recommended next action>"
    }
  }
}
```

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
