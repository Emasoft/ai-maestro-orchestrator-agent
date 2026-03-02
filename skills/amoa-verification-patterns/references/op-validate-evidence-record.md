# Operation: Validate Evidence Record


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Validation Requirements](#validation-requirements)
  - [Minimum Evidence Items](#minimum-evidence-items)
  - [Exit Code Verification](#exit-code-verification)
- [Steps](#steps)
  - [Step 1: Validate Single Evidence Item](#step-1-validate-single-evidence-item)
  - [Step 2: Collect Required Fields](#step-2-collect-required-fields)
  - [Step 3: Build Verification Record](#step-3-build-verification-record)
  - [Step 4: Validate Verification Record](#step-4-validate-verification-record)
  - [Step 5: Submit to Orchestrator](#step-5-submit-to-orchestrator)
- [Required Verification Record Fields](#required-verification-record-fields)
- [Evidence Types Reference](#evidence-types-reference)
- [Verification Statuses](#verification-statuses)
- [Command-Line Validation](#command-line-validation)
- [Common Validation Errors](#common-validation-errors)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-validate-evidence-record
---

## Purpose

Validate that evidence and verification records meet format requirements before submission to orchestrator.

## When to Use

- Before submitting evidence to orchestrator handoff
- Before creating verification reports
- When collecting evidence from multiple sources
- When preparing task completion documentation

## Prerequisites

- Evidence has been collected
- `scripts/evidence_format.py` is available
- Minimum 2 evidence items collected (per validation requirements)

## Validation Requirements

### Minimum Evidence Items

Every verification record must include at least **2 pieces of evidence**. Single evidence items are insufficient for reliability.

### Exit Code Verification

When `verification_type` is `"exit_code"`, the record must include an `exit_code` field.

## Steps

### Step 1: Validate Single Evidence Item

Before adding evidence to a record, validate it:

```python
from evidence_format import validate_evidence

evidence_dict = {
    "evidence_id": "test-abc123",
    "evidence_type": "test_result",
    "timestamp": "2025-01-15T12:00:00",
    "description": "Unit test result for login function",
    "value": {"passed": True, "duration_ms": 150}
}

valid, errors = validate_evidence(evidence_dict)
if not valid:
    for error in errors:
        print(f"Evidence error: {error}")
    # Fix errors before proceeding
```

### Step 2: Collect Required Fields

Ensure every evidence item has required fields:

| Field | Required | Description |
|-------|----------|-------------|
| `evidence_id` | Yes | Unique ID (alphanumeric with - and _) |
| `evidence_type` | Yes | From EvidenceType enum |
| `timestamp` | Yes | ISO-8601 format |
| `description` | Yes | Human-readable description |
| `value` | Yes | Type-specific data object |
| `source` | No | Evidence source |
| `related_task` | No | Task ID reference |
| `collector` | No | Agent/tool that collected it |

### Step 3: Build Verification Record

Assemble evidence into a complete verification record:

```python
record = {
    "verification_id": "verify-001",
    "task_id": "task-123",
    "verification_type": "exit_code",
    "timestamp": "2025-01-15T12:00:00",
    "status": "passed",
    "evidence": [evidence1, evidence2],  # Minimum 2 items
    "exit_code": 0  # Required for exit_code type
}
```

### Step 4: Validate Verification Record

Validate the complete record before submission:

```python
from evidence_format import validate_verification_record

valid, errors = validate_verification_record(record)
if not valid:
    for error in errors:
        print(f"Record error: {error}")
    sys.exit(1)  # Do not submit invalid records
```

### Step 5: Submit to Orchestrator

Only submit after validation passes.

## Required Verification Record Fields

| Field | Required | Description |
|-------|----------|-------------|
| `verification_id` | Yes | Unique verification ID |
| `task_id` | Yes | Related task ID |
| `verification_type` | Yes | `exit_code`, `evidence_based`, `integration`, `e2e` |
| `timestamp` | Yes | ISO-8601 format |
| `status` | Yes | `passed`, `failed`, `skipped`, `error` |
| `evidence` | Yes | Array of Evidence items (minimum 2) |
| `exit_code` | Conditional | Required when type is `exit_code` |
| `command_executed` | No | Command that was run |
| `duration_ms` | No | Execution duration |
| `summary` | No | Human-readable summary |

## Evidence Types Reference

| Type | Description |
|------|-------------|
| `EXIT_CODE` | Process exit codes |
| `FILE_CONTENT` | File contents or diffs |
| `COMMAND_OUTPUT` | Command stdout/stderr |
| `SCREENSHOT` | Visual evidence |
| `LOG_EXCERPT` | Extracted log entries |
| `TEST_RESULT` | Test execution results |
| `API_RESPONSE` | API call responses |
| `METRIC` | Performance or quality metrics |
| `APPROVAL` | Human approval or review |

## Verification Statuses

| Status | Meaning |
|--------|---------|
| `PASSED` | Verification succeeded |
| `FAILED` | Verification failed |
| `SKIPPED` | Verification was skipped (with reason) |
| `ERROR` | Verification encountered an error |

## Command-Line Validation

Validate evidence files from command line:

```bash
# Validate evidence file
python scripts/evidence_format.py --validate evidence.json

# Print schema documentation
python scripts/evidence_format.py --schema
```

**Exit codes:**
- `0`: Validation passed
- `1`: Validation failed

## Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing required field: evidence_id" | Field not provided | Add unique evidence_id |
| "Invalid evidence_type" | Type not in enum | Use valid type from list |
| "Insufficient evidence items" | Less than 2 items | Collect more evidence |
| "Missing exit_code for exit_code verification" | Type is exit_code but field missing | Add exit_code field |
| "Invalid timestamp format" | Not ISO-8601 | Use format: `2025-01-15T12:00:00` |

## Exit Criteria

This operation is complete when:
- [ ] All evidence items validated individually
- [ ] Verification record has all required fields
- [ ] Minimum 2 evidence items included
- [ ] Exit code field included (if verification_type is exit_code)
- [ ] `validate_verification_record()` returns `(True, [])` with no errors
- [ ] Record is ready for orchestrator submission

## Related Operations

- [op-collect-evidence.md](./op-collect-evidence.md) - Collecting evidence to validate
- [op-format-verification-report.md](./op-format-verification-report.md) - Creating complete verification report
- [op-notify-orchestrator.md](./op-notify-orchestrator.md) - Submitting validated evidence
