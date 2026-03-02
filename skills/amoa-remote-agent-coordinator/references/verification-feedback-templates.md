# Verification Loop 2-4 Feedback Templates

This document provides differentiated feedback message templates for verification loops 2 through 4, plus the restart notification and completion summary. Each loop has a progressively deeper focus area so that agents address distinct quality dimensions on each pass rather than repeating the same generic review.

---

## Contents

- 1. Verification Loop 2 Feedback (EOA sends to Agent) - when loop 1 found issues that need targeted re-verification
- 2. Verification Loop 3 Feedback (EOA sends to Agent) - when deeper review of edge cases and error handling is needed
- 3. Verification Loop 4 Feedback (EOA sends to Agent) - when final pre-PR quality gate on code style, docs, and security is needed
- 4. Verification Restart Notification (EOA sends to Agent) - when the 5th check still finds unresolved issues and the cycle must restart
- 5. Verification Completion Summary (EOA sends to ECOS) - when all loops pass and the task is ready for PR
- 6. Verification Loop Outcome Decision Tree - when deciding the next action after any loop completes

---

## 1. Verification Loop 2 Feedback (EOA sends to Agent)

### When to Use

Send this message when the agent requests PR permission for the second time, after completing verification loop 1. Loop 2 focuses on confirming that loop 1 issues are fixed and checking for regressions introduced by those fixes.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-orchestrator",
  "to": "<agent-session-name>",
  "subject": "VERIFICATION LOOP 2/4: {task_id} - FIX VERIFICATION AND REGRESSION CHECK",
  "priority": "high",
  "content": {
    "type": "verification-loop",
    "message": "VERIFICATION LOOP 2 of 4 - FIX VERIFICATION AND REGRESSION CHECK\n\nLoop 1 identified specific issues in your implementation. This loop focuses on two things:\n\n1. CONFIRM FIXES: Verify that every issue from loop 1 has been properly resolved. Do not just claim they are fixed - re-run the relevant tests, re-read the changed code, and confirm the fix addresses the root cause.\n\n2. REGRESSION CHECK: Your fixes may have introduced new problems. Re-test all functionality that existed before your fixes. Check that no previously passing tests now fail. Check that no previously working features are broken.\n\nAfter completing this review, report your findings and request PR permission again. 2 more loops required after this one.",
    "data": {
      "loop_number": 2,
      "previous_issues": ["<list each issue found in loop 1>"],
      "focus_areas": ["fix verification", "regression check"],
      "specific_checks": [
        "Re-run all tests that were failing in loop 1 and confirm they pass",
        "Re-read every file you modified as a fix and verify correctness",
        "Run the full test suite to detect regressions",
        "Check that no new warnings or linting errors appeared",
        "Verify that each fix addresses the root cause, not just the symptom"
      ]
    }
  }
}
```

### Expected Agent Response Template

```json
{
  "from": "<agent-session-name>",
  "to": "eoa-orchestrator",
  "subject": "VERIFICATION LOOP 2 COMPLETE: {task_id}",
  "priority": "normal",
  "content": {
    "type": "verification-report",
    "message": "Verification loop 2 complete. Reporting results.",
    "data": {
      "loop_number": 2,
      "issues_fixed": [
        {"issue": "<description>", "fix": "<what was done>", "verified_by": "<test name or manual check>"}
      ],
      "new_issues_found": [
        {"issue": "<description>", "severity": "critical|major|minor", "location": "<file:line>"}
      ],
      "evidence": {
        "test_results": "<pass/fail summary with counts>",
        "screenshots": ["<path if applicable>"],
        "files_reviewed": ["<list of files re-examined>"]
      }
    }
  }
}
```

### Decision Tree

```
Loop 2 report received
├─ Are all loop 1 issues confirmed fixed?
│   ├─ Yes
│   │   ├─ Were new regressions found?
│   │   │   ├─ Yes → Record new issues, agent must fix before next PR request
│   │   │   └─ No → Clean pass, wait for agent to request PR permission (triggers loop 3)
│   │   └─ Is evidence thorough (test results, file list)?
│   │       ├─ Yes → Accept report
│   │       └─ No → Reject, request deeper evidence with specific test names
│   └─ No (some loop 1 issues remain)
│       ├─ Agent claims fixed but evidence is weak → Request re-verification with specific file:line references
│       └─ Agent acknowledges not fixed → Agent must fix before next PR request
```

---

## 2. Verification Loop 3 Feedback (EOA sends to Agent)

### When to Use

Send this message when the agent requests PR permission for the third time, after completing verification loop 2. Loop 3 focuses on deeper review: edge cases, error handling, and integration points that shallow reviews miss.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-orchestrator",
  "to": "<agent-session-name>",
  "subject": "VERIFICATION LOOP 3/4: {task_id} - EDGE CASES AND ERROR HANDLING",
  "priority": "high",
  "content": {
    "type": "verification-loop",
    "message": "VERIFICATION LOOP 3 of 4 - EDGE CASES AND ERROR HANDLING\n\nLoops 1 and 2 covered basic correctness and regression. This loop requires you to think adversarially about your implementation.\n\n1. EDGE CASES: What happens with empty inputs, null values, maximum-size data, concurrent access, unexpected types? Test each boundary condition.\n\n2. ERROR PATHS: Trace every error path in your code. Does each error get caught, logged, and surfaced properly? Are there silent failures?\n\n3. PERFORMANCE: Are there unbounded loops, N+1 query patterns, or operations that scale poorly? Check for memory leaks in long-running processes.\n\n4. INTEGRATION POINTS: Does your code interact correctly with other modules? Are API contracts honored? Do shared state mutations cause conflicts?\n\nAfter completing this review, report your findings and request PR permission again. 1 more loop required after this one.",
    "data": {
      "loop_number": 3,
      "cumulative_issues": ["<all issues from loops 1 and 2, with status resolved/unresolved>"],
      "focus_areas": ["edge cases", "error paths", "performance", "integration points"],
      "specific_checks": [
        "Test with empty, null, and boundary-value inputs",
        "Trace every error handling path and verify it behaves correctly",
        "Check for unbounded loops, N+1 queries, and memory leaks",
        "Verify API contracts with upstream and downstream modules",
        "Test concurrent access if applicable",
        "Verify timeout and retry logic handles failures gracefully"
      ]
    }
  }
}
```

### Expected Agent Response Template

```json
{
  "from": "<agent-session-name>",
  "to": "eoa-orchestrator",
  "subject": "VERIFICATION LOOP 3 COMPLETE: {task_id}",
  "priority": "normal",
  "content": {
    "type": "verification-report",
    "message": "Verification loop 3 complete. Reporting results.",
    "data": {
      "loop_number": 3,
      "issues_fixed": [
        {"issue": "<description>", "fix": "<what was done>", "verified_by": "<test name or manual check>"}
      ],
      "new_issues_found": [
        {"issue": "<description>", "severity": "critical|major|minor", "category": "edge-case|error-handling|performance|integration", "location": "<file:line>"}
      ],
      "evidence": {
        "test_results": "<pass/fail summary with counts>",
        "edge_cases_tested": ["<list of specific edge cases checked>"],
        "error_paths_traced": ["<list of error paths verified>"],
        "files_reviewed": ["<list of files re-examined>"]
      }
    }
  }
}
```

### Decision Tree

```
Loop 3 report received
├─ Were edge case or error handling issues found?
│   ├─ Yes → Are they fixed in this same report?
│   │   ├─ Yes, with evidence → Accept, wait for next PR request (triggers loop 4)
│   │   └─ No, or evidence is weak → Agent must fix and provide evidence before next PR request
│   └─ No issues found
│       ├─ Did agent provide specific edge cases tested and error paths traced?
│       │   ├─ Yes (thorough evidence) → Accept clean pass, wait for next PR request
│       │   └─ No (vague report) → Reject, require specific edge case list and error path trace
│       └─ Is the implementation inherently simple (few code paths)?
│           ├─ Yes → Accept brief evidence if it covers all paths
│           └─ No → Require detailed breakdown
├─ Are any cumulative issues from loops 1-2 still unresolved?
│   ├─ Yes → Is the issue design-related (requires architectural change)?
│   │   ├─ Yes → Escalate to EAA (Architect Agent) for guidance
│   │   └─ No → Provide specific guidance, agent must fix before next PR request
│   └─ No → Proceed normally
```

---

## 3. Verification Loop 4 Feedback (EOA sends to Agent)

### When to Use

Send this message when the agent requests PR permission for the fourth time, after completing verification loop 3. Loop 4 is the final deep review before the 5th PR request triggers the approval decision. It focuses on code quality, documentation, test coverage, and security.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-orchestrator",
  "to": "<agent-session-name>",
  "subject": "VERIFICATION LOOP 4/4: {task_id} - FINAL QUALITY GATE",
  "priority": "high",
  "content": {
    "type": "verification-loop",
    "message": "VERIFICATION LOOP 4 of 4 - FINAL QUALITY GATE BEFORE PR DECISION\n\nThis is the last verification loop. After this, your next PR request triggers the final approval decision. Make this review count.\n\n1. CODE STYLE: Does the code follow the project's style guide? Are variable names clear and consistent? Is the code readable without comments explaining what it does?\n\n2. DOCUMENTATION: Are all public functions documented? Are complex algorithms explained? Is the README or relevant docs updated to reflect your changes?\n\n3. TEST COVERAGE: Are all new code paths covered by tests? Are there negative tests for expected failures? Do tests validate behavior, not implementation?\n\n4. SECURITY: Check for injection vulnerabilities, improper input validation, hardcoded secrets, insecure defaults, and data exposure. Run any available security linters.\n\n5. PR READINESS: Write a draft PR description. If you cannot clearly articulate what changed and why, the code may not be ready.\n\nAfter completing this review, report your findings and request PR permission one final time. This is the last loop - your next request triggers the approval decision.",
    "data": {
      "loop_number": 4,
      "cumulative_issues": ["<all issues from loops 1-3, with status resolved/unresolved>"],
      "focus_areas": ["code style", "documentation", "test coverage", "security"],
      "pr_readiness_checklist": [
        "All acceptance criteria met",
        "All tests passing",
        "No TODO/FIXME/HACK comments remaining",
        "No dead code or unused imports",
        "No hardcoded values that should be configurable",
        "No debugging or logging statements left in production paths",
        "Documentation updated to reflect changes",
        "PR description draft prepared"
      ]
    }
  }
}
```

### Expected Agent Response Template

```json
{
  "from": "<agent-session-name>",
  "to": "eoa-orchestrator",
  "subject": "VERIFICATION LOOP 4 COMPLETE: {task_id}",
  "priority": "normal",
  "content": {
    "type": "verification-report",
    "message": "Verification loop 4 complete. Final quality gate results.",
    "data": {
      "loop_number": 4,
      "issues_fixed": [
        {"issue": "<description>", "fix": "<what was done>", "verified_by": "<test name or manual check>"}
      ],
      "new_issues_found": [
        {"issue": "<description>", "severity": "critical|major|minor", "category": "style|docs|test-coverage|security", "location": "<file:line>"}
      ],
      "all_issues_resolved": true,
      "pr_ready": true,
      "remaining_concerns": ["<any minor items that do not block PR but should be noted>"],
      "evidence": {
        "test_results": "<pass/fail summary with counts>",
        "test_coverage_percent": "<percent if available>",
        "security_scan_results": "<clean or list of findings>",
        "pr_description_draft": "<brief summary of planned PR description>"
      }
    }
  }
}
```

### Decision Tree

```
Loop 4 report received
├─ all_issues_resolved == true AND pr_ready == true?
│   ├─ Yes → Is evidence thorough (test results, coverage, security scan)?
│   │   ├─ Yes → Record clean final pass, wait for 5th PR request to approve
│   │   └─ No → Reject, request complete evidence before accepting loop 4 as done
│   └─ No → Are remaining issues critical?
│       ├─ Critical issues remain → These must be fixed before 5th PR request
│       │   └─ Agent fixes and re-submits loop 4 report (does not advance to 5th request)
│       └─ Only minor or cosmetic issues remain
│           ├─ Note as known issues in PR description
│           └─ Accept loop 4, allow 5th PR request to proceed to approval decision
```

---

## 4. Verification Restart Notification (EOA sends to Agent)

### When to Use

Send this message when the 5th PR request (the approval decision point) reveals that critical issues remain unresolved after all 4 verification loops. The entire 4-loop verification cycle must restart from loop 1.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-orchestrator",
  "to": "<agent-session-name>",
  "subject": "VERIFICATION RESTART: {task_id} - UNRESOLVED ISSUES REQUIRE NEW CYCLE",
  "priority": "high",
  "content": {
    "type": "verification-restart",
    "message": "PR NOT APPROVED for {task_id}. Critical issues remain after all 4 verification loops.\n\nThe verification cycle is restarting from loop 1. You must fix ALL listed issues before requesting PR permission again.\n\nWhen you have addressed every issue below, notify me that you are ready to begin the verification cycle again.",
    "data": {
      "restart_reason": "<brief explanation of why issues persist, e.g., 'Fixes introduced new regressions' or 'Root cause not addressed'>",
      "cumulative_unresolved_issues": [
        {"issue": "<description>", "first_found_in_loop": 1, "severity": "critical|major", "location": "<file:line>"}
      ],
      "guidance_for_restart": "<specific guidance, e.g., 'Focus on the authentication token expiry logic - the fix in loop 2 masked the original bug rather than resolving it. Trace the token lifecycle from creation to validation.'>"
    }
  }
}
```

### Expected Agent Response Template

```json
{
  "from": "<agent-session-name>",
  "to": "eoa-orchestrator",
  "subject": "ACK: VERIFICATION RESTART FOR {task_id}",
  "priority": "normal",
  "content": {
    "type": "ack",
    "message": "Acknowledged. I will address all listed issues and notify you when ready to restart verification.",
    "data": {
      "issues_acknowledged": true,
      "planned_approach": "<brief description of how agent plans to address the issues>"
    }
  }
}
```

### Decision Tree

```
5th PR request received, issues remain
├─ Are unresolved issues critical (blocking correctness or security)?
│   ├─ Yes → Send restart notification, reset loop count to 0
│   │   ├─ Agent acknowledges → Wait for agent to notify readiness
│   │   └─ Agent does not acknowledge within 10 minutes → Re-send with urgent priority
│   └─ No (only minor or cosmetic)
│       ├─ Note as known issues in PR description
│       └─ Approve PR with conditions listed
```

---

## 5. Verification Completion Summary (EOA sends to ECOS)

### When to Use

Send this message to the Chief of Staff (ECOS) after all verification loops pass and the PR is approved (or created). This provides ECOS with a summary of the verification process for task tracking and team health metrics.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-orchestrator",
  "to": "ecos-chief-of-staff",
  "subject": "VERIFICATION COMPLETE: {task_id} - {module_id}",
  "priority": "normal",
  "content": {
    "type": "status",
    "message": "Verification complete for {task_id}. All loops passed. PR approved.",
    "data": {
      "module_id": "<module name, e.g., 'auth-core'>",
      "task_id": "<GitHub issue number, e.g., 'GH-42'>",
      "agent_name": "<agent session name>",
      "total_loops": 4,
      "restarts": 0,
      "issues_per_loop": [
        {"loop": 1, "issues_found": 3, "issues_fixed": 3},
        {"loop": 2, "issues_found": 1, "issues_fixed": 1},
        {"loop": 3, "issues_found": 0, "issues_fixed": 0},
        {"loop": 4, "issues_found": 0, "issues_fixed": 0}
      ],
      "final_status": "approved",
      "pr_url": "<pull request URL or 'pending creation'>",
      "time_spent": "<estimated total time from first PR request to approval>"
    }
  }
}
```

### Decision Tree

```
Verification approved
├─ Was the verification clean (zero restarts, few issues)?
│   ├─ Yes → Send summary with normal priority
│   └─ No (multiple restarts or many issues) → Send summary with high priority
│       └─ Include note: "Agent may benefit from clearer task specifications or smaller scope"
├─ Was the PR already created by the agent?
│   ├─ Yes → Include pr_url in summary
│   └─ No → Set pr_url to "pending creation", update ECOS when PR URL is available
```

---

## 6. Verification Loop Outcome Decision Tree

### When to Use

Use this decision tree after any verification loop completes (loops 1 through 4) to determine the correct next action. This is the master decision logic that governs the entire verification feedback flow.

```
Verification loop N complete (agent submitted report)
│
├─ Were issues found in loop N?
│   │
│   ├─ YES: Issues were found
│   │   │
│   │   ├─ Is loop N < 4?
│   │   │   │
│   │   │   ├─ YES: More loops remain
│   │   │   │   │
│   │   │   │   ├─ Record all issues with file:line references
│   │   │   │   ├─ Wait for agent to request PR permission again
│   │   │   │   └─ When agent requests → Send feedback for loop N+1 with focus on fixes
│   │   │   │       │
│   │   │   │       ├─ Agent fixes all issues in next loop
│   │   │   │       │   └─ Proceed to next loop normally
│   │   │   │       │
│   │   │   │       └─ Agent cannot fix some issues
│   │   │   │           │
│   │   │   │           ├─ Is the issue design-related (requires architectural change)?
│   │   │   │           │   ├─ YES → Escalate to EAA (Architect Agent)
│   │   │   │           │   │   ├─ Pause verification until EAA responds
│   │   │   │           │   │   └─ Resume with EAA guidance incorporated
│   │   │   │           │   │
│   │   │   │           │   └─ NO → Provide specific step-by-step guidance
│   │   │   │           │       ├─ Agent retries with guidance
│   │   │   │           │       └─ If still stuck after guidance → Escalate to user
│   │   │   │           │
│   │   │   │           └─ Is the issue a dependency on another module?
│   │   │   │               ├─ YES → Notify ECOS, pause verification
│   │   │   │               └─ NO → Agent must resolve before proceeding
│   │   │   │
│   │   │   └─ NO: This is loop 4 (final loop)
│   │   │       │
│   │   │       ├─ Are unresolved issues critical?
│   │   │       │   │
│   │   │       │   ├─ YES: Critical issues remain
│   │   │       │   │   ├─ Send restart notification (Section 4 template)
│   │   │       │   │   ├─ Reset loop count to 0
│   │   │       │   │   └─ Agent must fix all issues before restarting cycle
│   │   │       │   │
│   │   │       │   └─ NO: Only minor or cosmetic issues
│   │   │       │       ├─ Note issues as known items for PR description
│   │   │       │       └─ Allow 5th PR request to proceed to approval
│   │   │       │
│   │   │       └─ Were issues found AND fixed within loop 4 report?
│   │   │           ├─ YES → Treat as clean pass with fixes
│   │   │           └─ NO → Agent must fix before 5th request is accepted
│   │   │
│   │   └─ (Issues found path ends)
│   │
│   └─ NO: No issues found (clean pass)
│       │
│       ├─ Is agent evidence thorough?
│       │   │
│       │   ├─ YES: Report includes specific files reviewed, tests run, edge cases checked
│       │   │   └─ Record clean pass, wait for next PR request, proceed to next loop
│       │   │
│       │   └─ NO: Report is vague ("I checked everything, looks good")
│       │       ├─ Reject the report
│       │       ├─ Request deeper verification with specific evidence:
│       │       │   ├─ "List every file you reviewed"
│       │       │   ├─ "Name the specific tests you ran and their results"
│       │       │   └─ "Describe at least 3 edge cases you tested"
│       │       └─ Agent must re-submit loop N report with proper evidence
│       │
│       └─ (Clean pass path ends)
│
└─ (Decision tree ends - orchestrator waits for next PR request from agent)
```

### Summary of Focus Areas by Loop

| Loop | Primary Focus | Secondary Focus | Key Question |
|------|--------------|-----------------|--------------|
| 1 | General correctness, bugs, missing functionality | Test failures, linting errors | "Does the code work as specified?" |
| 2 | Fix verification, regression check | New issues from fixes | "Are loop 1 fixes correct and complete?" |
| 3 | Edge cases, error handling, performance | Integration points, concurrency | "What happens when things go wrong?" |
| 4 | Code style, documentation, test coverage, security | PR readiness, cleanup | "Is this code ready for production?" |
