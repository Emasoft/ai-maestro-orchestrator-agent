---
name: amoa-remote-agent-coordinator
description: "Use when coordinating remote AI agents via AI Maestro messaging. NOT for human coordination. Trigger with agent delegation or multi-agent requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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
<!-- TOC: Table of Contents | 0 Overview | 1 FAIL-FAST Principle | 2 When Agents Must Stop and Report | 0 Error Reporting Format | 1 Error Report Message Schema | 2 Error Types | 0 Orchestrator Response to Errors | 1 Acknowledging Error Reports | 2 Providing Solutions | 3 Escalation When Needed | 0 Troubleshooting | Problem: Agent Not Reporting Errors | Problem: Agent Reports Same Error Repeatedly | Problem: Unclear Error Type | Problem: False Blocker Reports -->

## Resources

- [agent-registration.md](./references/agent-registration.md)
- [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md)
- [verification-loops-protocol.md](./references/verification-loops-protocol.md)
- [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md)
- [error-handling-protocol.md](./references/error-handling-protocol.md)
- [escalation-procedures.md](./references/escalation-procedures.md)
- [messaging-protocol.md](./references/messaging-protocol.md)
- [task-instruction-format.md](./references/task-instruction-format.md)
- [rule-15-no-implementation.md](./references/rule-15-no-implementation.md)
- [rule-14-immutable-requirements.md](./references/rule-14-immutable-requirements.md)
- [script-output-rules.md](./references/script-output-rules.md)
- [examples-remote-coordination.md](./references/examples-remote-coordination.md)

