---
name: amoa-kanban-management
description: GitHub Projects V2 kanban board management. Use when creating boards, adding columns, moving items. Trigger with kanban or column requests.
license: Apache-2.0
compatibility: Requires gh CLI authenticated with project scopes. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Kanban Board Management Skill

## Overview

Manage GitHub Projects V2 kanban boards: create boards, columns, move items, sync status.

## Prerequisites

`gh` CLI authenticated with `project` and `read:project` OAuth scopes. See [references/gh-auth-scopes.md](references/gh-auth-scopes.md)
<!-- TOC: 1 Why project scopes are required - Default gh auth login does not include them | 2 Complete list of required OAuth scopes - All scopes needed for agent operations | 3 How to check current scopes - Verifying your authentication | 4 How to add missing scopes - Interactive browser flow required | 5 Pre-flight validation command - One-liner to check before operations | 6 Scope provisioning is a manual pre-deployment step - Cannot be automated by agents | 7 Troubleshooting - Common scope-related errors -->

## Instructions

1. Verify scopes: `gh auth status 2>&1 | grep -q "project" || echo "ERROR: gh auth refresh -h github.com -s project,read:project"`
2. Query board/column IDs via GraphQL. See [references/kanban-procedures.md](references/kanban-procedures.md)
<!-- TOC: Table of Contents | Add new columns safely (preserves existing columns and their assignments) -->
3. Execute procedure. NEVER call `updateProjectV2Field` directly -- use `scripts/gh-project-add-columns.py`
4. Verify JSON output. Columns: [references/kanban-column-system.md](references/kanban-column-system.md)
<!-- TOC: Table of Contents | Standard 8-Column System | Available Scripts -->

## Full Pipeline Workflow

The orchestrator is the PRIMARY kanban manager and drives the entire Issue-to-Release pipeline.
See [references/pipeline-workflow.md](references/pipeline-workflow.md) for the complete step-by-step.

**Pipeline Phases (kanban perspective):**

| Phase | Kanban Action | Card Movement |
|-------|--------------|---------------|
| 1. Task Creation | Create issue + kanban card | → **Backlog** or **Todo** |
| 2. Agent Request | Request agent from COS (NEVER create directly) | — |
| 3. Task Assignment | Assign agent to card, send task details | → **In Progress** |
| 4. Development Done | Agent reports completion | → **AI Review** |
| 5. AI Review (Integrator) | Integrator reviews PR | PASS → **Merge/Release** / FAIL → back to **In Progress** |
| 6. PR Merge | Integrator merges PR | → **Done** |
| 7. Release | All cards done → release PR from dev to main | — |

**Key Rules:**
- Orchestrator moves ALL cards — agents report status, orchestrator updates the board
- Orchestrator NEVER creates agents — always request via COS using `amp-send.sh`
- Each issue = separate branch = separate PR (isolation principle)
- Integrator = quality gate (reviews + merges)
- Multiple integrators can run in parallel for speed
- Failed reviews create sub-issues and move the card back to In Progress

**Parallel Review Optimization:**
- Create MULTIPLE integrator agents via COS for parallel PR reviews
- Monitor all reviews via `amp-kanban-list.sh --status ai-review`
- After review, integrators can be deleted or reassigned

Copy this checklist and track your progress:

- [ ] Verify OAuth scopes with pre-flight check
- [ ] Query board/column IDs, execute procedure from [references/kanban-procedures.md](references/kanban-procedures.md)
- [ ] Confirm JSON output matches expected format
- [ ] For pipeline: follow step-by-step in [references/pipeline-workflow.md](references/pipeline-workflow.md)

## Output

JSON from GraphQL mutations and board state reports.

## Examples

**Input:** `move-item --project 42 --item ITEM_ID --column "AI Review"`
**Output:** `{"updateProjectV2ItemFieldValue":{"projectV2Item":{"id":"ITEM_ID"}}}`
See [references/kanban-examples.md](references/kanban-examples.md)
<!-- TOC: Example 1: Pre-Flight Scope Check | Example 2: Create Task and Add to Board | Example 3: Move Item to AI Review | Example 4: Safe Guard Before Closing Issue -->

## Error Handling

See [references/kanban-error-handling.md](references/kanban-error-handling.md)
<!-- TOC: Table of Contents | Error Reference Table | Output Specification | Script Output Rules -->

## Resources

- [Auth & OAuth Scopes](references/gh-auth-scopes.md)
- [GraphQL Mutations](references/github-projects-v2-graphql.md)
- [Pitfalls & Guards](references/kanban-pitfalls.md)
- [Procedures](references/kanban-procedures.md)
- [Column System](references/kanban-column-system.md)
- [Checklists](references/kanban-checklist.md)
- [Error Handling](references/kanban-error-handling.md)
- [Examples](references/kanban-examples.md)
- [Pipeline Workflow](references/pipeline-workflow.md)
