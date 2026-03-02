---
name: eoa-start-orchestration
description: "Enter Orchestration Phase - begin coordinating remote agents for implementation"
argument-hint: "[--project-id ID]"
allowed-tools: ["Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eoa_start_orchestration.py:*)"]
---

# Start Orchestration Command

Enter Orchestration Phase Mode to coordinate remote agents implementing the approved plan module by module.

## Usage

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/eoa_start_orchestration.py" $ARGUMENTS
```

## Prerequisites

- Plan Phase must be complete (`/approve-plan` executed)
- Orchestration Phase state file must exist

## What This Command Does

1. **Activates Orchestration Phase** - Sets status to "executing"
2. **Loads module list** from approved plan
3. **Enables monitoring** - Stop hook now enforces module completion
4. **Prepares agent tracking** - Ready to register and assign agents

## Agent Types

Orchestration Phase coordinates three types of agents:

| Agent Type | Location | Assignment | Communication |
|------------|----------|------------|---------------|
| Local Subagents | Same Claude Code | Task tool | Direct |
| Remote AI Agents | Independent sessions | `/assign-module` | AI Maestro |
| Human Developers | GitHub | Kanban assign | GitHub notifications |

## Orchestration Activities

During Orchestration Phase:
1. Register remote agents with `/register-agent`
2. Assign modules with `/assign-module`
3. **Execute Instruction Verification Protocol** (MANDATORY)
4. Monitor progress every 10-15 minutes with `/check-agents`
5. **Proactive Progress Polling** with mandatory questions
6. Unblock stuck agents
7. Review completed work (delegate to local code-reviewer)
8. Enforce 4-verification loops before PRs

## Options

| Option | Description |
|--------|-------------|
| `--project-id` | GitHub Project ID for Kanban sync |

## Stop Hook Behavior

The stop hook blocks exit until:
- ALL modules have `complete` status
- ALL GitHub Project items are done
- ALL Claude Tasks are complete
- 4 verification loops passed

## Next Steps After Starting

1. Run `/register-agent ai implementer-1` to register remote AI agent
2. Run `/assign-module auth-core implementer-1` to assign first module
3. Execute Instruction Verification Protocol before agent starts
4. Run `/check-agents` periodically to poll progress

## Example

```
/start-orchestration --project-id PVT_kwDOBxxxxxx
```

This will:
1. Activate orchestration phase
2. Enable GitHub Project sync
3. Set up monitoring and polling
