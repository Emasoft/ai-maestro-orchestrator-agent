# Error Handling Protocol


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
  - [1.1 FAIL-FAST Principle](#11-fail-fast-principle)
  - [1.2 When Agents Must Stop and Report](#12-when-agents-must-stop-and-report)
- [2.0 Error Reporting Format](#20-error-reporting-format)
  - [2.1 Error Report Message Schema](#21-error-report-message-schema)
  - [2.2 Error Types](#22-error-types)
- [3.0 Orchestrator Response to Errors](#30-orchestrator-response-to-errors)
  - [3.1 Acknowledging Error Reports](#31-acknowledging-error-reports)
  - [3.2 Providing Solutions](#32-providing-solutions)
  - [3.3 Escalation When Needed](#33-escalation-when-needed)
- [4.0 Troubleshooting](#40-troubleshooting)
  - [Problem: Agent Not Reporting Errors](#problem-agent-not-reporting-errors)
  - [Problem: Agent Reports Same Error Repeatedly](#problem-agent-reports-same-error-repeatedly)
  - [Problem: Unclear Error Type](#problem-unclear-error-type)
  - [Problem: False Blocker Reports](#problem-false-blocker-reports)

---

## Table of Contents

- 1.0 Overview
- 1.1 FAIL-FAST Principle
- 1.2 When agents must stop and report
- 2.0 Error Reporting Format
- 2.1 Error report message schema
- 2.2 Error types
- 3.0 Orchestrator Response to Errors
- 3.1 Acknowledging error reports
- 3.2 Providing solutions
- 3.3 Escalation when needed

---

## 1.0 Overview

### 1.1 FAIL-FAST Principle

Remote agents must follow FAIL-FAST:

- NO workarounds
- NO fallbacks
- NO temporal solutions
- If blocked, REPORT and WAIT

### 1.2 When Agents Must Stop and Report

Agents should stop work and report when:
- Tests fail unexpectedly
- Dependencies cannot be resolved
- Specification is unclear or contradictory
- Architecture decision required
- Security concern discovered
- Cannot access required resources

---

## 2.0 Error Reporting Format

### 2.1 Error Report Message Schema

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "BLOCKED: Cannot complete {task_id}",
  "priority": "high",
  "content": {
    "type": "error-report",
    "task_id": "GH-XXX",
    "error_type": "dependency|test-failure|unclear-spec|blocked",
    "description": "Detailed description of the error",
    "attempted_solutions": [
      "Solution 1 that was tried",
      "Solution 2 that was tried"
    ],
    "blocking_at_checkpoint": "checkpoint_name",
    "suggested_action": "What the agent thinks should happen next"
  }
}
```

### 2.2 Error Types

| Type | Meaning | Example |
|------|---------|---------|
| `dependency` | Missing or conflicting dependency | Package version conflict |
| `test-failure` | Tests fail unexpectedly | CI passes, local fails |
| `unclear-spec` | Specification ambiguous | Missing acceptance criteria |
| `blocked` | Cannot proceed | Resource unavailable |
| `security` | Security concern found | Potential vulnerability |
| `architecture` | Design decision needed | Multiple valid approaches |

---

## 3.0 Orchestrator Response to Errors

### 3.1 Acknowledging Error Reports

The orchestrator MUST acknowledge error reports within 5 minutes:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "ACK: Error report for {task_id}",
  "priority": "high",
  "content": {
    "type": "error-ack",
    "task_id": "GH-XXX",
    "message": "Received your error report. Analyzing and will provide guidance."
  }
}
```

### 3.2 Providing Solutions

After analysis, provide concrete next steps:

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "<agent-session-name>",
  "subject": "SOLUTION: {task_id} blocker resolution",
  "priority": "high",
  "content": {
    "type": "solution",
    "task_id": "GH-XXX",
    "solution": "Detailed solution steps",
    "fallback": "What to do if solution doesn't work",
    "escalation_threshold": "When to report back if still blocked"
  }
}
```

### 3.3 Escalation When Needed

If the error requires user decision:
1. Acknowledge to agent that escalation is needed
2. Create escalation message to user
3. Keep agent informed of status
4. Relay user decision back to agent

---

## 4.0 Troubleshooting

### Problem: Agent Not Reporting Errors

**Symptoms**: Agent goes silent, no error reports received, task stalls.

**Solution**:
1. Send proactive status check message using the `agent-messaging` skill
2. If no response, check if agent is online
3. If agent is online but unresponsive, send explicit "Are you blocked?" message
4. Reassign task if no response after 3 attempts

### Problem: Agent Reports Same Error Repeatedly

**Symptoms**: Agent sends identical error reports, solution not working.

**Solution**:
1. Review the proposed solution - may be incomplete
2. Ask agent to provide more context about why solution fails
3. Escalate to user if root cause unclear
4. Consider reassigning to agent with different expertise

### Problem: Unclear Error Type

**Symptoms**: Agent reports error but type field is missing or wrong.

**Solution**:
1. Respond asking for specific error type from allowed list
2. Provide error type definitions in response
3. If agent consistently misclassifies, include error type guide in future task assignments

### Problem: False Blocker Reports

**Symptoms**: Agent reports being blocked but issue is solvable by agent.

**Solution**:
1. Ask agent what specific solutions they tried
2. If agent tried nothing, remind them of FAIL-FAST applies to real blockers only
3. Provide guidance on self-debugging techniques
4. Reserve blocking reports for genuine external dependencies
