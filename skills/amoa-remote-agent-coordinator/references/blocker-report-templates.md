# Implementer Blocker Report Templates

Process and dependency blocker reporting templates for implementer agents. These templates cover situations where an agent cannot continue work due to process, dependency, access, resource, requirement, or external service issues.

**Important**: This file is DISTINCT from `bug-reporting-protocol.md`, which covers code defect reports. Blocker reports cover non-code obstacles that prevent an agent from making progress on an assigned task.

---

## Contents

- [1. Agent Blocker Report (Agent to EOA)](#1-agent-blocker-report-agent-to-eoa) - When an implementer agent is blocked and needs EOA intervention
- [2. EOA Blocker Triage Response (EOA to Agent)](#2-eoa-blocker-triage-response-eoa-to-agent) - When EOA has triaged the blocker and responds with a resolution path
- [3. EOA Blocker Resolution Notification (EOA to Agent)](#3-eoa-blocker-resolution-notification-eoa-to-agent) - When EOA has fully resolved the blocker and the agent can resume work
- [4. Blocker Triage Decision Tree](#4-blocker-triage-decision-tree) - How EOA decides what action to take for each blocker type
- [5. Blocker vs Bug Report Decision Guide](#5-blocker-vs-bug-report-decision-guide) - How to determine whether to file a blocker report or a bug report

---

## 1. Agent Blocker Report (Agent to EOA)

### When to Use

Use this template when an implementer agent encounters a non-code obstacle that prevents continued progress on an assigned task. Specific situations include:

- Waiting on output from another agent that has not been delivered
- Missing access permissions to a repository, service, or resource
- Required infrastructure or compute resource is unavailable
- A requirement in the task instructions is ambiguous, contradictory, or incomplete
- An external service (API, CI/CD pipeline, third-party tool) is down or unreachable

Do NOT use this template for code bugs. Use `bug-reporting-protocol.md` for code defects instead.

### Send Template

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "{agent_session_name}",
  "to": "{eoa_session_name}",
  "subject": "[BLOCKED] Task {task_id}: {brief_description}",
  "priority": "high",
  "content": {
    "type": "blocker-report",
    "message": "Blocker report for task {task_id}. See data for details.",
    "data": {
      "task_id": "{task_id}",
      "blocker_type": "{dependency|access|resource|requirement|external_service}",
      "description": "Detailed description of what is blocking progress",
      "impact": "{blocked_completely|partially_blocked|degraded}",
      "workarounds_attempted": [
        "Description of first workaround attempted and its result",
        "Description of second workaround attempted and its result"
      ],
      "estimated_impact_on_deadline": "How this blocker affects the task deadline (e.g., '2 hours delay if resolved within 1 hour, 1 day delay otherwise')",
      "suggested_resolution": "What the agent believes would unblock the situation",
      "blocked_since": "{ISO 8601 timestamp when agent became blocked}",
      "related_agents": ["{session_name_of_related_agent_if_applicable}"]
    }
  }
}
```

**Variables to fill**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{agent_session_name}` | The blocked agent's full session name | `svgbbox-programmer-001` |
| `{eoa_session_name}` | The EOA orchestrator's full session name | `eoa-svgbbox-orchestrator` |
| `{task_id}` | The GitHub issue or task identifier | `GH-42` |
| `{brief_description}` | One-line summary of the blocker | `Waiting on auth module from programmer-002` |
| `{blocker_type}` | One of: `dependency`, `access`, `resource`, `requirement`, `external_service` | `dependency` |
| `{impact}` | One of: `blocked_completely`, `partially_blocked`, `degraded` | `blocked_completely` |

**Priority rules**:
- Use `"priority": "urgent"` when the blocker will cause a missed deadline within the next 2 hours
- Use `"priority": "high"` for all other blockers (this is the default for blocker reports)

### Example: Dependency Blocker

```json
{
  "from": "svgbbox-programmer-001",
  "to": "eoa-svgbbox-orchestrator",
  "subject": "[BLOCKED] Task GH-42: Waiting on auth module from programmer-002",
  "priority": "high",
  "content": {
    "type": "blocker-report",
    "message": "Blocker report for task GH-42. See data for details.",
    "data": {
      "task_id": "GH-42",
      "blocker_type": "dependency",
      "description": "The user-profile module (GH-42) requires the auth token interface exported by the auth-core module (GH-38), which is assigned to programmer-002. The auth-core module has not been delivered yet and no interim interface definition is available.",
      "impact": "blocked_completely",
      "workarounds_attempted": [
        "Attempted to define a temporary interface stub based on the task specification, but the spec does not include the token refresh method signature",
        "Checked if programmer-002 has pushed any partial work to a branch, but no branch exists yet"
      ],
      "estimated_impact_on_deadline": "If resolved within 2 hours, no deadline impact. Otherwise 1 day delay on GH-42 and dependent GH-45.",
      "suggested_resolution": "Request programmer-002 to publish the auth token interface definition as a standalone header file, even if the full implementation is not complete",
      "blocked_since": "2025-12-30T14:30:00Z",
      "related_agents": ["svgbbox-programmer-002"]
    }
  }
}
```

---

## 2. EOA Blocker Triage Response (EOA to Agent)

### When to Use

Use this template immediately after receiving and triaging a blocker report from an implementer agent. The EOA must respond to every blocker report. This template communicates the resolution path and provides interim instructions so the agent knows what to do while waiting.

### Response Template

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "{eoa_session_name}",
  "to": "{agent_session_name}",
  "subject": "[TRIAGE] Task {task_id}: Blocker {resolution_type}",
  "priority": "high",
  "content": {
    "type": "blocker-triage-response",
    "message": "Blocker triage response for task {task_id}. See data for details.",
    "data": {
      "task_id": "{task_id}",
      "original_blocker_type": "{dependency|access|resource|requirement|external_service}",
      "resolution_type": "{unblocked|workaround_provided|escalated|reassigned}",
      "resolution_details": "Detailed explanation of what EOA is doing to resolve the blocker",
      "estimated_resolution_time": "When the agent can expect the blocker to be fully resolved (e.g., '30 minutes', '2 hours', 'next planning cycle')",
      "interim_instructions": "Specific instructions for what the agent should do while waiting for the blocker to be resolved"
    }
  }
}
```

**Variables to fill**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{resolution_type}` | One of: `unblocked`, `workaround_provided`, `escalated`, `reassigned` | `workaround_provided` |
| `{estimated_resolution_time}` | Human-readable time estimate | `30 minutes` |
| `{interim_instructions}` | What the agent should do while waiting | `Work on the unit tests for the modules you have completed so far` |

**Resolution type meanings**:

| Resolution Type | Meaning | Agent Action |
|-----------------|---------|--------------|
| `unblocked` | The blocker has been resolved immediately | Resume work on the blocked task |
| `workaround_provided` | A temporary workaround is available | Apply the workaround and continue work |
| `escalated` | The blocker has been escalated to ECOS, EAA, EAMA, or the user | Follow interim instructions while waiting |
| `reassigned` | The task has been reassigned to avoid the blocker | Stop work and await new assignment |

### Example: Workaround Provided

```json
{
  "from": "eoa-svgbbox-orchestrator",
  "to": "svgbbox-programmer-001",
  "subject": "[TRIAGE] Task GH-42: Blocker workaround_provided",
  "priority": "high",
  "content": {
    "type": "blocker-triage-response",
    "message": "Blocker triage response for task GH-42. See data for details.",
    "data": {
      "task_id": "GH-42",
      "original_blocker_type": "dependency",
      "resolution_type": "workaround_provided",
      "resolution_details": "I have contacted programmer-002 with a priority request to publish the auth token interface. In the meantime, I am providing you with an interface stub based on the architect's design document (see artifact auth-token-interface-stub.ts shared via artifact-sharing-protocol).",
      "estimated_resolution_time": "1 hour for the full interface from programmer-002",
      "interim_instructions": "Use the provided interface stub (auth-token-interface-stub.ts) to continue implementing the user-profile module. The stub matches the architect's design and will be compatible with the final implementation. Proceed with all work except the token refresh integration, which requires the final interface."
    }
  }
}
```

---

## 3. EOA Blocker Resolution Notification (EOA to Agent)

### When to Use

Use this template after a previously reported blocker has been fully resolved. This notifies the agent that the obstacle no longer exists and provides instructions for resuming work, including any changes to the task scope that resulted from the blocker resolution.

### Notification Template

> **Note**: Use the agent-messaging skill to send messages. The JSON structure below shows the message content.

```json
{
  "from": "{eoa_session_name}",
  "to": "{agent_session_name}",
  "subject": "[RESOLVED] Task {task_id}: Blocker resolved",
  "priority": "normal",
  "content": {
    "type": "blocker-resolution",
    "message": "Blocker for task {task_id} has been resolved. See data for details.",
    "data": {
      "task_id": "{task_id}",
      "original_blocker_id": "{reference to original blocker report subject or timestamp}",
      "resolution_summary": "Description of how the blocker was resolved",
      "resume_instructions": "Specific instructions for resuming work on the task, including what has changed since the blocker was reported",
      "any_scope_changes": "Description of any changes to the task scope, acceptance criteria, or deadline resulting from the blocker resolution, or 'none' if no changes"
    }
  }
}
```

**Variables to fill**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{original_blocker_id}` | Reference to the original blocker report | `[BLOCKED] Task GH-42: Waiting on auth module from programmer-002` |
| `{resolution_summary}` | How the blocker was resolved | `programmer-002 published the auth-core interface` |
| `{resume_instructions}` | What the agent should do now | `Replace the interface stub with the published auth-core module and complete the token refresh integration` |
| `{any_scope_changes}` | Scope changes resulting from resolution | `Deadline extended by 4 hours to account for blocker delay` |

### Example: Dependency Blocker Resolved

```json
{
  "from": "eoa-svgbbox-orchestrator",
  "to": "svgbbox-programmer-001",
  "subject": "[RESOLVED] Task GH-42: Blocker resolved",
  "priority": "normal",
  "content": {
    "type": "blocker-resolution",
    "message": "Blocker for task GH-42 has been resolved. See data for details.",
    "data": {
      "task_id": "GH-42",
      "original_blocker_id": "[BLOCKED] Task GH-42: Waiting on auth module from programmer-002",
      "resolution_summary": "programmer-002 has published the final auth-core interface and pushed the auth-token module to the auth-core-v1 branch. The interface matches the stub previously provided, with one addition: a revoke_token() method was added per the architect's updated design.",
      "resume_instructions": "Replace the interface stub (auth-token-interface-stub.ts) with the published auth-core module from the auth-core-v1 branch. Integrate the token refresh method and add support for the new revoke_token() method. Update unit tests to cover token revocation.",
      "any_scope_changes": "Deadline extended by 2 hours (new deadline: 2025-12-30T20:00:00Z). Added acceptance criterion: revoke_token() must be supported."
    }
  }
}
```

---

## 4. Blocker Triage Decision Tree

When EOA receives a blocker report, follow this decision tree to determine the correct action.

> **Note**: Use the agent-messaging skill to send messages at each step where communication is required.

```
Blocker report received
│
├─ What is the blocker type?
│
├─ DEPENDENCY (waiting on another agent)
│   │
│   ├─ Is the other agent responsive?
│   │   │
│   │   ├─ YES
│   │   │   ├─ Send priority request to the other agent for the needed deliverable
│   │   │   ├─ Update the timeline for both tasks
│   │   │   └─ Provide interim instructions to the blocked agent
│   │   │
│   │   └─ NO (agent not responding after 2 poll attempts)
│   │       ├─ Reassign the dependency to a different agent
│   │       ├─ If no agent available, escalate to ECOS for new agent allocation
│   │       └─ Provide interim instructions to the blocked agent
│   │
│   └─ Is partial output available from the other agent?
│       │
│       ├─ YES → Provide partial output as workaround, set follow-up check
│       └─ NO → Proceed with reassign or escalate path above
│
├─ ACCESS or RESOURCE (missing permissions, unavailable infrastructure)
│   │
│   ├─ Can EOA grant access or allocate the resource directly?
│   │   │
│   │   ├─ YES
│   │   │   ├─ Grant access or allocate the resource
│   │   │   ├─ Notify the agent that the blocker is resolved
│   │   │   └─ Send blocker resolution notification
│   │   │
│   │   └─ NO (requires higher authority)
│   │       ├─ Escalate to ECOS with a security clearance or resource request
│   │       ├─ Provide estimated resolution time to the agent
│   │       └─ Provide interim instructions (e.g., work on other parts of the task)
│   │
│   └─ Is the resource critical or optional?
│       │
│       ├─ CRITICAL → Prioritize escalation, pause the blocked task components
│       └─ OPTIONAL → Provide workaround, continue without the resource
│
├─ REQUIREMENT (unclear, ambiguous, or contradictory instructions)
│   │
│   ├─ Is the Architect Agent (EAA) available?
│   │   │
│   │   ├─ YES
│   │   │   ├─ Escalate to EAA for requirement clarification
│   │   │   ├─ Include the specific ambiguity and the agent's interpretation options
│   │   │   └─ Provide interim instructions based on the most likely interpretation
│   │   │
│   │   └─ NO (EAA not available or not assigned to this project)
│   │       ├─ Escalate to EAMA (Assistant Manager) for user clarification
│   │       ├─ Include the requirement text and the conflicting interpretations
│   │       └─ Provide interim instructions based on the most conservative interpretation
│   │
│   └─ Is the requirement blocker critical to current work?
│       │
│       ├─ YES → Agent pauses affected component, works on unaffected components
│       └─ NO → Agent proceeds with best interpretation, flags for later review
│
└─ EXTERNAL SERVICE (third-party API, CI/CD pipeline, tool down)
    │
    ├─ Is there a workaround available?
    │   │
    │   ├─ YES
    │   │   ├─ Provide the workaround instructions to the agent
    │   │   ├─ Monitor the external service for restoration
    │   │   └─ Notify agent when service is restored (send resolution notification)
    │   │
    │   └─ NO (no workaround possible)
    │       ├─ Pause the task components that depend on the external service
    │       ├─ Redirect agent to work on independent task components
    │       ├─ Monitor the external service status
    │       └─ Notify agent when service is restored (send resolution notification)
    │
    └─ Is the service outage expected to be short or long?
        │
        ├─ SHORT (less than 1 hour) → Agent waits, works on other components
        └─ LONG (more than 1 hour) → Reassign agent to a different task if possible
```

---

## 5. Blocker vs Bug Report Decision Guide

When an agent encounters an obstacle, use this guide to determine whether to file a blocker report (this file) or a bug report (`bug-reporting-protocol.md`).

### Comparison Table

| Characteristic | Blocker Report (This File) | Bug Report (bug-reporting-protocol.md) |
|---|---|---|
| **Nature of the problem** | Process, dependency, access, or environment issue | Code defect, incorrect behavior, test failure |
| **Root cause** | External to the agent's code (another agent, service, permission, requirement) | Internal to the codebase (wrong logic, missing handling, regression) |
| **Agent can fix it** | No, the agent cannot resolve the obstacle alone | Sometimes, agent may be able to fix the code defect |
| **Needs EOA action** | Always requires EOA to coordinate, escalate, or grant access | Sometimes requires EOA (for triage), sometimes agent fixes directly |
| **Has reproduction steps** | Not applicable (it is a process obstacle, not a code defect) | Required (steps to reproduce the bug in code) |
| **Has severity levels** | Uses impact levels: `blocked_completely`, `partially_blocked`, `degraded` | Uses severity levels: `critical`, `high`, `normal`, `low` |
| **Priority** | Always `high` or `urgent` | Varies based on severity |
| **Template location** | This file (blocker-report-templates.md) | bug-reporting-protocol.md and its part files |
| **Message type** | `blocker-report` | `bug-report` |

### Decision Procedure

Ask these questions in order:

1. **Is the problem in the code?** If the agent found incorrect behavior, a failed test, or a logic error in the source code, file a **bug report**.
2. **Is the problem outside the agent's control?** If the agent cannot resolve the obstacle by changing code (e.g., waiting on another agent, missing permissions, service down, unclear requirements), file a **blocker report**.
3. **Can the agent reproduce it with specific code steps?** If yes, it is a **bug report**. If the problem is a process or environment state, it is a **blocker report**.

### Edge Cases

| Situation | Correct Report Type | Reasoning |
|---|---|---|
| Agent finds a bug in another agent's code | **Bug report** to EOA, who routes it to the responsible agent | The root cause is a code defect |
| Agent cannot access a repository | **Blocker report** | The root cause is a permission or access issue |
| CI/CD pipeline fails due to a code bug | **Bug report** | The root cause is a code defect, even though CI is the symptom |
| CI/CD pipeline fails due to infrastructure | **Blocker report** | The root cause is an infrastructure or service issue |
| Requirement says "fast" but does not define a threshold | **Blocker report** with `blocker_type: requirement` | The root cause is an unclear specification |
| Agent discovers a security vulnerability | **Bug report** with `severity: critical` | The root cause is a code defect, even if it also blocks progress |
