---
name: amoa-remote-agent-coordinator
description: "Use when coordinating remote AI agents via AI Maestro messaging. NOT for human coordination. Trigger with agent delegation or multi-agent requests."
license: Apache-2.0
compatibility: AI Maestro (AMP), Python 3.9+
metadata:
  author: Emasoft
  version: 1.2.0
context: fork
user-invocable: false
agent: amoa-main
---

# Remote Agent Coordinator

## Overview

Delegates tasks to remote AI agents via AI Maestro messaging.

## Prerequisites

AI Maestro (AMP) running, Python 3.9+, registered agents.

## Instructions

1. Verify AI Maestro running and agents registered
2. Prepare task with ACK block, context, scope, criteria
3. Send via AMP, wait for ACK (5 min timeout)
4. Monitor progress every 10-15 min
5. Enforce 4 verification loops before PR approval

Copy this checklist and track your progress:

- [ ] Verify AMP running and agents registered
- [ ] Send task with ACK block and criteria
- [ ] Monitor progress and enforce 4 verification loops
- [ ] Approve or reject PR

## Output

ACK confirmations, progress reports, verification results, PR decisions.

## Examples

**Input:** `Delegate "fix auth bug #42" to libs-auth-agent`
**Output:** Task sent, ACK received, 4 loops done, PR approved.

## Error Handling

See [error-handling-protocol.md](./references/error-handling-protocol.md).
<!-- TOC: Error Handling Protocol | Overview | FAIL-FAST Principle | When Agents Must Stop and Report | Error Reporting Format | Error Report Message Schema | Error Types | Orchestrator Response to Errors | Acknowledging Error Reports | Providing Solutions | Escalation When Needed | Troubleshooting | Problem: Agent Not Reporting Errors | Problem: Agent Reports Same Error Repeatedly | Problem: Unclear Error Type | Problem: False Blocker Reports -->

## Resources

- [agent-registration.md](./references/agent-registration.md)
  - 1.0 Overview
  - 2.0 Agent Registration Format
    - 2.1 Required Fields for Agent Registration
  - ...
- [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md)
  - Purpose
  - Message Types: Instructions vs Conversations
    - How to Identify Task Delegations
  - ...
- [verification-loops-protocol.md](./references/verification-loops-protocol.md)
  - 1.0 Overview
  - 2.0 The Verification Flow
    - 2.1 Understanding the 5 PR Requests Cycle
  - ...
- [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md)
  - 1.0 Overview
  - 2.0 Proactive Monitoring Principles
  - 3.0 Status Request Protocol
  - ...
- [error-handling-protocol.md](./references/error-handling-protocol.md)
  - 1.0 Overview
    - 1.1 FAIL-FAST Principle
    - 1.2 When Agents Must Stop and Report
  - ...
- [escalation-procedures.md](./references/escalation-procedures.md)
  - Overview
  - Escalation Hierarchy
  - What Remote Agents Handle (Level 0)
  - ...
- [messaging-protocol.md](./references/messaging-protocol.md)
  - IMPORTANT: Official Skill Reference
  - Overview
  - Document Structure
  - ...
- [task-instruction-format.md](./references/task-instruction-format.md)
    - Quick Reference
    - Detailed References
  - Overview
  - ...
- [rule-15-no-implementation.md](./references/rule-15-no-implementation.md)
  - 1.0 Overview
  - 2.0 What the Orchestrator NEVER Does
    - 2.1 Never Write Code
  - ...
- [rule-14-immutable-requirements.md](./references/rule-14-immutable-requirements.md)
  - 1.0 Overview
  - 2.0 Mandatory Task Delegation Elements
    - 2.1 Requirement Reference Section
  - ...
- [script-output-rules.md](./references/script-output-rules.md)
  - Token-Efficient Output Protocol
  - Output Format
  - Exceptions
- [examples-remote-coordination.md](./references/examples-remote-coordination.md)
  - 1.0 Example: Onboard and Assign Task to New Agent
    - 1.1 Step-by-step onboarding flow
    - 1.2 Task delegation with ACK instructions
  - ...

