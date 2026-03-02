# Session Lifecycle Message Templates

Complete reference for all session lifecycle message templates used between ECOS (Chief of Staff) and EOA (Orchestrator Agent). These templates cover the full agent lifecycle: waking, hibernating, terminating, and periodic status reporting.

> All message templates below should be sent using the `agent-messaging` skill, which handles the AI Maestro API format automatically.

## Table of Contents

- [1. ECOS Wake Message to EOA](#1-ecos-wake-message-to-eoa)
- [2. EOA Wake Acknowledgment to ECOS](#2-eoa-wake-acknowledgment-to-ecos)
- [3. ECOS Hibernate Directive to EOA](#3-ecos-hibernate-directive-to-eoa)
- [4. EOA Hibernate Acknowledgment to ECOS](#4-eoa-hibernate-acknowledgment-to-ecos)
- [5. ECOS Terminate Directive to EOA](#5-ecos-terminate-directive-to-eoa)
- [6. EOA Final Termination Report to ECOS](#6-eoa-final-termination-report-to-ecos)
- [7. EOA Periodic Status Report to ECOS (30-minute intervals)](#7-eoa-periodic-status-report-to-ecos-30-minute-intervals)

---

## 1. ECOS Wake Message to EOA

**When to use:** ECOS sends this message to bring EOA online at the start of a session or after a hibernation period. The wake message provides EOA with everything it needs to resume operations: pending task context, session configuration, and a summary of unread messages accumulated while EOA was offline.

> **Note**: Use the agent-messaging skill to send messages.

**JSON send template (ECOS to EOA):**

```json
{
  "from": "ecos-main",
  "to": "eoa-<project-name>",
  "subject": "Wake Directive: Resume Operations",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Wake up and resume orchestration duties. Review pending tasks and inbox, then report readiness.",
    "data": {
      "directive": "wake",
      "task_context": {
        "pending_tasks": [
          {
            "task_id": "<task-uuid>",
            "title": "<task-title>",
            "priority": "high|normal|low",
            "status": "in-progress|blocked|queued",
            "assigned_agent": "<agent-session-name-or-null>",
            "last_update": "<ISO8601-timestamp>"
          }
        ],
        "total_pending": 0,
        "total_blocked": 0
      },
      "session_config": {
        "project_name": "<project-name>",
        "project_dir": "<absolute-path-to-project>",
        "kanban_file": "<path-to-kanban-or-null>",
        "max_concurrent_agents": 5,
        "status_report_interval_minutes": 30
      },
      "inbox_summary": {
        "unread_count": 0,
        "oldest_unread_timestamp": "<ISO8601-timestamp-or-null>",
        "senders": ["<agent-name-1>", "<agent-name-2>"]
      }
    }
  }
}
```

**Key fields explained:**

| Field | Purpose |
|-------|---------|
| `task_context.pending_tasks` | Array of tasks that were active or queued before hibernation or shutdown |
| `task_context.total_pending` | Count of tasks not yet completed |
| `task_context.total_blocked` | Count of tasks with unresolved blockers |
| `session_config.project_name` | Project identifier used for session naming |
| `session_config.kanban_file` | Path to the kanban markdown file, or null if not configured |
| `session_config.max_concurrent_agents` | Maximum number of implementer agents EOA may spawn simultaneously |
| `session_config.status_report_interval_minutes` | How often EOA must send periodic status reports (default: 30) |
| `inbox_summary.unread_count` | Number of messages received while EOA was offline |
| `inbox_summary.senders` | List of agents who sent messages while EOA was offline |

---

## 2. EOA Wake Acknowledgment to ECOS

**When to use:** EOA sends this immediately after processing the wake directive from ECOS. This acknowledgment confirms that EOA has reviewed its pending tasks, checked its inbox, and is ready to begin orchestration.

> **Note**: Use the agent-messaging skill to send messages.

**JSON response template (EOA to ECOS):**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "ACK: Wake Directive - Ready for Operations",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "Wake acknowledged. Capabilities confirmed. <N> pending tasks loaded. <M> inbox messages processed. Ready to orchestrate.",
    "data": {
      "directive_ack": "wake",
      "capabilities_confirmed": true,
      "pending_tasks_acknowledged": 0,
      "inbox_messages_processed": 0,
      "ready_status": "ready|degraded|blocked",
      "degraded_reason": "<reason-if-degraded-or-null>",
      "first_action": "<description-of-what-eoa-will-do-first>"
    }
  }
}
```

**Key fields explained:**

| Field | Purpose |
|-------|---------|
| `capabilities_confirmed` | Boolean indicating EOA has verified its tools and MCP connections are operational |
| `pending_tasks_acknowledged` | Number of pending tasks EOA has loaded into its working state |
| `inbox_messages_processed` | Number of unread messages EOA has read and processed |
| `ready_status` | One of: `ready` (fully operational), `degraded` (operational with limitations), `blocked` (cannot proceed) |
| `degraded_reason` | If status is `degraded` or `blocked`, explains why (for example, missing MCP server, unreachable agent) |
| `first_action` | Brief description of what EOA will do first after waking (for example, "Resume task T-042 assigned to svgbbox-programmer-001") |

**Decision tree for EOA upon receiving Wake directive:**

```
EOA receives Wake directive from ECOS
    │
    ├─ Check inbox for unread messages?
    │     ├─ Yes (unread_count > 0) → Process all unread messages first
    │     │     ├─ Messages contain blockers → Report degraded status to ECOS
    │     │     └─ Messages processed OK → Continue to pending tasks check
    │     └─ No (unread_count == 0) → Continue to pending tasks check
    │
    ├─ Check pending tasks from task_context?
    │     ├─ Has pending tasks → Identify highest-priority task
    │     │     ├─ Task has assigned agent → Check if agent is online, resume
    │     │     └─ Task unassigned → Queue for next delegation cycle
    │     └─ No pending tasks → Report idle status to ECOS
    │
    └─ Send Wake ACK to ECOS with ready_status and first_action
```

---

## 3. ECOS Hibernate Directive to EOA

**When to use:** ECOS sends this when EOA should enter a suspended state. Reasons include: the system is idle and resources should be conserved, scheduled maintenance is occurring, or ECOS is redistributing workloads. EOA must save its current state before acknowledging.

> **Note**: Use the agent-messaging skill to send messages.

**JSON send template (ECOS to EOA):**

```json
{
  "from": "ecos-main",
  "to": "eoa-<project-name>",
  "subject": "Hibernate Directive: Suspend Operations",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Hibernate immediately. Save current state, pause active agents, and acknowledge when ready.",
    "data": {
      "directive": "hibernate",
      "reason": "idle|resource-saving|maintenance",
      "expected_duration": "<ISO8601-duration-or-unknown>",
      "save_state": true,
      "additional_instructions": "<optional-special-instructions-or-null>"
    }
  }
}
```

**Key fields explained:**

| Field | Purpose |
|-------|---------|
| `reason` | Why ECOS is requesting hibernation. One of: `idle` (no active work), `resource-saving` (freeing compute/tokens), `maintenance` (system maintenance window) |
| `expected_duration` | ISO 8601 duration (for example, `PT2H` for 2 hours, `P1D` for 1 day) or the string `unknown` if open-ended |
| `save_state` | Boolean. When `true`, EOA must persist its full state snapshot before hibernating. When `false`, EOA may discard transient state |
| `additional_instructions` | Optional free-text instructions from ECOS (for example, "Ensure agent svgbbox-programmer-001 commits before pausing") |

---

## 4. EOA Hibernate Acknowledgment to ECOS

**When to use:** EOA sends this after it has successfully paused all active agents, saved its state snapshot to a checkpoint file, and is ready to go offline. This acknowledgment includes a complete state snapshot so that ECOS (or a future EOA session) can restore operations.

> **Note**: Use the agent-messaging skill to send messages.

**JSON response template (EOA to ECOS):**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "ACK: Hibernate Directive - State Saved",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "Hibernate acknowledged. State saved to checkpoint. <N> agents paused. Ready to suspend.",
    "data": {
      "directive_ack": "hibernate",
      "state_snapshot": {
        "current_task_states": [
          {
            "task_id": "<task-uuid>",
            "title": "<task-title>",
            "status": "in-progress|blocked|queued|paused",
            "assigned_agent": "<agent-session-name-or-null>",
            "progress_pct": 0,
            "last_activity": "<ISO8601-timestamp>",
            "notes": "<brief-context>"
          }
        ],
        "agent_statuses": {
          "<agent-session-name>": {
            "status": "paused|offline|idle",
            "last_task": "<task-uuid-or-null>",
            "pause_acknowledged": true
          }
        },
        "pending_items": [
          {
            "type": "message|approval|review",
            "from": "<agent-or-entity>",
            "summary": "<brief-description>",
            "received_at": "<ISO8601-timestamp>"
          }
        ]
      },
      "checkpoint_file": "docs_dev/checkpoints/eoa-hibernate-<timestamp>.json",
      "agents_paused_count": 0,
      "all_agents_acknowledged_pause": true
    }
  }
}
```

**Key fields explained:**

| Field | Purpose |
|-------|---------|
| `state_snapshot.current_task_states` | Array of all tasks with their exact status at hibernation time |
| `state_snapshot.agent_statuses` | Map of every agent EOA manages, with their pause status |
| `state_snapshot.pending_items` | Unresolved items (messages awaiting reply, approvals pending, reviews not started) |
| `checkpoint_file` | Path to the JSON file where the full state snapshot is persisted on disk |
| `agents_paused_count` | Number of sub-agents that were actively running and have been paused |
| `all_agents_acknowledged_pause` | Boolean. `false` if any agent did not confirm its pause (requires ECOS attention) |

**Decision tree for EOA upon receiving Hibernate directive:**

```
EOA receives Hibernate directive from ECOS
    │
    ├─ Are any agents currently mid-task?
    │     ├─ Yes → Send pause directive to each active agent
    │     │     ├─ All agents acknowledge pause → Collect checkpoints from each
    │     │     │     └─ Save combined state snapshot to checkpoint file
    │     │     └─ Some agents do not acknowledge → Record non-responsive agents
    │     │           └─ Save state with all_agents_acknowledged_pause = false
    │     │                 └─ Send ACK to ECOS noting unresponsive agents
    │     └─ No agents mid-task → Save state snapshot immediately
    │
    ├─ Is save_state == true?
    │     ├─ Yes → Write checkpoint file to docs_dev/checkpoints/
    │     └─ No → Skip checkpoint file, include state_snapshot in ACK only
    │
    └─ Send Hibernate ACK to ECOS with state_snapshot and checkpoint_file path
```

---

## 5. ECOS Terminate Directive to EOA

**When to use:** ECOS sends this when EOA's session is ending permanently. Reasons include: the project is complete, an unrecoverable error requires a fresh start, or the user has requested manual shutdown. Unlike hibernate, terminate does not expect the session to resume.

> **Note**: Use the agent-messaging skill to send messages.

**JSON send template (ECOS to EOA):**

```json
{
  "from": "ecos-main",
  "to": "eoa-<project-name>",
  "subject": "Terminate Directive: End Session",
  "priority": "urgent",
  "content": {
    "type": "request",
    "message": "Terminate session. Compile final report if required. Shut down all managed agents.",
    "data": {
      "directive": "terminate",
      "reason": "project-complete|error|manual",
      "final_report_required": true,
      "additional_instructions": "<optional-special-instructions-or-null>"
    }
  }
}
```

**Key fields explained:**

| Field | Purpose |
|-------|---------|
| `reason` | Why the session is being terminated. One of: `project-complete` (all work done), `error` (unrecoverable failure), `manual` (user-requested shutdown) |
| `final_report_required` | Boolean. When `true`, EOA must compile and send a comprehensive final report before shutting down. When `false`, EOA may shut down immediately after saving state |
| `additional_instructions` | Optional instructions (for example, "Ensure all branches are pushed before terminating") |

---

## 6. EOA Final Termination Report to ECOS

**When to use:** EOA sends this as its last message before shutting down, but only when `final_report_required` was `true` in the terminate directive. This report provides a comprehensive summary of everything that happened during the session: completed work, remaining work, agent performance, and recommendations for the next session.

> **Note**: Use the agent-messaging skill to send messages.

**JSON response template (EOA to ECOS):**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "Final Termination Report: <project-name>",
  "priority": "urgent",
  "content": {
    "type": "response",
    "message": "Session terminated. Final report attached. <N> tasks completed, <M> tasks pending, <K> blockers remaining.",
    "data": {
      "directive_ack": "terminate",
      "completed_tasks": [
        {
          "task_id": "<task-uuid>",
          "title": "<task-title>",
          "completed_at": "<ISO8601-timestamp>",
          "outcome": "<brief-result-description>",
          "deliverables": ["<file-path-or-url>"]
        }
      ],
      "pending_tasks": [
        {
          "task_id": "<task-uuid>",
          "title": "<task-title>",
          "status": "in-progress|blocked|queued",
          "assigned_agent": "<agent-session-name-or-null>",
          "progress_pct": 0,
          "blockers": ["<blocker-description>"],
          "notes": "<context-for-next-session>"
        }
      ],
      "agent_summaries": {
        "<agent-session-name>": {
          "tasks_completed": 0,
          "tasks_failed": 0,
          "avg_task_duration_minutes": 0,
          "reliability_score": "high|medium|low",
          "notes": "<performance-observations>"
        }
      },
      "kanban_snapshot": {
        "backlog": 0,
        "in_progress": 0,
        "review": 0,
        "done": 0,
        "snapshot_file": "docs_dev/checkpoints/eoa-kanban-final-<timestamp>.md"
      },
      "blockers_remaining": [
        {
          "blocker_id": "<blocker-uuid>",
          "description": "<what-is-blocked-and-why>",
          "affected_tasks": ["<task-uuid>"],
          "escalated_to": "<agent-or-entity-or-null>",
          "suggested_resolution": "<recommended-action>"
        }
      ],
      "recommendations": {
        "for_next_session": [
          "<actionable-recommendation-1>",
          "<actionable-recommendation-2>"
        ],
        "architecture_concerns": ["<concern-if-any>"],
        "agent_roster_suggestions": "<suggestions-for-agent-team-composition>"
      }
    }
  }
}
```

**Key fields explained:**

| Field | Purpose |
|-------|---------|
| `completed_tasks` | Array of every task finished during this session, with outcomes and deliverables |
| `pending_tasks` | Array of every unfinished task, with progress and blocker details for the next session |
| `agent_summaries` | Performance summary for each agent EOA managed, including reliability scores |
| `kanban_snapshot` | Column counts and path to the final kanban state file |
| `blockers_remaining` | Unresolved blockers that the next session must address |
| `recommendations.for_next_session` | Actionable items the next EOA session should prioritize |
| `recommendations.architecture_concerns` | Design or architecture issues discovered during the session |
| `recommendations.agent_roster_suggestions` | Suggestions for which agents to spawn or retire in the next session |

**Decision tree for EOA upon receiving Terminate directive:**

```
EOA receives Terminate directive from ECOS
    │
    ├─ Is final_report_required == true?
    │     ├─ Yes → Compile final report
    │     │     ├─ Collect completed_tasks from session log
    │     │     ├─ Collect pending_tasks with current statuses
    │     │     ├─ Compile agent_summaries from performance data
    │     │     ├─ Snapshot kanban board to file
    │     │     ├─ List all blockers_remaining
    │     │     ├─ Formulate recommendations based on session experience
    │     │     ├─ Send Final Termination Report to ECOS
    │     │     └─ Shut down all managed agents, then self-terminate
    │     └─ No → Save minimal state to checkpoint file
    │           └─ Shut down all managed agents, then self-terminate
    │
    └─ Regardless of report: ensure all agents receive shutdown signal
          ├─ Active agents → Send terminate to each, wait for ACK (30s timeout)
          └─ Idle/paused agents → Send terminate, do not wait for ACK
```

---

## 7. EOA Periodic Status Report to ECOS (30-minute intervals)

**When to use:** EOA sends this report at regular intervals (default: every 30 minutes as configured in `session_config.status_report_interval_minutes`) to keep ECOS informed of ongoing operations. If nothing has changed since the last report, EOA sends a lightweight heartbeat-only variant instead of a full report.

> **Note**: Use the agent-messaging skill to send messages.

### 7a. Full Status Report (when changes occurred)

**JSON send template (EOA to ECOS):**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "Status Report: <project-name> - <ISO8601-timestamp>",
  "priority": "normal",
  "content": {
    "type": "status",
    "message": "Periodic status: <N> agents active, <M> tasks in progress, <K> completed since last report, <B> blockers.",
    "data": {
      "report_type": "full",
      "report_timestamp": "<ISO8601-timestamp>",
      "active_agents": {
        "count": 0,
        "list": [
          {
            "session_name": "<agent-session-name>",
            "role": "programmer|tester|reviewer",
            "current_task": "<task-uuid-or-null>",
            "status": "working|idle|blocked"
          }
        ]
      },
      "tasks_in_progress": [
        {
          "task_id": "<task-uuid>",
          "title": "<task-title>",
          "assigned_agent": "<agent-session-name>",
          "progress_pct": 0,
          "started_at": "<ISO8601-timestamp>",
          "estimated_completion": "<ISO8601-timestamp-or-null>"
        }
      ],
      "tasks_completed_since_last": [
        {
          "task_id": "<task-uuid>",
          "title": "<task-title>",
          "completed_at": "<ISO8601-timestamp>",
          "outcome": "success|partial|failed"
        }
      ],
      "blockers": [
        {
          "blocker_id": "<blocker-uuid>",
          "description": "<what-is-blocked>",
          "affected_tasks": ["<task-uuid>"],
          "waiting_on": "<agent-or-entity>",
          "since": "<ISO8601-timestamp>"
        }
      ],
      "next_milestones": [
        {
          "milestone": "<milestone-description>",
          "target_date": "<ISO8601-timestamp-or-null>",
          "dependency_tasks": ["<task-uuid>"]
        }
      ],
      "resource_utilization": {
        "agents_spawned_total": 0,
        "agents_currently_active": 0,
        "agents_paused": 0,
        "agents_terminated": 0,
        "max_concurrent_reached": 0
      }
    }
  }
}
```

### 7b. Heartbeat-Only Report (when no changes occurred)

**JSON send template (EOA to ECOS):**

```json
{
  "from": "eoa-<project-name>",
  "to": "ecos-main",
  "subject": "Heartbeat: <project-name> - <ISO8601-timestamp>",
  "priority": "low",
  "content": {
    "type": "status",
    "message": "Heartbeat: No changes since last report. <N> agents active, <M> tasks in progress.",
    "data": {
      "report_type": "heartbeat",
      "report_timestamp": "<ISO8601-timestamp>",
      "agents_active_count": 0,
      "tasks_in_progress_count": 0,
      "blockers_count": 0,
      "last_full_report_timestamp": "<ISO8601-timestamp>"
    }
  }
}
```

**Key fields explained (full report):**

| Field | Purpose |
|-------|---------|
| `report_type` | Either `full` (changes since last report) or `heartbeat` (no changes) |
| `active_agents.count` | Number of agents currently online and managed by EOA |
| `active_agents.list` | Details of each active agent including their current task and status |
| `tasks_in_progress` | Tasks currently being worked on, with progress percentages |
| `tasks_completed_since_last` | Tasks that finished since the previous status report |
| `blockers` | Unresolved blockers with details on what they are waiting for |
| `next_milestones` | Upcoming milestones and their dependency tasks |
| `resource_utilization` | Agent spawn and lifecycle statistics for the session |

**Decision tree for EOA periodic status report:**

```
30-minute status report timer fires
    │
    ├─ Any changes since last report?
    │     ├─ Yes (tasks completed, new blockers, agents spawned/terminated, etc.)
    │     │     ├─ Compile full status report (section 7a)
    │     │     │     ├─ Gather active_agents list from agent registry
    │     │     │     ├─ Gather tasks_in_progress from task tracker
    │     │     │     ├─ Gather tasks_completed_since_last from session log
    │     │     │     ├─ Gather current blockers
    │     │     │     ├─ Identify next_milestones
    │     │     │     ├─ Calculate resource_utilization
    │     │     │     └─ Send full report to ECOS
    │     │     └─ Reset "changes since last report" counter
    │     └─ No (nothing has changed)
    │           └─ Send heartbeat-only report (section 7b)
    │                 └─ Include reference to last full report timestamp
    │
    └─ Reset timer for next 30-minute interval
```

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| ECOS sends Wake but EOA does not respond | EOA session not started or crashed | ECOS should verify EOA session is running before sending Wake. If no response within 60 seconds, re-spawn EOA |
| EOA Wake ACK shows `ready_status: blocked` | Missing MCP server, unreachable dependency | Read the `degraded_reason` field. Fix the issue and send a new Wake directive |
| Hibernate ACK has `all_agents_acknowledged_pause: false` | Sub-agent crashed or is unresponsive | ECOS should force-terminate unresponsive agents and note them for investigation |
| Terminate report is empty | EOA had no tasks during the session | This is valid. Check `completed_tasks` and `pending_tasks` arrays are empty, not missing |
| Heartbeat reports stop arriving | EOA crashed or lost connection | ECOS should check EOA session status. If offline, attempt Wake or re-spawn |
| Status report shows `blockers` but no escalation was sent | EOA may not have reached escalation threshold | Check escalation protocol in [escalation-protocol.md](./escalation-protocol.md) for timing and priority rules |
| Checkpoint file path does not exist | Disk full or permission error | Verify `docs_dev/checkpoints/` directory exists and is writable. Create it if missing |
