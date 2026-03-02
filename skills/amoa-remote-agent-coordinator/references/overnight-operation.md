# Autonomous Operation

## Contents

- **When preparing infrastructure for overnight operation** → [Prerequisites Checklist](#prerequisites-checklist)
- **When handing off tasks to the orchestrator before leaving** → [User Handoff Protocol](#user-handoff-protocol)
- **When monitoring autonomous task execution** → [Operation Flow](#operation-flow)
- **When agents encounter issues requiring escalation** → [Escalation During Autonomous Operation](#escalation-during-autonomous-operation)
- **When agents or systems fail during autonomous operation** → [Recovery Procedures](#recovery-procedures)
- **When tuning autonomous operation behavior** → [Configuration](#configuration)
- **When planning and executing autonomous sessions** → [Best Practices](#best-practices)

## Overview

The EOA (Emasoft Orchestrator Agent) can coordinate remote developer agents autonomously while the user is away. This document describes the complete autonomous operation protocol.

## Prerequisites Checklist

Before initiating autonomous operation:

### Infrastructure
- [ ] AI Maestro messaging system (AMP) running
- [ ] All remote agents online and responsive
- [ ] GitHub access configured for all agents
- [ ] Branch permissions verified

### Project Setup
- [ ] GitHub Project kanban ready
- [ ] Issues created for all autonomous tasks
- [ ] Dependencies between tasks documented
- [ ] No blocking issues unresolved

### Agent Roster
- [ ] AGENT_ROSTER.md up to date
- [ ] Agent capabilities match task requirements
- [ ] Backup agents identified for critical tasks

### Quality Gates
- [ ] CI/CD pipeline functional
- [ ] Test suite stable (no flaky tests)
- [ ] Linting rules configured

## User Handoff Protocol

### Before Leaving

1. **User Reviews Queue**
   ```
   USER: "Complete features GH-101, GH-102, GH-103 autonomously"
   ```

2. **Orchestrator Confirms Understanding**
   ```
   ORCHESTRATOR: "Confirming autonomous tasks:
   - GH-101: User Authentication (high priority)
   - GH-102: Password Reset (normal priority)
   - GH-103: Session Management (normal priority)

   Scope estimate: All within current batch
   Available agents: dev-agent-1, dev-agent-2

   Proceed with autonomous operation?"
   ```

3. **User Approves**
   ```
   USER: "Approved. Escalate only for security issues."
   ```

4. **Orchestrator Begins**
   ```
   ORCHESTRATOR: "Autonomous operation initiated.
   Tasks assigned. Will report completion status when done."
   ```

## Operation Flow

### Phase 1: Task Distribution

```
ORCHESTRATOR analyzes tasks:
├── GH-101: User Auth
│   ├── Complexity: High
│   ├── Dependencies: None
│   └── Assign to: dev-agent-1 (strongest Python)
│
├── GH-102: Password Reset
│   ├── Complexity: Medium
│   ├── Dependencies: GH-101 (uses auth system)
│   └── Assign to: dev-agent-2 (after GH-101)
│
└── GH-103: Session Mgmt
    ├── Complexity: Medium
    ├── Dependencies: GH-101 (uses auth system)
    └── Assign to: dev-agent-1 (after completing GH-101)
```

### Phase 2: Initial Assignment

Send tasks to agents:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "dev-agent-1",
  "subject": "AUTONOMOUS: Implement User Authentication GH-101",
  "priority": "high",
  "content": {
    "type": "task",
    "task_id": "GH-101",
    "autonomous_mode": true,
    "instructions": "[Full task instruction]",
    "completion_criteria": ["..."],
    "test_requirements": ["..."],
    "escalation_rules": {
      "on_blocked": "Report and move to next available task",
      "on_security_concern": "STOP and send urgent escalation",
      "on_architecture_question": "Make best judgment, document decision"
    },
    "report_back": true,
    "next_task_on_complete": "GH-103"
  }
}
```

### Phase 3: Monitoring Loop

```
WHILE tasks_remaining AND user_away:

    1. CHECK for messages on each poll cycle
       └── Any completion reports?
       └── Any escalations?
       └── Any error reports?

    2. ON completion report:
       └── Run two-stage review on PR
       └── IF pass: approve, merge, assign next task
       └── IF fail: send fix instructions

    3. ON escalation:
       └── IF security: queue for user (urgent)
       └── IF architecture: make judgment, document
       └── IF blocked: reassign or defer

    4. ON error:
       └── Analyze error type
       └── Send fix instructions if clear
       └── Reassign to different agent if agent issue

    5. UPDATE GitHub Project cards
       └── Move completed to Done
       └── Update In Progress
       └── Add notes to cards
```

### Phase 4: PR Review (Autonomous)

When PR received:

```
1. Clone to ephemeral worktree
2. Run Gate 1: Spec Compliance
   └── Does PR implement what was asked?
   └── No scope creep?
   └── Interface contract met?

3. Run Gate 2: Quality
   └── Tests pass?
   └── Coverage adequate?
   └── No lint errors?
   └── No security issues?

4. DECISION:
   └── BOTH PASS: Approve and merge
   └── ANY FAIL: Send fix instructions, wait for fix
```

### Phase 5: Completion Report

Generate comprehensive report:

```markdown
# Autonomous Operation Report
**Session**: 2025-12-30-session-01
**Generated**: 2025-12-31 06:00:00

## Summary
- Tasks Completed: 2/3
- PRs Merged: 2
- Issues Encountered: 1
- Escalations: 0

## Task Status

### GH-101: User Authentication
- **Status**: COMPLETE
- **Agent**: dev-agent-1
- **PR**: #147 (merged)
- **Scope**: 3 files modified, 247 lines added
- **Tests**: 47 passed, 0 failed

### GH-102: Password Reset
- **Status**: COMPLETE
- **Agent**: dev-agent-2
- **PR**: #148 (merged)
- **Scope**: 2 files modified, 134 lines added
- **Tests**: 23 passed, 0 failed

### GH-103: Session Management
- **Status**: IN PROGRESS (70%)
- **Agent**: dev-agent-1
- **Branch**: feature/session-mgmt
- **Blocker**: None
- **Remaining**: Core logic complete, tests pending

## Issues Encountered

### Issue 1: CI Timeout
- **Task**: GH-101
- **Occurrence**: During initial test run
- **Description**: CI timed out on large test suite
- **Resolution**: Increased timeout, re-ran successfully
- **Action Taken**: Documented in PR comment

## Recommendations

1. Consider splitting test suite to reduce CI overhead
2. GH-103 has 2 remaining components to complete
3. All code reviewed and merged follows project standards

## Agent Performance

| Agent | Tasks Completed | PRs Merged | Issues Resolved |
|-------|-----------------|------------|-----------------|
| dev-agent-1 | 2 | 2 | 1 |
| dev-agent-2 | 1 | 1 | 0 |
```

## Escalation During Autonomous Operation

### Immediate Escalation (Notify User)

Only for:
- Security vulnerabilities discovered
- Data corruption risk
- Critical infrastructure failure

Message format:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "user-notification-channel",
  "subject": "URGENT: Security issue requires immediate attention",
  "priority": "urgent",
  "content": {
    "type": "urgent-escalation",
    "issue": "SQL injection vulnerability in legacy code",
    "risk": "High - production data at risk",
    "action_required": "Approve hotfix or rollback",
    "blocking": true
  }
}
```

### Deferred Escalation (User Review)

For:
- Architecture questions
- Dependency decisions
- Non-critical blockers

Message format:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-queue",
  "subject": "USER REVIEW: Architecture decision for GH-103",
  "priority": "normal",
  "content": {
    "type": "deferred-escalation",
    "issue": "Redis vs Memcached for session storage",
    "context": "Both work, need user preference",
    "current_action": "Proceeded with Redis (more features)",
    "reversible": true
  }
}
```

## Recovery Procedures

### Agent Goes Offline

1. Detect via missed heartbeat (3 consecutive failed pings)
2. Mark agent as offline in roster
3. Reassign pending tasks to backup agent
4. Log for user review

### All Agents Offline

1. Stop assigning new tasks
2. Document current state
3. Send alert to user
4. Wait for user intervention

### CI/CD Failure

1. Retry once after next poll cycle
2. If persistent after 3 retry attempts, mark PR as blocked
3. Continue with other tasks
4. Document for user review

### Merge Conflict

1. Do NOT attempt automatic resolution
2. Mark PR as blocked
3. Document conflict details
4. Queue for user resolution

## Configuration

### Event-Based Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `heartbeat_missed_threshold` | 3 pings | Mark agent offline |
| `ci_poll_attempts` | 5 checks | Before marking CI blocked |
| `message_check_trigger` | Each poll cycle | Check for messages |

### Attempt-Based Limits

| Limit | Value | Purpose |
|-------|-------|---------|
| `max_concurrent_tasks` | 3 | Per agent |
| `max_retry_attempts` | 3 | Before marking blocked |
| `max_fix_rounds` | 5 | Before escalating |

## Best Practices

### Before Autonomous Operation
1. Clear all blocking issues
2. Verify agent health
3. Run smoke tests
4. Confirm CI green

### During Autonomous Operation
1. Make conservative decisions
2. Document all choices
3. Prefer blocking over breaking
4. Merge only verified code

### After Autonomous Operation
1. Read completion report first
2. Address escalations
3. Complete in-progress tasks
4. Review agent performance
