# Operation: Update GitHub Issue


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Verification Result to Issue Status](#verification-result-to-issue-status)
- [Steps](#steps)
  - [Step 1: Determine Issue Update Action](#step-1-determine-issue-update-action)
  - [Step 2: Post Verification Comment](#step-2-post-verification-comment)
  - [Step 3: Update Issue Labels](#step-3-update-issue-labels)
  - [Step 4: Post Failure Details (if failed)](#step-4-post-failure-details-if-failed)
  - [Required Actions](#required-actions)
  - [Next Steps](#next-steps)
  - [Step 5: Close Issue (if complete)](#step-5-close-issue-if-complete)
- [Verification Report Format](#verification-report-format)
- [Verification Report](#verification-report)
- [Complete Workflow Example](#complete-workflow-example)
  - [Required Actions](#required-actions)
- [Label Reference](#label-reference)
- [Status Transitions](#status-transitions)
- [Exit Criteria](#exit-criteria)
- [Related Operations](#related-operations)

---
procedure: proc-complete-task
workflow-instruction: Step 19 - Task Completion
operation-id: op-update-github-issue
---

## Purpose

Update GitHub issues with verification results to maintain issue tracking accuracy after task completion.

## When to Use

- After verification completes (pass or fail)
- When task status changes based on verification
- When posting verification evidence to issue
- When closing issues after successful verification

## Prerequisites

- GitHub CLI (`gh`) is authenticated
- Issue number is known
- Verification results are ready
- Repository access permissions

## Verification Result to Issue Status

| Verification Result | GitHub Action |
|---------------------|---------------|
| All tests pass (exit 0) | Move to "AI Review" if PR exists |
| Evidence collected | Add comment with evidence summary |
| Verification failed | Move to "Blocked", add failure label |
| Retry succeeded | Remove failure label, resume workflow |

## Steps

### Step 1: Determine Issue Update Action

Based on verification result:

```bash
if [ $exit_code -eq 0 ]; then
    action="pass"
else
    action="fail"
fi
```

### Step 2: Post Verification Comment

Add structured comment to issue:

```bash
ISSUE_NUMBER=42
VERIFICATION_TYPE="exit-code"
RESULT="PASSED"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EVIDENCE="All 42 tests passed in 12.5s"
SCRIPT="testing_protocol.py"

gh issue comment $ISSUE_NUMBER --body "## Verification Report
- **Type**: $VERIFICATION_TYPE
- **Result**: $RESULT
- **Timestamp**: $TIMESTAMP
- **Evidence**: $EVIDENCE
- **Script**: $SCRIPT"
```

### Step 3: Update Issue Labels

**On verification pass:**
```bash
gh issue edit $ISSUE_NUMBER --add-label "verified"
```

**On verification fail:**
```bash
gh issue edit $ISSUE_NUMBER --add-label "verification-failed"
```

**On retry success:**
```bash
gh issue edit $ISSUE_NUMBER --remove-label "verification-failed"
gh issue edit $ISSUE_NUMBER --add-label "verified"
```

### Step 4: Post Failure Details (if failed)

```bash
FAILURE_REASON="2 tests failed: test_auth.py:45, test_api.py:89"

gh issue comment $ISSUE_NUMBER --body "## Verification Failed

**Reason**: $FAILURE_REASON

### Required Actions
1. Fix test_auth.py:45 - assertion failed
2. Fix test_api.py:89 - timeout exceeded

### Next Steps
Fix the failing tests and re-run verification."
```

### Step 5: Close Issue (if complete)

After all verification passes and PR merged:

```bash
gh issue close $ISSUE_NUMBER --comment "Issue resolved. All verification passed. Merged in PR #123."
```

## Verification Report Format

Standard comment format for issues:

```markdown
## Verification Report
- **Type**: {exit-code/evidence-based/integration/e2e}
- **Result**: PASSED/FAILED
- **Timestamp**: {ISO-8601}
- **Evidence**: {summary}
- **Script**: {script-name}
```

## Complete Workflow Example

```bash
#!/bin/bash
ISSUE_NUMBER=$1
TASK_ID="GH-$ISSUE_NUMBER"

# Run verification
python shared/testing_protocol.py --pytest tests/ --output report.json
exit_code=$?

# Get timestamp
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Parse results
total=$(jq '.summary.total' report.json)
passed=$(jq '.summary.passed' report.json)
failed=$(jq '.summary.failed' report.json)

if [ $exit_code -eq 0 ]; then
    # Success
    result="PASSED"
    gh issue edit $ISSUE_NUMBER --add-label "verified"
    gh issue comment $ISSUE_NUMBER --body "## Verification Report
- **Type**: exit-code
- **Result**: $result
- **Timestamp**: $timestamp
- **Evidence**: $passed/$total tests passed
- **Script**: testing_protocol.py"
else
    # Failure
    result="FAILED"
    failures=$(jq -r '.failures[].test' report.json | head -5 | tr '\n' ', ')
    gh issue edit $ISSUE_NUMBER --add-label "verification-failed"
    gh issue comment $ISSUE_NUMBER --body "## Verification Report
- **Type**: exit-code
- **Result**: $result
- **Timestamp**: $timestamp
- **Evidence**: $passed/$total tests passed, $failed failed
- **Failures**: $failures
- **Script**: testing_protocol.py

### Required Actions
Fix failing tests and re-run verification."
fi
```

## Label Reference

| Label | Meaning |
|-------|---------|
| `verified` | Verification passed |
| `verification-failed` | Verification failed |
| `blocked` | Issue blocked by verification failure |
| `ai-review` | Verification passed, awaiting review |

## Status Transitions

```
[In Progress] -> Verification Pass -> [AI Review]
[In Progress] -> Verification Fail -> [Blocked]
[Blocked] -> Retry Success -> [In Progress] or [AI Review]
[AI Review] -> PR Merged -> [Done]
```

## Exit Criteria

This operation is complete when:
- [ ] Verification result determined
- [ ] Structured comment posted to issue
- [ ] Appropriate labels added/removed
- [ ] Failure details posted (if applicable)
- [ ] Issue status reflects verification outcome

## Related Operations

- [op-verify-exit-code.md](./op-verify-exit-code.md) - Getting verification result
- [op-format-verification-report.md](./op-format-verification-report.md) - Report content
- [op-notify-orchestrator.md](./op-notify-orchestrator.md) - Notifying orchestrator
- [op-generate-test-report.md](./op-generate-test-report.md) - Test report details
