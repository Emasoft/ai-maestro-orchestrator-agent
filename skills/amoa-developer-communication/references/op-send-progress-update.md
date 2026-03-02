# Operation: Send Progress Update


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Update Structure](#update-structure)
  - [Standard Progress Update](#standard-progress-update)
- [Progress Update: <task_or_project>](#progress-update-task_or_project)
  - [Completed](#completed)
  - [In Progress](#in-progress)
  - [Blockers](#blockers)
  - [Next Steps](#next-steps)
  - [ETA](#eta)
  - [Blocker Communication](#blocker-communication)
- [Blocked: <task_name>](#blocked-task_name)
  - [What's blocking us](#whats-blocking-us)
  - [What we've tried](#what-weve-tried)
  - [What we need to unblock](#what-we-need-to-unblock)
  - [Impact if not resolved](#impact-if-not-resolved)
  - [ETA Adjustment](#eta-adjustment)
- [Timeline Update: <task_name>](#timeline-update-task_name)
  - [Why the change](#why-the-change)
  - [What we're doing about it](#what-were-doing-about-it)
  - [Scope options (if relevant)](#scope-options-if-relevant)
- [Steps](#steps)
- [Frequency Guidelines](#frequency-guidelines)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Tone Guidelines](#tone-guidelines)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [ETA Best Practices](#eta-best-practices)
- [Templates by Audience](#templates-by-audience)
  - [For Technical Stakeholders](#for-technical-stakeholders)
- [Dev Update: <feature>](#dev-update-feature)
  - [Changes merged](#changes-merged)
  - [Current work](#current-work)
  - [Technical blockers](#technical-blockers)
  - [Next](#next)
  - [For Non-Technical Stakeholders](#for-non-technical-stakeholders)
- [Progress Update: <feature>](#progress-update-feature)
  - [What's done](#whats-done)
  - [What's next](#whats-next)
  - [Any concerns?](#any-concerns)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-send-progress-update` |
| Procedure | `proc-handle-feedback` |
| Workflow Step | Step 15 |
| Trigger | Scheduled update or stakeholder request |
| Actor | Orchestrator (EOA) or implementing agent |
| Target | Stakeholders (user, team, manager) |

---

## Purpose

Communicate progress on tasks or projects with clear status, blockers, and next steps. Good progress updates reduce anxiety and prevent unnecessary check-ins.

---

## Prerequisites

- Active task or project with ongoing work
- Knowledge of current status
- Understanding of audience (technical vs. non-technical)
- Access to communication channel

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `task_or_project` | Yes | What you're updating about |
| `audience` | Yes | Who will read this (stakeholder type) |
| `accomplishments` | Yes | What was completed |
| `next_steps` | Yes | What's coming next |
| `blockers` | Optional | What's preventing progress |
| `eta_change` | Optional | If timeline shifted |

---

## Update Structure

### Standard Progress Update

```markdown
## Progress Update: <task_or_project>
**Date**: <date>
**Status**: <on_track / at_risk / blocked>

### Completed
- [x] <accomplishment_1>
- [x] <accomplishment_2>

### In Progress
- [ ] <current_work_1>
- [ ] <current_work_2>

### Blockers
<blockers_or_"None">

### Next Steps
<what_happens_next>

### ETA
<current_estimate>
```

### Blocker Communication

When blocked, be specific about what's needed:

```markdown
## Blocked: <task_name>

### What's blocking us
<clear_description_of_blocker>

### What we've tried
1. <attempted_solution_1>
2. <attempted_solution_2>

### What we need to unblock
<specific_request_or_decision_needed>

### Impact if not resolved
<consequence_and_timeline>
```

### ETA Adjustment

When timeline changes:

```markdown
## Timeline Update: <task_name>

**Previous ETA**: <old_estimate>
**New ETA**: <new_estimate>

### Why the change
<honest_explanation>

### What we're doing about it
<mitigation_or_adjustment>

### Scope options (if relevant)
- **Full scope**: <longer_eta>
- **Reduced scope**: <shorter_eta> (would exclude <what>)
```

---

## Steps

1. **Gather status information**:
   - What's been completed since last update
   - What's currently in progress
   - Any blockers or risks
   - ETA assessment

2. **Assess if ETA has changed**:
   - If yes, communicate early (not last minute)
   - Include explanation and options

3. **Format for audience**:
   - Technical audience: Include implementation details
   - Non-technical: Focus on outcomes and impact

4. **Send via appropriate channel**:
   - Scheduled updates: Issue comment or status meeting
   - Blockers: Direct message to decision maker
   - Major changes: Multiple channels

5. **Request action if needed**:
   - Be specific about what you need
   - Include deadline for response

---

## Frequency Guidelines

| Situation | Update Frequency |
|-----------|------------------|
| Normal progress | Weekly or at milestones |
| Blocked | Immediately when blocked |
| At risk | When risk identified |
| ETA change | As soon as known |
| Stakeholder asks | Within 24 hours |

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Progress update | Markdown message | Status report |
| Blocker notification | Urgent message | If blocked |
| ETA adjustment | Markdown message | If timeline changed |
| Action request | Message with deadline | If decision needed |

---

## Success Criteria

- Update is sent proactively (not when asked)
- Accomplishments are concrete (not vague)
- Blockers include what's needed to resolve
- ETA is a range, not a point estimate
- No surprises (bad news delivered early)

---

## Tone Guidelines

| Situation | Tone |
|-----------|------|
| On track | Confident, brief |
| At risk | Transparent, solution-focused |
| Blocked | Urgent, specific about needs |
| ETA slip | Honest, accountable |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| "Working on it" | List specific completed items |
| "Almost done" | Give percentage or remaining tasks |
| "Should be done soon" | Give date range with caveats |
| Blaming others | Focus on facts and what's needed |
| Hiding bad news | Report early with mitigation plan |

---

## Error Handling

| Situation | Response |
|-----------|----------|
| No progress to report | Explain why, focus on blockers |
| Don't know ETA | Say "investigating, will update by X" |
| Stakeholder unhappy | Acknowledge, offer options |
| Repeated slips | Deeper analysis, scope discussion |

---

## Important Rules

1. **Update proactively** - Don't wait to be asked
2. **Be specific** - Vague updates create anxiety
3. **Share bad news early** - Surprises erode trust
4. **Use ranges for ETAs** - Points are always wrong
5. **Include next steps** - End with forward motion

---

## ETA Best Practices

| Practice | Example |
|----------|---------|
| Use ranges | "3-5 days" not "4 days" |
| Include confidence | "High confidence: this week" |
| Note dependencies | "Assuming X is resolved" |
| Update when changed | Don't wait until deadline |

---

## Templates by Audience

### For Technical Stakeholders

```markdown
## Dev Update: <feature>

**Status**: <status>

### Changes merged
- PR #123: Implemented X
- PR #124: Fixed Y

### Current work
- Working on Z (branch: feature/z)

### Technical blockers
- Waiting for API endpoint from team B

### Next
- Complete Z, then integration testing
```

### For Non-Technical Stakeholders

```markdown
## Progress Update: <feature>

**Status**: <status>

### What's done
- Users can now do X
- Performance improved by Y%

### What's next
- Adding ability to Z (expected this week)

### Any concerns?
<blockers_in_plain_language>
```

---

## Next Operations

- Update delivered → Continue work
- Blocker reported → Track resolution
- ETA adjusted → Monitor for further changes
- Action requested → Follow up if no response
