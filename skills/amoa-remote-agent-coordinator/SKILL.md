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

Delegates coding tasks to remote AI agents via AI Maestro messaging. The orchestrator NEVER writes code.

## Prerequisites

AI Maestro (AMP) running, Python 3.9+, registered agents. See [agent-registration.md](./references/agent-registration.md).
<!-- TOC: Overview | Active Agents | Full Template -->

## Core Protocols

| Protocol | Reference |
|----------|-----------|
| ACK Protocol | [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) |
<!-- TOC: Message flow reference | Integration with other protocols -->
| 4-Verification Loops | [verification-loops-protocol.md](./references/verification-loops-protocol.md) |
<!-- TOC: Overview | Verification Flow | Step-by-Step | 5 PR Requests | Rules | Troubleshooting -->
| Progress Monitoring | [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md) |
<!-- TOC: Overview | Monitoring | Status | Completion | Templates -->
| Error Handling | [error-handling-protocol.md](./references/error-handling-protocol.md) |
<!-- TOC: Overview | Error Reporting Format | Orchestrator Response to Errors | Troubleshooting -->
| Escalation | [escalation-procedures.md](./references/escalation-procedures.md) |
<!-- TOC: Overview | Metrics | Escalation Categories -->
| Messaging | [messaging-protocol.md](./references/messaging-protocol.md) |
<!-- TOC: Overview | Structure | Quick Ref | Navigation -->

## Task Instruction Format

Every task MUST include: ACK block, PR notification, context, scope, interface contract, files, tests, criteria. Require 4 verification loops before PR.
See [task-instruction-format.md](./references/task-instruction-format.md)
<!-- TOC: Quick Reference | Detailed References -->

## Orchestrator Rules

- **Rule 15**: Orchestrator NEVER writes code. See [rule-15-no-implementation.md](./references/rule-15-no-implementation.md)
  <!-- TOC: Overview | Never Write Code | Self-Check Questions -->
- **Rule 14**: Every delegation MUST include requirement refs, forbidden actions. See [rule-14-immutable-requirements.md](./references/rule-14-immutable-requirements.md)
  <!-- TOC: Overview | Mandatory Elements | Template Reqs | Violation Handling -->

## Output

ACK confirmations, progress reports, verification results, PR approval decisions.

## Instructions

1. Verify AI Maestro is running and target agents are registered
2. Prepare task message with ACK block, context, scope, and acceptance criteria
3. Send task via AI Maestro messaging and wait for ACK (5 min timeout)
4. Monitor agent progress proactively every 10-15 minutes
5. Enforce 4 verification loops before approving PR creation

Copy this checklist and track your progress:

- [ ] Verify AI Maestro is running and agents registered
- [ ] Prepare task message with ACK block and criteria
- [ ] Send task and wait for ACK
- [ ] Monitor agent progress
- [ ] Enforce 4 verification loops before approving PR

## Error Handling

See [error-handling-protocol.md](./references/error-handling-protocol.md) for error reporting and troubleshooting.
<!-- TOC: Overview | Error Format | Response | Troubleshooting -->

## Examples

**Input:** `Delegate "fix auth bug #42" to libs-auth-agent with ACK protocol`
**Output:** Task sent via AMP, ACK received, 4 verification loops enforced, PR approved.

See [examples-remote-coordination.md](./references/examples-remote-coordination.md).
<!-- TOC: Loop counter tracking | Proactive polling sequence -->

## Resources

- [agent-registration.md](./references/agent-registration.md) — Agent registration/roster
  <!-- TOC: Overview | Active Agents | Full Template -->
- [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) — ACK
  <!-- TOC: Message flow reference | Integration with other protocols -->
- [verification-loops-protocol.md](./references/verification-loops-protocol.md) — 4-loops
  <!-- TOC: Overview | Flow | Steps | 5 PR Requests | Rules | Troubleshooting -->
- [error-handling-protocol.md](./references/error-handling-protocol.md) — Errors
  <!-- TOC: Overview | Error Format | Response | Troubleshooting -->
- [task-instruction-format.md](./references/task-instruction-format.md) — Task format
  <!-- TOC: Quick Reference | Detailed References -->
- [script-output-rules.md](./references/script-output-rules.md) — Output rules
  <!-- TOC: Token-Efficient Protocol | Output Format | Exceptions -->

