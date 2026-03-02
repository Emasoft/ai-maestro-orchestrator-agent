# Task Lifecycle Message Templates

This document provides the AI Maestro message templates for task lifecycle operations: cancelling tasks, pausing and resuming tasks, stopping work immediately, and broadcasting messages to multiple agents. These templates complement the standard task assignment and completion templates found in `message-templates.md`.

> All message templates below should be sent using the `agent-messaging` skill, which handles the AI Maestro API format automatically.

## Table of Contents

- [1. Task Cancellation (EOA to Agent)](#1-task-cancellation-eoa-to-agent)
- [2. Task Pause (EOA to Agent)](#2-task-pause-eoa-to-agent)
- [3. Task Resume (EOA to Agent)](#3-task-resume-eoa-to-agent)
- [4. Agent Stop Work Notification (EOA to Agent)](#4-agent-stop-work-notification-eoa-to-agent)
- [5. Broadcast Message (EOA to All Active Agents)](#5-broadcast-message-eoa-to-all-active-agents)
- [6. Cancel vs Pause vs Reassign Decision Tree](#6-cancel-vs-pause-vs-reassign-decision-tree)
- [7. Broadcast vs Targeted Decision Tree](#7-broadcast-vs-targeted-decision-tree)

---

## 1. Task Cancellation (EOA to Agent)

**When to use:** The Orchestrator (EOA) needs to permanently cancel a task that an agent is currently working on. Use this when the task is no longer needed at all. Common reasons include: requirements have changed and the task is obsolete, another task supersedes this one, or the entire project has been cancelled.

Unlike pause (which implies the task will resume later), cancellation means the task will NOT be resumed. The agent should wrap up, report what was done, and consider the task permanently closed.

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

### EOA Sends: Cancel Task

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Cancelled: <task-id>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Task <task-id> is cancelled. Reason: <reason-description>. Stop all work on this task. Provide a summary of work completed so far, files modified, and any pull requests created.",
    "data": {
      "task_id": "<task-id>",
      "action": "cancel",
      "reason": "<requirements_changed|task_superseded|project_cancelled>",
      "reason_detail": "<human-readable explanation of why the task is cancelled>",
      "work_summary_required": true,
      "superseded_by": "<new-task-id-if-applicable-or-null>"
    }
  }
}
```

**Field descriptions:**
- `reason`: One of three values. `requirements_changed` means the original requirements no longer apply. `task_superseded` means a different task replaces this one. `project_cancelled` means the entire project or feature is abandoned.
- `reason_detail`: A human-readable sentence explaining the cancellation so the agent understands context.
- `work_summary_required`: When `true`, the agent must report what was accomplished before stopping. When `false`, the agent can stop immediately without a detailed summary.
- `superseded_by`: If the reason is `task_superseded`, this field contains the identifier of the replacement task. Otherwise set to `null`.

### Agent Responds: Cancellation Acknowledgment

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "ACK Cancel: <task-id>",
  "priority": "normal",
  "content": {
    "type": "acknowledgment",
    "message": "Task <task-id> cancellation acknowledged. Work summary: <brief-description-of-what-was-done>. All work stopped.",
    "data": {
      "task_id": "<task-id>",
      "status": "cancelled",
      "work_summary": {
        "completed_items": ["<item-1>", "<item-2>"],
        "files_modified": ["<path/to/file-1>", "<path/to/file-2>"],
        "pull_requests": ["<pr-url-if-any>"],
        "uncommitted_work": "<description-of-any-uncommitted-changes-or-none>",
        "time_spent_description": "<brief estimate of effort spent>"
      }
    }
  }
}
```

### Decision Tree: When to Cancel a Task

```
Task needs stopping
│
├─ Is the task no longer needed at all?
│  │
│  ├─ YES: Requirements changed or feature dropped
│  │  └─ SEND CANCEL with reason "requirements_changed" or "project_cancelled"
│  │     └─ Set work_summary_required = true (to preserve knowledge)
│  │
│  └─ NO: The task is still needed in some form
│     │
│     ├─ Is a different task replacing this one?
│     │  │
│     │  ├─ YES: New task supersedes the old one
│     │  │  └─ SEND CANCEL with reason "task_superseded"
│     │  │     └─ Include superseded_by = "<new-task-id>"
│     │  │
│     │  └─ NO: The same task continues
│     │     └─ Do NOT cancel. Consider PAUSE or REASSIGN instead.
│     │
│     └─ (See Section 6 for full Cancel vs Pause vs Reassign tree)
```

---

## 2. Task Pause (EOA to Agent)

**When to use:** The Orchestrator (EOA) needs to temporarily suspend work on a task. The task will be resumed later. Use this when there is a temporary blocker such as: a dependency is not yet available, priorities have shifted and another task must be done first, or resources (such as API rate limits or compute) are temporarily constrained.

Unlike cancellation, a paused task is expected to resume. The agent should save its current state so that work can continue later without starting over.

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

### EOA Sends: Pause Task

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Paused: <task-id>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Pause work on task <task-id>. Reason: <reason-description>. Save your current state and report a checkpoint so work can be resumed later. Expected pause duration: <duration>.",
    "data": {
      "task_id": "<task-id>",
      "action": "pause",
      "reason": "<dependency_blocked|priority_shift|resource_constraint>",
      "reason_detail": "<human-readable explanation of why the task is paused>",
      "expected_duration": "<estimated time until resume, e.g. '2 hours', '1 day', 'unknown'>",
      "blocking_dependency": "<task-id-or-resource-that-is-blocking, or null>"
    }
  }
}
```

**Field descriptions:**
- `reason`: One of three values. `dependency_blocked` means a prerequisite task or resource is not yet available. `priority_shift` means a higher-priority task must be handled first. `resource_constraint` means a temporary limitation (API rate limits, compute capacity, etc.) prevents continued work.
- `expected_duration`: A human-readable estimate of how long the pause will last. Use `"unknown"` when the duration cannot be estimated.
- `blocking_dependency`: If the reason is `dependency_blocked`, this field identifies what is blocking. Otherwise set to `null`.

### Agent Responds: Pause Acknowledgment with State Checkpoint

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "ACK Pause: <task-id>",
  "priority": "normal",
  "content": {
    "type": "acknowledgment",
    "message": "Task <task-id> paused. State checkpoint saved. Progress: <percent>%. Ready to resume when unblocked.",
    "data": {
      "task_id": "<task-id>",
      "status": "paused",
      "state_checkpoint": {
        "progress_percent": 45,
        "current_step": "<description of what the agent was doing when paused>",
        "next_step_planned": "<description of what the agent would do next upon resume>",
        "uncommitted_work_location": "<path to branch, stash, or working directory with uncommitted changes>",
        "checkpoint_notes": "<any additional context needed to resume, such as decisions made, assumptions held>"
      }
    }
  }
}
```

### Decision Tree: When to Pause a Task

```
Task work needs to be interrupted temporarily
│
├─ Is there a dependency that is not yet available?
│  │
│  ├─ YES: Another task must complete first, or an external resource is pending
│  │  └─ SEND PAUSE with reason "dependency_blocked"
│  │     ├─ Set blocking_dependency to the specific task or resource identifier
│  │     └─ Set expected_duration based on the dependency's estimated completion
│  │
│  └─ NO: Dependencies are all satisfied
│     │
│     ├─ Has a higher-priority task arrived that needs the same agent?
│     │  │
│     │  ├─ YES: The agent must switch to the higher-priority task
│     │  │  └─ SEND PAUSE with reason "priority_shift"
│     │  │     └─ Set expected_duration based on the new task's estimated length
│     │  │
│     │  └─ NO: No priority conflict
│     │     │
│     │     ├─ Is there a temporary resource limitation?
│     │     │  │
│     │     │  ├─ YES: Rate limit, compute cap, quota exhaustion, etc.
│     │     │  │  └─ SEND PAUSE with reason "resource_constraint"
│     │     │  │     └─ Set expected_duration to the estimated recovery time
│     │     │  │
│     │     │  └─ NO: No temporary blocker exists
│     │     │     └─ Do NOT pause. If the task should stop permanently, use CANCEL.
│     │     │        If the task should stop urgently, use STOP WORK.
```

---

## 3. Task Resume (EOA to Agent)

**When to use:** The Orchestrator (EOA) is unpausing a previously paused task. The blocker that caused the pause has been resolved and the agent should continue from where it left off. This message includes any context that may have changed during the pause period, so the agent can adjust before resuming.

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

### EOA Sends: Resume Task

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Task Resumed: <task-id>",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Resume work on task <task-id>. The blocker has been resolved. Updated context: <description-of-any-changes-since-pause>. Resume from your last checkpoint.",
    "data": {
      "task_id": "<task-id>",
      "action": "resume",
      "updated_context": "<description of any changes that occurred while the task was paused, such as new commits by others, changed requirements, updated dependencies>",
      "resume_from": "<checkpoint reference from the agent's pause acknowledgment>",
      "blocker_resolution": "<description of how the blocker was resolved>"
    }
  }
}
```

**Field descriptions:**
- `updated_context`: A description of anything that changed while the task was paused. This may include new commits by other agents, updated requirements, new dependencies available, or configuration changes. If nothing changed, set to `"No changes since pause."`.
- `resume_from`: The checkpoint reference that the agent provided in its pause acknowledgment. This helps the agent locate its saved state.
- `blocker_resolution`: A description of how the original blocker was resolved, so the agent understands why it is safe to resume.

### Agent Responds: Resume Confirmation (Ready)

When the agent can successfully resume from the saved checkpoint:

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "ACK Resume: <task-id>",
  "priority": "normal",
  "content": {
    "type": "acknowledgment",
    "message": "Task <task-id> resumed. Checkpoint loaded. Continuing from: <next-step-description>. Updated context incorporated.",
    "data": {
      "task_id": "<task-id>",
      "status": "in-progress",
      "checkpoint_loaded": true,
      "resuming_from_step": "<description of the step the agent is resuming from>",
      "context_adjustments": "<description of any adjustments made based on updated_context, or 'none'>"
    }
  }
}
```

### Agent Responds: Resume Failure (State Lost)

When the agent cannot resume because its state was lost (for example, the agent session was restarted and has no memory of the checkpoint):

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "Resume Failed: <task-id>",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "Cannot resume task <task-id>. State checkpoint not found or not loadable. Reason: <explanation>. Requesting fresh task assignment.",
    "data": {
      "task_id": "<task-id>",
      "status": "resume_failed",
      "checkpoint_loaded": false,
      "failure_reason": "<session_restarted|checkpoint_corrupted|state_outdated>",
      "failure_detail": "<human-readable explanation of why the checkpoint cannot be loaded>",
      "request": "fresh_assignment"
    }
  }
}
```

### Decision Tree: Resume Handling

```
Resume message received by agent
│
├─ Can the agent load the saved checkpoint?
│  │
│  ├─ YES: Checkpoint file or state is available and intact
│  │  │
│  │  ├─ Is the updated_context compatible with saved state?
│  │  │  │
│  │  │  ├─ YES: No conflicts between saved state and new context
│  │  │  │  └─ SEND "ACK Resume" with checkpoint_loaded = true
│  │  │  │     └─ Continue work from the next_step_planned in the checkpoint
│  │  │  │
│  │  │  └─ NO: Context changes conflict with saved state
│  │  │     └─ SEND "ACK Resume" with context_adjustments describing changes
│  │  │        └─ Adapt approach based on updated_context before continuing
│  │  │
│  │  └─ (Proceed with work)
│  │
│  └─ NO: Checkpoint is missing, corrupted, or the session was restarted
│     │
│     └─ SEND "Resume Failed" with failure_reason
│        └─ EOA must decide: reassign task from scratch or provide new handoff
```

---

## 4. Agent Stop Work Notification (EOA to Agent)

**When to use:** The Orchestrator (EOA) needs an agent to stop all work immediately or gracefully. This is distinct from cancellation in two ways: (1) stop work is more urgent and may not require a detailed work summary, and (2) stop work may include a handoff to another agent.

Use this for situations such as: a critical bug has been discovered and all development must halt, the agent is working on the wrong branch or repository, or the agent must hand off work to a replacement agent immediately.

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

### EOA Sends: Stop Work

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Stop Work: <task-id>",
  "priority": "urgent",
  "content": {
    "type": "request",
    "message": "Stop all work on task <task-id> immediately. Urgency: <urgency-level>. <handoff-instruction>. Save current state and report what you have.",
    "data": {
      "task_id": "<task-id>",
      "action": "stop",
      "urgency": "<graceful|immediate>",
      "reason": "<human-readable explanation of why work must stop>",
      "handoff_required": true,
      "handoff_to": "<replacement-agent-name-or-null>"
    }
  }
}
```

**Field descriptions:**
- `urgency`: Two levels. `graceful` means the agent should finish its current atomic operation (such as completing a commit), save state, then stop. `immediate` means the agent should stop as soon as possible, even if it means leaving uncommitted work.
- `handoff_required`: When `true`, the agent must produce a handoff document describing current state, progress, and next steps so another agent can continue the work. When `false`, the agent can simply stop.
- `handoff_to`: The name of the agent that will take over this task. If `handoff_required` is `false`, this is `null`.

### Agent Responds: Stop Work Acknowledgment

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "ACK Stop: <task-id>",
  "priority": "urgent",
  "content": {
    "type": "acknowledgment",
    "message": "Work stopped on task <task-id>. <handoff-status>. Current state snapshot provided.",
    "data": {
      "task_id": "<task-id>",
      "status": "stopped",
      "work_state_snapshot": {
        "progress_percent": 30,
        "current_branch": "<git-branch-name>",
        "last_commit": "<commit-hash>",
        "uncommitted_changes": "<description of any uncommitted work, or 'none'>",
        "handoff_document": "<path to handoff doc if handoff_required was true, or null>"
      },
      "stopped_cleanly": true
    }
  }
}
```

**Field descriptions for the response:**
- `stopped_cleanly`: `true` if the agent was able to complete its current atomic operation before stopping (graceful). `false` if the agent had to abort mid-operation (immediate stop with uncommitted changes).
- `handoff_document`: The file path to a handoff document the agent created. This document should contain: current progress, decisions made, files modified, next steps planned, and any known issues. If `handoff_required` was `false`, this field is `null`.

### Decision Tree: Stop Work Urgency

```
EOA determines an agent must stop work
│
├─ Is there imminent risk of damage (wrong branch, wrong repo, critical bug)?
│  │
│  ├─ YES: Damage could worsen with every additional operation
│  │  └─ SEND STOP WORK with urgency "immediate"
│  │     ├─ Agent stops as fast as possible
│  │     └─ Accept that uncommitted work may exist
│  │
│  └─ NO: No imminent risk, but work should still stop soon
│     │
│     └─ SEND STOP WORK with urgency "graceful"
│        └─ Agent finishes current atomic operation, commits, then stops
│
├─ Does another agent need to continue this work?
│  │
│  ├─ YES: Work must be handed off
│  │  └─ Set handoff_required = true
│  │     └─ Set handoff_to = "<replacement-agent-name>"
│  │        └─ Agent produces handoff document before stopping
│  │
│  └─ NO: Work ends here (will be cancelled or re-planned later)
│     └─ Set handoff_required = false
│        └─ Agent stops without producing handoff document
```

---

## 5. Broadcast Message (EOA to All Active Agents)

**When to use:** The Orchestrator (EOA) needs to send the same information to all active agents simultaneously. Use this for announcements that affect multiple agents, such as: a repository-wide change (branch rename, dependency update), a new policy or workflow rule, a project milestone announcement, or an emergency notification.

Each broadcast message has a unique `broadcast_id` so that individual agent acknowledgments can be tracked.

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content. Send one message per agent, but include the same `broadcast_id` in each so responses can be correlated.

### EOA Sends: Broadcast

For each active agent, EOA sends the following message (varying only the `to` field):

```json
{
  "from": "orchestrator",
  "to": "<agent-name>",
  "subject": "Broadcast <broadcast-id>: <subject-line>",
  "priority": "<normal|high|urgent>",
  "content": {
    "type": "notification",
    "message": "<broadcast-message-body>",
    "data": {
      "broadcast_id": "<unique-broadcast-identifier, e.g. 'bcast-20260208-001'>",
      "scope": "<all|role-specific|project-specific>",
      "scope_filter": "<role name or project name if scope is not 'all', otherwise null>",
      "action_required": "<true if agents must do something, false if informational only>",
      "action_description": "<what agents must do, if action_required is true, otherwise null>",
      "action_deadline": "<deadline for action, if applicable, otherwise null>"
    }
  }
}
```

**Field descriptions:**
- `broadcast_id`: A unique identifier for this broadcast. Format: `bcast-YYYYMMDD-NNN` where `NNN` is a sequential number for the day. This identifier is used to track which agents have acknowledged the broadcast.
- `scope`: Determines which agents should receive the broadcast. `all` means every active agent. `role-specific` means only agents of a particular role (for example, all programmer agents). `project-specific` means only agents working on a particular project.
- `scope_filter`: When scope is `role-specific`, this contains the role name (for example, `programmer` or `integrator`). When scope is `project-specific`, this contains the project name. When scope is `all`, this is `null`.
- `action_required`: `true` when agents must take some action in response (such as rebasing their branch). `false` when the broadcast is purely informational.

### Agent Responds: Broadcast Acknowledgment

Each agent sends its own acknowledgment:

```json
{
  "from": "<agent-name>",
  "to": "orchestrator",
  "subject": "ACK Broadcast: <broadcast-id>",
  "priority": "low",
  "content": {
    "type": "acknowledgment",
    "message": "Broadcast <broadcast-id> received and understood. <action-taken-or-noted>",
    "data": {
      "broadcast_id": "<broadcast-id>",
      "acknowledged": true,
      "action_taken": "<description of action taken if action_required was true, or 'noted' if informational>"
    }
  }
}
```

### Decision Tree: Broadcast Construction

```
EOA has information to share with agents
│
├─ Does the information affect ALL active agents?
│  │
│  ├─ YES: Repository-wide change, emergency, or global policy
│  │  └─ Set scope = "all", scope_filter = null
│  │     │
│  │     ├─ Is it an emergency (critical bug, security issue)?
│  │     │  ├─ YES: Set priority = "urgent"
│  │     │  └─ NO: Set priority = "normal" or "high"
│  │     │
│  │     └─ Must agents take action (rebase, update, restart)?
│  │        ├─ YES: Set action_required = true, describe in action_description
│  │        └─ NO: Set action_required = false (informational only)
│  │
│  └─ NO: Only some agents are affected
│     │
│     ├─ Does it affect all agents of a particular role?
│     │  │
│     │  ├─ YES: For example, all programmer agents or all integrator agents
│     │  │  └─ Set scope = "role-specific", scope_filter = "<role-name>"
│     │  │     └─ Send only to agents matching that role
│     │  │
│     │  └─ NO: Not role-based
│     │     │
│     │     ├─ Does it affect all agents on a specific project?
│     │     │  │
│     │     │  ├─ YES: Project-specific change (branch rename, build config)
│     │     │  │  └─ Set scope = "project-specific", scope_filter = "<project-name>"
│     │     │  │     └─ Send only to agents assigned to that project
│     │     │  │
│     │     │  └─ NO: Affects only one or two specific agents
│     │     │     └─ Do NOT use broadcast.
│     │     │        └─ Send direct messages to those specific agents instead.
```

---

## 6. Cancel vs Pause vs Reassign Decision Tree

Use this decision tree when a task needs to stop but you are unsure whether to cancel, pause, or reassign it. This tree covers all three scenarios and helps the Orchestrator choose the correct lifecycle action.

```
Task needs stopping
│
├─ Is the task no longer needed at all?
│  │
│  ├─ YES: Requirements changed, feature dropped, or project cancelled
│  │  └─ ACTION: CANCEL the task
│  │     ├─ Send "Task Cancelled" message (see Section 1)
│  │     ├─ Set work_summary_required = true to preserve knowledge
│  │     └─ Close the corresponding GitHub issue if applicable
│  │
│  └─ NO: The task is still needed in some form
│     │
│     ├─ Is a different agent better suited to complete this task?
│     │  │
│     │  ├─ YES: Current agent lacks skills, capacity, or context
│     │  │  └─ ACTION: REASSIGN the task (stop + new assignment)
│     │  │     ├─ Step 1: Send "Stop Work" to current agent (see Section 4)
│     │  │     │  └─ Set handoff_required = true
│     │  │     │  └─ Set handoff_to = "<new-agent-name>"
│     │  │     ├─ Step 2: Wait for stop acknowledgment with handoff document
│     │  │     └─ Step 3: Send "Task Assignment" to new agent
│     │  │        └─ Include handoff_doc path from the stop acknowledgment
│     │  │
│     │  └─ NO: Current agent is the right one for the task
│     │     │
│     │     ├─ Is there a temporary blocker preventing continued work?
│     │     │  │
│     │     │  ├─ YES: Dependency not ready, priority shift, or resource limit
│     │     │  │  └─ ACTION: PAUSE the task
│     │     │  │     ├─ Send "Task Paused" message (see Section 2)
│     │     │  │     └─ Track the blocker and send "Task Resumed" when resolved
│     │     │  │
│     │     │  └─ NO: No blocker exists
│     │     │     └─ ACTION: Do not stop the task. Let it continue.
│     │     │        └─ If you reached this point but still feel the task
│     │     │           should stop, re-evaluate your reasoning. Perhaps the
│     │     │           task needs to be redefined rather than stopped.
```

---

## 7. Broadcast vs Targeted Decision Tree

Use this decision tree when the Orchestrator has information to communicate and needs to decide whether to broadcast or send targeted messages.

```
Information to share with agents
│
├─ Does this information affect all currently active agents?
│  │
│  ├─ YES: Examples include repository-wide branch rename, new coding standards,
│  │       emergency security patch, project-wide dependency update
│  │  └─ ACTION: Send BROADCAST to all agents (see Section 5)
│  │     └─ Set scope = "all"
│  │
│  └─ NO: Only some agents are affected
│     │
│     ├─ Does it affect all agents of a specific role category?
│     │  │  Examples: All programmer agents need to rebase, all integrator
│     │  │  agents need to update their review checklist
│     │  │
│     │  ├─ YES: Multiple agents share the same role and all need this info
│     │  │  └─ ACTION: Send ROLE-TARGETED BROADCAST (see Section 5)
│     │  │     └─ Set scope = "role-specific", scope_filter = "<role-name>"
│     │  │
│     │  └─ NO: Not a role-wide concern
│     │     │
│     │     ├─ Does it affect all agents working on a specific project?
│     │     │  │  Examples: Project branch was renamed, project build config changed,
│     │     │  │  project-specific deadline moved
│     │     │  │
│     │     │  ├─ YES: Multiple agents on the same project need this info
│     │     │  │  └─ ACTION: Send PROJECT-TARGETED BROADCAST (see Section 5)
│     │     │  │     └─ Set scope = "project-specific", scope_filter = "<project-name>"
│     │     │  │
│     │     │  └─ NO: Only one or two specific agents need this information
│     │     │     │
│     │     │     └─ ACTION: Send DIRECT MESSAGE to each affected agent
│     │     │        └─ Use standard message templates from message-templates.md
│     │     │           (such as Status Request, Task Assignment, etc.)
│     │     │        └─ Do NOT use broadcast for messages to fewer than 3 agents
```
