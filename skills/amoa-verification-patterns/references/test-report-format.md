# Test Report Format


## Contents

- [Table of Contents](#table-of-contents)
- [Purpose](#purpose)
- [Standard Report Structure](#standard-report-structure)
- [Minimal Report (For Orchestrator)](#minimal-report-for-orchestrator)
- [Language-Specific Converters](#language-specific-converters)
  - [Python (pytest)](#python-pytest)
  - [JavaScript (Jest)](#javascript-jest)
  - [Go](#go)
  - [Rust](#rust)
- [Report Locations](#report-locations)
- [Failure Detail Levels](#failure-detail-levels)
  - [Level 1: Minimal (default)](#level-1-minimal-default)
  - [Level 2: With Error](#level-2-with-error)
  - [Level 3: With Traceback](#level-3-with-traceback)
- [Report Storage and Handoff](#report-storage-and-handoff)
- [Orchestrator Response to Test Reports](#orchestrator-response-to-test-reports)
  - [If All Tests Pass](#if-all-tests-pass)
  - [If Tests Fail](#if-tests-fail)
  - [If Coverage Too Low](#if-coverage-too-low)
- [Error States](#error-states)
  - [Error Report Format](#error-report-format)
  - [Partial Results Handling](#partial-results-handling)
- [Completion Tracking](#completion-tracking)
  - [Attempt-Based Progress Tracking](#attempt-based-progress-tracking)
  - [Escalation Flow](#escalation-flow)
    - [After No Response](#after-no-response)
    - [After Multiple Check-ins](#after-multiple-check-ins)
    - [Blocker Escalation](#blocker-escalation)
  - [Additional Attempts Request](#additional-attempts-request)
  - [Progress Updates During Testing](#progress-updates-during-testing)
  - [Agent-Side Hang Prevention](#agent-side-hang-prevention)
  - [Completion Best Practices](#completion-best-practices)
  - [Related Protocol References](#related-protocol-references)
- [Integration](#integration)

---

## Table of Contents

1. [Purpose](#purpose)
2. [Standard Report Structure](#standard-report-structure)
3. [Minimal Report (For Orchestrator)](#minimal-report-for-orchestrator)
4. [Language-Specific Converters](#language-specific-converters)
   - [Python (pytest)](#python-pytest)
   - [JavaScript (Jest)](#javascript-jest)
   - [Go](#go)
   - [Rust](#rust)
5. [Report Locations](#report-locations)
6. [Failure Detail Levels](#failure-detail-levels)
   - [Level 1: Minimal (default)](#level-1-minimal-default)
   - [Level 2: With Error](#level-2-with-error)
   - [Level 3: With Traceback](#level-3-with-traceback)
7. [Report Storage and Handoff](#report-storage-and-handoff)
8. [Orchestrator Response to Test Reports](#orchestrator-response-to-test-reports)
   - [If All Tests Pass](#if-all-tests-pass)
   - [If Tests Fail](#if-tests-fail)
   - [If Coverage Too Low](#if-coverage-too-low)
9. [Error States](#error-states)
   - [Error Report Format](#error-report-format)
   - [Partial Results Handling](#partial-results-handling)
10. [Completion Tracking](#completion-tracking)
    - [Attempt-Based Progress Tracking](#attempt-based-progress-tracking)
    - [Escalation Flow](#escalation-flow)
      - [After No Response](#after-no-response)
      - [After Multiple Check-ins](#after-multiple-check-ins)
      - [Blocker Escalation](#blocker-escalation)
    - [Additional Attempts Request](#additional-attempts-request)
    - [Progress Updates During Testing](#progress-updates-during-testing)
    - [Agent-Side Hang Prevention](#agent-side-hang-prevention)
    - [Completion Best Practices](#completion-best-practices)
    - [Related Protocol References](#related-protocol-references)

## Purpose

Standardize test result reporting across all agents and languages for consistent orchestrator consumption.

## Standard Report Structure

```json
{
  "report_version": "1.0",
  "task_id": "GH-42",
  "agent_id": "dev-agent-1",
  "timestamp": "2025-12-31T03:00:00Z",
  "summary": {
    "total": 45,
    "passed": 42,
    "failed": 2,
    "skipped": 1,
    "duration_seconds": 12.5
  },
  "failures": [
    {
      "test": "test_auth.py::test_login_invalid_password",
      "file": "tests/test_auth.py",
      "line": 45,
      "error": "AssertionError: Expected 401, got 200",
      "traceback": "..."
    }
  ],
  "coverage": {
    "line_percent": 85.2,
    "branch_percent": 72.1,
    "uncovered_files": ["src/legacy.py"]
  }
}
```

## Minimal Report (For Orchestrator)

Agents MUST provide minimal summary:

```
[TESTS] 45 total: 42 passed, 2 failed, 1 skipped (12.5s)
FAILED: test_auth.py:45, test_api.py:89
COVERAGE: 85% lines, 72% branches
```

## Language-Specific Converters

### Python (pytest)

```bash
pytest --json-report --json-report-file=test-report.json
```

Convert to standard format:
```python
import json

def convert_pytest_report(pytest_json):
    data = json.load(pytest_json)
    return {
        "summary": {
            "total": data["summary"]["total"],
            "passed": data["summary"]["passed"],
            "failed": data["summary"]["failed"],
            "skipped": data["summary"]["skipped"],
            "duration_seconds": data["duration"]
        },
        "failures": [
            {
                "test": t["nodeid"],
                "error": t["call"]["longrepr"]
            }
            for t in data["tests"] if t["outcome"] == "failed"
        ]
    }
```

### JavaScript (Jest)

```bash
jest --json --outputFile=test-report.json
```

### Go

```bash
go test -json ./... > test-report.json
```

### Rust

```bash
cargo test -- --format json > test-report.json
```

## Report Locations

| Framework | Report File |
|-----------|-------------|
| pytest | `artifacts/tests/pytest-report.json` |
| jest | `artifacts/tests/jest-report.json` |
| go test | `artifacts/tests/go-report.json` |
| cargo test | `artifacts/tests/cargo-report.json` |

## Failure Detail Levels

### Level 1: Minimal (default)
```
FAILED: test_auth.py:45
```

### Level 2: With Error
```
FAILED: test_auth.py:45 - AssertionError: Expected 401, got 200
```

### Level 3: With Traceback
Full traceback in separate file: `artifacts/tests/failures/test_auth_45.txt`

## Report Storage and Handoff

- Write full report to `artifacts/tests/`
- Return minimal summary to orchestrator
- Link to detailed report if needed

## Orchestrator Response to Test Reports

When agent sends test report, orchestrator responds:

### If All Tests Pass

```json
{
  "type": "test-report-ack",
  "task_id": "GH-42",
  "status": "approved",
  "message": "All tests passed. Proceed to PR creation.",
  "next_action": "create-pr"
}
```

### If Tests Fail

```json
{
  "type": "test-report-ack",
  "task_id": "GH-42",
  "status": "rejected",
  "message": "Fix 2 failing tests before proceeding",
  "required_actions": [
    "Fix test_auth.py:45 - assertion failed",
    "Fix test_api.py:89 - timeout exceeded"
  ],
  "next_action": "fix-and-rerun"
}
```

### If Coverage Too Low

```json
{
  "type": "test-report-ack",
  "task_id": "GH-42",
  "status": "rejected",
  "message": "Coverage 65% below minimum 80%",
  "required_actions": [
    "Add tests for uncovered lines in src/auth.py:20-35",
    "Add tests for uncovered lines in src/api.py:100-120"
  ],
  "next_action": "add-tests-and-rerun"
}
```

## Error States

| State | Meaning | Action |
|-------|---------|--------|
| `report-generation-failed` | Test framework crashed | Include error in report, escalate |
| `coverage-unavailable` | Coverage tool failed | Report tests only, note coverage missing |
| `malformed-report` | Invalid JSON structure | Regenerate with correct format |
| `missing-required-fields` | Incomplete report | Add missing fields, resubmit |
| `test-hang-detected` | Test execution appears hung | Report partial results, escalate |

### Error Report Format

If test execution fails entirely:

```json
{
  "report_version": "1.0",
  "task_id": "GH-42",
  "status": "error",
  "error": {
    "type": "test-framework-crash",
    "message": "pytest ImportError: cannot import module 'auth'",
    "traceback": "Traceback (most recent call last):\n  File...",
    "partial_results": {
      "tests_run_before_crash": 12,
      "tests_passed": 10,
      "tests_failed": 2
    }
  },
  "next_steps": "Fix import error, rerun tests"
}
```

### Partial Results Handling

If only some tests could run:

```json
{
  "report_version": "1.0",
  "task_id": "GH-42",
  "status": "partial",
  "warning": "Only 45/60 tests executed due to hang prevention mechanism",
  "results": {
    "total": 45,
    "passed": 40,
    "failed": 5,
    "skipped": 0,
    "incomplete": 15
  }
}
```

## Completion Tracking

### Attempt-Based Progress Tracking

Test reports are tracked by completion milestones and orchestrator check-in attempts:

| Priority | Check-in Approach | Rationale |
|----------|------------------|-----------|
| `urgent` | Immediate follow-up after no response | Critical path blockers, production issues |
| `high` | Follow-up after 1-2 attempts | Feature development, bug fixes |
| `normal` | Follow-up after 2-3 attempts | Standard development tasks |
| `low` | Follow-up after 3+ attempts | Background refactoring, documentation |

**Progress Tracking:**
```
status_check_count = number_of_check_attempts
escalation_level = based_on_blocker_severity + unresponsiveness
```

Example:
```json
{
  "task_id": "GH-42",
  "priority": "high",
  "test_completed": true,
  "check_attempts": 2,
  "escalation_level": "monitoring"
}
```

### Escalation Flow

If test report not received by orchestrator:

#### After No Response
Orchestrator sends status request:
```json
{
  "type": "status-request",
  "task_id": "GH-42",
  "message": "Test report not received. Status?",
  "check_attempt": 1
}
```

Agent should respond with one of:
- Test report (if ready)
- Progress update (see below)
- Additional attempts request

#### After Multiple Check-ins
Orchestrator marks task as potentially stalled:
```json
{
  "type": "task-status-update",
  "task_id": "GH-42",
  "status": "potentially-stalled",
  "reason": "Test report not received after multiple check-ins",
  "check_attempts": 3,
  "action": "monitoring"
}
```

Agent can still submit report with explanation:
```json
{
  "report_version": "1.0",
  "task_id": "GH-42",
  "delay_explanation": "Coverage analysis required additional test cycles due to large codebase",
  "summary": { ... }
}
```

#### Blocker Escalation
If task is blocking critical path, orchestrator considers reassignment:
```json
{
  "type": "reassignment-warning",
  "task_id": "GH-42",
  "message": "Task blocking critical deliverable. May be reassigned if no response.",
  "blocker_severity": "high",
  "check_attempts": 4
}
```

If agent still doesn't respond, orchestrator reassigns task to another agent.

### Additional Attempts Request

If agent needs more attempts (e.g., slow tests, large codebase), request before check-in threshold:

```json
{
  "type": "additional-attempts-request",
  "task_id": "GH-42",
  "requested_additional_attempts": 3,
  "reason": "Integration tests running (10k+ tests)",
  "current_progress": "80% complete, 8000/10000 tests run",
  "completion_milestone": "test-execution"
}
```

Orchestrator responds:
```json
{
  "type": "additional-attempts-response",
  "task_id": "GH-42",
  "status": "approved",
  "additional_attempts_granted": 3,
  "message": "Extension granted. Monitor progress."
}
```

Or denies:
```json
{
  "type": "additional-attempts-response",
  "task_id": "GH-42",
  "status": "denied",
  "reason": "Task priority is urgent, blocking critical path",
  "action": "Submit partial results immediately"
}
```

### Progress Updates During Testing

For long-running test suites, agent SHOULD send progress updates at meaningful milestones (e.g., every 25% progress):

```json
{
  "type": "progress-update",
  "task_id": "GH-42",
  "phase": "running-tests",
  "progress_percent": 50,
  "details": "5000/10000 tests complete, 2 failures so far",
  "current_milestone": "integration-tests"
}
```

This prevents orchestrator from assuming the agent is stalled.

### Agent-Side Hang Prevention

Agents MUST implement test hang prevention to detect infinite loops or stuck processes:

```python
import signal

def run_tests_with_hang_prevention(task_id, max_test_duration_per_suite=3600):
    # Set technical timeout to prevent infinite hangs
    # This is NOT a policy deadline, but a safety mechanism
    # Default: 1 hour per test suite to catch hung tests

    def hang_handler(signum, frame):
        raise TimeoutError("Test execution appears hung (technical timeout)")

    signal.signal(signal.SIGALRM, hang_handler)
    signal.alarm(max_test_duration_per_suite)

    try:
        results = run_tests()  # Run actual tests
        signal.alarm(0)  # Cancel alarm
        return results
    except TimeoutError:
        # Test suite appears hung, submit partial results with hang report
        return submit_partial_test_report_with_hang_indication(task_id)
```

### Completion Best Practices

1. **Start tests immediately** - Don't delay test execution after task acceptance
2. **Request additional attempts early** - Don't wait until multiple check-ins have occurred
3. **Send progress updates** - Keep orchestrator informed on long tests at meaningful milestones
4. **Optimize test performance** - Run fast unit tests first, slow integration tests last
5. **Use partial results** - Better to report 80% tested than block on completion
6. **Cache dependencies** - Don't reinstall packages during test execution
7. **Parallelize tests** - Use `pytest -n auto` or `jest --maxWorkers=4`
8. **Monitor execution** - Log test progress to identify hung or slow tests

### Related Protocol References

See also:
- `echo-acknowledgment-protocol.md` (planned) - Acknowledgment requirements for status check messages
- `task-instruction-format.md` (planned) - Task-level completion tracking mechanism
- `messaging-protocol.md` (planned) - Message priority and completion handling

## Integration

This format integrates with:

- `messaging-protocol.md` (planned) - Test reports sent as messages
- `task-instruction-format.md` (planned) - Test requirements defined in task
- `artifact-sharing-protocol.md` (planned) - Test logs shared as artifacts
- `echo-acknowledgment-protocol.md` (planned) - Acknowledgment of status requests and timeout warnings
