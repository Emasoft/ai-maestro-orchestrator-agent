# Progress Monitoring (PROACTIVE ENFORCEMENT)


## Contents

- [Table of Contents](#table-of-contents)
- [1. Proactive Monitoring Principles](#1-proactive-monitoring-principles)
  - [1.1 Why Proactive Monitoring is Critical](#11-why-proactive-monitoring-is-critical)
  - [1.2 The Five Proactive Principles](#12-the-five-proactive-principles)
- [2. PROACTIVE Status Request Protocol](#2-proactive-status-request-protocol)
  - [2.1 When to Send Status Requests](#21-when-to-send-status-requests)
  - [2.2 Status Request Message Template](#22-status-request-message-template)
- [3. PROACTIVE Unblocking Protocol](#3-proactive-unblocking-protocol)
  - [3.1 When an Agent Reports a Blocker](#31-when-an-agent-reports-a-blocker)
  - [3.2 Unblocking Response Template](#32-unblocking-response-template)
- [4. PROACTIVE Task Completion Enforcement](#4-proactive-task-completion-enforcement)
  - [4.1 Before Allowing Agent to Stop](#41-before-allowing-agent-to-stop)
  - [4.2 Verification Requirements](#42-verification-requirements)
- [Troubleshooting](#troubleshooting)
  - [Agent Not Responding to Status Requests](#agent-not-responding-to-status-requests)
  - [Agent Reports Same Blocker Repeatedly](#agent-reports-same-blocker-repeatedly)
  - [Agent Claims Completion But Evidence Missing](#agent-claims-completion-but-evidence-missing)
- [See Also](#see-also)

---

## Table of Contents

- 1. Proactive Monitoring Principles
  - 1.1 Why Proactive Monitoring is Critical
  - 1.2 The Five Proactive Principles
- 2. PROACTIVE Status Request Protocol
  - 2.1 When to Send Status Requests
  - 2.2 Status Request Message Template
- 3. PROACTIVE Unblocking Protocol
  - 3.1 When an Agent Reports a Blocker
  - 3.2 Unblocking Response Template
- 4. PROACTIVE Task Completion Enforcement
  - 4.1 Before Allowing Agent to Stop
  - 4.2 Verification Requirements

---

## 1. Proactive Monitoring Principles

### 1.1 Why Proactive Monitoring is Critical

The orchestrator MUST PROACTIVELY monitor implementer agents. Do not wait passively for updates - actively reach out to ensure progress and completion.

Passive monitoring leads to:
- Agents getting stuck without reporting
- Tasks incomplete without notification
- Problems discovered too late to fix
- Wasted orchestrator context waiting

### 1.2 The Five Proactive Principles

1. **PROACTIVELY poll** for agent status every 10-15 minutes during active work
2. **PROACTIVELY send** status request messages using the `agent-messaging` skill if no update received
3. **PROACTIVELY offer** solutions when agents report blockers
4. **PROACTIVELY remind** agents of pending tasks and priorities
5. **PROACTIVELY verify** that agents don't stop until ALL tasks are complete

---

## 2. PROACTIVE Status Request Protocol

### 2.1 When to Send Status Requests

Send a status request when an implementer has been silent for more than 15 minutes.

**Triggers for status request:**
- No message received in 15+ minutes
- Agent marked task as "in progress" but no update
- Expected deliverable time has passed
- Other dependent tasks are waiting

### 2.2 Status Request Message Template

Use this template when requesting status:

```
PROACTIVE STATUS REQUEST:

[AGENT_NAME], I'm checking on your progress:

Current task: [TASK_DESCRIPTION]
Expected deliverable: [DELIVERABLE]
Time since last update: [TIME]

Please respond with:
1. Current status (working/blocked/complete)
2. What you've accomplished so far
3. Any blockers or issues
4. Estimated time to completion

If you're blocked, I can help unblock you.
```

---

## 3. PROACTIVE Unblocking Protocol

### 3.1 When an Agent Reports a Blocker

When an agent reports being blocked, respond IMMEDIATELY with solutions. Do not wait for the agent to figure it out alone.

**Blocker categories and typical solutions:**

| Blocker Type | Immediate Action |
|--------------|------------------|
| Missing dependency | Provide install command |
| API not responding | Provide alternative endpoint or test command |
| Permission denied | Escalate to user for access |
| Unclear specification | Provide clarification immediately |
| Code conflict | Provide merge resolution guidance |

### 3.2 Unblocking Response Template

Use this template when responding to blockers:

```
PROACTIVE UNBLOCKING RESPONSE:

I see you're blocked on: [BLOCKER_DESCRIPTION]

Proposed solution:
[SOLUTION_1]
[SOLUTION_2]
[ALTERNATIVE_APPROACH]

Try the proposed solution. If it doesn't work, report back immediately and I'll provide additional guidance.

Do NOT wait passively - try the solution now and report results.
```

---

## 4. PROACTIVE Task Completion Enforcement

### 4.1 Before Allowing Agent to Stop

When an agent indicates they want to stop, BEFORE allowing it:

1. **PROACTIVELY verify** all assigned tasks are complete
2. **PROACTIVELY request** evidence of completion (test results, build logs)
3. **PROACTIVELY challenge** any incomplete work
4. **PROACTIVELY require** 4 verification loops before PR (see verification-loops.md)

### 4.2 Verification Requirements

An agent may only stop when:

| Condition | Evidence Required |
|-----------|-------------------|
| Task complete | Test results passing |
| Code committed | Git log showing commit |
| PR ready | PR URL provided |
| Documentation updated | Diff showing changes |
| No outstanding issues | Issue tracker shows none |

If any condition is not met, send:

```
COMPLETION VERIFICATION FAILED:

You indicated completion, but I cannot verify:
- [MISSING_CONDITION_1]
- [MISSING_CONDITION_2]

Please provide evidence of completion or continue working until complete.
Do NOT stop until all conditions are verified.
```

---

## Troubleshooting

### Agent Not Responding to Status Requests

If an agent does not respond after 2 status requests:
1. Wait 5 more minutes
2. Send a third request with URGENT prefix
3. If still no response, escalate to user
4. Consider agent may be stuck in blocking operation

### Agent Reports Same Blocker Repeatedly

If an agent reports the same blocker more than twice:
1. The provided solutions are not working
2. Escalate to user for alternative approaches
3. Consider reassigning task to different agent
4. Document the blocker for future reference

### Agent Claims Completion But Evidence Missing

If agent claims completion but cannot provide evidence:
1. Do NOT approve PR or task closure
2. Request specific evidence items
3. If evidence not provided after 2 requests, mark task as incomplete
4. Escalate to user for verification

---

## See Also

- [verification-loops.md](verification-loops.md) - 4-verification-loops before PR
- [agent-selection-guide.md](agent-selection-guide.md) - Which agent for which task
- [orchestrator-guardrails.md](orchestrator-guardrails.md) - Orchestrator role boundaries
