# Two-Phase Mode Quick Reference Checklist

## Contents

- 1. Plan Phase Checklist
- 2. Orchestration Phase Checklist
- 3. Module Completion Checklist
- 4. Exit Verification Checklist

---

## 1. Plan Phase Checklist

Use this checklist when in Plan Phase Mode.

- [ ] Run `/start-planning` with user goal
- [ ] Create USER_REQUIREMENTS.md with all functional requirements
- [ ] Design system architecture
- [ ] Break down into modules with acceptance criteria
- [ ] Review exit criteria met:
  - [ ] USER_REQUIREMENTS.md complete
  - [ ] All modules defined with criteria
  - [ ] User approved the plan
- [ ] Run `/approve-plan` to transition

---

## 2. Orchestration Phase Checklist

Use this checklist when entering Orchestration Phase Mode.

- [ ] Run `/start-orchestration` after plan approval
- [ ] Register all remote agents via `/register-agent`
- [ ] For each module, complete the Module Completion Checklist (Section 3)
- [ ] Verify all modules complete
- [ ] Exit allowed

---

## 3. Module Completion Checklist

Complete this checklist for EACH module during Orchestration Phase.

### 3.1 Assignment

- [ ] Assign via `/assign-module`

### 3.2 Instruction Verification Protocol (MANDATORY)

- [ ] Send assignment with verification request
- [ ] Wait for agent to repeat understanding
- [ ] Verify repetition is correct (or send corrections)
- [ ] Answer all clarifying questions
- [ ] Authorize implementation

### 3.3 Proactive Progress Polling (MANDATORY)

- [ ] Poll every 10-15 minutes with ALL 6 questions
- [ ] Take immediate action on reported issues
- [ ] Track poll history

### 3.4 Instruction Update Verification (IF Sending Updates)

Only if sending updates mid-implementation:

- [ ] Execute Instruction Update Verification Protocol
- [ ] Send update notification using the `agent-messaging` skill (what changed, why, impact)
- [ ] Wait for receipt confirmation (agent PAUSES)
- [ ] Request feasibility assessment (5 questions)
- [ ] Address all concerns raised
- [ ] Authorize resume only after all concerns resolved
- [ ] Handle config feedback requests from implementer

### 3.5 Completion

- [ ] Require 4 verification loops before PR
- [ ] Mark module complete

---

## 4. Exit Verification Checklist

Before attempting to exit the orchestrator session:

### 4.1 Plan Phase Exit

- [ ] USER_REQUIREMENTS.md exists and is complete
- [ ] All modules are defined
- [ ] All modules have acceptance criteria
- [ ] User has approved the plan
- [ ] `/approve-plan` has been executed

### 4.2 Orchestration Phase Exit

- [ ] All modules have status: complete
- [ ] All verification loops completed (4 per module)
- [ ] All GitHub Issues closed
- [ ] No pending assignments
- [ ] No unresolved issues

---

## Related References

- [Plan Phase Workflow](plan-phase-workflow.md) - Detailed Plan Phase steps
- [Orchestration Phase Workflow](orchestration-phase-workflow.md) - Detailed Orchestration Phase steps
- [Instruction Verification Protocol](instruction-verification-protocol.md) - 8-step verification
- [Proactive Progress Polling](proactive-progress-polling.md) - 6 mandatory questions
- [Instruction Update Verification Protocol](instruction-update-verification-protocol.md) - 5-step update protocol
