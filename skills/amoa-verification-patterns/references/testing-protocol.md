# Testing Protocol


## Contents

- [Table of Contents](#table-of-contents)
- [8.1 Script Validation](#81-script-validation)
- [8.2 Pytest Integration](#82-pytest-integration)
- [8.3 Worktree Isolation Testing](#83-worktree-isolation-testing)
- [8.4 AI Maestro Notification](#84-ai-maestro-notification)
- [8.5 Combined Workflow Example](#85-combined-workflow-example)
- [8.6 Testing Protocol Scripts](#86-testing-protocol-scripts)
- [8.7 Integration with Verification Scripts](#87-integration-with-verification-scripts)
  - [8.7.1 Evidence Collection](#871-evidence-collection)
  - [8.7.2 Consistency Verification](#872-consistency-verification)
  - [8.7.3 Quality Pattern Detection](#873-quality-pattern-detection)
- [Troubleshooting](#troubleshooting)
  - [Problem: Script Validation Fails With Import Errors](#problem-script-validation-fails-with-import-errors)
  - [Problem: Pytest Collection Errors](#problem-pytest-collection-errors)
  - [Problem: Worktree Isolation Tests Fail Differently Than Local](#problem-worktree-isolation-tests-fail-differently-than-local)
  - [Problem: AI Maestro Notification Not Delivered](#problem-ai-maestro-notification-not-delivered)
  - [Problem: Test Results JSON Malformed](#problem-test-results-json-malformed)
  - [Problem: Evidence Collection Fails](#problem-evidence-collection-fails)
  - [Problem: Quality Pattern Detector False Positives](#problem-quality-pattern-detector-false-positives)

---

## Table of Contents

- [8.1 Script Validation](#81-script-validation)
  - 8.1.1 Validating syntax and CLI for scripts
  - 8.1.2 What it validates
- [8.2 Pytest Integration](#82-pytest-integration)
  - 8.2.1 Running pytest with result collection
  - 8.2.2 Features and output format
- [8.3 Worktree Isolation Testing](#83-worktree-isolation-testing)
  - 8.3.1 Running tests in isolated environment
  - 8.3.2 Why use worktree isolation
  - 8.3.3 What happens during worktree testing
- [8.4 AI Maestro Notification](#84-ai-maestro-notification)
  - 8.4.1 Sending test results to orchestrator
  - 8.4.2 Notification contents
  - 8.4.3 When to use notifications
- [8.5 Combined Workflow Example](#85-combined-workflow-example)
  - 8.5.1 Complete testing workflow with notification
- [8.6 Testing Protocol Scripts](#86-testing-protocol-scripts)
  - 8.6.1 Location and command reference
  - 8.6.2 Exit codes
- [8.7 Integration with Verification Scripts](#87-integration-with-verification-scripts)
  - 8.7.1 Evidence collection
  - 8.7.2 Consistency verification
  - 8.7.3 Quality pattern detection

---

## 8.1 Script Validation

Validate syntax and CLI for all scripts:

```bash
python shared/testing_protocol.py --scripts verification-patterns/scripts/
```

**What it validates:**
- Python syntax correctness
- CLI argument parsing
- Help text availability
- Required dependencies

---

## 8.2 Pytest Integration

Run pytest with result collection:

```bash
python shared/testing_protocol.py --pytest tests/ --output report.json
```

**Features:**
- Collects test results in JSON format
- Captures stdout/stderr
- Reports pass/fail counts
- Includes execution time
- Saves detailed error messages

---

## 8.3 Worktree Isolation Testing

Run tests in isolated worktree environment:

```bash
python shared/testing_protocol.py --worktree /path/to/worktree --command "pytest tests/"
```

**Why use worktree isolation:**
- Prevents test pollution of main working directory
- Ensures clean state for each test run
- Allows parallel test execution
- Simulates CI/CD environment locally

**What happens:**
1. Creates fresh git worktree at specified path
2. Copies necessary files (tests, scripts, config)
3. Executes test command in isolation
4. Collects results
5. Cleans up worktree

---

## 8.4 AI Maestro Notification

Send test results to orchestrator via AI Maestro:

```bash
python shared/testing_protocol.py --pytest tests/ --notify --branch feature-xyz
```

**Notification includes:**
- Test pass/fail summary
- Branch name
- Timestamp
- Error details (if any)
- Link to full report

**When to use:**
- After completing test run in background task
- When tests finish in CI/CD
- To alert orchestrator of failures
- To trigger next workflow step

---

## 8.5 Combined Workflow Example

Complete testing workflow with notification:

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

# 3. On success, verification complete
```

---

## 8.6 Testing Protocol Scripts

**Location**: `shared/testing_protocol.py`

**Command reference:**

```bash
# Basic script validation
python shared/testing_protocol.py --scripts <directory>

# Pytest with JSON output
python shared/testing_protocol.py --pytest <test-directory> --output <file.json>

# Worktree isolation
python shared/testing_protocol.py --worktree <path> --command "<command>"

# Full workflow with notification
python shared/testing_protocol.py \
  --pytest <test-dir> \
  --worktree <path> \
  --notify \
  --branch <branch-name> \
  --output <file.json>
```

**Exit codes:**
- `0`: All tests passed
- `1`: Tests failed or error occurred
- `2`: Script validation failed

---

## 8.7 Integration with Verification Scripts

### 8.7.1 Evidence Collection

```bash
# Run tests and collect evidence
python shared/testing_protocol.py --pytest tests/ --output results.json
python scripts/evidence_store.py add \
  --type EVENT \
  --source "testing_protocol" \
  --content "$(cat results.json)" \
  --output evidence.json
```

### 8.7.2 Consistency Verification

```bash
# Verify test results are consistent
python scripts/consistency_verifier.py json \
  --path results.json \
  --has-keys "passed,failed,total"
```

### 8.7.3 Quality Pattern Detection

```bash
# Check for test anti-patterns
python scripts/quality_pattern_detector.py \
  --path tests/ \
  --lang python \
  --output test-quality.json
```

---

## Troubleshooting

### Problem: Script Validation Fails With Import Errors

**Symptoms**: `--scripts` validation reports import errors for dependencies.

**Solution**:
1. Ensure virtual environment is activated before running validation
2. Install missing dependencies: `uv pip install -r requirements.txt`
3. Check if script uses conditional imports that fail at parse time
4. Verify Python version matches project requirements (3.12+)
5. For scripts with optional dependencies, add try/except around imports

### Problem: Pytest Collection Errors

**Symptoms**: `--pytest` fails during collection phase, no tests run.

**Solution**:
1. Check for syntax errors in test files: `python -m py_compile tests/*.py`
2. Verify conftest.py fixtures are valid
3. Check for circular imports in test modules
4. Ensure test file naming follows `test_*.py` pattern
5. Run pytest directly with `-v --collect-only` to diagnose

### Problem: Worktree Isolation Tests Fail Differently Than Local

**Symptoms**: Tests pass locally but fail in worktree isolation.

**Solution**:
1. Check for hard-coded absolute paths in tests
2. Verify all test fixtures are self-contained (no external dependencies)
3. Ensure environment variables are properly set in worktree
4. Check if tests depend on git state (clean worktree has no uncommitted changes)
5. Look for tests that write to relative paths assuming specific working directory

### Problem: AI Maestro Notification Not Delivered

**Symptoms**: Tests complete but orchestrator never receives notification.

**Solution**:
1. Use the `agent-messaging` skill to perform a health check on the AI Maestro service
2. Check agent session name is correct in notification
3. Verify network connectivity from test environment to AI Maestro
4. Check notification message format matches schema
5. Look for errors in AI Maestro logs for delivery failures

### Problem: Test Results JSON Malformed

**Symptoms**: `--output` produces invalid JSON that downstream tools reject.

**Solution**:
1. Check for test output containing non-UTF8 characters
2. Verify no test prints raw binary data to stdout
3. Ensure pytest plugins don't corrupt output format
4. Run with `--json` flag to get structured output
5. Validate output manually: `jq . report.json`

### Problem: Evidence Collection Fails

**Symptoms**: `evidence_store.py add` rejects test results.

**Solution**:
1. Verify test results JSON has required fields (passed, failed, total)
2. Check evidence store file permissions
3. Ensure evidence ID is unique (use UUID)
4. Verify evidence type is valid (EVENT, APPROVAL, etc.)
5. Check for JSON encoding issues in test output

### Problem: Quality Pattern Detector False Positives

**Symptoms**: Quality check flags valid tests as anti-patterns.

**Solution**:
1. Review flagged patterns - some may be intentional (e.g., testing error paths)
2. Add exclusion comments: `# quality-ignore: build-only-test`
3. Adjust score threshold if too strict: `--min-score 60`
4. Update detector patterns if false positive is common
5. Document intentional anti-patterns in test docstrings
