## Table of Contents
- [Pre-Task Interview Checklist](#pre-task-interview-checklist)
- [Post-Task Interview Checklist](#post-task-interview-checklist)
- [Pre-Task Interview Steps](#pre-task-interview-steps)
- [Post-Task Interview Steps](#post-task-interview-steps)

---

## Pre-Task Interview Checklist

- [ ] Send task assignment message via AI Maestro using the `agent-messaging` skill
- [ ] Wait for implementer ACK (acknowledgment)
- [ ] Send pre-task interview questions using the `agent-messaging` skill
- [ ] Evaluate implementer's understanding summary
- [ ] Check for concerns (requirements, design, capability, dependencies)
- [ ] Escalate design concerns to Architect (AMAA) if needed
- [ ] Escalate immutable requirement concerns to Manager (AMAMA) if needed
- [ ] Resolve blockers before proceeding
- [ ] Send PROCEED message after satisfactory answers
- [ ] Log interview results in handoff document

## Post-Task Interview Checklist

- [ ] Receive implementer's completion report [DONE]
- [ ] Send post-task verification questions
- [ ] Verify ALL requirements checklist items completed
- [ ] Verify test evidence (tests written and passing)
- [ ] Check code quality (linting, formatting, no TODOs)
- [ ] Check documentation updates (if required)
- [ ] Evaluate self-review responses
- [ ] Send APPROVED or REVISE message
- [ ] Wait for PR creation and PR number report
- [ ] Notify Integrator (AMIA) that PR is ready for review
- [ ] Update issue status to `status:ai-review`

---

## Pre-Task Interview Steps

1. Send task assignment message via AI Maestro using the `agent-messaging` skill
2. Wait for implementer ACK (acknowledgment)
3. Send pre-task interview questions using the `agent-messaging` skill ([interview-templates.md](./interview-templates.md))
<!-- TOC: Pre-Task Interview Questions | Pre-Task Interview: {TASK_ID} | Post-Task Interview Questions -->
4. Evaluate implementer's understanding summary
5. Check for concerns about requirements, design, capability, or dependencies
6. If design concerns exist, escalate to Architect (AMAA) ([escalation-messages.md](./escalation-messages.md))
7. If immutable requirement concerns exist, escalate to Manager (AMAMA) → User
8. If blockers are identified, resolve before proceeding
9. Send PROCEED message only after satisfactory answers
10. Log interview results in handoff document

## Post-Task Interview Steps

1. Receive implementer's completion report `[DONE]`
2. Send post-task verification questions ([interview-templates.md](./interview-templates.md))
<!-- TOC: Pre-Task Interview Questions | Pre-Task Interview: {TASK_ID} | Post-Task Interview Questions -->
3. Verify ALL requirements checklist items completed
4. Verify test evidence (tests written and passing)
5. Check code quality (linting, formatting, no TODOs)
6. Check documentation updates (if required)
7. Evaluate self-review responses
8. If verification passes, send APPROVED message ([escalation-messages.md](./escalation-messages.md))
9. If verification fails, send REVISE message with specific issues
10. Wait for PR creation and PR number report
11. Notify Integrator (AMIA) that PR is ready for review
12. Update issue status to `status:ai-review`
