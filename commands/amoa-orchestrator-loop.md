---
name: amoa-orchestrator-loop
description: "Start orchestrator loop - monitors tasks across Claude Tasks, GitHub, task files"
argument-hint: "[PROMPT] [--max-iterations N] [--completion-promise TEXT] [--task-file PATH] [--check-tasks] [--check-github] [--github-project NAME]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/amoa_setup_orchestrator_loop.py:*)"]
---

# Orchestrator Loop Command

Execute the setup script to initialize the orchestrator loop:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/amoa_setup_orchestrator_loop.py" $ARGUMENTS
```

The orchestrator loop monitors multiple task sources and prevents exit until ALL are complete:
- Claude Tasks (personal orchestrator tasks)
- GitHub Projects (team/project issues)
- Task file (markdown checklist if specified)
- Claude TODO list (current session)

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `PROMPT` | No | Initial prompt/instructions for the orchestrator |
| `--max-iterations` | No | Maximum number of loop iterations |
| `--completion-promise` | No | Text promise to display when all tasks complete |
| `--task-file` | No | Path to a markdown checklist file to monitor |
| `--check-tasks` | No | Check Claude task list for pending tasks |
| `--check-github` | No | Check GitHub issues for pending tasks |
| `--github-project` | No | GitHub project name to monitor for tasks |

Work on the highest-priority pending tasks. The loop will continue feeding you back to work until everything is done.

When all tasks are genuinely complete, output: ALL_TASKS_COMPLETE
