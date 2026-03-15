# AI Maestro Orchestrator Agent (amoa-)

**Version**: 1.6.0

## Overview

The Orchestrator Agent handles **task distribution, agent coordination, and progress monitoring** for multi-agent projects. It receives plans and coordinates subagents to implement them via AI Maestro inter-agent messaging.

## Requirements

- Python 3.8+ with PyYAML (`pip install pyyaml`)
- GitHub CLI (`gh`) for issue and project management
- AI Maestro messaging system for inter-agent communication

## Core Responsibilities

1. **Task Distribution**: Break plans into assignable tasks with dependency ordering
2. **Agent Coordination**: Manage subagents and remote agents via AI Maestro
3. **Progress Monitoring**: Track task completion via polling hooks
4. **Module Management**: Organize work into GitHub Issue-backed modules
5. **Verification**: Ensure instructions are followed correctly before exit
6. **Kanban Management**: GitHub Projects V2 board and column management

## Components

### Agents (6)

| Agent | Description |
|-------|-------------|
| `ai-maestro-orchestrator-agent-main-agent` | Main orchestrator — delegates to sub-agents |
| `amoa-team-orchestrator` | Coordinates team of remote agents |
| `amoa-task-summarizer` | Summarizes task progress and state |
| `amoa-checklist-compiler` | Creates verification checklists |
| `amoa-docker-container-expert` | Docker and container expertise |
| `amoa-experimenter` | Experimentation and prototyping |

### Commands (15)

| Command | Description |
|---------|-------------|
| `/amoa-start-orchestration` | Start orchestration phase |
| `/amoa-orchestrator-loop` | Start orchestration loop |
| `/amoa-orchestration-status` | Show orchestration phase status (modules/agents) |
| `/amoa-orchestrator-status` | Show orchestrator loop status (iterations/tasks) |
| `/amoa-cancel-orchestrator` | Cancel orchestration |
| `/amoa-register-agent` | Register remote agent |
| `/amoa-check-agents` | Check agent status and poll progress |
| `/amoa-assign-module` | Assign module to agent |
| `/amoa-reassign-module` | Reassign module to different agent |
| `/amoa-add-module` | Add new module |
| `/amoa-modify-module` | Modify existing module |
| `/amoa-remove-module` | Remove module |
| `/amoa-prioritize-module` | Change module priority |
| `/amoa-reassign-kanban-tasks` | Reassign kanban board tasks |
| `/amoa-generate-replacement-handoff` | Generate agent replacement handoff document |

### Skills (16)

| Skill | Description |
|-------|-------------|
| `amoa-two-phase-mode` | Plan-then-Execute workflows with formal approval |
| `amoa-orchestration-commands` | Orchestration command reference and loop mechanics |
| `amoa-orchestration-patterns` | Task breakdown patterns for human developers |
| `amoa-remote-agent-coordinator` | Remote AI agent coordination via AI Maestro |
| `amoa-module-management` | Module CRUD operations (1:1 with GitHub Issues) |
| `amoa-verification-patterns` | Implementation verification and evidence collection |
| `amoa-developer-communication` | Developer communication patterns and templates |
| `amoa-checklist-compilation-patterns` | Verification checklist generation |
| `amoa-agent-replacement` | Agent replacement and handoff protocols |
| `amoa-task-distribution` | Task breakdown, assignment, and load balancing |
| `amoa-progress-monitoring` | Progress tracking via state-based polling |
| `amoa-messaging-templates` | AI Maestro message format templates |
| `amoa-label-taxonomy` | GitHub label system for multi-agent coordination |
| `amoa-implementer-interview-protocol` | Interview-based task verification |
| `amoa-github-action-integration` | GitHub Actions CI/CD patterns |
| `amoa-kanban-management` | GitHub Projects V2 kanban board management |

### Hooks (4)

| Hook | Event | Description |
|------|-------|-------------|
| `amoa-orchestrator-stop` | Stop | Blocks exit until all tasks complete (120s timeout) |
| `amoa-instruction-verification-check` | PreToolUse | Blocks agent work if verification incomplete |
| `amoa-polling-reminder` | UserPromptSubmit | Reminds to poll agent progress |
| `amoa-file-tracker` | PostToolUse | Tracks Edit/Write file modifications |

## Project Structure

```
ai-maestro-orchestrator-agent/
├── .claude-plugin/      # Plugin manifest (plugin.json)
├── agents/              # Agent definitions (6 agents)
├── commands/            # Slash command definitions (15 commands)
├── docs/                # Architecture docs (role boundaries, workflow, registry)
├── git-hooks/           # Git hooks (pre-push validation)
├── hooks/               # Plugin hooks (hooks.json + 4 hook scripts)
├── scripts/             # Python scripts (56 scripts + validation suite)
│   └── amoa_stop_check/ # Stop hook package (lock, tasks, phase checks)
├── shared/              # Shared resources across skills
├── skills/              # Skill definitions (16 skills with references)
├── tests/               # Test suite
└── requirements.txt     # Python dependencies (PyYAML)
```

## Workflow

1. **Plan Phase**: Define modules and requirements (two-phase mode)
2. **Assignment**: Assign modules to agents via kanban board
3. **Execution**: Agents implement modules, report via AI Maestro
4. **Monitoring**: Poll agent progress, detect stalls, handle failures
5. **Verification**: 4-loop verification ensures all tasks complete
6. **Completion**: Stop hook enforces completion before session exit

## Installation

Install using `--plugin-dir` for local development:

```bash
claude --plugin-dir /path/to/ai-maestro-orchestrator-agent
```

Start a session with the main orchestrator agent:

```bash
claude --agent ai-maestro-orchestrator-agent-main-agent
```

After modifying plugin files, reload without restarting:

```bash
/reload-plugins
```

## Validation

Run the CPV (Claude Plugins Validation) suite:

```bash
cd ai-maestro-orchestrator-agent
uv run --with pyyaml --with mypy --with types-PyYAML python scripts/validate_plugin.py . --verbose --strict
```

The pre-push hook automatically syncs validators and runs validation before each push.

## Development

- **Sync validators**: `uv run python scripts/sync_cpv_validators.py`
- **Kanban management**: `uv run python scripts/amoa_kanban_manager.py <command>`
- **GitHub project columns**: `uv run python scripts/gh-project-add-columns.py`

## License

MIT
