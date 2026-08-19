## Table of Contents
- [Ratified 17-Column System](#ratified-17-column-system)
- [Available Scripts](#available-scripts)

---

## Ratified 17-Column System

The board uses the ratified 17-column vocabulary (`~/.claude/rules/universal-kanban.md`),
1:1 with the TRDD `column:` enum — 14 lifecycle columns plus 3 exception columns.
A card's column is its TRDD frontmatter `column:` field; there is no separate task database.

| Column | Status Label | Description |
|--------|-------------|-------------|
| Backburner | `status:backburner` | Deferred, not yet scheduled |
| Todo | `status:todo` | Scheduled, ready to be designed |
| Design | `status:design` | ARCHITECT is designing the task |
| Dispatch | `status:dispatch` | Designed, awaiting agent assignment |
| Dev | `status:dev` | Actively being implemented |
| Testing | `status:testing` | Under test |
| AI Review | `status:ai_review` | Code submitted for automated review |
| Human Review | `status:human_review` | Code awaiting human review |
| Complete | `status:complete` | Internally finished, not yet released |
| Publish | `status:publish` | Entering the publish pipeline |
| Published | `status:published` | Published artifact |
| Deploy | `status:deploy` | Entering the deploy pipeline |
| Live | `status:live` | Deployed and live |
| Live Auditing | `status:live_auditing` | Live, under audit/soak |

Exception columns (apply at any point in the lifecycle):

| Column | Status Label | Description |
|--------|-------------|-------------|
| Blocked | `status:blocked` | Blocked by a non-empty `blocked-by:` list |
| Failed | `status:failed` | Failed and retryable — stays open, never archived |
| Superseded | `status:superseded` | Replaced by other TRDD(s) |

---

## Available Scripts

The AMOA plugin includes these kanban management scripts in `scripts/`:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `amoa_kanban_manager.py` | Create tasks, assign agents, update status, check ready tasks | Day-to-day kanban operations |
| `amoa_sync_kanban.py` | Sync label status with GitHub Project board | After manual board changes or to reconcile state |
| `check-github-projects.py` | Query project board for pending items | Stop-hook checks, status queries |
| `gh-project-add-columns.py` | Safely add columns preserving existing assignments | When adding new columns to a live board |
