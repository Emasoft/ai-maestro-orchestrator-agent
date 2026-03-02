---
name: eoa-orchestration-patterns
description: "Use when coordinating work among multiple developers. Trigger with orchestration requests."
license: Apache-2.0
compatibility: Requires multiple developers or task agents, task tracking system (GitHub issues or similar), clear task definitions with success criteria, and communication channel for status updates. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 2.4.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Steps 10, 12, 23, 24"
procedure: "proc-decompose-design, proc-create-task-plan, proc-handle-successful-pr, proc-iterate"
---

# Orchestration Patterns Skill

## Overview

This skill teaches how to coordinate work among multiple developers using orchestration patterns.

## Output

| Output Type | Description | Example |
|-------------|-------------|---------|
| TaskCreate calls | Task definitions with success criteria | `TaskCreate(subject="Implement module X", ...)` |
| Task assignments | Agent assignments via AI Maestro or Task tool | Message to remote-dev-001 with task details |
| Progress reports | Regular status updates from monitoring | "Task 1: 60% complete, Task 2: blocked on DB" |
| Completion signals | Verification of all tasks done | "All 5 tasks completed, ready for integration" |
| Escalation requests | Blocked task escalations to user/EAMA | "Task 3 blocked: missing API credentials" |

## API Commands Reference

For AI Maestro messaging and Claude Code Tasks API, see [orchestration-api-commands.md](references/orchestration-api-commands.md):
- 1. AI Maestro Messaging for Remote Agents
  - 1.1 When to use AI Maestro vs Task tool
  - 1.2 Sending task assignments to remote agents
  - 1.3 Message types for EOA
- 2. Claude Code Tasks API
  - 2.1 When to use TaskCreate, TaskUpdate, TaskList
  - 2.2 Creating tasks with success criteria
  - 2.3 Task lifecycle commands

## Core Concepts

**Orchestration** is the act of coordinating multiple concurrent tasks performed by different agents to achieve a common goal. An orchestrator:
- Breaks down work into independent tasks
- Assigns tasks to the right workers
- Tracks progress and unblocks stuck work
- Manages communication and feedback

## Prerequisites

1. Multiple developers or task agents available for parallel work
2. A way to track task status (GitHub issues, task lists, or similar)
3. Clear task definitions with success criteria
4. A communication channel for status updates and escalations

## Instructions

### Procedure Overview

1. **Phase 1: Task Decomposition** - Break down the goal into independent, parallelizable tasks
2. **Phase 2: Task Assignment** - Assign tasks to developers with clear instructions
3. **Phase 3: Progress Monitoring** - Track task completion and identify blocks
4. **Phase 4: Escalation & Unblocking** - Handle blocked tasks and escalate when needed
5. **Phase 5: Integration & Verification** - Combine results and verify completion

---

## Reference Files

### Task Complexity Classifier ([references/task-complexity-classifier.md](references/task-complexity-classifier.md))

Evaluate task complexity to determine appropriate planning investment.

**Contents:**
- Classification Process - When deciding if a task needs planning
- Simple/Medium/Complex Task classification criteria
- Practical Tips and Anti-Patterns

**Read first** - Understanding task complexity guides all subsequent decisions.

---

### Agent Selection Guide ([references/agent-selection-guide.md](references/agent-selection-guide.md))

Select the right specialized agent for each task based on language, domain, and capabilities.

**Contents:**
- Selection Decision Tree - When you need to delegate a task
- Language-Specific Agents - Python/JS/Go/Rust agent selection
- Anti-Patterns and Best Practices

**Read second** - Essential for effective task delegation. **Prerequisite:** Task Complexity Classifier

---

### Project Setup Menu ([references/project-setup-menu.md](references/project-setup-menu.md))

Conduct interactive setup to establish project parameters, team configuration, and quality standards.

**Contents:**
- Menu Implementation - When starting a new project
- Team Configuration and Repository Configuration
- Release Strategy and Troubleshooting

**Read third** - Run before any project work begins. **Prerequisite:** Agent Selection Guide

---

### Language Verification Checklists ([references/language-verification-checklists.md](references/language-verification-checklists.md))

Ensure code quality, build success, and release readiness with language-specific verification standards.

**Contents:**
- Python/Go/JavaScript/TypeScript/Rust Verification Checklists
- Usage in Orchestration and Automation Scripts

**Read last** - Apply when reviewing deliverables. **Prerequisite:** Project Setup Menu

---

### Progress Monitoring ([references/progress-monitoring.md](references/progress-monitoring.md))

PROACTIVE monitoring of implementer agents to ensure progress and completion.

**Contents:**
- 1. Proactive Monitoring Principles
- 2. PROACTIVE Status Request Protocol
- 3. PROACTIVE Unblocking Protocol
- 4. PROACTIVE Task Completion Enforcement

**When to use:** When agent silent 15+ min, reports blocker, wants to stop, or task needs verification.

---

### Verification Loops ([references/verification-loops.md](references/verification-loops.md))

MANDATORY 4-verification-loops before any Pull Request is approved.

**Contents:**
- 1. Overview - Why 4 Verification Loops Are Required
- 2-5. Steps 1-4: Assignment, Verification Message, Tracking, Final Decision
- 6. Enforcement Rules

**When to use:** At task assignment, when agent asks "Can I make a PR?", when tracking verification.

---

### Orchestrator No Implementation Rule ([references/orchestrator-no-implementation.md](references/orchestrator-no-implementation.md))

RULE 15: The orchestrator NEVER writes production code.

**Contents:**
- Forbidden/Allowed Actions for Orchestrators
- Small Experiments (with limits)
- Self-Check Procedure

**When to use:** Before any action (self-check), when tempted to write code directly.

---

### User Requirements Immutable Rule ([references/user-requirements-immutable.md](references/user-requirements-immutable.md))

RULE 14: User requirements cannot be changed without explicit user approval.

**Contents:**
- Orchestration Requirement Enforcement by phase
- Requirement Issue Workflow

**When to use:** At project start, when requirement cannot be implemented as stated.

---

### Orchestrator-Exclusive Communications ([references/orchestrator-exclusive-communications.md](references/orchestrator-exclusive-communications.md))

RULE 16: Only the orchestrator can send/receive messages or commit changes.

**Contents:**
- Orchestrator-Exclusive Actions
- Sub-Agent Restrictions
- Communication Flow and Enforcement

**When to use:** Before spawning sub-agents, when sub-agent needs external communication.

---

### Non-Blocking Patterns ([references/non-blocking-patterns.md](references/non-blocking-patterns.md))

RULE 17: The orchestrator must ALWAYS remain responsive.

**Contents:**
- Async Task Delegation Patterns
- Polling Instead of Blocking
- Parallel Agent Spawning
- Emergency Response Availability

**When to use:** Before any long-running command, when spawning agents, when checking messages.

---

### Orchestrator Guardrails ([references/orchestrator-guardrails.md](references/orchestrator-guardrails.md))

Detailed role boundaries for orchestrator behavior.

---

### Delegation Checklist ([references/delegation-checklist.md](references/delegation-checklist.md))

Infrastructure task delegation procedures.

---

### Orchestration Examples ([references/orchestration-examples.md](references/orchestration-examples.md))

Detailed examples of orchestration patterns in practice.

**Contents:**
- 1. Authentication Module Implementation - Plan handoff handling
- 2. CI Failure Coordination - Investigation-first pattern
- 3. Parallel Code Review - Section-based decomposition
- 4. Blocked Dependency Handling - Parallel escalation pattern

**When to use:** When you need concrete examples of orchestration workflows.

---

### Orchestration API Commands ([references/orchestration-api-commands.md](references/orchestration-api-commands.md))

AI Maestro messaging and Claude Code Tasks API reference.

**Contents:**
- 1. AI Maestro Messaging for Remote Agents
- 2. Claude Code Tasks API

**When to use:** When sending messages or creating/updating tasks.

---

### RULE 14 Enforcement ([references/rule-14-enforcement.md](references/rule-14-enforcement.md))

Canonical text for RULE 14: User Requirements Are Immutable.

**When to use:** When enforcing requirement immutability at all orchestration phases.

---

### Sub-Agent Role Boundaries Template ([references/sub-agent-role-boundaries-template.md](references/sub-agent-role-boundaries-template.md))

Template for defining worker agent role boundaries in task delegations.

**When to use:** When delegating tasks to worker agents.

---

### Workflow Checklists ([references/workflow-checklists.md](references/workflow-checklists.md))

Orchestration workflow checklists for task decomposition, assignment, monitoring, and integration.

**When to use:** When executing orchestration workflows.

---

### Log Formats ([references/log-formats.md](references/log-formats.md))

Log format specifications for orchestration activities.

**When to use:** When creating delegation logs and status reports.

---

### Archive Structure ([references/archive-structure.md](references/archive-structure.md))

Archive directory structure for completed work.

**When to use:** When archiving completed tasks and projects.

---

## Quick Reference Checklist

Copy this checklist and track your progress:

- [ ] Break down the goal into independent tasks (Phase 1)
- [ ] Define success criteria for each task clearly
- [ ] Assign one task per agent/developer
- [ ] Provide complete task instructions with context and dependencies
- [ ] Define clear scope boundaries for each task
- [ ] Request minimal status reports (1-2 lines)
- [ ] Create tracking mechanism (GitHub issues or task list)
- [ ] **PROACTIVELY** monitor progress (check regularly, no fixed schedule)
- [ ] **PROACTIVELY** send status request messages using the `agent-messaging` skill if no update received
- [ ] **PROACTIVELY** offer solutions when agents report blockers
- [ ] Identify blocked tasks at first status checkpoint
- [ ] Escalate blocked tasks immediately
- [ ] **PROACTIVELY** remind agents of pending tasks
- [ ] Collect all task results
- [ ] **Require 4 verification loops before any PR** (see [verification-loops.md](references/verification-loops.md))
- [ ] Verify completion against success criteria
- [ ] Document lessons learned

---

## Examples

### Decompose and Delegate a Feature

This example shows how to decompose a feature request into tasks and delegate them.

**Input:** A feature request from the user (via EAMA):

```
Feature: Add user authentication module
Requirements:
- OAuth2 login with Google provider
- Session management with JWT tokens
- Rate limiting on login endpoint (5 attempts per minute)
```

**Output:** The orchestrator produces a task plan with assignments:

```
Task Plan: Authentication Module (3 parallel tasks)

Task 1: OAuth2 Integration
  Assign to: epa-backend-001
  Scope: src/auth/oauth.py, src/auth/providers/google.py
  Success criteria: Google OAuth2 flow completes end-to-end, tokens stored
  Dependencies: None

Task 2: Session Management
  Assign to: epa-backend-002
  Scope: src/auth/session.py, src/auth/jwt.py
  Success criteria: JWT issued on login, validated on protected routes, expires correctly
  Dependencies: None (uses mock OAuth response until Task 1 merges)

Task 3: Rate Limiting
  Assign to: epa-backend-003
  Scope: src/middleware/rate_limit.py, tests/test_rate_limit.py
  Success criteria: Login endpoint rejects 6th attempt within 60s window, returns 429
  Dependencies: None (uses mock login endpoint)

Result: 3 tasks delegated in parallel, each with clear scope and success criteria.
```

For more detailed orchestration examples with transcripts, see [orchestration-examples.md](references/orchestration-examples.md):
- Authentication module implementation from plan handoff
- CI failure coordination with investigation-first pattern
- Parallel code review across 5 developers
- Blocked dependency handling with parallel escalation

---

## Important Notes

1. **Never block the orchestrator** - Delegate all long-running tasks to agents
2. **RULE 17: Stay responsive** - Check AI Maestro messages regularly
3. **One task per agent** - Clear boundaries prevent conflicts
4. **Minimal status reports** - Request 1-2 lines only: "[DONE] task-name - result"
5. **Early escalation** - Identify blocks at first checkpoint; escalate immediately
6. **PROACTIVE monitoring** - Poll agents regularly; never wait passively
7. **4-verification-loops** - Only approve PR on 5th request if no issues remain
8. **Orchestrator-exclusive communications** - Sub-agents prepare content but NEVER send externally
9. **Parallel spawning** - Spawn up to 20 agents simultaneously for independent tasks

---

## Error Handling

| Issue | Cause | Resolution |
|-------|-------|------------|
| Agent unresponsive | Agent crashed or blocked | Poll until response; reassign if unrecoverable |
| Task conflict | Same file modified by multiple agents | Assign non-overlapping scope |
| Verification loop stuck | Agent doesn't check changes | Send explicit verification message |
| Escalation pending | User unavailable | Queue issue, continue other work |

See individual reference files for detailed troubleshooting.

---

## Resources

- [Task Complexity Classifier](./references/task-complexity-classifier.md)
- [Agent Selection Guide](./references/agent-selection-guide.md)
- [Project Setup Menu](./references/project-setup-menu.md)
- [Language Verification Checklists](./references/language-verification-checklists.md)
- [RULE 14 - User Requirements Immutable](./references/user-requirements-immutable.md)
- [RULE 14 Enforcement](./references/rule-14-enforcement.md)
- [RULE 15 - Orchestrator No Implementation](./references/orchestrator-no-implementation.md)
- [RULE 16 - Orchestrator Exclusive Communications](./references/orchestrator-exclusive-communications.md)
- [RULE 17 - Non-Blocking Patterns](./references/non-blocking-patterns.md)
- [Orchestration Examples](./references/orchestration-examples.md)
- [Orchestration API Commands](./references/orchestration-api-commands.md)
- [Sub-Agent Role Boundaries Template](./references/sub-agent-role-boundaries-template.md)
- [Workflow Checklists](./references/workflow-checklists.md)
- [Log Formats](./references/log-formats.md)
- [Archive Structure](./references/archive-structure.md)
