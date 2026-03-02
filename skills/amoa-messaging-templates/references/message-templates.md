# Message Templates by Scenario

This document provides the complete AI Maestro message templates for all common agent communication scenarios across emasoft plugins.

> All message templates below should be sent using the `agent-messaging` skill, which handles the AI Maestro API format automatically.

## Table of Contents

- [2.1 Task Assignment (EOA → Remote Agent)](#21-task-assignment-eoa--remote-agent)
- [2.2 Task Completion Report (Agent → EOA)](#22-task-completion-report-agent--eoa)
- [2.3 Status Request (EOA → Agent)](#23-status-request-eoa--agent)
- [2.4 Status Response (Agent → EOA)](#24-status-response-agent--eoa)
- [2.5 Approval Request (ECOS → EAMA)](#25-approval-request-ecos--eama)
- [2.6 Approval Response (EAMA → ECOS)](#26-approval-response-eama--ecos)
- [2.7 Escalation (Any Agent → ECOS/EAMA)](#27-escalation-any-agent--ecoseama)
- [2.8 Acknowledgment (Any Agent)](#28-acknowledgment-any-agent)
- [2.9 Design Handoff (EAA → EOA)](#29-design-handoff-eaa--eoa)
- [2.10 Integration Request (EOA → EIA)](#210-integration-request-eoa--eia)
- [2.11 Integration Result (EIA → EOA)](#211-integration-result-eia--eoa)

---

## 2.1 Task Assignment (EOA → Remote Agent)

**When to use:** EOA assigning implementation task to remote agent

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Assignment: <task-title>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "You are assigned: <task-description>. Success criteria: <criteria>. Report status when starting and when complete.",
    "data": {
      "task_id": "<task-id>",
      "issue_number": "<github-issue-number>",
      "handoff_doc": "docs_dev/handoffs/<handoff-filename>.md"
    }
  }
}
```

---

## 2.2 Task Completion Report (Agent → EOA)

**When to use:** Agent reporting task completion to orchestrator

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "Task Complete: <task-title>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "[DONE] <task-id> - <brief-result>. Details: <output-location>",
    "data": {
      "task_id": "<task-id>",
      "status": "complete",
      "output_file": "docs_dev/reports/<report-filename>.md"
    }
  }
}
```

---

## 2.3 Status Request (EOA → Agent)

**When to use:** Orchestrator polling agent for status

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Status Request: <task-id>",
  "priority": "normal",
  "content": {
    "type": "request",
    "message": "What is your current status on <task-id>? Report progress, blockers, and next steps.",
    "data": {
      "task_id": "<task-id>"
    }
  }
}
```

---

## 2.4 Status Response (Agent → EOA)

**When to use:** Agent responding to status request

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "Status: <task-id>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "[IN_PROGRESS] <task-id> - <progress-description>. Blockers: <none|blocker-list>. Next: <next-step>",
    "data": {
      "task_id": "<task-id>",
      "status": "in-progress",
      "progress_percent": 60,
      "blockers": []
    }
  }
}
```

---

## 2.5 Approval Request (ECOS → EAMA)

**When to use:** Chief of Staff requesting approval from Assistant Manager

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "chief-of-staff",
  "to": "assistant-manager",
  "subject": "Approval Required: <operation-type>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Requesting approval to <operation-description>. Risk level: <low|medium|high>. Justification: <reason>",
    "data": {
      "operation": "<spawn|terminate|hibernate|wake>",
      "target": "<agent-name>",
      "risk_level": "medium",
      "justification": "<reason>"
    }
  }
}
```

---

## 2.6 Approval Response (EAMA → ECOS)

**When to use:** Assistant Manager responding to approval request

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "assistant-manager",
  "to": "chief-of-staff",
  "subject": "Approval Decision: <operation-type>",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "<APPROVED|REJECTED>: <operation-description>. <rationale>",
    "data": {
      "decision": "approved|rejected",
      "operation": "<operation-type>",
      "rationale": "<reason>"
    }
  }
}
```

---

## 2.7 Escalation (Any Agent → ECOS/EAMA)

**When to use:** Agent encountering blocker requiring escalation

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<agent-name>",
  "to": "chief-of-staff",
  "subject": "Escalation: <issue-summary>",
  "priority": "high",
  "content": {
    "type": "notification",
    "message": "Escalating: <issue-description>. Attempted: <what-was-tried>. Need: <what-is-needed>",
    "data": {
      "task_id": "<task-id>",
      "blocker_type": "<technical|resource|approval|external>",
      "attempted_solutions": ["<solution-1>", "<solution-2>"],
      "required_action": "<what-is-needed>"
    }
  }
}
```

---

## 2.8 Acknowledgment (Any Agent)

**When to use:** Acknowledging receipt of message

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "<agent-name>",
  "to": "<sender-name>",
  "subject": "ACK: <original-subject>",
  "priority": "low",
  "content": {
    "type": "acknowledgment",
    "message": "Received and understood. Will <action>.",
    "data": {
      "original_subject": "<original-subject>",
      "action_planned": "<what-agent-will-do>"
    }
  }
}
```

---

## 2.9 Design Handoff (EAA → EOA)

**When to use:** Architect handing off design to Orchestrator

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "architect",
  "to": "orchestrator",
  "subject": "Design Complete: <project-name>",
  "priority": "high",
  "content": {
    "type": "notification",
    "message": "Architecture design complete for <project-name>. Handoff document ready. Modules: <count>. Ready for implementation planning.",
    "data": {
      "handoff_doc": "docs_dev/design/handoffs/<handoff-id>.md",
      "architecture_doc": "docs_dev/design/architecture.md",
      "module_count": 5,
      "adr_count": 3
    }
  }
}
```

---

## 2.10 Integration Request (EOA → EIA)

**When to use:** Orchestrator requesting code integration/review

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "orchestrator",
  "to": "integrator",
  "subject": "Integration Request: PR #<pr-number>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Review and verify PR #<pr-number>: <pr-title>. Run full verification workflow. Report pass/fail with details.",
    "data": {
      "pr_number": 123,
      "pr_url": "https://github.com/owner/repo/pull/123",
      "request_type": "full_verification"
    }
  }
}
```

---

## 2.11 Integration Result (EIA → EOA)

**When to use:** Integrator reporting integration/review result

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "integrator",
  "to": "orchestrator",
  "subject": "Integration Result: PR #<pr-number>",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "[<PASS|FAIL>] PR #<pr-number>. <summary>. Details: <report-location>",
    "data": {
      "pr_number": 123,
      "result": "pass|fail",
      "ci_status": "passing",
      "review_status": "approved",
      "report_file": "docs_dev/integration/reports/pr-123-verification.md"
    }
  }
}
```

---

## Decision Trees for Core Message Templates

The following decision trees show the exact branching logic EOA follows when sending or receiving the most common message types. Each leaf node references the appropriate template from the sections above.

### Task Assignment Decision Tree

**When EOA needs to assign a task to an agent:**

```
Task assignment needed
├─ Is agent registered in AI Maestro?
│   ├─ Yes → Is agent currently idle (no in-progress tasks)?
│   │         ├─ Yes → Does task conflict with agent's other assigned files?
│   │         │         ├─ No conflict → Send Task Assignment (template 2.1) → Wait for ACK
│   │         │         │                 ├─ ACK received within 2 min → Mark task "in-progress" on kanban
│   │         │         │                 └─ No ACK within 2 min → Retry once → Still no ACK → Escalate to ECOS
│   │         │         └─ Conflict detected → Choose different agent or wait for current task to complete
│   │         └─ No (agent busy) → Is task priority higher than current task?
│   │                               ├─ Yes (urgent) → Send Priority Override message → Reassign current task
│   │                               └─ No → Queue task, assign when agent becomes available
│   └─ No → Request ECOS to spawn new agent for this task
```

### Task Completion Report Decision Tree

**When EOA receives a completion report from an agent:**

```
Completion report received from agent
├─ Does report include all required fields (task_id, summary, files_changed, tests_passed)?
│   ├─ Yes → Do self-reported tests show 100% pass rate?
│   │         ├─ Yes → Are all checklist items marked complete?
│   │         │         ├─ Yes → Move task to "ai-review" on kanban → Send Integration Request to EIA
│   │         │         │         ├─ EIA accepts → Move to "merge-release" → Notify ECOS
│   │         │         │         └─ EIA rejects → Send Rework Assignment (template 2.7) back to agent
│   │         │         └─ No (incomplete checklist) → Send Clarification Request (template 2.6) to agent
│   │         └─ No (test failures) → Send Rework Assignment with failure details → Agent retries
│   └─ No (missing fields) → Send Clarification Request listing missing fields → Agent resubmits
```

### Status Request/Response Decision Tree

**When EOA polls agents for status:**

```
Scheduled status check (every 15 min per active agent)
├─ Send Status Request (template 2.3) to agent
│   ├─ Response received within 3 min → Parse progress percentage
│   │   ├─ Progress > 0% since last check → Log progress, continue monitoring
│   │   ├─ Progress = 0% (stalled) → Is this the 2nd consecutive stall?
│   │   │                             ├─ Yes → Send direct inquiry about blockers
│   │   │                             │         ├─ Blocker reported → Triage blocker (see escalation-procedures.md)
│   │   │                             │         └─ No blocker, just slow → Allow one more cycle, then escalate
│   │   │                             └─ No (first stall) → Log warning, check again next cycle
│   │   └─ Agent reports blocker → Triage immediately (see escalation-procedures.md)
│   └─ No response within 3 min → Retry once after 2 min
│       ├─ Second attempt succeeds → Process response as above
│       └─ Second attempt fails → Mark agent as unresponsive → Escalate to ECOS
```
