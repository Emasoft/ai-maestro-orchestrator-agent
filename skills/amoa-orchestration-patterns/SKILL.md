---
name: amoa-orchestration-patterns
description: "Use when breaking down tasks for human developers. Trigger with task decomposition requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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

- [ ] Decompose goal into tasks with criteria
- [ ] Assign agents, monitor, escalate
- [ ] Verify 4 loops before PR; integrate

## Examples

**Input:** "Implement OAuth2 login"
**Output:** 5 parallel agents: db-schema, oauth-config, login-flow, token-refresh, auth-tests. Monitor 10 min, 4 loops before PR.

[orchestration-examples.md](references/orchestration-examples.md)
<!-- TOC: Authentication Module Implementation | 1 When you receive a plan handoff from AMAMA for authentication | 2 Task creation pattern for multi-component modules | CI Failure Coordination | 1 When CI tests fail and need coordinated fixes | 2 Investigation-first pattern for unknown root causes | Parallel Code Review | 1 When coordinating reviews across multiple developers | 2 Section-based decomposition for large codebases | Blocked Dependency Handling | 1 When one task blocks on external dependency | 2 Parallel escalation pattern for infrastructure blockers -->

## Error Handling

Blocked tasks escalate per [progress-monitoring.md](references/progress-monitoring.md). Failed agents respawn once, then escalate.
<!-- TOC: Table of Contents | Proactive Monitoring Principles | 1 Why Proactive Monitoring is Critical | 2 The Five Proactive Principles | PROACTIVE Status Request Protocol | 1 When to Send Status Requests | 2 Status Request Message Template | PROACTIVE Unblocking Protocol | 1 When an Agent Reports a Blocker | 2 Unblocking Response Template | PROACTIVE Task Completion Enforcement | 1 Before Allowing Agent to Stop | 2 Verification Requirements | Troubleshooting | Agent Not Responding to Status Requests | Agent Reports Same Blocker Repeatedly | Agent Claims Completion But Evidence Missing | See Also -->

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
    - [Part 1: Team, Repository & Release Configuration](references/project-setup-menu-part1-team-repo-release.md)
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

AI Maestro running, GitHub CLI (`gh`) authenticated.
