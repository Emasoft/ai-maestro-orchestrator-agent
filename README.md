# Orchestrator Agent (amoa-)

**Version**: 1.0.0

## Overview

The Orchestrator Agent handles **task distribution, agent coordination, and progress monitoring**. It receives plans from the Architect and coordinates subagents to implement them.

## Core Responsibilities

1. **Task Distribution**: Break plans into assignable tasks
2. **Agent Coordination**: Manage subagents and remote agents
3. **Progress Monitoring**: Track task completion
4. **Module Management**: Organize work into modules
5. **Verification**: Ensure instructions are followed correctly

## Components

### Agents

| Agent | Description |
|-------|-------------|
| `amoa-main.md` | Main orchestrator agent |
| `amoa-team-orchestrator.md` | Coordinates team of agents |
| `amoa-task-summarizer.md` | Summarizes task progress |
| `amoa-checklist-compiler.md` | Creates verification checklists |
| `amoa-docker-container-expert.md` | Docker and container expertise |
| `amoa-experimenter.md` | Experimentation and prototyping |

### Commands

| Command | Description |
|---------|-------------|
| `amoa-start-orchestration` | Start orchestration phase |
| `amoa-register-agent` | Register remote agent |
| `amoa-assign-module` | Assign module to agent |
| `amoa-reassign-module` | Reassign module |
| `amoa-check-agents` | Check agent status |
| `amoa-add-module` | Add new module |
| `amoa-modify-module` | Modify module |
| `amoa-remove-module` | Remove module |
| `amoa-prioritize-module` | Change module priority |
| `amoa-orchestrator-loop` | Start orchestration loop |
| `amoa-orchestrator-status` | Check orchestrator status |
| `amoa-cancel-orchestrator` | Cancel orchestration |

### Skills

| Skill | Description |
|-------|-------------|
| `amoa-two-phase-mode` | Two-phase orchestration mode |
| `amoa-orchestration-commands` | Orchestration command patterns |
| `amoa-orchestration-patterns` | Orchestration best practices |
| `amoa-remote-agent-coordinator` | Remote agent coordination |
| `amoa-module-management` | Module CRUD operations |
| `amoa-verification-patterns` | Instruction verification |
| `amoa-developer-communication` | Developer comm patterns |
| `amoa-checklist-compilation-patterns` | Checklist generation |
| `amoa-agent-replacement` | Agent replacement handoffs |
| `amoa-task-distribution` | Task breakdown and assignment |
| `amoa-progress-monitoring` | Progress tracking and polling |
| `amoa-messaging-templates` | AI Maestro message formats |
| `amoa-label-taxonomy` | GitHub label system |
| `amoa-implementer-interview-protocol` | Interview-based requirements |
| `amoa-github-action-integration` | GitHub Actions patterns |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `amoa-orchestrator-stop` | Stop | Block exit until tasks complete |
| `amoa-instruction-verification-check` | PreToolUse | Verify instructions before work |
| `amoa-polling-reminder` | UserPromptSubmit | Remind to poll progress |
| `amoa-file-tracker` | PostToolUse | Track file modifications |

## Project Structure Notes

### Non-Standard Directories

- **`git-hooks/`** — Contains git hook scripts (pre-push) for plugin validation before pushing
- **`shared/`** — Shared resources used across skills and agents

### Shell Scripts Compatibility

3 bash/shell scripts (`.sh` files) require **Linux or macOS** and are not natively available on Windows. Windows users should use WSL2 or equivalent.

## Workflow

1. Receives plan from Architect (via Assistant Manager)
2. Creates modules from plan
3. Assigns modules to agents
4. Monitors progress via polling
5. Handles failures and reassignments
6. Reports completion to Assistant Manager
7. Hands off to Integrator for quality gates

## Installation (Production)

<!-- Marketplace installation will be available once the AI Maestro marketplace is configured -->

Install using `--plugin-dir` for now (marketplace coming soon). Use `--scope local` to install only for this agent's directory, or `--scope global` for all projects.

Role plugins are installed with `--scope local` inside the specific agent's working directory (`~/agents/<agent-name>/`). This ensures the plugin is only available to that agent.

Once installed, start a session with the main agent:

```bash
claude --agent amoa-orchestrator-main-agent
```

## Development Only (--plugin-dir)

`--plugin-dir` loads a plugin directly from a local directory without marketplace installation. Use only during plugin development.

```bash
claude --plugin-dir ./OUTPUT_SKILLS/ai-maestro-orchestrator-agent
```

## Validation

```bash
cd OUTPUT_SKILLS/ai-maestro-orchestrator-agent
uv run python scripts/validate_plugin.py . --verbose
```
