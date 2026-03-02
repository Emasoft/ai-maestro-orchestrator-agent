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
- Transition Commands (Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked)
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
  - Before Moving to "In Progress"
  - Before Moving to "AI Review"
  - Before Moving to "Human Review"
  - Before Moving to "Merge/Release"
  - Before Moving to "Done"
  - Before Setting "Blocked"
- Error Handling
- Best Practices
- Troubleshooting

---

## Status States

### Canonical 8-Column System

| # | Column | Code | Label | Description |
|---|--------|------|-------|-------------|
| 1 | Backlog | backlog | status:backlog | Entry point for new tasks |
| 2 | Todo | todo | status:todo | Ready to start, dependencies resolved |
| 3 | In Progress | in-progress | status:in-progress | Active work |
| 4 | AI Review | ai-review | status:ai-review | Integrator reviews ALL tasks |
| 5 | Human Review | human-review | status:human-review | User reviews BIG tasks only |
| 6 | Merge/Release | merge-release | status:merge-release | Ready to merge |
| 7 | Done | done | status:done | Completed |
| 8 | Blocked | blocked | status:blocked | Blocked at any stage |

---

## Quick Reference

### Status Labels
| State | Label |
|-------|-------|
| Backlog | `status:backlog` |
| Todo | `status:todo` |
| In Progress | `status:in-progress` |
| AI Review | `status:ai-review` |
| Human Review | `status:human-review` |
| Merge/Release | `status:merge-release` |
| Done | `status:done` |
| Blocked | `status:blocked` |

### Valid Transitions

```
Backlog ► Todo ► In Progress ► AI Review ─┬─► Merge/Release ► Done
                     │                    │         ▲
                     │                    ▼         │
                     │              Human Review ───┘
                     │              (big tasks only)
                     │
                     │◄──── AI Review (changes requested)
                     │
                     ▼
                  Blocked
                     │
                     ▼
                In Progress
```

### Quick Commands

**Move from Backlog to Todo:**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:backlog" \
  --add-label "status:todo"
```

**Start work on issue (Todo to In Progress):**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:todo" \
  --add-label "status:in-progress"
```

**Submit for AI Review:**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:in-progress" \
  --add-label "status:ai-review"
```

**Escalate to Human Review (big tasks only):**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:ai-review" \
  --add-label "status:human-review"
```

**Move to Merge/Release:**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:ai-review" \
  --add-label "status:merge-release"
```

**Mark as done:**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:merge-release" \
  --add-label "status:done"
```

**Mark as blocked:**
```bash
gh issue edit {{ISSUE_NUMBER}} \
  --repo {{GITHUB_OWNER}}/{{REPO_NAME}} \
  --remove-label "status:in-progress" \
  --add-label "status:blocked"
```

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
./scripts/sync-issue-status.sh 42 "In Progress" "Started work"
./scripts/sync-issue-status.sh 42 "AI Review" "PR #123 ready for review"
./scripts/sync-issue-status.sh 42 "Done" "Merged and deployed"
./scripts/sync-issue-status.sh 42 "Blocked" "Waiting for API key"
```

See [Part 3](./KANBAN_SYNC_PROTOCOL-part3-automation-and-troubleshooting.md) for the full script source.

---

## See Also

- [TASK_TEMPLATE.md](./TASK_TEMPLATE.md) - Task issue template
- [PROGRESS_UPDATE_TEMPLATE.md](./PROGRESS_UPDATE_TEMPLATE.md) - Progress reporting format
- [TOOLCHAIN_TEMPLATE.md](./TOOLCHAIN_TEMPLATE.md) - Agent toolchain specification
