# Pipeline Workflow: Issue to Release

Complete step-by-step workflow for the orchestrator-driven development pipeline.

## Table of Contents

- [Step 1: Task Creation](#step-1-task-creation)
- [Step 2: Agent Request via COS](#step-2-agent-request-via-cos)
- [Step 3: Task Assignment](#step-3-task-assignment)
- [Step 4: Move to Review](#step-4-move-to-review)
- [Step 5: AI Review (Integrator)](#step-5-ai-review-integrator)
- [Step 6: Parallel Review Optimization](#step-6-parallel-review-optimization)
- [Step 7: PR Merge (Integrator)](#step-7-pr-merge-integrator)
- [Step 8: Release Preparation](#step-8-release-preparation)
- [Key Rules](#key-rules)
- [Error Recovery](#error-recovery)

---

## Step 1: Task Creation

Create GitHub issues from design docs or feature requests. Each issue becomes a kanban card.

```bash
# Create the GitHub issue in the target repo
gh issue create --repo <owner/repo> --title "Issue title" --body "Description" --label "status:backlog"

# Add to kanban board
amp-kanban-create-task.sh --project <id> --title "Issue title" --status backlog
```

**Rules:**
- Issues are linked to specific repos in the project
- Each issue gets a unique branch name: `feature/<short-desc>` or `fix/<short-desc>`
- Label with priority (`priority:critical`, `priority:high`, `priority:normal`, `priority:low`)
- Label with component/module tags from `amoa-label-taxonomy`

---

## Step 2: Agent Request via COS

The orchestrator NEVER creates agents directly. Always request via the Chief-of-Staff (COS).

```bash
# Request a programmer agent from COS
amp-send.sh <cos-name> "Agent Request" "Need a programmer-agent for issue #N in repo <owner/repo>. Role-plugin: ai-maestro-programmer-agent. Branch: feature/<desc>"

# Request an integrator agent from COS
amp-send.sh <cos-name> "Agent Request" "Need an integrator-agent for PR review in repo <owner/repo>. Role-plugin: ai-maestro-integrator-agent"
```

**COS responsibilities:**
- Creates the agent with the requested role-plugin (e.g., `ai-maestro-programmer-agent`)
- Assigns a random persona name and avatar
- Reports back the agent's persona name to the orchestrator

**Wait for COS response before proceeding to Step 3.**

---

## Step 3: Task Assignment

Once COS reports the new agent name, assign the issue and send task details.

```bash
# Move card to Todo
amp-kanban-move.sh <card-id> todo

# Assign the agent to the issue
gh issue edit <N> --repo <owner/repo> --add-assignee <agent-name>

# Send task details to the agent
amp-send.sh <agent-name> "Task Assignment" "Issue #N: <title>. Repo: <owner/repo>. Branch: feature/<desc>. Acceptance criteria: <criteria>. When done, run amp-task-done.sh"

# Move card to In Progress
amp-kanban-move.sh <card-id> in-progress
```

**Agent workflow (from agent's perspective):**
1. Clone repo, create branch `feature/<desc>`
2. Implement the feature/fix
3. Run tests, commit, push
4. Create PR: `gh pr create --repo <owner/repo> --title "..." --body "Closes #N"`
5. Report completion: `amp-task-done.sh "PR #M submitted for issue #N"`

---

## Step 4: Move to Review

When the agent reports done via `amp-task-done.sh`:

```bash
# Move kanban card to AI Review
amp-kanban-move.sh <card-id> ai-review

# Request integrator agent from COS (if not already available)
amp-send.sh <cos-name> "Agent Request" "Need an integrator-agent for PR #M review in repo <owner/repo>"
```

---

## Step 5: AI Review (Integrator)

Send PR review task to the integrator agent.

```bash
# Assign review task
amp-send.sh <integrator-name> "PR Review" "Review PR #M in repo <owner/repo>. Check: code quality, tests pass, acceptance criteria met. If PASS: report amp-task-done.sh. If FAIL: create bug report with amp-send.sh back to me."
```

**Review outcomes:**

### PASS
```bash
# Integrator reports: "PR #M review PASSED"
# Orchestrator moves card forward
amp-kanban-move.sh <card-id> merge-release
```

### FAIL
```bash
# Integrator reports: "PR #M review FAILED - bugs: [list]"
# Orchestrator moves card back
amp-kanban-move.sh <card-id> in-progress

# Create sub-issues for each bug found
gh issue create --repo <owner/repo> --title "Bug: <description>" --body "Found during review of PR #M. Parent: #N" --label "type:bug,status:todo"

# Assign original programmer agent to fix
amp-send.sh <programmer-name> "Bug Fix" "Review of PR #M found bugs. See issues #X, #Y. Fix and update the PR. Run amp-task-done.sh when fixed."
```

---

## Step 6: Parallel Review Optimization

For multiple PRs awaiting review, create multiple integrator agents in parallel.

```bash
# Request multiple integrators from COS
amp-send.sh <cos-name> "Agent Request" "Need integrator-agent for PR #M1 review in repo <owner/repo>"
amp-send.sh <cos-name> "Agent Request" "Need integrator-agent for PR #M2 review in repo <owner/repo>"
amp-send.sh <cos-name> "Agent Request" "Need integrator-agent for PR #M3 review in repo <owner/repo>"

# Each integrator reviews a different PR simultaneously
# Monitor all reviews
amp-kanban-list.sh --status ai-review
```

**After review completes:**
- Integrators can be deleted (if no further work)
- Integrators can be reassigned to review other PRs
- Orchestrator tracks all review outcomes

---

## Step 7: PR Merge (Integrator)

When review passes, the integrator merges the PR.

```bash
# Orchestrator sends merge instruction to integrator
amp-send.sh <integrator-name> "Merge PR" "PR #M in repo <owner/repo> is approved. Merge with: gh pr merge <M> --squash --repo <owner/repo>"
```

**Integrator executes:**
```bash
gh pr merge <M> --squash --repo <owner/repo>
amp-task-done.sh "PR #M merged into dev branch"
```

**Orchestrator updates board:**
```bash
amp-kanban-move.sh <card-id> done
```

---

## Step 8: Release Preparation

When ALL cards in the kanban are in `done` status, initiate release.

```bash
# Verify all cards are done
amp-kanban-list.sh --status done
amp-kanban-list.sh --status in-progress  # Should return empty
amp-kanban-list.sh --status ai-review    # Should return empty

# Request integrator for release vetting
amp-send.sh <cos-name> "Agent Request" "Need integrator-agent for release vetting of repo <owner/repo>"

# Send release task to integrator
amp-send.sh <integrator-name> "Release Vetting" "Vet the full dev branch in repo <owner/repo>. All PRs have been merged. Create release PR: dev -> main. Report when ready for MANAGER approval."
```

**Release flow:**
1. Integrator vets the full dev branch (all merged PRs combined)
2. Integrator creates release PR: `gh pr create --repo <owner/repo> --base main --head dev --title "Release vX.Y.Z"`
3. MANAGER must approve the release PR (final sign-off)
4. Integrator merges release after MANAGER approval: `gh pr merge <release-PR> --merge --repo <owner/repo>`
5. Integrator creates release tag if needed: `gh release create vX.Y.Z --repo <owner/repo>`

---

## Key Rules

| Rule | Description |
|------|-------------|
| Orchestrator is PRIMARY kanban manager | Moves ALL cards on the board |
| Orchestrator NEVER creates agents | Always request via COS using `amp-send.sh` |
| One issue = one branch = one PR | Isolation principle for clean merges |
| Integrator = quality gate | Reviews code AND merges PRs |
| Parallel integrators allowed | Multiple integrators can review different PRs simultaneously |
| Failed reviews loop back | Card returns to In Progress, sub-issues created for bugs |
| MANAGER approves releases only | Final sign-off on release PRs (dev -> main) |

---

## Error Recovery

| Scenario | Action |
|----------|--------|
| Agent unresponsive after assignment | Wait for ACK timeout, then request replacement agent from COS |
| PR has merge conflicts | Send conflict resolution task back to programmer agent |
| Integrator reports ambiguous result | Request second integrator for independent review |
| All integrators busy | Request additional integrator agents from COS |
| Release PR fails CI | Send CI fix task to integrator, hold release |
| MANAGER rejects release | Integrator creates issue list from rejection feedback, orchestrator re-opens cards |
