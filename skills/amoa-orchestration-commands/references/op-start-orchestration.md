---
procedure: support-skill
workflow-instruction: support
---

# Operation: Start Orchestration Phase


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify Plan Phase Complete](#step-1-verify-plan-phase-complete)
  - [Step 2: Execute Start Command](#step-2-execute-start-command)
  - [Step 3: Verify State File Created/Updated](#step-3-verify-state-file-createdupdated)
- [Modules](#modules)
- [Agent Registry](#agent-registry)
  - [Step 4: Register Agents](#step-4-register-agents)
  - [Step 5: Assign First Module](#step-5-assign-first-module)
  - [Step 6: Begin Monitoring](#step-6-begin-monitoring)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Checklist](#checklist)

## When to Use

Use this operation after plan approval to begin the orchestration phase that coordinates agents implementing the approved plan.

## Prerequisites

- Plan Phase complete (USER_REQUIREMENTS.md exists, plan approved)
- `/approve-plan` has been executed
- State file `design/state/exec-phase.md` exists or can be created

## Procedure

### Step 1: Verify Plan Phase Complete

```bash
# Check for plan approval marker
grep -q "status: approved" design/state/exec-phase.md || echo "Plan not approved"

# Verify USER_REQUIREMENTS.md exists
test -f USER_REQUIREMENTS.md || test -f design/USER_REQUIREMENTS.md
```

### Step 2: Execute Start Command

```bash
# Basic start
/start-orchestration

# With GitHub Project integration
/start-orchestration --project-id PVT_kwDOBxxxxxx
```

### Step 3: Verify State File Created/Updated

The command creates or updates `design/state/exec-phase.md`:

```yaml
---
phase: orchestration
status: executing
started_at: 2024-01-15T10:00:00Z
plan_id: plan-20240115
project_id: PVT_kwDOBxxxxxx
---

# Orchestration Phase State

## Modules
| Module | Status | Assigned | Progress |
|--------|--------|----------|----------|
| auth-core | pending | - | 0% |
| api-routes | pending | - | 0% |

## Agent Registry
| Agent ID | Type | Session | Status |
|----------|------|---------|--------|
| (none registered yet) |
```

### Step 4: Register Agents

After starting, register available agents:

```bash
# Register AI agent
/register-agent ai implementer-1 --session helper-agent-generic

# Register human developer (optional)
/register-agent human dev-alice --email alice@example.com
```

### Step 5: Assign First Module

```bash
# Assign a module to an agent
/assign-module auth-core implementer-1
```

### Step 6: Begin Monitoring

```bash
# Check initial status
/orchestration-status

# Start regular polling
/check-agents --interval 15
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Status | String | "Orchestration phase started" |
| State File | Path | `design/state/exec-phase.md` |
| Project ID | String | GitHub Project ID (if provided) |
| Modules Loaded | Number | Count of modules from plan |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Plan not approved" | Plan Phase incomplete | Run `/approve-plan` first |
| "State file missing" | No exec-phase.md | Create from template |
| "Invalid project ID" | Wrong format | Use `gh project list` to get correct ID |
| "Already executing" | Orchestration already active | Use `/orchestration-status` to check |

## Example

```bash
# Complete orchestration start sequence

# 1. Verify prerequisites
test -f USER_REQUIREMENTS.md && echo "Requirements exist"
grep "status: approved" design/state/exec-phase.md && echo "Plan approved"

# 2. Start orchestration
/start-orchestration --project-id PVT_kwDOB1234567

# 3. Register agents
/register-agent ai implementer-1 --session helper-agent-generic
/register-agent ai implementer-2 --session helper-agent-generic-2

# 4. Assign first modules
/assign-module auth-core implementer-1
/assign-module api-routes implementer-2

# 5. Verify status
/orchestration-status
```

## Checklist

- [ ] Verify USER_REQUIREMENTS.md exists
- [ ] Verify plan is approved
- [ ] Run `/start-orchestration` (with --project-id if using GitHub Projects)
- [ ] Verify state file created
- [ ] Register at least one agent
- [ ] Assign first module
- [ ] Verify `/orchestration-status` shows active state
