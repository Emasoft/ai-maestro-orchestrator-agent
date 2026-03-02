# Operation: Verify Exit Code


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Exit Code Convention](#exit-code-convention)
- [Steps](#steps)
  - [Step 1: Run the Process](#step-1-run-the-process)
  - [Step 2: Check the Exit Code](#step-2-check-the-exit-code)
  - [Step 3: Interpret the Result](#step-3-interpret-the-result)
  - [Step 4: Act on the Result](#step-4-act-on-the-result)
- [Examples](#examples)
  - [Bash Script Example](#bash-script-example)
  - [Python Script Example](#python-script-example)
- [Setting Exit Codes in Your Code](#setting-exit-codes-in-your-code)
  - [Bash](#bash)
  - [Python](#python)
- [Output Format](#output-format)
- [Common Pitfalls](#common-pitfalls)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-verify-exit-code
---

## Purpose

Use process exit codes as verification signals to determine task completion success or failure.

## When to Use

- When running scripts or commands that should succeed
- When orchestrating multiple commands in sequence
- When building CI/CD pipelines
- When a simple yes/no answer is needed: "Did it work?"

## Prerequisites

- Process or script to execute is ready
- Exit code conventions are understood (0=success, non-zero=failure)

## Exit Code Convention

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success - process completed as expected |
| `1` | General failure |
| `2` | Script validation or syntax error |
| `1-255` | Various failure types (specific meaning varies by tool) |

## Steps

### Step 1: Run the Process

Execute the process and capture its exit code immediately.

**Bash:**
```bash
python3 my_script.py
exit_code=$?
```

**Python:**
```python
import subprocess
result = subprocess.run(['python3', 'my_script.py'])
exit_code = result.returncode
```

### Step 2: Check the Exit Code

Immediately after the process completes, check the exit code value.

### Step 3: Interpret the Result

Apply the convention:
- Exit code `0` = Success
- Any other exit code = Failure

### Step 4: Act on the Result

If exit code is non-zero:
1. Stop the workflow
2. Log the error
3. Fail fast
4. Report to orchestrator

## Examples

### Bash Script Example

```bash
#!/bin/bash

# Step 1: Run a process
pytest tests/
exit_code=$?

# Step 2-3: Check and interpret
if [ $exit_code -eq 0 ]; then
    echo "SUCCESS: All tests passed"
    exit 0
else
    echo "FAILURE: Tests failed with exit code $exit_code"
    exit 1
fi
```

### Python Script Example

```python
import subprocess
import sys

# Step 1: Run a process
result = subprocess.run(['pytest', 'tests/'], capture_output=True, text=True)

# Step 2: Get exit code
exit_code = result.returncode

# Step 3: Interpret
if exit_code == 0:
    print("SUCCESS: All tests passed")
    sys.exit(0)
else:
    print(f"FAILURE: Tests failed with exit code {exit_code}")
    print(f"stderr: {result.stderr}")
    sys.exit(1)
```

## Setting Exit Codes in Your Code

### Bash

```bash
# Success
exit 0

# Failure
exit 1

# Script validation error
exit 2
```

### Python

```python
import sys

# Success
sys.exit(0)

# Failure
sys.exit(1)

# Failure with message
sys.exit("Error: missing configuration")
```

## Output Format

Exit code evidence for orchestrator:

```json
{
  "evidence_id": "exit-abc123",
  "evidence_type": "EXIT_CODE",
  "timestamp": "2025-01-15T10:30:00Z",
  "description": "Exit code from pytest execution",
  "value": {
    "exit_code": 0,
    "command": "pytest tests/",
    "stdout": "All 42 tests passed",
    "stderr": ""
  }
}
```

## Common Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| Exit code 0 but process failed | Script doesn't set exit code | Add explicit `sys.exit(1)` on failure |
| Exit code lost | Checked after another command | Capture immediately with `$?` |
| Multiple processes | Only last exit code captured | Check each process individually |

## Exit Criteria

This operation is complete when:
- [ ] Process was executed
- [ ] Exit code was captured immediately after execution
- [ ] Exit code was interpreted (0=success, non-zero=failure)
- [ ] Appropriate action was taken based on result
- [ ] Evidence was documented

## Related Operations

- [op-collect-evidence.md](./op-collect-evidence.md) - General evidence collection
- [op-run-test-suite.md](./op-run-test-suite.md) - Running tests that produce exit codes
- [op-format-verification-report.md](./op-format-verification-report.md) - Including exit codes in reports
