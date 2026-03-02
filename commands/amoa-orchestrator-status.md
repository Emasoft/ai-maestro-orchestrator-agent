---
name: eoa-orchestrator-status
description: "Check orchestrator loop status and pending tasks"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_check_orchestrator_status.py:*)"]
---

# Orchestrator Status

Check the current state of the orchestrator loop:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_check_orchestrator_status.py"
```

This shows:
- Whether an orchestrator loop is active
- Current iteration count
- Pending tasks from each source (Claude Tasks, GitHub, task file, TODO)
- Configuration settings
