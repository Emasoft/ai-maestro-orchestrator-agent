# Bug Reporting Protocol - Part 2: Handling and Resolution

## Purpose

Define how bugs are escalated, handled in error states, verified when fixed, and integrated with other protocols. This is the second part of the Bug Reporting Protocol.

## Contents

### Part 1: Reporting and Classification
See [bug-reporting-protocol-part1-reporting-and-classification.md](bug-reporting-protocol-part1-reporting-and-classification.md):
- If you need to understand the bug report format - Structure and fields required for all bug reports
- If you need to classify bug severity - How to determine if bug is critical, high, normal, or low
- If you need to understand how orchestrator handles bugs - Acknowledgment, GitHub tracking, and resolution flow

### This File (Part 2: Handling and Resolution)
1. [If a bug cannot be immediately fixed](#escalation-handling) - When and how to escalate bugs based on severity
2. [If orchestrator responds with error states](#error-states) - Handling cannot-reproduce, duplicate, not-a-bug, needs-more-info, escalated responses
3. [If you need to follow acknowledgment protocol](#echoacknowledgment-integration) - Bug reports must follow echo-acknowledgment pattern
4. [If you are fixing a reported bug](#bug-verification-requirements) - How to verify and report bug fixes
5. [If you are creating a bug report](#best-practices) - Agent and orchestrator best practices
6. [If you need to integrate bugs with other protocols](#integration) - How bug reporting integrates with other messaging protocols
7. [If you need to understand message types](#message-type-registry) - All message types used in bug reporting

## Escalation Handling

### Escalation Triggers by Severity

| Severity | Max Ack Attempts | Max Reproduction Attempts | Escalation Trigger |
|----------|------------------|---------------------------|-------------------|
| `critical` | 2 | 2 | Blocker identified or max attempts exceeded |
| `high` | 2 | 3 | Blocker identified or max attempts exceeded |
| `normal` | 3 | 3 | Max attempts exceeded |
| `low` | 3 | 3 | Max attempts exceeded |

### Escalation Flow

If orchestrator doesn't acknowledge:

1. **First attempt** (initial bug report):
   - Agent sends bug-report with `attempt: 1` field
   - Wait for acknowledgment

2. **Second attempt** (after no ack):
   - Agent retries bug report with `retry: true, attempt: 2` flag
   - Wait for acknowledgment

3. **Max attempts exceeded**:
   - Agent logs non-responsive orchestrator
   - Agent blocks development if bug severity is critical/high
   - Agent notifies user via session output

If bug cannot be reproduced:

1. **Max reproduction attempts exceeded**:
   - Orchestrator escalates to user
   - Orchestrator considers reassigning task or closing as cannot-reproduce
   - Orchestrator updates GitHub issue with reproduction status

### Example Escalation Flow (High Severity)

```
Attempt 1: Agent sends bug-report (severity: high, attempt: 1)
           → No ack received
Attempt 2: Agent retries bug-report (retry: true, attempt: 2)
           → No ack received
           → Log "Orchestrator unresponsive", block development
           → Max ack attempts (2) exceeded → Escalate to user
```

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

## Echo/Acknowledgment Integration

All bug reports follow the echo-acknowledgment protocol (see `echo-acknowledgment-protocol.md`):

1. **Agent sends bug-report** with `requires_ack: true`
2. **Orchestrator sends bug-report-ack** promptly
3. **If agent needs clarification**, send `bug-clarification`
4. **Orchestrator confirms** understanding and action plan

### Acknowledgment Required

Bug reports ALWAYS require acknowledgment. If no ack received:

1. Retry once (see Escalation Handling)
2. If still no ack, agent must block development for critical/high severity
3. Agent notifies user via session output

### Acknowledgment Format

Follows standard task-acknowledgment format from echo-acknowledgment-protocol:

```json
{
  "type": "bug-report-ack",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "received",
  "received_at": "2025-12-31T03:15:00Z",
  "understanding": "Critical SQL injection in login endpoint - creating GitHub issue, assigning to agent, max 2 attempts",
  "next_steps": [
    "Create GitHub issue GH-89",
    "Assign to dev-agent-1",
    "Set critical priority",
    "Monitor for resolution"
  ]
}
```

## Bug Verification Requirements

Before reporting bug as fixed, agent MUST:

1. **Write reproduction test** that fails before fix
2. **Apply fix**
3. **Verify test passes** after fix
4. **Run full test suite** to ensure no regressions
5. **Provide test evidence** in bug-fix-report

### Verification Evidence Format

```json
{
  "type": "bug-fix-report",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "verification": {
    "reproduction_test": "test_auth.py::test_sql_injection_regression",
    "before_fix": "FAILED - injection successful",
    "after_fix": "PASSED - injection blocked",
    "full_suite": "47 passed, 0 failed",
    "evidence_artifacts": [
      "artifacts/tests/before-fix-results.log",
      "artifacts/tests/after-fix-results.log",
      "artifacts/tests/full-suite-results.log"
    ]
  },
  "fix_commit": "abc123def",
  "pr_url": "https://github.com/user/repo/pull/90"
}
```

## Best Practices

### For Agents Reporting Bugs

1. **Investigate first** - Verify it's actually a bug, not expected behavior
2. **Minimal reproduction** - Simplify steps to minimal reproducible case
3. **Complete evidence** - Include logs, screenshots, error messages
4. **Severity accuracy** - Don't over/under-estimate severity
5. **Suggested fix** - If you have hypothesis, include it
6. **Related issues** - Link to related bugs/tasks

### For Orchestrator Processing Bugs

1. **Acknowledge quickly** - Don't block agent waiting for response
2. **Triage accurately** - Verify severity is appropriate
3. **Track immediately** - Create GitHub issue for every non-duplicate bug
4. **Clear ownership** - Always assign bugs to specific agent
5. **Set attempt limits** - Based on severity, set clear max attempt thresholds
6. **Verify fixes** - Never close without running tests

## Integration

This protocol integrates with:

- `messaging-protocol.md` - Bug reports use standard message envelope
- `echo-acknowledgment-protocol.md` - Bug reports follow ack pattern
- `task-instruction-format.md` - Bug fixes are tasks with completion criteria
- `test-report-format.md` - Verification tests reported using test format
- `artifact-sharing-protocol.md` - Evidence logs/screenshots shared as artifacts
- `status-management.md` - GitHub issues updated with bug status

## Message Type Registry

Bug reporting protocol defines these message types:

| Message Type | Direction | Purpose |
|-------------|-----------|---------|
| `bug-report` | Agent -> Orchestrator | Initial bug report |
| `bug-report-ack` | Orchestrator -> Agent | Acknowledge bug received |
| `bug-report-response` | Orchestrator -> Agent | Action plan for bug |
| `bug-clarification` | Agent -> Orchestrator | Additional bug details |
| `bug-fix-report` | Agent -> Orchestrator | Report bug fixed |

All message types include:
- `task_id` - Parent task where bug discovered
- `bug_id` - GitHub issue number once created
- `severity` - critical|high|normal|low
- `status` - Current state in bug lifecycle

---

## Troubleshooting

### Problem: Bug Marked Cannot-Reproduce But Agent Can Reproduce

**Symptoms**: Orchestrator closes bug as cannot-reproduce, but agent consistently reproduces it.

**Solution**:
1. Compare environment details exactly (Python version, OS, dependencies hash)
2. Provide video recording of reproduction if possible
3. Create minimal reproduction case - smallest code that triggers bug
4. Check for timing-dependent issues (race conditions reproduce intermittently)
5. Request orchestrator use exact same environment setup

### Problem: Bug Fix Rejected Despite Tests Passing

**Symptoms**: Agent reports bug fixed with passing tests, but orchestrator rejects.

**Solution**:
1. Verify reproduction test exists (test that failed before fix)
2. Ensure test actually tests the bug scenario, not just a related case
3. Check full test suite passes (no regressions introduced)
4. Include complete verification evidence in bug-fix-report
5. Ensure PR is merged, not just created

### Problem: Escalation Decision Delayed

**Symptoms**: Bug requiring architectural decision stuck in escalated state.

**Solution**:
1. Send reminder to user with clear decision options
2. Include recommendation and reasoning for preferred option
3. Set expectation: escalated bugs need user input before agent can proceed
4. If user unresponsive, agent should block on critical bugs
5. Consider if simpler non-architectural fix is possible

### Problem: Duplicate Detection Fails

**Symptoms**: Same bug reported multiple times, not caught as duplicate.

**Solution**:
1. Search existing issues before creating new bug report
2. Use consistent bug titles: "BUG: {component} - {brief description}"
3. Link related issues in bug report's `related_issues` field
4. Orchestrator should search by component and symptoms before creating issue
5. When duplicate found, close with reference to original

### Problem: Bug Fix Introduces New Bugs

**Symptoms**: Fix for one bug causes failures elsewhere.

**Solution**:
1. Ensure full test suite runs before reporting fix complete
2. Look for test failures in unrelated areas (regression indicators)
3. If fix requires changing shared code, review all callers
4. Consider if fix is correct approach or masking deeper issue
5. May need to revert fix and try different approach

### Problem: Low Severity Bugs Never Get Fixed

**Symptoms**: Low severity bugs accumulate, never addressed.

**Solution**:
1. Bundle low-severity bugs into cleanup tasks when workload allows
2. Address low bugs that affect same component as current high-priority work
3. Track low-severity bug count - if too many, schedule dedicated cleanup sprint
4. Prioritize low bugs that affect user-facing strings (typos, error messages)
5. Close low bugs that become obsolete due to other changes

---

**Previous:** See [Part 1: Reporting and Classification](bug-reporting-protocol-part1-reporting-and-classification.md) for bug message schema, severity levels, and orchestrator response flow.
