---
name: the-skills-menu
description: "Dynamic skill menu for the ai-maestro-orchestrator-agent plugin. Teaches agents which skills are available, when to use them, and how to load them with the Skill() tool. Use when an agent needs to pick a downstream skill at runtime. Used by every ai-maestro-orchestrator-agent agent via the-skills-menu method (TRDD-9dd64dbf)."
user-invocable: false
---

# the-skills-menu — universal ai-maestro-orchestrator-agent skill catalog

## Overview

This skill is the **catalog** every ai-maestro-orchestrator-agent agent consults to
discover operational skills at runtime. The agent preloads only this
catalog in its `skills:` frontmatter; everything else loads on demand
via the `Skill()` tool.

## Prerequisites

- The calling agent has `Skill` in its `tools:` list.
- A clear task statement so you can pick the right skill.

## Instructions

Follow these steps in order:

1. Identify the task domain.
2. Skim the **Plugin Skills** section below and pick a candidate.
3. Invoke the chosen skill via `Skill({skill: "ai-maestro-orchestrator-agent:<name>"})`
   (use the plugin namespace prefix — cross-plugin references require it).
4. Follow the loaded skill's own checklist; do NOT load another skill
   until the first one returns.
5. Surface the downstream skill's summary to the caller.

## Output

This catalog returns nothing itself — it documents invocations for
OTHER skills. The chosen downstream skill produces the actual output.

## Standalone Skills

No standalone (user/local/project-scope) skills are tracked by this
plugin's catalog yet. Add entries here as the plugin starts to
reference standalone skills outside its own namespace.

## Plugin Skills

The ai-maestro-orchestrator-agent plugin ships the operational skills below. Pick the one your task needs and load it on demand:

| # | Skill | What it does |
|---|-------|--------------|
| 1 | `amoa-agent-replacement` | Use when replacing agents |
| 2 | `amoa-checklist-compilation-patterns` | Use when compiling verification checklists from requirements |
| 3 | `amoa-developer-communication` | Use when communicating with human developers in code reviews and issues |
| 4 | `amoa-github-action-integration` | Trigger with Claude Code action requests |
| 5 | `amoa-implementer-interview-protocol` | Use when verifying implementer readiness |
| 6 | `amoa-kanban-management` | GitHub Projects V2 kanban board management |
| 7 | `amoa-label-taxonomy` | Use when applying GitHub labels |
| 8 | `amoa-messaging-templates` | Use when sending inter-agent messages |
| 9 | `amoa-module-lifecycle` | Use when adding, modifying, removing, prioritizing, or reassigning modules |
| 10 | `amoa-module-management` | Use when managing modules during Orchestration Phase |
| 11 | `amoa-module-sync` | Use when syncing modules with GitHub Issues or troubleshooting module state |
| 12 | `amoa-orchestration-commands` | Use when running orchestration phase commands |
| 13 | `amoa-orchestration-guardrails` | Use when enforcing orchestrator boundaries, rules, and delegation patterns |
| 14 | `amoa-orchestration-loop` | Use when running the orchestrator loop or managing stop hook behavior |
| 15 | `amoa-orchestration-patterns` | Use when breaking down tasks for human developers |
| 16 | `amoa-plan-phase` | Use when running Plan Phase of two-phase mode |
| 17 | `amoa-progress-monitoring` | Use when monitoring agent progress |
| 18 | `amoa-prrd-trdd-kanban` | ORCHESTRATOR's role in the PRRD / TRDD / Kanban workflow |
| 19 | `amoa-remote-agent-coordinator` | Use when coordinating remote AI agents via AI Maestro messaging |
| 20 | `amoa-task-distribution` | Use when distributing tasks |
| 21 | `amoa-two-phase-mode` | Use when running Plan-then-Execute workflows |
| 22 | `amoa-verification-patterns` | Use when verifying implementations |

All entries above are invoked as
`Skill({skill: "ai-maestro-orchestrator-agent:<name>"})`.

## Resources

- `the-skills-menu-create` (skill `claude-plugins-validation:the-skills-menu-create`) —
  the migrator skill in the CPV plugin that can regenerate this
  catalog from the plugin's current skill inventory at any time.
  It is NOT bundled in this plugin; install
  `claude-plugins-validation` to access it.
