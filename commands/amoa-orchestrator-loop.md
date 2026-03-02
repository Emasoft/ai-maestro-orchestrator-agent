---
name: eoa-orchestrator-loop
description: "Start orchestrator loop - monitors tasks across Claude Tasks, GitHub, task files"
argument-hint: "[PROMPT] [--max-iterations N] [--completion-promise TEXT] [--task-file PATH]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_setup_orchestrator_loop.py:*)"]
---

# Orchestrator Loop Command

Execute the setup script to initialize the orchestrator loop:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_setup_orchestrator_loop.py" $ARGUMENTS
```

The orchestrator loop monitors multiple task sources and prevents exit until ALL are complete:
- Claude Tasks (personal orchestrator tasks)
- GitHub Projects (team/project issues)
- Task file (markdown checklist if specified)
- Claude TODO list (current session)

Work on the highest-priority pending tasks. The loop will continue feeding you back to work until everything is done.

When all tasks are genuinely complete, output: ALL_TASKS_COMPLETE
