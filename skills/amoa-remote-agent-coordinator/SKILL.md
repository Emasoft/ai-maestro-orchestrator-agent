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
  <!-- TOC: Table of Contents | 0 Overview | 0 Agent Registration Format | 1 Required Fields for Agent Registration | 2 Agent Capabilities List | 3 Availability States | 0 Agent Roster Management | 1 Creating and Maintaining AGENT_ROSTER.md | Active Agents | Offline Agents | 2 Updating Agent Status | 3 Tracking Current Task Assignments | 0 Agent Roster File Template | 1 Full Template | Onboarding Agents | Agent History | Recently Completed Tasks | 0 Integration with Onboarding | 1 Registration After Successful Onboarding | 2 Verification Task Completion Requirement -->
- [echo-acknowledgment-protocol.md](./references/echo-acknowledgment-protocol.md)
  <!-- TOC: Message Types: Instructions vs Conversations | When task acknowledgment is required | If agent receives task normally | If agent has questions about the task | If agent fails to acknowledge in time | If agent encounters resource or capability issues | During long task execution with checkpoints | Proactive enforcement by orchestrator | Message flow reference | Integration with other protocols -->
- [verification-loops-protocol.md](./references/verification-loops-protocol.md)
  <!-- TOC: Table of Contents | 0 Overview | 0 The Verification Flow | 1 Understanding the 5 PR Requests Cycle | 0 Step-by-Step Implementation | 1 Including PR Notification Requirement in Task Assignment | 2 Responding to Agent PR Requests with Verification Messages | 3 Tracking Verification State Per Task | Verification State Tracker | 4 Waiting for Next PR Request After Each Verification Report | 5 Making the Final Decision on the 5th PR Request | 0 Summary: The 5 PR Requests | 0 Enforcement Rules | 1 What the Orchestrator MUST NOT Do | 2 What the Orchestrator MUST Do | 0 Troubleshooting | Problem: Agent Creates PR Without Waiting for Approval | Problem: Agent Claims "No Issues Found" But Issues Exist | Problem: Verification Loop Count Lost | Problem: Agent Skipping Verification Steps | Problem: Endless Loop - Issues Keep Appearing -->
- [progress-monitoring-protocol.md](./references/progress-monitoring-protocol.md)
  <!-- TOC: Table of Contents | 0 Overview | 0 Proactive Monitoring Principles | 0 Status Request Protocol | 1 Checking Agent Status (PROACTIVELY) | 2 Expected Update Events by Task Type | 3 Proactive Status Request Timeline | 0 Proactive Unblocking Protocol | 1 When an Agent Reports Being Blocked | 0 Task Completion Enforcement | 1 Verifying All Acceptance Criteria Are Met | 0 No Update Protocol (Proactive Escalation) | 1 Escalation Timeline When Agent Goes Silent | 0 Message Templates | 1 Status Request Message | 2 Unblocking Assistance Message | 3 Completion Verification Message | 0 Troubleshooting | Problem: Agent Goes Silent During Task | Problem: Agent Reports Progress But No Actual Work | Problem: Agent Keeps Reporting "Almost Done" | Problem: Agent Claims Complete But Acceptance Criteria Not Met | Problem: Proactive Checks Interrupt Agent's Flow | Problem: Multiple Blocked Agents Create Backlog | Problem: Agent Unblocking Attempts Not Working -->
- [error-handling-protocol.md](./references/error-handling-protocol.md)
  <!-- TOC: Table of Contents | 0 Overview | 1 FAIL-FAST Principle | 2 When Agents Must Stop and Report | 0 Error Reporting Format | 1 Error Report Message Schema | 2 Error Types | 0 Orchestrator Response to Errors | 1 Acknowledging Error Reports | 2 Providing Solutions | 3 Escalation When Needed | 0 Troubleshooting | Problem: Agent Not Reporting Errors | Problem: Agent Reports Same Error Repeatedly | Problem: Unclear Error Type | Problem: False Blocker Reports -->
- [escalation-procedures.md](./references/escalation-procedures.md)
  <!-- TOC: Overview | Contents | Escalation Hierarchy | What Remote Agents Handle (Level 0) | What Orchestrator Handles (Level 1) | What Requires User Escalation (Level 2) | Escalation Message Formats | Escalation Categories | Escalation Response Handling | Escalation Queue Management | Do's and Don'ts | Metrics | Decision Trees for Escalation Handling -->
- [messaging-protocol.md](./references/messaging-protocol.md)
  <!-- TOC: IMPORTANT: Official Skill Reference | Overview | Document Structure | Part 1: API and Schema Reference | Part 2: Sending and Receiving Messages | Part 3: Message Types by Category | Part 4: Agents, Errors, and Best Practices | Part 5: Notifications and Response Expectations | Part 6: Timeouts and Protocol Integration | Part 7: Troubleshooting | Quick Reference | Essential Commands | Priority Quick Guide | Required Message Fields | Navigation -->
- [task-instruction-format.md](./references/task-instruction-format.md)
  <!-- TOC: **[Overview](#overview)** - Critical principle: teach agents in every message | **[Agent Response Templates](#agent-response-templates)** - Templates to link in task delegations | **[Mandatory ACK Block](#mandatory-ack-block)** - Include this in EVERY task delegation -->
- [rule-15-no-implementation.md](./references/rule-15-no-implementation.md)
  <!-- TOC: Table of Contents | 0 Overview | 0 What the Orchestrator NEVER Does | 1 Never Write Code | 2 Never Run Builds | 3 Never Edit Source Files | 4 Never Set Up Infrastructure | 0 Task Delegation Self-Check | 1 Pre-Delegation Verification | 2 Self-Check Questions | 0 Correct vs Incorrect Usage | 1 Common Scenarios and Proper Handling | 2 Examples of Violations -->
- [rule-14-immutable-requirements.md](./references/rule-14-immutable-requirements.md)
  <!-- TOC: Table of Contents | 0 Overview | 0 Mandatory Task Delegation Elements | 1 Requirement Reference Section | User Requirements (IMMUTABLE) | 2 Forbidden Actions Block | FORBIDDEN (RULE 14 Violations) | 3 Escalation Protocol Section | If Requirements Have Issues | 0 Task Template Requirements | 1 Updating All Task Delegation Templates | 2 Verification Checklist | 0 Violation Handling | 1 When Remote Agent Reports a Violation | 2 Requirement Issue Report Format | Requirement Issue Report | Issue Description | Agent's Concern | Options | Recommendation | 3 User Decision Workflow -->
- [script-output-rules.md](./references/script-output-rules.md)
  <!-- TOC: Token-Efficient Output Protocol | Output Format | Exceptions -->
- [examples-remote-coordination.md](./references/examples-remote-coordination.md)
  <!-- TOC: 0 Example: Onboard and Assign Task to New Agent | 1 Step-by-step onboarding flow | 2 Task delegation with ACK instructions | 0 Example: 4-Verification Loop Sequence | 1 Complete conversation flow | 2 Loop counter tracking | 0 Example: Progress Monitoring Flow | 1 Proactive polling sequence | 2 Handling no-response scenarios -->

