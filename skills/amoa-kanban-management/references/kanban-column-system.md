## Table of Contents
- [Ratified 22-Column System (3-Pillars 4.0.0)](#ratified-22-column-system-3-pillars-400)
- [Available Scripts](#available-scripts)

---

## Ratified 22-Column System (3-Pillars 4.0.0)

The board uses the ratified 22-column vocabulary (the 3-pillars spec 4.0.0, clauses
3P-KAN-01..21),
1:1 with the TRDD `column:` enum for cards ON THE BOARD. A card's column is its TRDD
frontmatter `column:` field; there is no separate task database.

| Column | Status Label | Description |
|--------|-------------|-------------|
| Backburner | `status:backburner` | Not yet approved |
| Approval | `status:approval` | Awaiting COS/MANAGER approval per `min-approval-requirement:` |
| Design | `status:design` | Card expanded in place with design + specs |
| Design AI Review | `status:design_ai_review` | Design body reviewed by COS/MANAGER |
| Design Human Review | `status:design_human_review` | Human review; skipped when `min-approval-requirement: none` |
| Todo | `status:todo` | Approved and designed, ready to be verified |
| Verify Assumptions | `status:verify_assumptions` | Every claim in the card is verified |
| Plan | `status:plan` | Non-interactive plan-mode produces a plan file |
| Dispatch | `status:dispatch` | Planned, awaiting agent assignment |
| Dev | `status:dev` | Actively being implemented; enforces the plan's steps |
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

These 22 are the BOARD vocabulary. Five additional BRACKET values are legal `column:`
values but are NOT board columns — `proposal`/`planned` (intake antechamber ahead of
`backburner`) and `refused`/`completed`/`cancelled` (archival terminals), defined by the
folder lifecycle, not by the board (3P-KAN-20). Legal set = 27.

---

## Available Scripts

The AMOA plugin includes these kanban management scripts in `scripts/`:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `amoa_kanban_manager.py` | Create tasks, assign agents, update status, check ready tasks | Day-to-day kanban operations |
| `amoa_sync_kanban.py` | Sync label status with GitHub Project board | After manual board changes or to reconcile state |
| `check-github-projects.py` | Query project board for pending items | Stop-hook checks, status queries |
| `gh-project-add-columns.py` | Safely add columns preserving existing assignments | When adding new columns to a live board |
