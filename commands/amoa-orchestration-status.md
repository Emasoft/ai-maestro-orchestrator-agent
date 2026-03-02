---
name: eoa-orchestration-status
description: Display Orchestration Phase progress - module completion, assignments, verification status
allowed-tools:
  - "Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py:*)"
  - "Read"
---

# Orchestration Phase Status

Display the current orchestration phase progress, including module completion, agent assignments, and verification status.

## Basic Usage

Show full orchestration status in human-readable text:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py"
```

## Options

### Verbose Output

Show extra details including module descriptions, task UUIDs, and verification sub-status:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py" --verbose
```

### Modules Only

Show only module completion information:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py" --modules-only
```

### Agents Only

Show only active agent assignments:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py" --agents-only
```

### JSON Output

Output as JSON for programmatic use:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py" --format json
```

### Custom Project Root

Check status for a project at a different path:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_orchestration_status.py" --project-root /path/to/project
```

## What This Shows

- **Current phase** (plan or orchestration)
- **Module completion** count and per-module status with assigned agents
- **Active assignments** mapping agents to modules with work status
- **Verification status** including loops remaining and blocking issues
- **Polling schedule** if configured

## Difference from /eoa-orchestrator-status

- `/eoa-orchestrator-status` shows the orchestrator **loop** status (iteration count, task sources, configuration)
- `/eoa-orchestration-status` shows the orchestration **phase** status (modules, agents, assignments, verification)
