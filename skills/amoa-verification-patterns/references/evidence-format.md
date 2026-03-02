# Evidence Format Enforcement


## Contents

- [Table of Contents](#table-of-contents)
- [7.1 Evidence Format Script](#71-evidence-format-script)
- [7.2 Evidence Types](#72-evidence-types)
- [7.3 Verification Statuses](#73-verification-statuses)
- [7.4 Required Evidence Fields](#74-required-evidence-fields)
- [7.5 Required Verification Record Fields](#75-required-verification-record-fields)
- [7.6 Validation Requirements](#76-validation-requirements)
- [7.7 Validating Evidence Before Submission](#77-validating-evidence-before-submission)
- [7.8 Creating Properly-Formatted Evidence](#78-creating-properly-formatted-evidence)
- [7.9 Integration with Handoff Protocols](#79-integration-with-handoff-protocols)
- [7.10 Command-Line Usage](#710-command-line-usage)

---

## Table of Contents

- [7.1 Evidence Format Script](#71-evidence-format-script)
  - 7.1.1 Location and purpose
  - 7.1.2 Evidence dataclass
  - 7.1.3 VerificationRecord dataclass
- [7.2 Evidence Types](#72-evidence-types)
  - 7.2.1 EXIT_CODE, FILE_CONTENT, COMMAND_OUTPUT
  - 7.2.2 SCREENSHOT, LOG_EXCERPT, TEST_RESULT
  - 7.2.3 API_RESPONSE, METRIC, APPROVAL
- [7.3 Verification Statuses](#73-verification-statuses)
  - 7.3.1 PASSED, FAILED, SKIPPED, ERROR
- [7.4 Required Evidence Fields](#74-required-evidence-fields)
  - 7.4.1 evidence_id, evidence_type, timestamp
  - 7.4.2 description, value, optional fields
- [7.5 Required Verification Record Fields](#75-required-verification-record-fields)
  - 7.5.1 verification_id, task_id, verification_type
  - 7.5.2 timestamp, status, evidence array
- [7.6 Validation Requirements](#76-validation-requirements)
  - 7.6.1 Minimum evidence items
  - 7.6.2 Exit code verification requirements
- [7.7 Validating Evidence Before Submission](#77-validating-evidence-before-submission)
  - 7.7.1 validate_evidence() usage
  - 7.7.2 validate_verification_record() usage
- [7.8 Creating Properly-Formatted Evidence](#78-creating-properly-formatted-evidence)
  - 7.8.1 create_exit_code_evidence()
  - 7.8.2 create_test_result_evidence()
  - 7.8.3 create_approval_evidence()
- [7.9 Integration with Handoff Protocols](#79-integration-with-handoff-protocols)
  - 7.9.1 Planning to Implementation handoff
  - 7.9.2 Implementation to Review handoff
  - 7.9.3 Review to Completion handoff
- [7.10 Command-Line Usage](#710-command-line-usage)
  - 7.10.1 Validate evidence files
  - 7.10.2 Print schema documentation

---

## 7.1 Evidence Format Script

**Location**: `scripts/evidence_format.py`

This script provides:
- **Evidence** dataclass: Single piece of verification evidence
- **VerificationRecord** dataclass: Complete verification report
- **Validation functions**: Enforce format requirements
- **Helper functions**: Create properly-formatted evidence

---

## 7.2 Evidence Types

All evidence must specify one of these types:

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

---

## 7.3 Verification Statuses

All verification records must report one of these statuses:

| Status | Meaning |
|--------|---------|
| `PASSED` | Verification succeeded |
| `FAILED` | Verification failed |
| `SKIPPED` | Verification was skipped (with reason) |
| `ERROR` | Verification encountered an error |

---

## 7.4 Required Evidence Fields

Every evidence item must include:

```python
{
    "evidence_id": "exit-a1b2c3d4",      # Unique ID (alphanumeric with - and _)
    "evidence_type": "exit_code",         # From EvidenceType enum
    "timestamp": "2025-01-01T12:00:00",   # ISO-8601 format
    "description": "Exit code from: pytest",
    "value": {                            # Type-specific data
        "exit_code": 0,
        "command": "pytest tests/"
    },
    "source": "command_execution",        # Optional: evidence source
    "related_task": "task-123",           # Optional: task ID
    "collector": "test-agent"             # Optional: agent/tool name
}
```

---

## 7.5 Required Verification Record Fields

Every verification record must include:

```python
{
    "verification_id": "verify-12345",
    "task_id": "task-123",
    "verification_type": "exit_code",     # exit_code|evidence_based|integration|e2e
    "timestamp": "2025-01-01T12:00:00",
    "status": "passed",                   # passed|failed|skipped|error
    "evidence": [                         # List of Evidence items
        { /* Evidence item 1 */ },
        { /* Evidence item 2 */ }
    ],
    "command_executed": "pytest tests/",  # Optional
    "exit_code": 0,                       # Required for exit_code type
    "duration_ms": 1500,                  # Optional
    "summary": "All tests passed",        # Optional
    "details": "...",                     # Optional
    "agent_id": "test-agent",             # Optional
    "environment": {}                     # Optional
}
```

---

## 7.6 Validation Requirements

From `../shared/thresholds.py` (`VERIFICATION` thresholds):

- **Minimum evidence items**: `MIN_EVIDENCE_ITEMS = 2`
  - Every verification record must include at least 2 pieces of evidence
  - Single evidence items are insufficient for reliability

- **Exit code verification**: Must include `exit_code` field when `verification_type` is `"exit_code"`

Evidence remains valid until system state changes. Re-collect evidence when dependencies, code, or configuration change.

---

## 7.7 Validating Evidence Before Submission

Use the validation functions before submitting evidence to orchestrator or handoff:

```python
from evidence_format import validate_evidence, validate_verification_record

# Validate single evidence item
evidence_dict = {
    "evidence_id": "test-abc123",
    "evidence_type": "test_result",
    "timestamp": "2025-01-01T12:00:00",
    "description": "Unit test result",
    "value": {"passed": True}
}

valid, errors = validate_evidence(evidence_dict)
if not valid:
    for error in errors:
        print(f"Evidence error: {error}")
    sys.exit(1)

# Validate complete verification record
record = {
    "verification_id": "verify-001",
    "task_id": "task-123",
    "verification_type": "exit_code",
    "timestamp": "2025-01-01T12:00:00",
    "status": "passed",
    "evidence": [evidence_dict, /* more evidence */],
    "exit_code": 0
}

valid, errors = validate_verification_record(record)
if not valid:
    for error in errors:
        print(f"Record error: {error}")
    sys.exit(1)
```

---

## 7.8 Creating Properly-Formatted Evidence

Use helper functions to create evidence:

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
    stdout="All tests passed",
    stderr=""
)

# Test result evidence
evidence2 = create_test_result_evidence(
    test_name="test_user_login",
    passed=True,
    duration_ms=150,
    output="Test completed successfully"
)

# Approval evidence
evidence3 = create_approval_evidence(
    approver="orchestrator",
    approval_type="code_review",
    reference="PR #123"
)

# All helper functions return Evidence objects
print(evidence1.to_dict())  # Convert to dict for JSON serialization
```

---

## 7.9 Integration with Handoff Protocols

Evidence format enforcement integrates with **handoff protocols** (`../shared/references/handoff-protocols.md`):

| Handoff | Required Evidence |
|---------|-------------------|
| Planning to Implementation | Architecture diagram (FILE_CONTENT), Risk assessment (OBSERVATION) |
| Implementation to Review | Test results (TEST_RESULT), CI status (EXIT_CODE), Code changes (FILE_CONTENT) |
| Review to Completion | PR approval (APPROVAL), Verification (TEST_RESULT or EXIT_CODE), Merge commit (EVENT) |

See handoff-protocols.md for complete deliverable requirements at each phase.

---

## 7.10 Command-Line Usage

Validate evidence files before submission:

```bash
# Validate evidence file
python scripts/evidence_format.py --validate evidence.json

# Print schema documentation
python scripts/evidence_format.py --schema
```

**Exit codes:**
- `0`: Validation passed
- `1`: Validation failed (errors printed to stdout)
