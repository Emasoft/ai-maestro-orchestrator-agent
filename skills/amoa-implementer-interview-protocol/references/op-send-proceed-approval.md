# Operation: Send PROCEED Approval


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Steps](#steps)
- [PROCEED Message Template](#proceed-message-template)
- [PROCEED: <issue_number>](#proceed-issue_number)
  - [Confirmed Acceptance Criteria](#confirmed-acceptance-criteria)
  - [Expectations](#expectations)
  - [On Completion](#on-completion)
- [State Updates](#state-updates)
  - [Module Status Update](#module-status-update)
  - [Assignment Update](#assignment-update)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-send-proceed-approval` |
| Procedure | `proc-clarify-tasks` |
| Workflow Step | Step 14 |
| Trigger | Implementer passes pre-task interview evaluation |
| Actor | Orchestrator (EOA) |
| Target | Implementer agent |

---

## Purpose

Send official authorization for the implementer to begin work. PROCEED is the formal gate that transitions a task from "assigned" to "in-progress". Without PROCEED, the implementer must not start coding.

---

## Prerequisites

- Pre-task interview completed
- Evaluation passed all criteria (op-evaluate-understanding-response)
- No unresolved concerns or blockers
- No pending escalations

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `implementer_agent_id` | Yes | Target agent session name |
| `issue_number` | Yes | GitHub issue number |
| `confirmed_criteria` | Yes | List of acceptance criteria implementer will fulfill |
| `approved_approach` | Optional | Implementation approach if discussed |

---

## Steps

1. **Verify all prerequisites met**:
   - Interview responses evaluated
   - No pending escalations
   - No unresolved blockers

2. **Construct PROCEED message** with:
   - Explicit PROCEED authorization
   - Confirmed understanding acknowledgment
   - Reminder of acceptance criteria
   - Expected deliverables

3. **Send the PROCEED** using the `agent-messaging` skill:
   - **Recipient**: the implementer agent session name
   - **Subject**: "PROCEED: <issue_number>"
   - **Content**: the proceed message with reminders and acceptance criteria
   - **Type**: `approval`, **Priority**: `high`

   **Verify**: confirm message delivery.

4. **Update state file**:
   - Module status: `pending` → `in-progress`
   - Assignment status: `awaiting_repetition` → `authorized`
   - Instruction verification: `authorized_at: <timestamp>`

5. **Update GitHub Issue**:
   - Add label: `status:in-progress`
   - Remove label: `status:assigned`

6. **Log PROCEED** in handoff document

---

## PROCEED Message Template

```markdown
## PROCEED: <issue_number>

Your understanding of the task has been verified. You are authorized to begin implementation.

### Confirmed Acceptance Criteria

You will implement the following:

- [ ] <criterion_1>
- [ ] <criterion_2>
- [ ] <criterion_3>

### Expectations

1. Implement ALL listed acceptance criteria
2. Write tests for your implementation
3. Follow existing code patterns and style
4. Report completion with `[DONE]` when finished
5. Do NOT create PR until you receive APPROVED

### On Completion

When you complete implementation, report `[DONE]` and prepare for post-task interview.

Good luck!
```

---

## State Updates

### Module Status Update

```yaml
modules_status:
  - id: "<module_id>"
    status: "in-progress"  # Changed from "assigned"
```

### Assignment Update

```yaml
active_assignments:
  - agent: "<implementer_agent_id>"
    module: "<module_id>"
    status: "in-progress"  # Changed from "pending_verification"
    instruction_verification:
      status: "authorized"  # Changed from "awaiting_repetition"
      authorized_at: "<ISO_timestamp>"
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| PROCEED message sent | AI Maestro message ID | Delivery confirmation |
| State file updated | YAML changes | Module and assignment status |
| GitHub Issue updated | Label changes | status:in-progress added |
| Handoff logged | Document entry | Authorization timestamp |

---

## Success Criteria

- Implementer receives PROCEED message
- Message contains all confirmed acceptance criteria
- State file reflects `in-progress` status
- GitHub Issue has `status:in-progress` label
- Handoff document records authorization

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Message not delivered | AI Maestro issue | Retry, verify agent connectivity |
| State file update fails | File locked or corrupt | Retry, validate YAML |
| GitHub label fails | gh CLI issue | Manual label update via GitHub UI |

---

## Important Rules

1. **PROCEED is final** - Once sent, implementer is authorized to code
2. **Cannot revoke easily** - If requirements change after PROCEED, use `/modify-module`
3. **One PROCEED per assignment** - Do not send duplicate PROCEED messages
4. **Tracks accountability** - Timestamp records who authorized when

---

## Next Operations

After PROCEED sent:
- Wait for implementer to report `[DONE]`
- Monitor progress via `/check-agents`
- Handle issues via exception procedures
- On `[DONE]`, proceed to `op-send-posttask-interview.md`
