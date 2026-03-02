# Operation: Collect Evidence


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
  - [Step 1: Define Expected Outcome](#step-1-define-expected-outcome)
  - [Step 2: Run the Code](#step-2-run-the-code)
  - [Step 3: Collect Evidence](#step-3-collect-evidence)
  - [Step 4: Compare Evidence to Expectation](#step-4-compare-evidence-to-expectation)
  - [Step 5: Document Results](#step-5-document-results)
- [Output Format](#output-format)
- [Common Evidence Types](#common-evidence-types)
- [Verification Principles](#verification-principles)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-collect-evidence
---

## Purpose

Collect measurable proof that code produces the expected result during task completion verification.

## When to Use

- When verifying a completed implementation works correctly
- When proving behavior to orchestrator before handoff
- When documenting that a task meets its acceptance criteria

## Prerequisites

- Task implementation is complete
- Expected outcomes are defined
- Test environment is ready

## Steps

### Step 1: Define Expected Outcome

Write down exactly what you expect to happen before running code.

Examples:
- "The function should return an integer equal to 5"
- "A file named 'output.txt' should be created"
- "The database should contain exactly 10 new records"
- "Exit code should be 0"

### Step 2: Run the Code

Execute the code under test in isolation. Control all inputs. Eliminate variables.

```bash
# Example: Run the implementation
python src/my_module.py --input test_data.json
```

### Step 3: Collect Evidence

Immediately after execution, gather all measurable data:

| Evidence Type | How to Collect |
|--------------|----------------|
| Return values | Capture function return value |
| Output files | Read file content, check existence |
| Console output | Capture stdout/stderr |
| State changes | Query database, check object state |
| Exit codes | Capture `$?` in bash, `result.returncode` in Python |
| Performance | Measure execution time |

### Step 4: Compare Evidence to Expectation

Check if collected evidence matches expected outcome.

```python
# Evidence collected: result = 5
# Expected: 5
# Match: YES -> PASS
# Match: NO -> FAIL
```

### Step 5: Document Results

Record:
- What you tested
- What inputs you provided
- What evidence you collected
- Whether evidence matched expectations
- Date and time of verification

## Output Format

Evidence must be structured for orchestrator handoff:

```json
{
  "evidence_id": "evidence-abc123",
  "evidence_type": "return_value",
  "timestamp": "2025-01-15T10:30:00Z",
  "description": "Function add(2,3) return value",
  "value": {
    "expected": 5,
    "actual": 5,
    "match": true
  }
}
```

## Common Evidence Types

| Type | Description | Example |
|------|-------------|---------|
| `EXIT_CODE` | Process exit codes | `{"exit_code": 0, "command": "pytest"}` |
| `FILE_CONTENT` | File contents or diffs | `{"path": "output.txt", "content": "..."}` |
| `COMMAND_OUTPUT` | Command stdout/stderr | `{"stdout": "...", "stderr": ""}` |
| `TEST_RESULT` | Test execution results | `{"passed": true, "name": "test_login"}` |
| `API_RESPONSE` | API call responses | `{"status": 200, "body": {...}}` |
| `METRIC` | Performance metrics | `{"latency_ms": 150}` |

## Verification Principles

1. **Never trust assumptions** - Verify every claim with evidence
2. **Measure what matters** - Collect evidence that answers "Does it work?"
3. **Reproducibility** - Evidence must be reproducible
4. **Fail fast** - Stop immediately on failure, report it
5. **Document everything** - Evidence becomes your proof

## Exit Criteria

This operation is complete when:
- [ ] Expected outcome was defined before execution
- [ ] Code was executed in controlled environment
- [ ] Evidence was collected and documented
- [ ] Evidence was compared to expectation
- [ ] Result (PASS/FAIL) is determined

## Related Operations

- [op-verify-exit-code.md](./op-verify-exit-code.md) - Using exit codes as evidence
- [op-validate-evidence-record.md](./op-validate-evidence-record.md) - Validating evidence format
- [op-format-verification-report.md](./op-format-verification-report.md) - Creating verification report
