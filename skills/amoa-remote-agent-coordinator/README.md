# Remote Agent Coordinator Skill

## Purpose

Enables EOA (Emasoft Orchestrator Agent) to delegate coding tasks to remote AI agents and human developers via AI Maestro messaging. The orchestrator NEVER writes code - it creates precise instructions for remote agents.

## When to Use

- When onboarding a new agent to the project
- When assigning a coding task to a remote developer
- When coordinating multiple remote agents on a feature
- When setting up overnight autonomous operation
- When reviewing reports from remote agents
- When escalating issues between agents

## Key Features

- AI Maestro messaging integration
- Acknowledgment protocol enforcement
- 4-verification loops for PR requests
- Progress monitoring and polling
- Error handling and escalation

## Core Protocols

| Protocol | Use When |
|----------|----------|
| Acknowledgment | Task requires confirmation of receipt |
| 4-Verification Loops | Agent requests PR permission |
| Progress Monitoring | Tracking agent progress |
| Error Handling | Agent reports being blocked |
| Escalation | Issue requires user decision |

## Entry Point

See [SKILL.md](./SKILL.md) for complete instructions.

## Related Skills

- `github-projects-sync` - Task tracking via GitHub
- `orchestration-patterns` - Coordination workflows
