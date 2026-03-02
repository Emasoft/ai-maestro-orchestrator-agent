# Response Templates from ECOS, EAMA, and EAA Back to EOA

This document provides structured templates for messages that EOA **receives** from ECOS (Chief of Staff), EAMA (Assistant Manager), and EAA (Architect Agent). For each response type, this reference includes the incoming message format, the processing instructions EOA must follow, and the decision tree for handling the response.

> All message templates below should be sent using the `agent-messaging` skill, which handles the AI Maestro API format automatically.

## Table of Contents

- [1. ECOS Response to EOA Task Completion Report](#1-ecos-response-to-eoa-task-completion-report)
  - [1.1 When ECOS accepts the completed task](#11-when-ecos-accepts-the-completed-task)
  - [1.2 When ECOS requests rework on the completed task](#12-when-ecos-requests-rework-on-the-completed-task)
  - [1.3 When ECOS requests clarification on the completed task](#13-when-ecos-requests-clarification-on-the-completed-task)
- [2. EAMA Response to EOA Blocker Escalation (User Decision)](#2-eama-response-to-eoa-blocker-escalation-user-decision)
  - [2.1 When EAMA delivers the user decision](#21-when-eama-delivers-the-user-decision)
  - [2.2 When the user defers the decision](#22-when-the-user-defers-the-decision)
  - [2.3 When the user rejects all proposed options](#23-when-the-user-rejects-all-proposed-options)
- [3. EAA Response to Design Issue Escalation](#3-eaa-response-to-design-issue-escalation)
  - [3.1 When EAA provides actionable design guidance](#31-when-eaa-provides-actionable-design-guidance)
  - [3.2 When EAA provides a revised design document](#32-when-eaa-provides-a-revised-design-document)
  - [3.3 When EAA requests more context before advising](#33-when-eaa-requests-more-context-before-advising)
- [4. ECOS Response to EOA Periodic Status Report](#4-ecos-response-to-eoa-periodic-status-report)
  - [4.1 When ECOS acknowledges with no further action](#41-when-ecos-acknowledges-with-no-further-action)
  - [4.2 When ECOS changes task priorities](#42-when-ecos-changes-task-priorities)
  - [4.3 When ECOS adds a new task](#43-when-ecos-adds-a-new-task)
- [5. EAMA Response to Immutable Requirement Escalation](#5-eama-response-to-immutable-requirement-escalation)
  - [5.1 When the user selects a standard option](#51-when-the-user-selects-a-standard-option)
  - [5.2 When the user proposes a custom resolution](#52-when-the-user-proposes-a-custom-resolution)
  - [5.3 When the user waives the requirement](#53-when-the-user-waives-the-requirement)

---

## 1. ECOS Response to EOA Task Completion Report

**When to use:** After EOA sends a task completion report to ECOS (using template 1.4 in [ai-maestro-message-templates.md](ai-maestro-message-templates.md)), ECOS reviews the result and responds with one of three statuses: `accepted`, `rework_requested`, or `clarification_requested`.

> **Note**: Use the agent-messaging skill to send messages.

### Incoming Response Template (ECOS to EOA)

```json
{
  "from": "ecos-main",
  "to": "eoa-<project-name>",
  "subject": "Completion Review: <task-name>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "<human-readable review outcome>",
    "data": {
      "task_uuid": "<task-uuid>",
      "review_status": "accepted|rework_requested|clarification_requested",
      "comments": "<review notes or empty string>",
      "corrections": ["<correction-1>", "<correction-2>"],
      "questions": ["<question-1>", "<question-2>"]
    }
  }
}
```

**Field descriptions:**
- `review_status`: One of `accepted` (task is done), `rework_requested` (task must be redone with corrections), or `clarification_requested` (ECOS needs more information before deciding)
- `comments`: Free-text notes from ECOS explaining the review outcome
- `corrections`: Array of specific items to fix (populated only when `review_status` is `rework_requested`, empty array otherwise)
- `questions`: Array of specific questions ECOS needs answered (populated only when `review_status` is `clarification_requested`, empty array otherwise)

### EOA Processing Instructions

#### 1.1 When ECOS accepts the completed task

When `review_status` is `accepted`:
1. Close the task in the kanban board by moving the card to the "Done" column
2. Update the GitHub issue with a comment recording ECOS acceptance
3. Close the GitHub issue: `gh issue close <issue-number> --comment "Task accepted by ECOS."`
4. Remove the task from the active task list
5. Send acknowledgment to ECOS confirming the task is closed

#### 1.2 When ECOS requests rework on the completed task

When `review_status` is `rework_requested`:
1. Move the kanban card back to "In Progress"
2. Add a comment to the GitHub issue with the corrections list from the `corrections` field
3. Forward the corrections to the agent that performed the task, using the task assignment template from [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.2, including the corrections in the message body
4. Set the task priority to `high` since rework is time-sensitive

#### 1.3 When ECOS requests clarification on the completed task

When `review_status` is `clarification_requested`:
1. Keep the kanban card in its current column (do not move it)
2. Gather the information needed to answer the questions in the `questions` field
3. If the information is available in the task report or agent output, compile it and reply to ECOS directly
4. If the information requires the original agent to provide it, forward the questions to that agent and wait for the response before replying to ECOS

### Decision Tree

```
EOA receives ECOS completion review response
    │
    ├─ review_status = "accepted"?
    │     ├─ Yes → Close task in kanban (move to Done)
    │     │         ├─ Update GitHub issue with acceptance comment
    │     │         ├─ Close GitHub issue
    │     │         ├─ Remove task from active list
    │     │         └─ Send ACK to ECOS
    │     └─ No → Continue checking
    │
    ├─ review_status = "rework_requested"?
    │     ├─ Yes → Move kanban card back to In Progress
    │     │         ├─ Comment corrections on GitHub issue
    │     │         ├─ Forward corrections to implementing agent
    │     │         └─ Set task priority to high
    │     └─ No → Continue checking
    │
    └─ review_status = "clarification_requested"?
          └─ Yes → Keep kanban card in current column
                    ├─ Can EOA answer from existing info?
                    │     ├─ Yes → Compile answer, reply to ECOS
                    │     └─ No → Forward questions to agent, wait for reply, then reply to ECOS
                    └─ (end)
```

---

## 2. EAMA Response to EOA Blocker Escalation (User Decision)

**When to use:** After EOA escalates a blocker to EAMA requesting user input (using template 1.6 in [ai-maestro-message-templates.md](ai-maestro-message-templates.md)), EAMA collects the user decision and responds with one of three statuses: `user_decision_delivered`, `user_deferred`, or `user_rejected_all`.

> **Note**: Use the agent-messaging skill to send messages.

### Incoming Response Template (EAMA to EOA)

```json
{
  "from": "eama-assistant-manager",
  "to": "eoa-<project-name>",
  "subject": "User Decision: <blocker-description>",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "<human-readable summary of user decision>",
    "data": {
      "task_uuid": "<task-uuid>",
      "blocker_issue_number": "<github-issue-number>",
      "decision_status": "user_decision_delivered|user_deferred|user_rejected_all",
      "chosen_option": "<option identifier or null>",
      "user_rationale": "<user explanation or empty string>",
      "defer_until": "<ISO8601 timestamp or null>",
      "additional_instructions": "<extra context from user or empty string>"
    }
  }
}
```

**Field descriptions:**
- `decision_status`: One of `user_decision_delivered` (user picked an option), `user_deferred` (user will decide later), or `user_rejected_all` (none of the proposed options are acceptable)
- `chosen_option`: The identifier of the option the user selected (matches one of the options EOA originally proposed). Set to `null` when `decision_status` is not `user_decision_delivered`
- `user_rationale`: The user's explanation for their choice, deferral, or rejection
- `defer_until`: ISO8601 timestamp indicating when to re-check with EAMA. Set to `null` when not deferred
- `additional_instructions`: Any extra context or constraints the user provided alongside their decision

### EOA Processing Instructions

#### 2.1 When EAMA delivers the user decision

When `decision_status` is `user_decision_delivered`:
1. Extract the `chosen_option` value from the response
2. Close the blocker GitHub issue: `gh issue close <blocker_issue_number> --comment "Resolved: user chose option <chosen_option>. Rationale: <user_rationale>"`
3. Remove the `status:blocked` label from the parent task issue and restore the previous status label
4. Move the kanban card from the Blocked column back to its previous column
5. Forward the decision to the blocked agent with instructions to proceed using the chosen option, including the `additional_instructions` if present
6. Send ACK to EAMA confirming the decision has been relayed

#### 2.2 When the user defers the decision

When `decision_status` is `user_deferred`:
1. Add a comment to the blocker GitHub issue: "User deferred decision. Will revisit by <defer_until>."
2. Keep the kanban card in the Blocked column
3. Record the `defer_until` timestamp as a reminder to re-check
4. Continue working on other non-blocked tasks
5. When the `defer_until` time arrives, send a follow-up escalation to EAMA reminding about the pending decision

#### 2.3 When the user rejects all proposed options

When `decision_status` is `user_rejected_all`:
1. Add a comment to the blocker GitHub issue: "User rejected all proposed options. Rationale: <user_rationale>. Escalating to ECOS for alternative approach."
2. Keep the kanban card in the Blocked column
3. Escalate to ECOS with a message explaining that the user rejected all options, including the `user_rationale`, and request ECOS to develop an alternative approach
4. Wait for ECOS to respond with a new set of options or a resolution strategy

### Decision Tree

```
EOA receives EAMA blocker response
    │
    ├─ decision_status = "user_decision_delivered"?
    │     ├─ Yes → Extract chosen_option
    │     │         ├─ Close blocker GitHub issue with decision
    │     │         ├─ Remove status:blocked label from parent task
    │     │         ├─ Move kanban card from Blocked to previous column
    │     │         ├─ Forward decision to blocked agent
    │     │         └─ Send ACK to EAMA
    │     └─ No → Continue checking
    │
    ├─ decision_status = "user_deferred"?
    │     ├─ Yes → Comment on blocker issue with deferral note
    │     │         ├─ Keep kanban card in Blocked column
    │     │         ├─ Set reminder for defer_until timestamp
    │     │         ├─ Continue other non-blocked work
    │     │         └─ Re-escalate to EAMA when defer_until arrives
    │     └─ No → Continue checking
    │
    └─ decision_status = "user_rejected_all"?
          └─ Yes → Comment rejection rationale on blocker issue
                    ├─ Keep kanban card in Blocked column
                    ├─ Escalate to ECOS for alternative approach
                    └─ Wait for ECOS response with new options
```

---

## 3. EAA Response to Design Issue Escalation

**When to use:** After EOA escalates a design issue to EAA (Architect Agent) because an agent encountered an architectural ambiguity, a design constraint conflict, or needs guidance on implementation approach. EAA responds with one of three statuses: `design_guidance`, `revised_design_doc`, or `investigate_further`.

> **Note**: Use the agent-messaging skill to send messages.

### Incoming Response Template (EAA to EOA)

```json
{
  "from": "eaa-<project-name>-architect",
  "to": "eoa-<project-name>",
  "subject": "Design Response: <issue-description>",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "<human-readable design advice summary>",
    "data": {
      "task_uuid": "<task-uuid>",
      "response_type": "design_guidance|revised_design_doc|investigate_further",
      "guidance": "<actionable architectural advice or empty string>",
      "design_doc_path": "<path to updated design document or null>",
      "adr_path": "<path to new Architecture Decision Record or null>",
      "questions_for_agent": ["<question-1>", "<question-2>"],
      "constraints": ["<constraint-1>", "<constraint-2>"]
    }
  }
}
```

**Field descriptions:**
- `response_type`: One of `design_guidance` (textual architectural advice the agent can follow), `revised_design_doc` (EAA updated the design document to resolve the ambiguity), or `investigate_further` (EAA needs more context from the agent before providing guidance)
- `guidance`: Actionable text describing what approach the agent should take. Populated when `response_type` is `design_guidance`, empty string otherwise
- `design_doc_path`: File path to the updated design/handoff document. Populated when `response_type` is `revised_design_doc`, `null` otherwise
- `adr_path`: File path to a new Architecture Decision Record if EAA created one. Can be `null`
- `questions_for_agent`: Array of questions EAA needs the agent to answer. Populated when `response_type` is `investigate_further`, empty array otherwise
- `constraints`: Array of architectural constraints the agent must respect when implementing the guidance

### EOA Processing Instructions

#### 3.1 When EAA provides actionable design guidance

When `response_type` is `design_guidance`:
1. Read the `guidance` field and verify it is specific enough for the agent to act on
2. Forward the guidance to the implementing agent, including any items in the `constraints` array as mandatory rules
3. If an ADR was created (check `adr_path`), instruct the agent to read the ADR before proceeding
4. Add a comment to the GitHub issue recording the design guidance received
5. Send ACK to EAA confirming the guidance has been relayed

#### 3.2 When EAA provides a revised design document

When `response_type` is `revised_design_doc`:
1. Read the updated design document at the path specified in `design_doc_path`
2. Update the handoff document reference in the task tracking to point to the new document
3. Notify the implementing agent that the design document has been revised and they must re-read it before continuing work
4. If an ADR was created (check `adr_path`), instruct the agent to read the ADR as well
5. Add a comment to the GitHub issue referencing the updated design document path
6. Send ACK to EAA confirming the updated document has been distributed

#### 3.3 When EAA requests more context before advising

When `response_type` is `investigate_further`:
1. Read the questions in the `questions_for_agent` array
2. Forward these questions to the implementing agent that originally raised the design issue
3. Wait for the agent to respond with the requested context
4. Once the agent responds, compile the answers and send them back to EAA as a follow-up message
5. Do not close or modify the GitHub issue until EAA provides a final design response

### Decision Tree

```
EOA receives EAA design response
    │
    ├─ response_type = "design_guidance"?
    │     ├─ Yes → Is guidance specific and actionable?
    │     │         ├─ Yes → Forward guidance + constraints to agent
    │     │         │         ├─ ADR created? → Yes: instruct agent to read ADR
    │     │         │         │                 No: skip
    │     │         │         ├─ Comment on GitHub issue
    │     │         │         └─ Send ACK to EAA
    │     │         └─ No → Reply to EAA requesting more specific guidance
    │     └─ No → Continue checking
    │
    ├─ response_type = "revised_design_doc"?
    │     ├─ Yes → Read updated design document
    │     │         ├─ Update handoff doc reference in task tracking
    │     │         ├─ Notify agent to re-read design document
    │     │         ├─ ADR created? → Yes: instruct agent to read ADR
    │     │         │                 No: skip
    │     │         ├─ Comment on GitHub issue with new doc path
    │     │         └─ Send ACK to EAA
    │     └─ No → Continue checking
    │
    └─ response_type = "investigate_further"?
          └─ Yes → Forward questions_for_agent to implementing agent
                    ├─ Wait for agent response
                    ├─ Compile answers
                    ├─ Send compiled answers back to EAA
                    └─ Keep GitHub issue open until final EAA response
```

---

## 4. ECOS Response to EOA Periodic Status Report

**When to use:** After EOA sends its periodic status report to ECOS (summarizing progress across all active tasks, agent health, and blockers), ECOS reviews the report and responds with one of three statuses: `acknowledged`, `priority_change`, or `additional_task`.

> **Note**: Use the agent-messaging skill to send messages.

### Incoming Response Template (ECOS to EOA)

```json
{
  "from": "ecos-main",
  "to": "eoa-<project-name>",
  "subject": "Status Report Review: <report-date>",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "<human-readable response to status report>",
    "data": {
      "review_type": "acknowledged|priority_change|additional_task",
      "priority_changes": [
        {
          "task_uuid": "<task-uuid>",
          "old_priority": "normal|high|urgent",
          "new_priority": "normal|high|urgent",
          "reason": "<why priority changed>"
        }
      ],
      "new_task": {
        "task_name": "<name or null>",
        "task_description": "<description or null>",
        "priority": "normal|high|urgent",
        "deadline": "<ISO8601 or null>",
        "acceptance_criteria": ["<criterion-1>"],
        "handoff_doc": "<path or null>"
      },
      "comments": "<additional notes from ECOS>"
    }
  }
}
```

**Field descriptions:**
- `review_type`: One of `acknowledged` (ECOS has no further action), `priority_change` (ECOS wants to adjust priorities for existing tasks), or `additional_task` (ECOS is adding a new task based on the status report)
- `priority_changes`: Array of priority change objects. Each contains the `task_uuid` of the task to change, the `old_priority`, the `new_priority`, and the `reason` for the change. Populated only when `review_type` is `priority_change`, empty array otherwise
- `new_task`: Object describing a new task to add. All fields are `null` when `review_type` is not `additional_task`
- `comments`: Free-text notes from ECOS about the status report

### EOA Processing Instructions

#### 4.1 When ECOS acknowledges with no further action

When `review_type` is `acknowledged`:
1. Log the acknowledgment (no action required)
2. Continue normal operations
3. If `comments` is non-empty, review the comments for any informal suggestions and consider them for future reports

#### 4.2 When ECOS changes task priorities

When `review_type` is `priority_change`:
1. For each entry in the `priority_changes` array:
   - Locate the task by `task_uuid` in the kanban board
   - Update the task priority label from `old_priority` to `new_priority`
   - Add a comment to the GitHub issue: "Priority changed from <old_priority> to <new_priority>. Reason: <reason>"
   - If the task is currently assigned to an agent, notify that agent about the priority change
2. Re-sort the task queue based on the updated priorities
3. Send ACK to ECOS listing which tasks had their priority changed

#### 4.3 When ECOS adds a new task

When `review_type` is `additional_task`:
1. Create a new GitHub issue for the task using the data in the `new_task` object
2. Create a kanban card in the "To Do" column
3. If a `handoff_doc` path is provided, verify the document exists and is readable
4. Assign the task to an available agent following the standard task assignment process (see [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.2)
5. Send ACK to ECOS confirming the new task has been created and assigned

### Decision Tree

```
EOA receives ECOS status report response
    │
    ├─ review_type = "acknowledged"?
    │     ├─ Yes → Log acknowledgment
    │     │         ├─ Comments present? → Yes: review for suggestions
    │     │         │                      No: skip
    │     │         └─ Continue normal operations
    │     └─ No → Continue checking
    │
    ├─ review_type = "priority_change"?
    │     ├─ Yes → For each entry in priority_changes:
    │     │         ├─ Update task priority label on kanban
    │     │         ├─ Comment on GitHub issue with reason
    │     │         ├─ Task assigned to agent?
    │     │         │     ├─ Yes → Notify agent of priority change
    │     │         │     └─ No → Skip notification
    │     │         └─ (next entry)
    │     │         After all entries processed:
    │     │         ├─ Re-sort task queue by priority
    │     │         └─ Send ACK to ECOS
    │     └─ No → Continue checking
    │
    └─ review_type = "additional_task"?
          └─ Yes → Create GitHub issue from new_task data
                    ├─ Create kanban card in To Do column
                    ├─ Handoff doc provided?
                    │     ├─ Yes → Verify doc exists and is readable
                    │     └─ No → Skip
                    ├─ Assign task to available agent
                    └─ Send ACK to ECOS
```

---

## 5. EAMA Response to Immutable Requirement Escalation

**When to use:** After EOA escalates to EAMA because an agent cannot satisfy an immutable project requirement (a requirement that cannot be changed without explicit user approval). This happens when there is a hard conflict between a requirement and the technical reality (for example, a required dependency is unavailable, a performance target is physically impossible, or a required integration API does not exist). EAMA collects the user decision and responds with one of three statuses: `option_selected`, `custom_resolution`, or `requirement_waived`.

> **Note**: Use the agent-messaging skill to send messages.

### Incoming Response Template (EAMA to EOA)

```json
{
  "from": "eama-assistant-manager",
  "to": "eoa-<project-name>",
  "subject": "Requirement Resolution: <requirement-description>",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "<human-readable summary of user resolution>",
    "data": {
      "task_uuid": "<task-uuid>",
      "requirement_id": "<requirement identifier>",
      "resolution_type": "option_selected|custom_resolution|requirement_waived",
      "selected_option": "<option identifier or null>",
      "custom_solution": "<user-proposed solution text or null>",
      "waiver_scope": "<what is waived or null>",
      "user_rationale": "<user explanation>",
      "updated_constraints": ["<new-constraint-1>", "<new-constraint-2>"]
    }
  }
}
```

**Field descriptions:**
- `resolution_type`: One of `option_selected` (user picked one of the predefined options A/B/C that EOA proposed), `custom_resolution` (user proposed a different solution not in the original options), or `requirement_waived` (user decided to remove the requirement entirely)
- `selected_option`: The option identifier the user chose (for example, "A", "B", or "C"). Set to `null` unless `resolution_type` is `option_selected`
- `custom_solution`: The user's own proposed solution text. Set to `null` unless `resolution_type` is `custom_resolution`
- `waiver_scope`: Description of exactly what is being waived (for example, "Performance target for module X reduced from 100ms to 500ms"). Set to `null` unless `resolution_type` is `requirement_waived`
- `user_rationale`: The user's explanation for their decision
- `updated_constraints`: Array of any new constraints the user attached to their decision (for example, "Must still pass security audit" even if a performance requirement is waived)

### EOA Processing Instructions

#### 5.1 When the user selects a standard option

When `resolution_type` is `option_selected`:
1. Identify the selected option from the `selected_option` field
2. Map the option to the specific implementation approach that EOA originally proposed
3. Add a comment to the GitHub issue: "Requirement conflict resolved. User selected option <selected_option>. Rationale: <user_rationale>"
4. Forward the chosen implementation approach to the implementing agent, including any `updated_constraints`
5. Remove the `status:blocked` label from the task and restore the previous status label
6. Move the kanban card from Blocked to its previous column
7. Send ACK to EAMA confirming the option is being implemented

#### 5.2 When the user proposes a custom resolution

When `resolution_type` is `custom_resolution`:
1. Read the `custom_solution` text carefully
2. Evaluate whether the custom solution is technically feasible given the current project state and agent capabilities
3. If feasible:
   - Add a comment to the GitHub issue: "Requirement conflict resolved with custom solution. Details: <custom_solution>"
   - Forward the custom solution to the implementing agent with any `updated_constraints`
   - Remove `status:blocked` label and restore previous status label
   - Move kanban card from Blocked to its previous column
   - Send ACK to EAMA confirming feasibility and implementation start
4. If not feasible:
   - Reply to EAMA explaining why the custom solution is not feasible, providing specific technical reasons
   - Include alternative suggestions if possible
   - Keep the task in Blocked status until EAMA responds with a revised solution

#### 5.3 When the user waives the requirement

When `resolution_type` is `requirement_waived`:
1. Read the `waiver_scope` to understand exactly what is being removed
2. Update the project requirements document to reflect the waiver, noting the `user_rationale`
3. Add a comment to the GitHub issue: "Requirement waived by user. Scope: <waiver_scope>. Rationale: <user_rationale>"
4. Notify the implementing agent that the previously blocking requirement has been removed
5. Include any `updated_constraints` in the notification (the user may have added replacement constraints)
6. Remove `status:blocked` label and restore previous status label
7. Move kanban card from Blocked to its previous column
8. Send ACK to EAMA confirming the requirement has been waived and the agent has been notified

### Decision Tree

```
EOA receives EAMA requirement resolution response
    │
    ├─ resolution_type = "option_selected"?
    │     ├─ Yes → Map selected_option to implementation approach
    │     │         ├─ Comment on GitHub issue with decision
    │     │         ├─ Forward approach + updated_constraints to agent
    │     │         ├─ Remove status:blocked, restore previous status
    │     │         ├─ Move kanban card from Blocked to previous column
    │     │         └─ Send ACK to EAMA
    │     └─ No → Continue checking
    │
    ├─ resolution_type = "custom_resolution"?
    │     ├─ Yes → Evaluate custom_solution feasibility
    │     │         ├─ Feasible?
    │     │         │     ├─ Yes → Comment on GitHub issue
    │     │         │     │         ├─ Forward solution + updated_constraints to agent
    │     │         │     │         ├─ Remove status:blocked, restore previous status
    │     │         │     │         ├─ Move kanban card from Blocked to previous column
    │     │         │     │         └─ Send ACK to EAMA (feasible, implementing)
    │     │         │     └─ No → Reply to EAMA with infeasibility explanation
    │     │         │               ├─ Include technical reasons
    │     │         │               ├─ Suggest alternatives if possible
    │     │         │               └─ Keep task in Blocked status
    │     │         └─ (end)
    │     └─ No → Continue checking
    │
    └─ resolution_type = "requirement_waived"?
          └─ Yes → Read waiver_scope
                    ├─ Update project requirements document
                    ├─ Comment on GitHub issue with waiver details
                    ├─ Notify agent: requirement removed + updated_constraints
                    ├─ Remove status:blocked, restore previous status
                    ├─ Move kanban card from Blocked to previous column
                    └─ Send ACK to EAMA
```

---

## Cross-Reference

| EOA Outgoing Template | Described In | Expected Response | Described In This File |
|---|---|---|---|
| Task Completion Report (EOA to ECOS) | [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.4 | ECOS Completion Review | Section 1 above |
| Blocker Escalation (EOA to EAMA) | [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.6 | EAMA User Decision | Section 2 above |
| Design Issue Escalation (EOA to EAA) | [message-templates.md](message-templates.md) section 2.9 | EAA Design Response | Section 3 above |
| Periodic Status Report (EOA to ECOS) | [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.4 | ECOS Status Review | Section 4 above |
| Immutable Requirement Escalation (EOA to EAMA) | [ai-maestro-message-templates.md](ai-maestro-message-templates.md) section 1.6 | EAMA Requirement Resolution | Section 5 above |
