# Operation: Generate Test Report


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Standard Report Structure](#standard-report-structure)
- [Steps](#steps)
  - [Step 1: Run Tests with JSON Output](#step-1-run-tests-with-json-output)
  - [Step 2: Convert to Standard Format](#step-2-convert-to-standard-format)
  - [Step 3: Write Standard Report](#step-3-write-standard-report)
  - [Step 4: Generate Minimal Summary](#step-4-generate-minimal-summary)
- [Report Locations](#report-locations)
- [Failure Detail Levels](#failure-detail-levels)
  - [Level 1: Minimal (default)](#level-1-minimal-default)
  - [Level 2: With Error](#level-2-with-error)
  - [Level 3: With Traceback](#level-3-with-traceback)
- [Error Report Format](#error-report-format)
- [Partial Results Format](#partial-results-format)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-generate-test-report
---

## Purpose

Create standardized test reports in the format required by orchestrator for task completion verification.

## When to Use

- After test suite execution completes
- When preparing verification handoff to orchestrator
- When converting language-specific test output to standard format
- When documenting test coverage for task completion

## Prerequisites

- Test suite has been executed
- Raw test output is available (pytest, jest, go test, etc.)
- Task ID is known

## Standard Report Structure

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

## Steps

### Step 1: Run Tests with JSON Output

**Python (pytest):**
```bash
pytest --json-report --json-report-file=test-report.json
```

**JavaScript (Jest):**
```bash
jest --json --outputFile=test-report.json
```

**Go:**
```bash
go test -json ./... > test-report.json
```

**Rust:**
```bash
cargo test -- --format json > test-report.json
```

### Step 2: Convert to Standard Format

**Python (pytest) converter:**

```python
import json

def convert_pytest_report(pytest_json_path):
    with open(pytest_json_path) as f:
        data = json.load(f)

    return {
        "report_version": "1.0",
        "task_id": get_task_id(),  # From environment or config
        "agent_id": get_agent_id(),
        "timestamp": data.get("created"),
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
                "file": t["nodeid"].split("::")[0],
                "error": t["call"]["longrepr"] if "call" in t else "Unknown"
            }
            for t in data.get("tests", []) if t["outcome"] == "failed"
        ]
    }
```

### Step 3: Write Standard Report

Save to artifacts directory:

```python
import json

report = convert_pytest_report("pytest-report.json")
with open("artifacts/tests/pytest-report.json", "w") as f:
    json.dump(report, f, indent=2)
```

### Step 4: Generate Minimal Summary

Create orchestrator-friendly summary:

```python
def generate_minimal_summary(report):
    summary = report["summary"]
    failures = report.get("failures", [])

    lines = [
        f"[TESTS] {summary['total']} total: {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped ({summary['duration_seconds']}s)"
    ]

    if failures:
        failed_tests = [f"{f['file']}:{f.get('line', '?')}" for f in failures[:5]]
        lines.append(f"FAILED: {', '.join(failed_tests)}")

    if "coverage" in report:
        cov = report["coverage"]
        lines.append(f"COVERAGE: {cov['line_percent']}% lines, {cov['branch_percent']}% branches")

    return "\n".join(lines)
```

**Output:**
```
[TESTS] 45 total: 42 passed, 2 failed, 1 skipped (12.5s)
FAILED: test_auth.py:45, test_api.py:89
COVERAGE: 85% lines, 72% branches
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
Full traceback saved separately: `artifacts/tests/failures/test_auth_45.txt`

## Error Report Format

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

## Partial Results Format

If only some tests could run:

```json
{
  "report_version": "1.0",
  "task_id": "GH-42",
  "status": "partial",
  "warning": "Only 45/60 tests executed due to hang prevention",
  "results": {
    "total": 45,
    "passed": 40,
    "failed": 5,
    "skipped": 0,
    "incomplete": 15
  }
}
```

## Exit Criteria

This operation is complete when:
- [ ] Tests executed with JSON output
- [ ] Raw output converted to standard format
- [ ] Standard report saved to artifacts directory
- [ ] Minimal summary generated for orchestrator
- [ ] Failure details saved (if any failures)

## Related Operations

- [op-run-test-suite.md](./op-run-test-suite.md) - Running tests that produce output
- [op-format-verification-report.md](./op-format-verification-report.md) - Overall verification report
- [op-notify-orchestrator.md](./op-notify-orchestrator.md) - Sending report to orchestrator
- [op-collect-evidence.md](./op-collect-evidence.md) - Including test results as evidence
