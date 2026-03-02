# Multi-Project Coordination and Human Developer Assignment Templates

This document provides message templates for cross-project dependency coordination between Orchestrator Agents (EOA) and for assigning tasks to human developers via GitHub issues.

---

## Contents

- [1. Cross-Project Dependency Notification (EOA to EOA via ECOS)](#1-cross-project-dependency-notification-eoa-to-eoa-via-ecos)
- [2. Cross-Project Status Request (EOA to ECOS to Other EOA)](#2-cross-project-status-request-eoa-to-ecos-to-other-eoa)
- [3. Cross-Project Status Response (Other EOA to ECOS to EOA)](#3-cross-project-status-response-other-eoa-to-ecos-to-eoa)
- [4. Human Developer Task Assignment (EOA to GitHub)](#4-human-developer-task-assignment-eoa-to-github)
- [5. Human Developer Completion Report (GitHub to EOA)](#5-human-developer-completion-report-github-to-eoa)
- [6. Cross-Project Conflict Decision Tree](#6-cross-project-conflict-decision-tree)

---

## 1. Cross-Project Dependency Notification (EOA to EOA via ECOS)

**When to use**: The EOA discovers that one of its tasks depends on a deliverable from another project. The EOA cannot contact the other project's EOA directly. Instead, the EOA sends the notification to ECOS, which routes it to the correct project's EOA.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-{project}-orchestrator",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "[CROSS-DEP] {requesting_project} depends on {target_project}",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Cross-project dependency detected. My project requires a deliverable from another project before a blocking task can proceed. Please route this notification to the target project's EOA.",
    "data": {
      "requesting_project": "{requesting_project_name}",
      "target_project": "{target_project_name}",
      "dependency_type": "api|library|data|design",
      "dependency_description": "Description of the specific deliverable needed",
      "blocking_task_id": "GH-{issue_number}",
      "requested_completion_by": "YYYY-MM-DD"
    }
  }
}
```

### Response Template (ECOS to Requesting EOA)

```json
{
  "from": "ecos-chief-of-staff-main-agent",
  "to": "eoa-{project}-orchestrator",
  "subject": "RE: [CROSS-DEP] {requesting_project} depends on {target_project}",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "Dependency notification routed to target project's EOA. Current status of the target deliverable is included below.",
    "data": {
      "routed_to": "eoa-{target_project}-orchestrator",
      "target_deliverable_status": "not_started|in_progress|blocked|completed",
      "estimated_delivery": "YYYY-MM-DD",
      "notes": "Any relevant context from the target EOA"
    }
  }
}
```

### Decision Tree

```
Cross-project dependency detected
├─ Is the dependency type known?
│   ├─ Yes (api/library/data/design) ─→ Fill template with dependency_type
│   └─ No ─→ Investigate the dependency before sending notification
├─ Is there a blocking task ID (GitHub issue)?
│   ├─ Yes ─→ Include blocking_task_id in the message
│   └─ No ─→ Create a GitHub issue for the blocked task first
└─ Send notification to ECOS
    ├─ ECOS acknowledges ─→ Wait for routed response
    └─ No acknowledgment within 30 minutes ─→ Resend with priority "urgent"
```

---

## 2. Cross-Project Status Request (EOA to ECOS to Other EOA)

**When to use**: The EOA needs to know the current progress, blockers, estimated completion time, or deliverable readiness of another project. The request goes through ECOS, which queries the other project's EOA on behalf of the requesting EOA.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template

```json
{
  "from": "eoa-{project}-orchestrator",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "[STATUS-REQ] Query {target_project} status",
  "priority": "normal",
  "content": {
    "type": "request",
    "message": "Requesting status information from another project. Please forward this query to the target project's EOA and relay their response back.",
    "data": {
      "target_project": "{target_project_name}",
      "query_type": "progress|blocker|eta|deliverable",
      "context": "Why this information is needed and what decision depends on it"
    }
  }
}
```

### Response Template (ECOS Relays Target EOA Response)

```json
{
  "from": "ecos-chief-of-staff-main-agent",
  "to": "eoa-{project}-orchestrator",
  "subject": "RE: [STATUS-REQ] Query {target_project} status",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Status response from {target_project}'s EOA relayed below.",
    "data": {
      "target_project": "{target_project_name}",
      "query_type": "progress|blocker|eta|deliverable",
      "response_summary": "Summary of the target EOA's response",
      "raw_response": "Verbatim response from the target EOA"
    }
  }
}
```

### Decision Tree

```
Need information about another project
├─ Identify the query type
│   ├─ progress ─→ Ask for overall completion percentage and current phase
│   ├─ blocker ─→ Ask what is blocking the target project
│   ├─ eta ─→ Ask for estimated completion date of a specific deliverable
│   └─ deliverable ─→ Ask if a specific output artifact is ready to consume
├─ Include context explaining why this information is needed
└─ Send to ECOS
    ├─ Response received ─→ Process and plan accordingly
    └─ No response within 1 hour ─→ Resend with priority "high"
```

---

## 3. Cross-Project Status Response (Other EOA to ECOS to EOA)

**When to use**: The EOA receives a status query from ECOS (forwarded from another project's EOA) and must respond with the requested information. The response goes back through ECOS, which relays it to the requesting EOA.

> **Note**: Use the agent-messaging skill to send messages.

### Send Template (Target EOA Responds to ECOS)

```json
{
  "from": "eoa-{target_project}-orchestrator",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "RE: [STATUS-REQ] Response for {requesting_project}",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Responding to cross-project status query from {requesting_project}. Please relay this response to the requesting EOA.",
    "data": {
      "requesting_project": "{requesting_project_name}",
      "query_type": "progress|blocker|eta|deliverable",
      "answer": "Detailed answer to the status query",
      "current_phase": "Phase name or description",
      "completion_percentage": 0,
      "known_blockers": [],
      "estimated_delivery": "YYYY-MM-DD"
    }
  }
}
```

### Decision Tree

```
Received a cross-project status query from ECOS
├─ Identify the query type from the incoming message
│   ├─ progress ─→ Report current phase and completion percentage
│   ├─ blocker ─→ List all active blockers and their severity
│   ├─ eta ─→ Calculate and report estimated delivery date
│   └─ deliverable ─→ Confirm readiness or report remaining work
├─ Gather accurate information from local task tracking
│   ├─ Information available ─→ Respond with full data fields
│   └─ Information incomplete ─→ Respond with what is known, note unknowns
└─ Send response to ECOS for relay
```

---

## 4. Human Developer Task Assignment (EOA to GitHub)

**When to use**: The EOA determines that a task requires a human developer (not an AI agent). The EOA creates a GitHub issue with a specific format that human developers can pick up, including acceptance criteria, deadline, and the label `assigned-to-human` to distinguish it from AI agent tasks.

> **Note**: Use the agent-messaging skill to send messages.

### GitHub Issue Creation Template

Use the `gh` CLI to create the issue:

```bash
gh issue create \
  --title "{issue_title}" \
  --body "$(cat <<'ISSUE_BODY'
## Task Description

{task_description}

## Acceptance Criteria

- [ ] {criterion_1}
- [ ] {criterion_2}
- [ ] {criterion_3}

## Deadline

**Target completion**: {deadline_date}

## Context

- Assigned by: EOA ({project_name} Orchestrator)
- Related issues: {related_issue_numbers}
- Priority: {priority}

## Instructions for Human Developer

1. Review the acceptance criteria above
2. Create a feature branch from `main`
3. Implement the changes
4. Ensure all acceptance criteria checkboxes can be checked
5. Open a Pull Request referencing this issue (use `Closes #{issue_number}`)
6. Request review if required

**Note**: When the PR is merged and this issue is closed, the EOA will automatically detect the completion and integrate the deliverable.
ISSUE_BODY
)" \
  --assignee "{github_username}" \
  --label "assigned-to-human,{priority_label},{component_label}"
```

### Send Template (EOA Notifies ECOS of Human Assignment)

```json
{
  "from": "eoa-{project}-orchestrator",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "[HUMAN-ASSIGN] Task assigned to human developer: {github_username}",
  "priority": "normal",
  "content": {
    "type": "notification",
    "message": "A task has been assigned to a human developer via GitHub issue. Tracking will be done through GitHub issue events.",
    "data": {
      "assignee": "{github_username}",
      "issue_title": "{issue_title}",
      "issue_number": 0,
      "issue_url": "https://github.com/{owner}/{repo}/issues/{number}",
      "labels": ["assigned-to-human", "{priority_label}", "{component_label}"],
      "deadline": "YYYY-MM-DD"
    }
  }
}
```

### Decision Tree

```
Task requires human developer (not AI agent)
├─ Does a GitHub issue already exist for this task?
│   ├─ Yes ─→ Update existing issue with assignment and labels
│   └─ No ─→ Create new issue using the template above
├─ Assign to the correct human developer
│   ├─ Developer known ─→ Use --assignee with their GitHub username
│   └─ Developer not known ─→ Add label "help-wanted", escalate to ECOS
├─ Add the "assigned-to-human" label to distinguish from AI tasks
├─ Notify ECOS of the human assignment
└─ Set up monitoring for issue close events
    ├─ Poll periodically: gh issue view {number} --json state
    └─ When state changes to "closed" ─→ Proceed to Section 5
```

---

## 5. Human Developer Completion Report (GitHub to EOA)

**When to use**: The EOA detects that a GitHub issue assigned to a human developer has been closed. The EOA retrieves the completion details including any linked Pull Request URL and completion notes from the issue comments. This triggers the integration of the human developer's deliverable into the project workflow.

> **Note**: Use the agent-messaging skill to send messages.

### Monitoring Command

```bash
# Check if a human-assigned issue has been closed
gh issue view {issue_number} --json state,closedAt,comments,linkedPullRequests
```

### Incoming Data (Parsed from GitHub)

When the issue is closed, extract the following fields:

| Field | Source | Description |
|-------|--------|-------------|
| `issue_number` | GitHub issue number | The closed issue identifier |
| `pr_url` | `linkedPullRequests[0].url` | URL of the linked Pull Request, if any |
| `completion_notes` | Last comment body on the issue | Any notes the developer left upon closing |

### Send Template (EOA Notifies ECOS of Human Completion)

```json
{
  "from": "eoa-{project}-orchestrator",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "[HUMAN-DONE] Human developer completed GH-{issue_number}",
  "priority": "normal",
  "content": {
    "type": "notification",
    "message": "A human-assigned task has been completed. The GitHub issue has been closed. Deliverable integration will proceed.",
    "data": {
      "issue_number": 0,
      "pr_url": "https://github.com/{owner}/{repo}/pull/{pr_number}",
      "completion_notes": "Notes extracted from the closing comment",
      "closed_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  }
}
```

### Decision Tree

```
Human-assigned GitHub issue close event detected
├─ Was a Pull Request linked to the issue?
│   ├─ Yes ─→ Verify PR was merged (not just closed)
│   │         ├─ PR merged ─→ Pull latest code, run integration tests
│   │         └─ PR closed without merge ─→ Reopen issue, ask developer for clarification
│   └─ No ─→ Check if deliverable was committed directly to main
│             ├─ Commits found ─→ Pull latest code, run integration tests
│             └─ No commits found ─→ Reopen issue, request deliverable evidence
├─ Were all acceptance criteria met?
│   ├─ Yes ─→ Mark task complete, notify ECOS, unblock dependent tasks
│   └─ No ─→ Reopen issue with comment listing unmet criteria
└─ Update local task tracking with completion timestamp
```

---

## 6. Cross-Project Conflict Decision Tree

**When to use**: The EOA detects that one of its tasks depends on a deliverable from another project. Use this decision tree to determine the correct course of action based on whether the dependency is critical-path (blocking progress) or nice-to-have (improves quality but is not strictly required).

> **Note**: Use the agent-messaging skill to send messages.

### Decision Tree

```
Cross-project dependency detected
│
├─ Is dependency critical-path?
│   │
│   ├─ YES (blocking: cannot proceed without it)
│   │   │
│   │   ├─ Is other project's delivery on schedule?
│   │   │   │
│   │   │   ├─ YES (on track, expected on time)
│   │   │   │   └─ Request priority notification when ready
│   │   │   │       Action: Send Section 1 template with priority "high"
│   │   │   │       Action: Set local task status to "waiting-on-dependency"
│   │   │   │       Action: Continue other non-blocked tasks
│   │   │   │
│   │   │   └─ NO (delayed or at risk)
│   │   │       │
│   │   │       ├─ Can task proceed with assumptions?
│   │   │       │   │
│   │   │       │   ├─ YES (assumptions are safe to make)
│   │   │       │   │   └─ Proceed with assumptions, verify later
│   │   │       │   │       Action: Document assumptions in GitHub issue comment
│   │   │       │   │       Action: Add label "has-assumptions" to the blocked task
│   │   │       │   │       Action: Set reminder to verify when dependency arrives
│   │   │       │   │
│   │   │       │   └─ NO (assumptions too risky or impossible)
│   │   │       │       └─ Escalate to ECOS for cross-project priority adjustment
│   │   │       │           Action: Send Section 1 template with priority "urgent"
│   │   │       │           Action: Include impact analysis in the message
│   │   │       │           Action: Set local task status to "blocked-escalated"
│   │   │
│   └─ NO (nice-to-have: improves output but not strictly required)
│       │
│       └─ Set monitoring, continue without blocking
│           Action: Send Section 1 template with priority "normal"
│           Action: Continue task execution without waiting
│           │
│           ├─ Dependency delivered ─→ Integrate when available
│           │   Action: Pull deliverable into current project
│           │   Action: Run integration verification
│           │   Action: Update task with improved output
│           │
│           └─ Dependency delayed beyond project deadline ─→ Skip, note as known limitation
│               Action: Add comment to GitHub issue documenting the limitation
│               Action: Add label "known-limitation" to the task
│               Action: Proceed with delivery, note gap in release notes
```
