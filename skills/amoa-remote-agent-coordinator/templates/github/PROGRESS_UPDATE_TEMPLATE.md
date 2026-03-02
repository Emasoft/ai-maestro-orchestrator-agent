---
name: progress-update-template
description: Template for progress updates from agents with sections for status, blockers, and next steps
---

# Progress Update Template

> **TODO**: This is a stub template. Expand with specific progress reporting patterns and examples based on actual usage.

## Update Summary

### Task Reference
- **Task ID**: `TASK-{ID}`
- **Issue**: #{issue_number}
- **Agent**: {agent_session_name}
- **Timestamp**: {YYYY-MM-DD HH:MM}

### Current Status
- [ ] On Track
- [ ] At Risk
- [ ] Blocked
- [ ] Completed

### Progress Percentage
{0-100}%

---

## Status Details

### Work Completed
1. {First completed item}
2. {Second completed item}
3. {Third completed item}

### Current Focus
{What is being worked on right now}

### Time Spent
{Hours/effort spent since last update}

---

## Blockers

### Active Blockers
| Blocker | Impact | Mitigation | Owner |
|---------|--------|------------|-------|
| {description} | {High/Medium/Low} | {proposed solution} | {who can resolve} |

### Resolved Blockers
| Blocker | Resolution | Date |
|---------|------------|------|
| {description} | {how it was resolved} | {date} |

### Risks Identified
- **Risk**: {description}
  - **Likelihood**: {High/Medium/Low}
  - **Impact**: {High/Medium/Low}
  - **Mitigation**: {proposed action}

---

## Next Steps

### Immediate Actions
1. {Next immediate task}
2. {Following task}
3. {Subsequent task}

### Estimated Completion
{Date or timeframe for task completion}

### Help Needed
- [ ] Code review requested
- [ ] Technical guidance needed
- [ ] Dependency resolution required
- [ ] Additional context needed
- [ ] None

### Questions for Orchestrator
1. {Question if any}

---

## Artifacts

### Code Changes
- Branch: `{branch_name}`
- Commits: {number of commits}
- Files changed: {count}

### Pull Requests
- PR #{pr_number}: {status}

### Documentation Updates
- {List any documentation changes}

### Test Results
- Tests passed: {count}
- Tests failed: {count}
- Coverage: {percentage}%

---

## Communication Log

### Messages Sent
| To | Subject | Timestamp |
|----|---------|-----------|
| {recipient} | {subject} | {timestamp} |

### Messages Received
| From | Subject | Timestamp |
|------|---------|-----------|
| {sender} | {subject} | {timestamp} |
