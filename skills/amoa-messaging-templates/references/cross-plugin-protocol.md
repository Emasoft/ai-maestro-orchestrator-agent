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

| Label | Meaning |
|-------|---------|
| `status:todo` | Not started |
| `status:in-progress` | Being worked on |
| `status:blocked` | Blocked, needs attention |
| `status:review` | Ready for review |
| `status:done` | Complete |
