# Progress Polling Protocol Reference

This document describes the MANDATORY Proactive Progress Polling Protocol for monitoring active agents during implementation.

---

## Contents

- 2.1 Why Proactive Polling is Mandatory
- 2.2 The 6 Mandatory Questions
- 2.3 Polling Frequency Rules
  - 2.3.1 Standard polling (10-15 min)
  - 2.3.2 Blocked agent polling (5 min)
  - 2.3.3 Near-completion polling
- 2.4 Poll Message Template
- 2.5 Response Action Matrix
- 2.6 Tracking Poll History
- 2.7 Handling Non-Responsive Agents
- 2.8 Escalation Procedures

---

## 2.1 Why Proactive Polling is Mandatory

**The Problem**: Remote agents may encounter issues but not report them proactively. Common scenarios:

| Scenario | Agent Behavior | Result Without Polling |
|----------|----------------|------------------------|
| Technical blocker | Struggles silently | Hours wasted on unsolvable problem |
| Unclear requirement | Makes assumptions | Incorrect implementation |
| Unexpected complexity | Continues anyway | Delayed delivery, buggy code |
| Missing information | Waits passively | Complete stall |

**The Solution**: The orchestrator MUST actively ask about issues. Never assume "no news is good news."

**Key Principle**: Agents report progress when asked, but may not report blockers unless explicitly questioned.

---

## 2.2 The 6 Mandatory Questions

**EVERY progress poll MUST include these 6 questions. No exceptions.**

### Question 1: Current Progress
"What is your current progress? (percentage complete, what specific items are done)"

**Purpose**: Establish baseline, detect stalls.

### Question 2: Next Steps
"What are you working on right now?"

**Purpose**: Verify agent is on the right track.

### Question 3: Issues or Problems
"Are there any issues or problems? (technical issues, environmental problems, dependency issues)"

**Purpose**: Surface technical blockers.

### Question 4: Clarity Check
"Is anything unclear? (requirements, acceptance criteria, expected behavior)"

**Purpose**: Surface requirement ambiguities.

### Question 5: Unforeseen Difficulties
"Any unforeseen difficulties? (complexity higher than expected, missing information)"

**Purpose**: Surface scope creep or estimation issues.

### Question 6: Needs Assessment
"Do you need anything from me? (documentation, clarification, decisions, resources)"

**Purpose**: Identify how orchestrator can help.

---

## 2.3 Polling Frequency Rules

### 2.3.1 Standard Polling (10-15 minutes)

**When**: Agent is working normally, no known issues.

**Frequency**: Every 10-15 minutes.

**Why 10-15 minutes?**
- Short enough to catch issues early
- Long enough to let agent make progress
- Allows for meaningful status updates

### 2.3.2 Blocked Agent Polling (5 minutes)

**When**: Agent has reported a blocker or issue.

**Frequency**: Every 5 minutes until resolved.

**Actions During Blocked State**:
1. Provide immediate assistance
2. Research solutions
3. Consider reassignment if unresolvable
4. Update estimated completion time

### 2.3.3 Near-Completion Polling (5-10 minutes)

**When**: Agent reports 80%+ completion.

**Frequency**: Every 5-10 minutes.

**Why**: Final stretch often reveals integration issues, edge cases.

---

## 2.4 Poll Message Template

### AI Agent Poll Message (via AI Maestro)

```markdown
Subject: [POLL] Module: {module_name} - Progress Check #{poll_number}

## Status Request

Please provide your current status:

1. **Current progress**: What percentage complete? What specific items are done?
2. **Next steps**: What are you working on right now?

## MANDATORY Questions (Answer ALL)

3. **Are there any issues or problems?**
   - Technical issues (code not working, tests failing)
   - Environmental problems (dependencies, configuration)
   - Dependency issues (waiting on other modules)

4. **Is anything unclear?**
   - Requirements ambiguity
   - Acceptance criteria questions
   - Expected behavior uncertainty

5. **Any unforeseen difficulties?**
   - Complexity higher than expected
   - Missing information discovered
   - Approach not working as planned

6. **Do you need anything from me?**
   - Documentation needed
   - Clarification required
   - Decision needed from orchestrator/user
   - Resources or access required

---

If all is clear with no blockers, reply:
"Progress: {X}%. No blockers. Proceeding as planned."

Expected response time: 5 minutes
Task UUID: {task_uuid}
```

### Human Developer Poll (via GitHub Comment)

```markdown
## Progress Check #{poll_number}

Hi @{github_username}, checking in on module `{module_name}`.

Please update:
- [ ] Current progress (% complete)
- [ ] What's done, what's remaining
- [ ] Any blockers or issues?
- [ ] Anything unclear?
- [ ] Need any help?

Thanks!
```

---

## 2.5 Response Action Matrix

### Issue: Technical Problem

**Agent says**: "Tests are failing, I can't figure out why"

**Orchestrator actions**:
1. Ask for error details
2. Research the issue yourself
3. Provide specific debugging steps
4. If complex: assign a research task to another agent
5. Update: "I'm looking into this, will respond in 5 minutes"

### Issue: Unclear Requirement

**Agent says**: "I'm not sure how error messages should be formatted"

**Orchestrator actions**:
1. Provide immediate clarification
2. Update the original requirements document
3. Confirm agent's understanding of clarification

### Issue: Unexpected Complexity

**Agent says**: "This is more complex than expected, might take longer"

**Orchestrator actions**:
1. Assess the scope increase
2. Options:
   - Accept extended timeline
   - Split into smaller modules
   - Simplify requirements
   - Reassign to more experienced agent
3. Communicate decision clearly

### Issue: Needs Documentation

**Agent says**: "I need the API specification for the user service"

**Orchestrator actions**:
1. Provide documentation immediately if available
2. If not available: create it or assign someone to create it
3. Don't let agent wait - this is highest priority

### Issue: Needs Decision

**Agent says**: "Should we support both OAuth 2.0 and OIDC?"

**Orchestrator actions**:
1. If within orchestrator authority: make decision immediately
2. If needs user input: escalate to user, inform agent of expected wait
3. Provide interim guidance if possible

### Issue: Completely Blocked

**Agent says**: "I'm completely stuck, can't proceed"

**Orchestrator actions**:
1. This is HIGHEST PRIORITY
2. Drop other tasks to unblock
3. Options:
   - Provide solution
   - Pair with agent to solve together
   - Reassign module
   - Escalate to user
4. Never leave an agent blocked for more than 15 minutes

---

## 2.6 Tracking Poll History

### State File Structure

```yaml
progress_polling:
  last_poll: "2026-01-08T16:30:00+00:00"
  poll_count: 3
  next_poll_due: "2026-01-08T16:45:00+00:00"
  current_frequency: "15min"  # or "5min" for blocked
  poll_history:
    - poll_number: 1
      timestamp: "2026-01-08T16:00:00+00:00"
      progress_reported: "30%"
      issues_reported: false
      response_time_seconds: 180
    - poll_number: 2
      timestamp: "2026-01-08T16:15:00+00:00"
      progress_reported: "45%"
      issues_reported: true
      issue_type: "unclear_requirement"
      issue_description: "Unclear token expiry handling"
      issue_resolved: true
      resolution: "Provided clarification"
      response_time_seconds: 120
    - poll_number: 3
      timestamp: "2026-01-08T16:30:00+00:00"
      progress_reported: "60%"
      issues_reported: false
      response_time_seconds: 90
```

### Metrics to Track

| Metric | Purpose |
|--------|---------|
| Average response time | Detect unresponsive agents |
| Issues per module | Identify unclear requirements |
| Time blocked | Measure orchestrator effectiveness |
| Progress velocity | Predict completion |

---

## 2.7 Handling Non-Responsive Agents

### Escalation Timeline

| Time Without Response | Action |
|----------------------|--------|
| 5 minutes | Send reminder |
| 10 minutes | Send urgent follow-up |
| 15 minutes | Try alternative communication |
| 20 minutes | Mark agent as unresponsive |
| 30 minutes | Consider reassignment |

### Reminder Message

```markdown
Subject: [URGENT] No response to progress poll

I sent a progress poll 10 minutes ago and haven't received a response.

Please respond immediately with your status, or if you're blocked, let me know.

If I don't hear back in 5 minutes, I will need to consider reassigning the module.
```

### Alternative Communication

For AI agents:
- Check if AI Maestro session is still active
- Try a different message format
- Check for API errors

For human developers:
- Tag in GitHub issue
- Send email if available
- Slack message if available

---

## 2.8 Escalation Procedures

### When to Escalate to User

1. Agent blocked for >30 minutes with no resolution in sight
2. Scope creep requires product decision
3. Agent unresponsive for >30 minutes
4. Technical issue beyond orchestrator knowledge
5. Resource constraints (need more agents)

### Escalation Message Format

```markdown
## Escalation Required

**Module**: auth-core
**Agent**: implementer-1
**Issue**: Agent blocked on OAuth callback URL format decision

**Context**: Agent needs to know if we're supporting multiple callback URLs or just one. This affects the database schema and token validation logic.

**Options**:
1. Single callback URL (simpler, limited)
2. Multiple callback URLs (complex, flexible)

**My Recommendation**: Option 2 for flexibility

**Action Needed**: Please decide so I can unblock the agent.
```

---

## Summary

The Progress Polling Protocol ensures:

1. **Issues surface early** - Don't wait for agents to report
2. **No agent left blocked** - Immediate response to problems
3. **Accurate progress tracking** - Know true status at all times
4. **Proactive support** - Help agents before they ask

**Key rules**:
- Poll every 10-15 minutes (5 min if blocked)
- Always ask ALL 6 questions
- Respond to issues within 5 minutes
- Never assume silence means progress
