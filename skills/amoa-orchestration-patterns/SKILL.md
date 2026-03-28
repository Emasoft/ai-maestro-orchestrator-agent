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

Decomposes goals into parallel tasks, assigns agents, monitors progress, and verifies results.

## Output

Task assignments, progress updates, and verified integration results.

## Instructions

**Governance:** ORCHESTRATOR is a governance title (one of 4: MANAGER, CHIEF-OF-STAFF, ORCHESTRATOR, MEMBER). ORCHESTRATOR is the primary kanban manager and can message MANAGER directly.

**Multi-Repo Rule:** All git commands need `git -C "$REPO_PATH"`, all gh commands need `--repo "$OWNER/$REPO"`. Each subagent prompt MUST include: target repo path, repo remote URL, and report output path (`$AGENT_DIR/reports/`).

1. Identify target repo(s) for the goal: `$AGENT_DIR/repos/<repo-name>`
2. Decompose goal into independent tasks with success criteria (include target repo per task)
3. Assign each to one agent (up to 20 parallel); monitor every 10-15 min
4. Run 4 verification loops before PR approval; integrate and archive

Copy this checklist and track your progress:

- [ ] Decompose goal into tasks with success criteria
- [ ] Assign agents, monitor, escalate blocked tasks
- [ ] Verify 4 loops before PR; integrate results

## Examples

`Implement OAuth2` → 5 parallel agents: DB schema, OAuth config, login flow, token refresh, tests.

[orchestration-examples](references/orchestration-examples.md)
<!-- TOC: Authentication Module Implementation | CI Failure Coordination | Parallel Code Review | Blocked Dependency Handling -->

## Error Handling

Blocked tasks escalate per [progress-monitoring](references/progress-monitoring.md). Failed agents respawn once, then escalate.
<!-- TOC: Proactive Monitoring Principles | PROACTIVE Status Request Protocol | Troubleshooting -->

## Resources

- [quick-reference-checklist](references/quick-reference-checklist.md)
<!-- TOC: Quick Reference Checklist | Phase 1: Decomposition | Phase 5: Integration and Verification -->
- [task-complexity-classifier](references/task-complexity-classifier.md)
<!-- TOC: Task Complexity Assessment | Decision Matrix | Classification Process -->
- [agent-selection-guide](references/agent-selection-guide.md)
<!-- TOC: Overview | Quick Navigation by Problem | Golden Rules -->
- [project-setup-menu](references/project-setup-menu.md)
<!-- TOC: Overview | Document Structure | Storage Keys Reference -->
- [language-verification-checklists](references/language-verification-checklists.md)
<!-- TOC: Quick Navigation | Cross-Language Resources -->
- [verification-loops](references/verification-loops.md)
<!-- TOC: Overview | Steps 1-5 | Enforcement Rules -->
- [orchestrator-no-implementation](references/orchestrator-no-implementation.md)
<!-- TOC: See Also | Core Principle -->
- [user-requirements-immutable](references/user-requirements-immutable.md)
<!-- TOC: Core Principle | Enforcement | Forbidden Actions | Issue Workflow -->
- [rule-14-enforcement](references/rule-14-enforcement.md)
<!-- TOC: 1 When handling user requirements in any workflow | 2 When detecting potential requirement deviations -->
- [orchestrator-exclusive-communications](references/orchestrator-exclusive-communications.md)
<!-- TOC: Core Principle | Sub-Agent Restrictions | Communication Flow -->
- [non-blocking-patterns](references/non-blocking-patterns.md)
<!-- TOC: Summary | Overview -->
- [orchestrator-guardrails](references/orchestrator-guardrails.md)
<!-- TOC: Quick Reference Summary | Related Documents -->
- [delegation-checklist](references/delegation-checklist.md)
<!-- TOC: Tracking | Objective -->
- [orchestration-api-commands](references/orchestration-api-commands.md)
<!-- TOC: Claude Code Tasks API | Message types for AMOA -->
- [workflow-checklists](references/workflow-checklists.md)
<!-- TOC: Checklist: Receiving New Task | Checklist: Delegating Task | Checklist: Reporting Results -->
- [decomposition-example](references/decomposition-example.md)
<!-- TOC: Example: Decompose and Delegate a Feature | Error Handling Reference -->

## Prerequisites

AI Maestro running (`http://localhost:23000`), GitHub CLI (`gh`) authenticated. All gh commands must specify `--repo <owner/repo>`. All git commands must use `git -C <repo-path>`.
