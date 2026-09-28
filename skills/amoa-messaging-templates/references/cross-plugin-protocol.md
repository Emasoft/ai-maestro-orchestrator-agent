## Table of Contents
- [Communication Hierarchy](#communication-hierarchy)
- [Who Messages Whom](#who-messages-whom)
- [Label Prefix for GitHub](#label-prefix-for-github-single-account-mode)
- [Status Labels](#status-labels)

---

## Communication Hierarchy

```
USER
  |
AMAMA (Assistant Manager) - User's interface, approval authority
  |
AMCOS (Chief of Staff) - Agent lifecycle, team management
  | | |
AMAA (Architect)  AMOA (Orchestrator)  AMIA (Integrator)
```

## Who Messages Whom

| From | To | Purpose |
|------|-----|---------|
| AMAMA | AMCOS | Project creation, approval decisions, status requests |
| AMCOS | AMAMA | Approval requests, status reports, escalations |
| AMCOS | AMOA | Agent availability notifications, team assignments |
| AMCOS | AMAA | Design requests (via AMOA typically) |
| AMOA | AMAA | Design requests, requirements handoff |
| AMOA | AMIA | Integration/review requests |
| AMOA | Remote Agents | Task assignments, status requests |
| AMAA | AMOA | Design handoffs |
| AMIA | AMOA | Integration results, quality reports |
| Any Agent | AMCOS | Escalations, resource requests |

## Label Prefix for GitHub (Single-Account Mode)

All plugins use `assign:` prefix for agent assignment labels:

```bash
# Assign task to agent
gh issue edit <number> --add-label "assign:<agent-name>"

# Query agent's tasks
gh issue list --label "assign:<agent-name>"
```

## Status Labels

The ratified 22-column vocabulary (3P-KAN, the 3-pillars spec 4.0.0), 1:1 with the TRDD
`column:` enum:

| Label | Meaning |
|-------|---------|
| `status:backburner` | Not yet approved |
| `status:approval` | Awaiting COS/MANAGER approval per `min-approval-requirement:` |
| `status:design` | Card expanded in place with design + specs |
| `status:design_ai_review` | Design body reviewed by COS/MANAGER |
| `status:design_human_review` | Human review; skipped when `min-approval-requirement: none` |
| `status:todo` | Approved and designed, ready to be verified |
| `status:verify_assumptions` | Every claim in the card is verified |
| `status:plan` | Non-interactive plan-mode produces a plan file |
| `status:dispatch` | Planned, awaiting agent assignment |
| `status:dev` | Actively being implemented; enforces the plan's steps |
| `status:testing` | Under test |
| `status:ai_review` | Code submitted for automated review |
| `status:human_review` | Code awaiting human review |
| `status:complete` | Internally finished, not yet released |
| `status:publish` | Entering the publish pipeline |
| `status:published` | Published artifact |
| `status:deploy` | Entering the deploy pipeline |
| `status:live` | Deployed and live |
| `status:live_auditing` | Live, under audit/soak |
| `status:blocked` | Blocked by a non-empty `blocked-by:` list |
| `status:failed` | Failed and retryable — stays open, never archived |
| `status:superseded` | Replaced by other TRDD(s) |
