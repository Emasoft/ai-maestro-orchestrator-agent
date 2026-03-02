---
operation: approve-plan-transition
procedure: proc-create-task-plan
workflow-instruction: Step 12 - Task Plan Creation
parent-skill: eoa-two-phase-mode
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Approve Plan and Transition to Orchestration


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Validate Exit Criteria](#step-1-validate-exit-criteria)
  - [Step 2: Run Validation Command](#step-2-run-validation-command)
  - [Step 3: Create GitHub Issues](#step-3-create-github-issues)
  - [Step 4: Initialize Orchestration State](#step-4-initialize-orchestration-state)
  - [Step 5: Update Plan Phase State](#step-5-update-plan-phase-state)
  - [Step 6: Output Transition Summary](#step-6-output-transition-summary)
- [Plan Phase Complete](#plan-phase-complete)
  - [Created GitHub Issues](#created-github-issues)
  - [Next Steps](#next-steps)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: Successful Transition](#example-successful-transition)
  - [Example: Failed Validation](#example-failed-validation)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- Plan Phase is complete with all requirements documented
- All modules are defined with acceptance criteria
- User has reviewed and approved the plan

## Prerequisites

- Plan Phase state file exists at `design/state/plan-phase.md`
- USER_REQUIREMENTS.md is complete
- All modules have acceptance criteria defined
- User has confirmed plan approval

## Procedure

### Step 1: Validate Exit Criteria

Verify all Plan Phase exit criteria are met:

| Criterion | Validation | Pass/Fail |
|-----------|------------|-----------|
| USER_REQUIREMENTS.md exists | File exists and has content | [ ] |
| Functional requirements complete | All FR-* items documented | [ ] |
| Non-functional requirements complete | All NFR-* items documented | [ ] |
| Architecture documented | Design section complete | [ ] |
| All modules defined | modules array populated | [ ] |
| All modules have acceptance criteria | Each module has criteria | [ ] |
| All modules have priority | priority field set | [ ] |
| Dependencies identified | dependencies array set | [ ] |
| User approved | Explicit user confirmation | [ ] |

### Step 2: Run Validation Command

Execute the `/approve-plan` command:

```
/approve-plan
```

This command:
1. Reads plan phase state file
2. Validates all exit criteria
3. If validation fails, outputs missing criteria
4. If validation passes, proceeds to transition

### Step 3: Create GitHub Issues

If validation passes, create GitHub Issues for all modules:

```bash
# For each module in the plan
for module in modules:
    gh issue create \
      --title "[Module] $module.name" \
      --body "$module.description + $module.acceptance_criteria" \
      --label "module,priority-$module.priority,status:todo"
```

### Step 4: Initialize Orchestration State

Create the orchestration phase state file at `design/state/orchestration-phase.md`:

```yaml
---
phase: "orchestration"
orchestration_id: "orch-YYYYMMDD-HHMMSS"
status: "active"
created_at: "ISO timestamp"
plan_id: "plan-YYYYMMDD-HHMMSS"

registered_agents: []

modules:
  - id: "auth-core"
    name: "Core Authentication"
    github_issue: 1
    assigned_agent: null
    status: "todo"
    verification_loops: 0

github_project_id: "PVT_kwDO..."
---
```

### Step 5: Update Plan Phase State

Mark Plan Phase as complete:

```yaml
plan_phase_complete: true
transitioned_at: "ISO timestamp"
orchestration_id: "orch-YYYYMMDD-HHMMSS"
```

### Step 6: Output Transition Summary

Provide summary to user:

```markdown
## Plan Phase Complete

**Plan ID:** plan-20260205-143022
**Orchestration ID:** orch-20260205-144500

### Created GitHub Issues
| Module | Issue | Priority | Status |
|--------|-------|----------|--------|
| Core Authentication | #1 | high | todo |
| Google OAuth2 | #2 | medium | blocked |
| GitHub OAuth2 | #3 | medium | blocked |
| Auth Tests | #4 | low | blocked |

### Next Steps
1. Run `/start-orchestration` to enter orchestration phase
2. Register agents with `/register-agent`
3. Assign modules with `/assign-module`
```

## Checklist

Copy this checklist and track your progress:
- [ ] Verify USER_REQUIREMENTS.md is complete
- [ ] Verify all modules have acceptance criteria
- [ ] Verify all modules have priorities set
- [ ] Verify dependencies are documented
- [ ] Obtain explicit user approval
- [ ] Run `/approve-plan` command
- [ ] Verify validation passes
- [ ] Confirm GitHub Issues created
- [ ] Verify orchestration state file created
- [ ] Review transition summary

## Examples

### Example: Successful Transition

**Command:**
```
/approve-plan
```

**Output:**
```
Validating Plan Phase exit criteria...

[PASS] USER_REQUIREMENTS.md exists
[PASS] Functional requirements: 8 items documented
[PASS] Non-functional requirements: 5 items documented
[PASS] Architecture design complete
[PASS] Modules defined: 4 modules
[PASS] Acceptance criteria: All modules have criteria
[PASS] Priorities: All modules have priority
[PASS] Dependencies: All dependencies documented

Creating GitHub Issues...
Created: #1 [Module] Core Authentication
Created: #2 [Module] Google OAuth2
Created: #3 [Module] GitHub OAuth2
Created: #4 [Module] Auth Tests

Initializing Orchestration Phase...
Created: design/state/orchestration-phase.md

TRANSITION COMPLETE
Plan Phase: plan-20260205-143022
Orchestration Phase: orch-20260205-144500

Run /start-orchestration to continue.
```

### Example: Failed Validation

**Command:**
```
/approve-plan
```

**Output:**
```
Validating Plan Phase exit criteria...

[PASS] USER_REQUIREMENTS.md exists
[PASS] Functional requirements: 8 items documented
[FAIL] Non-functional requirements: Section empty
[PASS] Architecture design complete
[PASS] Modules defined: 4 modules
[FAIL] Acceptance criteria: oauth-github missing criteria
[PASS] Priorities: All modules have priority
[PASS] Dependencies: All dependencies documented

VALIDATION FAILED

Missing criteria:
1. Non-functional requirements section is empty
2. Module "oauth-github" has no acceptance criteria

Please complete these items before running /approve-plan again.
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Validation failed | Missing required elements | Complete missing items, re-run |
| GitHub issue creation failed | gh CLI not authenticated | Run `gh auth login` |
| State file not found | Plan phase not started | Run `/start-planning` first |
| User not approved | Missing explicit confirmation | Request user approval |

## Related Operations

- [op-decompose-goals-to-modules.md](op-decompose-goals-to-modules.md) - Modules must be complete
- [op-define-acceptance-criteria.md](op-define-acceptance-criteria.md) - Criteria must be defined
- [op-create-github-issues.md](op-create-github-issues.md) - Issues created during transition
- [op-schedule-claude-tasks.md](op-schedule-claude-tasks.md) - Tasks created after transition
