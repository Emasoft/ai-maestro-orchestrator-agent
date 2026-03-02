# Reassignment Communication Templates

This document provides complete message templates for the full reassignment flow when an agent is replaced or reassigned to a different task. Each section covers one step of the reassignment protocol, including the message to send, the expected response, and a decision tree for handling outcomes.

---

## Table of Contents

- 1. Reassignment Notification to Old Agent (EOA to Old Agent)
  - 1.1 When to send a reassignment notification
  - 1.2 Reassignment notification message template
  - 1.3 Expected acknowledgment from old agent
  - 1.4 Decision tree for reassignment notification outcomes
- 2. Old Agent Work Summary Response (Old Agent to EOA)
  - 2.1 When to expect a work summary response
  - 2.2 Work summary response message template
  - 2.3 Work summary data fields explained
  - 2.4 Decision tree for work summary outcomes
- 3. Reassignment Assignment to New Agent (EOA to New Agent)
  - 3.1 When to send a reassignment assignment
  - 3.2 Reassignment assignment message template
  - 3.3 Expected acknowledgment from new agent
  - 3.4 Decision tree for new agent assignment outcomes
- 4. Agent Recovery Decision Notification (EOA to Both Agents)
  - 4.1 When a recovery decision notification is needed
  - 4.2 Recovery decision notification message template
  - 4.3 Graceful stop message template for removed agent
  - 4.4 Continuation confirmation message template for kept agent
  - 4.5 Decision tree for recovery decision outcomes
- 5. EOA Response to Agent Recovery Decision
  - 5.1 When EOA must respond to ECOS recovery report
  - 5.2 EOA response to keep replacement agent template
  - 5.3 EOA response to revert to original agent template
  - 5.4 Decision tree for EOA recovery response
- 6. Reassignment Flow Decision Tree
  - 6.1 Complete reassignment decision tree
  - 6.2 Timeout thresholds reference

---

## 1. Reassignment Notification to Old Agent (EOA to Old Agent)

### 1.1 When to send a reassignment notification

Send this message when the Orchestrator (EOA) decides to remove an agent from a task and replace it with a different agent. Reasons for reassignment include performance issues, agent unavailability, skill mismatch between the agent and the task requirements, or changing project needs that require a different agent profile.

> **Note**: Use the agent-messaging skill to send messages.

### 1.2 Reassignment notification message template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "<old-agent-session-name>",
  "subject": "[REASSIGN] Task <task-uuid> - You Are Being Reassigned",
  "priority": "high",
  "content": {
    "type": "reassignment_notification",
    "message": "You are being removed from task <task-uuid>. Reason: <reason>. Please provide a complete work summary within the deadline specified below. If handoff_required is true, you must also prepare a handoff document at docs_dev/handoffs/ before the deadline.",
    "data": {
      "task_id": "<task-uuid>",
      "reason": "<performance|availability|skill_mismatch|project_needs>",
      "handoff_required": true,
      "deadline_for_summary": "<ISO-8601-timestamp>"
    }
  }
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | The unique identifier (UUID) of the task being reassigned |
| `reason` | string | One of: `performance` (agent not meeting quality or speed targets), `availability` (agent session crashed or is unreachable), `skill_mismatch` (task requires capabilities the agent lacks), `project_needs` (strategic reallocation of resources) |
| `handoff_required` | boolean | If `true`, the old agent must prepare a handoff document at `docs_dev/handoffs/` containing all context, files, and decisions. If `false`, only the work summary message is required |
| `deadline_for_summary` | string | An ISO 8601 timestamp (for example `2026-02-08T15:00:00Z`) by which the old agent must respond with its work summary. If no response is received by this deadline, the reassignment proceeds with partial context |

### 1.3 Expected acknowledgment from old agent

The old agent should respond with a brief acknowledgment and then follow up with the full work summary (see Section 2):

```json
{
  "from": "<old-agent-session-name>",
  "to": "eoa-orchestrator-main-agent",
  "subject": "[ACK] Reassignment Notification Received - Task <task-uuid>",
  "priority": "high",
  "content": {
    "type": "ack",
    "message": "Acknowledged reassignment from task <task-uuid>. I will provide a full work summary by <deadline>. Handoff document will be prepared at docs_dev/handoffs/."
  }
}
```

### 1.4 Decision tree for reassignment notification outcomes

```
Send reassignment notification to old agent
├─ Old agent responds with ACK within 5 minutes
│   ├─ ACK confirms summary will be provided by deadline
│   │   └─ WAIT for work summary (proceed to Section 2)
│   └─ ACK raises concerns or questions
│       └─ ADDRESS concerns, then WAIT for work summary
├─ Old agent does not respond within 5 minutes
│   ├─ RETRY notification once (resend with urgent priority)
│   │   ├─ Response received on retry
│   │   │   └─ WAIT for work summary (proceed to Section 2)
│   │   └─ No response on retry
│   │       └─ MARK agent as unresponsive, proceed to Section 6
│   │          (assign new agent with partial or reconstructed context)
└─ Old agent responds with error or refusal
    └─ ESCALATE to ECOS for agent status investigation
       PROCEED with reassignment using available context
```

---

## 2. Old Agent Work Summary Response (Old Agent to EOA)

### 2.1 When to expect a work summary response

After the old agent acknowledges the reassignment notification, it should provide a structured work summary before the deadline specified in the notification. This summary contains all information the new agent will need to continue the work.

> **Note**: Use the agent-messaging skill to send messages.

### 2.2 Work summary response message template

```json
{
  "from": "<old-agent-session-name>",
  "to": "eoa-orchestrator-main-agent",
  "subject": "[SUMMARY] Work Summary for Task <task-uuid>",
  "priority": "high",
  "content": {
    "type": "work_summary",
    "message": "Here is my complete work summary for task <task-uuid>. Progress is at <percentage>%. All modified files, pull requests, blockers, uncommitted work location, and planned next steps are included in the data section below.",
    "data": {
      "task_id": "<task-uuid>",
      "progress_percentage": 45,
      "files_modified": [
        "src/auth/token_manager.py",
        "src/auth/refresh_handler.py",
        "tests/test_token_manager.py"
      ],
      "prs_created": [
        "https://github.com/org/repo/pull/42"
      ],
      "blockers": [
        "Redis connection timeout in CI environment - see issue #78"
      ],
      "uncommitted_work": "docs_dev/wip/task-uuid-uncommitted/",
      "notes": "The token refresh logic is 80% complete. The remaining work involves error retry logic and integration tests. I chose RS256 over HS256 per the user requirement in issue #35."
    }
  }
}
```

### 2.3 Work summary data fields explained

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | The unique identifier of the task, must match the original assignment |
| `progress_percentage` | integer | Estimated completion percentage from 0 to 100 |
| `files_modified` | array of strings | Full relative paths of every file the agent created, modified, or deleted during the task |
| `prs_created` | array of strings | Full URLs to any pull requests the agent opened on GitHub |
| `blockers` | array of strings | Description of each issue that is blocking or was blocking progress, including references to GitHub issues if applicable |
| `uncommitted_work` | string | Path to the directory where any uncommitted or work-in-progress files have been saved. The agent must push or copy uncommitted work here before the deadline |
| `notes` | string | Free-form text explaining technical decisions made, approaches tried (including failed ones), and any other context the new agent would need |

### 2.4 Decision tree for work summary outcomes

```
Wait for work summary from old agent
├─ Summary received before deadline
│   ├─ Summary is complete (all fields populated)
│   │   └─ CREATE handoff document from summary
│   │      PROCEED to assign new agent (Section 3)
│   ├─ Summary is partial (some fields empty or missing)
│   │   ├─ Missing fields are critical (files_modified or progress_percentage)
│   │   │   └─ REQUEST missing fields from old agent (5 minute deadline)
│   │   │       ├─ Old agent provides missing fields
│   │   │       │   └─ CREATE handoff document, PROCEED to Section 3
│   │   │       └─ Old agent does not respond
│   │   │           └─ RECONSTRUCT missing context from git log and GitHub
│   │   │              PROCEED to Section 3 with partial context, NOTE the gap
│   │   └─ Missing fields are non-critical (notes or prs_created)
│   │       └─ CREATE handoff document with available data
│   │          PROCEED to Section 3, NOTE missing fields
│   └─ Summary data appears incorrect or contradictory
│       └─ VERIFY against git log and GitHub issues
│          USE verified data for handoff, DISCARD contradictions
│          PROCEED to Section 3
├─ Summary NOT received by deadline (more than 15 minutes past deadline)
│   └─ MARK old agent as non-responsive for summary
│      RECONSTRUCT context from version control and GitHub
│      PROCEED to Section 3 with reconstructed context, NOTE the gap
└─ Old agent reports inability to provide summary (for example, lost context)
    └─ ACKNOWLEDGE the limitation
       RECONSTRUCT from git commits, PR descriptions, GitHub issue comments
       PROCEED to Section 3 with reconstructed context
```

---

## 3. Reassignment Assignment to New Agent (EOA to New Agent)

### 3.1 When to send a reassignment assignment

Send this message after receiving and processing the old agent's work summary (or after reconstructing context if the old agent was unresponsive). This message gives the new agent everything it needs to continue the task from where the old agent stopped.

> **Note**: Use the agent-messaging skill to send messages.

### 3.2 Reassignment assignment message template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "<new-agent-session-name>",
  "subject": "[TASK] Reassignment - Continue Task <task-uuid>",
  "priority": "high",
  "content": {
    "type": "reassignment_assignment",
    "message": "You are being assigned to continue task <task-uuid>, previously worked on by <old-agent-session-name>. The previous agent reached <progress_percentage>% completion. Review the previous agent summary and handoff document carefully before starting. Known blockers are listed below. You MUST complete the Instruction Verification Protocol: read the handoff, confirm your understanding, and identify any gaps before beginning work.",
    "data": {
      "original_task_id": "<task-uuid>",
      "previous_agent_summary": {
        "progress_percentage": 45,
        "files_modified": [
          "src/auth/token_manager.py",
          "src/auth/refresh_handler.py",
          "tests/test_token_manager.py"
        ],
        "prs_created": [
          "https://github.com/org/repo/pull/42"
        ],
        "blockers": [
          "Redis connection timeout in CI environment - see issue #78"
        ],
        "uncommitted_work": "docs_dev/wip/task-uuid-uncommitted/",
        "notes": "The token refresh logic is 80% complete. The remaining work involves error retry logic and integration tests. I chose RS256 over HS256 per the user requirement in issue #35."
      },
      "continue_from": "Token refresh error retry logic and integration tests. The core token generation and validation is complete and tested. Start by reviewing src/auth/token_manager.py and the existing tests.",
      "known_blockers": [
        "Redis connection timeout in CI - may need CI environment variable fix"
      ],
      "handoff_doc": "docs_dev/handoffs/handoff-task-uuid-old-agent-to-new-agent.md"
    }
  }
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `original_task_id` | string | The task UUID, preserved from the original assignment so all tracking remains consistent |
| `previous_agent_summary` | object | The complete work summary received from the old agent (see Section 2.3 for field details). If the old agent was unresponsive, this contains the reconstructed context instead |
| `continue_from` | string | A human-readable description of exactly where to pick up the work. This should specify the next concrete action the new agent should take |
| `known_blockers` | array of strings | All known blockers, both those reported by the old agent and any discovered during context reconstruction |
| `handoff_doc` | string | Path to the full handoff document containing verbatim requirements, technical decisions, integration points, and all other context. The new agent must read this document before starting work |

### 3.3 Expected acknowledgment from new agent

```json
{
  "from": "<new-agent-session-name>",
  "to": "eoa-orchestrator-main-agent",
  "subject": "[ACK] Reassignment Accepted - Task <task-uuid>",
  "priority": "high",
  "content": {
    "type": "ack",
    "message": "Accepted reassignment for task <task-uuid>. I have read the handoff document at <handoff_doc_path>. My understanding: <brief-summary-of-requirements>. I will continue from: <continue_from_description>. Questions: <questions-or-none>."
  }
}
```

### 3.4 Decision tree for new agent assignment outcomes

```
Send reassignment assignment to new agent
├─ New agent responds with ACK within 10 minutes
│   ├─ ACK confirms understanding (summary is accurate)
│   │   ├─ No questions raised
│   │   │   └─ AUTHORIZE new agent to begin work
│   │   │      NOTIFY old agent of release (Section 4 graceful stop)
│   │   │      UPDATE kanban board with new assignee
│   │   └─ Questions raised but non-blocking
│   │       └─ ANSWER questions
│   │          AUTHORIZE new agent to begin work
│   │          UPDATE kanban board
│   ├─ ACK shows misunderstanding (summary does not match requirements)
│   │   └─ SEND correction message (use Verification Request template)
│   │      WAIT for revised understanding
│   │      REPEAT until understanding verified
│   └─ ACK rejects the assignment (agent reports inability to continue)
│       └─ TRY assigning to another available agent
│          ├─ Another agent available
│          │   └─ REPEAT Section 3 with the new candidate agent
│          └─ No other agents available
│              └─ ESCALATE to ECOS requesting a new agent be spawned
├─ New agent does not respond within 10 minutes
│   ├─ RETRY once with urgent priority
│   │   ├─ Response received
│   │   │   └─ PROCESS as above
│   │   └─ No response
│   │       └─ MARK new agent as unresponsive
│   │          ESCALATE to ECOS for agent health check
│   │          REQUEST alternative agent from ECOS
└─ New agent responds with error
    └─ DIAGNOSE error (missing handoff doc, unreadable path, etc.)
       FIX issue and RESEND assignment
```

---

## 4. Agent Recovery Decision Notification (EOA to Both Agents)

### 4.1 When a recovery decision notification is needed

This notification is needed when ECOS reports that the original agent (the one that was replaced) has recovered and is available again. The Orchestrator must decide whether to keep the replacement agent on the task or revert to the original agent. This decision is then communicated to both agents: the agent being removed receives a graceful stop message, and the agent continuing receives a confirmation.

> **Note**: Use the agent-messaging skill to send messages.

### 4.2 Recovery decision notification message template

Send this to both agents simultaneously. The `decision` field tells each agent what happens next.

**Message to both agents:**

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "<both-agent-session-names>",
  "subject": "[RECOVERY] Agent Recovery Decision - Task <task-uuid>",
  "priority": "high",
  "content": {
    "type": "recovery_decision",
    "message": "The original agent <original-agent-session-name> has recovered and is available. After evaluating progress and context, the decision is: <decision>. Reason: <reason>. See handoff_instructions for your specific next action.",
    "data": {
      "task_id": "<task-uuid>",
      "decision": "<keep_replacement|revert_to_original>",
      "reason": "<explanation of why this decision was made>",
      "handoff_instructions": "<specific instructions for the agent receiving this message>"
    }
  }
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `decision` | string | Either `keep_replacement` (the replacement agent continues, original agent is released) or `revert_to_original` (the original agent resumes, replacement agent is released) |
| `reason` | string | Explanation of the decision. For example: "Replacement agent is 80% complete and switching back would lose progress" or "Original agent has critical domain context that cannot be transferred" |
| `handoff_instructions` | string | Specific instructions for the receiving agent. For the agent being kept: "Continue work as assigned." For the agent being removed: "Provide final work summary and prepare handoff document." |

### 4.3 Graceful stop message template for removed agent

Send this to whichever agent is being removed from the task (either the original or the replacement, depending on the decision):

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "<removed-agent-session-name>",
  "subject": "[STOP] Graceful Release from Task <task-uuid>",
  "priority": "normal",
  "content": {
    "type": "graceful_stop",
    "message": "You are being released from task <task-uuid>. Decision: <decision>. Please complete the following before stopping: 1) Push all uncommitted work to a branch or copy to docs_dev/wip/. 2) Provide a final brief status summary. 3) Confirm you have stopped work on this task. Thank you for your contribution.",
    "data": {
      "task_id": "<task-uuid>",
      "decision": "<keep_replacement|revert_to_original>",
      "reason": "<explanation>"
    }
  }
}
```

### 4.4 Continuation confirmation message template for kept agent

Send this to the agent that will continue working on the task:

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "<continuing-agent-session-name>",
  "subject": "[CONFIRMED] Continue Task <task-uuid>",
  "priority": "normal",
  "content": {
    "type": "continuation_confirmation",
    "message": "You are confirmed to continue working on task <task-uuid>. The other agent has been notified and will provide a final summary. If the decision was revert_to_original and you are the original agent, check the handoff document for work completed during your absence. Proceed with your assignment.",
    "data": {
      "task_id": "<task-uuid>",
      "decision": "<keep_replacement|revert_to_original>",
      "handoff_doc": "docs_dev/handoffs/handoff-task-uuid-recovery-decision.md"
    }
  }
}
```

### 4.5 Decision tree for recovery decision outcomes

```
ECOS reports original agent recovered
├─ Evaluate current state of replacement agent
│   ├─ Replacement agent has made significant progress (over 50%)
│   │   └─ DECISION: keep_replacement
│   │      ├─ SEND graceful stop to original agent (Section 4.3)
│   │      ├─ SEND continuation confirmation to replacement agent (Section 4.4)
│   │      └─ UPDATE kanban: original agent removed, replacement confirmed
│   ├─ Replacement agent has made minimal progress (under 20%)
│   │   └─ DECISION: revert_to_original
│   │      ├─ SEND graceful stop to replacement agent (Section 4.3)
│   │      ├─ SEND continuation confirmation to original agent (Section 4.4)
│   │      ├─ SEND handoff from replacement to original (use Section 2 template)
│   │      └─ UPDATE kanban: replacement removed, original reassigned
│   └─ Replacement agent progress is between 20% and 50%
│       ├─ Original agent has critical domain context
│       │   └─ DECISION: revert_to_original (domain knowledge outweighs progress)
│       ├─ Replacement agent is performing well with no blockers
│       │   └─ DECISION: keep_replacement (momentum outweighs context switch cost)
│       └─ UNCLEAR which agent is better positioned
│           └─ ESCALATE to user for decision
│              PROVIDE both agents' status summaries to user
│              WAIT for user decision before proceeding
├─ Original agent recovered but with reduced capacity
│   └─ DECISION: keep_replacement
│      ASSIGN original agent to a different, lower-priority task
└─ Original agent recovery is uncertain (intermittent availability)
    └─ DECISION: keep_replacement
       MONITOR original agent for 30 minutes
       IF stable → consider for future assignments
       IF unstable → REPORT to ECOS for decommission
```

---

## 5. EOA Response to Agent Recovery Decision

### 5.1 When EOA must respond to ECOS recovery report

When ECOS sends a recovery report indicating that a previously failed or removed agent is now available again, the Orchestrator must evaluate the situation and respond to ECOS with the decision and its rationale.

> **Note**: Use the agent-messaging skill to send messages.

### 5.2 EOA response to keep replacement agent template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "[DECISION] Recovery Decision - Keep Replacement - Task <task-uuid>",
  "priority": "normal",
  "content": {
    "type": "recovery_response",
    "message": "Decision for task <task-uuid>: keep replacement agent <replacement-agent-session>. Reason: <reason>. The replacement agent has reached <progress>% completion and switching back would cause unacceptable delay. Original agent <original-agent-session> has been sent a graceful stop. Original agent is available for reassignment to other tasks.",
    "data": {
      "task_id": "<task-uuid>",
      "decision": "keep_replacement",
      "replacement_agent": "<replacement-agent-session-name>",
      "original_agent": "<original-agent-session-name>",
      "original_agent_available": true
    }
  }
}
```

### 5.3 EOA response to revert to original agent template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "[DECISION] Recovery Decision - Revert to Original - Task <task-uuid>",
  "priority": "normal",
  "content": {
    "type": "recovery_response",
    "message": "Decision for task <task-uuid>: revert to original agent <original-agent-session>. Reason: <reason>. The replacement agent <replacement-agent-session> has been sent a graceful stop and will provide a work summary handoff. Original agent will receive the handoff and resume work.",
    "data": {
      "task_id": "<task-uuid>",
      "decision": "revert_to_original",
      "replacement_agent": "<replacement-agent-session-name>",
      "original_agent": "<original-agent-session-name>",
      "replacement_agent_available": true
    }
  }
}
```

### 5.4 Decision tree for EOA recovery response

```
Receive ECOS recovery report for original agent
├─ Task is still in progress
│   ├─ Evaluate replacement agent progress (see Section 4.5 decision tree)
│   │   ├─ Keep replacement → SEND keep response to ECOS (Section 5.2)
│   │   └─ Revert to original → SEND revert response to ECOS (Section 5.3)
│   └─ EXECUTE recovery notifications to both agents (Section 4)
├─ Task is already completed by replacement agent
│   └─ SEND response to ECOS: "Task already completed by replacement"
│      MARK original agent as available for new assignments
│      NO recovery decision needed
└─ Task was cancelled or deprioritized while agent was down
    └─ SEND response to ECOS: "Task no longer active"
       MARK both agents as available for new assignments
       NO recovery decision needed
```

---

## 6. Reassignment Flow Decision Tree

### 6.1 Complete reassignment decision tree

This is the master decision tree for the entire reassignment flow from initial trigger to completion.

```
Agent needs reassignment
│
├─ Is old agent responsive?
│   │
│   ├─ YES (old agent can communicate)
│   │   │
│   │   └─ REQUEST work summary (Section 1 notification, Section 2 summary)
│   │       │
│   │       ├─ Summary received within deadline
│   │       │   │
│   │       │   └─ CREATE handoff document from summary
│   │       │      ASSIGN new agent with full context (Section 3)
│   │       │       │
│   │       │       ├─ New agent ACKs and confirms understanding
│   │       │       │   │
│   │       │       │   └─ NOTIFY old agent of release (Section 4.3 graceful stop)
│   │       │       │      UPDATE kanban board with new assignee
│   │       │       │      CONFIRM to ECOS that replacement is complete
│   │       │       │      DONE - reassignment successful
│   │       │       │
│   │       │       └─ New agent rejects or does not respond
│   │       │           │
│   │       │           ├─ TRY another available agent
│   │       │           │   └─ REPEAT Section 3 with new candidate
│   │       │           │
│   │       │           └─ No other agents available
│   │       │               └─ ESCALATE to ECOS requesting new agent spawn
│   │       │                  WAIT for ECOS to provide new agent
│   │       │                  REPEAT Section 3 when new agent is ready
│   │       │
│   │       └─ Summary NOT received (timeout after 15 minutes past deadline)
│   │           │
│   │           └─ ASSIGN new agent with partial context (Section 3)
│   │              NOTE gap in handoff document
│   │              RECONSTRUCT what is possible from git log and GitHub
│   │              PROCEED as above
│   │
│   └─ NO (old agent is unresponsive)
│       │
│       └─ Is their work in version control?
│           │
│           ├─ YES (commits and/or PRs exist)
│           │   │
│           │   └─ RECONSTRUCT context from commits, PR descriptions, issue comments
│           │      CREATE handoff document from reconstructed context
│           │      ASSIGN new agent with reconstructed context (Section 3)
│           │      NOTE in handoff that context was reconstructed, not provided by agent
│           │      PROCEED with standard new agent flow
│           │
│           └─ NO (no commits, no PRs, no recoverable work)
│               │
│               └─ ASSIGN new agent from scratch (use standard task assignment,
│                  not reassignment template)
│                  ESCALATE old agent status to ECOS for investigation
│                  TREAT as fresh assignment with original requirements
│                  UPDATE kanban: old agent removed, new agent assigned
```

### 6.2 Timeout thresholds reference

| Step | Timeout | Action on timeout |
|------|---------|-------------------|
| Old agent ACK of reassignment notification | 5 minutes | Retry once with urgent priority, then mark unresponsive |
| Old agent work summary delivery | 15 minutes past deadline | Proceed with partial or reconstructed context |
| New agent ACK of reassignment assignment | 10 minutes | Retry once with urgent priority, then try another agent |
| Graceful stop confirmation from removed agent | 10 minutes | Log non-response, proceed without confirmation |
| ECOS recovery decision response | 30 minutes | Escalate to user if ECOS does not respond |

---

## See Also

- [agent-communication-templates.md](./agent-communication-templates.md) - General agent communication templates
- [ecos-replacement-protocol.md](./ecos-replacement-protocol.md) - ECOS-initiated replacement protocol
- [proactive-handoff-protocol.md](./proactive-handoff-protocol.md) - Automatic handoff triggers and format
- [assignment-workflow.md](./assignment-workflow.md) - Standard task assignment workflow
- [escalation-procedures.md](./escalation-procedures.md) - When and how to escalate issues
