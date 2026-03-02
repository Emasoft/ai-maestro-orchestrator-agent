# Operation: Escalate Design Concern to Architect


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Steps](#steps)
- [Escalation Message Template](#escalation-message-template)
- [Design Review Request: <issue_number>](#design-review-request-issue_number)
  - [Concern Description](#concern-description)
  - [Current Context](#current-context)
  - [Request](#request)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Waiting State](#waiting-state)
- [Post-Resolution Steps](#post-resolution-steps)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-escalate-design-concern` |
| Procedure | `proc-clarify-tasks` |
| Workflow Step | Step 14 |
| Trigger | Implementer raises design concern in pre-task interview |
| Actor | Orchestrator (EOA) |
| Target | Architect (EAA) |

---

## Purpose

Escalate design-related concerns from the implementer to the Architect agent (EAA) for resolution. Design decisions are outside the orchestrator's authority and must be resolved before implementation can proceed.

---

## Prerequisites

- Pre-task interview completed
- Implementer identified a design concern
- Concern categorized as design-related (not requirements or capability)
- Architect agent (EAA) is available

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `issue_number` | Yes | GitHub issue number |
| `module_name` | Yes | Name of the module being implemented |
| `concern_description` | Yes | Implementer's stated concern |
| `implementer_agent_id` | Yes | Who raised the concern |
| `context` | Yes | Relevant architectural context |

---

## Steps

1. **Document the concern** in the handoff document

2. **Prepare escalation message** with:
   - Issue/module identification
   - Exact concern as stated by implementer
   - Current architectural context
   - Request for design decision

3. **Send to Architect** using the `agent-messaging` skill:
   - **Recipient**: `architect`
   - **Subject**: "Design Review Request: <issue_number>"
   - **Content**: the escalation message with design concern details
   - **Type**: `escalation`, **Priority**: `high`

   **Verify**: confirm message delivery.

4. **Update implementer** that concern is being reviewed

5. **Wait for Architect response** before proceeding

6. **Apply Architect's decision** to the task

---

## Escalation Message Template

```markdown
## Design Review Request: <issue_number>

**Module**: <module_name>
**Reported by**: <implementer_agent_id>

### Concern Description

<concern_description>

### Current Context

<current_architectural_context>

### Request

Please provide a design decision on how to proceed. The implementer is waiting for guidance before starting work.

Options to consider:
1. Confirm current approach is correct
2. Provide alternative approach
3. Request additional information

Please respond with your decision and rationale.
```

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Escalation sent | AI Maestro message ID | Confirmation of delivery |
| Implementer notified | AI Maestro message | Status update |
| Handoff updated | Document entry | Concern and escalation logged |

---

## Success Criteria

- Architect receives complete context about the concern
- Implementer knows their concern is being reviewed
- Clear request for decision made to Architect
- Handoff document tracks the escalation

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Architect unavailable | Agent not registered | Escalate to EAMA for human architect involvement |
| No response in 24h | Architect backlog | Follow up with reminder |
| Design decision unclear | Ambiguous response | Request clarification from Architect |

---

## Waiting State

While waiting for Architect response:
- Implementer should NOT start implementation
- Other modules can continue if independent
- Orchestrator monitors for Architect response
- Status: `blocked:design-review`

---

## Post-Resolution Steps

After Architect responds:

1. **If approach confirmed**:
   - Inform implementer
   - Proceed to `op-send-proceed-approval`

2. **If alternative provided**:
   - Update task requirements/approach
   - Re-interview implementer with new approach
   - Proceed when new approach understood

3. **If more info needed**:
   - Gather requested information
   - Re-submit to Architect
   - Wait for final decision

---

## Next Operations

Based on Architect response:
- Approach confirmed → `op-send-proceed-approval.md`
- New approach given → `op-send-pretask-interview.md` (re-interview)
- Requirement issue found → `op-escalate-requirement-concern.md`
