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

4. **Files / Domains Touched** (single-writer ownership check): List the exact
   files, modules, and mutable surfaces (config, schema, API, docs) you expect
   to CREATE or MODIFY. For each, confirm you are the single owner of that
   surface for this task. If you must touch a surface owned by another task or
   agent, say so explicitly — that surface needs a domain claim or a delegation
   to its owner (NEVER two writers on one surface).

5. **Derived Tasks (NPT / EHT)**: What derived tasks do you anticipate?
   - **NPT (Necessary-Prerequisite Tasks)** — work that MUST land BEFORE you can
     proceed (e.g. "the auth schema must be migrated first").
   - **EHT (Effects-Handling Tasks)** — work that handles the CONSEQUENCES of
     your change (e.g. "update every caller of the renamed function", "update
     the docs", "re-test downstream consumers").
   List each you foresee, or state "none anticipated" — surfacing them now lets
   the Orchestrator author them and avoids cross-task collisions later.

6. **Approach**: Briefly describe how you plan to implement this.

7. **Blockers**: Is anything preventing you from starting immediately?

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
| Design concerns | Escalate to Architect (AMAA) |
| Requirement concerns (mutable) | Discuss with Architect |
| Requirement concerns (immutable) | Escalate to Manager (AMAMA) → User |
| Capability issues | Consider reassignment or skill provision |
| Blockers identified | Resolve blockers first |
| Files/domains overlap another task or agent's surface | Do NOT PROCEED — resolve ownership first (domain claim or delegate to the owner); two writers on one surface is forbidden |
| Anticipated NPT not yet tracked | Author the NPT (and mark this task `blocked-by:` it) before PROCEED |
| Anticipated EHT not yet tracked | Author the EHT(s); they gate this task's transition to `complete` (EHTs are post-conditions) |

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
├─ Did agent answer ALL 7 required questions?
│   ├─ Yes → Evaluate understanding quality for each answer:
│   │   ├─ Q1 (Task Summary): Does agent correctly restate scope + all deliverables?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: FAIL → Note which deliverables were missed
│   │   ├─ Q2 (Acceptance Criteria): Does agent know what "done" means?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: FAIL → Note misunderstood criteria
│   │   ├─ Q3 (Concerns): Are raised concerns valid / are there unraised ones?
│   │   │   ├─ Resolvable in-team → handle per the in-development loop
│   │   │   │   (FULL_PROJECT_WORKFLOW Step 18.5); design concern → AMAA
│   │   │   └─ None / acceptable → Score: PASS
│   │   ├─ Q4 (Files/Domains — single-writer check): Does any named surface
│   │   │       overlap another task or agent's owned surface?
│   │   │   ├─ No overlap, agent is sole owner → Score: PASS
│   │   │   └─ Overlap → Score: FAIL (BLOCKING) → Resolve ownership first
│   │   │       (domain claim or delegate to owner) BEFORE PROCEED
│   │   ├─ Q5 (Derived NPT/EHT): Did agent surface plausible prerequisites and
│   │   │       effect-handling tasks?
│   │   │   ├─ Yes (or genuinely "none") → Score: PASS → Author any untracked
│   │   │   │   NPT (set this task blocked-by it) / EHT (gates `complete`)
│   │   │   └─ Obvious NPT/EHT missed → Score: FAIL → Name them, re-interview
│   │   ├─ Q6 (Approach): Is the proposed approach technically sound?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: FAIL → Note technical concerns
│   │   ├─ Q7 (Blockers): Did agent identify realistic blockers?
│   │   │   ├─ Yes → Score: PASS
│   │   │   └─ No → Score: WARN (acceptable, not blocking)
│   │   │
│   │   └─ Overall evaluation:
│   │       ├─ All PASS (or PASS + WARN) → Send Proceed Approval → Agent begins work
│   │       ├─ Any Q4 ownership-overlap FAIL → NEVER PROCEED until resolved
│   │       ├─ 1 FAIL (non-Q4) → Send REVISE with specific correction needed
│   │       │           → Agent resubmits → Re-evaluate (max 3 REVISE cycles)
│   │       └─ 2+ FAIL → Consider reassignment → Escalate to AMCOS if needed
│   └─ No (missing answers) → Send REVISE requesting all missing answers
│       → If agent fails to answer after 2 attempts → Escalate to AMCOS
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
│       ├─ Is failure due to misunderstanding? → Escalate to AMCOS: request different agent
│       ├─ Is failure due to task complexity? → Escalate to AMCOS: request task simplification
│       └─ Is failure due to agent capability? → Escalate to AMCOS: request specialized agent
│
│   In all escalation cases:
│   → Include full interview history (all attempts + all REVISE feedback)
│   → Recommend specific action (reassign / simplify / split task)
```
