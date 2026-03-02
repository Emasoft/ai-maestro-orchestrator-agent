# Mid-Task Update Templates

Templates for handling changes that occur while agents are actively working on assigned tasks. These templates cover three scenarios: receiving requirement updates from the Chief of Staff (ECOS), relaying module or priority modifications to working agents, and processing user decisions forwarded by the Assistant Manager (EAMA).

---

## Table of Contents

- 1. ECOS Mid-Task Requirement Update (ECOS to EOA)
  - 1.1 When to use this template
  - 1.2 Incoming message template from ECOS
  - 1.3 Decision tree for processing the update
- 2. EOA Acknowledgment of Requirement Update (EOA to ECOS)
  - 2.1 When to use this template
  - 2.2 Acknowledgment message template
  - 2.3 Decision tree for composing the acknowledgment
- 3. Module Modification Notification (EOA to Agent)
  - 3.1 When to use this template
  - 3.2 Notification message template
  - 3.3 Expected agent response template
  - 3.4 Decision tree for module modification handling
- 4. Priority Change Notification (EOA to Agent)
  - 4.1 When to use this template
  - 4.2 Notification message template
  - 4.3 Expected agent response template
  - 4.4 Decision tree for priority change handling
- 5. EAMA User Decision Response (EAMA to EOA)
  - 5.1 When to use this template
  - 5.2 Incoming decision message from EAMA
  - 5.3 Relay message to affected agent
  - 5.4 Decision tree for processing user decisions
- 6. Mid-Task Update Severity Decision Tree
  - 6.1 Full decision tree diagram
  - 6.2 Severity classification rules
  - 6.3 Timing considerations

---

## 1. ECOS Mid-Task Requirement Update (ECOS to EOA)

### 1.1 When to use this template

Use this template when the Chief of Staff (ECOS) sends a requirement change after task delegation has already occurred. This happens when the Architect (EAA) revises specifications, when the user changes scope through EAMA, or when external constraints force a requirement adjustment.

> **Note**: Use the agent-messaging skill to send messages.

### 1.2 Incoming message template from ECOS

This is the message format EOA receives from ECOS. EOA does not send this message; EOA receives and processes it.

```json
{
  "from": "ecos-chief-of-staff-main-agent",
  "to": "eoa-orchestrator-main-agent",
  "subject": "Mid-Task Requirement Update - [task identifier]",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Requirement update for active task. Review affected modules and relay changes to assigned agents.",
    "data": {
      "task_id": "TASK-0042",
      "change_type": "scope_change",
      "affected_modules": ["module-auth", "module-api"],
      "new_requirements": "Authentication must support OAuth2 in addition to API keys",
      "old_requirements": "Authentication via API keys only",
      "justification": "User requested OAuth2 support after reviewing initial implementation plan"
    }
  }
}
```

Field definitions for `data`:
- `task_id`: The identifier of the task being modified. Must match a task that EOA has already delegated to an agent.
- `change_type`: One of three severity levels:
  - `minor_clarification`: Small detail added or corrected. Does not change the scope or interfaces. Example: clarifying a field name format.
  - `scope_change`: The boundaries of the task expand, shrink, or shift. Interfaces or modules may be added or removed. Example: adding OAuth2 support to an auth module.
  - `breaking_change`: Fundamental assumptions of the current implementation are invalidated. The agent may need to discard significant work. Example: switching from REST to GraphQL API architecture.
- `affected_modules`: Array of module identifiers that are impacted by the change. EOA uses this list to determine which agents to notify.
- `new_requirements`: Plain text description of what the updated requirements are.
- `old_requirements`: Plain text description of what the requirements were before the change. Included so EOA and agents can understand what shifted.
- `justification`: Explanation of why the change is happening. EOA relays this to agents so they understand the reasoning.

### 1.3 Decision tree for processing the update

```
Requirement update received from ECOS
│
├─ Is the task_id recognized?
│   ├─ Yes → Identify assigned agent(s) for affected_modules
│   │         │
│   │         ├─ change_type is "minor_clarification"
│   │         │   └─ Relay to agent immediately (Section 3)
│   │         │       └─ Send ACK to ECOS (Section 2)
│   │         │
│   │         ├─ change_type is "scope_change"
│   │         │   ├─ Send pause instruction to agent
│   │         │   ├─ Assess impact on timeline
│   │         │   ├─ Send ACK to ECOS with impact assessment (Section 2)
│   │         │   └─ Send module modification to agent (Section 3)
│   │         │
│   │         └─ change_type is "breaking_change"
│   │             ├─ Send stop instruction to agent immediately
│   │             ├─ Escalate to EAA for re-planning if needed
│   │             ├─ Send ACK to ECOS with severity assessment (Section 2)
│   │             └─ Wait for EAA re-plan before sending new instructions
│   │
│   └─ No → Reply to ECOS with error: task_id not found in active assignments
│
└─ Is the message malformed or missing required fields?
    └─ Yes → Reply to ECOS requesting corrected message
```

---

## 2. EOA Acknowledgment of Requirement Update (EOA to ECOS)

### 2.1 When to use this template

Send this acknowledgment after receiving and processing a mid-task requirement update from ECOS (Section 1). ECOS expects an acknowledgment confirming that EOA has understood the change and has begun relaying it to affected agents.

> **Note**: Use the agent-messaging skill to send messages.

### 2.2 Acknowledgment message template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "ecos-chief-of-staff-main-agent",
  "subject": "ACK: Mid-Task Requirement Update - [task identifier]",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Requirement update received and processed. Relaying changes to affected agents.",
    "data": {
      "task_id": "TASK-0042",
      "change_type_received": "scope_change",
      "agents_notified": ["svgbbox-programmer-001"],
      "impact_assessment": "Agent is approximately 20% through implementation. Scope change can be absorbed without restart. Estimated delay: 2 hours.",
      "action_taken": "Agent paused, updated instructions being prepared"
    }
  }
}
```

Field definitions for `data`:
- `task_id`: Echoes back the task identifier from the original ECOS message.
- `change_type_received`: Echoes back the change type so ECOS can confirm EOA interpreted the severity correctly.
- `agents_notified`: Array of agent session names that EOA has contacted or will contact about this change.
- `impact_assessment`: EOA's analysis of how this change affects the current work in progress. Includes estimated completion percentage and time impact.
- `action_taken`: What EOA has done or is doing in response. One of: "Relayed to agent, no pause needed", "Agent paused, updated instructions being prepared", "Agent stopped, awaiting EAA re-plan".

### 2.3 Decision tree for composing the acknowledgment

```
Composing ACK for ECOS
│
├─ change_type is "minor_clarification"
│   ├─ action_taken = "Relayed to agent, no pause needed"
│   ├─ impact_assessment = brief note, no delay expected
│   └─ priority = "normal"
│
├─ change_type is "scope_change"
│   ├─ action_taken = "Agent paused, updated instructions being prepared"
│   ├─ impact_assessment = include completion percentage and estimated delay
│   └─ priority = "normal"
│
└─ change_type is "breaking_change"
    ├─ action_taken = "Agent stopped, awaiting EAA re-plan"
    ├─ impact_assessment = include whether existing work is salvageable
    └─ priority = "high"
```

---

## 3. Module Modification Notification (EOA to Agent)

### 3.1 When to use this template

Use this template when EOA needs to inform a working agent that one or more modules in their assignment have changed. This is the message EOA sends after receiving and acknowledging a requirement update from ECOS (Sections 1 and 2).

> **Note**: Use the agent-messaging skill to send messages.

### 3.2 Notification message template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "svgbbox-programmer-001",
  "subject": "Module Modification - [module identifier]",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "Your current assignment has been modified. Review the changes below and confirm your understanding before proceeding.",
    "data": {
      "task_id": "TASK-0042",
      "module_id": "module-auth",
      "modification_type": "scope_change",
      "changes_summary": "Add OAuth2 authentication flow alongside existing API key authentication. Both methods must be supported simultaneously.",
      "impact_assessment": "New OAuth2 token validation logic required. Existing API key validation code remains unchanged. New files needed for OAuth2 flow.",
      "action_required": "continue_adapted"
    }
  }
}
```

Field definitions for `data`:
- `task_id`: The task identifier this modification belongs to.
- `module_id`: The specific module within the task that is being modified.
- `modification_type`: One of three types:
  - `scope_change`: The module's responsibilities have expanded, shrunk, or shifted. The agent must adjust what they are building.
  - `interface_change`: The module's inputs, outputs, or API contracts have changed. The agent must update how their module connects to other modules.
  - `dependency_change`: A module that this module depends on has changed. The agent must verify their code still works with the updated dependency.
- `changes_summary`: Plain text description of exactly what changed. Must be specific enough for the agent to act on without asking clarifying questions.
- `impact_assessment`: EOA's analysis of how this change affects the agent's current work. Helps the agent understand what they can keep and what they must modify.
- `action_required`: One of three directives:
  - `continue_adapted`: The agent should adjust their current work to incorporate the changes and continue without stopping. Used for minor modifications.
  - `pause_for_review`: The agent should stop coding, review the full scope of changes, and confirm understanding before resuming. Used for significant modifications.
  - `restart`: The agent should stop current work entirely. EOA will send new task instructions. Used when existing work is incompatible with the changes.

### 3.3 Expected agent response template

The agent should reply with this format to confirm they have processed the modification.

```json
{
  "from": "svgbbox-programmer-001",
  "to": "eoa-orchestrator-main-agent",
  "subject": "ACK: Module Modification - [module identifier]",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Module modification received and understood. Proceeding with adapted approach.",
    "data": {
      "task_id": "TASK-0042",
      "module_id": "module-auth",
      "understanding_confirmed": true,
      "estimated_impact_on_timeline": "Additional 2 hours for OAuth2 flow implementation",
      "questions_or_blockers": "none"
    }
  }
}
```

If the agent has questions or blockers, the `questions_or_blockers` field should contain the specific question text instead of "none". EOA must address blockers before the agent can resume.

### 3.4 Decision tree for module modification handling

```
EOA sends module modification to agent
│
├─ action_required is "continue_adapted"
│   ├─ Agent ACKs with understanding_confirmed = true
│   │   └─ Continue monitoring progress as normal
│   ├─ Agent ACKs with questions_or_blockers != "none"
│   │   ├─ EOA can answer → Send clarification message
│   │   └─ EOA cannot answer → Escalate to ECOS or EAA
│   └─ Agent does not ACK within 5 minutes
│       └─ Re-send notification, escalate if still no response
│
├─ action_required is "pause_for_review"
│   ├─ Agent ACKs with understanding_confirmed = true
│   │   └─ Send "resume" instruction to agent
│   ├─ Agent ACKs with understanding_confirmed = false
│   │   └─ Provide additional context until agent confirms understanding
│   └─ Agent does not ACK within 5 minutes
│       └─ Re-send notification, escalate if still no response
│
└─ action_required is "restart"
    ├─ Agent ACKs
    │   └─ Send new task instructions when ready
    └─ Agent does not ACK within 5 minutes
        └─ Force-stop agent session, re-assign task
```

---

## 4. Priority Change Notification (EOA to Agent)

### 4.1 When to use this template

Use this template when the priority of an active task changes. Priority changes come from ECOS (who receives them from the user via EAMA or from project-level decisions). EOA must relay the new priority to the working agent so the agent adjusts their pace and resource allocation.

> **Note**: Use the agent-messaging skill to send messages.

### 4.2 Notification message template

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "svgbbox-programmer-001",
  "subject": "Priority Change - [task identifier]",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "The priority of your current task has changed. Adjust your work accordingly.",
    "data": {
      "task_id": "TASK-0042",
      "old_priority": "normal",
      "new_priority": "urgent",
      "reason": "User demo scheduled for tomorrow. Authentication module must be completed by end of day.",
      "action_required": "accelerate"
    }
  }
}
```

Field definitions for `data`:
- `task_id`: The task whose priority has changed.
- `old_priority`: The previous priority level. One of: "low", "normal", "high", "urgent".
- `new_priority`: The updated priority level. Same values as old_priority.
- `reason`: Plain text explanation of why the priority changed. The agent needs this context to understand the urgency.
- `action_required`: One of three directives:
  - `accelerate`: The agent should speed up work on this task. Skip non-essential polish, focus on core functionality. This is used when priority increases.
  - `deprioritize`: The agent should reduce focus on this task. If the agent has multiple assignments, other tasks take precedence. If this is the only task, the agent should work at a normal pace and may be re-assigned soon. This is used when priority decreases.
  - `no_change`: The priority level changed on paper but does not require the agent to change their behavior. This is informational only. Used when the change is minor (for example, "normal" to "high" when the agent is already working at full capacity).

### 4.3 Expected agent response template

```json
{
  "from": "svgbbox-programmer-001",
  "to": "eoa-orchestrator-main-agent",
  "subject": "ACK: Priority Change - [task identifier]",
  "priority": "normal",
  "content": {
    "type": "response",
    "message": "Priority change acknowledged. Adjusting work pace accordingly.",
    "data": {
      "task_id": "TASK-0042",
      "new_priority_acknowledged": "urgent",
      "action_taken": "accelerate",
      "estimated_completion": "6 hours from now",
      "concerns": "none"
    }
  }
}
```

If the agent has concerns about meeting the new timeline, the `concerns` field should contain specific details about what may prevent timely completion. EOA must evaluate whether to escalate these concerns to ECOS.

### 4.4 Decision tree for priority change handling

```
EOA sends priority change to agent
│
├─ action_required is "accelerate"
│   ├─ Agent ACKs with concerns = "none"
│   │   └─ Increase polling frequency to monitor progress
│   ├─ Agent ACKs with concerns != "none"
│   │   ├─ Concerns are resolvable by EOA → Provide assistance
│   │   └─ Concerns require ECOS intervention → Escalate to ECOS
│   └─ Agent does not ACK within 3 minutes (shorter for urgent)
│       └─ Re-send with priority "urgent", escalate if still no response
│
├─ action_required is "deprioritize"
│   ├─ Agent ACKs
│   │   └─ Reduce polling frequency, monitor normally
│   └─ Agent does not ACK within 5 minutes
│       └─ Re-send notification
│
└─ action_required is "no_change"
    ├─ Agent ACKs
    │   └─ No further action needed
    └─ Agent does not ACK within 5 minutes
        └─ Informational only, no escalation needed
```

---

## 5. EAMA User Decision Response (EAMA to EOA)

### 5.1 When to use this template

Use this template when the Assistant Manager (EAMA) forwards a user decision back to EOA. This happens after EOA (or another agent via EOA) escalated a question or decision to the user. EAMA collects the user's answer and sends it to EOA, who must then relay it to the agent that originally needed the decision.

> **Note**: Use the agent-messaging skill to send messages.

### 5.2 Incoming decision message from EAMA

This is the message format EOA receives from EAMA. EOA does not send this message; EOA receives and processes it.

```json
{
  "from": "eama-assistant-manager-main-agent",
  "to": "eoa-orchestrator-main-agent",
  "subject": "User Decision - Escalation [escalation identifier]",
  "priority": "high",
  "content": {
    "type": "response",
    "message": "User has made a decision on the escalated question. Relay to the requesting agent.",
    "data": {
      "escalation_id": "ESC-0015",
      "user_decision": "option_b",
      "decision_details": "Use OAuth2 with PKCE flow for public clients. API keys remain for server-to-server authentication.",
      "constraints": "Must be backward-compatible with existing API key users. No migration required for current users."
    }
  }
}
```

Field definitions for `data`:
- `escalation_id`: The identifier of the original escalation that was sent to the user. EOA uses this to look up which agent and task the decision applies to.
- `user_decision`: The option the user selected. One of:
  - `option_a`, `option_b`, `option_c`: Corresponds to predefined options that were presented in the original escalation.
  - `custom`: The user provided a response that does not match any predefined option. The full response is in `decision_details`.
- `decision_details`: Full text of the user's decision, including any elaboration or instructions the user provided beyond the option selection.
- `constraints`: Any additional constraints or conditions the user attached to their decision. These must be relayed to the agent and treated as requirements.

### 5.3 Relay message to affected agent

After receiving the user decision, EOA relays it to the agent that originally requested the escalation.

```json
{
  "from": "eoa-orchestrator-main-agent",
  "to": "svgbbox-programmer-001",
  "subject": "User Decision Received - Escalation [escalation identifier]",
  "priority": "high",
  "content": {
    "type": "request",
    "message": "The user has responded to your escalated question. Apply the decision and its constraints to your current work.",
    "data": {
      "escalation_id": "ESC-0015",
      "user_decision": "option_b",
      "decision_details": "Use OAuth2 with PKCE flow for public clients. API keys remain for server-to-server authentication.",
      "constraints": "Must be backward-compatible with existing API key users. No migration required for current users.",
      "action_required": "Apply this decision to your current implementation and confirm when integrated."
    }
  }
}
```

The agent should respond with a standard acknowledgment confirming they have understood and applied the decision.

### 5.4 Decision tree for processing user decisions

```
User decision received from EAMA
│
├─ Is the escalation_id recognized?
│   ├─ Yes → Look up the original requesting agent and task
│   │         │
│   │         ├─ user_decision is "option_a", "option_b", or "option_c"
│   │         │   ├─ Relay decision to agent (Section 5.3)
│   │         │   └─ Wait for agent ACK
│   │         │
│   │         ├─ user_decision is "custom"
│   │         │   ├─ Parse decision_details for actionable instructions
│   │         │   ├─ If clear → Relay to agent (Section 5.3)
│   │         │   └─ If ambiguous → Ask EAMA for clarification before relaying
│   │         │
│   │         └─ Are there constraints?
│   │             ├─ Yes → Include constraints as mandatory requirements in relay
│   │             └─ No → Relay decision without additional constraints
│   │
│   └─ No → Reply to EAMA with error: escalation_id not found
│
└─ Is the requesting agent still active?
    ├─ Yes → Relay as described above
    └─ No → Store decision, re-assign task with decision pre-applied
```

---

## 6. Mid-Task Update Severity Decision Tree

### 6.1 Full decision tree diagram

This decision tree is the master flowchart for handling any mid-task update. Use it to determine the correct response to any incoming change, regardless of source.

```
Mid-task update received
│
├─ What is the change severity?
│
├─ Minor clarification
│   │   (change_type = "minor_clarification")
│   │   Definition: Small detail corrected or added. No scope
│   │   or interface changes. Agent can absorb without pausing.
│   │
│   ├─ Relay to agent immediately using Section 3
│   │   (action_required = "continue_adapted")
│   │
│   ├─ Agent ACKs with understanding confirmed
│   │   └─ Continue normal progress monitoring
│   │
│   └─ Agent responds with confusion or questions
│       ├─ Provide additional context from ECOS message
│       ├─ If still unclear → Ask ECOS for more detail
│       └─ Once resolved → Agent continues
│
├─ Scope change
│   │   (change_type = "scope_change")
│   │   Definition: Task boundaries expand, shrink, or shift.
│   │   Modules may be added or removed. Interfaces may change.
│   │
│   ├─ Pause agent work immediately
│   │   (action_required = "pause_for_review")
│   │
│   ├─ Assess current agent progress
│   │   │
│   │   ├─ Agent in early stages (less than 30% done)
│   │   │   ├─ Update instructions with new scope
│   │   │   ├─ Send module modification (Section 3)
│   │   │   ├─ Agent confirms understanding
│   │   │   └─ Resume work with updated instructions
│   │   │
│   │   └─ Agent in late stages (30% or more done)
│   │       ├─ Re-verify feasibility of adapting existing work
│   │       ├─ If adaptable → Send modification, resume
│   │       └─ If not adaptable → Treat as breaking change (below)
│   │
│   └─ Send ACK to ECOS with impact assessment (Section 2)
│
└─ Breaking change
    │   (change_type = "breaking_change")
    │   Definition: Fundamental assumptions invalidated. Core
    │   architecture, technology, or approach must change.
    │
    ├─ Stop agent immediately
    │   (action_required = "restart")
    │
    ├─ Assess whether old work is salvageable
    │   │
    │   ├─ Old work is salvageable
    │   │   ├─ Request EAA to re-plan affected modules only
    │   │   ├─ Identify which completed work can be reused
    │   │   ├─ Send new instructions incorporating salvaged work
    │   │   └─ Resume agent with updated task assignment
    │   │
    │   └─ Old work is incompatible
    │       ├─ Cancel the current task assignment
    │       ├─ Request EAA for complete re-architecture
    │       ├─ Create new task assignment from scratch
    │       └─ Assign to same agent (or new agent if re-assignment needed)
    │
    └─ Send ACK to ECOS with severity assessment (Section 2)
```

### 6.2 Severity classification rules

When ECOS does not explicitly set the `change_type` field, or when EOA needs to independently assess severity, use these rules:

- **Minor clarification**: The change can be described in one sentence. No module boundaries change. No interfaces change. No new dependencies are introduced. Example: "The date format should be ISO 8601, not Unix timestamp."
- **Scope change**: The change adds, removes, or modifies a module or its interfaces. The agent's task list grows or shrinks. New files or components are needed. Example: "Add OAuth2 support alongside API keys."
- **Breaking change**: The change invalidates a core assumption. The technology stack, architecture pattern, or fundamental approach must change. Existing code cannot be adapted incrementally. Example: "Switch from REST API to GraphQL."

If uncertain between two severity levels, always choose the higher severity. It is safer to over-react (pause and assess) than to under-react (let an agent continue building on invalidated assumptions).

### 6.3 Timing considerations

Response time expectations vary by severity:

- **Minor clarification**: Relay to agent within 2 minutes of receiving from ECOS. Agent should ACK within 5 minutes.
- **Scope change**: Send pause instruction within 1 minute. Complete assessment and relay within 10 minutes. Agent should ACK within 5 minutes of receiving updated instructions.
- **Breaking change**: Send stop instruction within 30 seconds. Assessment may take longer (up to 30 minutes if EAA re-planning is needed). Agent should ACK stop within 2 minutes.

If any timeout is exceeded, escalate to ECOS with a status update explaining the delay.
