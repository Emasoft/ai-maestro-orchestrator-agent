# Kanban Synchronization Protocol

## Overview

This protocol defines when and how agents should update GitHub issue status and move cards on the kanban board. All status transitions are tracked through both issue labels and project board columns to maintain consistency.

---

## Table of Contents

### Part 1: Synchronization Rules
**File:** [KANBAN_SYNC_PROTOCOL-part1-synchronization-rules.md](./KANBAN_SYNC_PROTOCOL-part1-synchronization-rules.md)

- Rule 1: Update Status When Starting Work
- Rule 2: Update Status When Blocked
- Rule 3: Update Status When Unblocked
- Rule 4: Update Status When Creating PR
- Rule 5: Update Status When Tests Fail
- Rule 6: Update Status When PR Merged
- Rule 7: Handle PR Changes Requested

### Part 2: Label Transitions and Board Commands
**File:** [KANBAN_SYNC_PROTOCOL-part2-transitions-and-commands.md](./KANBAN_SYNC_PROTOCOL-part2-transitions-and-commands.md)

- Valid Transitions (mermaid diagram)
- Transition Commands (Backburner, Todo, Dev, Testing, AI Review, Human Review, Publish, Complete, Blocked)
- Project Board Sync Commands
  - Get Item ID for Issue
  - Update Status Field
  - Update Platform Field
  - Update Priority Field
  - Update Agent Field

### Part 3: Automation Script and Troubleshooting
**File:** [KANBAN_SYNC_PROTOCOL-part3-automation-and-troubleshooting.md](./KANBAN_SYNC_PROTOCOL-part3-automation-and-troubleshooting.md)

- Automation Script (`scripts/sync-issue-status.sh`)
- Required Fields Before Status Change
  - Before Moving to "Dev"
  - Before Moving to "AI Review"
  - Before Moving to "Human Review"
  - Before Moving to "Publish"
  - Before Moving to "Complete"
  - Before Setting "Blocked"
- Error Handling
- Best Practices
- Troubleshooting

---

## Status States

### Ratified 17-Column System

The board uses the ratified 17-column vocabulary (`~/.claude/rules/universal-kanban.md`),
14 lifecycle columns plus 3 exception columns.

| Column | Status Label | Description |
|--------|-------------|-------------|
| Backburner | `status:backburner` | Deferred, not yet scheduled |
| Todo | `status:todo` | Scheduled, ready to be designed |
| Design | `status:design` | ARCHITECT is designing the task |
| Dispatch | `status:dispatch` | Designed, awaiting agent assignment |
| Dev | `status:dev` | Actively being implemented |
| Testing | `status:testing` | Under test |
| AI Review | `status:ai_review` | Integrator reviews ALL tasks |
| Human Review | `status:human_review` | User reviews BIG tasks only |
| Complete | `status:complete` | Internally finished, not yet released |
| Publish | `status:publish` | Entering the publish pipeline |
| Published | `status:published` | Published artifact |
| Deploy | `status:deploy` | Entering the deploy pipeline |
| Live | `status:live` | Deployed and live |
| Live Auditing | `status:live_auditing` | Live, under audit/soak |
| Blocked | `status:blocked` | Blocked at any stage |
| Failed | `status:failed` | Failed and retryable |
| Superseded | `status:superseded` | Replaced by other task(s) |

---

## Quick Reference

### Status Labels

See the table above for the full 17-label vocabulary.

### Valid Transitions

```
Backburner ► Todo ► Dev ► Testing ─┬─► AI Review ─┬─► Publish ► Complete
                            │      │              │       ▲
                            │      ▼              ▼       │
                            │    (back to Dev)  Human Review
                            │                     (big tasks only)
                            │
                            │◄──── AI Review (changes requested)
                            │
                            ▼
                         Blocked
                            │
                            ▼
                           Dev
```

### Quick Commands

Every status transition uses the same `gh issue edit` pattern — only the
label pair changes:

```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:{{OLD_STATUS}}" \
  --add-label "status:{{NEW_STATUS}}"
```

Apply the concrete per-transition label pairs from
[KANBAN_SYNC_PROTOCOL-part2-transitions-and-commands.md](./KANBAN_SYNC_PROTOCOL-part2-transitions-and-commands.md)
(Transition Commands section). Two transitions are not listed there — use
the pattern above with these pairs: Backburner → Todo (`backburner` →
`todo`) and Todo → Dev (`todo` → `dev`).

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_OWNER` | Repository owner | `myorg` |
| `REPO_NAME` | Repository name | `myrepo` |
| `PROJECT_NUMBER` | GitHub Project number | `1` |
| `PROJECT_ID` | GitHub Project ID (GraphQL) | `PVT_xxx` |
| `ITEM_ID` | Project item ID | `PVTI_xxx` |
| `STATUS_FIELD_ID` | Status field ID | `PVTSSF_xxx` |
| `AGENT_NAME` | Agent session name | `worker-1` |
| `AIMAESTRO_API` | AI Maestro API URL (AMP handles routing automatically) | Managed by AMP |

---

## Using the Sync Script

The automation script handles both label updates and kanban board synchronization:

```bash
# Usage
./scripts/sync-issue-status.sh ISSUE_NUMBER NEW_STATUS [COMMENT]

# Examples
./scripts/sync-issue-status.sh 42 "Dev" "Started work"
./scripts/sync-issue-status.sh 42 "AI Review" "PR #123 ready for review"
./scripts/sync-issue-status.sh 42 "Complete" "Merged and deployed"
./scripts/sync-issue-status.sh 42 "Blocked" "Waiting for API key"
```

See [Part 3](./KANBAN_SYNC_PROTOCOL-part3-automation-and-troubleshooting.md) for the full script source.

---

## See Also

- [TASK_TEMPLATE.md](./TASK_TEMPLATE.md) - Task issue template
- [PROGRESS_UPDATE_TEMPLATE.md](./PROGRESS_UPDATE_TEMPLATE.md) - Progress reporting format
- [TOOLCHAIN_TEMPLATE.md](./TOOLCHAIN_TEMPLATE.md) - Agent toolchain specification
