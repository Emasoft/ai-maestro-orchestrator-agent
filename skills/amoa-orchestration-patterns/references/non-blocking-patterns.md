# Non-Blocking Orchestration Patterns


## Contents

- [Overview](#overview)
- [RULE 17: Orchestrator Must Remain Responsive (IRON RULE)](#rule-17-orchestrator-must-remain-responsive-iron-rule)
- [1. Async Task Delegation Patterns](#1-async-task-delegation-patterns)
  - [1.1 Background Bash Pattern](#11-background-bash-pattern)
  - [1.2 Task Agent with Timeout](#12-task-agent-with-timeout)
  - [1.3 Fire-and-Forget Pattern for Non-Critical Tasks](#13-fire-and-forget-pattern-for-non-critical-tasks)
- [2. Polling Instead of Blocking](#2-polling-instead-of-blocking)
  - [2.1 Progress Polling Protocol](#21-progress-polling-protocol)
  - [2.2 Status Check Without Blocking](#22-status-check-without-blocking)
- [3. Automatic Escalation Triggers](#3-automatic-escalation-triggers)
  - [3.1 When Orchestrator Has Been Unresponsive](#31-when-orchestrator-has-been-unresponsive)
  - [3.2 Self-Check for Responsiveness](#32-self-check-for-responsiveness)
- [4. Parallel Agent Spawning](#4-parallel-agent-spawning)
  - [4.1 Batch Spawning Pattern](#41-batch-spawning-pattern)
  - [4.2 Maximum Concurrent Agents](#42-maximum-concurrent-agents)
- [5. Message Queue Processing](#5-message-queue-processing)
  - [5.1 AI Maestro Priority Queue](#51-ai-maestro-priority-queue)
  - [5.2 Non-Blocking Message Check](#52-non-blocking-message-check)
- [6. Graceful Handoff Pattern](#6-graceful-handoff-pattern)
  - [6.1 Complete Handoff](#61-complete-handoff)
  - [6.2 Instruction Document Template](#62-instruction-document-template)
- [Objective](#objective)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Report Format](#report-format)
- [Timeout](#timeout)
- [7. Emergency Response Availability](#7-emergency-response-availability)
  - [7.1 Always Available For](#71-always-available-for)
  - [7.2 Interrupt Protocol](#72-interrupt-protocol)
- [8. Task Tracking for Async Operations](#8-task-tracking-for-async-operations)
  - [8.1 Tracking Document Format](#81-tracking-document-format)
- [In Progress](#in-progress)
- [Pending Check](#pending-check)
  - [8.2 Task Completion Verification](#82-task-completion-verification)
- [Quick Reference Checklist](#quick-reference-checklist)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Summary](#summary)

---

## Overview

This document defines patterns that ensure the orchestrator ALWAYS remains responsive and available for urgent issues. The orchestrator must NEVER be blocked by long-running operations.

---

## RULE 17: Orchestrator Must Remain Responsive (IRON RULE)

**The orchestrator must ALWAYS be available to:**
1. Respond to user questions and urgent requests
2. Receive and process incoming AI Maestro messages
3. Handle escalations from implementer agents
4. Make real-time decisions about blocked work

**The orchestrator must NEVER:**
1. Wait synchronously for long-running commands
2. Block on test execution or build processes
3. Wait for agent completion without setting a timeout
4. Run any process that takes more than 30 seconds synchronously

---

## 1. Async Task Delegation Patterns

### 1.1 Background Bash Pattern

When you need to run a command that may take more than 30 seconds:

**WRONG (Blocking):**
```bash
# Orchestrator runs directly - BLOCKS for entire duration
npm run test
```

**CORRECT (Non-Blocking):**
```bash
# Delegate to background shell
Bash tool with run_in_background: true
# Or delegate to a task agent
Task agent with: "Run npm test and report results to docs_dev/test-results.md"
```

### 1.2 Task Agent with Timeout

Always spawn task agents with explicit timeout expectations:

```
Task agent prompt:
"Execute [task]. If not complete within 15 minutes, report current status
and blockers. Return: '[DONE/IN_PROGRESS/BLOCKED] task_name - status'"
```

### 1.3 Fire-and-Forget Pattern for Non-Critical Tasks

For tasks that don't need immediate results:

```
Pattern:
1. Spawn task agent with: run_in_background: true
2. Note the task_id in tracking document
3. Continue with other work
4. Check output file later when convenient
```

**Use for:**
- Code formatting/linting
- Documentation generation
- Non-blocking test runs
- Log analysis

---

## 2. Polling Instead of Blocking

### 2.1 Progress Polling Protocol

Instead of waiting for agents to complete:

```
Every 10-15 minutes:
1. Send status request to active agents
2. Process any responses received
3. Identify and escalate blockers
4. Continue with other work
```

### 2.2 Status Check Without Blocking

```bash
# Check if background task completed (non-blocking)
TaskOutput tool with block: false, timeout: 1000

# If still running, continue with other work
# If complete, process results
```

---

## 3. Automatic Escalation Triggers

### 3.1 When Orchestrator Has Been Unresponsive

If the orchestrator hasn't checked in for 30+ minutes:

```
Escalation triggers:
1. AI Maestro messages pile up (unread count > 3)
2. Agent reports blocked status but gets no response
3. Stop hook detects stale task tracking
```

### 3.2 Self-Check for Responsiveness

Before starting any potentially long operation, the orchestrator must ask:

```
RESPONSIVENESS SELF-CHECK:
1. Is this a long-running operation? → DELEGATE
2. Do I have unread AI Maestro messages? → READ FIRST
3. Are any agents waiting for my response? → RESPOND FIRST
4. Has user asked anything pending? → RESPOND FIRST
```

---

## 4. Parallel Agent Spawning

### 4.1 Batch Spawning Pattern

When you have multiple independent tasks:

```
CORRECT: Spawn all in single message
- Task 1: Agent A - File formatting
- Task 2: Agent B - Test execution
- Task 3: Agent C - Documentation
→ All run in parallel

WRONG: Spawn sequentially and wait
- Task 1: Agent A - File formatting (wait...)
- Task 1 done
- Task 2: Agent B - Test execution (wait...)
→ Sequential, wastes time
```

### 4.2 Maximum Concurrent Agents

The orchestrator can spawn up to 20 task agents simultaneously. Use this capacity:

```
Example: Fixing 10 files
CORRECT:
- Spawn 10 python-code-fixer agents in parallel (one per file)
- Continue with other work
- Collect results when all complete

WRONG:
- Fix file 1 (wait...)
- Fix file 2 (wait...)
- ...10 sequential waits
```

---

## 5. Message Queue Processing

### 5.1 AI Maestro Priority Queue

Process messages in priority order without blocking:

```
Priority Order:
1. URGENT - Process immediately, interrupt current work
2. HIGH - Process within 5 minutes
3. NORMAL - Process within 15 minutes
4. LOW - Process when convenient
```

### 5.2 Non-Blocking Message Check

Use the `agent-messaging` skill to perform a quick non-blocking unread message count check.

If the unread count is greater than 0, read messages before continuing.
If the unread count is 0, continue with the current task.

---

## 6. Graceful Handoff Pattern

When the orchestrator needs to delegate work and remain available:

### 6.1 Complete Handoff

```
1. Create detailed instruction document in docs_dev/
2. Spawn task agent with:
   - Clear task description
   - Path to instruction document
   - Success criteria
   - Timeout expectation
   - Report format requirement
3. Log task in tracking document
4. Continue with other work
5. Check results on schedule or when notified
```

### 6.2 Instruction Document Template

```markdown
# Task Assignment: [TASK_NAME]

## Objective
[One sentence description]

## Requirements
[Specific requirements list]

## Success Criteria
[How to know when done]

## Report Format
Return: "[DONE/FAILED] task_name - one_line_result"
If details needed, write to: docs_dev/[task]-results.md

## Timeout
If not complete in [X] minutes, report status and blockers.
```

---

## 7. Emergency Response Availability

### 7.1 Always Available For

The orchestrator must be immediately available for:

1. **User questions** - No task is more important than user interaction
2. **URGENT AI Maestro messages** - May contain corrections or blockers
3. **Agent blockers** - Unblock immediately to maintain progress
4. **Critical errors** - Test failures, build failures, security issues

### 7.2 Interrupt Protocol

When an urgent matter arrives while working on something else:

```
1. Immediately pause current work (note where you stopped)
2. Process the urgent matter
3. Resume previous work
4. Never say "I'll get to that after I finish this"
```

---

## 8. Task Tracking for Async Operations

### 8.1 Tracking Document Format

Maintain a tracking document at `docs_dev/active-tasks.md`:

```markdown
# Active Tasks

## In Progress
| Task ID | Agent | Started | Timeout | Status |
|---------|-------|---------|---------|--------|
| task-001 | python-fixer | 14:30 | 15 min | Running |
| task-002 | test-runner | 14:25 | 20 min | Running |

## Pending Check
| Task ID | Output File | Check After |
|---------|-------------|-------------|
| task-003 | docs_dev/lint-results.md | 14:45 |
```

### 8.2 Task Completion Verification

When checking task completion:

```
1. Use TaskOutput with block: false
2. If not complete, note and continue
3. If complete, process results
4. Update tracking document
5. Never wait synchronously for completion
```

---

## Quick Reference Checklist

Before any operation, verify:

- [ ] Operation takes < 30 seconds OR is delegated to agent/background
- [ ] No unread AI Maestro messages (or will check within 5 min)
- [ ] No agents waiting for response
- [ ] User questions answered
- [ ] Tracking document updated
- [ ] Can be interrupted if urgent matter arrives

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Synchronous test execution | Blocks orchestrator for minutes | Delegate to agent |
| Waiting for agent completion | Blocks until done | Set timeout, poll |
| Sequential file operations | Slow, blocks progress | Parallel agents |
| Ignoring AI Maestro messages | Miss urgent info | Check every 10-15 min |
| "I'll respond after this task" | Delays may cascade | Interrupt and respond |
| Long Bash commands | Blocks the session | Use run_in_background |

---

## Summary

The orchestrator's primary job is COORDINATION, not EXECUTION. Every moment spent waiting is a moment unavailable for:
- User interaction
- Agent coordination
- Blocker resolution
- Priority management

**RULE 17**: The orchestrator must remain responsive at ALL times. Delegate everything that takes more than 30 seconds.
