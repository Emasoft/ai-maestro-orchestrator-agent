# Bug Reporting Protocol - Part 1: Reporting and Classification

## Purpose

Define how remote agents report bugs to the orchestrator, including bug classification, severity assessment, and reproduction steps. This protocol ensures all bugs are properly tracked, prioritized, and resolved.

## Contents

### This File (Part 1: Reporting and Classification)
1. [If you need to understand the bug report format](#bug-message-schema) - Structure and fields required for all bug reports
2. [If you need to classify bug severity](#severity-levels) - How to determine if bug is critical, high, normal, or low
3. [If you need to understand how orchestrator handles bugs](#orchestrator-response-flow) - Acknowledgment, GitHub tracking, and resolution flow

### Part 2: Handling and Resolution
See [bug-reporting-protocol-part2-handling-and-resolution.md](bug-reporting-protocol-part2-handling-and-resolution.md):
- If a bug cannot be immediately fixed - When and how to escalate bugs based on severity
- If orchestrator responds with error states - Handling cannot-reproduce, duplicate, not-a-bug, needs-more-info, escalated responses
- If you need to follow acknowledgment protocol - Bug reports must follow echo-acknowledgment pattern
- If you are fixing a reported bug - How to verify and report bug fixes
- If you are creating a bug report - Agent and orchestrator best practices
- If you need to integrate bugs with other protocols - How bug reporting integrates with other messaging protocols
- If you need to understand message types - All message types used in bug reporting

## When to Use

- When agent discovers a bug during development or testing
- When CI/CD pipeline failures indicate a bug
- When integration tests reveal unexpected behavior
- When code review identifies potential bugs
- When security vulnerabilities are discovered

## Bug Message Schema

### Complete Bug Report Object

```json
{
  "type": "bug-report",
  "task_id": "GH-42",
  "bug": {
    "title": "Brief bug description",
    "severity": "critical|high|normal|low",
    "component": "component-name",
    "discovered_in": "task-phase",
    "affects_task": true,
    "reproduction": {
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expected": "Expected behavior description",
      "actual": "Actual behavior description",
      "environment": {
        "python_version": "3.12",
        "os": "Ubuntu 22.04",
        "dependencies": "uv.lock hash or requirements.txt snapshot"
      },
      "reproducibility": "always|sometimes|once"
    },
    "evidence": {
      "error_message": "Full error traceback",
      "logs": "artifacts/logs/bug-evidence-20251231.log",
      "screenshots": ["artifacts/screenshots/bug-ui-20251231.png"],
      "test_failure": "test_auth.py::test_login_timeout FAILED"
    },
    "impact": {
      "blocks_development": true,
      "security_concern": false,
      "data_loss_risk": false,
      "user_facing": true
    },
    "suggested_fix": "Optional: Agent's hypothesis about the fix",
    "related_issues": ["GH-38", "GH-27"]
  },
  "requires_ack": true,
  "priority": "high"
}
```

## Severity Levels

### Critical

**Use when:**
- Security vulnerabilities (data exposure, auth bypass, injection)
- Data loss or corruption
- Complete system/feature failure
- Production outage

**Acknowledgment required:** Yes

**Example:**
```json
{
  "type": "bug-report",
  "task_id": "GH-42",
  "bug": {
    "title": "SQL injection vulnerability in login endpoint",
    "severity": "critical",
    "component": "auth/login",
    "discovered_in": "security-review",
    "affects_task": true,
    "reproduction": {
      "steps": [
        "Navigate to /api/login",
        "Submit username: admin' OR '1'='1",
        "Submit any password"
      ],
      "expected": "Login rejected with 401 Unauthorized",
      "actual": "Login succeeds, returns admin token",
      "environment": {
        "python_version": "3.12",
        "os": "Ubuntu 22.04",
        "dependencies": "uv.lock:abc123"
      },
      "reproducibility": "always"
    },
    "evidence": {
      "error_message": "None - silent success",
      "logs": "artifacts/logs/sql-injection-test.log",
      "test_failure": "test_security.py::test_sql_injection FAILED"
    },
    "impact": {
      "blocks_development": true,
      "security_concern": true,
      "data_loss_risk": true,
      "user_facing": true
    },
    "suggested_fix": "Use parameterized queries instead of string concatenation"
  },
  "priority": "urgent"
}
```

### High

**Use when:**
- Core feature completely broken
- Test suite failures preventing PR merge
- Deployment blockers
- Significant performance degradation

**Acknowledgment required:** Yes

**Example:**
```json
{
  "type": "bug-report",
  "task_id": "GH-42",
  "bug": {
    "title": "JWT token validation fails on refresh",
    "severity": "high",
    "component": "auth/jwt",
    "discovered_in": "integration-testing",
    "affects_task": true,
    "reproduction": {
      "steps": [
        "Login successfully (get access + refresh tokens)",
        "Wait for access token to expire",
        "Call /api/refresh with refresh_token",
        "Observe 401 Unauthorized error"
      ],
      "expected": "New access token returned",
      "actual": "401 Unauthorized with 'Invalid refresh token'",
      "environment": {
        "python_version": "3.12",
        "os": "Ubuntu 22.04",
        "dependencies": "uv.lock:def456"
      },
      "reproducibility": "always"
    },
    "evidence": {
      "error_message": "jwt.exceptions.InvalidTokenError: Token has expired",
      "logs": "artifacts/logs/jwt-refresh-failure.log",
      "test_failure": "test_auth.py::test_token_refresh FAILED"
    },
    "impact": {
      "blocks_development": true,
      "security_concern": false,
      "data_loss_risk": false,
      "user_facing": true
    },
    "suggested_fix": "Check refresh token expiry logic in jwt_utils.py:validate_refresh_token()"
  },
  "priority": "high"
}
```

### Normal

**Use when:**
- Non-critical feature bug
- UI/UX issues
- Performance issues (non-critical)
- Edge case failures

**Acknowledgment required:** Yes

**Example:**
```json
{
  "type": "bug-report",
  "task_id": "GH-42",
  "bug": {
    "title": "Login form doesn't clear on failed attempt",
    "severity": "normal",
    "component": "auth/ui",
    "discovered_in": "manual-testing",
    "affects_task": false,
    "reproduction": {
      "steps": [
        "Navigate to /login",
        "Enter invalid credentials",
        "Click 'Login'",
        "Observe error message displayed"
      ],
      "expected": "Error shown, form fields cleared",
      "actual": "Error shown, but password field retains value",
      "environment": {
        "python_version": "3.12",
        "os": "macOS 14",
        "dependencies": "uv.lock:ghi789"
      },
      "reproducibility": "always"
    },
    "evidence": {
      "error_message": "None - UI behavior issue",
      "screenshots": ["artifacts/screenshots/login-form-not-cleared.png"]
    },
    "impact": {
      "blocks_development": false,
      "security_concern": false,
      "data_loss_risk": false,
      "user_facing": true
    },
    "suggested_fix": "Add form.reset() after displaying error in login.js"
  },
  "priority": "normal"
}
```

### Low

**Use when:**
- Minor cosmetic issues
- Documentation bugs
- Rare edge cases
- Nice-to-have improvements

**Acknowledgment required:** Yes

**Example:**
```json
{
  "type": "bug-report",
  "task_id": "GH-42",
  "bug": {
    "title": "Typo in error message: 'Authetication' should be 'Authentication'",
    "severity": "low",
    "component": "auth/messages",
    "discovered_in": "code-review",
    "affects_task": false,
    "reproduction": {
      "steps": [
        "Trigger any auth error",
        "Read error message"
      ],
      "expected": "Error: Authentication failed",
      "actual": "Error: Authetication failed",
      "environment": {
        "python_version": "3.12",
        "os": "Any",
        "dependencies": "Any"
      },
      "reproducibility": "always"
    },
    "evidence": {
      "error_message": "See auth/errors.py line 42"
    },
    "impact": {
      "blocks_development": false,
      "security_concern": false,
      "data_loss_risk": false,
      "user_facing": true
    },
    "suggested_fix": "Fix typo in auth/errors.py:42"
  },
  "priority": "low"
}
```

## Orchestrator Response Flow

### Step 1: Acknowledgment

Orchestrator acknowledges bug report (using echo-acknowledgment-protocol):

```json
{
  "type": "bug-report-ack",
  "task_id": "GH-42",
  "bug_id": "auto-generated-or-github-issue",
  "status": "received",
  "received_at": "2025-12-31T03:15:00Z",
  "action": "creating-github-issue"
}
```

### Step 2: GitHub Issue Creation

Orchestrator creates GitHub issue for tracking:

```bash
gh issue create \
  --title "BUG: JWT token validation fails on refresh (GH-42)" \
  --body "$(cat bug-report-GH-42.md)" \
  --label "bug,severity:high,component:auth" \
  --assignee dev-agent-1 \
  --milestone v1.0
```

Response to agent:

```json
{
  "type": "bug-report-response",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "tracked",
  "github_issue": "https://github.com/user/repo/issues/89",
  "action_required": "fix-immediately",
  "assigned_to": "dev-agent-1",
  "max_attempts": 3
}
```

### Step 3: Resolution Tracking

Agent reports bug fixed:

```json
{
  "type": "bug-fix-report",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "fixed",
  "fix_commit": "abc123def",
  "test_evidence": "All tests pass - artifacts/tests/fix-verification.log",
  "pr_url": "https://github.com/user/repo/pull/90"
}
```

Orchestrator verifies and closes:

```bash
# Orchestrator runs tests to verify fix
# If tests pass:
gh issue close 89 --comment "Verified fixed in commit abc123def. Tests pass."
```

---

## Troubleshooting

### Problem: Bug Report Rejected For Missing Fields

**Symptoms**: Orchestrator returns error indicating incomplete bug report.

**Solution**:
1. Review bug message schema in Section "Bug Message Schema"
2. Ensure all required fields are present: type, task_id, bug (with title, severity, component)
3. Verify reproduction object includes steps, expected, actual
4. Check JSON syntax is valid (no trailing commas, proper quoting)
5. Use the severity-level examples as templates

### Problem: Severity Level Disagreement

**Symptoms**: Orchestrator downgrades/upgrades severity after receiving report.

**Solution**:
1. Review severity definitions in Section "Severity Levels"
2. Critical = security, data loss, complete failure, production outage
3. High = core feature broken, test failures blocking merge, deployment blockers
4. Normal = non-critical bugs, UI issues, edge cases
5. Low = cosmetic, documentation, rare edge cases
6. Accept orchestrator's assessment - they have broader project context

### Problem: Bug Report Not Acknowledged

**Symptoms**: Agent sends bug-report but receives no ack.

**Solution**:
1. Verify message was delivered via AI Maestro delivery confirmation
2. Check if orchestrator session is online
3. Retry with `retry: true, attempt: 2` field after reasonable wait
4. If still no ack after 2 attempts, block development for critical/high severity
5. Notify user via session output about unresponsive orchestrator

### Problem: Reproduction Steps Insufficient

**Symptoms**: Orchestrator returns `needs-more-info` status.

**Solution**:
1. Break down steps to atomic actions (one action per step)
2. Include exact input values, not placeholders
3. Specify starting state (logged in? fresh install? specific config?)
4. Add environment details: versions, OS, dependencies
5. Include exact error messages and stack traces

### Problem: GitHub Issue Created But Wrong Labels

**Symptoms**: Bug tracked in GitHub but missing or wrong severity/component labels.

**Solution**:
1. Verify labels exist in the repository (`gh label list`)
2. Check label names match exactly: `severity:critical`, not `critical`
3. Ensure component label matches component field in bug report
4. Orchestrator should auto-create missing labels or use existing ones
5. If labels consistently wrong, update label mapping in orchestrator config

### Problem: Bug Evidence Files Not Found

**Symptoms**: Orchestrator cannot access evidence artifacts in logs/screenshots.

**Solution**:
1. Verify artifact paths are relative to project root
2. Ensure artifacts were committed and pushed (not just local)
3. Check if artifacts are in `.gitignore` (they shouldn't be for bug evidence)
4. Use consistent artifact path pattern: `artifacts/{type}/{task_id}-{timestamp}.{ext}`
5. Consider using artifact-sharing-protocol for large evidence files

---

**Next:** See [Part 2: Handling and Resolution](bug-reporting-protocol-part2-handling-and-resolution.md) for escalation, error states, acknowledgment integration, verification requirements, and best practices.
