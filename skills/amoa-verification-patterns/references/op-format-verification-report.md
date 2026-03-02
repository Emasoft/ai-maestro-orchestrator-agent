# Operation: Format Verification Report


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Report Components](#report-components)
- [Steps](#steps)
  - [Step 1: Create Evidence Items](#step-1-create-evidence-items)
  - [Step 2: Assemble Verification Record](#step-2-assemble-verification-record)
  - [Step 3: Validate Before Submission](#step-3-validate-before-submission)
  - [Step 4: Write to File](#step-4-write-to-file)
- [Report Format Reference](#report-format-reference)
  - [Full Verification Record](#full-verification-record)
  - [Minimal Report for Orchestrator](#minimal-report-for-orchestrator)
- [Status Values](#status-values)
- [Handoff Phase Integration](#handoff-phase-integration)
- [Output Locations](#output-locations)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-format-verification-report
---

## Purpose

Create a properly-formatted verification report for orchestrator handoff after task completion.

## When to Use

- After collecting all verification evidence
- When preparing task completion documentation
- When handing off from implementation to review phase
- When reporting verification results to orchestrator

## Prerequisites

- Evidence has been collected and validated
- Task verification is complete (PASS or FAIL determined)
- All required evidence fields are populated

## Report Components

A verification report contains:
1. **Verification metadata** (ID, task, type, timestamp)
2. **Status** (passed/failed/skipped/error)
3. **Evidence array** (minimum 2 items)
4. **Summary** (human-readable result)

## Steps

### Step 1: Create Evidence Items

Use helper functions to create properly-formatted evidence:

```python
from evidence_format import (
    create_exit_code_evidence,
    create_test_result_evidence,
    create_approval_evidence
)

# Exit code evidence
evidence1 = create_exit_code_evidence(
    exit_code=0,
    command="pytest tests/",
    stdout="All 42 tests passed",
    stderr=""
)

# Test result evidence
evidence2 = create_test_result_evidence(
    test_name="test_user_login",
    passed=True,
    duration_ms=150,
    output="Test completed successfully"
)
```

### Step 2: Assemble Verification Record

Combine evidence into a complete verification record:

```python
from datetime import datetime

verification_record = {
    "verification_id": f"verify-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "task_id": "task-123",
    "verification_type": "exit_code",
    "timestamp": datetime.now().isoformat(),
    "status": "passed",
    "evidence": [
        evidence1.to_dict(),
        evidence2.to_dict()
    ],
    "exit_code": 0,
    "command_executed": "pytest tests/",
    "duration_ms": 1500,
    "summary": "All 42 tests passed. Coverage: 85%",
    "agent_id": "test-agent"
}
```

### Step 3: Validate Before Submission

Always validate the record before submission:

```python
from evidence_format import validate_verification_record

valid, errors = validate_verification_record(verification_record)
if not valid:
    raise ValueError(f"Invalid verification record: {errors}")
```

### Step 4: Write to File

Save the report for orchestrator handoff:

```python
import json

with open("artifacts/verification-report.json", "w") as f:
    json.dump(verification_record, f, indent=2)
```

## Report Format Reference

### Full Verification Record

```json
{
  "verification_id": "verify-20250115103000",
  "task_id": "GH-42",
  "verification_type": "exit_code",
  "timestamp": "2025-01-15T10:30:00",
  "status": "passed",
  "evidence": [
    {
      "evidence_id": "exit-a1b2c3d4",
      "evidence_type": "EXIT_CODE",
      "timestamp": "2025-01-15T10:30:00",
      "description": "Exit code from pytest",
      "value": {
        "exit_code": 0,
        "command": "pytest tests/"
      }
    },
    {
      "evidence_id": "test-e5f6g7h8",
      "evidence_type": "TEST_RESULT",
      "timestamp": "2025-01-15T10:30:00",
      "description": "Test suite results",
      "value": {
        "passed": 42,
        "failed": 0,
        "skipped": 1
      }
    }
  ],
  "exit_code": 0,
  "command_executed": "pytest tests/",
  "duration_ms": 1500,
  "summary": "All 42 tests passed, 1 skipped",
  "agent_id": "test-agent",
  "environment": {
    "python_version": "3.12",
    "platform": "linux"
  }
}
```

### Minimal Report for Orchestrator

When context is limited, provide minimal summary:

```
[VERIFICATION] GH-42: PASSED
Evidence: exit_code=0, 42/42 tests passed
Timestamp: 2025-01-15T10:30:00
```

## Status Values

| Status | When to Use |
|--------|-------------|
| `passed` | All verification criteria met |
| `failed` | One or more criteria not met |
| `skipped` | Verification intentionally skipped (with reason) |
| `error` | Verification could not complete due to error |

## Handoff Phase Integration

| Handoff | Required Evidence Types |
|---------|------------------------|
| Planning to Implementation | FILE_CONTENT (architecture), OBSERVATION (risk assessment) |
| Implementation to Review | TEST_RESULT, EXIT_CODE (CI), FILE_CONTENT (code changes) |
| Review to Completion | APPROVAL (PR), TEST_RESULT, EVENT (merge commit) |

## Output Locations

| Artifact | Location |
|----------|----------|
| Full JSON report | `artifacts/verification-report.json` |
| Minimal summary | Return to orchestrator directly |
| Failure details | `artifacts/tests/failures/` |

## Exit Criteria

This operation is complete when:
- [ ] All evidence items created with helper functions
- [ ] Verification record assembled with all required fields
- [ ] Record validated with `validate_verification_record()`
- [ ] Report written to artifacts directory
- [ ] Minimal summary prepared for orchestrator

## Related Operations

- [op-collect-evidence.md](./op-collect-evidence.md) - Collecting evidence to include
- [op-validate-evidence-record.md](./op-validate-evidence-record.md) - Validating record format
- [op-notify-orchestrator.md](./op-notify-orchestrator.md) - Sending report to orchestrator
- [op-generate-test-report.md](./op-generate-test-report.md) - Creating test-specific reports
