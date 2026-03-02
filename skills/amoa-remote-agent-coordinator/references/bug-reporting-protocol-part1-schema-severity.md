# Bug Reporting Protocol - Part 1: Schema and Severity Levels


## Contents

- [Bug Message Schema](#bug-message-schema)
  - [Complete Bug Report Object](#complete-bug-report-object)
- [Severity Levels](#severity-levels)
  - [Critical](#critical)
  - [High](#high)
  - [Normal](#normal)
  - [Low](#low)

---

This document covers bug message structure and severity classification.

**Parent document**: [bug-reporting-protocol.md](bug-reporting-protocol.md)

---

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

---

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
