# Escalation Procedures

## Overview

This document defines when and how the EOA (Emasoft Orchestrator Agent) escalates issues to the user or higher authority. Proper escalation ensures problems are addressed without exceeding orchestrator's decision-making scope.

## Contents

- **[If you need to understand the escalation hierarchy](#escalation-hierarchy)** - Learn which authority level handles which types of decisions
- **[If a remote agent can handle something autonomously](#what-remote-agents-handle-level-0)** - Identify what agents resolve without escalation
- **[If the orchestrator needs to make a decision](#what-orchestrator-handles-level-1)** - See what requires orchestrator-level decisions
- **[If you need to escalate to the user](#what-requires-user-escalation-level-2)** - Determine when user involvement is required and with what priority
- **[If you need to format an escalation message](#escalation-message-formats)** - Use proper message structures for different escalation types
- **[If you need to handle different escalation categories](#escalation-categories)** - Understand security, architecture, dependency, and resource escalations
- **[If you're waiting for an escalation response](#escalation-response-handling)** - Know how to handle user responses and no-response scenarios
- **[If you need to manage the escalation queue](#escalation-queue-management)** - Track and prioritize pending escalations
- **[If you want best practices for escalation](#dos-and-donts)** - Learn what to do and avoid when escalating
- **[If you need to track escalation metrics](#metrics)** - Monitor escalation patterns and identify improvements

## Escalation Hierarchy

```
Level 0: Remote Agent (can handle autonomously)
    ↓
Level 1: Orchestrator (coordination decisions)
    ↓
Level 2: User (architecture, security, business)
```

## What Remote Agents Handle (Level 0)

Agents resolve autonomously:
- Code implementation details
- Test writing and debugging
- Minor refactoring within scope
- Documentation updates
- Dependency version patches (minor)

## What Orchestrator Handles (Level 1)

Orchestrator decides:
- Task assignment and reassignment
- Scheduling and prioritization
- PR approval/rejection based on gates
- Agent coordination
- Progress tracking
- Minor scope clarifications

## What Requires User Escalation (Level 2)

### Immediate Escalation (Urgent)

Escalate IMMEDIATELY for:

| Issue Type | Example | Why Immediate |
|------------|---------|---------------|
| Security vulnerability | SQL injection found | Production risk |
| Data corruption risk | Migration might lose data | Irreversible |
| Legal/compliance | License incompatibility | Legal exposure |
| Breaking change | API contract violation | External impact |
| Production incident | Service down | Business impact |

### Deferred Escalation (Morning Queue)

Can wait until morning:

| Issue Type | Example | Why Deferrable |
|------------|---------|----------------|
| Architecture question | Redis vs Memcached | No urgency |
| Dependency choice | Which testing framework | No urgency |
| Feature interpretation | "fast" means how fast? | Clarification |
| Resource request | Need more agents | Planning |
| Process question | Which branch strategy? | Methodology |

## Escalation Message Formats

### Urgent Escalation

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "URGENT ESCALATION: [brief description]",
  "priority": "urgent",
  "content": {
    "type": "escalation",
    "escalation_level": "urgent",
    "task_id": "GH-42",
    "category": "security|data|legal|breaking|incident",
    "summary": "One-line summary of the issue",
    "details": "Full description of what was found",
    "impact": "What happens if not addressed",
    "discovered_at": "2025-12-30T03:00:00Z",
    "recommended_action": "What should be done",
    "awaiting_response": true,
    "contact_user": true
  }
}
```

### Deferred Escalation

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "MORNING REVIEW: [brief description]",
  "priority": "normal",
  "content": {
    "type": "escalation",
    "escalation_level": "deferred",
    "task_id": "GH-42",
    "category": "architecture|dependency|interpretation|resource|process",
    "summary": "One-line summary",
    "details": "Full context",
    "options": [
      {
        "option": "A",
        "description": "Use Redis",
        "pros": ["More features", "Persistence"],
        "cons": ["More complex"]
      },
      {
        "option": "B",
        "description": "Use Memcached",
        "pros": ["Simpler", "Faster for cache"],
        "cons": ["No persistence"]
      }
    ],
    "recommendation": "A",
    "recommendation_rationale": "Project needs persistence for sessions",
    "interim_action": "Proceeding with A unless instructed otherwise",
    "reversible": true,
    "awaiting_response": true,
    "review_checkpoint": "next-planning-cycle"
  }
}
```

### Blocker Escalation

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "BLOCKED: [brief description]",
  "priority": "high",
  "content": {
    "type": "escalation",
    "escalation_level": "blocker",
    "task_id": "GH-42",
    "review_cycles_blocked": 3,
    "retry_attempts": 2,
    "blocker_type": "external|internal|unclear-spec|dependency",
    "description": "What is blocking progress",
    "attempted_solutions": [
      "Tried X - result Y",
      "Tried A - result B"
    ],
    "required_to_unblock": "What is needed to continue",
    "workaround_available": false,
    "impact_on_dependencies": "Blocks GH-42 completion and dependent GH-43"
  }
}
```

## Escalation Categories

### Security

**Triggers**:
- Credentials in code
- SQL injection
- XSS vulnerability
- Authentication bypass
- Unauthorized access
- Data exposure

**Action**: STOP work, escalate immediately, do not commit vulnerable code.

### Architecture

**Triggers**:
- Design pattern choice not in methodology
- New component introduction
- Database schema changes
- API contract changes
- Service boundaries

**Action**: Document options, make recommendation, proceed with best judgment if deferrable, flag for review.

### Dependency

**Triggers**:
- New dependency needed
- Dependency version conflict
- License incompatibility
- Deprecated dependency
- Major version upgrade

**Action**: Document need, suggest alternatives, await approval for new deps.

### Unclear Specification

**Triggers**:
- Ambiguous requirement
- Contradictory requirements
- Missing acceptance criteria
- Edge case not specified

**Action**: Document interpretation options, proceed with most likely intent, flag for confirmation.

### Resource

**Triggers**:
- Need more agents
- Agent unavailable
- Infrastructure limit
- Capacity constraint

**Action**: Document need, suggest reallocation, await guidance.

## Escalation Response Handling

### When User Responds

1. **Acknowledge receipt**
   ```json
   {
     "type": "escalation-acknowledgment",
     "escalation_id": "esc-123",
     "received_at": "2025-12-30T08:00:00Z"
   }
   ```

2. **Implement decision**
   - Update task instructions
   - Notify affected agents
   - Update GitHub issue

3. **Confirm implementation**
   ```json
   {
     "type": "escalation-resolved",
     "escalation_id": "esc-123",
     "decision": "A",
     "implemented_at": "2025-12-30T08:30:00Z",
     "notes": "Switched to Redis per user decision"
   }
   ```

### When No Response

| Escalation Type | Retry Limit | Default Action |
|-----------------|-------------|----------------|
| Urgent | After 3 retry attempts | Continue retrying, add to next planning report |
| Deferred | After next planning cycle | Proceed with recommendation |
| Blocker | After 2 review cycles | Reassign or defer task |

## Escalation Queue Management

### Queue File

Maintain `ESCALATION_QUEUE.md`:

```markdown
# Escalation Queue

## Urgent (Awaiting Immediate Response)
| ID | Retry Count | Task | Issue | Status |
|----|-------------|------|-------|--------|
| esc-001 | 2 | GH-42 | Security: SQL injection | AWAITING |

## Next Planning Review (Deferred)
| ID | Review Cycle | Task | Issue | Recommendation |
|----|--------------|------|-------|----------------|
| esc-002 | 1 | GH-43 | Architecture: Redis vs Memcached | Redis |
| esc-003 | 1 | GH-44 | Dependency: Add new testing lib | Approve |

## Resolved
| ID | Attempts | Task | Issue | Decision | By |
|----|----------|------|-------|----------|-----|
| esc-000 | 1 | GH-41 | Unclear spec | Clarified | User |
```

### Priority Rules

1. Security always first
2. Blockers by retry count (most attempts first)
3. Deferred by task priority
4. FIFO within same priority

## Do's and Don'ts

### DO

- Escalate early if uncertain
- Include all context
- Provide clear options
- Make recommendations
- Document interim actions
- Track resolution

### DON'T

- Make security decisions autonomously
- Change architecture without approval
- Add dependencies without approval
- Ignore escalation responses
- Escalate the same issue repeatedly
- Assume user saw the message

## Metrics

Track escalation patterns:

```markdown
## Escalation Metrics (Per Sprint)

| Category | Count | Avg Retry Attempts | Resolution Rate |
|----------|-------|--------------------|-----------------|
| Security | 1 | 1 | 100% |
| Architecture | 3 | 2 | 100% |
| Dependency | 2 | 1 | 100% |
| Unclear spec | 5 | 2 | 100% |
| Blocker | 2 | 3 | 100% |

### Insights
- High unclear spec count suggests need for better requirements
- All security escalations resolved within first attempt (good)
```

## Decision Trees for Escalation Handling

### Cross-Reference

For the core Escalate vs Retry decision tree, see `decision-trees-core.md` Section 1.

### No Response Escalation Decision Tree

When an escalation sent to ECOS, EAMA, or EAA gets no response, follow this decision tree:

```
Escalation sent, no response received
├─ How long since escalation was sent?
│   ├─ < 10 minutes → Wait (within normal response window)
│   ├─ 10-30 minutes → Send follow-up reminder with original escalation context
│   │   ├─ Response received → Process response normally
│   │   └─ Still no response → Continue to next check
│   ├─ 30-60 minutes → Re-send escalation with priority bumped up one level
│   │   ├─ Was originally "normal" → Re-send as "high"
│   │   ├─ Was originally "high" → Re-send as "urgent"
│   │   └─ Was already "urgent" → Send to ALL available ECOS instances
│   └─ > 60 minutes → Emergency protocol
│       ├─ Is the blocked task critical path?
│       │   ├─ Yes → Pause ALL dependent tasks → Document full state
│       │   │         → Send emergency notification to ECOS with full audit trail
│       │   └─ No → Continue other work → Log timeout incident
│       └─ Record incident for post-mortem review
```

### User Response Processing Decision Tree

When EOA receives a user decision relayed through EAMA or ECOS, follow this decision tree:

```
User decision received via ECOS/EAMA relay
├─ Is the decision clear and actionable?
│   ├─ Yes → Does it match one of the options EOA presented?
│   │         ├─ Yes → Execute the chosen option
│   │         │         → Send confirmation to ECOS: "Executing option X as directed"
│   │         │         → Update affected agents with new direction
│   │         │         → Resume paused tasks if applicable
│   │         └─ No (user chose something different) → Is the alternative feasible?
│   │             ├─ Yes → Adapt plan to user's choice → Execute
│   │             └─ No → Send back explanation of why it's not feasible
│   │                     → Provide revised options → Wait for new decision
│   └─ No (ambiguous or incomplete) → Send clarification request through ECOS
│       → Include: what was understood, what needs clarification, specific questions
│       → Continue other unblocked work while waiting
```
