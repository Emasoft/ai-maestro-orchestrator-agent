# Remote Agent Registration


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 Agent Registration Format](#20-agent-registration-format)
  - [2.1 Required Fields for Agent Registration](#21-required-fields-for-agent-registration)
  - [2.2 Agent Capabilities List](#22-agent-capabilities-list)
  - [2.3 Availability States](#23-availability-states)
- [3.0 Agent Roster Management](#30-agent-roster-management)
  - [3.1 Creating and Maintaining AGENT_ROSTER.md](#31-creating-and-maintaining-agent_rostermd)
- [Active Agents](#active-agents)
- [Offline Agents](#offline-agents)
  - [3.2 Updating Agent Status](#32-updating-agent-status)
  - [3.3 Tracking Current Task Assignments](#33-tracking-current-task-assignments)
- [4.0 Agent Roster File Template](#40-agent-roster-file-template)
  - [4.1 Full Template](#41-full-template)
- [Active Agents](#active-agents)
- [Offline Agents](#offline-agents)
- [Onboarding Agents](#onboarding-agents)
- [Agent History](#agent-history)
  - [Recently Completed Tasks](#recently-completed-tasks)
- [5.0 Integration with Onboarding](#50-integration-with-onboarding)
  - [5.1 Registration After Successful Onboarding](#51-registration-after-successful-onboarding)
  - [5.2 Verification Task Completion Requirement](#52-verification-task-completion-requirement)

---

## Table of Contents

- 1.0 Overview
- 1.1 When to register a new agent
- 1.2 Prerequisites before registration
- 2.0 Agent Registration Format
- 2.1 Required fields for agent registration
- 2.2 Agent capabilities list
- 2.3 Availability states
- 3.0 Agent Roster Management
- 3.1 Creating and maintaining AGENT_ROSTER.md
- 3.2 Updating agent status
- 3.3 Tracking current task assignments
- 4.0 Agent Roster File Template
- 4.1 Active agents section
- 4.2 Offline agents section
- 5.0 Integration with Onboarding
- 5.1 Registration after successful onboarding
- 5.2 Verification task completion requirement

---

## 1.0 Overview

Before an agent can receive tasks, it must be registered in the project's agent roster. Registration happens after successful completion of onboarding verification.

---

## 2.0 Agent Registration Format

### 2.1 Required Fields for Agent Registration

```json
{
  "agent_id": "dev-agent-1",
  "session_name": "libs-core-developer",
  "capabilities": ["python", "typescript", "testing"],
  "availability": "active|busy|offline",
  "current_task": null
}
```

### 2.2 Agent Capabilities List

Common capability tags:
- Languages: `python`, `typescript`, `javascript`, `rust`, `go`, `java`
- Frameworks: `react`, `vue`, `django`, `fastapi`, `express`
- Skills: `testing`, `documentation`, `devops`, `security`, `database`
- Platforms: `macos`, `linux`, `windows`, `docker`, `kubernetes`

### 2.3 Availability States

| State | Meaning | Can Receive Tasks |
|-------|---------|-------------------|
| `active` | Ready for new tasks | Yes |
| `busy` | Working on current task | No (queue only) |
| `offline` | Not responding | No |
| `onboarding` | Still in onboarding | No |

---

## 3.0 Agent Roster Management

### 3.1 Creating and Maintaining AGENT_ROSTER.md

The orchestrator maintains `AGENT_ROSTER.md` in the project root:

```markdown
# Agent Roster

## Active Agents

| Agent ID | Session Name | Capabilities | Status | Current Task |
|----------|--------------|--------------|--------|--------------|
| dev-agent-1 | libs-core-developer | Python, TypeScript | Active | - |
| dev-agent-2 | apps-frontend-dev | React, CSS | Busy | GH-42 |
| human-dev-1 | - | Full stack | Active | - |

## Offline Agents

| Agent ID | Last Seen | Notes |
|----------|-----------|-------|
| dev-agent-3 | 2025-12-29 | Machine down |
```

### 3.2 Updating Agent Status

Update the roster when:
- Agent completes a task: `busy` -> `active`
- Agent accepts a new task: `active` -> `busy`
- Agent goes unresponsive: any -> `offline`
- Agent comes back online: `offline` -> `active`

### 3.3 Tracking Current Task Assignments

The `Current Task` column should always reflect:
- Task ID (e.g., `GH-42`) when agent is busy
- `-` when agent is available
- Task queue if agent has multiple assigned tasks

---

## 4.0 Agent Roster File Template

### 4.1 Full Template

```markdown
# Agent Roster

Last Updated: {ISO-8601 timestamp}

## Active Agents

| Agent ID | Session Name | Capabilities | Status | Current Task | Last Heartbeat |
|----------|--------------|--------------|--------|--------------|----------------|
| {agent_id} | {session_name} | {capabilities} | {status} | {task_id or -} | {timestamp} |

## Offline Agents

| Agent ID | Last Seen | Notes |
|----------|-----------|-------|
| {agent_id} | {last_seen_timestamp} | {reason if known} |

## Onboarding Agents

| Agent ID | Started | Stage | Blockers |
|----------|---------|-------|----------|
| {agent_id} | {start_timestamp} | {verification|setup|reading} | {any blockers} |

## Agent History

### Recently Completed Tasks
| Agent ID | Task ID | Completed | Duration |
|----------|---------|-----------|----------|
| {agent_id} | {task_id} | {timestamp} | {hours}h |
```

---

## 5.0 Integration with Onboarding

### 5.1 Registration After Successful Onboarding

An agent is only registered after:
1. Completing all onboarding steps
2. Successfully passing the verification task
3. Sending a valid registration message

### 5.2 Verification Task Completion Requirement

Before adding to active roster, verify:
- [ ] Agent completed onboarding verification task
- [ ] PR was reviewed and approved
- [ ] Agent demonstrated TDD workflow
- [ ] Agent communication follows expected formats
