# Exit Code Proof


## Contents

- [Table of Contents](#table-of-contents)
- [2.1 What is an Exit Code](#21-what-is-an-exit-code)
- [2.2 Why Exit Codes Matter](#22-why-exit-codes-matter)
- [2.3 Exit Code Proof Steps](#23-exit-code-proof-steps)
  - [2.3.1 Step 1: Run the Process](#231-step-1-run-the-process)
  - [2.3.2 Step 2: Check the Exit Code](#232-step-2-check-the-exit-code)
  - [2.3.3 Step 3: Interpret the Result](#233-step-3-interpret-the-result)
  - [2.3.4 Step 4: Act on the Result](#234-step-4-act-on-the-result)
- [2.4 Exit Code Proof Examples](#24-exit-code-proof-examples)
  - [2.4.1 Bash Script Example](#241-bash-script-example)
  - [2.4.2 Python Script Example](#242-python-script-example)
- [2.5 Setting Exit Codes in Your Code](#25-setting-exit-codes-in-your-code)
  - [2.5.1 Bash](#251-bash)
  - [2.5.2 Python](#252-python)
- [2.6 When to Use Exit Code Proof](#26-when-to-use-exit-code-proof)

---

## Table of Contents

- [2.1 What is an Exit Code](#21-what-is-an-exit-code)
  - 2.1.1 Definition and conventions
  - 2.1.2 Exit code 0 means success, 1-255 means failure
- [2.2 Why Exit Codes Matter](#22-why-exit-codes-matter)
  - 2.2.1 Simple, reliable, scriptable, universal
- [2.3 Exit Code Proof Steps](#23-exit-code-proof-steps)
  - 2.3.1 Step 1: Run the Process
  - 2.3.2 Step 2: Check the Exit Code
  - 2.3.3 Step 3: Interpret the Result
  - 2.3.4 Step 4: Act on the Result
- [2.4 Exit Code Proof Examples](#24-exit-code-proof-examples)
  - 2.4.1 Bash script example
  - 2.4.2 Python script example
- [2.5 Setting Exit Codes in Your Code](#25-setting-exit-codes-in-your-code)
  - 2.5.1 Bash exit codes
  - 2.5.2 Python exit codes
- [2.6 When to Use Exit Code Proof](#26-when-to-use-exit-code-proof)
  - 2.6.1 Shell scripts, CI/CD pipelines, orchestration

---

## 2.1 What is an Exit Code

An exit code is a single number sent by a program to its parent process when the program terminates.

**Convention:**
- **Exit code 0**: Success
- **Exit code 1-255**: Failure (different codes can indicate different types of failure)

---

## 2.2 Why Exit Codes Matter

Exit codes provide a reliable, standardized way to determine if a process succeeded or failed:

| Property | Benefit |
|----------|---------|
| **Simple** | One number, easy to check |
| **Reliable** | Not affected by output text |
| **Scriptable** | Easy to use in shell scripts and automation |
| **Universal** | Works across all operating systems |

---

## 2.3 Exit Code Proof Steps

### 2.3.1 Step 1: Run the Process

Execute the process and capture its exit code.

### 2.3.2 Step 2: Check the Exit Code

Immediately after the process completes, check the exit code.

### 2.3.3 Step 3: Interpret the Result

- Exit code 0 = Success
- Any other exit code = Failure

### 2.3.4 Step 4: Act on the Result

If exit code is non-zero, stop the script, log the error, and fail fast.

---

## 2.4 Exit Code Proof Examples

### 2.4.1 Bash Script Example

```bash
#!/bin/bash

# Step 1: Run a process
python3 my_script.py
SCRIPT_EXIT_CODE=$?

# Step 2: Check the exit code
# Step 3: Interpret the result
if [ $SCRIPT_EXIT_CODE -eq 0 ]; then
    # Success
    echo "Script executed successfully"
    exit 0
else
    # Failure
    echo "Script failed with exit code $SCRIPT_EXIT_CODE"
    exit 1
fi
```

### 2.4.2 Python Script Example

```python
import subprocess
import sys

# Step 1: Run a process
result = subprocess.run(['python3', 'my_script.py'])

# Step 2: Check the exit code
exit_code = result.returncode

# Step 3: Interpret the result
if exit_code == 0:
    print("Script executed successfully")
    sys.exit(0)
else:
    print(f"Script failed with exit code {exit_code}")
    sys.exit(1)
```

---

## 2.5 Setting Exit Codes in Your Code

### 2.5.1 Bash

```bash
exit 0  # Success
exit 1  # Failure
```

### 2.5.2 Python

```python
import sys
sys.exit(0)  # Success
sys.exit(1)  # Failure
```

---

## 2.6 When to Use Exit Code Proof

| Scenario | Why |
|----------|-----|
| Running processes from shell scripts | Capture success/failure reliably |
| Orchestrating multiple commands | Stop on first failure |
| Building CI/CD pipelines | Gate deployments on test results |
| Need a simple yes/no answer | Did it work or not? |
| Need to fail fast on error | Stop processing immediately |
