---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: review-completion-report
---

# Operation: Review Completion Report


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Steps](#steps)
  - [Step 1: Retrieve Acceptance Criteria](#step-1-retrieve-acceptance-criteria)
  - [Step 2: Check PR Existence](#step-2-check-pr-existence)
  - [Step 3: Check CI Status](#step-3-check-ci-status)
  - [Step 4: Verify Each Criterion](#step-4-verify-each-criterion)
  - [Step 5: Make Verification Decision](#step-5-make-verification-decision)
- [Verification Checklist](#verification-checklist)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Review agent's completion report against the original acceptance criteria and verify all requirements are met.

## When to Use

- When agent reports task as complete
- After PR is created and ready for review
- Before closing a task issue

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| completion_report | Agent's [DONE] message | Yes |
| acceptance_criteria | Original task delegation | Yes |
| pr_number | Created PR | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| verification_passed | Boolean | All criteria met |
| missing_criteria | Array | Criteria not satisfied |
| review_comments | String | Feedback for agent |

## Steps

### Step 1: Retrieve Acceptance Criteria

```bash
# Get original acceptance criteria from issue
CRITERIA=$(gh issue view $TASK_ID --json body | jq -r '.body' | grep -A20 "## Completion Criteria")

# Parse into checklist
echo "$CRITERIA"
```

### Step 2: Check PR Existence

```bash
# Verify PR exists and is linked
PR_EXISTS=$(gh pr view $PR_NUMBER --json number 2>/dev/null)

if [ -z "$PR_EXISTS" ]; then
  echo "VERIFICATION FAILED: PR #$PR_NUMBER does not exist"
  exit 1
fi

# Check PR is linked to issue
PR_LINKED=$(gh pr view $PR_NUMBER --json body | jq -r '.body' | grep -c "#$TASK_ID")

if [ "$PR_LINKED" -eq 0 ]; then
  echo "WARNING: PR does not reference issue #$TASK_ID"
fi
```

### Step 3: Check CI Status

```bash
# Get CI/test status
CI_STATUS=$(gh pr view $PR_NUMBER --json statusCheckRollup | jq -r '.statusCheckRollup[] | .conclusion')

ALL_PASSING=true
for status in $CI_STATUS; do
  if [ "$status" != "SUCCESS" ] && [ "$status" != "NEUTRAL" ]; then
    ALL_PASSING=false
    echo "CI check failed: $status"
  fi
done

if [ "$ALL_PASSING" = true ]; then
  echo "All CI checks passing"
else
  echo "VERIFICATION FAILED: CI checks not passing"
fi
```

### Step 4: Verify Each Criterion

```bash
# For each acceptance criterion, verify it's met
MISSING_CRITERIA=()

# Example checks:
# - [ ] Tests added for new functionality
TEST_COUNT=$(gh pr view $PR_NUMBER --json files | jq '[.files[] | select(.path | contains("test"))] | length')
if [ "$TEST_COUNT" -eq 0 ]; then
  MISSING_CRITERIA+=("No tests added")
fi

# - [ ] Documentation updated
DOC_UPDATED=$(gh pr view $PR_NUMBER --json files | jq '[.files[] | select(.path | endswith(".md"))] | length')
# Check if documentation was required

# Report missing criteria
if [ ${#MISSING_CRITERIA[@]} -gt 0 ]; then
  echo "Missing criteria:"
  printf '%s\n' "${MISSING_CRITERIA[@]}"
fi
```

### Step 5: Make Verification Decision

```bash
if [ "$ALL_PASSING" = true ] && [ ${#MISSING_CRITERIA[@]} -eq 0 ]; then
  # Verification passed
  echo "VERIFICATION PASSED"

  # Update issue status
  gh issue edit $TASK_ID --remove-label "status:in-progress" --add-label "status:done"

  # Add completion comment
  gh issue comment $TASK_ID --body "Task completed successfully. PR #$PR_NUMBER approved."

  # Send approval to agent using the agent-messaging skill:
  # Recipient: the agent session name
  # Subject: "Task Approved: #[TASK_ID]"
  # Content: "Task #[TASK_ID] has been verified and approved. PR #[PR_NUMBER] ready for merge."
  # Type: approval, Priority: normal
  # Data: task_id, pr_number
else
  # Verification failed
  echo "VERIFICATION FAILED"

  # Send revision request
  MISSING_JSON=$(printf '%s\n' "${MISSING_CRITERIA[@]}" | jq -R . | jq -s .)

  # Send revision request using the agent-messaging skill:
  # Recipient: the agent session name
  # Subject: "Revision Required: #[TASK_ID]"
  # Content: "Completion verification failed. Please address the following: [missing criteria]. Update PR and report completion again."
  # Type: revision, Priority: high
  # Data: task_id, missing_criteria (array)
  #
  # Verify: confirm message delivery
      }
    }'
fi
```

## Verification Checklist

Copy and use for each completion review:

- [ ] PR exists and is linked to issue
- [ ] All CI checks passing
- [ ] Tests added (if required)
- [ ] Documentation updated (if required)
- [ ] Code review approved (if required)
- [ ] All acceptance criteria in issue checklist met
- [ ] No new blockers introduced
- [ ] No scope creep beyond original task

## Success Criteria

- [ ] All acceptance criteria verified
- [ ] CI status checked
- [ ] PR properly linked
- [ ] Agent notified of result

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| PR not found | Wrong PR number | Ask agent for correct PR |
| CI failing | Code issues | Agent must fix before approval |
| Criteria missing | Incomplete work | Send detailed revision request |

## Related Operations

- op-enforce-verification-loops
- op-verify-task-completion (in progress-monitoring skill)
