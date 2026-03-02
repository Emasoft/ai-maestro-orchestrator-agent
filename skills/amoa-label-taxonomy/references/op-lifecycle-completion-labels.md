---
procedure: support-skill
workflow-instruction: support
---

# Operation: Set Labels on Task Completion


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify Task Completion](#step-1-verify-task-completion)
  - [Step 2: Determine Completion Path](#step-2-determine-completion-path)
  - [Step 3: Handle PR Review Status (if applicable)](#step-3-handle-pr-review-status-if-applicable)
  - [Step 4: Move to AI Review](#step-4-move-to-ai-review)
  - [Step 5: Move to Human Review (BIG tasks only)](#step-5-move-to-human-review-big-tasks-only)
  - [Step 6: Move to Merge-Release](#step-6-move-to-merge-release)
  - [Step 7: Apply Completion Labels](#step-7-apply-completion-labels)
  - [Step 8: Close Issue (if policy allows)](#step-8-close-issue-if-policy-allows)
  - [Step 9: Notify Orchestrator](#step-9-notify-orchestrator)
- [Output](#output)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Example 1: Simple Completion](#example-1-simple-completion)
  - [Example 2: Completion After PR Merge](#example-2-completion-after-pr-merge)
  - [Example 3: Partial Completion with Handoff](#example-3-partial-completion-with-handoff)
  - [Example 4: Completion with Blockers Found](#example-4-completion-with-blockers-found)
- [Checklist](#checklist)

## When to Use

Use this operation when an agent completes their assigned work and the task is done.

## Prerequisites

- Issue is in `status:in-progress` with `assign:<agent>` label
- Agent has completed the work
- Work has been verified/reviewed
- GitHub CLI (`gh`) authenticated

## Procedure

### Step 1: Verify Task Completion

Before marking complete, confirm:

```bash
# Check current labels
gh issue view <ISSUE_NUM> --json labels --jq '.labels[].name'

# Should have:
# - status:in-progress
# - assign:<agent-id>
```

Completion criteria:
- All acceptance criteria met
- Tests passing
- Code reviewed (if required)
- Documentation updated (if required)

### Step 2: Determine Completion Path

| Scenario | Action |
|----------|--------|
| Work complete, no PR | Go to Step 3 |
| Work complete, PR open | Add `review:*` label first |
| Work complete, PR merged | Go to Step 3 |
| Work incomplete, reassigning | Use op-lifecycle-assignment-labels |

### Step 3: Handle PR Review Status (if applicable)

```bash
# PR submitted, needs review
gh issue edit <ISSUE_NUM> --add-label "review:requested"

# PR approved
gh issue edit <ISSUE_NUM> \
  --remove-label "review:requested" \
  --add-label "review:approved"

# PR merged - continue to completion
```

### Step 4: Move to AI Review

Once work is complete, the Integrator (EIA) reviews the deliverables.

```bash
# Move from in-progress to ai-review
gh issue edit <ISSUE_NUM> \
  --remove-label "status:in-progress" \
  --add-label "status:ai-review"
```

The Integrator will review the code, run quality gates, and either approve or request changes.

### Step 5: Move to Human Review (BIG tasks only)

For BIG tasks (tasks labeled `size:big` or `size:epic`), the user reviews the work via EAMA (Assistant Manager) before it can proceed.

```bash
# After AI review passes, move to human-review (BIG tasks only)
gh issue edit <ISSUE_NUM> \
  --remove-label "status:ai-review" \
  --add-label "status:human-review"
```

> **Note:** Small tasks skip `status:human-review` and go directly from `status:ai-review` to `status:merge-release`.

### Step 6: Move to Merge-Release

After all reviews pass, the task is ready to merge.

```bash
# After review(s) approved, move to merge-release
gh issue edit <ISSUE_NUM> \
  --remove-label "status:ai-review,status:human-review,review:approved" \
  --add-label "status:merge-release"
```

For small tasks skipping human review:

```bash
# Small tasks: directly from ai-review to merge-release
gh issue edit <ISSUE_NUM> \
  --remove-label "status:ai-review,review:approved" \
  --add-label "status:merge-release"
```

### Step 7: Apply Completion Labels

```bash
# After merge is complete, mark as done
gh issue edit <ISSUE_NUM> \
  --remove-label "assign:<agent-id>,status:merge-release" \
  --add-label "status:done"
```

### Step 8: Close Issue (if policy allows)

```bash
# Close with completion comment
gh issue close <ISSUE_NUM> --comment "Task completed by <agent-id>. All acceptance criteria verified."

# Or leave open if requires additional verification
gh issue comment <ISSUE_NUM> --body "**Task Completed**
- Agent: <agent-id>
- Completion time: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Status: done (issue remains open for final verification)"
```

### Step 9: Notify Orchestrator

Send a completion notification using the `agent-messaging` skill:
- **Recipient**: `orchestrator-master`
- **Subject**: "Task Complete: Issue #<ISSUE_NUM>"
- **Content**: "Issue #<ISSUE_NUM> completed by <agent-id>"
- **Type**: `task_complete`, **Priority**: `normal`

**Verify**: confirm message delivery.

## Output

| Field | Type | Description |
|-------|------|-------------|
| Assignment Removed | Boolean | `assign:*` label removed |
| Status Change | String | `status:in-progress` -> `status:ai-review` -> [`status:human-review` (BIG only)] -> `status:merge-release` -> `status:done` |
| Issue State | String | Open or Closed |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No assignment label | Already removed or never set | Just update status |
| Multiple status labels | Previous error | Remove all, add `status:done` |
| PR not merged | Review incomplete | Keep `status:in-progress`, add `review:*` |

## Examples

### Example 1: Simple Completion

```bash
# Task done, no PR involved
gh issue edit 42 \
  --remove-label "assign:implementer-1,status:in-progress" \
  --add-label "status:done"

gh issue close 42 --comment "Completed by implementer-1"
```

### Example 2: Completion After PR Merge

```bash
# PR was merged, now complete the issue
gh issue edit 42 \
  --remove-label "assign:implementer-1,status:in-progress,review:approved" \
  --add-label "status:done"

gh issue close 42 --comment "PR #99 merged. Task completed."
```

### Example 3: Partial Completion with Handoff

```bash
# Agent completed part, handing off
gh issue edit 42 \
  --remove-label "assign:implementer-1"

gh issue comment 42 --body "**Partial Completion Handoff**
- Completed: API endpoints implemented
- Remaining: Unit tests needed
- Handing off to new assignee"

# Then assign to new agent
gh issue edit 42 --add-label "assign:implementer-2"
```

### Example 4: Completion with Blockers Found

```bash
# Work reveals blocking issue
gh issue edit 42 \
  --remove-label "assign:implementer-1,status:in-progress" \
  --add-label "status:blocked"

gh issue comment 42 --body "**Blocked**
- Completed: Initial implementation
- Blocker: Requires API update (see issue #45)
- Will resume after #45 resolved"
```

## Checklist

- [ ] Verify all acceptance criteria met
- [ ] Verify tests passing
- [ ] Verify code reviewed (if required)
- [ ] Handle PR review labels if applicable
- [ ] Move to `status:ai-review` (Integrator reviews)
- [ ] Move to `status:human-review` (BIG tasks only, user reviews via EAMA)
- [ ] Move to `status:merge-release` (ready to merge)
- [ ] Remove `assign:<agent>` label
- [ ] Add `status:done`
- [ ] Add completion comment
- [ ] Close issue (if policy allows)
- [ ] Notify orchestrator
- [ ] Update orchestrator state file
