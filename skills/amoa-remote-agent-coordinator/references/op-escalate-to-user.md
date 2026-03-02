---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: escalate-to-user
---

# Operation: Escalate to User


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Escalation Categories](#escalation-categories)
- [Steps](#steps)
  - [Step 1: Prepare Escalation Message](#step-1-prepare-escalation-message)
  - [Step 2: Send to EAMA (User Communication Channel)](#step-2-send-to-eama-user-communication-channel)
  - [Step 3: Update Blocked Task (if applicable)](#step-3-update-blocked-task-if-applicable)
  - [Step 4: Queue Management](#step-4-queue-management)
- [Escalation Message Template](#escalation-message-template)
- [User Decision Required](#user-decision-required)
  - [Context](#context)
  - [Decision Needed](#decision-needed)
  - [Options](#options)
  - [Recommendation](#recommendation)
  - [Impact](#impact)
- [Escalation Levels](#escalation-levels)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Tracking Resolution](#tracking-resolution)
- [Related Operations](#related-operations)

## Purpose

Escalate decisions to the user when they exceed orchestrator authority (architecture, security, requirement changes).

## When to Use

- Architecture decisions not covered by methodology
- Security vulnerabilities discovered
- Dependency conflicts requiring user choice
- Test failures suggesting specification issues
- Requirement clarifications needed
- Breaking changes proposed

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| escalation_type | Category of escalation | Yes |
| context | Relevant background | Yes |
| options | Possible decisions (if applicable) | No |
| urgency | Priority level | Yes |
| blocking_task | Task blocked by this decision | No |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| escalation_id | String | Tracking ID for follow-up |
| user_notified | Boolean | Confirmation of notification |
| queue_position | Integer | Position in escalation queue |

## Escalation Categories

| Category | Examples | Urgency Default |
|----------|----------|-----------------|
| Architecture | Design pattern choice, module boundaries | Normal |
| Security | Vulnerability, credentials handling | Urgent |
| Requirements | Ambiguous spec, conflicting requirements | High |
| Dependencies | Version conflicts, breaking updates | Normal |
| Scope | Feature creep, out-of-scope requests | Normal |
| Blockers | External dependencies, access issues | High |

## Steps

### Step 1: Prepare Escalation Message

```bash
ESCALATION_ID="esc-$(date +%Y%m%d%H%M%S)-$RANDOM"

# Create escalation record
cat > "escalation_${ESCALATION_ID}.json" << EOF
{
  "id": "$ESCALATION_ID",
  "type": "$ESCALATION_TYPE",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "context": "$CONTEXT",
  "options": $OPTIONS_JSON,
  "urgency": "$URGENCY",
  "blocking_task": "$BLOCKING_TASK",
  "status": "pending"
}
EOF
```

### Step 2: Send to EAMA (User Communication Channel)

Send an escalation message to EAMA using the `agent-messaging` skill:
- **Recipient**: `eama-main`
- **Subject**: "[ESCALATION] [escalation_type]: [brief_description]"
- **Content**: "User decision required." followed by category, context, options, impact (blocking task), and urgency
- **Type**: `escalation`
- **Priority**: the urgency level
- **Data**: include `escalation_id`, `type`, `blocking_task`, `options`

**Verify**: confirm message delivery.

### Step 3: Update Blocked Task (if applicable)

```bash
if [ -n "$BLOCKING_TASK" ]; then
  # Mark task as blocked
  gh issue edit $BLOCKING_TASK --add-label "status:blocked"
  gh issue edit $BLOCKING_TASK --add-label "blocked:user-decision"

  # Add escalation reference
  gh issue comment $BLOCKING_TASK --body "Blocked pending user decision. Escalation ID: $ESCALATION_ID. Category: $ESCALATION_TYPE"
fi
```

### Step 4: Queue Management

```bash
# Add to escalation queue
echo "$ESCALATION_ID|$ESCALATION_TYPE|$URGENCY|$(date -u +%Y-%m-%dT%H:%M:%SZ)|pending" >> escalation_queue.txt

# Get queue position
QUEUE_POSITION=$(grep -n "pending" escalation_queue.txt | wc -l)
echo "Queue position: $QUEUE_POSITION"
```

## Escalation Message Template

```markdown
## User Decision Required

**Escalation ID**: [ID]
**Category**: [Architecture/Security/Requirements/Dependencies/Scope/Blockers]
**Urgency**: [Normal/High/Urgent]

### Context
[Background information explaining the situation]

### Decision Needed
[Clear statement of what decision is needed]

### Options
1. **Option A**: [Description]
   - Pros: [...]
   - Cons: [...]

2. **Option B**: [Description]
   - Pros: [...]
   - Cons: [...]

### Recommendation
[Orchestrator's recommendation if appropriate, or "No recommendation - requires user judgment"]

### Impact
- Blocking task: #[number] (or "None")
- Affected agents: [list]
- Timeline impact: [description]
```

## Escalation Levels

| Level | Who Handles | Examples |
|-------|-------------|----------|
| Level 0 | Orchestrator | Routine decisions within methodology |
| Level 1 | EAMA (User) | Architecture, requirements, scope |
| Level 2 | User (Direct) | Security, breaking changes, major decisions |

## Success Criteria

- [ ] Escalation ID generated
- [ ] Message sent to EAMA
- [ ] Blocked task updated (if applicable)
- [ ] Queue position recorded
- [ ] Audit log entry created

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| EAMA unreachable | Agent offline | Queue escalation, retry |
| User unavailable | After hours | Queue with urgency flag |
| Duplicate escalation | Same issue raised twice | Dedupe by context hash |

## Tracking Resolution

When user responds:

```bash
# Update escalation status
DECISION="$USER_DECISION"
jq '.status = "resolved" | .decision = "'"$DECISION"'" | .resolved_at = "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"' \
  "escalation_${ESCALATION_ID}.json" > tmp.json && mv tmp.json "escalation_${ESCALATION_ID}.json"

# Unblock task
if [ -n "$BLOCKING_TASK" ]; then
  gh issue edit $BLOCKING_TASK --remove-label "status:blocked"
  gh issue edit $BLOCKING_TASK --remove-label "blocked:user-decision"
  gh issue edit $BLOCKING_TASK --add-label "status:in-progress"
  gh issue comment $BLOCKING_TASK --body "Unblocked. User decision: $DECISION"
fi

# Notify assigned agent
Send a decision notification to the assigned agent using the `agent-messaging` skill:
- **Recipient**: the assigned agent session name
- **Subject**: "Decision Made: [escalation_id]"
- **Content**: "User has made a decision on your blocked task. Decision: [decision]. You may now proceed with task #[blocking_task]."
- **Type**: `decision`
- **Priority**: `high`
- **Data**: include `escalation_id`, `decision`, `task_id`

**Verify**: confirm message delivery.
```

## Related Operations

- op-handle-blocker-report (in progress-monitoring skill)
- op-poll-agent-progress
