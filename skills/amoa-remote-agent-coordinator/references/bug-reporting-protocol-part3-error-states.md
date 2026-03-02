# Bug Reporting Protocol - Part 3: Error States


## Contents

- [Error States](#error-states)
  - [Cannot Reproduce](#cannot-reproduce)
  - [Duplicate](#duplicate)
  - [Not a Bug](#not-a-bug)
  - [Needs More Info](#needs-more-info)
  - [Escalated](#escalated)

---

This document covers all error states and edge cases in bug handling.

**Parent document**: [bug-reporting-protocol.md](bug-reporting-protocol.md)

---

## Error States

### Cannot Reproduce

Orchestrator cannot reproduce the bug:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "cannot-reproduce",
  "orchestrator_environment": {
    "python_version": "3.12",
    "os": "Ubuntu 22.04",
    "dependencies": "uv.lock:abc123"
  },
  "test_results": "All tests pass - no failures observed",
  "needs": "more-info",
  "questions": [
    "Can you provide exact uv.lock hash you're using?",
    "Are you running tests with --verbose flag?",
    "Can you share full error traceback?"
  ]
}
```

Agent provides more details:

```json
{
  "type": "bug-clarification",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "additional_info": {
    "uv_lock_hash": "def456",
    "verbose_output": "artifacts/logs/verbose-test-failure.log",
    "full_traceback": "artifacts/logs/full-traceback.txt"
  },
  "video_recording": "artifacts/recordings/bug-reproduction.mp4"
}
```

If still cannot reproduce after 3 attempts, close as `cannot-reproduce`:

```bash
gh issue close 89 --comment "Cannot reproduce after 3 attempts. Closing. If bug reoccurs, please reopen with additional details."
gh issue label 89 --add "cannot-reproduce"
```

### Duplicate

Bug is duplicate of existing issue:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "duplicate",
  "status": "duplicate",
  "duplicate_of": "GH-67",
  "message": "This bug is already tracked in GH-67. Closing as duplicate.",
  "action": "Monitor GH-67 for resolution"
}
```

### Not a Bug

Reported behavior is expected/by-design:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "not-a-bug",
  "explanation": "JWT refresh tokens are designed to expire after 7 days as per security requirements in GH-12",
  "documentation": "docs/security/jwt-tokens.md#refresh-token-expiry",
  "action": "Close issue"
}
```

### Needs More Info

Insufficient information to triage:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "needs-more-info",
  "missing": [
    "Reproduction steps incomplete (missing step between 2 and 3)",
    "No error traceback provided",
    "Environment details missing OS version"
  ],
  "max_clarification_attempts": 3,
  "warning": "Issue will be closed if info not provided after 3 requests"
}
```

Agent provides clarification:

```json
{
  "type": "bug-clarification",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "updated_reproduction": {
    "steps": ["Updated step 1", "Updated step 2", "NEW step 2.5", "Updated step 3"],
    "error_traceback": "artifacts/logs/full-error.log",
    "environment": {
      "os": "Ubuntu 22.04.3 LTS"
    }
  }
}
```

### Escalated

Bug requires architectural decision or user input:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "escalated",
  "escalation_type": "architecture",
  "reason": "Bug fix requires changing API contract (breaking change)",
  "options": [
    {
      "option": "A",
      "description": "Maintain backward compatibility with deprecated endpoint",
      "pros": ["No breaking changes", "Gradual migration"],
      "cons": ["Technical debt", "More complex code"]
    },
    {
      "option": "B",
      "description": "Breaking change - remove old endpoint",
      "pros": ["Clean codebase", "Simpler maintenance"],
      "cons": ["Breaking change for existing clients"]
    }
  ],
  "recommendation": "B",
  "awaiting_user_decision": true
}
```

User/orchestrator responds:

```json
{
  "type": "escalation-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "decision": "B",
  "additional_instructions": "Proceed with breaking change. Update API docs and add migration guide.",
  "max_implementation_attempts": 2
}
```
