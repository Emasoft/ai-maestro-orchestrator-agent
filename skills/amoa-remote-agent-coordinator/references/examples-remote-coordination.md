# Remote Agent Coordination Examples

## Table of Contents

- 1.0 Example: Onboard and Assign Task to New Agent
  - 1.1 Step-by-step onboarding flow
  - 1.2 Task delegation with ACK instructions
- 2.0 Example: 4-Verification Loop Sequence
  - 2.1 Complete conversation flow
  - 2.2 Loop counter tracking
- 3.0 Example: Progress Monitoring Flow
  - 3.1 Proactive polling sequence
  - 3.2 Handling no-response scenarios

---

## 1.0 Example: Onboard and Assign Task to New Agent

### 1.1 Step-by-step onboarding flow

```bash
# Step 1: Agent completes onboarding checklist
# Step 2: Agent sends registration message via AI Maestro

# Orchestrator receives registration and adds to roster
# Verify agent has required LSP servers
# Assign first task with ACK protocol

Send the first task assignment using the `agent-messaging` skill:
- **Recipient**: `implementer-new`
- **Subject**: "First Task Assignment"
- **Content**: "[ACK REQUIRED] Task: Implement feature X. Before starting, reply: [ACK] task-001 - RECEIVED"
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `task_id` ("task-001")

**Verify**: confirm message delivery and wait for ACK.
```

### 1.2 Task delegation with ACK instructions

This example shows the full delegation message structure:

Send a full delegation message using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Task: Implement auth-core module"
- **Priority**: `high`
- **Type**: `task`
- **Content**: Include the full task description with mandatory ACK protocol:
  - Task identifier: `auth-core`
  - ACK format: `[ACK] auth-core - {status}` with Understanding line
  - Status options: RECEIVED, CLARIFICATION_NEEDED, REJECTED, QUEUED
  - Context: JWT authentication implementation for user login
  - Scope: `src/auth/`
  - Tests: `pytest tests/auth/`

**Verify**: confirm message delivery and wait for ACK response.

**Expected ACK response:**
```
[ACK] auth-core - RECEIVED
Understanding: I will implement JWT authentication in src/auth/ with login, token generation, and validation endpoints.
```

---

## 2.0 Example: 4-Verification Loop Sequence

### 2.1 Complete conversation flow

This shows the full 5 PR requests cycle required before approval:

```
PR Request #1: Agent: "Can I create PR?"
→ Orchestrator: "Check your changes for errors" (Loop 1)

PR Request #2: Agent: "Checked, can I create PR?"
→ Orchestrator: "Check your changes for errors" (Loop 2)

PR Request #3: Agent: "Checked again, can I create PR?"
→ Orchestrator: "Check your changes for errors" (Loop 3)

PR Request #4: Agent: "Triple-checked, can I create PR?"
→ Orchestrator: "Check your changes for errors" (Loop 4)

PR Request #5: Agent: "Fourth check complete, can I create PR?"
→ Orchestrator: "APPROVED - create PR" or "NOT APPROVED - restart loops"
```

### 2.2 Loop counter tracking

The orchestrator tracks verification state per task:

| Task ID | Agent | PR Requests | Current State |
|---------|-------|-------------|---------------|
| auth-core | implementer-1 | 4 | Loop 4 complete |
| db-migration | implementer-2 | 2 | Loop 2 in progress |

**Important**: The orchestrator MUST maintain this state across messages to ensure all 4 loops are completed before approval.

---

## 3.0 Example: Progress Monitoring Flow

### 3.1 Proactive polling sequence

This shows the 10-15 minute polling cycle during active work:

Every 10-15 minutes during active work, send a progress check using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Progress Check"
- **Content**: "1. Current progress? 2. Next steps? 3. Any issues? 4. Anything unclear? 5. Difficulties? 6. Need anything?"
- **Type**: `request`
- **Priority**: `normal`
- **Data**: include `poll_id`

**Verify**: confirm message delivery.

**Timeline example:**
```
[T+0 min] Task delegated to agent
[T+15 min] Orchestrator polls: "Status update? Any issues or unclear items?"
[T+30 min] Agent responds: "50% complete, working on token validation"
[T+45 min] Orchestrator polls: "Status update? Any difficulties?"
[T+60 min] Agent responds: "80% complete, writing tests"
```

### 3.2 Handling no-response scenarios

```
[T+15 min] Poll #1: "Status update?" - No response
[T+30 min] Poll #2: "Status update?" - No response
[T+45 min] Escalation: "Agent unresponsive - consider reassignment"
```

**Action**: After 2 consecutive no-response polls, send escalation message and consider task reassignment.

---

## Related References

- [echo-acknowledgment-protocol.md](./echo-acknowledgment-protocol.md) - Full ACK protocol
- [verification-loops-protocol.md](./verification-loops-protocol.md) - 4-loop details
- [progress-monitoring-protocol.md](./progress-monitoring-protocol.md) - Polling intervals
