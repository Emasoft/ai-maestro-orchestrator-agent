# Decision Trees Core: 7 Essential Operational Decision Points

This reference defines the 7 most important decision trees that the Emasoft Orchestrator Agent (EOA) uses during daily operations. Each tree addresses a specific scenario where EOA must choose between competing actions. The trees use measurable input variables so decisions are consistent and auditable.

**Prerequisite reading**: Before using these decision trees, read:
- [escalation-procedures.md](./escalation-procedures.md) for escalation message formats
- [verification-loops-protocol.md](./verification-loops-protocol.md) for verification loop mechanics
- [messaging-protocol-part2-send-receive.md](./messaging-protocol-part2-send-receive.md) for how to send messages to other agents

---

## Table of Contents

- [1. Escalate vs Retry Decision Tree](#1-escalate-vs-retry-decision-tree)
  - 1.1 When to use this tree
  - 1.2 Input variables EOA must gather
  - 1.3 Full decision tree with all branches
  - 1.4 Outcome actions at each leaf node
  - 1.5 Concrete example
- [2. Reassign vs Wait Decision Tree](#2-reassign-vs-wait-decision-tree)
  - 2.1 When to use this tree
  - 2.2 Input variables EOA must gather
  - 2.3 Full decision tree with all branches
  - 2.4 Outcome actions at each leaf node
  - 2.5 Concrete example
- [3. Conflicting Multi-Agent Responses Decision Tree](#3-conflicting-multi-agent-responses-decision-tree)
  - 3.1 When to use this tree
  - 3.2 Input variables EOA must gather
  - 3.3 Full decision tree with all branches
  - 3.4 Outcome actions at each leaf node
  - 3.5 Concrete example
- [4. Verification Loop Outcome Decision Tree](#4-verification-loop-outcome-decision-tree)
  - 4.1 When to use this tree
  - 4.2 Input variables EOA must gather
  - 4.3 Full decision tree with all branches
  - 4.4 Outcome actions at each leaf node
  - 4.5 Concrete example
- [5. Agent Recovery Decision Tree](#5-agent-recovery-decision-tree)
  - 5.1 When to use this tree
  - 5.2 Input variables EOA must gather
  - 5.3 Full decision tree with all branches
  - 5.4 Outcome actions at each leaf node
  - 5.5 Concrete example
- [6. Direct Handling vs Delegation Decision Tree](#6-direct-handling-vs-delegation-decision-tree)
  - 6.1 When to use this tree
  - 6.2 Input variables EOA must gather
  - 6.3 Full decision tree with all branches
  - 6.4 Outcome actions at each leaf node
  - 6.5 Concrete example
- [7. Post-Task Interview Escalation Decision Tree](#7-post-task-interview-escalation-decision-tree)
  - 7.1 When to use this tree
  - 7.2 Input variables EOA must gather
  - 7.3 Full decision tree with all branches
  - 7.4 Outcome actions at each leaf node
  - 7.5 Concrete example

---

## 1. Escalate vs Retry Decision Tree

### 1.1 When to use this tree

Use this tree every time an agent reports a failure, error, or blocker during task execution. The tree determines whether EOA should ask the agent to retry the task, try a different approach, or escalate the problem to a higher-level agent (ECOS or EAA).

### 1.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `retry_count` | Integer (0+) | Count of how many times this specific agent has already retried this specific task. EOA tracks this in the task record. |
| `error_severity` | One of: `critical`, `high`, `medium`, `low` | Determined from the agent's error report. Critical means data loss or security risk. High means task cannot proceed. Medium means partial progress possible. Low means cosmetic or non-blocking. |
| `time_elapsed_minutes` | Integer | Minutes since the task was first assigned. Compare against the task deadline. |
| `task_priority` | One of: `P0`, `P1`, `P2`, `P3` | From the original task assignment. P0 is highest urgency. |
| `deadline_50_percent` | Integer | Half of the total time budget for this task in minutes. If deadline is 120 minutes, this value is 60. |

### 1.3 Full decision tree with all branches

```
Agent reports an issue with the task
    │
    ├─ Is error_severity "critical"?
    │     ├─ Yes → ESCALATE to ECOS immediately
    │     │         ├─ Include: full error log, task ID, agent session name
    │     │         └─ Action: mark task as BLOCKED, do NOT retry
    │     │
    │     └─ No → Is retry_count >= 3?
    │               ├─ Yes → Is the error the same as previous retries?
    │               │         ├─ Yes (same error each time) → ESCALATE to ECOS
    │               │         │    Reason: systematic issue, retrying will not help
    │               │         │    Include: all 3+ error logs showing same pattern
    │               │         │
    │               │         └─ No (different error each time) → TRY DIFFERENT APPROACH
    │               │              Action: send the agent a new strategy or reassign
    │               │              to a different agent with alternative instructions
    │               │
    │               └─ No (retry_count < 3) → Is time_elapsed > deadline_50_percent?
    │                         ├─ Yes → ESCALATE with time warning
    │                         │         Action: escalate to ECOS with message:
    │                         │         "Task [ID] has used >50% of time budget
    │                         │         with [retry_count] failed attempts.
    │                         │         Requesting guidance or reassignment."
    │                         │
    │                         └─ No → RETRY with guidance
    │                                  Action: send agent a retry message that includes:
    │                                  - What went wrong (from their error report)
    │                                  - Specific guidance on what to try differently
    │                                  - Remaining time budget
    │                                  Increment retry_count by 1
```

### 1.4 Outcome actions at each leaf node

| Leaf | Action | Message template |
|------|--------|------------------|
| ESCALATE to ECOS immediately | Send urgent message to ECOS via AI Maestro with priority `urgent`. Mark task status as `BLOCKED`. | Use the escalation template from [escalation-procedures.md](./escalation-procedures.md) |
| ESCALATE (systematic issue) | Send high-priority message to ECOS with all error logs attached. Mark task as `BLOCKED`. | Include the phrase: "Systematic failure detected after [N] retries with identical error." |
| TRY DIFFERENT APPROACH | Either provide the agent with alternative instructions, or reassign to a different agent entirely. Reset retry_count to 0 if reassigning. | Use the task delegation template from [task-instruction-format-part1-core-template.md](./task-instruction-format-part1-core-template.md) |
| ESCALATE with time warning | Send high-priority message to ECOS requesting guidance. Keep task status as `IN_PROGRESS` but flag it. | Include: time elapsed, time remaining, retry count, last error summary. |
| RETRY with guidance | Send the agent a normal-priority message with specific instructions on what to change. | Include: "This is retry [N] of 3. Previous error: [summary]. Please try: [specific guidance]." |

### 1.5 Concrete example

Scenario: Agent `svgbbox-programmer-001` is implementing a bounding box calculation function. On its second attempt (retry_count = 2), it reports an error: "TypeError: cannot read property 'x' of undefined". The error severity is `high` (task cannot proceed). The task priority is P1. The task was assigned 25 minutes ago with a 120-minute deadline (deadline_50_percent = 60).

Walking the tree:
1. Is error_severity "critical"? No (it is "high").
2. Is retry_count >= 3? No (it is 2).
3. Is time_elapsed (25) > deadline_50_percent (60)? No.
4. Result: **RETRY with guidance**.

EOA sends: "This is retry 3 of 3. Previous error: TypeError on property 'x' of undefined. The input SVG element may not have x/y attributes. Please add null checks for element.getAttribute('x') before accessing the value. Remaining time budget: 95 minutes."

---

## 2. Reassign vs Wait Decision Tree

### 2.1 When to use this tree

Use this tree when an agent has gone silent -- it has not responded to messages or provided progress updates within the expected polling interval. This tree determines whether EOA should wait longer, send a reminder, or reassign the task to a different agent.

### 2.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `no_response_minutes` | Integer | Minutes since the agent's last message or progress update. EOA tracks this from AI Maestro message timestamps. |
| `task_priority` | One of: `P0`, `P1`, `P2`, `P3` | From the original task assignment. |
| `available_agents_count` | Integer (0+) | Number of agents currently idle or available for reassignment. Query the agent registry. |
| `task_deadline_proximity` | One of: `far` (>50% time remaining), `near` (25-50% remaining), `imminent` (<25% remaining) | Calculate from task start time, current time, and deadline. |

### 2.3 Full decision tree with all branches

```
Agent has not responded to messages or polling
    │
    ├─ Has it been more than 30 minutes with no response?
    │     │
    │     ├─ Yes (no_response_minutes > 30)
    │     │     │
    │     │     ├─ Is task_priority P0 or P1?
    │     │     │     │
    │     │     │     ├─ Yes (P0 or P1) → REASSIGN immediately
    │     │     │     │    ├─ Is available_agents_count > 0?
    │     │     │     │    │     ├─ Yes → Reassign to best available agent
    │     │     │     │    │     │         Include all context from original assignment
    │     │     │     │    │     │         Mark original agent as UNRESPONSIVE
    │     │     │     │    │     │
    │     │     │     │    │     └─ No (no agents available) → ESCALATE to ECOS
    │     │     │     │    │           Request: "Need replacement agent for P0/P1
    │     │     │     │    │           task. Current agent unresponsive 30+ min.
    │     │     │     │    │           No available agents in pool."
    │     │     │     │    │
    │     │     │     │    └─ (after reassignment) Notify ECOS about unresponsive agent
    │     │     │     │
    │     │     │     └─ No (P2 or P3) → SEND URGENT REMINDER, wait 15 more minutes
    │     │     │           Action: send priority "high" message to agent:
    │     │     │           "No response received for 30+ minutes on task [ID].
    │     │     │           Please reply with status within 15 minutes or task
    │     │     │           will be reassigned."
    │     │     │           Set a 15-minute timer. If still no response, reassign.
    │     │     │
    │     │     └─ (not reached -- all branches covered above)
    │     │
    │     └─ No (no_response_minutes <= 30)
    │           │
    │           ├─ Is task_priority P0?
    │           │     │
    │           │     ├─ Yes → SEND URGENT REMINDER now
    │           │     │         Action: send priority "urgent" message:
    │           │     │         "P0 task [ID] requires immediate status update.
    │           │     │         Please respond within 10 minutes."
    │           │     │
    │           │     └─ No (P1, P2, P3) → WAIT
    │           │           Action: do nothing now, check again at 30-minute mark
    │           │           Log: "Agent [name] silent for [N] minutes on [priority]
    │           │           task. Will escalate at 30-minute mark."
    │           │
    │           └─ (not reached -- all branches covered above)
```

### 2.4 Outcome actions at each leaf node

| Leaf | Action | Follow-up |
|------|--------|-----------|
| REASSIGN immediately | Create new task assignment with all original context plus any partial results from unresponsive agent. Use [op-prepare-task-delegation.md](./op-prepare-task-delegation.md). | Notify ECOS about the unresponsive agent for potential health check. |
| ESCALATE to ECOS (no agents) | Send urgent message to ECOS requesting a new agent be spawned or an existing one freed up. | Block on ECOS response before proceeding. |
| SEND URGENT REMINDER (P2/P3) | Send high-priority AI Maestro message. Start a 15-minute countdown timer. | If no response after the 15 minutes, re-enter this tree -- the answer to "> 30 minutes" will now be Yes. |
| SEND URGENT REMINDER (P0) | Send urgent-priority AI Maestro message. Start a 10-minute countdown timer. | If no response after 10 minutes, re-enter this tree at the 30+ minute branch. |
| WAIT | Log the silence. Set a reminder to check again at the 30-minute mark. | No message sent to the agent yet. |

### 2.5 Concrete example

Scenario: Agent `svgbbox-programmer-002` was assigned a P2 task to write unit tests. It last sent a progress update 35 minutes ago. There are 2 available agents in the pool. The task deadline is 4 hours away (proximity: "far").

Walking the tree:
1. Has it been more than 30 minutes? Yes (35 minutes).
2. Is task priority P0 or P1? No (it is P2).
3. Result: **SEND URGENT REMINDER, wait 15 more minutes**.

EOA sends: "No response received for 35 minutes on task TSK-042 (write unit tests for bounding box module). Please reply with status within 15 minutes or the task will be reassigned."

---

## 3. Conflicting Multi-Agent Responses Decision Tree

### 3.1 When to use this tree

Use this tree when two or more agents provide contradictory results, recommendations, or implementations for overlapping or related tasks. This commonly happens when parallel agents work on related modules, or when a verification agent disagrees with an implementation agent.

### 3.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `response_A` | Text summary | The first agent's result or recommendation, summarized by EOA. |
| `response_B` | Text summary | The second agent's result or recommendation, summarized by EOA. |
| `conflict_type` | One of: `implementation`, `design`, `test_result` | EOA categorizes the conflict. `implementation` means two different code approaches. `design` means disagreement on architecture or patterns. `test_result` means one agent says tests pass and the other says they fail. |
| `agents_involved` | List of agent names | The session names of all agents involved in the conflict. |

### 3.3 Full decision tree with all branches

```
Two or more agents have provided contradictory results
    │
    ├─ Is conflict_type "implementation"?
    │     │
    │     ├─ Yes → Are both implementation approaches functionally valid?
    │     │         (Both produce correct output, just different code)
    │     │         │
    │     │         ├─ Yes (both valid) → CHOOSE THE SIMPLER APPROACH
    │     │         │    Criteria for "simpler":
    │     │         │    1. Fewer lines of code
    │     │         │    2. Fewer dependencies
    │     │         │    3. Easier to test
    │     │         │    4. More consistent with existing codebase style
    │     │         │    Action: notify both agents of the decision and why
    │     │         │    Use the chosen approach, archive the other
    │     │         │
    │     │         └─ No (one or both have flaws) → ESCALATE to EAA
    │     │              Reason: architectural guidance needed to determine
    │     │              the correct approach
    │     │              Include: both approaches with pros/cons analysis
    │     │              Action: block task until EAA responds
    │     │
    │     └─ No → Is conflict_type "test_result"?
    │               │
    │               ├─ Yes → REQUEST BOTH AGENTS TO RE-RUN TESTS
    │               │         Action: send message to both agents:
    │               │         "Conflicting test results detected for [module].
    │               │         Please re-run tests with verbose logging enabled
    │               │         and return the full output. Use these exact steps:
    │               │         1. Clean all caches and build artifacts
    │               │         2. Run tests with --verbose flag
    │               │         3. Return the complete stdout and stderr"
    │               │         │
    │               │         └─ After re-run results arrive:
    │               │               ├─ Results now agree → Use agreed result
    │               │               └─ Results still conflict → ESCALATE to EIA
    │               │                    Reason: integration/environment issue
    │               │                    Include: both verbose test logs
    │               │
    │               └─ No (conflict_type is "design") → ESCALATE to EAA
    │                     Reason: design decisions are EAA's responsibility
    │                     Action: send high-priority message to EAA with:
    │                     - Both agents' positions summarized
    │                     - The specific design question to resolve
    │                     - Any constraints from existing architecture
    │                     Block task until EAA responds
```

### 3.4 Outcome actions at each leaf node

| Leaf | Action | Who is notified |
|------|--------|-----------------|
| CHOOSE THE SIMPLER APPROACH | Select one approach, record the rationale, notify both agents. The rejected agent should not feel penalized -- phrase the notification positively. | Both involved agents, task log updated. |
| ESCALATE to EAA (implementation) | Send detailed comparison to EAA. Pause both agents' work on the conflicting area. | EAA, both agents (told to pause), ECOS (informed of delay). |
| REQUEST RE-RUN | Send identical re-run instructions to both agents. Wait for both results before deciding. | Both agents. |
| ESCALATE to EIA (persistent test conflict) | After re-run still conflicts, send to EIA for environment/integration investigation. | EIA, both agents, ECOS. |
| ESCALATE to EAA (design) | Send design question to EAA immediately. Do not attempt to resolve design conflicts yourself. | EAA, both agents (told to pause). |

### 3.5 Concrete example

Scenario: Agent `svgbbox-programmer-001` implemented SVG path parsing using a regex-based approach. Agent `svgbbox-programmer-002` implemented the same parsing using a DOM-based approach. Both produce correct output for the test cases, but the approaches are fundamentally different. The conflict_type is `implementation`.

Walking the tree:
1. Is conflict_type "implementation"? Yes.
2. Are both approaches functionally valid? Yes (both produce correct output).
3. Result: **CHOOSE THE SIMPLER APPROACH**.

EOA evaluates: The regex approach is 45 lines, no dependencies, but fragile with edge cases. The DOM approach is 30 lines, uses an existing dependency (xmldom), and handles edge cases naturally. EOA chooses the DOM approach (fewer lines, handles edge cases, uses existing dependency).

EOA notifies both: "Both parsing approaches work correctly. Proceeding with the DOM-based approach from programmer-002 because it handles edge cases more robustly and reuses an existing project dependency. Programmer-001, your regex approach was valid -- please archive it as an alternative in the design notes."

---

## 4. Verification Loop Outcome Decision Tree

### 4.1 When to use this tree

Use this tree at the end of each verification loop (loops 1 through 4, and the optional 5th check) in the 4-loop verification protocol. Each time a verification pass completes, EOA must decide what to do with the results.

### 4.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `loop_number` | Integer (1-5) | Which verification loop just completed. Loops 1-4 are standard. Loop 5 is the optional final sign-off. |
| `issues_found_count` | Integer (0+) | Number of distinct issues the verifier reported. |
| `issue_severity` | One of: `critical`, `major`, `minor`, `cosmetic` | The highest severity among all issues found. Critical means broken functionality. Major means significant quality gap. Minor means small improvements needed. Cosmetic means style or formatting only. |
| `agent_evidence_quality` | One of: `thorough`, `adequate`, `superficial` | How well the verifying agent documented their findings. Thorough means they provided specific file names, line numbers, and reproduction steps. Adequate means general descriptions. Superficial means vague or one-line statements. |

### 4.3 Full decision tree with all branches

```
Verification loop N has completed
    │
    ├─ Were any issues found? (issues_found_count > 0)
    │     │
    │     ├─ Yes (issues found)
    │     │     │
    │     │     ├─ Is loop_number < 4?
    │     │     │     │
    │     │     │     ├─ Yes (still have loops remaining)
    │     │     │     │    Action: RECORD ISSUES AND SEND FEEDBACK
    │     │     │     │    1. Log all issues in the task record
    │     │     │     │    2. Send issues to the implementing agent
    │     │     │     │    3. Include: issue description, severity, file/line
    │     │     │     │    4. Request fixes and re-submission for next loop
    │     │     │     │    5. Advance to loop N+1 after fixes are submitted
    │     │     │     │
    │     │     │     └─ No (loop_number is 4)
    │     │     │           │
    │     │     │           ├─ Is issue_severity "critical" or "major"?
    │     │     │           │     │
    │     │     │           │     ├─ Yes → REJECT AND RESTART
    │     │     │           │     │    Action: reject the deliverable entirely
    │     │     │           │     │    1. Notify implementing agent: work rejected
    │     │     │           │     │    2. Send cumulative issues from all 4 loops
    │     │     │           │     │    3. Reset loop counter to 1
    │     │     │           │     │    4. Consider reassigning to different agent
    │     │     │           │     │       if same issues persist (use Tree 1)
    │     │     │           │     │
    │     │     │           │     └─ No (severity is "minor" or "cosmetic")
    │     │     │           │          Action: NOTE AS KNOWN ISSUES, PROCEED
    │     │     │           │          1. Record issues as "known minor issues"
    │     │     │           │          2. Proceed to loop 5 (final sign-off check)
    │     │     │           │          3. Include known issues list in sign-off
    │     │     │           │          4. These can be addressed in a follow-up task
    │     │     │           │
    │     │     │           └─ (not reached -- all branches covered)
    │     │     │
    │     │     └─ (not reached -- all branches covered)
    │     │
    │     └─ No (no issues found, issues_found_count == 0)
    │           │
    │           ├─ Is agent_evidence_quality "thorough"?
    │           │     │
    │           │     ├─ Yes → RECORD CLEAN PASS
    │           │     │    Action: mark this loop as passed
    │           │     │    1. Log: "Loop [N] passed - no issues found"
    │           │     │    2. Include verifier's evidence in task record
    │           │     │    3. If loop 4: proceed to loop 5 (final sign-off)
    │           │     │    4. If loop 5: APPROVE deliverable as complete
    │           │     │
    │           │     └─ No (evidence is "adequate" or "superficial")
    │           │          Action: REJECT VERIFICATION, REQUEST DEEPER ANALYSIS
    │           │          1. Do NOT count this as a passed loop
    │           │          2. Send message to verifier:
    │           │             "Your verification for loop [N] found no issues,
    │           │             but the evidence provided is insufficient.
    │           │             Please re-verify with:
    │           │             - Specific files and line numbers checked
    │           │             - Test commands run and their output
    │           │             - Edge cases explicitly tested"
    │           │          3. Re-run the same loop number after deeper analysis
    │           │
    │           └─ (not reached -- all branches covered)
```

### 4.4 Outcome actions at each leaf node

| Leaf | Action | Next step |
|------|--------|-----------|
| RECORD ISSUES AND SEND FEEDBACK | Log issues, send to implementer with fix instructions. | Wait for implementer to submit fixes, then start loop N+1. |
| REJECT AND RESTART | Reject deliverable, send cumulative issues. Reset to loop 1. | Optionally reassign using Tree 1 (Escalate vs Retry). |
| NOTE AS KNOWN ISSUES, PROCEED | Accept with noted issues. Create follow-up task for minor fixes. | Proceed to loop 5 for final sign-off. |
| RECORD CLEAN PASS | Mark loop as passed. Log evidence. | Advance to next loop, or approve if this was loop 5. |
| REJECT VERIFICATION | Do not advance loop count. Require deeper analysis from verifier. | Re-run the same loop after verifier resubmits. |

### 4.5 Concrete example

Scenario: Loop 3 of 4 has just completed for a CSS rendering module. The verifier (an EIA agent) found 2 issues: one minor (inconsistent variable naming) and one major (the module fails on SVG elements with percentage-based widths). The agent provided thorough evidence including test files and error output.

Walking the tree:
1. Were any issues found? Yes (2 issues).
2. Is loop_number < 4? Yes (loop 3).
3. Result: **RECORD ISSUES AND SEND FEEDBACK**.

EOA logs both issues and sends to the implementing agent: "Verification loop 3 found 2 issues. Issue 1 (major): CSS rendering fails on SVG elements using percentage-based widths. See test file `test_percentage_widths.svg` and error log attached. Issue 2 (minor): Variable naming inconsistency -- `elemWidth` vs `element_width` in renderer.py lines 45 and 78. Please fix both issues and resubmit for loop 4."

---

## 5. Agent Recovery Decision Tree

### 5.1 When to use this tree

Use this tree when an agent that was previously marked as unresponsive or failed comes back online (recovers) while a replacement agent is already working on its task. EOA must decide whether to keep the replacement or revert to the original agent.

### 5.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `original_agent_status` | One of: `recovered`, `partially_recovered`, `unstable` | From the agent's recovery message and any diagnostic output. `recovered` means fully operational. `partially_recovered` means functional but with limitations. `unstable` means intermittently responsive. |
| `replacement_agent_progress_percent` | Integer (0-100) | How far the replacement agent has progressed on the task. Obtained from the replacement agent's last progress update. |
| `task_overlap_risk` | One of: `none`, `low`, `high` | Risk that switching agents mid-task will cause conflicts (e.g., both wrote to the same files, both committed to the same branch). EOA assesses this from both agents' work logs. |
| `original_work_salvageable` | Boolean | Whether the original agent's partial work (before it went unresponsive) can be reused. Determined by checking if the work is in a committed, clean state. |

### 5.3 Full decision tree with all branches

```
Original agent has recovered while replacement is working
    │
    ├─ Has the replacement agent completed more than 50% of the task?
    │     │
    │     ├─ Yes (replacement_agent_progress_percent > 50)
    │     │    Action: KEEP REPLACEMENT
    │     │    1. Notify original agent: "Task [ID] has been reassigned.
    │     │       Replacement agent is >50% complete. Your recovery is
    │     │       noted and you will be assigned new tasks."
    │     │    2. Mark original agent as "available" in registry
    │     │    3. Let replacement finish the task
    │     │    4. Log the incident for ECOS review
    │     │
    │     └─ No (replacement_agent_progress_percent <= 50)
    │           │
    │           ├─ Is original agent's previous work salvageable?
    │           │     │
    │           │     ├─ Yes (work is committed and clean)
    │           │     │    │
    │           │     │    ├─ Is task_overlap_risk "high"?
    │           │     │    │     │
    │           │     │    │     ├─ Yes → KEEP REPLACEMENT (too risky to switch)
    │           │     │    │     │    Notify original: assigned to new tasks
    │           │     │    │     │    Reason: switching now risks merge conflicts
    │           │     │    │     │
    │           │     │    │     └─ No (overlap risk is "none" or "low")
    │           │     │    │          Action: REVERT TO ORIGINAL AGENT
    │           │     │    │          1. Pause replacement agent
    │           │     │    │          2. Handoff replacement's partial work to original
    │           │     │    │          3. Send original agent: "Resuming task [ID].
    │           │     │    │             Your previous work is intact. Replacement
    │           │     │    │             agent added [summary of new work]. Please
    │           │     │    │             continue from where you left off,
    │           │     │    │             incorporating the replacement's progress."
    │           │     │    │          4. Mark replacement as "available"
    │           │     │    │          5. Log the handoff details
    │           │     │    │
    │           │     │    └─ (not reached -- all branches covered)
    │           │     │
    │           │     └─ No (work is not salvageable -- uncommitted, corrupt, or stale)
    │           │          Action: KEEP REPLACEMENT
    │           │          1. Notify original: previous work could not be recovered
    │           │          2. Discard original's stale work (do NOT delete files --
    │           │             move to an archive branch or folder)
    │           │          3. Let replacement continue
    │           │          4. Assign original to new tasks
    │           │
    │           └─ (not reached -- all branches covered)
```

### 5.4 Outcome actions at each leaf node

| Leaf | Action | Risk mitigation |
|------|--------|-----------------|
| KEEP REPLACEMENT (>50%) | Let replacement finish. Free up original for other tasks. | None needed -- replacement is well underway. |
| KEEP REPLACEMENT (high overlap) | Let replacement finish despite original's recovery. | Avoiding merge conflicts outweighs the benefit of the original's familiarity. |
| REVERT TO ORIGINAL | Pause replacement, handoff partial work, resume original. | Ensure the handoff message clearly lists what the replacement changed and where. |
| KEEP REPLACEMENT (stale work) | Let replacement continue. Archive original's work, do not delete. | Move original's stale work to `_dev` folder or archive branch for reference. |

### 5.5 Concrete example

Scenario: Agent `svgbbox-programmer-001` became unresponsive 45 minutes ago and was replaced by `svgbbox-programmer-003`. The replacement is now 30% done (has set up the test framework but not written actual tests). The original agent has now recovered and is fully operational. The original's work (a half-complete test file) was committed to a feature branch before the outage. The overlap risk is low because the replacement started fresh on a new branch.

Walking the tree:
1. Has replacement completed more than 50%? No (30%).
2. Is original agent's previous work salvageable? Yes (committed to feature branch).
3. Is task_overlap_risk "high"? No (it is "low").
4. Result: **REVERT TO ORIGINAL AGENT**.

EOA sends to `svgbbox-programmer-001`: "Resuming task TSK-055 (write unit tests for path parser). Your previous work on branch `feature/path-parser-tests` is intact. Replacement agent programmer-003 set up the test framework in a new branch `feature/path-parser-tests-v2` and created test fixtures in `tests/fixtures/`. Please continue on your branch, incorporating the test fixtures from the replacement's branch."

EOA sends to `svgbbox-programmer-003`: "Task TSK-055 is being returned to the original agent who has recovered. Your test framework setup and fixtures will be used. You are now available for new assignments."

---

## 6. Direct Handling vs Delegation Decision Tree

### 6.1 When to use this tree

Use this tree every time a new request or task arrives. The tree determines whether EOA should handle it directly (because it is simple enough) or delegate it to a specialized agent (because it requires coding, research, or multi-step work).

### 6.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `requires_code` | Boolean | Does this task involve writing, modifying, or debugging code? |
| `requires_research` | Boolean | Does this task require searching documentation, exploring codebases, or investigating unknowns? |
| `task_complexity` | One of: `simple`, `medium`, `complex` | Simple: can be answered in 1-2 messages with information EOA already has. Medium: requires some investigation but no specialized skills. Complex: requires deep analysis, multiple steps, or specialized tools. |
| `eoa_current_load` | One of: `light` (0-2 active tasks), `moderate` (3-5), `heavy` (6+) | Count of tasks EOA is currently actively coordinating. |

### 6.3 Full decision tree with all branches

```
New request or task has arrived
    │
    ├─ Does the task require writing, modifying, or debugging code?
    │     │
    │     ├─ Yes → DELEGATE TO EPA (Programmer Agent) always
    │     │         EOA must NEVER write code directly
    │     │         This is a hard rule with no exceptions
    │     │         Action: prepare task delegation using
    │     │         op-prepare-task-delegation template
    │     │
    │     └─ No → Is it a simple status check, query, or acknowledgment?
    │               (Examples: "What is the status of task X?",
    │               "How many agents are active?",
    │               "Acknowledge receipt of message")
    │               │
    │               ├─ Yes → HANDLE DIRECTLY
    │               │         EOA responds immediately from its own knowledge
    │               │         and tracking data. No delegation needed.
    │               │         Maximum response time: 2 minutes.
    │               │
    │               └─ No → Does the task require research or multi-step analysis?
    │                         (Examples: "Investigate why module X is slow",
    │                         "Find all files affected by this API change",
    │                         "Compare these two library options")
    │                         │
    │                         ├─ Yes → DELEGATE TO APPROPRIATE AGENT
    │                         │    │
    │                         │    ├─ Is it an architecture/design question?
    │                         │    │     ├─ Yes → Delegate to EAA (Architect)
    │                         │    │     └─ No ↓
    │                         │    │
    │                         │    ├─ Is it a quality/review question?
    │                         │    │     ├─ Yes → Delegate to EIA (Integrator)
    │                         │    │     └─ No ↓
    │                         │    │
    │                         │    ├─ Is it a coordination/team question?
    │                         │    │     ├─ Yes → Delegate to ECOS (Chief of Staff)
    │                         │    │     └─ No ↓
    │                         │    │
    │                         │    └─ General research → Delegate to EPA with
    │                         │         research-focused instructions (EPA can
    │                         │         use SERENA, grep, and other tools)
    │                         │
    │                         └─ No → HANDLE DIRECTLY
    │                              The task is non-code, non-research, and
    │                              non-trivial (e.g., "Update the task board",
    │                              "Send a progress report to ECOS")
    │                              EOA handles these operational tasks itself
```

### 6.4 Outcome actions at each leaf node

| Leaf | Action | Template to use |
|------|--------|-----------------|
| DELEGATE TO EPA | Prepare full task delegation with context, acceptance criteria, and deadline. | [op-prepare-task-delegation.md](./op-prepare-task-delegation.md) |
| HANDLE DIRECTLY (status) | Respond immediately from EOA's task tracking data. | No template needed -- respond conversationally. |
| DELEGATE TO EAA | Send architecture question with relevant context and constraints. | [escalation-procedures.md](./escalation-procedures.md) |
| DELEGATE TO EIA | Send quality/review request with the code or artifact to review. | [op-review-completion-report.md](./op-review-completion-report.md) |
| DELEGATE TO ECOS | Send coordination question to ECOS. | [messaging-protocol-part2-send-receive.md](./messaging-protocol-part2-send-receive.md) |
| DELEGATE TO EPA (research) | Send research task with specific questions to answer and where to look. | [task-instruction-format-part1-core-template.md](./task-instruction-format-part1-core-template.md) |
| HANDLE DIRECTLY (operational) | EOA performs the operational task itself (updating boards, sending reports). | Use appropriate operational procedure (op-*.md files). |

### 6.5 Concrete example

Scenario: ECOS sends EOA a message: "The SVG bounding box library needs a new function to calculate the combined bounding box of multiple overlapping elements. Please get this implemented."

Walking the tree:
1. Does it require writing code? Yes (implementing a new function).
2. Result: **DELEGATE TO EPA** always.

EOA prepares a task delegation: "Task TSK-060: Implement `combinedBoundingBox(elements: SVGElement[]): BBox` function. Requirements: Given an array of SVG elements, compute the smallest bounding box that contains all of them. Handle edge cases: empty array (return null), single element (return its bbox), overlapping elements. Write tests. Deadline: 3 hours. Acceptance criteria: function passes all tests, handles edge cases, has JSDoc comments."

---

## 7. Post-Task Interview Escalation Decision Tree

### 7.1 When to use this tree

Use this tree during the post-task interview phase, after an agent submits a completed task and EOA reviews the deliverable. If EOA finds issues and issues a REVISE verdict (asking the agent to fix problems and resubmit), this tree determines how many REVISE cycles are acceptable before escalating.

### 7.2 Input variables EOA must gather

| Variable | Type | How to obtain |
|----------|------|---------------|
| `revise_count` | Integer (0+) | Number of times EOA has issued REVISE for this specific task to this specific agent. Tracked in the task record. |
| `issue_types` | List of: `design`, `implementation`, `quality` | Categories of the issues found. `design` means the approach is wrong. `implementation` means the code has bugs. `quality` means the code works but does not meet standards. |
| `agent_response_quality` | One of: `improving`, `stagnant`, `declining` | Whether the agent's revisions are getting better, staying the same, or getting worse with each REVISE. EOA compares the issues found across REVISE iterations. |
| `same_issues_persist` | Boolean | Whether the exact same issues (or substantially similar ones) keep appearing across REVISE iterations. |

### 7.3 Full decision tree with all branches

```
EOA has issued a REVISE verdict on an agent's deliverable
    │
    ├─ Is revise_count >= 3?
    │     │
    │     ├─ Yes (3 or more REVISE cycles for this task)
    │     │     │
    │     │     ├─ Are the issues the same each time? (same_issues_persist == true)
    │     │     │     │
    │     │     │     ├─ Yes → ESCALATE TO ECOS (agent capability issue)
    │     │     │     │    Reason: the agent is unable to fix these specific issues
    │     │     │     │    after 3+ attempts. This suggests the task exceeds the
    │     │     │     │    agent's capability or the agent has a fundamental
    │     │     │     │    misunderstanding.
    │     │     │     │    Action:
    │     │     │     │    1. Send ECOS: "Agent [name] has failed to resolve
    │     │     │     │       [issue description] after [N] REVISE cycles.
    │     │     │     │       Requesting reassignment or agent capability review."
    │     │     │     │    2. Include all REVISE feedback history
    │     │     │     │    3. Pause the task until ECOS responds
    │     │     │     │
    │     │     │     └─ No (different issues each time) → ESCALATE TO EAA
    │     │     │          Reason: the task instructions or design may be unclear,
    │     │     │          causing the agent to fix one thing and break another
    │     │     │          Action:
    │     │     │          1. Send EAA: "Task [ID] has gone through [N] REVISE
    │     │     │             cycles with different issues each time. The design
    │     │     │             spec may need clarification or the task may need
    │     │     │             to be broken into smaller pieces."
    │     │     │          2. Include: original task spec, all REVISE feedback,
    │     │     │             all agent submissions
    │     │     │          3. Pause until EAA provides updated spec
    │     │     │
    │     │     └─ (not reached -- all branches covered)
    │     │
    │     └─ No (revise_count < 3)
    │           │
    │           ├─ Does issue_types contain "design"?
    │           │     │
    │           │     ├─ Yes → ESCALATE TO EAA immediately
    │           │     │    Reason: design issues should not be resolved through
    │           │     │    REVISE iterations with the implementer. The architect
    │           │     │    must clarify the design.
    │           │     │    Action:
    │           │     │    1. Send EAA the specific design question
    │           │     │    2. Tell the implementing agent to pause
    │           │     │    3. Once EAA responds, send updated guidance to agent
    │           │     │    4. Do NOT count this as a REVISE -- it was a design gap
    │           │     │
    │           │     └─ No (issues are implementation or quality only)
    │           │          Action: SEND REVISE WITH DETAILED GUIDANCE
    │           │          1. For each issue, provide:
    │           │             - What is wrong (specific file, line, behavior)
    │           │             - What the correct behavior should be
    │           │             - A hint on how to fix it (without writing code)
    │           │          2. Set a deadline for the revision
    │           │          3. Increment revise_count by 1
    │           │          4. If agent_response_quality is "declining", add a
    │           │             warning: "Quality of revisions is declining.
    │           │             Please take extra care on this submission."
    │           │
    │           └─ (not reached -- all branches covered)
```

### 7.4 Outcome actions at each leaf node

| Leaf | Action | Expected response time |
|------|--------|----------------------|
| ESCALATE TO ECOS (capability) | Send detailed failure report to ECOS. Pause task. Wait for ECOS to either reassign, provide training, or adjust the task. | ECOS should respond within 30 minutes for P0/P1, 2 hours for P2/P3. |
| ESCALATE TO EAA (unclear spec) | Send spec ambiguity report to EAA with all evidence. Pause task. Wait for updated spec. | EAA should respond within 1 hour. |
| ESCALATE TO EAA (design issue) | Send design question immediately, even on first REVISE. Do not count as a REVISE cycle. | EAA should respond within 1 hour. |
| SEND REVISE WITH GUIDANCE | Send detailed fix instructions. Increment counter. Wait for resubmission. | Agent should resubmit within the deadline set by EOA (typically 1-2 hours). |

### 7.5 Concrete example

Scenario: Agent `svgbbox-programmer-001` submitted a completed SVG text measurement function. EOA's review found that the function does not account for font-size inheritance from parent elements. This is the second REVISE (revise_count = 2). The first REVISE was about a different issue (missing viewBox handling) which was fixed. The current issue type is `implementation`. The agent's response quality is `improving` (the first issue was fixed correctly).

Walking the tree:
1. Is revise_count >= 3? No (it is 2).
2. Does issue_types contain "design"? No (it is `implementation`).
3. Result: **SEND REVISE WITH DETAILED GUIDANCE**.

EOA sends: "REVISE (attempt 3 of 3) for task TSK-070 (SVG text measurement). Issue: The function `measureText()` in `src/text.py` line 34 reads `font-size` only from the element's direct style attribute. However, SVG elements inherit font-size from parent elements via CSS cascade. Correct behavior: traverse parent elements until a font-size is found, or use the SVG default (16px). Hint: check `element.parentNode` recursively for computed style. Deadline for resubmission: 90 minutes."

---

## Cross-References Between Trees

The 7 decision trees often chain into each other during real operations. Here are the most common transitions:

| From Tree | Trigger | To Tree |
|-----------|---------|---------|
| Tree 1 (Escalate vs Retry) → | "Try different approach" chosen, but new agent needed | → Tree 2 (Reassign vs Wait) |
| Tree 2 (Reassign vs Wait) → | Original agent recovers after reassignment | → Tree 5 (Agent Recovery) |
| Tree 4 (Verification Loop) → | Loop 4 fails, task must restart with possibly different agent | → Tree 1 (Escalate vs Retry) |
| Tree 6 (Direct vs Delegate) → | Task delegated, agent goes silent | → Tree 2 (Reassign vs Wait) |
| Tree 6 (Direct vs Delegate) → | Task delegated, agent submits result | → Tree 7 (Post-Task Interview) |
| Tree 7 (Post-Task Interview) → | REVISE issued, agent fails repeatedly | → Tree 1 (Escalate vs Retry) |
| Tree 7 (Post-Task Interview) → | Task approved, enters verification | → Tree 4 (Verification Loop) |

These transitions are natural -- when one tree's outcome leads to a new scenario, simply enter the appropriate tree with fresh input variables.
