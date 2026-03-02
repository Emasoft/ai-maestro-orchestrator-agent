# Two-Phase Mode Workflow Diagram

## Contents

- 1. Visual Workflow Overview
- 2. Phase Transitions
- 3. Module Processing Loop

---

## 1. Visual Workflow Overview

```
USER GOAL
    |
    v
+-------------------+
| /start-planning   |  <-- Enter Plan Phase Mode
+--------+----------+
         |
         v
+-------------------+
| PLAN PHASE        |
| - Write specs     |
| - Design arch     |
| - Define modules  |
+--------+----------+
         |
         | (Stop hook blocks until plan complete)
         v
+-------------------+
| /approve-plan     |  <-- Transition + Create GitHub Issues
+--------+----------+
         |
         v
+-------------------+
| /start-orchestration
+--------+----------+
         |
         v
+------------------------+
| For EACH Module:       |
+------------------------+
         |
         v
+------------------------+
| 1. Assign to Agent     |
| 2. INSTRUCTION         |  <-- MANDATORY
|    VERIFICATION        |
|    (8-step protocol)   |
+------------------------+
         |
         v
+------------------------+
| 3. Agent Implements    |
| 4. Poll every 10-15min |  <-- MANDATORY 6 questions
| 5. IF UPDATES NEEDED:  |  <-- MANDATORY 5-step protocol
|    UPDATE VERIFICATION |
| 6. Review + 4-loops    |
+------------------------+
         |
         v
+-------------------+
| ALL MODULES       |
| COMPLETE          |
+-------------------+
         |
         | (Stop hook blocks until all complete)
         v
    EXIT ALLOWED
```

---

## 2. Phase Transitions

| From | To | Trigger | Condition |
|------|------|---------|-----------|
| None | Plan Phase | `/start-planning` | User provides goal |
| Plan Phase | Orchestration Phase | `/approve-plan` | All exit criteria met |
| Orchestration Phase | Complete | Stop hook passes | All modules complete + 4 verification loops |

---

## 3. Module Processing Loop

For each module during Orchestration Phase:

```
+-------------------+
| Assign Module     |
| /assign-module    |
+--------+----------+
         |
         v
+-------------------+
| Instruction       |  <-- 8-step protocol
| Verification      |
+--------+----------+
         |
         v
+-------------------+
| Agent Implements  |
+--------+----------+
         |
    +----+----+
    |         |
    v         v
+-------+  +--------+
| Poll  |  | Update |  <-- If requirements change
| 10-15 |  | Verif. |  <-- 5-step protocol
| min   |  | Proto. |
+---+---+  +----+---+
    |           |
    +-----------+
         |
         v
+-------------------+
| 4 Verification    |
| Loops             |
+--------+----------+
         |
         v
+-------------------+
| Mark Complete     |
+-------------------+
```

---

## Related References

- [Plan Phase Workflow](plan-phase-workflow.md) - Detailed Plan Phase steps
- [Orchestration Phase Workflow](orchestration-phase-workflow.md) - Detailed Orchestration Phase steps
- [Instruction Verification Protocol](instruction-verification-protocol.md) - 8-step verification
- [Proactive Progress Polling](proactive-progress-polling.md) - Polling protocol
- [Instruction Update Verification Protocol](instruction-update-verification-protocol.md) - Mid-implementation updates
