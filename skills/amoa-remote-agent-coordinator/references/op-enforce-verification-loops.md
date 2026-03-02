---
procedure: proc-execute-task
workflow-instruction: Step 17 - Task Execution
operation: enforce-verification-loops
---

# Operation: Enforce 4-Verification Loops


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [The 5 PR Requests Cycle](#the-5-pr-requests-cycle)
- [Steps](#steps)
  - [Step 1: Track PR Request Count](#step-1-track-pr-request-count)
  - [Step 2: Respond Based on Count](#step-2-respond-based-on-count)
  - [Step 3: Final Approval Decision (5th Request)](#step-3-final-approval-decision-5th-request)
- [Enforcement Rules](#enforcement-rules)
  - [MUST](#must)
  - [MUST NOT](#must-not)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Require agents to perform 4 self-verification cycles before approving PR creation. This ensures code quality through iterative self-review.

## When to Use

- When agent requests permission to create a PR
- After agent reports task completion
- Before any code merge

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| task_id | Issue number | Yes |
| agent_name | Assigned agent | Yes |
| pr_request_count | Internal tracking | Yes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| verification_response | String | "verify" or "approved" |
| current_loop | Integer | Which verification loop (1-4) |
| pr_approved | Boolean | True only after 5th request |

## The 5 PR Requests Cycle

| PR Request # | Orchestrator Response | Agent Action |
|--------------|----------------------|--------------|
| 1st | "Check your changes for errors" | Self-review, fix issues |
| 2nd | "Check your changes for errors" | Self-review, fix issues |
| 3rd | "Check your changes for errors" | Self-review, fix issues |
| 4th | "Check your changes for errors" | Self-review, fix issues |
| 5th | "Approved" or "Rejected with reasons" | Create PR or fix issues |

## Steps

### Step 1: Track PR Request Count

```bash
# Get current verification count for this task
VERIFICATION_FILE="verification_state_${TASK_ID}.json"

if [ -f "$VERIFICATION_FILE" ]; then
  PR_REQUEST_COUNT=$(jq -r '.pr_request_count' "$VERIFICATION_FILE")
else
  PR_REQUEST_COUNT=0
fi

PR_REQUEST_COUNT=$((PR_REQUEST_COUNT + 1))

# Save updated count
echo '{"task_id": "'"$TASK_ID"'", "agent": "'"$AGENT_NAME"'", "pr_request_count": '$PR_REQUEST_COUNT'}' > "$VERIFICATION_FILE"
```

### Step 2: Respond Based on Count

If the PR request count is less than 5 (verification loop not yet complete):

Send a verification request message using the `agent-messaging` skill:
- **Recipient**: the agent requesting PR (by session name)
- **Subject**: "Verification Required: #[TASK_ID] ([COUNT]/4)"
- **Content**: "Check your changes for errors. This is verification request [COUNT] of 4 required before PR approval."
- **Type**: `verification`
- **Priority**: `normal`
- **Data**: include `task_id`, `verification_loop` (current count), `remaining_loops`

**Verify**: confirm message delivery.

If the PR request count reaches 5, proceed to final approval decision.

### Step 3: Final Approval Decision (5th Request)

Review the agent's final submission against acceptance criteria.

**If criteria are met**, send an approval message using the `agent-messaging` skill:
- **Recipient**: the agent
- **Subject**: "PR Approved: #[TASK_ID]"
- **Content**: "You may now create a PR for task #[TASK_ID]. Ensure all tests pass before submission."
- **Type**: `approval`
- **Priority**: `normal`
- **Data**: include `task_id`, `pr_approved` (true)

**If criteria are NOT met**, send a rejection message using the `agent-messaging` skill:
- **Recipient**: the agent
- **Subject**: "PR Rejected: #[TASK_ID]"
- **Content**: "PR creation not approved. Issues found: [list]. Address these issues and request PR permission again."
- **Type**: `rejection`
- **Priority**: `high`
- **Data**: include `task_id`, `pr_approved` (false), `issues` (array)

**Verify**: confirm message delivery in both cases.

```bash
# NOTE: The logic below handles tracking the verification state
CRITERIA_MET=true  # Determine from review
# Then send the appropriate approval or rejection message
# using the agent-messaging skill as described above
    }'

  # Reset verification count for another 4 loops
  echo '{"task_id": "'"$TASK_ID"'", "agent": "'"$AGENT_NAME"'", "pr_request_count": 0}' > "$VERIFICATION_FILE"
fi
```

## Enforcement Rules

### MUST

- Respond to first 4 PR requests with "Check your changes for errors"
- Track verification count per task (not globally)
- Make actual approval decision only on 5th request
- Reset count if PR is rejected

### MUST NOT

- Skip verification loops
- Approve before 5th request
- Allow agent to bypass with urgency claims
- Count verification loops across different tasks

## Success Criteria

- [ ] Verification count tracked per task
- [ ] First 4 requests receive "verify" response
- [ ] 5th request triggers actual review
- [ ] Approval/rejection based on acceptance criteria
- [ ] Count reset if rejected

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Count lost | State file deleted | Reset to 0, inform agent |
| Agent skips loops | Agent creates PR directly | Reject PR, require loops |
| Wrong task counted | Task ID mismatch | Verify task ID in messages |

## Related Operations

- op-review-completion-report
- op-prepare-task-delegation
