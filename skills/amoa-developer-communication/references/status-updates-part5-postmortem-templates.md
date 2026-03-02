# Status Updates - Part 5: Post-Mortem Communication and Templates

## Contents
- 5.5 Post-mortem communication
  - 5.5.1 Blameless retrospective format
  - 5.5.2 What we learned
  - 5.5.3 Action items and owners
- Templates Quick Reference

---

## 5.5 Post-Mortem Communication

When things go wrong, communicate what happened and what you learned. Blame-free.

### 5.5.1 Blameless Retrospective Format

Focus on systems and processes, not people. Humans make mistakes; systems either catch them or don't.

**Template**:
```
# Post-Mortem: [Incident Title]
**Date**: [Date of incident]
**Duration**: [How long it lasted]
**Impact**: [What was affected, how many users]
**Authors**: [Who wrote this post-mortem]

## Summary
[1-2 sentences: What happened and how we resolved it]

## Timeline
[Chronological events, in UTC]

## Root Cause
[Technical explanation without blame]

## Contributing Factors
[What made this worse or allowed it to happen]

## What Went Well
[Things that worked in our response]

## What Could Have Gone Better
[Opportunities for improvement]

## Action Items
[Specific follow-ups with owners and due dates]
```

### 5.5.2 What We Learned

Extract lessons that apply beyond this specific incident.

**Categories of learning**:
- **Detection**: How could we have caught this sooner?
- **Prevention**: How could we have prevented this?
- **Response**: How could we have responded better?
- **Recovery**: How could we have recovered faster?

**Example**:
```
## What We Learned

### Detection
We didn't know about this until users reported it (2 hours after it started).
**Learning**: We need alerting on authentication failure rates.

### Prevention
The bug was introduced in PR #456 two weeks ago and passed review.
**Learning**: Auth-related changes need security-focused review.

### Response
The on-call engineer wasn't familiar with the auth service.
**Learning**: Need runbooks for critical services.

### Recovery
Rollback took 45 minutes because we weren't sure which commit was safe.
**Learning**: Tag known-good releases; maintain rollback playbook.
```

### 5.5.3 Action Items and Owners

Every post-mortem needs concrete follow-ups. No action items = learning lost.

**Template for action items**:
```
## Action Items

| Priority | Action | Owner | Due Date | Status |
|----------|--------|-------|----------|--------|
| P1 | Add auth failure rate alerting | @sre-team | Next sprint | Not started |
| P1 | Create auth service runbook | @auth-lead | 2024-02-15 | In progress |
| P2 | Security review process for auth PRs | @security | 2024-02-28 | Not started |
| P2 | Tag releases with stability indicators | @devops | 2024-03-01 | Not started |
```

**Good action items are**:
- **Specific**: Not "improve monitoring" but "add alert for auth failure rate >5%"
- **Owned**: Single owner, not "the team"
- **Time-bound**: Due date, not "soon"
- **Tracked**: Review status in follow-up meetings

---

## Templates Quick Reference

### Daily/Weekly Progress Update
```markdown
## Progress Update - [Date]

### Completed
- [Deliverable 1] (PR #X)
- [Deliverable 2] (PR #Y)

### In Progress
- [Task 1] - ETA: [Day]
- [Task 2] - ETA: [Day]

### Blockers
- [Blocker]: Need [action] from [person]

### Notes
[Any context, risks, or FYIs]
```

### Blocker Communication
```markdown
## Blocker: [Title]

**Impact**: [What's blocked]
**Urgency**: [When this becomes critical]

**Details**:
- Trying to: [goal]
- Getting: [error/issue]

**Tried**:
1. [Attempt] - [Result]

**Need**:
- [Specific action] from [person/team]
```

### Completion Notification
```markdown
## [Feature] Complete - Ready for Review

**PR**: #[number]
**Summary**: [What it does]

**Changes**:
- [Change 1]
- [Change 2]

**Testing**: [What was tested]

**Review focus**: [Where to look carefully]
```

### Delay Notification
```markdown
## Timeline Update: [Feature]

**Original ETA**: [Date]
**New ETA**: [Date range]

**Reason**: [What happened]

**Options**:
1. [Accept delay]
2. [Cut scope]
3. [Add resources]

**Recommendation**: [Your suggestion]
```

---

**Previous**: [Part 4: Completion Notification](status-updates-part4-completion-notification.md)
**Back to Index**: [Status Updates Guide](status-updates.md)
