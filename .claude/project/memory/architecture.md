---
name: architecture
description: "how does ai-maestro-orchestrator-agent work — overview, the main parts (agents, skills, hooks, scripts), where the key pieces live"
ocd: 2026-06-14
lmd: 2026-06-14
metadata:
  node_type: memory
  type: project
  tier: hub
  functionality: architecture
  globs: ["agents/**", "skills/**", "scripts/**", "hooks/**", "commands/**"]
---
ai-maestro-orchestrator-agent (AMOA) is a Claude Code plugin: the project-linked
orchestrator that receives work from the assistant-manager (AMCOS), breaks it
into assignable tasks, delegates to implementers/testers, monitors progress, and
reports results back. It manages a kanban (GitHub Projects) and coordinates
agents over AI Maestro inter-agent messaging (AMP). It does not write production
code itself — only the `amoa-experimenter` sub-agent writes ephemeral testbed
code in Docker.

## Parts map
- **Main agent** — `agents/ai-maestro-orchestrator-agent-main-agent.md` (task
  distribution, kanban management, coordination; loads the AMOA skills).
- **Sub-agents** — `agents/amoa-*.md` (checklist-compiler, docker-container-
  expert, experimenter, task-summarizer, team-orchestrator); sub-agents cannot
  send AMP, they return content to the main agent.
- **Skills** — `skills/amoa-*` (orchestration patterns/commands/guardrails/loop,
  task distribution, progress monitoring, kanban, label taxonomy, messaging
  templates, remote-agent-coordinator, prrd-trdd-kanban, verification patterns…).
- **Hooks** — `hooks/hooks.json` (Stop: block premature exit; PreToolUse:
  instruction-verification gate on Task; UserPromptSubmit: polling reminder;
  PostToolUse: file tracker).
- **Scripts** — `scripts/amoa_*.py` (stop-check, verification-status, polling-due,
  file-tracker, sync-kanban, reassign-kanban, init-design-folders, …) with unit
  tests in `tests/unit/`.
- **Memory** — janitor-hosted GLOBAL wiki-memory (no per-plugin memory skills);
  the proactive contract lives in `CLAUDE.md` + the main agent prompt; this is
  the PROJECT-scope wikimem root.

## Applies to
- (radiates down to the component/aspect pages of this functionality — empty until
  the first one is written; wire the reciprocal `## Governed by` on each)

## See also
- (lateral links to other functionality hubs, once they exist)

## Notes and lessons learned
