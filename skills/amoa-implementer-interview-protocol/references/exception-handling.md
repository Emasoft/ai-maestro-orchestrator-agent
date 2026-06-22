# Exception Handling

> **In-development issue dialog — canonical definition lives elsewhere.** The
> back-and-forth that happens when an implementer hits an issue, ambiguity,
> blocker, or design flaw *while coding* (the in-development loop, dialog loop b)
> is defined once in `docs/FULL_PROJECT_WORKFLOW.md` → **Step 18.5: In-Dev Issue
> Dialog (MEMBER ⇄ AMOA)**. The cases below that involve that loop (§1, §2, §6)
> POINT to that canonical description rather than restating it — there is no
> parallel copy to drift out of sync. The remaining cases (§4, §5, §7, §8, §9)
> are interview-protocol-specific exceptions and are defined here.

## Table of Contents

- [1. Implementer Disagrees with Requirements](#1-implementer-disagrees-with-requirements)
- [2. Architect Recommends Design Change](#2-architect-recommends-design-change)
- [3. User Approves Requirement Change](#3-user-approves-requirement-change)
- [4. Implementer Never Acknowledges](#4-implementer-never-acknowledges)
- [5. Implementer Misunderstands Task](#5-implementer-misunderstands-task)
- [6. Implementer Has Design Concerns](#6-implementer-has-design-concerns)
- [7. Implementer Reports Incomplete Work](#7-implementer-reports-incomplete-work)
- [8. Tests Fail in Post-Task Interview](#8-tests-fail-in-post-task-interview)
- [9. Implementer Creates PR Before Approval](#9-implementer-creates-pr-before-approval)

## 1. Implementer Disagrees with Requirements

This is an instance of the **in-development issue dialog** — route it per the
canonical loop in `docs/FULL_PROJECT_WORKFLOW.md` → *Step 18.5: In-Dev Issue
Dialog*. In short:

1. Document the disagreement.
2. Mutable requirement → AMOA decides pragmatically and records the rationale.
   Immutable (user-specified) requirement → escalate via AMCOS → AMAMA → USER
   (see [escalation-messages.md](./escalation-messages.md) → *Immutable
   Requirement Issues*). Do NOT modify an immutable requirement without USER
   approval.
3. WAIT for resolution; do NOT allow implementation to proceed with unapproved
   changes.

## 2. Architect Recommends Design Change

This is the resolution side of the **in-development issue dialog** (a
design-change-request was raised to AMAA — see `docs/FULL_PROJECT_WORKFLOW.md` →
*Step 18.5* and *Steps 15–16*). When the Architect approves a design change:

1. Update the design document.
2. Re-interview the implementer with the new design (re-run the pre-task
   handshake so the new files/domains and NPT/EHT are re-confirmed).
3. Document the change in the issue.

## 3. User Approves Requirement Change

If user approves changing an immutable requirement:

1. Document the approval with timestamp
2. Update the requirement document
3. Update the task with new requirement
4. Re-interview implementer
5. Proceed with updated requirements

## 4. Implementer Never Acknowledges

**Cause**: Agent unresponsive or offline

**Solution**:
1. Send reminder after 5 minutes
2. Check AI Maestro agent status
3. Escalate to **amoa-progress-monitoring**
4. Consider reassignment if no response after 3 attempts

## 5. Implementer Misunderstands Task

**Cause**: Unclear requirements or insufficient context

**Solution**:
1. Clarify requirements
2. Update handoff document
3. Re-send interview questions
4. Verify understanding before approving PROCEED

## 6. Implementer Has Design Concerns

**Cause**: Architectural incompatibility surfaced during the pre-task handshake
or mid-development. This is the entry point of the **in-development issue
dialog** — route it per `docs/FULL_PROJECT_WORKFLOW.md` → *Step 18.5: In-Dev
Issue Dialog*:

1. AMOA sends a design-change-request to the Architect (AMAA) — AMOA → AMAA,
   DIRECT (see [escalation-messages.md](./escalation-messages.md) → *Design
   Issues → Architect*).
2. WAIT for the architect decision; never silently improvise around the flaw.
3. Update the design and re-interview if the design changed.

## 7. Implementer Reports Incomplete Work

**Cause**: Rushed or blocked during implementation

**Solution**:
1. Send REVISE with specific missing items
2. Use post-task verification questions
3. Do NOT approve PR until complete

## 8. Tests Fail in Post-Task Interview

**Cause**: Code doesn't meet acceptance criteria

**Solution**:
1. Send REVISE message
2. Require passing tests before PR approval
3. Re-verify after fixes

## 9. Implementer Creates PR Before Approval

**Cause**: Protocol violation

**Solution**:
1. Remind implementer of protocol
2. Review PR manually (do not auto-merge)
3. Update process training if pattern repeats
