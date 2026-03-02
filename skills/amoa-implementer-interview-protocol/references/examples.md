# Interview Protocol Examples

## Table of Contents

- [Example 1: Send Pre-Task Interview Questions](#example-1-send-pre-task-interview-questions)
- [Example 2: Escalate Design Concern to Architect](#example-2-escalate-design-concern-to-architect)
- [Example 3: Send PROCEED After Satisfactory Interview](#example-3-send-proceed-after-satisfactory-interview)
- [Example 4: Send Post-Task Verification Questions](#example-4-send-post-task-verification-questions)
- [Example 5: Send APPROVED and Handoff to Integrator](#example-5-send-approved-and-handoff-to-integrator)

## Example 1: Send Pre-Task Interview Questions

Send a pre-task interview message using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Pre-Task Interview: #42"
- **Content**: Pre-task interview questions covering: task summary, acceptance criteria, concerns, approach, and blockers. Include instruction "Reply with answers. Do NOT start until I confirm PROCEED."
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `issue_number` (42)

**Verify**: confirm message delivery and wait for interview response.

## Example 2: Escalate Design Concern to Architect

When the implementer reports a design issue (e.g., "API design uses synchronous calls, but requirement needs real-time updates"), send an escalation using the `agent-messaging` skill:
- **Recipient**: `architect`
- **Subject**: "Design Review Required: #42"
- **Content**: "Implementer identified design issue for task #42. Issue: [description]. Please review and advise on design modification."
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `task_id`, `implementer`, `concern`, `design_doc`

**Verify**: confirm message delivery.

## Example 3: Send PROCEED After Satisfactory Interview

Send a PROCEED approval using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "PROCEED: #42"
- **Content**: "Your understanding is confirmed. You may begin implementation. Reminders: Follow design document, respect immutable requirements, report blockers immediately, report completion when done (do NOT create PR yet)."
- **Type**: `approval`
- **Priority**: `normal`

**Verify**: confirm message delivery.

## Example 4: Send Post-Task Verification Questions

Send post-task verification questions using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "Post-Task Interview: #42"
- **Content**: Post-task interview questions covering: requirements checklist (each requirement confirmed), testing evidence, code quality, documentation, self-review. Include instruction "Reply with evidence."
- **Type**: `request`
- **Priority**: `high`

**Verify**: confirm message delivery and wait for verification response.

## Example 5: Send APPROVED and Handoff to Integrator

**Step 1**: Send APPROVED message to implementer using the `agent-messaging` skill:
- **Recipient**: `implementer-1`
- **Subject**: "APPROVED: #42"
- **Content**: "Verification complete. Create PR now. PR Requirements: Title format, link to #42, include test evidence. Report PR number when created."
- **Type**: `approval`
- **Priority**: `normal`

**Step 2**: After implementer reports PR #123 created, update issue status:
```bash
gh issue edit 42 --remove-label "status:in-progress" --add-label "status:ai-review"
```

**Step 3**: Notify Integrator using the `agent-messaging` skill:
- **Recipient**: `integrator`
- **Subject**: "PR Ready for Review: #123"
- **Content**: "PR #123 is ready for review. Task: #42. Pre-verified by orchestrator."
- **Type**: `request`
- **Priority**: `high`
- **Data**: include `pr_number` (123), `issue_number` (42), `implementer`, `verification_status` ("pre-verified")

**Verify**: confirm all messages delivered.
