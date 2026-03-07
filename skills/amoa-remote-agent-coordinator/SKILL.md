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

AI Maestro (AMP) running, Python 3.9+, registered agents. See [agent-registration](./references/agent-registration.md).

## Workflow

1. Verify AI Maestro is running and agents are registered
2. Prepare delegation with ACK protocol + complete instruction format
3. Send task via AI Maestro, wait for ACK (5 min timeout)
4. Monitor proactively every 10-15 minutes
5. Enforce 4-verification-loop before PR approval
6. Review completion against acceptance criteria

Checklist: See [coordination-checklist.md](./references/coordination-checklist.md)

## Core Protocols

| Protocol | Reference |
|----------|-----------|
| ACK Protocol | [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) |
| 4-Verification Loops | [verification-loops-protocol.md](./references/verification-loops-protocol.md) |
| Progress Monitoring | [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md) |
| Error Handling | [error-handling-protocol.md](./references/error-handling-protocol.md) |
| Escalation | [escalation-procedures.md](./references/escalation-procedures.md) |
| Messaging | [messaging-protocol.md](./references/messaging-protocol.md) |

## MANDATORY: ACK Protocol

Include ACK instructions in EVERY task message. See [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md) section 2.3.

## Task Instruction Format

Every task MUST include: ACK block, PR notification, context, scope, interface contract, files, tests, criteria.
See [task-instruction-format.md](./references/task-instruction-format.md)

## MANDATORY: 4-Verification Loops

Require 4 loops before PR approval. See [verification-loops-protocol.md](./references/verification-loops-protocol.md)

## Orchestrator Rules

- **Rule 15**: Orchestrator NEVER writes code. See [rule-15-no-implementation.md](./references/rule-15-no-implementation.md)
- **Rule 14**: Every delegation MUST include requirement refs, forbidden actions, escalation. See [rule-14-immutable-requirements.md](./references/rule-14-immutable-requirements.md)

## References

All reference docs are in `./references/` covering: agent onboarding/registration/types/templates, operations (overnight, coordination, document storage, artifacts, bug reporting), config (central config, change notification, toolchain templates), LSP (overview, installation, enforcement, management), and skills (format, authoring, directory structure).

## Troubleshooting

See [error-handling-troubleshooting.md](./references/error-handling-troubleshooting.md)

## Scripts & Output

See [design-document-scripts.md](./references/design-document-scripts.md) and [script-output-rules.md](./references/script-output-rules.md)

## Instructions

1. Verify AI Maestro is running and target agents are registered.
2. Prepare the task message with ACK block, context, scope, acceptance criteria per [task-instruction-format.md](./references/task-instruction-format.md).
3. Send the task via AI Maestro messaging and wait for ACK (5 min timeout).
4. Monitor agent progress proactively every 10-15 minutes.
5. Enforce 4 verification loops before approving PR creation.

## Output

See [script-output-rules.md](./references/script-output-rules.md).

## Error Handling

See [error-handling-protocol.md](./references/error-handling-protocol.md).

## Examples

See [examples-remote-coordination.md](./references/examples-remote-coordination.md).

## Resources

See [References](#references) above.
