---
name: amoa-orchestration-patterns
description: "Use when breaking down tasks for human developers. Trigger with task decomposition requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed, task agents, GitHub issues.
metadata:
  author: Emasoft
  version: 2.4.0
context: fork
user-invocable: false
agent: amoa-main
---

# Orchestration Patterns Skill

## Overview

Decomposes goals into parallel tasks, assigns agents, monitors progress, and verifies results. For guardrails and rules, see skill `amoa-orchestration-guardrails`.

## Output

Task assignments, progress updates, and verified integration results.

## Instructions

1. Decompose goal into independent tasks with success criteria
2. Assign each to one agent (up to 20 parallel); monitor every 10-15 min
3. Run 4 verification loops before PR approval; integrate and archive

Copy this checklist and track your progress:

- [ ] Decompose goal into tasks with success criteria
- [ ] Assign agents, monitor, escalate blocked tasks
- [ ] Verify 4 loops before PR; integrate results

## Examples

`Implement OAuth2` -- 5 parallel agents: DB schema, OAuth config, login flow, token refresh, tests.

[orchestration-examples.md](references/orchestration-examples.md)
<!-- TOC: Orchestration Examples | Authentication Module Implementation | When you receive a plan handoff from AMAMA for authentication | Task creation pattern for multi-component modules | CI Failure Coordination | When CI tests fail and need coordinated fixes | Investigation-first pattern for unknown root causes | Parallel Code Review | When coordinating reviews across multiple developers | Section-based decomposition for large codebases | Blocked Dependency Handling | When one task blocks on external dependency | Parallel escalation pattern for infrastructure blockers -->

## Error Handling

Blocked tasks escalate per [progress-monitoring.md](references/progress-monitoring.md). Failed agents respawn once, then escalate.
<!-- TOC: Progress Monitoring (PROACTIVE ENFORCEMENT) | Proactive Monitoring Principles | Why Proactive Monitoring is Critical | The Five Proactive Principles | PROACTIVE Status Request Protocol | When to Send Status Requests | Status Request Message Template | PROACTIVE Unblocking Protocol | When an Agent Reports a Blocker | Unblocking Response Template | PROACTIVE Task Completion Enforcement | Before Allowing Agent to Stop | Verification Requirements | Troubleshooting | Agent Not Responding to Status Requests | Agent Reports Same Blocker Repeatedly | Agent Claims Completion But Evidence Missing | See Also -->

## Resources

- [quick-reference-checklist.md](references/quick-reference-checklist.md)
- [task-complexity-classifier.md](references/task-complexity-classifier.md)
  - Task Complexity Assessment
  - Use-Case Quick Reference
  - Simple Task
  - ...
- [agent-selection-guide.md](references/agent-selection-guide.md)
  - Overview
  - Use-Case Quick Reference
    - Part 1: Language-Specific Agents
  - ...
- [project-setup-menu.md](references/project-setup-menu.md)
  - Overview
  - Document Structure
    - [Part 1: Team, Repository & Release Configuration](project-setup-menu-part1-team-repo-release.md)
  - ...
- [language-verification-checklists.md](references/language-verification-checklists.md)
  - Quick Navigation
  - Cross-Language Resources
  - Documents
  - ...
- [verification-loops.md](references/verification-loops.md)
  - 1. Overview
    - 1.1 Why 4 Verification Loops Are Required
    - 1.2 The Precise Flow Diagram
  - ...
- [orchestration-api-commands.md](references/orchestration-api-commands.md)
  - 1. AI Maestro Messaging for Remote Agents
    - 1.1 When to use AI Maestro vs Task tool
    - 1.2 Sending task assignments to remote agents
  - ...
- [decomposition-example.md](references/decomposition-example.md)

## Prerequisites

AI Maestro running (`http://localhost:23000`), GitHub CLI (`gh`) authenticated.
