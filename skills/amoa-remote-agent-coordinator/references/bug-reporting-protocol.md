# Bug Reporting Protocol


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Document Structure](#document-structure)
  - [Part 1: Schema and Severity Levels](#part-1-schema-and-severity-levels)
  - [Part 2: Response Flow and Escalation](#part-2-response-flow-and-escalation)
  - [Part 3: Error States](#part-3-error-states)
  - [Part 4: Verification, Best Practices, and Troubleshooting](#part-4-verification-best-practices-and-troubleshooting)
- [Quick Reference](#quick-reference)
  - [Message Types](#message-types)
  - [Severity Quick Guide](#severity-quick-guide)
  - [Bug Report Minimal Example](#bug-report-minimal-example)
  - [Bug Fix Report Minimal Example](#bug-fix-report-minimal-example)
- [Integration](#integration)

---

## Purpose

Define how remote agents report bugs to the orchestrator, including bug classification, severity assessment, reproduction steps, and escalation paths. This protocol ensures all bugs are properly tracked, prioritized, and resolved.

## When to Use

- When agent discovers a bug during development or testing
- When CI/CD pipeline failures indicate a bug
- When integration tests reveal unexpected behavior
- When code review identifies potential bugs
- When security vulnerabilities are discovered

---

## Document Structure

This protocol is split into 4 parts for easier navigation:

### Part 1: Schema and Severity Levels
**File**: [bug-reporting-protocol-part1-schema-severity.md](bug-reporting-protocol-part1-schema-severity.md)

**Contents**:
- Bug Message Schema - Complete bug report object structure
  - Required fields: type, task_id, bug object
  - Bug object: title, severity, component, reproduction, evidence, impact
  - Optional: suggested_fix, related_issues
- Severity Levels - How to classify bugs
  - Critical: Security vulnerabilities, data loss, system failure, production outage
  - High: Core feature broken, test failures blocking PR, deployment blockers
  - Normal: Non-critical bugs, UI/UX issues, edge case failures
  - Low: Cosmetic issues, documentation bugs, rare edge cases

### Part 2: Response Flow and Escalation
**File**: [bug-reporting-protocol-part2-response-escalation.md](bug-reporting-protocol-part2-response-escalation.md)

**Contents**:
- Orchestrator Response Flow
  - Step 1: Acknowledgment (bug-report-ack message)
  - Step 2: GitHub Issue Creation (gh issue create with labels)
  - Step 3: Resolution Tracking (bug-fix-report, verification, close)
- Escalation Handling
  - Escalation triggers by severity (max ack attempts, max reproduction attempts)
  - Escalation flow when orchestrator doesn't acknowledge
  - Escalation flow when bug cannot be reproduced
  - Example escalation flow for high severity

### Part 3: Error States
**File**: [bug-reporting-protocol-part3-error-states.md](bug-reporting-protocol-part3-error-states.md)

**Contents**:
- Cannot Reproduce - Orchestrator unable to replicate bug
  - Response format with questions for clarification
  - Agent clarification format with additional info
  - Closing procedure after 3 failed attempts
- Duplicate - Bug already tracked in another issue
  - Response format with duplicate_of reference
- Not a Bug - Expected/by-design behavior
  - Response format with explanation and documentation
- Needs More Info - Insufficient details to triage
  - Response format listing missing items
  - Agent clarification format
  - Warning about closure after 3 requests
- Escalated - Requires architectural decision or user input
  - Response format with options, pros/cons, recommendation
  - User response format with decision

### Part 4: Verification, Best Practices, and Troubleshooting
**File**: [bug-reporting-protocol-part4-verification-troubleshooting.md](bug-reporting-protocol-part4-verification-troubleshooting.md)

**Contents**:
- Echo/Acknowledgment Integration
  - Bug reports require ack (follows echo-acknowledgment-protocol)
  - Acknowledgment format with understanding and next_steps
- Bug Verification Requirements
  - 5-step verification: write test, apply fix, verify pass, run suite, provide evidence
  - Verification evidence format
- Best Practices
  - For agents: investigate first, minimal reproduction, complete evidence
  - For orchestrator: acknowledge quickly, triage accurately, track immediately
- Integration with other protocols
  - messaging-protocol.md, echo-acknowledgment-protocol.md
  - task-instruction-format.md, test-report-format.md
  - artifact-sharing-protocol.md, status-management.md
- Message Type Registry
  - bug-report, bug-report-ack, bug-report-response
  - bug-clarification, bug-fix-report
- Troubleshooting
  - Cannot reproduce issues
  - Expected behavior disputes
  - Critical bugs not getting attention
  - Bug fix causes regressions
  - Agent cannot fix after multiple attempts
  - Duplicate bugs reported
  - Severity disputes
  - Insufficient detail in reports

---

## Quick Reference

### Message Types

| Message Type | Direction | Purpose |
|-------------|-----------|---------|
| `bug-report` | Agent -> Orchestrator | Initial bug report |
| `bug-report-ack` | Orchestrator -> Agent | Acknowledge bug received |
| `bug-report-response` | Orchestrator -> Agent | Action plan for bug |
| `bug-clarification` | Agent -> Orchestrator | Additional bug details |
| `bug-fix-report` | Agent -> Orchestrator | Report bug fixed |

### Severity Quick Guide

| Severity | When to Use | Max Ack Attempts |
|----------|-------------|------------------|
| `critical` | Security, data loss, system failure | 2 |
| `high` | Core feature broken, blockers | 2 |
| `normal` | Non-critical bugs, UI issues | 3 |
| `low` | Cosmetic, docs, rare edge cases | 3 |

### Bug Report Minimal Example

```json
{
  "type": "bug-report",
  "task_id": "GH-42",
  "bug": {
    "title": "Brief description",
    "severity": "high",
    "component": "auth/login",
    "discovered_in": "testing",
    "affects_task": true,
    "reproduction": {
      "steps": ["Step 1", "Step 2"],
      "expected": "Expected behavior",
      "actual": "Actual behavior",
      "reproducibility": "always"
    },
    "impact": {
      "blocks_development": true,
      "security_concern": false
    }
  },
  "requires_ack": true,
  "priority": "high"
}
```

### Bug Fix Report Minimal Example

```json
{
  "type": "bug-fix-report",
  "task_id": "GH-42",
  "bug_id": "GH-89",
  "status": "fixed",
  "verification": {
    "reproduction_test": "test_auth.py::test_regression",
    "before_fix": "FAILED",
    "after_fix": "PASSED",
    "full_suite": "47 passed, 0 failed"
  },
  "fix_commit": "abc123def",
  "pr_url": "https://github.com/user/repo/pull/90"
}
```

---

## Integration

This protocol integrates with:

- `messaging-protocol.md` - Bug reports use standard message envelope
- `echo-acknowledgment-protocol.md` - Bug reports follow ack pattern
- `task-instruction-format.md` - Bug fixes are tasks with completion criteria
- `test-report-format.md` - Verification tests reported using test format
- `artifact-sharing-protocol.md` - Evidence logs/screenshots shared as artifacts
- `status-management.md` - GitHub issues updated with bug status
