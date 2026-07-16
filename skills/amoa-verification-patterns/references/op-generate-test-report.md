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
- [Error Report Format](#error-report-format)
- [Partial Results Format](#partial-results-format)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

## Operation Metadata

- procedure: proc-complete-task
- workflow-instruction: Step 19 - Task Completion
- operation-id: op-generate-test-report

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

Canonical copy: the standard report JSON structure is maintained in [test-report-format.md](test-report-format.md) (section "Standard Report Structure") — read that file; this pointer avoids a drifting duplicate.

## Steps

### Step 1: Run Tests with JSON Output

Canonical copy: the per-framework JSON-output commands (pytest, Jest, Go, Rust) are maintained in [test-report-format.md](test-report-format.md) (section "Language-Specific Converters") — read that file; this pointer avoids a drifting duplicate.

Run the command for the project's framework and confirm the raw JSON report file was produced.

### Step 2: Convert to Standard Format

Canonical copy: the pytest-to-standard-format converter is maintained in [test-report-format.md](test-report-format.md) (section "Language-Specific Converters") — read that file; this pointer avoids a drifting duplicate.

delta: for this operation the converter must also populate the envelope fields `report_version`, `task_id` (from environment or config), `agent_id`, and `timestamp` (from the pytest report's `created` field); each failure entry must include `file` (the nodeid segment before `::`); and missing `call` data must fall back to the error string `"Unknown"`.

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

Canonical copy: the expected minimal-summary output example is maintained in [test-report-format.md](test-report-format.md) (section "Minimal Report (For Orchestrator)") — read that file; this pointer avoids a drifting duplicate.

## Report Locations

Canonical copy: the framework-to-report-file locations table is maintained in [test-report-format.md](test-report-format.md) (section "Report Locations") — read that file; this pointer avoids a drifting duplicate.

## Failure Detail Levels

Canonical copy: the three failure detail levels (minimal, with error, with traceback) are maintained in [test-report-format.md](test-report-format.md) (section "Failure Detail Levels") — read that file; this pointer avoids a drifting duplicate.

## Error Report Format

Canonical copy: the error report JSON format (used when test execution fails entirely) is maintained in [test-report-format.md](test-report-format.md) (section "Error Report Format") — read that file; this pointer avoids a drifting duplicate.

## Partial Results Format

Canonical copy: the partial-results report JSON format is maintained in [test-report-format.md](test-report-format.md) (section "Partial Results Handling") — read that file; this pointer avoids a drifting duplicate.

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
