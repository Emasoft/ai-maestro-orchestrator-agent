# Echo/Acknowledgment Protocol

## Contents

- [Message Types: Instructions vs Conversations](#message-types-instructions-vs-conversations)
- [When task acknowledgment is required](#when-task-acknowledgment-is-required)
- [If agent receives task normally](#if-agent-receives-task-normally)
- [If agent has questions about the task](#if-agent-has-questions-clarification-occurs)
- [If agent fails to acknowledge in time](#if-agent-fails-to-acknowledge-in-time)
- [If agent encounters resource or capability issues](#if-agent-encounters-resource-or-capability-issues)
- [During long task execution with checkpoints](#during-long-task-execution-with-checkpoints)
- [Proactive enforcement by orchestrator](#proactive-enforcement-by-orchestrator)
- [Message flow reference](#message-flow-reference)
- [Integration with other protocols](#integration-with-other-protocols)

## Purpose

Ensure remote agents receive and understand task instructions before beginning work. This protocol prevents silent failures and confirms task comprehension.

**CRITICAL PRINCIPLE**: Remote agents DO NOT have this skill. They do not know the ACK protocol unless the orchestrator TEACHES them. The orchestrator MUST:
1. Include ACK instructions IN EVERY task delegation message
2. Explain the exact format the agent should use
3. State that ACK is mandatory before work begins
4. Proactively request ACK if not received

The orchestrator cannot assume remote agents know anything about acknowledgment - it must be explicitly taught in each message.

---

## Message Types: Instructions vs Conversations

**NOT ALL MESSAGES REQUIRE ACKNOWLEDGMENT.** The protocol distinguishes between:

| Type | Description | Acknowledgment |
|------|-------------|----------------|
| **Task Delegation** | Explicit instructions with templates, checklists, acceptance criteria | **MANDATORY** |
| **Conversation** | Discussions, clarifications, Q&A, feedback | Not required |

### How to Identify Task Delegations

A message is a **Task Delegation** (requires ACK) if it contains ANY of:
- Task ID (e.g., `## Task: GH-42-feature`)
- Acceptance Criteria section
- Git Workflow section (branch, PR instructions)
- Verification Commands section
- Required Output Format section
- Checklist with `- [ ]` items
- Templates with placeholders to fill

### How to Identify Conversations

A message is a **Conversation** (no ACK needed) if it is:
- A clarifying question
- Feedback on previous work
- Discussion of approach options
- Back-and-forth technical discussion
- Status inquiry without new instructions
- General coordination without specific task

### Why This Distinction Matters

- **Task Delegations** need ACK because the orchestrator MUST know the agent received the instructions before proceeding. Without ACK, the orchestrator cannot determine if silence means "working on it" or "never received it".
- **Conversations** don't need ACK because they are interactive by nature. The response IS the acknowledgment.

---

## When task acknowledgment is required

Task acknowledgment is MANDATORY when:
- Sending ANY task delegation to a remote agent
- Before considering a task "assigned"
- When resuming communication after downtime
- When sending corrective instructions for a task

Task acknowledgment is NOT required when:
- Having a back-and-forth discussion
- Asking clarifying questions
- Providing feedback on work
- Requesting status updates (the status IS the response)

## If agent receives task normally

### Orchestrator sends task with required acknowledgment

The orchestrator initiates the protocol:

```json
{
  "type": "task-assignment",
  "task_id": "GH-42",
  "requires_ack": true,
  "ack_timeout_minutes": 5,
  "content": {
    "title": "Implement user authentication",
    "description": "...",
    "acceptance_criteria": ["..."]
  }
}
```

### Remote agent responds with acknowledgment

The agent must respond within the specified timeout:

```json
{
  "type": "task-acknowledgment",
  "task_id": "GH-42",
  "status": "received",
  "received_at": "2025-12-31T03:00:00Z",
  "understanding": "Implementing JWT auth with login/logout endpoints",
  "questions": [],
  "estimated_checkpoints": [
    "Tests written - checkpoint 1",
    "Implementation complete - checkpoint 2",
    "PR ready - checkpoint 3"
  ]
}
```

### If agent has questions, clarification occurs

If agent has questions, the following exchange happens:

```json
{
  "type": "task-acknowledgment",
  "task_id": "GH-42",
  "status": "needs-clarification",
  "questions": [
    "Should JWT tokens expire after 24h or 7 days?",
    "Should we support refresh tokens?"
  ]
}
```

Orchestrator responds:

```json
{
  "type": "task-clarification",
  "task_id": "GH-42",
  "answers": [
    "24 hours with refresh token support",
    "Yes, implement refresh tokens"
  ]
}
```

Agent confirms understanding:

```json
{
  "type": "task-acknowledgment",
  "task_id": "GH-42",
  "status": "confirmed",
  "understanding": "JWT with 24h expiry + refresh tokens"
}
```

### Work can only begin after confirmation

Only after `status: confirmed` or `status: received` (with no questions) can the agent begin work.

## If agent fails to acknowledge in time

If no acknowledgment is received within the specified timeout:

1. RETRY once with shorter timeout (2 min)
2. IF still no response:
   - Mark agent as `unresponsive`
   - Reassign task to different agent
   - Log incident for review

### Exponential Backoff Retry Mechanism

For critical tasks requiring guaranteed delivery:

| Attempt | Timeout | Wait Before Retry | Total Elapsed |
|---------|---------|-------------------|---------------|
| 1       | 5 min   | -                 | 5 min         |
| 2       | 2 min   | 30 sec            | 7.5 min       |
| 3       | 1 min   | 1 min             | 9.5 min       |
| Final   | -       | Mark unresponsive | 9.5 min       |

Backoff formula: `wait = min(base_wait * 2^(attempt-1), max_wait)`
- `base_wait`: 30 seconds
- `max_wait`: 2 minutes

## If agent encounters resource or capability issues

### When agent cannot acknowledge due to errors

When agent cannot acknowledge, it MUST send error response:

```json
{
  "type": "task-acknowledgment-error",
  "task_id": "GH-42",
  "error_code": "RESOURCE_UNAVAILABLE",
  "error_message": "Cannot accept task: current load at 95%",
  "timestamp": "2025-12-31T03:00:00Z",
  "retry_after_minutes": 15,
  "alternative_agents": ["agent-backend-02", "agent-backend-03"]
}
```

**Error Codes:**

| Code | Meaning | Orchestrator Action |
|------|---------|---------------------|
| `RESOURCE_UNAVAILABLE` | Agent at capacity | Wait or reassign |
| `CAPABILITY_MISMATCH` | Agent lacks skills | Reassign immediately |
| `NETWORK_ERROR` | Communication issue | Retry with backoff |
| `INVALID_TASK_FORMAT` | Malformed message | Fix and resend |
| `AGENT_SHUTTING_DOWN` | Agent going offline | Reassign immediately |

## During long task execution with checkpoints

When a task spans multiple phases, agents send progress acknowledgments at each checkpoint:

```json
{
  "type": "checkpoint-ack",
  "task_id": "GH-42",
  "checkpoint": 1,
  "status": "completed",
  "summary": "Tests written for auth endpoints",
  "next_checkpoint": 2
}
```

## Proactive enforcement by orchestrator

**The orchestrator MUST proactively enforce acknowledgment.** This is not optional.

### Enforcement Steps (MANDATORY)

After sending ANY Task Delegation:

1. **Immediately add ACK requirement to message**
   ```
   ---
   ACKNOWLEDGMENT REQUIRED: Reply with [ACK] {task_id} - RECEIVED
   Include: Understanding: {1-line summary of what you will do}
   ---
   ```

2. **Set timer for ACK timeout** (default: 5 minutes)

3. **If no ACK within timeout:**
   - Send explicit ACK request:
     ```
     Subject: ACK REQUIRED: {task_id}

     I sent you task {task_id} but have not received acknowledgment.
     Please confirm receipt with: [ACK] {task_id} - {status}

     Status options: RECEIVED, CLARIFICATION_NEEDED, REJECTED, QUEUED
     ```

4. **If still no ACK after second request (2 more minutes):**
   - Mark agent as `unresponsive`
   - Reassign task OR escalate to user
   - Log incident

### ACK Format (Simplified)

Remote agents MUST respond with:

```
[ACK] {task_id} - {status}
Understanding: {1-line summary of what agent will do}
```

**Status values:**
- `RECEIVED` - Task received, will begin work immediately
- `CLARIFICATION_NEEDED` - Task received but need more info (include questions)
- `REJECTED` - Cannot accept task (with reason)
- `QUEUED` - Received but have prior tasks to complete first

### Examples

**Good ACK (RECEIVED):**
```
[ACK] GH-4-xls-implementation - RECEIVED
Understanding: Will implement directory listing with fs::read_dir, serde_json formatting, and all CLI flags (--sort, --reverse, --format, --verbose, --human)
```

**Good ACK (CLARIFICATION_NEEDED):**
```
[ACK] GH-4-xls-implementation - CLARIFICATION_NEEDED
Understanding: Implement xls CLI directory browser
Questions:
1. Should --format support both JSON and table output?
2. Should --verbose show file permissions on all platforms?
```

**Good ACK (QUEUED):**
```
[ACK] GH-4-xls-implementation - QUEUED
Understanding: Directory browser with full CLI flags
Note: Currently completing GH-3, will start this after current task completes
```

### Proactive Check After Delegation

The orchestrator SHOULD add to its workflow after EVERY task delegation:

```
- [ ] Task delegation sent to {agent}
- [ ] ACK received within 5 minutes
- [ ] Understanding confirms agent comprehends scope
- [ ] If CLARIFICATION_NEEDED: answer questions and await RECEIVED
- [ ] Task officially assigned only after ACK confirmed
```

---

## Message flow reference

Visual representation of the complete message flow:

```
Orchestrator                    Remote Agent
     |                               |
     |-- task-assignment ----------->|
     |                               |
     |<-- task-acknowledgment -------|
     |    (received/needs-clarif)    |
     |                               |
     |-- task-clarification -------->| (if needed)
     |                               |
     |<-- task-acknowledgment -------|
     |    (confirmed)                |
     |                               |
     |        [WORK BEGINS]          |
     |                               |
     |<-- checkpoint-ack ------------|
     |<-- checkpoint-ack ------------|
     |<-- task-complete -------------|
```

## Integration with other protocols

This protocol integrates with:
- `task-instruction-format.md` - Task structure
- `status-management.md` - GitHub issue updates
- `session-memory/` - Acknowledgment history
- `artifact-sharing-protocol.md` - Artifacts may be shared during task acknowledgment
- `change-notification-protocol.md` - Config changes may require re-acknowledgment

---

## Troubleshooting

### Problem: Agent Never Acknowledges Tasks

**Symptoms**: Task delegation sent, no ACK received within timeout, agent appears online.

**Solution**:
1. Verify message delivery - check AI Maestro logs for delivery confirmation
2. Check if agent is processing other tasks (may be at capacity)
3. Send explicit ACK reminder with shorter timeout
4. If no response after 3 attempts, mark agent as unresponsive and reassign task
5. Document incident for user review

### Problem: Agent ACKs But With Wrong Understanding

**Symptoms**: Agent sends ACK with `Understanding:` that doesn't match task requirements.

**Solution**:
1. Send explicit correction message quoting the misunderstood parts
2. Include correct interpretation with specific examples
3. Request new ACK with corrected understanding
4. Do NOT allow work to begin until understanding is verified
5. If agent consistently misunderstands, consider reassigning to different agent

### Problem: Agent ACKs as CLARIFICATION_NEEDED But Questions Are Vague

**Symptoms**: Agent requests clarification but questions are too general to answer.

**Solution**:
1. Ask agent to be specific: "Which part of the acceptance criteria is unclear?"
2. Provide additional context from GitHub Issue or spec documents
3. If agent cannot articulate specific questions, this may indicate task scope is too large
4. Consider breaking task into smaller, more concrete subtasks

### Problem: Agent ACKs as QUEUED But Never Starts

**Symptoms**: Agent acknowledged task as QUEUED, but never transitions to working on it.

**Solution**:
1. Send proactive status check asking about prior task completion
2. If prior task is blocked, help unblock it first
3. If prior task is complete but agent didn't start new task, send explicit "begin now" message
4. Set a reminder to check again in 15 minutes
5. If pattern repeats, escalate queue management issues to user

### Problem: Multiple Agents ACK Same Task

**Symptoms**: Same task delegated to multiple agents accidentally, both ACK.

**Solution**:
1. Immediately send CANCEL message to the agent who should NOT work on it
2. Confirm with remaining agent that they are the sole assignee
3. Update tracking to reflect single assignment
4. Review delegation workflow to prevent recurrence
5. Consider adding task_uuid to prevent duplicate delegations

### Problem: ACK Timeout During Network Issues

**Symptoms**: Agent is working but ACKs are not being received due to network problems.

**Solution**:
1. Check AI Maestro server status and connectivity
2. Verify agent's session is still active
3. Try alternative communication method if available
4. Increase timeout temporarily if network is flaky
5. Once connectivity restored, request status update to sync state

---

## Decision Trees for Acknowledgment Handling

### ACK Evaluation Decision Tree

```
ACK received from agent
├─ Does ACK echo back the correct task_id and instruction summary?
│   ├─ Yes (correct understanding) → Log ACK → Proceed with monitoring
│   └─ No (wrong understanding) → What kind of mismatch?
│       ├─ Wrong task_id → Agent confused about which task → Resend with explicit task_id
│       ├─ Wrong summary (misunderstood instructions) → Send correction message
│       │   → Include: "Your understanding: X. Correct understanding: Y"
│       │   → Request new ACK with corrected understanding
│       │   ├─ Corrected ACK received → Proceed
│       │   └─ Still wrong after 2 corrections → Escalate to ECOS
│       │       → Possible agent capability mismatch
│       └─ Partial summary (some items missing) → Send supplement with missing items
│           → Request updated ACK confirming full scope
```

**Cross-reference**: For Stop Work ACK handling, see `task-lifecycle-templates.md` Section 5 (Agent Stop Work Notification).
