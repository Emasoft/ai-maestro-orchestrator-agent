# Bug Reporting Protocol - Part 4: Verification, Best Practices, and Troubleshooting


## Contents

- [Echo/Acknowledgment Integration](#echoacknowledgment-integration)
  - [Acknowledgment Required](#acknowledgment-required)
  - [Acknowledgment Format](#acknowledgment-format)
- [Bug Verification Requirements](#bug-verification-requirements)
  - [Verification Evidence Format](#verification-evidence-format)
- [Best Practices](#best-practices)
  - [For Agents Reporting Bugs](#for-agents-reporting-bugs)
  - [For Orchestrator Processing Bugs](#for-orchestrator-processing-bugs)
- [Integration](#integration)
- [Message Type Registry](#message-type-registry)
- [Troubleshooting](#troubleshooting)
  - [Problem: Bug Report Rejected as "Cannot Reproduce"](#problem-bug-report-rejected-as-cannot-reproduce)
  - [Problem: Agent Reports Bug But It's Expected Behavior](#problem-agent-reports-bug-but-its-expected-behavior)
  - [Problem: Critical Bug Not Getting Attention](#problem-critical-bug-not-getting-attention)
  - [Problem: Bug Fix Causes Regressions](#problem-bug-fix-causes-regressions)
  - [Problem: Agent Cannot Fix Bug After Multiple Attempts](#problem-agent-cannot-fix-bug-after-multiple-attempts)
  - [Problem: Duplicate Bugs Reported](#problem-duplicate-bugs-reported)
  - [Problem: Bug Severity Disputed](#problem-bug-severity-disputed)
  - [Problem: Bug Reports Lack Sufficient Detail](#problem-bug-reports-lack-sufficient-detail)

---

This document covers bug verification, best practices, integration, and troubleshooting.

**Parent document**: [bug-reporting-protocol.md](bug-reporting-protocol.md)

---

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

---

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

---

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

---

## Integration

This protocol integrates with:

- `messaging-protocol.md` - Bug reports use standard message envelope
- `echo-acknowledgment-protocol.md` - Bug reports follow ack pattern
- `task-instruction-format.md` - Bug fixes are tasks with completion criteria
- `test-report-format.md` - Verification tests reported using test format
- `artifact-sharing-protocol.md` - Evidence logs/screenshots shared as artifacts
- `status-management.md` - GitHub issues updated with bug status

---

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

### Problem: Bug Report Rejected as "Cannot Reproduce"

**Symptoms**: Orchestrator says bug cannot be reproduced but agent sees it consistently.

**Solution**:
1. Verify exact environment match (OS, Python version, dependencies)
2. Share exact uv.lock or requirements.txt hash
3. Provide video recording of reproduction
4. Share full verbose logs including setup steps
5. Ask orchestrator to try on same exact commit hash

### Problem: Agent Reports Bug But It's Expected Behavior

**Symptoms**: Orchestrator marks as "not-a-bug", agent disagrees.

**Solution**:
1. Point agent to relevant documentation/spec
2. If spec is unclear, update spec for clarity
3. If behavior should change, create feature request instead
4. Document this edge case for future reference
5. Close bug issue with detailed explanation

### Problem: Critical Bug Not Getting Attention

**Symptoms**: Critical severity bug not acknowledged or acted upon.

**Solution**:
1. Verify priority field is set to `urgent`
2. Send follow-up reminder with escalation warning
3. If orchestrator unresponsive, escalate directly to user
4. Block all related development until acknowledged
5. Document escalation in GitHub Issue comments

### Problem: Bug Fix Causes Regressions

**Symptoms**: Fix resolves original bug but breaks other functionality.

**Solution**:
1. Revert fix immediately
2. Analyze test coverage gaps that missed regression
3. Write additional tests for affected areas
4. Develop fix that addresses both issues
5. Run full test suite before resubmitting fix

### Problem: Agent Cannot Fix Bug After Multiple Attempts

**Symptoms**: Agent reports failed fix attempts, max attempts reached.

**Solution**:
1. Review all attempted fixes for patterns
2. Consider if bug requires different expertise
3. Reassign to agent with relevant skill set
4. If architectural issue, escalate for design decision
5. Document all approaches tried in GitHub Issue

### Problem: Duplicate Bugs Reported

**Symptoms**: Multiple agents report same underlying bug.

**Solution**:
1. Link duplicates to canonical issue
2. Close duplicates with reference to primary issue
3. Consolidate evidence from all reports into primary
4. Notify all reporters of consolidation
5. Improve search to help agents find existing issues

### Problem: Bug Severity Disputed

**Symptoms**: Agent and orchestrator disagree on severity level.

**Solution**:
1. Review severity criteria objectively
2. Consider actual impact on users/development
3. If security related, default to higher severity
4. Document rationale for final severity decision
5. If still disputed, escalate to user for final call

### Problem: Bug Reports Lack Sufficient Detail

**Symptoms**: Agent sends bug report with missing fields or vague descriptions.

**Solution**:
1. Send back needs-more-info response listing missing items
2. Provide example of well-formed bug report
3. Set reminder for clarification deadline
4. If pattern continues, include bug template in task instructions
5. Close after 3 clarification requests with no response
