# Interview Templates


## Contents

- [Pre-Task Interview Questions](#pre-task-interview-questions)
- [Pre-Task Interview: {TASK_ID}](#pre-task-interview-task_id)
- [Post-Task Interview Questions](#post-task-interview-questions)
- [Post-Task Interview: {TASK_ID}](#post-task-interview-task_id)
- [Evaluating Pre-Task Responses](#evaluating-pre-task-responses)
- [Evaluating Post-Task Responses](#evaluating-post-task-responses)
- [Decision Trees for Interview Evaluation](#decision-trees-for-interview-evaluation)
  - [Pre-Task Interview Evaluation Decision Tree](#pre-task-interview-evaluation-decision-tree)
  - [Post-Task Interview Evaluation Decision Tree](#post-task-interview-evaluation-decision-tree)
  - [REVISE Cycle Escalation Decision Tree](#revise-cycle-escalation-decision-tree)

## Pre-Task Interview Questions

The Orchestrator MUST ask these questions:

```markdown
## Pre-Task Interview: {TASK_ID}

Please confirm your understanding:

1. **Task Summary**: In your own words, what does this task require?

2. **Acceptance Criteria**: What must be true for this task to be complete?

3. **Concerns**: Do you have any concerns about:
   - The requirements (unclear, conflicting, infeasible)?
   - The design (incompatible with existing code)?
   - Your capability (missing tools, skills, access)?
   - Dependencies (blocked by other tasks)?

4. **Approach**: Briefly describe how you plan to implement this.

5. **Blockers**: Is anything preventing you from starting immediately?

Reply with your answers. Do NOT start implementation until I confirm PROCEED.
```

## Post-Task Interview Questions

When implementer reports `[DONE]`:

```markdown
## Post-Task Interview: {TASK_ID}

Before PR creation, please confirm:

1. **Requirements Checklist**: For each requirement, confirm implementation:
   - [ ] REQ-001: {description} - Implemented? Where?
   - [ ] REQ-002: {description} - Implemented? Where?
   - [ ] (list all requirements)

2. **Testing Evidence**:
   - What tests did you write?
   - Do all tests pass? (provide test output)
   - Are there edge cases not covered?

3. **Code Quality**:
   - Did you run linting/formatting?
   - Any technical debt introduced?
   - Any TODO items left?

4. **Documentation**:
   - Did you update relevant docs?
   - Are code comments adequate?

5. **Self-Review**:
   - Did you review your own changes?
   - Any concerns about the implementation?

Reply with evidence for each item.
```

## Evaluating Pre-Task Responses

| Response | Action |
|----------|--------|
| Clear understanding, no concerns | Send PROCEED |
| Minor clarification needed | Clarify and send PROCEED |
| Design concerns | Escalate to Architect (EAA) |
| Requirement concerns (mutable) | Discuss with Architect |
| Requirement concerns (immutable) | Escalate to Manager (EAMA) → User |
| Capability issues | Consider reassignment or skill provision |
| Blockers identified | Resolve blockers first |

## Evaluating Post-Task Responses

| Response | Action |
|----------|--------|
| All requirements met, tests pass | Send APPROVED |
| Minor issues identified | Request fixes, re-interview |
| Missing requirements | REVISE - specify what's missing |
| Tests failing | REVISE - fix tests first |
| Quality concerns | REVISE - address concerns |
| Requirement deviation | Escalate (see escalation-procedures.md) |

## Decision Trees for Interview Evaluation

### Pre-Task Interview Evaluation Decision Tree

```
Pre-task interview responses received from agent
├─ Did agent answer ALL required questions?
│   ├─ Yes → Evaluate understanding quality for each answer:
│   │   ├─ Question 1 (Task Scope): Does agent correctly identify all deliverables?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: FAIL → Note which deliverables were missed
│   │   ├─ Question 2 (Approach): Is proposed approach technically sound?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: FAIL → Note technical concerns
│   │   ├─ Question 3 (Dependencies): Does agent identify correct dependencies?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: FAIL → Note missing/incorrect dependencies
│   │   ├─ Question 4 (Risks): Does agent identify realistic risks?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: WARN (acceptable, not blocking)
│   │   │
│   │   └─ Overall evaluation:
│   │       ├─ All PASS (or PASS + WARN) → Send Proceed Approval → Agent begins work
│   │       ├─ 1 FAIL → Send REVISE with specific correction needed
│   │       │           → Agent resubmits → Re-evaluate (max 3 REVISE cycles)
│   │       └─ 2+ FAIL → Consider reassignment → Escalate to ECOS if needed
│   └─ No (missing answers) → Send REVISE requesting all missing answers
│       → If agent fails to answer after 2 attempts → Escalate to ECOS
```

### Post-Task Interview Evaluation Decision Tree

```
Post-task interview responses received from agent
├─ Did agent complete all sections (summary, files changed, tests, known issues)?
│   ├─ Yes → Cross-check against task requirements:
│   │   ├─ Do "files changed" match expected scope?
│   │   │   ├─ Yes → Continue evaluation
│   │   │   └─ No → Flag: unexpected files touched OR expected files missing
│   │   ├─ Do test results show all passing?
│   │   │   ├─ Yes → Continue evaluation
│   │   │   └─ No → Identify failing tests → Decide: rework or accept with known issues
│   │   ├─ Are "known issues" acceptable?
│   │   │   ├─ Yes (minor/documented) → Continue evaluation
│   │   │   └─ No (critical issues) → Send back for rework
│   │   │
│   │   └─ Overall evaluation:
│   │       ├─ All checks pass → Accept completion → Proceed to verification loops
│   │       ├─ Minor issues → Accept with conditions → Note issues for verification
│   │       └─ Major issues → Reject → Send REVISE with specific rework items
│   └─ No (incomplete report) → Send REVISE requesting missing sections
```

### REVISE Cycle Escalation Decision Tree

```
REVISE sent to agent (interview response was inadequate)
├─ Is this the 1st REVISE for this interview?
│   ├─ Yes → Send specific feedback on what needs improvement
│   │         → Wait for resubmission (timeout: 10 min)
│   │         ├─ Resubmission received → Re-evaluate from top
│   │         └─ Timeout → Send reminder → Wait 5 more min → If still nothing, escalate
│   ├─ 2nd REVISE → Send more detailed guidance with examples
│   │               → Explicitly state: "This is your second revision. One more attempt remains."
│   │               → Wait for resubmission → Re-evaluate
│   └─ 3rd REVISE (final) → Agent has failed 3 times
│       ├─ Is failure due to misunderstanding? → Escalate to ECOS: request different agent
│       ├─ Is failure due to task complexity? → Escalate to ECOS: request task simplification
│       └─ Is failure due to agent capability? → Escalate to ECOS: request specialized agent
│
│   In all escalation cases:
│   → Include full interview history (all attempts + all REVISE feedback)
│   → Recommend specific action (reassign / simplify / split task)
```
