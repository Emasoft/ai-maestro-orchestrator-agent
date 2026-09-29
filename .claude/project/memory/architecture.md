---
name: architecture
description: "how does ai-maestro-orchestrator-agent work — overview, the main parts (agents, skills, hooks, scripts), where the key pieces live / what is AMOA and what does it do / AMOA plugin architecture overview — main agent, sub-agents, skills, hooks, scripts / which agent receives work from the assistant manager AMCOS / where does AMOA delegate tasks to implementers and testers / how does AMOA manage the kanban on GitHub Projects / how do AMOA agents coordinate over AMP inter-agent messaging / which sub-agent writes code in Docker / where are the AMOA hooks and scripts defined"
ocd: 2026-06-14
lmd: 2026-09-28
metadata:
  node_type: memory
  type: project
  tier: hub
  functionality: architecture
  globs: ["agents/**", "skills/**", "scripts/**", "hooks/**", "commands/**"]
publish-globally: false
---
^AMOAOVER [desc: "AMOA — a Claude Code plugin: the project-linked orchestrator receiving work from AMCOS, breaking it into tasks, delegating to implementers/testers, monitoring; never writes production code itself", keywords: what is AMOA ai-maestro-orchestrator-agent plugin orchestrator overview receive work from AMCOS assistant-manager delegate to implementers testers monitor progress report results kanban GitHub Projects AMP inter-agent messaging, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
ai-maestro-orchestrator-agent (AMOA) is a Claude Code plugin: the project-linked
orchestrator that receives work from the assistant-manager (AMCOS), breaks it
into assignable tasks, delegates to implementers/testers, monitors progress, and
reports results back. It manages a kanban (GitHub Projects) and coordinates
agents over AI Maestro inter-agent messaging (AMP). It does not write production
code itself — only the `amoa-experimenter` sub-agent writes ephemeral testbed
code in Docker.

## Parts map
^AMOAMAIN [desc: "the AMOA main agent — agents/ai-maestro-orchestrator-agent-main-agent.md — does task distribution, kanban management, and coordination, and loads the AMOA skills", keywords: AMOA main agent task distribution kanban coordination loads skills which file defines the orchestrator agents/ai-maestro-orchestrator-agent-main-agent.md, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
- **Main agent** — `agents/ai-maestro-orchestrator-agent-main-agent.md` (task
  distribution, kanban management, coordination; loads the AMOA skills).
^AMOASUBS [desc: "AMOA sub-agents live in agents/amoa-*.md (checklist-compiler, docker-container-expert, experimenter, task-summarizer, team-orchestrator) and cannot send AMP — they return content to the main agent", keywords: AMOA sub-agents amoa-*.md checklist-compiler docker-container-expert experimenter task-summarizer team-orchestrator cannot send AMP return content to main agent, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
- **Sub-agents** — `agents/amoa-*.md` (checklist-compiler, docker-container-
  expert, experimenter, task-summarizer, team-orchestrator); sub-agents cannot
  send AMP, they return content to the main agent.
^AMOASKLS [desc: "AMOA skills in skills/amoa-* — orchestration patterns, task distribution, progress monitoring, kanban, label taxonomy, messaging templates, remote-agent-coordinator, prrd-trdd-kanban, verification", keywords: AMOA skills skills/amoa-* orchestration patterns commands guardrails loop task distribution progress monitoring kanban label taxonomy messaging templates remote-agent-coordinator prrd-trdd-kanban verification, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
- **Skills** — `skills/amoa-*` (orchestration patterns/commands/guardrails/loop,
  task distribution, progress monitoring, kanban, label taxonomy, messaging
  templates, remote-agent-coordinator, prrd-trdd-kanban, verification patterns…).
^AMOAHOKS [desc: "AMOA hooks live in hooks/hooks.json — Stop blocks premature exit, PreToolUse is an instruction-verification gate on Task, UserPromptSubmit is a polling reminder, PostToolUse is a file tracker", keywords: AMOA hooks hooks.json Stop block premature exit PreToolUse instruction-verification gate on Task UserPromptSubmit polling reminder PostToolUse file tracker, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
- **Hooks** — `hooks/hooks.json` (Stop: block premature exit; PreToolUse:
  instruction-verification gate on Task; UserPromptSubmit: polling reminder;
  PostToolUse: file tracker).
^AMOASCRS [desc: "AMOA scripts are scripts/amoa_*.py (stop-check, verification-status, polling-due, file-tracker, sync-kanban, reassign-kanban, init-design-folders, …) with unit tests in tests/unit/", keywords: AMOA scripts amoa_*.py stop-check verification-status polling-due file-tracker sync-kanban reassign-kanban init-design-folders unit tests tests/unit, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
- **Scripts** — `scripts/amoa_*.py` (stop-check, verification-status, polling-due,
  file-tracker, sync-kanban, reassign-kanban, init-design-folders, …) with unit
  tests in `tests/unit/`.
^AMOAMEMO [desc: "AMOA memory is the janitor-hosted GLOBAL wiki — no per-plugin memory skills; the proactive contract lives in CLAUDE.md + the main agent prompt; this page's scope is the PROJECT wikimem root", keywords: AMOA memory janitor-hosted GLOBAL wiki no per-plugin skills proactive contract CLAUDE.md main agent prompt PROJECT-scope wikimem root, type: project, ocd: 2026-06-14, lmd: 2026-09-28]
- **Memory** — janitor-hosted GLOBAL wiki-memory (no per-plugin memory skills);
  the proactive contract lives in `CLAUDE.md` + the main agent prompt; this is
  the PROJECT-scope wikimem root.

## Applies to
- (radiates down to the component/aspect pages of this functionality — empty until
  the first one is written; wire the reciprocal `## Governed by` on each)

## See also
- (lateral links to other functionality hubs, once they exist)

## Notes and lessons learned
