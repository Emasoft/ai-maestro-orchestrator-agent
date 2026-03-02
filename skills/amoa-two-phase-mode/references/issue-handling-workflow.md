# Issue Handling Workflow


## Contents

- [Overview](#overview)
- [When to Trigger](#when-to-trigger)
- [Issue Categories](#issue-categories)
- [Creating Issue Tasks](#creating-issue-tasks)
- [Standard Task Workflow](#standard-task-workflow)
  - [Phase 1: Initial Assessment](#phase-1-initial-assessment)
  - [Phase 2: Triage (for BUG, ENHANCEMENT, INVESTIGATION)](#phase-2-triage-for-bug-enhancement-investigation)
  - [Phase 3: Investigation (for BUG, BLOCKER, INVESTIGATION)](#phase-3-investigation-for-bug-blocker-investigation)
  - [Phase 4: Test Creation (for BUG, ENHANCEMENT, INVESTIGATION)](#phase-4-test-creation-for-bug-enhancement-investigation)
  - [Phase 5: GitHub Workflow](#phase-5-github-workflow)
  - [Phase 6: Resolution](#phase-6-resolution)
- [Category-Specific Workflows](#category-specific-workflows)
  - [BUG Workflow](#bug-workflow)
  - [BLOCKER Workflow](#blocker-workflow)
  - [QUESTION Workflow](#question-workflow)
  - [ENHANCEMENT Workflow](#enhancement-workflow)
  - [CONFIG Workflow](#config-workflow)
  - [INVESTIGATION Workflow](#investigation-workflow)
- [Claude Tasks Task File Location](#claude-tasks-task-file-location)
- [Integration with Stop Hook](#integration-with-stop-hook)
- [Best Practices](#best-practices)
- [Script Reference](#script-reference)

---

## Overview

When an implementer reports an issue (bug, blocker, question, enhancement), the orchestrator MUST immediately create Claude Code native Task entries to track the complete handling procedure. This ensures systematic resolution and nothing is missed.

## When to Trigger

Create issue Claude Tasks when:

1. **Implementer sends AI Maestro message** reporting an issue
2. **Progress poll reveals a problem** (issue unclear, blocker found, unforeseen difficulty)
3. **Code review identifies a bug** that requires immediate attention
4. **Test failures** indicate a regression
5. **Config feedback request** requires resolution

## Issue Categories

| Category | Priority | Description |
|----------|----------|-------------|
| `BUG` | HIGH | Software defect requiring investigation and fix |
| `BLOCKER` | CRITICAL | Dependency or environment issue preventing progress |
| `QUESTION` | NORMAL | Clarification needed from orchestrator |
| `ENHANCEMENT` | NORMAL | Feature request or improvement suggestion |
| `CONFIG` | HIGH | Configuration guidance needed |
| `INVESTIGATION` | HIGH | Complex issue requiring research |

## Creating Issue Tasks

Use the `eoa_create_issue_tasks.py <!-- TODO: Script not implemented -->` script:

```bash
python3 scripts/eoa_create_issue_tasks.py <!-- TODO: Script not implemented --> \
    --category BUG \
    --reporter implementer-1 \
    --module auth-core \
    --title "Login fails with OAuth tokens" \
    --description "When using OAuth refresh tokens, login fails with 401 error"
```

Or use the `/create-issue-tasks` command (see commands/create-issue-tasks.md).

## Standard Task Workflow

### Phase 1: Initial Assessment

1. **Interview the reporter** - Get full details about the issue
2. **Evaluate category** - Confirm issue type (BUG, BLOCKER, etc.)
3. **Determine severity** - Impact on users and timeline
4. **Check history** - Search git commits for previous occurrences
5. **Create GitHub Issue** - Track in project management

### Phase 2: Triage (for BUG, ENHANCEMENT, INVESTIGATION)

1. **Verify reproducibility** - Can we reproduce the issue?
2. **Collect reproduction steps** - Exact steps to trigger
3. **Identify affected components** - Which modules are involved?
4. **Check latest version** - Does issue exist in newer releases?
5. **Verify not user error** - Confirm it's a real bug

### Phase 3: Investigation (for BUG, BLOCKER, INVESTIGATION)

1. **Spawn researcher agent** - Deep investigation of root cause
2. **Search GitHub history** - Related issues or discussions
3. **Check dependency updates** - May be fixed by updates
4. **Review recent changes** - What changed that could cause this?
5. **Analyze error logs** - Stack traces, error messages
6. **Spawn experimenter** - Isolated testing of hypotheses

### Phase 4: Test Creation (for BUG, ENHANCEMENT, INVESTIGATION)

1. **Create diagnostic test** - Test that identifies the bug
2. **Add regression test** - Prevent future recurrence
3. **Verify test fails** - Before the fix is applied
4. **Verify test passes** - After the fix is applied

### Phase 5: GitHub Workflow

1. **Create feature branch** - Isolate the fix
2. **Assign issue** - To appropriate implementer
3. **Update project board** - Move to "In Progress"
4. **Link to specs** - Connect with module documentation

### Phase 6: Resolution

1. **Notify reporter** - Communicate approach and timeline
2. **Update task status** - Move through columns
3. **Verify fix** - Comprehensive testing
4. **Close GitHub Issue** - Mark as resolved
5. **Mark Claude Tasks DONE** - Complete tracking

## Category-Specific Workflows

### BUG Workflow

Full workflow: Assessment → Triage → Investigation → Tests → GitHub → Resolution

Key actions:
- Reproduce the bug
- Identify root cause
- Create regression test
- Implement fix

### BLOCKER Workflow

Expedited: Assessment → Investigation → Workaround → Resolution

Key actions:
- Identify blocking dependency
- Find workaround ASAP
- Update environment config
- Document workaround

### QUESTION Workflow

Quick: Assessment → Research → Answer → Verify

Key actions:
- Review question
- Research in specs/docs
- Formulate clear answer
- Confirm understanding

### ENHANCEMENT Workflow

Planning: Assessment → Triage → Plan → Tests → GitHub → Resolution

Key actions:
- Evaluate feasibility
- Create implementation plan
- Add acceptance tests
- Track as new feature

### CONFIG Workflow

Configuration: Assessment → Determine → Configure → Verify

Key actions:
- Review config request
- Determine correct values
- Create config files
- Verify in environment

### INVESTIGATION Workflow

Deep dive: Assessment → Triage → Full Investigation → Tests → Document

Key actions:
- Spawn researcher agent
- Spawn experimenter agent
- Document findings
- Create actionable items

## Claude Tasks Task File Location

Task files are created in: `docs_dev/issue-tasks/`

File naming: `ISSUE-YYYYMMDD-HHMMSS.md`

Example: `docs_dev/issue-tasks/ISSUE-20260109-143022.md`

## Integration with Stop Hook

The orchestrator stop hook checks `docs_dev/issue-tasks/` for pending Claude Code native Tasks. Exit is blocked if:

- Any issue task file has `status: "open"` in frontmatter
- Any `[PENDING]` or `[IN_PROGRESS]` tasks remain

## Best Practices

1. **Create immediately** - Don't wait, create tasks as soon as issue is reported
2. **Be thorough** - Don't skip triage for "obvious" bugs
3. **Document everything** - Use the Notes section in the task file
4. **Update status** - Change tasks from PENDING → IN_PROGRESS → DONE
5. **Close when done** - Mark issue as resolved, update frontmatter status

## Script Reference

See `scripts/eoa_create_issue_tasks.py <!-- TODO: Script not implemented -->` for implementation details.

```
Usage: eoa_create_issue_tasks.py <!-- TODO: Script not implemented --> [OPTIONS]

Options:
  --category    Issue category (required)
  --reporter    Who reported the issue (required)
  --module      Affected module (required)
  --title       Brief issue title (required)
  --description Detailed description
  --docs-dev-path Path to docs_dev (default: docs_dev)
  --json        Output result as JSON
```
