# Edge Case Protocols for Orchestrator Agent


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 AI Maestro Unavailable](#10-ai-maestro-unavailable)
  - [1.1 Detection Methods](#11-detection-methods)
  - [1.2 Response Workflow](#12-response-workflow)
  - [1.3 Queue Management](#13-queue-management)
  - [1.4 Fallback Coordination](#14-fallback-coordination)
- [AI Maestro Fallback: Task Assignment](#ai-maestro-fallback-task-assignment)
  - [Instructions](#instructions)
  - [Response Required](#response-required)
- [2.0 GitHub Unavailable](#20-github-unavailable)
  - [2.1 Detection Methods](#21-detection-methods)
  - [2.2 Response Workflow](#22-response-workflow)
  - [2.3 Local State Caching](#23-local-state-caching)
- [3.0 Remote Agent Timeout](#30-remote-agent-timeout)
  - [3.1 Detection Methods](#31-detection-methods)
  - [3.2 Escalation Ladder](#32-escalation-ladder)
  - [3.3 Reassignment Protocol](#33-reassignment-protocol)
- [4.0 Module Assignment Failures](#40-module-assignment-failures)
  - [4.1 Agent Capacity Exceeded](#41-agent-capacity-exceeded)
  - [4.2 Skill Mismatch](#42-skill-mismatch)
  - [4.3 Dependency Deadlock](#43-dependency-deadlock)
- [5.0 Progress Monitoring Failures](#50-progress-monitoring-failures)
  - [5.1 Stale Progress Reports](#51-stale-progress-reports)
  - [5.2 Conflicting Status Updates](#52-conflicting-status-updates)
  - [5.3 Missing Checkpoints](#53-missing-checkpoints)
- [6.0 Incomplete Task Instructions](#60-incomplete-task-instructions)
  - [6.1 Detection Methods](#61-detection-methods)
  - [6.2 Clarification Protocol](#62-clarification-protocol)
  - [6.3 Blocking Behavior](#63-blocking-behavior)
- [Emergency Recovery](#emergency-recovery)
- [Related Documents](#related-documents)

---

This document defines standardized protocols for handling edge cases and failure scenarios in the Orchestrator Agent (eoa-) plugin.

## Table of Contents

- 1.0 AI Maestro Unavailable
  - 1.1 Detection Methods
  - 1.2 Response Workflow
  - 1.3 Queue Management
  - 1.4 Fallback Coordination
- 2.0 GitHub Unavailable
  - 2.1 Detection Methods
  - 2.2 Response Workflow
  - 2.3 Local State Caching
- 3.0 Remote Agent Timeout
  - 3.1 Detection Methods
  - 3.2 Escalation Ladder
  - 3.3 Reassignment Protocol
- 4.0 Module Assignment Failures
  - 4.1 Agent Capacity Exceeded
  - 4.2 Skill Mismatch
  - 4.3 Dependency Deadlock
- 5.0 Progress Monitoring Failures
  - 5.1 Stale Progress Reports
  - 5.2 Conflicting Status Updates
  - 5.3 Missing Checkpoints
- 6.0 Incomplete Task Instructions
  - 6.1 Detection Methods
  - 6.2 Clarification Protocol
  - 6.3 Blocking Behavior

---

## 1.0 AI Maestro Unavailable

### 1.1 Detection Methods

The Orchestrator relies on AI Maestro for inter-agent communication. Detect unavailability through:

| Check | Method | Failure Indicator |
|-------|--------|-------------------|
| API Health | Use `agent-messaging` skill health check | HTTP 503/504 or timeout |
| Connection Test | Use `agent-messaging` skill to query unread count | Connection timeout after 10 seconds |
| Agent Registry | Use `agent-messaging` skill to query agent registry | Registry unreachable or empty response |

### 1.2 Response Workflow

When AI Maestro is unavailable, follow this protocol:

1. **Log the failure**:
   ```bash
   echo "$(date -Iseconds) | AIMAESTRO_UNAVAILABLE | AI Maestro AMP | HTTP $STATUS_CODE" >> .claude/logs/maestro-failures.log
   ```

2. **Queue outgoing messages**:

   > **Note**: This offline fallback is ONLY for when AI Maestro is completely unreachable. Under normal conditions, always use the `agent-messaging` skill to send messages.

   ```bash
   mkdir -p .claude/queue/outbox
   cat > ".claude/queue/outbox/${RECIPIENT_AGENT}-$(date +%s).json" <<EOF
   {
     "to": "${RECIPIENT_AGENT}",
     "subject": "${SUBJECT}",
     "priority": "${PRIORITY}",
     "content": {"type": "${TYPE}", "message": "${MESSAGE}"},
     "queued_at": "$(date -Iseconds)"
   }
   EOF
   ```

3. **Display warning to user**:
   ```
   WARNING: AI Maestro is unavailable. Messages queued locally.
   Queued: N messages in .claude/queue/outbox/
   Will retry every 5 minutes.
   ```

4. **Use fallback coordination** (see section 1.4)

5. **Retry schedule**:
   - Retry every 5 minutes
   - After 30 minutes (6 retries), require user intervention
   - Present options: wait, use fallback, abort current tasks

### 1.3 Queue Management

Process queued messages when AI Maestro recovers:

When AI Maestro recovers, flush the queue by sending each queued message using the `agent-messaging` skill, then remove the processed queue files.

### 1.4 Fallback Coordination

When AI Maestro is down, use these fallback methods:

| Priority | Method | Use Case |
|----------|--------|----------|
| 1st | GitHub Issues | Task assignments, status updates |
| 2nd | Handoff .md files | Detailed instructions, specifications |
| 3rd | Direct polling | Check `.claude/shared/` directories |

**GitHub Issue Fallback Template**:
```markdown
## AI Maestro Fallback: Task Assignment

**To**: @agent-name
**Priority**: HIGH
**Type**: task_assignment

### Instructions
[Task details here]

### Response Required
Reply to this issue with status updates every 30 minutes.
```

---

## 2.0 GitHub Unavailable

### 2.1 Detection Methods

| Check | Command | Failure Indicator |
|-------|---------|-------------------|
| API Status | `gh api rate_limit` | HTTP 5xx errors |
| Network | `gh issue list --limit 1` | Network failure |
| Rate Limit | `gh api rate_limit --jq '.rate.remaining'` | Returns 0 (403 error) |

### 2.2 Response Workflow

1. **Cache last known state**:
   ```bash
   mkdir -p .claude/cache/github
   cp .claude/state/github-*.json .claude/cache/github/
   echo "$(date -Iseconds)" > .claude/cache/github/cached_at
   ```

2. **Queue GitHub operations**:
   ```bash
   mkdir -p .claude/queue/github
   cat > ".claude/queue/github/op-$(date +%s).json" <<EOF
   {
     "operation": "issue_create",
     "params": {...},
     "queued_at": "$(date -Iseconds)"
   }
   EOF
   ```

3. **Notify user**:
   ```
   WARNING: GitHub is temporarily unavailable.
   - Cached state from: [timestamp]
   - Queued operations: N
   - Continuing with non-GitHub work.
   - Will retry every 10 minutes.
   ```

4. **Continue with non-GitHub work**:
   - Local file operations
   - Code generation
   - Test execution
   - Documentation updates

5. **Retry every 10 minutes** until GitHub recovers

### 2.3 Local State Caching

Maintain local mirrors of critical GitHub state:

| State | Location | Refresh |
|-------|----------|---------|
| Open issues | `.claude/cache/github/issues.json` | Every poll |
| PR status | `.claude/cache/github/prs.json` | Every poll |
| Project board | `.claude/cache/github/project.json` | Every poll |

---

## 3.0 Remote Agent Unresponsive

### 3.1 Detection Methods

AI agents collaborate asynchronously and may be hibernated for extended periods. Detection is based on **state**, not elapsed time.

| State | Detection | Priority |
|-------|-----------|----------|
| No ACK | Agent has not acknowledged task receipt | Normal |
| No Progress | Agent acknowledged but no status update since | Normal |
| Stale | Agent's last update predates significant system events | High |
| Unresponsive | Multiple reminders sent without any response | Urgent |
| Offline | AI Maestro reports agent session terminated | Immediate |

### 3.2 Escalation Order

Follow this escalation sequence **in order**:

**Step 1: First Reminder (when state = No ACK or No Progress)**

Send a first reminder using the `agent-messaging` skill:
- **Recipient**: the unresponsive agent session name
- **Subject**: "Progress Check: Task <TASK_ID>"
- **Content**: "Please provide status update for task <TASK_ID>. Awaiting response."
- **Type**: `status_request`, **Priority**: `high`

**Verify**: confirm message delivery.

**Step 2: Urgent Reminder (when state = Unresponsive after Step 1)**

Send an urgent escalation using the `agent-messaging` skill:
- **Recipient**: the unresponsive agent session name
- **Subject**: "URGENT: Task <TASK_ID> - Response Required"
- **Content**: "No response to previous reminder. Task may be reassigned if no response."
- **Type**: `escalation`, **Priority**: `urgent`

**Verify**: confirm message delivery.

**Step 3: Escalate to User or Reassign (when still unresponsive after Step 2)**
- If user online: Present options (wait, reassign, abort)
- If user offline: Auto-reassign to available agent (see 3.3)

### 3.3 Reassignment Protocol

When reassigning a timed-out task:

1. **Mark original assignment as abandoned**:
   ```json
   {
     "task_id": "TASK-001",
     "original_agent": "agent-name",
     "status": "abandoned",
     "reason": "unresponsive",
     "abandoned_at": "<ISO-8601-timestamp>"
   }
   ```

2. **Select new agent**:
   - Check agent availability via AI Maestro
   - Match agent skills to task requirements
   - Avoid reassigning to overloaded agents

3. **Transfer context**:
   - Include all original instructions
   - Include any partial progress from abandoned agent
   - Add note: "Reassigned from [agent] due to timeout"

4. **Notify all parties**:
   - Original agent: "Task reassigned due to timeout"
   - New agent: Task assignment with full context
   - User: "Task [ID] reassigned from [agent] to [new_agent]"

---

## 4.0 Module Assignment Failures

### 4.1 Agent Capacity Exceeded

**Detection**: Agent responds with "at capacity" or has more than 3 active modules.

**Response**:
1. Check other agents for availability
2. If all agents at capacity:
   - Queue module with priority
   - Notify user: "All agents at capacity. Module queued."
   - Set reminder to check again in 15 minutes
3. Consider spawning additional agent session

### 4.2 Skill Mismatch

**Detection**: Agent reports missing skills for assigned module.

**Response**:
1. Review module requirements
2. Search for agent with matching skills
3. If no match found:
   - Split module into smaller tasks
   - Assign parts to different specialized agents
   - Create coordination task to integrate results

### 4.3 Dependency Deadlock

**Detection**: Module A depends on Module B, which depends on Module A.

**Response**:
1. Log the circular dependency
2. Present to user with visualization:
   ```
   CIRCULAR DEPENDENCY DETECTED:
   Module A (auth-service) -> depends on -> Module B (user-service)
   Module B (user-service) -> depends on -> Module A (auth-service)
   ```
3. Request user guidance on resolution:
   - Break dependency by creating interface
   - Merge modules
   - Implement one with mock, update later

---

## 5.0 Progress Monitoring Failures

### 5.1 Stale Progress Reports

**Detection**: Progress report timestamp older than 30 minutes.

**Response**:
1. Send status request to agent
2. If no response in 5 minutes, escalate per section 3.2
3. Mark progress as "STALE" in status displays
4. Continue polling at increased frequency (every 5 minutes)

### 5.2 Conflicting Status Updates

**Detection**: Agent reports "complete" but verification shows incomplete.

**Response**:
1. Log the conflict:
   ```json
   {
     "conflict_type": "status_mismatch",
     "reported": "complete",
     "verified": "incomplete",
     "missing": ["tests", "documentation"]
   }
   ```
2. Send clarification request to agent
3. Block status advancement until resolved
4. If unresolved after 2 clarification attempts, escalate to user

### 5.3 Missing Checkpoints

**Detection**: Expected checkpoint file not found after task marked complete.

**Response**:
1. Request checkpoint from agent
2. Provide template of expected checkpoint format
3. Block completion until checkpoint received
4. If agent cannot provide checkpoint, mark task for review

---

## 6.0 Incomplete Task Instructions

### 6.1 Detection Methods

| Missing Element | Detection |
|-----------------|-----------|
| Required field empty | JSON schema validation |
| Ambiguous requirements | Multiple possible interpretations |
| Conflicting constraints | Mutually exclusive requirements |
| Missing dependencies | Referenced module not defined |

### 6.2 Clarification Protocol

1. **List missing or ambiguous items**:
   ```
   INCOMPLETE TASK INSTRUCTIONS

   Missing:
   - [ ] Success criteria not defined
   - [ ] Output file path not specified

   Ambiguous:
   - "Handle errors appropriately" - Need specific error handling requirements

   Conflicting:
   - "Must be fast" vs "Must be thorough" - Need priority guidance
   ```

2. **Generate clarification questions**:
   ```
   Questions for User:
   1. What are the success criteria for this task?
   2. Where should output files be written?
   3. Should error handling prioritize recovery or fail-fast?
   4. Should we prioritize speed or thoroughness?
   ```

3. **Block progression** until all questions answered

4. **Verify answers resolve ambiguities**:
   - Re-validate against schema
   - Confirm no remaining conflicts
   - Get explicit confirmation before proceeding

### 6.3 Blocking Behavior

The Orchestrator MUST NOT proceed with task assignment when:

| Condition | Reason |
|-----------|--------|
| Missing success criteria | Cannot verify completion |
| Missing output location | Cannot locate results |
| Conflicting requirements | Cannot satisfy both |
| Missing skill requirements | Cannot select agent |

Display to user:
```
BLOCKED: Cannot proceed with task assignment.

Reason: [specific reason]

Required information:
- [list of required items]

Please provide the missing information or modify the requirements.
```

---

## Emergency Recovery

If multiple edge cases compound (e.g., AI Maestro down + GitHub down + agent timeout):

1. **Stop all active tasks**
2. **Save complete state to local files**
3. **Create recovery checkpoint**
4. **Notify user immediately**
5. **Wait for user guidance before resuming**

Recovery checkpoint location: `.claude/recovery/checkpoint-{timestamp}.json`

---

## Related Documents

- [error-handling-protocol.md](../../eoa-remote-agent-coordinator/references/error-handling-protocol.md) - Detailed error handling
- [escalation-procedures.md](../../eoa-remote-agent-coordinator/references/escalation-procedures.md) - Escalation ladder
- [progress-monitoring-protocol.md](../../eoa-remote-agent-coordinator/references/progress-monitoring-protocol.md) - Monitoring patterns
- [messaging-protocol.md](../../eoa-remote-agent-coordinator/references/messaging-protocol.md) - AI Maestro messaging
