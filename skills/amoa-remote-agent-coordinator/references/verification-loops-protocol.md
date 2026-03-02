# 4-Verification-Loops Protocol Before PR


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 The Verification Flow](#20-the-verification-flow)
  - [2.1 Understanding the 5 PR Requests Cycle](#21-understanding-the-5-pr-requests-cycle)
- [3.0 Step-by-Step Implementation](#30-step-by-step-implementation)
  - [3.1 Including PR Notification Requirement in Task Assignment](#31-including-pr-notification-requirement-in-task-assignment)
  - [3.2 Responding to Agent PR Requests with Verification Messages](#32-responding-to-agent-pr-requests-with-verification-messages)
  - [3.3 Tracking Verification State Per Task](#33-tracking-verification-state-per-task)
- [Verification State Tracker](#verification-state-tracker)
  - [3.4 Waiting for Next PR Request After Each Verification Report](#34-waiting-for-next-pr-request-after-each-verification-report)
  - [3.5 Making the Final Decision on the 5th PR Request](#35-making-the-final-decision-on-the-5th-pr-request)
- [4.0 Summary: The 5 PR Requests](#40-summary-the-5-pr-requests)
- [5.0 Enforcement Rules](#50-enforcement-rules)
  - [5.1 What the Orchestrator MUST NOT Do](#51-what-the-orchestrator-must-not-do)
  - [5.2 What the Orchestrator MUST Do](#52-what-the-orchestrator-must-do)
- [6.0 Troubleshooting](#60-troubleshooting)
  - [Problem: Agent Creates PR Without Waiting for Approval](#problem-agent-creates-pr-without-waiting-for-approval)
  - [Problem: Agent Claims "No Issues Found" But Issues Exist](#problem-agent-claims-no-issues-found-but-issues-exist)
  - [Problem: Verification Loop Count Lost](#problem-verification-loop-count-lost)
  - [Problem: Agent Skipping Verification Steps](#problem-agent-skipping-verification-steps)
  - [Problem: Endless Loop - Issues Keep Appearing](#problem-endless-loop---issues-keep-appearing)

---

## Table of Contents

- 1.0 Overview
- 1.1 When the orchestrator requires verification before PR approval
- 1.2 When the agent requests permission to create a PR
- 2.0 The Verification Flow
- 2.1 Understanding the 5 PR requests cycle
- 2.2 When to send verification loop messages
- 3.0 Step-by-Step Implementation
- 3.1 Including PR notification requirement in task assignment
- 3.2 Responding to agent PR requests with verification messages
- 3.3 Tracking verification state per task
- 3.4 Waiting for next PR request after each verification report
- 3.5 Making the final decision on the 5th PR request
- 4.0 Verification Message Templates
- 4.1 When sending each verification loop message
- 4.2 When approving PR creation
- 4.3 When rejecting PR creation
- 5.0 Enforcement Rules
- 5.1 What the orchestrator MUST NOT do
- 5.2 What the orchestrator MUST do

---

## 1.0 Overview

**CRITICAL**: For EACH TASK assigned to an implementer, the orchestrator MUST require 4 verification loops BEFORE allowing the implementer to create a Pull Request.

This protocol ensures code quality by forcing the agent to self-review their implementation 4 times before submitting for final review.

---

## 2.0 The Verification Flow

### 2.1 Understanding the 5 PR Requests Cycle

```
+-------------------------------------------------------------------------+
| TASK ASSIGNMENT: Orchestrator tells agent:                              |
| "You MUST notify me BEFORE making any PR request for final verification"|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| AGENT WORKS ON TASK                                                      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| AGENT: "I'm done. Can I make a PR?"  (1st request)                      |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 1    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| AGENT checks, reports results                                            |
| AGENT: "Can I make a PR now?"  (2nd request)                            |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 2    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| AGENT checks, reports results                                            |
| AGENT: "Can I make a PR now?"  (3rd request)                            |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 3    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| AGENT checks, reports results                                            |
| AGENT: "Can I make a PR now?"  (4th request)                            |
| ORCHESTRATOR: "Check your changes for errors" <- VERIFICATION LOOP 4    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| AGENT checks, reports results                                            |
| AGENT: "Can I make a PR now?"  (5th request)                            |
|                                                                          |
| IF no issues discovered or left to fix in ALL 4 loops:                  |
|   ORCHESTRATOR: "APPROVED. You may create the PR."                      |
| ELSE:                                                                    |
|   ORCHESTRATOR: "Issues remain. Fix them and we restart verification."  |
+-------------------------------------------------------------------------+
```

---

## 3.0 Step-by-Step Implementation

### 3.1 Including PR Notification Requirement in Task Assignment

**Every task delegation message MUST include this instruction:**

```markdown
================================================================================
PR NOTIFICATION REQUIREMENT (MANDATORY)
================================================================================

BEFORE you create any Pull Request, you MUST:

1. Notify me that you believe the task is complete
2. Request my permission to create the PR
3. WAIT for my approval before creating the PR

DO NOT create a PR without my explicit approval.

When you are ready, message me with:
"Task {task_id} complete. Requesting permission to create PR."

I will then initiate a verification phase before approving the PR.
================================================================================
```

### 3.2 Responding to Agent PR Requests with Verification Messages

**Every time the agent asks "Can I make a PR?", respond with this FULL message (4 times total):**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "VERIFICATION LOOP {N}/4: {task_id} - MANDATORY REVIEW BEFORE PR",
  "priority": "high",
  "content": {
    "type": "verification-loop",
    "task_id": "GH-XX",
    "loop_number": N,
    "message": "VERIFICATION LOOP {N} of 4 - MANDATORY REVIEW BEFORE PR

You have requested permission to create a PR for task {task_id}. However, before
I can approve, you must complete verification loop {N} of 4.

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

This is verification loop {N} of 4. You cannot create a PR until all 4 loops complete.

After completing this review, report:
1. Issues found and fixed (with details)
2. Confirmation that verification loop {N} is complete

Then you may request PR permission again. {4-N} more loop(s) required."
  }
}
```

### 3.3 Tracking Verification State Per Task

The orchestrator MUST track how many times each agent has requested PR permission:

```markdown
## Verification State Tracker

| Agent | Task | PR Requests | Loops Completed | Next Action |
|-------|------|-------------|-----------------|-------------|
| helper-agent-1 | GH-42 | 2 | 2/4 | Waiting for 3rd PR request |
| helper-agent-2 | GH-43 | 5 | 4/4 | APPROVED - can create PR |
| helper-agent-3 | GH-44 | 1 | 1/4 | Waiting for 2nd PR request |
```

### 3.4 Waiting for Next PR Request After Each Verification Report

When the agent reports verification results:

**If issues were found and fixed:**
1. Acknowledge the fixes
2. **Wait for the agent to request PR permission again**
3. When they request, send next "Check your changes" message

**If no issues found:**
1. Acknowledge the clean review
2. **Wait for the agent to request PR permission again**
3. When they request, send next "Check your changes" message (still required!)

**IMPORTANT**: The orchestrator does NOT proactively send all 4 verification messages. The orchestrator RESPONDS to the agent's PR requests with "Check your changes for errors".

### 3.5 Making the Final Decision on the 5th PR Request

When the agent requests PR permission for the 5th time (after completing all 4 verification loops):

**If NO issues were discovered or remain unfixed across all 4 loops:**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "APPROVED: Create PR for {task_id}",
  "priority": "normal",
  "content": {
    "type": "pr-approval",
    "task_id": "GH-XX",
    "message": "All 4 verification loops complete for {task_id} with no outstanding issues.\n\nYou are now APPROVED to create the Pull Request.\n\nEnsure the PR description includes:\n1. Summary of changes\n2. How it was tested\n3. Any known limitations\n\nNotify me when the PR is created with the PR URL."
  }
}
```

**If issues WERE discovered and remain unfixed:**

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "NOT APPROVED: Issues remain in {task_id}",
  "priority": "high",
  "content": {
    "type": "pr-rejection",
    "task_id": "GH-XX",
    "message": "PR NOT APPROVED for {task_id}.\n\nThe following issues were discovered during verification but remain unfixed:\n\n{list of unfixed issues}\n\nFix these issues. Then we restart the 4-loop verification from the beginning.\n\nNotify me when you are ready to begin verification again."
  }
}
```

---

## 4.0 Summary: The 5 PR Requests

| PR Request # | Orchestrator Response |
|--------------|----------------------|
| 1st | "Check your changes for errors" (Loop 1) |
| 2nd | "Check your changes for errors" (Loop 2) |
| 3rd | "Check your changes for errors" (Loop 3) |
| 4th | "Check your changes for errors" (Loop 4) |
| 5th | "APPROVED" (if no issues) OR "NOT APPROVED - restart" (if issues remain) |

---

## 5.0 Enforcement Rules

### 5.1 What the Orchestrator MUST NOT Do

- Do NOT approve PR before the agent has made 5 PR requests
- Do NOT skip loops for "simple" changes
- Do NOT accept "I already reviewed it" instead of completing verification
- Do NOT approve PR if any issues remain unfixed
- Do NOT proactively send all verification messages (must wait for PR requests)

### 5.2 What the Orchestrator MUST Do

- MUST include PR notification requirement in EVERY task assignment
- MUST respond to each PR request with "Check your changes for errors" (4 times)
- MUST track PR request count per task
- MUST only approve on 5th request if ALL issues are resolved
- MUST restart the 4-loop count if issues remain after loop 4

---

## 6.0 Troubleshooting

### Problem: Agent Creates PR Without Waiting for Approval

**Symptoms**: PR created before 4 verification loops completed.

**Solution**:
1. Close the unauthorized PR
2. Send message using the `agent-messaging` skill reminding agent of PR notification requirement
3. Include PR notification requirement text in message
4. Agent must restart from loop 1
5. If repeated, escalate to user about agent compliance

### Problem: Agent Claims "No Issues Found" But Issues Exist

**Symptoms**: Agent reports clean verification but orchestrator sees obvious issues.

**Solution**:
1. Explicitly list the issues you observe
2. Ask agent to re-examine specific files/functions
3. Provide concrete examples of what to look for
4. If agent cannot find issues after 3 prompts, consider reassigning code review

### Problem: Verification Loop Count Lost

**Symptoms**: Orchestrator unsure how many loops completed.

**Solution**:
1. Check session memory for verification state tracker
2. Check GitHub issue comments for loop progress
3. If unclear, restart from loop 1 (conservative approach)
4. Update tracker after each loop to prevent recurrence

### Problem: Agent Skipping Verification Steps

**Symptoms**: Agent responses are shallow, not actually reviewing code.

**Solution**:
1. Request specific evidence of review (file names, line numbers checked)
2. Ask pointed questions about specific code sections
3. If agent cannot answer, they did not review
4. Send more detailed verification checklist

### Problem: Endless Loop - Issues Keep Appearing

**Symptoms**: After 4+ loop restarts, issues keep being found.

**Solution**:
1. Evaluate if task scope is too large
2. Consider breaking task into smaller PRs
3. Review if acceptance criteria are clear
4. Escalate to user if fundamentally misaligned

---

## Per-Loop Differentiated Criteria and Decision Trees

### Per-Loop Focus Areas

Each verification loop has a progressively narrower focus:

| Loop | Focus Area | What to Check | Pass Criteria |
|------|-----------|---------------|---------------|
| 1 | Functional completeness | All requirements met, core logic works, tests pass | All checklist items verified |
| 2 | Code quality | Style, naming, documentation, error handling | No major quality issues |
| 3 | Edge cases | Boundary conditions, error paths, concurrency | No unhandled edge cases found |
| 4 | Integration readiness | API compatibility, dependency versions, config | Ready for EIA review |

### Verification Loop Outcome Decision Tree

```
Verification loop N completed (N = 1 to 4)
├─ Did agent find issues in this loop?
│   ├─ Yes → Are issues within agent's ability to fix?
│   │         ├─ Yes → Send "Fix and re-verify" instruction
│   │         │         → Agent fixes → Re-run same loop N
│   │         │         ├─ Issues resolved → Proceed to loop N+1
│   │         │         └─ Issues persist after 2 fix attempts → Escalate to ECOS
│   │         └─ No (needs architectural change) → Escalate to ECOS for EAA
│   │             → Pause verification → Wait for design guidance
│   └─ No (clean loop) → Is this the final loop (loop 4)?
│       ├─ Yes → All 4 loops passed → Move task to "ai-review" for EIA
│       │         → Send completion summary with all loop results
│       └─ No → Proceed to loop N+1 with narrower focus
│
After loop 4 fails for the 5th cumulative attempt:
├─ Compile full failure history (all loops, all attempts)
├─ Send detailed failure report to ECOS
├─ Recommend: reassign to different agent OR request EAA architecture review
└─ Do NOT attempt loop 5+ without ECOS approval
```

**Cross-reference**: For detailed verification feedback message templates for loops 2-4, see `verification-feedback-templates.md`.
