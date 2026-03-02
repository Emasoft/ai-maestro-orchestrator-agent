---
name: eoa-implementer-interview-protocol
description: Interview protocols for task verification. Use when checking implementer readiness or approving PR creation. Trigger with task assignment.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Steps 14, 19"
procedure: "proc-clarify-tasks, proc-complete-task"
---

# Implementer Interview Protocol

## Overview

The Orchestrator (EOA) MUST interview the Implementer agent both **before** and **after** task execution. This is NOT optional. Skipping these interviews leads to wasted work, requirement violations, and integration failures. The pre-task interview verifies understanding, capability, compatibility, and feasibility. The post-task interview verifies completeness, quality, testing, and documentation before approving PR creation.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow
2. Read **eoa-remote-agent-coordinator/references/rule-14-immutable-requirements.md** for immutable vs. mutable requirements
3. Read **eoa-label-taxonomy** for status labels
4. Read **eoa-messaging-templates** for message formats
5. Access to AI Maestro API for agent messaging
6. Understanding of escalation paths (EOA → EAA for design, EOA → EAMA → User for requirements)

---

## 1. Pre-Task Interview (MANDATORY)

### 1.1 Purpose

Before the Implementer starts work, the Orchestrator MUST verify:

1. **Understanding** - Does the implementer understand the task?
2. **Capability** - Can the implementer do the task with available tools/skills?
3. **Compatibility** - Are there conflicts with existing code or architecture?
4. **Feasibility** - Are the requirements achievable as specified?

### 1.2 Interview Flow

```
ORCHESTRATOR                           IMPLEMENTER
     |                                      |
     |-- Task Assignment Message ---------->|
     |                                      |
     |<-- ACK + Understanding Summary ------|
     |                                      |
     |-- Interview Questions -------------->|
     |                                      |
     |<-- Answers + Concerns ---------------|
     |                                      |
     [Evaluate responses]                   |
     |                                      |
     |-- PROCEED or ESCALATE -------------->|
```

### 1.3 Interview Questions and Response Evaluation

**Full question templates and evaluation criteria**: [interview-templates.md](./references/interview-templates.md)
- Pre-task interview questions (5 key questions)
- Post-task interview questions (5 verification areas)
- Response evaluation tables for both phases
- Decision trees for PROCEED vs. escalate

**Key questions cover**: Task summary, acceptance criteria, concerns (requirements/design/capability/dependencies), implementation approach, and blockers.

### 1.4 Escalation Paths and Messages

**Full escalation templates**: [escalation-messages.md](./references/escalation-messages.md)
- Design issue escalation to Architect
- Immutable requirement escalation to Manager → User
- PROCEED approval message
- APPROVED approval message
- REVISE rejection message

**Escalation triggers**:
- Design concerns → Escalate to Architect (EAA)
- Immutable requirement concerns → Escalate to Manager (EAMA) → User
- Capability issues → Reassign or provide skills
- Blockers → Resolve before proceeding

---

## 2. Post-Task Interview (MANDATORY)

### 2.1 Purpose

After the Implementer reports completion, the Orchestrator MUST verify:

1. **Completeness** - Were ALL requirements implemented?
2. **Quality** - Does the code meet quality standards?
3. **Testing** - Were tests written and do they pass?
4. **Documentation** - Is documentation updated if required?

### 2.2 Interview Flow

```
IMPLEMENTER                            ORCHESTRATOR
     |                                      |
     |-- Completion Report ---------------->|
     |                                      |
     |<-- Post-Task Interview Questions ----|
     |                                      |
     |-- Answers + Evidence --------------->|
     |                                      |
     |                     [Verify responses]
     |                                      |
     |<-- APPROVED or REVISE ---------------|
     |                                      |
     [If APPROVED: Create PR]              |
     |                                      |
     |-- PR Created: #{NUMBER} ------------>|
     |                                      |
     |            [Notify Integrator]      |
```

### 2.3 Post-Task Verification

**Full post-task protocol**: [interview-templates.md](./references/interview-templates.md)
- Complete verification question template (5 areas)
- Response evaluation table
- APPROVED, REVISE, and escalation criteria

**Verification areas**: Requirements checklist, testing evidence, code quality, documentation, self-review.

**Outcomes**:
- All pass → Send APPROVED
- Minor issues → Request fixes, re-interview
- Major issues → Send REVISE with specific actions
- Requirement deviations → Escalate

---

## 3. Handoff to Integrator

### 3.1 When PR is Created

After implementer creates PR and reports the number:

1. Update issue status: `status:ai-review`
2. Notify Integrator via AI Maestro (template in **eoa-messaging-templates**)
3. Transfer responsibility from orchestrator to integrator

### 3.2 Responsibility Transfer

| Before PR Creation | After PR Creation |
|--------------------|-------------------|
| Orchestrator responsible | Integrator responsible |
| Implementer executes | Implementer responds to review |
| Task tracked via issue | Work tracked via PR |

---

## 4. Exception Handling

**Full exception handling procedures**: [exception-handling.md](./references/exception-handling.md)
- Requirement disagreements (3 types with escalation paths)
- No acknowledgment received
- Misunderstood tasks
- Design change recommendations
- Incomplete work reports
- Test failures
- PR protocol violations

**Common exceptions covered**:
1. Implementer disagrees with requirements → escalate
2. Architect recommends design change → update and re-interview
3. User approves requirement change → document and proceed
4. Implementer never ACKs → reminder → escalate
5. Work reported incomplete → REVISE with specifics
6. Tests fail → REVISE, require passing tests

---

## Instructions

Follow these steps to conduct implementer interviews:

### Checklist

Copy this checklist and track your progress:

**Pre-Task Interview:**
- [ ] Send task assignment message via AI Maestro using the `agent-messaging` skill
- [ ] Wait for implementer ACK (acknowledgment)
- [ ] Send pre-task interview questions using the `agent-messaging` skill
- [ ] Evaluate implementer's understanding summary
- [ ] Check for concerns (requirements, design, capability, dependencies)
- [ ] Escalate design concerns to Architect (EAA) if needed
- [ ] Escalate immutable requirement concerns to Manager (EAMA) if needed
- [ ] Resolve blockers before proceeding
- [ ] Send PROCEED message after satisfactory answers
- [ ] Log interview results in handoff document

**Post-Task Interview:**
- [ ] Receive implementer's completion report [DONE]
- [ ] Send post-task verification questions
- [ ] Verify ALL requirements checklist items completed
- [ ] Verify test evidence (tests written and passing)
- [ ] Check code quality (linting, formatting, no TODOs)
- [ ] Check documentation updates (if required)
- [ ] Evaluate self-review responses
- [ ] Send APPROVED or REVISE message
- [ ] Wait for PR creation and PR number report
- [ ] Notify Integrator (EIA) that PR is ready for review
- [ ] Update issue status to `status:ai-review`

### Pre-Task Interview Steps

1. Send task assignment message via AI Maestro using the `agent-messaging` skill
2. Wait for implementer ACK (acknowledgment)
3. Send pre-task interview questions using the `agent-messaging` skill ([interview-templates.md](./references/interview-templates.md))
4. Evaluate implementer's understanding summary
5. Check for concerns about requirements, design, capability, or dependencies
6. If design concerns exist, escalate to Architect (EAA) ([escalation-messages.md](./references/escalation-messages.md))
7. If immutable requirement concerns exist, escalate to Manager (EAMA) → User
8. If blockers are identified, resolve before proceeding
9. Send PROCEED message only after satisfactory answers
10. Log interview results in handoff document

### Post-Task Interview Steps

1. Receive implementer's completion report `[DONE]`
2. Send post-task verification questions ([interview-templates.md](./references/interview-templates.md))
3. Verify ALL requirements checklist items completed
4. Verify test evidence (tests written and passing)
5. Check code quality (linting, formatting, no TODOs)
6. Check documentation updates (if required)
7. Evaluate self-review responses
8. If verification passes, send APPROVED message ([escalation-messages.md](./references/escalation-messages.md))
9. If verification fails, send REVISE message with specific issues
10. Wait for PR creation and PR number report
11. Notify Integrator (EIA) that PR is ready for review
12. Update issue status to `status:ai-review`

---

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Interview questions | Markdown message via AI Maestro | Pre-task or post-task question template |
| PROCEED approval | Markdown message | "PROCEED: Your understanding is confirmed. Begin implementation." |
| APPROVED approval | Markdown message | "APPROVED: Create PR with requirements X, Y, Z." |
| REVISE request | Markdown message | "REVISE: Issues found. Fix X, Y, Z before re-reporting." |
| Escalation to Architect | AI Maestro JSON | Design review request with concern details |
| Escalation to Manager | AI Maestro JSON | User decision request for requirement issue |
| Handoff to Integrator | AI Maestro JSON | PR ready for review notification |

---

## Error Handling

**Common errors and solutions**: [exception-handling.md](./references/exception-handling.md)

| Error | Quick Solution |
|-------|----------------|
| Implementer never ACKs | Reminder → escalate to progress-monitoring |
| Misunderstands task | Clarify, update handoff, re-interview |
| Design concerns | Escalate to Architect (EAA) |
| Requirement concerns | Escalate to Manager (EAMA) → User |
| Incomplete work | REVISE with specific items |
| Tests fail | REVISE, require passing tests |
| PR before approval | Remind protocol, manual review |

---

## Examples

**Full examples with code**: [examples.md](./references/examples.md)
- Example 1: Send pre-task interview questions
- Example 2: Escalate design concern to architect
- Example 3: Send PROCEED approval
- Example 4: Send post-task verification questions
- Example 5: Send APPROVED and handoff to integrator

**Quick example - Pre-task interview**: Send using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Pre-Task Interview: #42"
- **Content**: "Pre-Task Interview: #42 - 1. Task Summary? 2. Acceptance Criteria? 3. Concerns? 4. Approach? 5. Blockers?"
- **Type**: `request`, **Priority**: `high`

---

## Resources

- **[interview-templates.md](./references/interview-templates.md)** - Question templates, evaluation, and decision trees (Pre-Task, Post-Task, REVISE Cycle Escalation)
- **[escalation-messages.md](./references/escalation-messages.md)** - Escalation and approval messages, escalation path selection decision tree, EAA/EAMA response templates
- **[exception-handling.md](./references/exception-handling.md)** - Exception procedures
- **[examples.md](./references/examples.md)** - Complete curl examples
- **AGENT_OPERATIONS.md** - Core orchestrator workflow
- **eoa-remote-agent-coordinator/references/rule-14-immutable-requirements.md** - Immutable vs. mutable requirements
- **eoa-label-taxonomy** - Status label workflow
- **eoa-messaging-templates** - Message templates for interviews and escalations
- **eoa-task-distribution** - Task assignment protocol
- **eoa-progress-monitoring** - Agent state tracking
