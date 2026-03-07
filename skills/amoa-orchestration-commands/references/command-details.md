## Table of Contents
- /start-orchestration - Enter orchestration phase
- /orchestration-status - View phase progress
- /orchestrator-status - Check loop state
- /orchestrator-loop - Start continuous loop
- /cancel-orchestrator - Cancel active loop

---

## /start-orchestration

**Purpose**: Enter Orchestration Phase to coordinate remote agents implementing the approved plan.

**Syntax**:
```bash
/start-orchestration [--project-id PVT_kwDOBxxxxxx]
```

**Options**:
- `--project-id`: GitHub Project ID for Kanban synchronization

**What it does**:
1. Verifies Plan Phase is complete
2. Sets orchestration status to "executing"
3. Loads module list from approved plan
4. Enables stop hook enforcement
5. Prepares agent tracking structures

**Example**:
```
/start-orchestration --project-id PVT_kwDOB1234567
```

---

## /orchestration-status

**Purpose**: View current Orchestration Phase progress including modules, agents, and verification status.

**Syntax**:
```bash
/orchestration-status [--verbose] [--agents-only] [--modules-only]
```

**Options**:
- `--verbose`: Show detailed polling history and acceptance criteria
- `--agents-only`: Show only agent information
- `--modules-only`: Show only module status

**Output sections**:
- Phase status header (plan ID, status, progress percentage)
- Module status table with completion indicators
- Registered agents list (AI and human)
- Active assignments with verification and polling info

---

## /orchestrator-status

**Purpose**: Check orchestrator loop status and pending tasks across all sources.

**Syntax**:
```bash
/orchestrator-status [--verbose]
```

**Options**:
- `--verbose`: Show detailed debug information and recent log entries

**Output sections**:
- Loop active/inactive status
- Iteration count and limits
- Task sources with pending counts (Claude Tasks, GitHub, Task file, TODO)
- Current task preview
- Debug info (log file, lock file status)

---

## /orchestrator-loop

**Purpose**: Start orchestrator loop for continuous task-driven development.

**Syntax**:
```bash
/orchestrator-loop [PROMPT] [options]
```

**Options**:
- `--max-iterations N`: Maximum iterations before escalation (default: 100)
- `--completion-promise TEXT`: Promise phrase to trigger completion
- `--task-file PATH`: Markdown task file to monitor
- `--check-tasks BOOL`: Check Claude Tasks (default: true)
- `--check-github BOOL`: Check GitHub Projects (default: true)
- `--github-project ID`: Specific GitHub Project ID

**Example**:
```
/orchestrator-loop "Complete all pending authentication tasks" --max-iterations 50
```

---

## /cancel-orchestrator

**Purpose**: Cancel active orchestrator loop.

**What it does**:
1. Checks if loop state file exists
2. Reads current iteration number
3. Removes state file to stop loop
4. Reports cancellation with iteration count

**Note**: This command is hidden from slash command suggestions but remains functional.
