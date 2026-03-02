# Evidence-Based Verification


## Contents

- [Table of Contents](#table-of-contents)
- [1.1 What is Evidence](#11-what-is-evidence)
- [1.2 Evidence-Based Verification Steps](#12-evidence-based-verification-steps)
  - [1.2.1 Step 1: Define the Expected Outcome](#121-step-1-define-the-expected-outcome)
  - [1.2.2 Step 2: Run the Code](#122-step-2-run-the-code)
  - [1.2.3 Step 3: Collect Evidence](#123-step-3-collect-evidence)
  - [1.2.4 Step 4: Compare Evidence to Expectation](#124-step-4-compare-evidence-to-expectation)
  - [1.2.5 Step 5: Document Results](#125-step-5-document-results)
- [1.3 Evidence-Based Verification Example](#13-evidence-based-verification-example)
- [1.4 When to Use Evidence-Based Verification](#14-when-to-use-evidence-based-verification)

---

## Table of Contents

- [1.1 What is Evidence](#11-what-is-evidence)
  - 1.1.1 Types of measurable evidence
  - 1.1.2 Return values, output files, console output
  - 1.1.3 State changes and side effects
  - 1.1.4 Performance metrics and error signals
- [1.2 Evidence-Based Verification Steps](#12-evidence-based-verification-steps)
  - 1.2.1 Step 1: Define the Expected Outcome
  - 1.2.2 Step 2: Run the Code
  - 1.2.3 Step 3: Collect Evidence
  - 1.2.4 Step 4: Compare Evidence to Expectation
  - 1.2.5 Step 5: Document Results
- [1.3 Evidence-Based Verification Example](#13-evidence-based-verification-example)
  - 1.3.1 Python code example with all 5 steps
- [1.4 When to Use Evidence-Based Verification](#14-when-to-use-evidence-based-verification)
  - 1.4.1 New functions, modifications, proving behavior
  - 1.4.2 Troubleshooting and pre-deployment

---

## 1.1 What is Evidence

Evidence-based verification means collecting measurable proof that code produces the expected result.

Evidence is any measurable output or observable effect that proves behavior:

| Evidence Type | Description | Examples |
|--------------|-------------|----------|
| **Return values** | Numbers, strings, booleans returned by functions | `return 5`, `return True` |
| **Output files** | Files created, modified, or deleted | `output.txt`, `report.json` |
| **Console output** | Text printed to stdout or stderr | `print("Success")` |
| **State changes** | Database records, variable assignments, object mutations | New row in table |
| **Side effects** | Network requests made, APIs called, resources allocated | HTTP POST sent |
| **Performance metrics** | Execution time, memory usage, resource consumption | 150ms latency |
| **Error signals** | Exception types, error codes, error messages | `ValueError`, exit code 1 |

---

## 1.2 Evidence-Based Verification Steps

### 1.2.1 Step 1: Define the Expected Outcome

Before running code, write down exactly what you expect to happen.

**Examples:**
- "The function should return an integer equal to 5"
- "A file named 'output.txt' should be created in the current directory"
- "The database should contain exactly 10 new records"

### 1.2.2 Step 2: Run the Code

Execute the code under test in isolation. Control all inputs. Eliminate variables.

### 1.2.3 Step 3: Collect Evidence

Immediately after execution, gather all measurable data:
- Capture console output
- Read return values
- Check file system state
- Query databases
- Inspect memory state

### 1.2.4 Step 4: Compare Evidence to Expectation

Check if the evidence matches your expected outcome. If it does not match, you have discovered a bug.

### 1.2.5 Step 5: Document Results

Record:
- What you tested
- What inputs you provided
- What evidence you collected
- Whether the evidence matched expectations
- Date and time of verification

---

## 1.3 Evidence-Based Verification Example

```python
def add(a, b):
    """Add two numbers and return the result."""
    return a + b

# Step 1: Define expected outcome
# When add(2, 3) is called, it should return 5

# Step 2: Run the code
result = add(2, 3)

# Step 3: Collect evidence
# Evidence collected: result = 5 (return value)

# Step 4: Compare
# Expected: 5
# Collected: 5
# Match: YES

# Step 5: Document
print(f"Verification: add(2, 3) returns {result} - PASS")
```

---

## 1.4 When to Use Evidence-Based Verification

Use evidence-based verification:

| Scenario | Why |
|----------|-----|
| When you write a new function | Prove it works before integration |
| When you modify existing code | Ensure no regressions |
| When you want to prove behavior to another person | Provide reproducible evidence |
| When you need to troubleshoot | Find where behavior diverges from expectation |
| Before deploying to production | Final safety check |
