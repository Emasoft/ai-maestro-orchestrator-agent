# Workflow Checklists

## Table of Contents (Use-Case Oriented)

- **1.0 When you receive a new task from ECOS/EAMA** → [Checklist: Receiving New Task](#checklist-receiving-new-task)
- **2.0 When you need to delegate a task to a sub-agent** → [Checklist: Delegating Task](#checklist-delegating-task)
- **3.0 When monitoring progress of delegated tasks** → [Checklist: Monitoring Delegated Task](#checklist-monitoring-delegated-task)
- **4.0 When verifying a sub-agent's completed work** → [Checklist: Verifying Task Completion](#checklist-verifying-task-completion)
- **5.0 When reporting results back to ECOS/EAMA** → [Checklist: Reporting Results](#checklist-reporting-results)

---

## Checklist: Receiving New Task

**USE CASE:** When ECOS or EAMA sends you a task

```
- [ ] Receive AI Maestro message
- [ ] Parse message content (extract task description, priority, deadline)
- [ ] Identify task type (implementation/review/fix/research)
- [ ] Log task in docs_dev/orchestration/task-log.md with UUID
- [ ] Assess complexity (simple/moderate/complex)
- [ ] Determine if can handle directly or needs delegation
- [ ] If delegation needed, identify appropriate sub-agent
- [ ] Send ACK to sender confirming receipt
- [ ] Create GitHub issue if task requires tracking
- [ ] Set up status file: docs_dev/orchestration/status/[task-uuid].md
```

**Success Criteria:**
- Task logged with unique UUID
- ACK sent to sender within 5 minutes
- Status file created with initial state
- Delegation decision made (direct vs delegate)

---

## Checklist: Delegating Task

**USE CASE:** When delegating to a sub-agent

```
- [ ] Select sub-agent based on task category and availability
- [ ] Prepare detailed task instructions (use template)
- [ ] Include success criteria in instructions
- [ ] Include deadline and priority
- [ ] Include required artifacts/deliverables
- [ ] Send AI Maestro message to sub-agent using the `agent-messaging` skill
- [ ] Wait for ACK from sub-agent (timeout: 15 minutes)
- [ ] If no ACK, retry once, then escalate to ECOS
- [ ] Log delegation in docs_dev/orchestration/delegation-log.md
- [ ] Create GitHub issue with assigned:[agent-name] label
- [ ] Update task-log.md status to "DELEGATED"
- [ ] Set follow-up reminder based on expected completion time
```

**Success Criteria:**
- Sub-agent ACK received
- GitHub issue created with correct label
- Delegation logged with timestamp
- Follow-up reminder scheduled

---

## Checklist: Monitoring Delegated Task

**USE CASE:** While task is in progress

```
- [ ] Check AI Maestro inbox for progress updates
- [ ] If no update by expected time, send status request
- [ ] Review any interim reports from agent
- [ ] Check GitHub issue for comments/updates
- [ ] If agent reports blockers, assess escalation vs retry
- [ ] Update status file with latest progress
- [ ] If critical path task, poll more frequently
- [ ] If agent overdue >50%, send reminder
- [ ] If agent overdue >100%, escalate to ECOS
```

**Polling Frequency:**
- Normal tasks: Every 2-4 hours
- Critical path: Every 30-60 minutes
- Overdue tasks: Every 15 minutes

**Escalation Triggers:**
- Agent unresponsive for >4 hours
- Agent overdue by 100%+
- Agent reports technical blocker
- Agent requests help/escalation

---

## Checklist: Verifying Task Completion

**USE CASE:** When agent reports completion

```
- [ ] Receive completion report via AI Maestro
- [ ] Verify report has all required sections
- [ ] Check acceptance criteria all met
- [ ] Review test results (if applicable)
- [ ] Verify artifacts/deliverables provided
- [ ] Check GitHub issue status updated
- [ ] Update status file with completion details
- [ ] Update task-log.md status to "COMPLETE"
- [ ] Send ACK to agent confirming completion verified
- [ ] Prepare summary for ECOS/EAMA
```

**Required Report Sections:**
- Summary of work done
- Acceptance criteria verification
- Test results (if applicable)
- Artifacts/deliverables
- Any issues encountered

**Verification Method:**
- All acceptance criteria marked complete
- Test results show passing status
- Deliverables accessible and correct
- GitHub issue has "Done" label

---

## Checklist: Reporting Results

**USE CASE:** When reporting back to ECOS/EAMA

```
- [ ] Prepare 1-2 line summary
- [ ] Include key finding
- [ ] Include link to detailed report file
- [ ] Send AI Maestro message to requester using the `agent-messaging` skill
- [ ] Wait for ACK from requester
- [ ] Update task-log.md status to "REPORTED"
- [ ] Move task files to docs_dev/orchestration/archive/[task-uuid]/
- [ ] Update kanban board (close issue)
- [ ] Clean up temporary files
```

**Report Format:**
```
[1-2 line summary]
Key finding: [one-line summary]
Details: docs_dev/orchestration/reports/[task-uuid].md
```

**Archive Contents:**
- Final status file
- Delegation history
- AI Maestro message transcripts
- Completion reports
- Test results
- Artifacts/deliverables

**Cleanup Actions:**
- Remove temporary files from docs_dev/orchestration/
- Close GitHub issue
- Update task log to "ARCHIVED"
- Confirm archive directory structure correct

---

## Quick Reference: Checklist Selection

| Situation | Use This Checklist |
|-----------|-------------------|
| New message from ECOS/EAMA | [Receiving New Task](#checklist-receiving-new-task) |
| Need to assign work to sub-agent | [Delegating Task](#checklist-delegating-task) |
| Task in progress, checking status | [Monitoring Delegated Task](#checklist-monitoring-delegated-task) |
| Agent says task is done | [Verifying Task Completion](#checklist-verifying-task-completion) |
| Sending results back to requester | [Reporting Results](#checklist-reporting-results) |

---

## Notes

- All checklists should be followed sequentially
- Do NOT skip steps - each has a purpose
- Update logs immediately after each checklist step
- If any step fails, stop and escalate
- Keep audit trail of all checklist completions
