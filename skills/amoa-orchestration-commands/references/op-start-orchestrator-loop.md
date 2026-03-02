---
procedure: support-skill
workflow-instruction: support
---

# Operation: Start Orchestrator Loop


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Prepare Task Sources](#step-1-prepare-task-sources)
  - [Step 2: Start the Loop](#step-2-start-the-loop)
  - [Step 3: Understand Loop State File](#step-3-understand-loop-state-file)
- [Current Iteration](#current-iteration)
  - [Step 4: Understand Task Monitoring](#step-4-understand-task-monitoring)
  - [Step 5: Monitor Loop Progress](#step-5-monitor-loop-progress)
  - [Step 6: Understand Stop Hook Behavior](#step-6-understand-stop-hook-behavior)
  - [Step 7: Provide Completion Promise (Optional)](#step-7-provide-completion-promise-optional)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Authentication Module](#authentication-module)
- [API Routes](#api-routes)
- [Checklist](#checklist)

## When to Use

Use this operation to start the continuous task-driven development loop that monitors multiple task sources.

## Prerequisites

- Orchestration phase active (`/start-orchestration` executed)
- At least one agent registered
- At least one task assigned

## Procedure

### Step 1: Prepare Task Sources

Ensure task sources are ready:

```bash
# GitHub Projects: Verify project exists
gh project list --owner <OWNER>

# Task file: Create or verify
test -f TASKS.md || touch TASKS.md

# Claude Tasks: Active via TaskList API
# (automatically available)
```

### Step 2: Start the Loop

```bash
# Basic start
/orchestrator-loop

# With specific goal
/orchestrator-loop "Complete all authentication module tasks"

# With max iterations
/orchestrator-loop --max-iterations 50

# With custom task file
/orchestrator-loop --task-file "design/TASKS.md"

# Full options
/orchestrator-loop "Complete auth tasks" \
  --max-iterations 100 \
  --completion-promise "AUTH_MODULE_DONE" \
  --task-file "TASKS.md" \
  --check-tasks true \
  --check-github true \
  --github-project PVT_kwDOBxxxxxx
```

### Step 3: Understand Loop State File

The command creates `design/state/loop.md`:

```yaml
---
status: active
started_at: 2024-01-15T10:00:00Z
iteration: 0
max_iterations: 100
completion_promise: "AUTH_MODULE_DONE"
task_sources:
  claude_tasks: true
  github_projects: true
  task_file: "TASKS.md"
  todo_list: true
github_project_id: PVT_kwDOBxxxxxx
---

# Orchestrator Loop State

## Current Iteration
- Number: 0
- Started: 2024-01-15T10:00:00Z
- Pending Tasks: (checking...)
```

### Step 4: Understand Task Monitoring

The loop checks (in order):
1. **Claude Tasks** - TaskList API items
2. **GitHub Projects** - Open Kanban cards
3. **Task File** - Unchecked `- [ ]` items
4. **TODO List** - Claude session TODOs

Priority: Claude Tasks > GitHub Projects > Task File > TODO List

### Step 5: Monitor Loop Progress

```bash
# Check loop status
/orchestrator-status

# Watch iteration count
/orchestrator-status --verbose
```

### Step 6: Understand Stop Hook Behavior

The loop prevents Claude from stopping until:
1. All task sources show 0 pending tasks
2. 4 verification loops complete (quadruple-check)
3. `ALL_TASKS_COMPLETE` is output

### Step 7: Provide Completion Promise (Optional)

If configured, output the promise to signal completion:

```
<promise>AUTH_MODULE_DONE</promise>
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Loop Started | Boolean | Whether loop started successfully |
| State File | Path | `design/state/loop.md` |
| Max Iterations | Number | Iteration limit before escalation |
| Task Sources | Array | Active task source monitors |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Loop already active" | Existing loop running | Use `/cancel-orchestrator` first |
| "No tasks found" | All sources empty | Add tasks before starting |
| "Project not found" | Invalid GitHub Project ID | Verify with `gh project list` |
| "State file error" | Write permission | Check design/state/ permissions |

## Example

```bash
# Complete orchestrator loop setup

# 1. Ensure orchestration is active
/orchestration-status

# 2. Create task file with initial tasks
cat > TASKS.md <<EOF
# Tasks

## Authentication Module
- [ ] Implement login endpoint
- [ ] Add token generation
- [ ] Create validation middleware
- [ ] Write unit tests
- [ ] Integration tests

## API Routes
- [ ] Setup express router
- [ ] Add rate limiting
EOF

# 3. Start the loop
/orchestrator-loop "Complete all tasks in TASKS.md and GitHub project" \
  --max-iterations 100 \
  --task-file "TASKS.md" \
  --github-project PVT_kwDOB1234567

# 4. Monitor progress
/orchestrator-status

# 5. Loop will continue until:
#    - All tasks complete
#    - 4 verification loops pass
#    - Or max iterations reached
```

## Checklist

- [ ] Verify orchestration phase is active
- [ ] Prepare task sources (GitHub Projects, task file)
- [ ] Run `/orchestrator-loop` with appropriate options
- [ ] Verify loop state file created
- [ ] Check initial task count
- [ ] Monitor with `/orchestrator-status`
- [ ] Let loop run until completion or intervention needed
