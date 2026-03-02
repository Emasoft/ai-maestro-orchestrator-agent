# Progress Monitoring Protocol (Proactive Enforcement)


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 Proactive Monitoring Principles](#20-proactive-monitoring-principles)
- [3.0 Status Request Protocol](#30-status-request-protocol)
  - [3.1 Checking Agent Status (PROACTIVELY)](#31-checking-agent-status-proactively)
  - [3.2 Expected Update Events by Task Type](#32-expected-update-events-by-task-type)
  - [3.3 Proactive Status Request Timeline](#33-proactive-status-request-timeline)
- [4.0 Proactive Unblocking Protocol](#40-proactive-unblocking-protocol)
  - [4.1 When an Agent Reports Being Blocked](#41-when-an-agent-reports-being-blocked)
- [5.0 Task Completion Enforcement](#50-task-completion-enforcement)
  - [5.1 Verifying All Acceptance Criteria Are Met](#51-verifying-all-acceptance-criteria-are-met)
- [6.0 No Update Protocol (Proactive Escalation)](#60-no-update-protocol-proactive-escalation)
  - [6.1 Escalation Timeline When Agent Goes Silent](#61-escalation-timeline-when-agent-goes-silent)
- [7.0 Message Templates](#70-message-templates)
  - [7.1 Status Request Message](#71-status-request-message)
  - [7.2 Unblocking Assistance Message](#72-unblocking-assistance-message)
  - [7.3 Completion Verification Message](#73-completion-verification-message)
- [8.0 Troubleshooting](#80-troubleshooting)
  - [Problem: Agent Goes Silent During Task](#problem-agent-goes-silent-during-task)
  - [Problem: Agent Reports Progress But No Actual Work](#problem-agent-reports-progress-but-no-actual-work)
  - [Problem: Agent Keeps Reporting "Almost Done"](#problem-agent-keeps-reporting-almost-done)
  - [Problem: Agent Claims Complete But Acceptance Criteria Not Met](#problem-agent-claims-complete-but-acceptance-criteria-not-met)
  - [Problem: Proactive Checks Interrupt Agent's Flow](#problem-proactive-checks-interrupt-agents-flow)
  - [Problem: Multiple Blocked Agents Create Backlog](#problem-multiple-blocked-agents-create-backlog)
  - [Problem: Agent Unblocking Attempts Not Working](#problem-agent-unblocking-attempts-not-working)

---

## Table of Contents

- 1.0 Overview
- 1.1 When to proactively monitor agent progress
- 1.2 Why passive waiting is wrong
- 2.0 Proactive Monitoring Principles
- 2.1 Polling intervals by task type
- 2.2 When to send status request messages
- 3.0 Status Request Protocol
- 3.1 Sending proactive status request messages
- 3.2 Expected update events by task type
- 4.0 Proactive Unblocking Protocol
- 4.1 When an agent reports being blocked
- 4.2 Proposing solutions to blockers
- 4.3 Following up on unblocking attempts
- 5.0 Task Completion Enforcement
- 5.1 Verifying all acceptance criteria are met
- 5.2 Requesting completion reports with evidence
- 6.0 No Update Protocol (Proactive Escalation)
- 6.1 Escalation timeline when agent goes silent
- 6.2 Reassignment procedures
- 7.0 Message Templates
- 7.1 Status request message
- 7.2 Unblocking assistance message
- 7.3 Completion verification message

---

## 1.0 Overview

**CRITICAL**: The orchestrator must PROACTIVELY monitor implementer agents. Do not wait passively for updates - actively reach out to ensure progress and completion.

---

## 2.0 Proactive Monitoring Principles

1. **PROACTIVELY poll** for agent status every 10-15 minutes during active work
2. **PROACTIVELY send** status request messages using the `agent-messaging` skill if no update received
3. **PROACTIVELY offer** solutions when agents report blockers
4. **PROACTIVELY remind** agents of pending tasks (no arbitrary deadlines per RULE 13)
5. **PROACTIVELY verify** that agents don't stop until ALL tasks are complete

---

## 3.0 Status Request Protocol

### 3.1 Checking Agent Status (PROACTIVELY)

PROACTIVELY poll for updates from remote agents at regular intervals.

Check your inbox using the `agent-messaging` skill to retrieve any unread messages from remote agents.

**Verify**: confirm all unread messages have been processed.

### 3.2 Expected Update Events by Task Type

| Task Type | Update Trigger | Orchestrator PROACTIVE Check |
|-----------|----------------|------------------------------|
| Small fix | After each test cycle | Every 10 minutes |
| Feature | After each component completion | Every 15 minutes |
| Complex | After each milestone checkpoint | Every 20 minutes |
| Overnight | On completion or blocker encountered | Every 30 minutes |

### 3.3 Proactive Status Request Timeline

The orchestrator MUST PROACTIVELY request status updates:

**After task delegation:**
1. **Immediately** - Send ACK reminder after 5 minutes if no ACK
2. **Every 15 minutes** - Send status request if no update
3. **On any silence > 30 minutes** - Send escalated "Are you stuck?" message

---

## 4.0 Proactive Unblocking Protocol

### 4.1 When an Agent Reports Being Blocked

When an agent reports being blocked, the orchestrator MUST PROACTIVELY:

1. **Acknowledge immediately** (within 2 minutes)
2. **Analyze the blocker** - Is it technical, dependency, or unclear spec?
3. **Propose solutions** - Offer 2-3 concrete approaches
4. **Follow up** - Check if the solution worked within 10 minutes

---

## 5.0 Task Completion Enforcement

### 5.1 Verifying All Acceptance Criteria Are Met

The orchestrator MUST PROACTIVELY ensure implementers don't stop prematurely:

1. **PROACTIVELY verify** all acceptance criteria are met before allowing PR
2. **PROACTIVELY request** completion reports with evidence
3. **PROACTIVELY check** that tests pass before accepting "done" status
4. **PROACTIVELY remind** agents of any missed items

---

## 6.0 No Update Protocol (Proactive Escalation)

### 6.1 Escalation Timeline When Agent Goes Silent

If no update received after expected checkpoint:

1. **IMMEDIATELY** - Send status-request message using the `agent-messaging` skill (don't wait)
2. **After 5 minutes** - Send follow-up with increased urgency
3. **After 10 minutes** - Send "Are you stuck? I can help" message
4. **After 15 minutes** - Mark agent as potentially offline, prepare reassignment
5. **After 20 minutes** - Reassign task if critical, log for user review

---

## 7.0 Message Templates

### 7.1 Status Request Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "STATUS REQUEST: {task_id}",
  "priority": "high",
  "content": {
    "type": "status-request",
    "task_id": "GH-XX",
    "message": "PROACTIVE CHECK: Please provide current status on task {task_id}.\n\n1. What have you completed so far?\n2. What are you currently working on?\n3. Are you blocked on anything?\n4. What remaining steps do you see? (per RULE 13 - no time estimates)\n\nIf you're stuck, describe the issue and I will help find a solution."
  }
}
```

### 7.2 Unblocking Assistance Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "HELP: Solution for blocker in {task_id}",
  "priority": "urgent",
  "content": {
    "type": "unblock-assistance",
    "task_id": "GH-XX",
    "message": "I see you're blocked on {blocker_description}.\n\nHere are proposed solutions:\n\n1. {solution_1}\n2. {solution_2}\n3. {solution_3}\n\nTry solution 1 first. If it doesn't work, move to solution 2.\n\nReport back in 10 minutes with results."
  }
}
```

### 7.3 Completion Verification Message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "COMPLETION CHECK: {task_id}",
  "priority": "high",
  "content": {
    "type": "completion-verification",
    "task_id": "GH-XX",
    "message": "Before you stop work on {task_id}, please confirm:\n\n1. [ ] All acceptance criteria met\n2. [ ] All tests pass locally\n3. [ ] Code follows project style\n4. [ ] PR description complete\n5. [ ] No TODO comments left in code\n\nDo NOT stop until ALL items are checked."
  }
}
```

---

## 8.0 Troubleshooting

### Problem: Agent Goes Silent During Task

**Symptoms**: No status updates received, agent not responding to polls.

**Solution**:
1. Send immediate status request with `urgent` priority
2. Wait 5 minutes, then send "Are you stuck?" message
3. Check AI Maestro for agent online status
4. If agent appears offline, mark task as orphaned
5. Reassign task if no response after 20 minutes

### Problem: Agent Reports Progress But No Actual Work

**Symptoms**: Agent sends progress updates but code/commits show no changes.

**Solution**:
1. Ask for specific evidence: file names modified, test results
2. Request screenshot or log output
3. Check git log for commits from agent
4. If agent cannot provide evidence, investigate blockers directly
5. Consider agent may be stuck but not admitting it - offer help proactively

### Problem: Agent Keeps Reporting "Almost Done"

**Symptoms**: Multiple progress updates say 90%+ complete but no completion.

**Solution**:
1. Ask for specific remaining steps (not percentage)
2. Break down "remaining 10%" into concrete subtasks
3. Set checkpoint for each subtask
4. If pattern continues, task may have hidden complexity - reassess scope
5. Consider pairing agent with another agent for review

### Problem: Agent Claims Complete But Acceptance Criteria Not Met

**Symptoms**: Agent says task is done, but verification shows missing requirements.

**Solution**:
1. Send completion verification checklist with specific criteria
2. Quote the exact criteria that are not met
3. Do NOT approve PR until all criteria verified
4. If agent disputes criteria, escalate to user for clarification
5. Document discrepancy in GitHub Issue

### Problem: Proactive Checks Interrupt Agent's Flow

**Symptoms**: Agent complains that frequent status requests break concentration.

**Solution**:
1. Adjust polling interval based on task complexity (longer for complex tasks)
2. Allow agent to set "do not disturb" window with automatic resume
3. Request brief ACK instead of full status update
4. Use passive monitoring (git commits, CI status) instead of active polling when possible

### Problem: Multiple Blocked Agents Create Backlog

**Symptoms**: Several agents blocked simultaneously, orchestrator overwhelmed.

**Solution**:
1. Triage blockers by impact - unblock critical path first
2. Escalate common blockers to user immediately
3. Group similar blockers for batch resolution
4. Consider if blocker pattern indicates systemic issue
5. Reassign non-critical tasks to reduce active workload

### Problem: Agent Unblocking Attempts Not Working

**Symptoms**: Orchestrator provides solutions but agent remains blocked.

**Solution**:
1. Request detailed explanation of why solution didn't work
2. Try alternative approaches (2-3 options)
3. If technical blocker, consider reassigning to agent with different expertise
4. If external dependency, escalate to user for external action
5. Document all attempted solutions in GitHub Issue for future reference

---

## Verification

After completing each monitoring cycle:

- [ ] **Verify**: confirm all status request messages were delivered via the `agent-messaging` skill's sent messages feature
- [ ] **Verify**: confirm agent responses were received and processed within expected timeframes
- [ ] **Verify**: confirm any escalation messages reached ECOS or EAMA successfully
- [ ] **Verify**: confirm kanban board reflects current task statuses accurately
