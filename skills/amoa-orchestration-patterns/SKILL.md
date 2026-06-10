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
  <!-- TOC: Quick Reference Checklist | Phase 1: Decomposition | Phase 2-4: Assignment, Monitoring, Escalation | Phase 5: Integration and Verification | [ ] Break down the goal into independent tasks (Phase 1) | [ ] Define success criteria for each task clearly | [ ] Assign one task per agent/developer | [ ] Provide complete task instructions with context and dependencies | [ ] Define clear scope boundaries for each task | [ ] Request minimal status reports (1-2 lines) | [ ] Create tracking mechanism (GitHub issues or task list) | [ ] **PROACTIVELY** monitor progress (check regularly, no fixed schedule) | [ ] **PROACTIVELY** send status request messages using the `agent-messaging` skill if no update received | [ ] **PROACTIVELY** offer solutions when agents report blockers | [ ] Identify blocked tasks at first status checkpoint | [ ] Escalate blocked tasks immediately | [ ] **PROACTIVELY** remind agents of pending tasks | [ ] Collect all task results | [ ] **Require 4 verification loops before any PR** (see the verification-loops reference) | [ ] Verify completion against success criteria | [ ] Document lessons learned -->
- [task-complexity-classifier.md](references/task-complexity-classifier.md)
  <!-- TOC: Task Complexity Assessment | Use-Case Quick Reference | Simple Task | Criteria | Action | Example Pattern | Medium Task | Complex Task | Decision Matrix | Examples | Simple Task Examples | Medium Task Examples | Complex Task Examples | Classification Process | Step 1: Initial Assessment | Step 2: Count Complexity Signals | Step 3: Apply Classification | Step 4: Choose Action Pattern | Anti-Patterns to Avoid | Over-Planning Simple Tasks | Under-Planning Complex Tasks | Treating All Medium Tasks as Complex | Practical Tips | When in Doubt | Escalation Signals | De-escalation Signals | Summary -->
  - Task Complexity Assessment
  - Use-Case Quick Reference
  - Simple Task
  - ...
- [agent-selection-guide.md](references/agent-selection-guide.md)
  <!-- TOC: Overview | Use-Case Quick Reference | Table of Contents | Part 1: Language-Specific Agents | Part 2: Specialized Agents | Part 3: Decision Tree & Selection | Part 4: Anti-Patterns & Best Practices | Part 5: Advanced Topics & Troubleshooting | Quick Navigation by Problem | Summary: Golden Rules | Remember -->
  - Overview
  - Use-Case Quick Reference
    - Part 1: Language-Specific Agents
  - ...
- [project-setup-menu.md](references/project-setup-menu.md)
  <!-- TOC: Overview | Document Structure | [Part 1: Team, Repository & Release Configuration | [Part 2: Documentation & Quality Requirements | [Part 3: Implementation & Troubleshooting | Quick Navigation by Use Case | Storage Keys Reference -->
  - Overview
  - Document Structure
    - [Part 1: Team, Repository & Release Configuration](references/project-setup-menu-part1-team-repo-release.md)
      <!-- TOC: Table of Contents | Overview | Use-Case Quick Reference | Team Configuration | Question 1: Human Developers | Question 2: AI Remote Agents | Question 3: Access Permissions | Repository Configuration | Question 4: Branch Protection | Question 5: Required Reviews | Question 6: CI Requirements | Release Strategy | Question 7: Alpha-Only Development | Question 8: Package Publishing | Question 9: Versioning Scheme -->
  - ...
- [language-verification-checklists.md](references/language-verification-checklists.md)
  <!-- TOC: Quick Navigation | Cross-Language Resources | Documents | Part 1: Core Languages | Part 2: Extended Platforms | Part 3: Swift and Universal Resources | When to Use Each Checklist -->
  - Quick Navigation
  - Cross-Language Resources
  - Documents
  - ...
- [verification-loops.md](references/verification-loops.md)
  <!-- TOC: Table of Contents | Overview | 1 Why 4 Verification Loops Are Required | 2 The Precise Flow Diagram | Step 1: At Task Assignment | 1 PR Notification Requirement Template | 2 Including in Every Delegation | Step 2: Full Verification Message | 1 When to Send This Message | 2 Verification Message Template (Send 4 Times) | 3 What the Agent Must Check | Step 3: Track PR Requests Per Task | 1 Tracking Table Format | 2 Sample Tracking Table | Step 4: On 5th Request - Final Decision | 1 Approval Conditions | 2 Summary Table | Enforcement Rules | 1 What is NEVER Allowed | 2 What is ALWAYS Required | Troubleshooting | Agent Creates PR Without Approval | Agent Says "No Issues Found" Every Loop | Issues Persist After 4 Loops | See Also -->
  - 1. Overview
    - 1.1 Why 4 Verification Loops Are Required
    - 1.2 The Precise Flow Diagram
  - ...
- [orchestration-api-commands.md](references/orchestration-api-commands.md)
  <!-- TOC: AI Maestro Messaging for Remote Agents | 1 When to use AI Maestro vs Task tool | 2 Sending task assignments to remote agents | 3 Message types for AMOA | Claude Code Tasks API | 1 When to use TaskCreate, TaskUpdate, TaskList | 2 Creating tasks with success criteria | 3 Task lifecycle commands | 4 Task success criteria requirements -->
  - 1. AI Maestro Messaging for Remote Agents
    - 1.1 When to use AI Maestro vs Task tool
    - 1.2 Sending task assignments to remote agents
  - ...
- [decomposition-example.md](references/decomposition-example.md)
  <!-- TOC: Example: Decompose and Delegate a Feature | Input: Feature Request | Output: Task Plan with Assignments | Error Handling Reference | OAuth2 login with Google provider | Session management with JWT tokens | Rate limiting on login endpoint (5 attempts per minute) | Authentication module implementation from plan handoff | CI failure coordination with investigation-first pattern | Parallel code review across 5 developers | Blocked dependency handling with parallel escalation -->

## Prerequisites

AI Maestro running, GitHub CLI (`gh`) authenticated.
