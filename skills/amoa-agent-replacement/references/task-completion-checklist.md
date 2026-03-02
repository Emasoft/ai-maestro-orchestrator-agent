# Task Completion Checklist (Orchestrator Agent)


## Contents

- [Before Reporting Task Complete](#before-reporting-task-complete)
  - [1. Acceptance Criteria Met](#1-acceptance-criteria-met)
  - [2. Quality Gates Passed](#2-quality-gates-passed)
  - [3. Orchestration Verification](#3-orchestration-verification)
  - [4. Documentation Updated](#4-documentation-updated)
  - [5. Handoff Prepared](#5-handoff-prepared)
  - [6. GitHub Updated (if applicable)](#6-github-updated-if-applicable)
  - [7. Session Memory Updated](#7-session-memory-updated)
- [Verification Loop](#verification-loop)
- [Common Traps (Orchestrator-Specific)](#common-traps-orchestrator-specific)
- [Completion Report Format](#completion-report-format)
- [Pre-Completion Checklist for Orchestrators](#pre-completion-checklist-for-orchestrators)
- [When to Escalate vs Complete](#when-to-escalate-vs-complete)

---

## Before Reporting Task Complete

STOP and verify ALL of the following:

### 1. Acceptance Criteria Met
- [ ] ALL acceptance criteria from task definition satisfied
- [ ] Evidence documented for each criterion
- [ ] No "partial" or "mostly" completions
- [ ] All delegated subtasks confirmed complete by subagents

### 2. Quality Gates Passed
- [ ] Linting passed (ruff check, eslint)
- [ ] Type checking passed (mypy, pyright)
- [ ] Tests pass (pytest, jest)
- [ ] No regressions introduced
- [ ] All subagent reports validated

### 3. Orchestration Verification
- [ ] All spawned agents completed their tasks
- [ ] All agent responses collected and verified
- [ ] No orphaned or stalled subagents
- [ ] GitHub Issues updated with agent progress
- [ ] Project board items moved to correct columns

### 4. Documentation Updated
- [ ] Code comments explain WHY (not just what)
- [ ] README updated if behavior changed
- [ ] CHANGELOG entry added (if applicable)
- [ ] TODO lists updated with completed items

### 5. Handoff Prepared
- [ ] Handoff document written to docs_dev/handoffs/
- [ ] Next steps clearly defined
- [ ] AI Maestro message queued to relevant agents
- [ ] Blocking dependencies documented

### 6. GitHub Updated (if applicable)
- [ ] PR created/updated with description
- [ ] Issue comments added with progress
- [ ] Labels updated to reflect status
- [ ] Projects board item moved
- [ ] Issue checklists updated

### 7. Session Memory Updated
- [ ] activeContext.md reflects completed work
- [ ] progress.md has completion entry
- [ ] patterns.md captures any new learnings

## Verification Loop

Before marking complete, ask yourself:

1. "If I was a different agent reading this, would I know what was done?"
2. "Is there any ambiguity about what 'done' means?"
3. "Did I actually test this, or am I assuming it works?"
4. "Are there edge cases I didn't handle?"
5. "Did ALL my delegated subagents report success?"
6. "Have I verified their work, not just trusted their reports?"

If ANY answer is uncertain, the task is NOT complete. Continue work.

## Common Traps (Orchestrator-Specific)

| Trap | Reality |
|------|---------|
| "Subagent said done" | Does NOT equal "verified done" |
| "Tests compile" | Does NOT equal "tests pass" |
| "Code written" | Does NOT equal "code tested" |
| "PR created" | Does NOT equal "PR reviewed and merged" |
| "Should work" | Does NOT equal "verified working" |
| "Almost done" | Does NOT equal "done" |
| "Agent spawned" | Does NOT equal "agent completed" |
| "Message sent" | Does NOT equal "message acknowledged" |

## Completion Report Format

When reporting completion:

```yaml
status: COMPLETE
task_id: <uuid>
summary: <1-2 sentences>
evidence:
  - <what proves it's done>
  - <test output, screenshots, etc.>
  - <subagent completion reports>
files_changed:
  - <path:lines>
subagents_used:
  - agent: <name>
    task: <what they did>
    status: <verified complete>
next_steps: <what happens next>
handoff: <path to handoff doc>
github_updates:
  - issue: <number>
    action: <comment/close/label>
```

## Pre-Completion Checklist for Orchestrators

Before declaring ANY task complete:

1. **Collect all subagent reports** - Do not proceed until all agents respond
2. **Verify each claim** - Read actual output, not just status messages
3. **Run integration tests** - Ensure all pieces work together
4. **Update tracking** - GitHub issues, project boards, progress files
5. **Prepare handoff** - Next agent must be able to continue seamlessly
6. **Queue notifications** - AI Maestro messages to dependent agents

## When to Escalate vs Complete

| Situation | Action |
|-----------|--------|
| All criteria met, verified | Mark COMPLETE |
| 1+ criteria unmet but fixable | Continue work, do NOT mark complete |
| Blocked by external dependency | Mark BLOCKED, document reason |
| Requires user decision | Mark WAITING, notify user |
| Subagent failed | Retry or escalate, do NOT mark complete |
