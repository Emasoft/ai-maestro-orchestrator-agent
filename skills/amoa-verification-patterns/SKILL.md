---
name: eoa-verification-patterns
description: "Use when verifying implementations. Trigger with verification, testing, or evidence requests."
license: Apache-2.0
compatibility: "Requires Python 3.8+, Bash shell, Git. Supports Windows, macOS, and Linux. Optional dependencies: Selenium for E2E browser testing, Docker for service orchestration, SQLite/PostgreSQL for database examples. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: "1.0.0"
agent: eoa-main
context: fork
user-invocable: false
workflow-instruction: "Step 19"
procedure: "proc-complete-task"
---

# Verification Patterns for EOA (Emasoft Orchestrator Agent)

## Overview

This skill teaches evidence-based verification techniques for proving that code, systems, and operations work correctly.

## Prerequisites

- Python 3.8+ with Bash shell
- Git for version control
- Optional: Selenium for E2E browser testing
- Optional: Docker for service orchestration
- Optional: SQLite/PostgreSQL for database examples

## Instructions

This skill teaches evidence-based verification techniques for proving that code, systems, and operations work correctly. Verification is not about hope or assumptions - it is about collecting measurable, reproducible evidence that a system behaves as intended.

The four core verification patterns are:
1. **Evidence-based verification**: Collecting measurable proof that code works
2. **Exit code proof**: Using process exit codes as signals of success or failure
3. **End-to-end (E2E) testing**: Testing complete workflows from input to output
4. **Integration verification**: Testing how components work together

---

## Table of Contents

### When you need to understand verification fundamentals
See [Verification Principles](#verification-principles) below.

### When you need to collect measurable proof that code works
See [Evidence-Based Verification](./references/evidence-based-verification.md):
- 1.1 What is Evidence
  - 1.1.1 Types of measurable evidence
  - 1.1.2 Return values, output files, console output
  - 1.1.3 State changes and side effects
  - 1.1.4 Performance metrics and error signals
- 1.2 Evidence-Based Verification Steps
  - 1.2.1 Step 1: Define the Expected Outcome
  - 1.2.2 Step 2: Run the Code
  - 1.2.3 Step 3: Collect Evidence
  - 1.2.4 Step 4: Compare Evidence to Expectation
  - 1.2.5 Step 5: Document Results
- 1.3 Evidence-Based Verification Example
- 1.4 When to Use Evidence-Based Verification

### When you need to use process exit codes to signal success/failure
See [Exit Code Proof](./references/exit-code-proof.md):
- 2.1 What is an Exit Code
  - 2.1.1 Definition and conventions
  - 2.1.2 Exit code 0 means success, 1-255 means failure
- 2.2 Why Exit Codes Matter
- 2.3 Exit Code Proof Steps
  - 2.3.1 Step 1: Run the Process
  - 2.3.2 Step 2: Check the Exit Code
  - 2.3.3 Step 3: Interpret the Result
  - 2.3.4 Step 4: Act on the Result
- 2.4 Exit Code Proof Examples (Bash, Python)
- 2.5 Setting Exit Codes in Your Code
- 2.6 When to Use Exit Code Proof

### When you need to test complete workflows from start to finish
See [End-to-End Testing](./references/end-to-end-testing.md):
- 3.1 What is E2E Testing
  - 3.1.1 Complete user workflow verification
  - 3.1.2 Testing from input to output through all components
- 3.2 Why E2E Testing Matters
- 3.3 E2E Testing Steps
  - 3.3.1 Step 1: Define a Complete User Workflow
  - 3.3.2 Step 2: Prepare Test Environment
  - 3.3.3 Step 3: Execute the Workflow
  - 3.3.4 Step 4: Verify Final Outcome
  - 3.3.5 Step 5: Clean Up
- 3.4 E2E Testing Examples (Web app with Selenium, Data pipeline)
- 3.5 When to Use E2E Testing

### When you need to test how components work together
See [Integration Verification](./references/integration-verification.md):
- 4.1 What is Integration Verification
  - 4.1.1 Testing multiple components together
  - 4.1.2 Difference from unit testing and E2E testing
- 4.2 Why Integration Verification Matters
- 4.3 Integration Verification Steps
  - 4.3.1 Step 1: Identify Components to Test
  - 4.3.2 Step 2: Prepare Test Environment
  - 4.3.3 Step 3: Define Integration Points
  - 4.3.4 Step 4: Execute Component Interactions
  - 4.3.5 Step 5: Verify Results
  - 4.3.6 Step 6: Clean Up
- 4.4 Integration Verification Examples (API + Database, Microservices)
- 4.5 When to Use Integration Verification

### When you need to build comprehensive verification strategies
See [Combining Verification Patterns](./references/combining-patterns.md):
- 5.1 Pattern Combinations
- 5.2 Verification Pyramid (layer structure and dependencies)
- 5.3 Complete Verification Strategy Example

### When you need to make verification work on Windows, macOS, and Linux
See [Cross-Platform Support](./references/cross-platform-support.md):
- 6.1 Platform-Specific Behavior
- 6.2 UTF-8 Encoding
- 6.3 Platform Detection
- 6.4 Path Handling with pathlib
- 6.5 Command Execution with run_command()

### When you need to format evidence for orchestrator handoff
See [Evidence Format Enforcement](./references/evidence-format.md):
- 7.1 Evidence Format Script (location, dataclasses)
- 7.2 Evidence Types (EXIT_CODE, FILE_CONTENT, TEST_RESULT, etc.)
- 7.3 Verification Statuses (PASSED, FAILED, SKIPPED, ERROR)
- 7.4 Required Evidence Fields
- 7.5 Required Verification Record Fields
- 7.6 Validation Requirements (minimum evidence items)
- 7.7 Validating Evidence Before Submission
- 7.8 Creating Properly-Formatted Evidence (helper functions)
- 7.9 Integration with Handoff Protocols
- 7.10 Command-Line Usage

### When you need to execute tests with proper protocols
See [Testing Protocol](./references/testing-protocol.md):
- 8.1 Script Validation
- 8.2 Pytest Integration (result collection, JSON output)
- 8.3 Worktree Isolation Testing
- 8.4 AI Maestro Notification
- 8.5 Combined Workflow Example
- 8.6 Testing Protocol Scripts (command reference, exit codes)
- 8.7 Integration with Verification Scripts

### When you need to update GitHub issues with verification results
See [Integration with GitHub Projects](./references/github-integration.md):
- 9.1 Verification Results and Issue Status (automatic transitions)
- 9.2 Verification Evidence in Issue Comments (structured format)
- 9.3 Automation Script Integration (gh CLI commands)
- 9.4 Cross-Reference to Related Skills

### When you need to solve common verification problems
See [Troubleshooting](./references/troubleshooting.md):
- 10.1 Tests Pass Locally but Fail in CI/CD
- 10.2 Exit Code is 0 but Process Failed
- 10.3 Integration Test Fails with Timeout
- 10.4 E2E Test is Flaky (passes sometimes, fails sometimes)
- 10.5 Verification Requires Access to Internal State

### When you need to troubleshoot Docker-based verification environments
See [Docker Troubleshooting](./references/docker-troubleshooting.md):
- Docker service not starting
- Container networking issues
- Volume mount problems
- Image build failures
- Resource constraints and performance issues

### When you need to automate verification tasks
See [Automation Scripts](./references/automation-scripts.md):
- 11.1 Traceability and Requirements Scripts (traceability_validator.py)
- 11.2 Evidence Collection Scripts (evidence_store.py)
- 11.3 Consistency and Verification Scripts (consistency_verifier.py, with_server.py)
- 11.4 Code Quality Scripts (quality_pattern_detector.py)
- 11.5 Scoring and Analysis Scripts (scoring_framework.py, comparison_analyzer.py)
- 11.6 Testing and Validation Scripts (ab_test_calculator.py, checklist_validator.py)

### When you need standard test report formats
See [Test Report Format](./references/test-report-format.md):
- Standard Report Structure
- Minimal Report (For Orchestrator)
- Language-Specific Converters (Python/pytest, JavaScript/Jest, Go, Rust)
- Report Locations
- Failure Detail Levels
- Orchestrator Response to Test Reports
- Error States
- Completion Tracking (attempt tracking, escalation flows, hang prevention)
- Integration

## Examples

### Example 1: Evidence-Based Verification

```python
def test_user_creation():
    # Step 1: Define expected outcome
    expected_email = "test@example.com"

    # Step 2: Run the code
    user = create_user(email=expected_email)

    # Step 3: Collect evidence
    actual_email = user.email
    db_record = db.query(User).filter_by(id=user.id).first()

    # Step 4: Compare evidence to expectation
    assert actual_email == expected_email
    assert db_record is not None
    assert db_record.email == expected_email

    # Step 5: Document results (test framework handles this)
```

### Example 2: Exit Code Proof

```bash
# Run tests and capture exit code
pytest tests/ --cov=src
exit_code=$?

# Interpret result
if [ $exit_code -eq 0 ]; then
    echo "SUCCESS: All tests passed"
else
    echo "FAILURE: Tests failed with exit code $exit_code"
    exit 1
fi
```

---

## Output

When verification tasks complete, provide results in this format:

| Field | Description | Example |
|-------|-------------|---------|
| **Status** | PASSED, FAILED, or ERROR | `PASSED` |
| **Evidence Type** | Type of verification performed | `EXIT_CODE`, `FILE_CONTENT`, `TEST_RESULT` |
| **Evidence** | Measurable proof collected | `Exit code: 0`, `All 42 tests passed` |
| **Timestamp** | When verification was performed | `2024-01-15T10:30:00Z` |
| **Details** | Additional context or failure reasons | `See test_results.json for details` |

---

## Error Handling

See [Troubleshooting](./references/troubleshooting.md) for complete solutions.

| Issue | Cause | Resolution |
|-------|-------|------------|
| Tests pass locally, fail in CI | Environment differences | Check env vars, dependencies |
| Exit code 0 but process failed | Missing exit code in script | Add explicit `sys.exit(1)` on failure |
| Integration test timeout | Slow service startup | Increase timeout, add health checks |
| Flaky E2E test | Race conditions | Add explicit waits, retry logic |

---

## Verification Principles

Before learning specific verification patterns, understand these principles:

### Principle 1: Never Trust Assumptions
Do not assume code works. Do not say "this should work" or "probably works." Verify every claim with evidence.

### Principle 2: Measure What Matters
Collect evidence that answers the question: "Does the system do what it is supposed to do?" Track:
- Return values
- Output data
- Side effects (files created, state changes)
- Performance metrics
- Error conditions

### Principle 3: Reproducibility
Evidence is only valid if it can be reproduced. If you verify something once, you should be able to verify it again with the same result.

### Principle 4: Fail Fast
If something fails during verification, stop immediately and report the failure. Do not continue as if it succeeded.

### Principle 5: Document Evidence
Record what you verified, when you verified it, and what the results were. This documentation becomes your proof.

---

## Quick Reference: Verification Pattern Selection

| Situation | Pattern | Reference |
|-----------|---------|-----------|
| Prove a function returns correct value | Evidence-based verification | [evidence-based-verification.md](./references/evidence-based-verification.md) |
| Check if a script succeeded | Exit code proof | [exit-code-proof.md](./references/exit-code-proof.md) |
| Verify user workflow works | E2E testing | [end-to-end-testing.md](./references/end-to-end-testing.md) |
| Test API calls database correctly | Integration verification | [integration-verification.md](./references/integration-verification.md) |
| Build CI/CD pipeline | Exit code proof + E2E | [combining-patterns.md](./references/combining-patterns.md) |
| Cross-platform script | Platform-aware commands | [cross-platform-support.md](./references/cross-platform-support.md) |
| Report to orchestrator | Evidence format | [evidence-format.md](./references/evidence-format.md) |
| Run tests in isolation | Worktree testing | [testing-protocol.md](./references/testing-protocol.md) |
| Update GitHub issues | gh CLI integration | [github-integration.md](./references/github-integration.md) |
| Debug flaky tests | Troubleshooting guide | [troubleshooting.md](./references/troubleshooting.md) |
| Automate quality checks | Automation scripts | [automation-scripts.md](./references/automation-scripts.md) |

---

## Quick Reference: Scripts Location

All verification scripts are in `scripts/`:

| Script | Purpose |
|--------|---------|
| `evidence_format.py` | Evidence format validation and creation |
| `evidence_store.py` | Evidence collection with deduplication |
| `consistency_verifier.py` | File, git, URL, JSON verification |
| `with_server.py` | Server orchestration for integration tests |
| `quality_pattern_detector.py` | Anti-pattern detection |
| `scoring_framework.py` | Weighted multi-dimension scoring |
| `comparison_analyzer.py` | Gap analysis with baselines |
| `ab_test_calculator.py` | Statistical hypothesis testing |
| `checklist_validator.py` | Dependency-aware checklist validation |
| `traceability_validator.py` | Requirements coverage validation |

---

## Quick Reference: Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | Success | Continue workflow |
| `1` | General failure | Stop and report |
| `2` | Script validation failed | Fix script issues |

---

## Summary

Verification is not optional. Every claim that code works must be backed by evidence. Use:

- **Evidence-based verification** to collect measurable proof
- **Exit code proof** to signal success or failure
- **E2E testing** to verify complete workflows
- **Integration verification** to verify components work together

Combine these patterns to build confidence that your systems work correctly before deploying to production.

For detailed implementation of each pattern, see the reference files linked in the Table of Contents above.

---

## Resources

- [evidence-based-verification.md](./references/evidence-based-verification.md) - Collecting measurable proof
- [exit-code-proof.md](./references/exit-code-proof.md) - Using process exit codes
- [end-to-end-testing.md](./references/end-to-end-testing.md) - Complete workflow testing
- [integration-verification.md](./references/integration-verification.md) - Component interaction testing
- [combining-patterns.md](./references/combining-patterns.md) - Comprehensive strategies
- [cross-platform-support.md](./references/cross-platform-support.md) - Platform compatibility
- [evidence-format.md](./references/evidence-format.md) - Evidence formatting for handoff
- [testing-protocol.md](./references/testing-protocol.md) - Test execution protocols
- [github-integration.md](./references/github-integration.md) - GitHub issue updates
- [troubleshooting.md](./references/troubleshooting.md) - Common issues
- [docker-troubleshooting.md](./references/docker-troubleshooting.md) - Docker troubleshooting
- [automation-scripts.md](./references/automation-scripts.md) - Script reference
- [test-report-format.md](./references/test-report-format.md) - Report standards

---

## Checklist

Copy this checklist and track your progress:

- [ ] Understand verification principles (never trust assumptions, measure what matters)
- [ ] Define expected outcome for the verification task
- [ ] Select appropriate verification pattern (evidence-based, exit code, E2E, or integration)
- [ ] Prepare test environment (dependencies, services, test data)
- [ ] Execute verification steps according to selected pattern
- [ ] Collect measurable evidence (return values, output files, exit codes, state changes)
- [ ] Compare evidence to expected outcome
- [ ] Document verification results in standard format
- [ ] Handle failures with fail-fast approach (stop and report immediately)
- [ ] Ensure reproducibility of verification (can be repeated with same results)
- [ ] Report results to orchestrator with proper evidence format
- [ ] Update GitHub issues if applicable (status transitions, evidence comments)
- [ ] Clean up test environment and temporary resources
