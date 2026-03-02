# Operation: Evaluate Understanding Response


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Evaluation Criteria](#evaluation-criteria)
  - [Question 1: Task Summary](#question-1-task-summary)
  - [Question 2: Acceptance Criteria](#question-2-acceptance-criteria)
  - [Question 3: Concerns](#question-3-concerns)
  - [Question 4: Implementation Approach](#question-4-implementation-approach)
  - [Question 5: Blockers](#question-5-blockers)
- [Steps](#steps)
- [Decision Matrix](#decision-matrix)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-evaluate-understanding-response` |
| Procedure | `proc-clarify-tasks` |
| Workflow Step | Step 14 |
| Trigger | Implementer responds to pre-task interview |
| Actor | Orchestrator (EOA) |
| Input From | Implementer agent |

---

## Purpose

Evaluate the implementer's pre-task interview responses to determine if they correctly understand the task and are ready to proceed. This operation gates implementation start.

---

## Prerequisites

- Pre-task interview questions sent (op-send-pretask-interview completed)
- Implementer has responded with answers
- Original task requirements available for comparison

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `implementer_response` | Yes | Full text of implementer's answers |
| `original_requirements` | Yes | The actual task requirements for comparison |
| `acceptance_criteria` | Yes | Official acceptance criteria list |

---

## Evaluation Criteria

### Question 1: Task Summary

| Response Quality | Action |
|-----------------|--------|
| Correct understanding | Mark PASS |
| Partial understanding | Request clarification |
| Misunderstanding | Correct and re-interview |

**Check for:**
- Core objective captured correctly
- No scope creep (adding unrequested features)
- No scope reduction (missing required features)

### Question 2: Acceptance Criteria

| Response Quality | Action |
|-----------------|--------|
| All criteria listed | Mark PASS |
| Missing criteria | Point out missing items |
| Extra criteria added | Clarify scope boundaries |

**Check for:**
- 1:1 match with official criteria
- No reinterpretation of requirements
- No added assumptions

### Question 3: Concerns

| Concern Type | Action |
|-------------|--------|
| No concerns | Proceed if other answers pass |
| Requirements concern | Evaluate if valid, escalate if needed |
| Design concern | Escalate to Architect (EAA) |
| Capability concern | Assess skill gap, reassign if needed |
| Dependency concern | Check dependency status, resolve |

### Question 4: Implementation Approach

| Response Quality | Action |
|-----------------|--------|
| Sound approach | Mark PASS |
| Concerning approach | Request alternative |
| Violates architecture | Escalate to Architect (EAA) |

**Check for:**
- Approach aligns with existing patterns
- No obvious anti-patterns
- Testability considered

### Question 5: Blockers

| Response | Action |
|----------|--------|
| No blockers | Proceed if other answers pass |
| Blockers identified | Resolve before PROCEED |

---

## Steps

1. **Read the implementer's response** carefully

2. **Evaluate each answer** against the criteria tables above

3. **Document evaluation results** for each question:
   - PASS / CLARIFY / ESCALATE / FAIL

4. **Determine overall outcome**:
   - All PASS → Proceed to `op-send-proceed-approval`
   - Any CLARIFY → Request clarification, re-evaluate
   - Any ESCALATE → Route to appropriate party
   - Any FAIL → Re-interview after correction

5. **Record evaluation** in handoff document

---

## Decision Matrix

| Q1 | Q2 | Q3 | Q4 | Q5 | Outcome |
|----|----|----|----|----|---------|
| PASS | PASS | No concerns | PASS | No blockers | PROCEED |
| PASS | PASS | Design concern | PASS | No blockers | ESCALATE to Architect |
| CLARIFY | * | * | * | * | Request clarification |
| * | FAIL | * | * | * | Re-interview |
| * | * | * | * | Blockers | Resolve blockers first |

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Evaluation result | PROCEED / CLARIFY / ESCALATE / RE-INTERVIEW | Overall decision |
| Per-question status | PASS / CLARIFY / ESCALATE / FAIL | Detailed breakdown |
| Next action | Operation name | What to do next |

---

## Success Criteria

- All five questions evaluated
- Clear decision reached (no ambiguity)
- Evaluation documented in handoff
- Next action identified

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Incomplete response | Agent didn't answer all questions | Request missing answers |
| Ambiguous response | Unclear answers | Request clarification |
| Response contradicts itself | Confusion | Request re-submission |

---

## Next Operations

Based on evaluation outcome:
- All PASS → `op-send-proceed-approval.md`
- Design concern → `op-escalate-design-concern.md`
- Requirement concern → `op-escalate-requirement-concern.md`
- Clarification needed → Re-run `op-send-pretask-interview.md` with specific questions
