---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: verify-task-completion
---

# Operation: Verify Task Completion


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Expected Completion Report Format](#expected-completion-report-format)
- [Steps](#steps)
  - [Step 1: Parse Completion Report](#step-1-parse-completion-report)
  - [Step 2: Check PR Existence](#step-2-check-pr-existence)
  - [Step 3: Check CI Status](#step-3-check-ci-status)
  - [Step 4: Check Test Status from Report](#step-4-check-test-status-from-report)
  - [Step 5: Verify Issue Checklist](#step-5-verify-issue-checklist)
  - [Step 6: Check Required Documentation](#step-6-check-required-documentation)
  - [Step 7: Make Verification Decision](#step-7-make-verification-decision)
- [Verification Checklist](#verification-checklist)
- [Success Criteria](#success-criteria)
- [Failure Handling](#failure-handling)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Verify that an agent's completion report meets all acceptance criteria before closing the task.

## When to Use

- Agent sends a `[DONE]` message
- Agent reports task completion
- Before closing any task issue

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Completing agent | Yes |
| completion_report | Agent's [DONE] message | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| verification_passed | Boolean | All criteria met |
| missing_items | Array | Criteria not satisfied |
| task_closed | Boolean | Issue closed (if passed) |

## Expected Completion Report Format

```
[DONE] <task-id> - <result-summary>
Output: <file-path or PR-number>
Tests: <passed/failed>
```

## Steps

### Step 1: Parse Completion Report

```bash
TASK_ID=$1
AGENT_NAME=$2
COMPLETION_REPORT=$3

# Extract components
RESULT_SUMMARY=$(echo "$COMPLETION_REPORT" | head -1 | sed 's/\[DONE\] [0-9]* - //')
OUTPUT_REF=$(echo "$COMPLETION_REPORT" | grep "Output:" | sed 's/Output: //')
TEST_STATUS=$(echo "$COMPLETION_REPORT" | grep "Tests:" | sed 's/Tests: //')

echo "Result: $RESULT_SUMMARY"
echo "Output: $OUTPUT_REF"
echo "Tests: $TEST_STATUS"
```

### Step 2: Check PR Existence

```bash
# Extract PR number if referenced
PR_NUMBER=$(echo "$OUTPUT_REF" | grep -oP '#\d+' | tr -d '#' | head -1)

if [ -n "$PR_NUMBER" ]; then
  # Verify PR exists
  PR_EXISTS=$(gh pr view $PR_NUMBER --json number 2>/dev/null)

  if [ -z "$PR_EXISTS" ]; then
    echo "FAIL: PR #$PR_NUMBER does not exist"
    MISSING_ITEMS+=("PR #$PR_NUMBER not found")
  else
    echo "PASS: PR #$PR_NUMBER exists"

    # Verify PR is linked to issue
    PR_BODY=$(gh pr view $PR_NUMBER --json body | jq -r '.body')
    if ! echo "$PR_BODY" | grep -q "#$TASK_ID"; then
      echo "WARN: PR does not reference issue #$TASK_ID"
    fi
  fi
else
  echo "WARN: No PR number in completion report"
fi
```

### Step 3: Check CI Status

```bash
if [ -n "$PR_NUMBER" ]; then
  CI_RESULTS=$(gh pr view $PR_NUMBER --json statusCheckRollup | jq -r '.statusCheckRollup[] | "\(.name): \(.conclusion)"')

  ALL_PASSING=true
  while IFS= read -r result; do
    if echo "$result" | grep -qv "SUCCESS\|NEUTRAL"; then
      ALL_PASSING=false
      echo "FAIL: $result"
      MISSING_ITEMS+=("CI check failed: $result")
    fi
  done <<< "$CI_RESULTS"

  if [ "$ALL_PASSING" = true ]; then
    echo "PASS: All CI checks passing"
  fi
fi
```

### Step 4: Check Test Status from Report

```bash
if [ "$TEST_STATUS" = "passed" ]; then
  echo "PASS: Agent reports tests passed"
elif [ "$TEST_STATUS" = "failed" ]; then
  echo "FAIL: Agent reports tests failed"
  MISSING_ITEMS+=("Tests not passing")
else
  echo "WARN: Test status unclear: $TEST_STATUS"
fi
```

### Step 5: Verify Issue Checklist

```bash
# Get checklist items from issue body
ISSUE_BODY=$(gh issue view $TASK_ID --json body | jq -r '.body')

# Count checked vs unchecked items
CHECKED=$(echo "$ISSUE_BODY" | grep -c '\[x\]' || echo 0)
UNCHECKED=$(echo "$ISSUE_BODY" | grep -c '\[ \]' || echo 0)

if [ "$UNCHECKED" -gt 0 ]; then
  echo "FAIL: $UNCHECKED checklist items not complete"
  MISSING_ITEMS+=("$UNCHECKED checklist items incomplete")
else
  echo "PASS: All checklist items complete ($CHECKED items)"
fi
```

### Step 6: Check Required Documentation

```bash
# If task required documentation updates, verify
if echo "$ISSUE_BODY" | grep -qi "documentation\|docs\|readme"; then
  if [ -n "$PR_NUMBER" ]; then
    DOC_FILES=$(gh pr view $PR_NUMBER --json files | jq '[.files[] | select(.path | endswith(".md"))] | length')

    if [ "$DOC_FILES" -eq 0 ]; then
      echo "WARN: Task mentions documentation but no .md files in PR"
      # May or may not be a failure depending on requirements
    else
      echo "PASS: Documentation files updated ($DOC_FILES files)"
    fi
  fi
fi
```

### Step 7: Make Verification Decision

```bash
if [ ${#MISSING_ITEMS[@]} -eq 0 ]; then
  # VERIFICATION PASSED
  echo "VERIFICATION PASSED - All criteria met"

  # Update task status
  gh issue edit $TASK_ID --remove-label "status:in-progress" --add-label "status:done"

  # Remove agent assignment (task complete)
  gh issue edit $TASK_ID --remove-label "assign:$AGENT_NAME"

  # Add completion comment
  gh issue comment $TASK_ID --body "**TASK VERIFIED COMPLETE**

Agent: $AGENT_NAME
Result: $RESULT_SUMMARY
PR: #$PR_NUMBER
Verified at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # Close issue
  gh issue close $TASK_ID

  # Notify agent of success using the agent-messaging skill:
  # - Recipient: $AGENT_NAME
  # - Subject: "Task Approved: #$TASK_ID"
  # - Content: "Congratulations! Task #$TASK_ID has been verified and approved. Your PR is ready for merge."
  # - Type: approval, Priority: normal
  # - Data: task_id, pr_number
else
  # VERIFICATION FAILED
  echo "VERIFICATION FAILED - Missing: ${MISSING_ITEMS[*]}"

  # Send revision request
  MISSING_LIST=$(printf '%s\n' "${MISSING_ITEMS[@]}")

  # Send revision request using the agent-messaging skill:
  # - Recipient: $AGENT_NAME
  # - Subject: "Revision Required: #$TASK_ID"
  # - Content: "Task completion verification failed. Please address the following: $MISSING_LIST. Update your work and report completion again."
  # - Type: revision, Priority: high
  # - Data: task_id, missing_items

  # Add comment to issue
  gh issue comment $TASK_ID --body "**COMPLETION VERIFICATION FAILED**

Missing items:
$(printf '- %s\n' "${MISSING_ITEMS[@]}")

Agent notified to address issues."
fi
```

## Verification Checklist

Copy and use for each completion review:

- [ ] Completion report received and parsed
- [ ] PR exists (if referenced)
- [ ] PR linked to issue
- [ ] All CI checks passing
- [ ] Agent reports tests passed
- [ ] All issue checklist items complete
- [ ] Documentation updated (if required)
- [ ] Code review approved (if required)

## Success Criteria

- [ ] All verification checks passed
- [ ] Task status updated to done
- [ ] Agent assignment removed
- [ ] Issue closed
- [ ] Agent notified

## Failure Handling

If verification fails:
1. Do NOT close the issue
2. Do NOT change status to done
3. Send detailed revision request to agent
4. Add comment listing all missing items
5. Agent must address issues and report completion again

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| PR not found | Wrong number or not created | Ask agent for correct PR |
| CI still running | PR just created | Wait for CI, re-verify |
| Checklist unclear | Malformed markdown | Manually review issue |

## Related Operations

- op-review-completion-report (in remote-agent-coordinator skill)
- op-detect-agent-state
