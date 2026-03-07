## Table of Contents
- [Standard 8-Column System](#standard-8-column-system)
- [Available Scripts](#available-scripts)

---

## Standard 8-Column System

| Column | Status Label | Description |
|--------|-------------|-------------|
| Backlog | `status:backlog` | Tasks identified but not yet scheduled |
| Todo | `status:todo` | Tasks scheduled for current sprint |
| In Progress | `status:in-progress` | Tasks actively being worked on |
| AI Review | `status:ai-review` | Code submitted for automated review |
| Human Review | `status:human-review` | Code awaiting human review |
| Merge/Release | `status:merge-release` | Approved and ready to merge |
| Done | `status:done` | Completed tasks |
| Blocked | `status:blocked` | Tasks blocked by dependencies |

---

## Available Scripts

The AMOA plugin includes these kanban management scripts in `scripts/`:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `amoa_kanban_manager.py` | Create tasks, assign agents, update status, check ready tasks | Day-to-day kanban operations |
| `amoa_sync_kanban.py` | Sync label status with GitHub Project board | After manual board changes or to reconcile state |
| `check-github-projects.py` | Query project board for pending items | Stop-hook checks, status queries |
| `gh-project-add-columns.py` | Safely add columns preserving existing assignments | When adding new columns to a live board |
