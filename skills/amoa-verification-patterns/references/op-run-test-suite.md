# Operation: Run Test Suite


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
  - [Step 1: Validate Scripts First](#step-1-validate-scripts-first)
  - [Step 2: Run Tests with Result Collection](#step-2-run-tests-with-result-collection)
  - [Step 3: Check Exit Code](#step-3-check-exit-code)
  - [Step 4: Collect Test Evidence](#step-4-collect-test-evidence)
- [Test Execution Options](#test-execution-options)
  - [Basic Test Run](#basic-test-run)
  - [Worktree Isolation Testing](#worktree-isolation-testing)
  - [With Orchestrator Notification](#with-orchestrator-notification)
- [Complete Workflow Example](#complete-workflow-example)
- [Test Report Output Format](#test-report-output-format)
- [Exit Codes Reference](#exit-codes-reference)
- [Hang Prevention](#hang-prevention)
- [Best Practices](#best-practices)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-run-test-suite
---

## Purpose

Execute test suite with proper protocol to verify task completion before handoff.

## When to Use

- After completing implementation, before verification handoff
- When verifying code changes haven't introduced regressions
- When collecting test evidence for orchestrator
- When running tests in CI/CD pipeline

## Prerequisites

- Implementation is complete and code is committed
- Test environment is configured
- Dependencies are installed
- `shared/testing_protocol.py` is available

## Steps

### Step 1: Validate Scripts First

Before running tests, validate all scripts for syntax errors:

```bash
python shared/testing_protocol.py --scripts verification-patterns/scripts/
```

**What it validates:**
- Python syntax correctness
- CLI argument parsing
- Help text availability
- Required dependencies

### Step 2: Run Tests with Result Collection

Execute pytest with JSON output for structured results:

```bash
python shared/testing_protocol.py --pytest tests/ --output report.json
```

**Features:**
- Collects test results in JSON format
- Captures stdout/stderr
- Reports pass/fail counts
- Includes execution time
- Saves detailed error messages

### Step 3: Check Exit Code

Verify the test run completed successfully:

```bash
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "Tests failed with exit code $exit_code"
    # Handle failure
fi
```

### Step 4: Collect Test Evidence

Convert test results to evidence format:

```bash
python scripts/evidence_store.py add \
  --type EVENT \
  --source "testing_protocol" \
  --content "$(cat report.json)" \
  --output evidence.json
```

## Test Execution Options

### Basic Test Run

```bash
python shared/testing_protocol.py --pytest tests/ --output report.json
```

### Worktree Isolation Testing

Run tests in isolated environment to prevent pollution:

```bash
python shared/testing_protocol.py \
  --worktree /tmp/test-worktree \
  --command "pytest tests/ -v" \
  --output test-results.json
```

**Why use worktree isolation:**
- Prevents test pollution of main working directory
- Ensures clean state for each test run
- Allows parallel test execution
- Simulates CI/CD environment locally

### With Orchestrator Notification

```bash
python shared/testing_protocol.py \
  --pytest tests/ \
  --notify \
  --branch feature-xyz \
  --output test-results.json
```

## Complete Workflow Example

```bash
# 1. Validate all scripts first
python shared/testing_protocol.py --scripts verification-patterns/scripts/

# 2. Run tests in isolation with notification
python shared/testing_protocol.py \
  --worktree /tmp/test-worktree \
  --command "pytest tests/ -v" \
  --notify \
  --branch feature-verification \
  --output test-results.json

# 3. Verify consistency of results
python scripts/consistency_verifier.py json \
  --path test-results.json \
  --has-keys "passed,failed,total"

# 4. On success, verification complete
```

## Test Report Output Format

```json
{
  "report_version": "1.0",
  "task_id": "GH-42",
  "agent_id": "dev-agent-1",
  "timestamp": "2025-01-15T10:30:00Z",
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
      "error": "AssertionError: Expected 401, got 200"
    }
  ],
  "coverage": {
    "line_percent": 85.2,
    "branch_percent": 72.1
  }
}
```

## Exit Codes Reference

| Code | Meaning | Action |
|------|---------|--------|
| `0` | All tests passed | Continue to handoff |
| `1` | Tests failed or error occurred | Fix failures, rerun |
| `2` | Script validation failed | Fix script issues |

## Hang Prevention

Implement timeout to prevent infinite hangs:

```python
import signal

def run_tests_with_hang_prevention(max_duration=3600):
    def hang_handler(signum, frame):
        raise TimeoutError("Test execution appears hung")

    signal.signal(signal.SIGALRM, hang_handler)
    signal.alarm(max_duration)

    try:
        results = run_tests()
        signal.alarm(0)
        return results
    except TimeoutError:
        return submit_partial_results()
```

## Best Practices

1. **Start tests immediately** - Don't delay after task acceptance
2. **Run fast tests first** - Unit tests before integration tests
3. **Parallelize** - Use `pytest -n auto` for parallel execution
4. **Cache dependencies** - Don't reinstall packages during tests
5. **Use partial results** - Better to report 80% than block on completion
6. **Monitor execution** - Log progress to identify slow tests

## Exit Criteria

This operation is complete when:
- [ ] Scripts validated with no syntax errors
- [ ] Test suite executed successfully (or failures captured)
- [ ] Exit code captured and interpreted
- [ ] Test results saved to JSON file
- [ ] Evidence collected for verification record
- [ ] Report ready for orchestrator notification

## Related Operations

- [op-verify-exit-code.md](./op-verify-exit-code.md) - Interpreting test exit codes
- [op-collect-evidence.md](./op-collect-evidence.md) - Evidence collection from tests
- [op-generate-test-report.md](./op-generate-test-report.md) - Creating standardized reports
- [op-notify-orchestrator.md](./op-notify-orchestrator.md) - Sending test results
