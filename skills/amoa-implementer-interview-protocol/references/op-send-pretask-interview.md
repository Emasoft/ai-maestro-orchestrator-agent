# Operation: Send Pre-Task Interview Questions


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Steps](#steps)
- [Message Template](#message-template)
- [Pre-Task Interview: <issue_number>](#pre-task-interview-issue_number)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Next Operation](#next-operation)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-send-pretask-interview` |
| Procedure | `proc-clarify-tasks` |
| Workflow Step | Step 14 |
| Trigger | Task assignment to implementer agent |
| Actor | Orchestrator (AMOA) |
| Target | Implementer agent |

---

## Purpose

Send structured interview questions to an implementer agent BEFORE they begin work. This operation verifies the implementer understands the task, has required capabilities, and identifies potential blockers.

---

## Prerequisites

- Task assignment message already sent to implementer
- Implementer has acknowledged (ACK) the assignment
- AI Maestro API is accessible
- Issue number and requirements are known

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `implementer_agent_id` | Yes | Target agent session name |
| `issue_number` | Yes | GitHub issue number (e.g., `#42`) |
| `task_summary` | Yes | Brief description of the task |
| `acceptance_criteria` | Yes | List of requirements to implement |

---

## Steps

1. **Construct the interview message** with the seven key questions:
   - Task summary in your own words
   - Acceptance criteria understanding
   - Concerns (requirements/design/capability/dependencies)
   - Files/domains to be touched (single-writer ownership check)
   - Anticipated NPT/EHT derived tasks
   - Implementation approach
   - Blockers

2. **Format the message** using the pre-task interview template

3. **Send the interview** using the `agent-messaging` skill:
   - **Recipient**: the implementer agent session name
   - **Subject**: "Pre-Task Interview: <issue_number>"
   - **Content**: the formatted interview questions
   - **Type**: `request`, **Priority**: `high`

   **Verify**: confirm message delivery.

4. **Log the interview request** in handoff document

5. **Wait for implementer response** before proceeding

---

## Message Template

```markdown
## Pre-Task Interview: <issue_number>

Before you begin implementation, please answer these questions:

1. **Task Summary**: Describe the task in your own words. What are you building?

2. **Acceptance Criteria**: List the specific acceptance criteria you will implement:
   - [ ] Criterion 1
   - [ ] Criterion 2
   - [ ] Criterion 3

3. **Concerns**: Do you have concerns about any of the following?
   - Requirements clarity
   - Design approach
   - Your capability/tools
   - Dependencies on other modules

4. **Files / Domains Touched** (single-writer ownership check): List the exact
   files, modules, and mutable surfaces (config, schema, API, docs) you expect
   to create or modify, and confirm you are the single owner of each for this
   task. Flag any surface owned by another task/agent — it needs a domain claim
   or a delegation (never two writers on one surface).

5. **Derived Tasks (NPT / EHT)**: What derived tasks do you anticipate?
   - **NPT** (necessary prerequisites that must land BEFORE this task), and
   - **EHT** (effect-handling: caller updates, doc updates, downstream re-tests).
   List each you foresee, or state "none anticipated".

6. **Implementation Approach**: Briefly describe how you plan to implement this.

7. **Blockers**: Are there any blockers preventing you from starting?

Reply with your answers. Do not begin implementation until you receive PROCEED.
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Message sent confirmation | AI Maestro response JSON | Contains message ID |
| Interview logged | Handoff document entry | Timestamp and questions sent |

---

## Success Criteria

- Message delivered successfully (AI Maestro returns message ID)
- Message contains all seven interview questions
- Priority set to "high"
- Subject includes issue number

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| AI Maestro unreachable | Service down | Retry after 30 seconds, escalate if persistent |
| Agent not found | Wrong agent ID | Verify agent ID with `/check-agents` |
| Message not delivered | Network issue | Check AI Maestro logs, retry |

---

## Next Operation

After receiving implementer's response, proceed to:
- `op-evaluate-understanding-response.md` - Evaluate the answers
