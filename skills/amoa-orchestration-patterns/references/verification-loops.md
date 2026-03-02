# MANDATORY: 4-Verification-Loops Before PR


## Contents

- [Table of Contents](#table-of-contents)
- [1. Overview](#1-overview)
  - [1.1 Why 4 Verification Loops Are Required](#11-why-4-verification-loops-are-required)
  - [1.2 The Precise Flow Diagram](#12-the-precise-flow-diagram)
- [2. Step 1: At Task Assignment](#2-step-1-at-task-assignment)
  - [2.1 PR Notification Requirement Template](#21-pr-notification-requirement-template)
  - [2.2 Including in Every Delegation](#22-including-in-every-delegation)
- [3. Step 2: Full Verification Message](#3-step-2-full-verification-message)
  - [3.1 When to Send This Message](#31-when-to-send-this-message)
  - [3.2 Verification Message Template (Send 4 Times)](#32-verification-message-template-send-4-times)
  - [3.3 What the Agent Must Check](#33-what-the-agent-must-check)
- [4. Step 3: Track PR Requests Per Task](#4-step-3-track-pr-requests-per-task)
  - [4.1 Tracking Table Format](#41-tracking-table-format)
  - [4.2 Sample Tracking Table](#42-sample-tracking-table)
- [5. Step 4: On 5th Request - Final Decision](#5-step-4-on-5th-request---final-decision)
  - [5.1 Approval Conditions](#51-approval-conditions)
  - [5.2 Summary Table](#52-summary-table)
- [6. Enforcement Rules](#6-enforcement-rules)
  - [6.1 What is NEVER Allowed](#61-what-is-never-allowed)
  - [6.2 What is ALWAYS Required](#62-what-is-always-required)
- [Troubleshooting](#troubleshooting)
  - [Agent Creates PR Without Approval](#agent-creates-pr-without-approval)
  - [Agent Says "No Issues Found" Every Loop](#agent-says-no-issues-found-every-loop)
  - [Issues Persist After 4 Loops](#issues-persist-after-4-loops)
- [See Also](#see-also)

---

## Table of Contents

- 1. Overview
  - 1.1 Why 4 Verification Loops Are Required
  - 1.2 The Precise Flow Diagram
- 2. Step 1: At Task Assignment
  - 2.1 PR Notification Requirement Template
  - 2.2 Including in Every Delegation
- 3. Step 2: Full Verification Message
  - 3.1 When to Send This Message
  - 3.2 Verification Message Template (Send 4 Times)
  - 3.3 What the Agent Must Check
- 4. Step 3: Track PR Requests Per Task
  - 4.1 Tracking Table Format
  - 4.2 Sample Tracking Table
- 5. Step 4: On 5th Request - Final Decision
  - 5.1 Approval Conditions
  - 5.2 Summary Table
- 6. Enforcement Rules
  - 6.1 What is NEVER Allowed
  - 6.2 What is ALWAYS Required

---

## 1. Overview

### 1.1 Why 4 Verification Loops Are Required

**CRITICAL**: For EACH TASK assigned to an implementer, the orchestrator MUST require 4 verification loops BEFORE allowing the implementer to create a Pull Request.

This catches:
- Bugs missed in initial implementation
- Edge cases not covered by tests
- Security vulnerabilities
- Performance issues
- Code quality problems
- Incomplete implementations

Without verification loops, agents rush to create PRs with bugs.

### 1.2 The Precise Flow Diagram

```
+---------------------------------------------------------------------------+
| TASK ASSIGNMENT: Orchestrator tells agent:                                |
| "You MUST notify me BEFORE making any PR request for final verification"  |
+---------------------------------------------------------------------------+
                                    |
                                    v
                     [ AGENT WORKS ON TASK ]
                                    |
                                    v
+---------------------------------------------------------------------------+
| AGENT: "I'm done. Can I make a PR?"  (1st request)                        |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 1     |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
| AGENT: "Can I make a PR now?"  (2nd request)                              |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 2     |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
| AGENT: "Can I make a PR now?"  (3rd request)                              |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 3     |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
| AGENT: "Can I make a PR now?"  (4th request)                              |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 4     |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
| AGENT: "Can I make a PR now?"  (5th request)                              |
|                                                                           |
| IF no issues discovered or left to fix in ALL 4 loops:                    |
|   ORCHESTRATOR: "APPROVED. You may create the PR."                        |
| ELSE:                                                                     |
|   ORCHESTRATOR: "Issues remain. Fix them and we restart verification."   |
+---------------------------------------------------------------------------+
```

---

## 2. Step 1: At Task Assignment

### 2.1 PR Notification Requirement Template

**PROACTIVELY include in EVERY task delegation:**

```
================================================================================
PR NOTIFICATION REQUIREMENT (MANDATORY)
================================================================================

BEFORE you create any Pull Request, you MUST:

1. Notify me that you believe the task is complete
2. Request my permission to create the PR
3. WAIT for my approval before creating the PR

DO NOT create a PR without my explicit approval.

When ready, message: "Task {task_id} complete. Requesting permission to create PR."
================================================================================
```

### 2.2 Including in Every Delegation

This template MUST appear in every task assignment message. If you forget to include it, the agent may create a PR without verification loops.

---

## 3. Step 2: Full Verification Message

### 3.1 When to Send This Message

Send this message every time the agent asks "Can I make a PR?" for the first 4 requests.

### 3.2 Verification Message Template (Send 4 Times)

```
VERIFICATION LOOP [N] of 4 - MANDATORY REVIEW BEFORE PR

You have requested permission to create a PR for task {task_id}. However, before
I can approve, you must complete verification loop [N] of 4.

Examine your implementation in depth. Check for:

- Bugs, errors and missing functionality
- Edge cases not covered by tests
- Wrong references and violations of the specifications
- Incongruences and inconsistent naming
- Redundant code and duplicated logic
- Partial or incomplete implementation
- Missing error handling and input validation
- Security vulnerabilities (injection, XSS, auth bypass, data exposure)
- Performance issues (N+1 queries, unbounded loops, memory leaks)
- Workarounds, hacks, fallbacks and cheap solutions instead of proper
  architectural fixes of the root causes and code improvements
- Hardcoded values that should be configurable
- TODO/FIXME/HACK comments left in code
- Dead code and unused imports
- Outdated comments and unverified assumptions
- Non up-to-date documentation
- Logical flaws and adherence to the task requirements
- Test coverage gaps and untested code paths
- Integration issues with existing code
- Logging and debugging statements left in production code

Audit your implementation for potential alternatives and things you may have missed.
Fix ALL the issues you find. Iterate until no other issues are found.

This is verification loop [N] of 4. You cannot create a PR until all 4 loops complete.

After completing this review, report:
1. Issues found and fixed (with details)
2. Confirmation that verification loop [N] is complete

Then you may request PR permission again. [4-N] more loop(s) required.
```

### 3.3 What the Agent Must Check

| Category | Items to Check |
|----------|----------------|
| Correctness | Bugs, errors, missing functionality |
| Edge Cases | Uncovered edge cases, boundary conditions |
| Specifications | Wrong references, spec violations |
| Naming | Inconsistent naming, unclear variable names |
| Duplication | Redundant code, duplicated logic |
| Completeness | Partial implementation, missing features |
| Error Handling | Missing validation, unhandled exceptions |
| Security | Injection, XSS, auth bypass, data exposure |
| Performance | N+1 queries, unbounded loops, memory leaks |
| Quality | Workarounds, hacks, hardcoded values |
| Cleanup | TODO/FIXME comments, dead code, unused imports |
| Documentation | Outdated comments, unverified assumptions |
| Testing | Coverage gaps, untested code paths |
| Integration | Issues with existing code |
| Debug Code | Logging/debugging statements in production |

---

## 4. Step 3: Track PR Requests Per Task

### 4.1 Tracking Table Format

Maintain a table tracking PR requests for each task:

| Column | Description |
|--------|-------------|
| Agent | Agent name or session |
| Task | Task ID or GitHub issue |
| PR Requests | Number of times agent asked for PR |
| Loops Completed | X/4 verification loops done |
| Next Action | What happens next |

### 4.2 Sample Tracking Table

| Agent | Task | PR Requests | Loops Completed | Next Action |
|-------|------|-------------|-----------------|-------------|
| helper-1 | GH-42 | 2 | 2/4 | Waiting for 3rd PR request |
| helper-2 | GH-43 | 5 | 4/4 | APPROVED |
| helper-3 | GH-44 | 1 | 1/4 | Waiting for 2nd PR request |

---

## 5. Step 4: On 5th Request - Final Decision

### 5.1 Approval Conditions

| Condition | Response |
|-----------|----------|
| No issues remain after 4 loops | "APPROVED. You may create the PR." |
| Issues remain after 4 loops | "NOT APPROVED. Fix issues. Restart verification from loop 1." |

### 5.2 Summary Table

| PR Request # | Orchestrator Response |
|--------------|----------------------|
| 1st | "Check your changes for errors" (Loop 1) |
| 2nd | "Check your changes for errors" (Loop 2) |
| 3rd | "Check your changes for errors" (Loop 3) |
| 4th | "Check your changes for errors" (Loop 4) |
| 5th | APPROVED (if clean) OR RESTART (if issues) |

---

## 6. Enforcement Rules

### 6.1 What is NEVER Allowed

- NEVER approve PR before the agent has made 5 PR requests
- NEVER skip loops for "simple" changes
- NEVER proactively send all verification messages (wait for PR requests)
- NEVER approve if issues remain unfixed
- NEVER combine loops or do 2 at once

### 6.2 What is ALWAYS Required

- ALWAYS include PR notification requirement in task assignments
- ALWAYS respond to each PR request with "Check your changes for errors"
- ALWAYS track PR request count per task
- ALWAYS restart from loop 1 if issues remain after loop 4
- ALWAYS require 4 complete loops before approval

---

## Troubleshooting

### Agent Creates PR Without Approval

If an agent creates a PR without completing verification loops:
1. Close or request changes on the PR immediately
2. Message agent: "PR created without approval. Complete 4 verification loops first."
3. Track this as a violation for agent evaluation

### Agent Says "No Issues Found" Every Loop

If agent reports no issues in every loop:
1. Verify the agent is actually checking (not just saying so)
2. Request specific evidence of checks performed
3. Consider running your own verification

### Issues Persist After 4 Loops

If issues remain after 4 loops:
1. Do NOT approve the PR
2. Send: "Issues remain. Fix them and restart verification from loop 1."
3. Track additional loops as "restart cycles"

---

## See Also

- [progress-monitoring.md](progress-monitoring.md) - Proactive monitoring protocol
- [agent-selection-guide.md](agent-selection-guide.md) - Which agent for which task
- [orchestrator-guardrails.md](orchestrator-guardrails.md) - Orchestrator role boundaries

---

## Verification

After completing verification loops:

- [ ] **Verify**: confirm all 4 verification loop results were recorded
- [ ] **Verify**: confirm message delivery for each loop via the `agent-messaging` skill's sent messages feature
- [ ] **Verify**: confirm PR approval or rejection decision was communicated to the agent
- [ ] **Verify**: confirm EIA was notified if PR was approved for code review
