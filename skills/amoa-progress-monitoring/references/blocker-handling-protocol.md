## Table of Contents

- [Iron Rule for Blockers](#iron-rule-for-blockers)
- [Comprehensive Blocker Definition](#comprehensive-blocker-definition)
- [Blocker Response Protocol](#blocker-response-protocol)
- [Update Labels and Create Blocker Issue](#update-labels-and-create-blocker-issue)
- [When Blocker Resolved](#when-blocker-resolved)
- [Blocker Lifecycle Checklist](#blocker-lifecycle-checklist)

---

## Iron Rule for Blockers

**IRON RULE FOR BLOCKERS**: The user must ALWAYS be informed of blockers immediately. There is NO scenario where a blocker should be "monitored quietly" for hours or days before telling the user. The user may have the solution ready in minutes — but only if they know about the problem.

When an agent reports `[BLOCKED]`, AMOA must verify the blocker is real (agent cannot solve it themselves), then IMMEDIATELY escalate to AMAMA for user notification. There is NO waiting period for user notification — escalation happens as soon as the blocker is confirmed.

## Comprehensive Blocker Definition

A blocker is ANY condition preventing task progress that the assigned agent cannot resolve independently:

| Blocker Category | Examples | Verification |
|------------------|----------|--------------|
| **Task Dependency** | Feature B requires API from Feature A (still in development) | Check if blocking task is complete |
| **Problem Resolution** | Bug must be fixed before feature can be tested | Verify bug status, check if workaround exists |
| **Missing Resource** | Need API key, database access, test environment | Confirm resource is not available via normal channels |
| **Missing Approval** | Design decision, architecture choice, breaking change | Check if approval authority (user/architect) was consulted |
| **External Dependency** | Third-party API down, vendor response needed | Verify external status, check if alternative exists |
| **Access/Credentials** | Repository access, deployment credentials, service permissions | Confirm access cannot be obtained via team processes |

## Blocker Response Protocol

When agent reports `[BLOCKED]`:

1. **Verify** the blocker is real (agent cannot solve it themselves)
2. **Record** the task's current column BEFORE moving to Blocked (for restoration after unblocking)
3. **Move** task to Blocked column and add `status:blocked` label
4. **Remove** the `status:in-progress` (or whatever status it had) label
5. **Comment** on the blocked task issue with blocker details
6. **Create a separate GitHub issue** for the blocker itself (labeled `type:blocker`, referencing the blocked task). This makes the blocking problem visible to all agents and team members on the issue tracker.
7. **Escalate** to AMAMA IMMEDIATELY via AI Maestro blocker-escalation message (see amoa-messaging-templates). Include the blocker issue number.
8. **Continue** monitoring for self-resolution while waiting for user response
9. **Check** if other unblocked tasks can be assigned to the waiting agent

## Update Labels and Create Blocker Issue

```bash
# BEFORE moving to blocked, record current status
CURRENT_STATUS=$(gh issue view $ISSUE --json labels | jq -r '.labels[] | select(.name | startswith("status:")) | .name')

# Mark task as blocked
gh issue edit $ISSUE --remove-label "$CURRENT_STATUS" --add-label "status:blocked"

# Create a GitHub issue for the blocker (the problem preventing progress)
BLOCKER_ISSUE=$(gh issue create --title "BLOCKER: <one-line description of the blocking problem>" --label "type:blocker" \
  --body "## Blocker

This issue tracks a problem that is blocking task #$ISSUE.

**Blocked Task**: #$ISSUE
**Category**: <Task Dependency | Problem Resolution | Missing Resource | Access/Credentials | Missing Approval | External Dependency>
**What's Needed**: <specific action to resolve>
**Impact**: <what work is prevented>
**Previous Status**: $CURRENT_STATUS

## Resolution
Close this issue when the blocking problem is resolved and the blocked task can resume." \
  | grep -oP '\d+$')

# Add blocker details as comment on the blocked task
gh issue comment $ISSUE --body "BLOCKED: <blocker-description>. Previous status: $CURRENT_STATUS. Blocker tracked in #$BLOCKER_ISSUE"
```

## When Blocker Resolved

When a blocker is resolved, the task returns to the COLUMN IT WAS IN BEFORE being blocked (not always "In Progress" — it could have been in Testing, Review, Deploy, etc.).

```bash
# Retrieve previous status from issue comments or metadata
PREVIOUS_STATUS=$(gh issue view $ISSUE --json comments | jq -r '.comments[-1].body' | grep "Previous status:" | awk '{print $3}')

# Close the blocker issue (the issue tracking the blocking problem)
gh issue close $BLOCKER_ISSUE --comment "Resolved: <resolution details>. Blocked task #$ISSUE can now resume."

# Restore previous status on the blocked task
gh issue edit $ISSUE --remove-label "status:blocked" --add-label "$PREVIOUS_STATUS"

# Add resolution comment on the blocked task
gh issue comment $ISSUE --body "Unblocked. Blocker #$BLOCKER_ISSUE resolved. Returning to $PREVIOUS_STATUS."

# Notify agent that blocker is resolved
# (send message via AI Maestro using the agent-messaging skill)
```

## Blocker Lifecycle Checklist

Copy this checklist and track your progress:

**When a task becomes blocked:**
- [ ] Verify the blocker is real (agent cannot solve it themselves)
- [ ] Record the task's current status label (`$CURRENT_STATUS`) before moving to Blocked
- [ ] Remove current `status:*` label from the blocked task
- [ ] Add `status:blocked` label to the blocked task
- [ ] Move task to Blocked column on Kanban board
- [ ] Add blocker details as comment on the blocked task issue (include `Previous status: $CURRENT_STATUS`)
- [ ] Create a separate GitHub issue for the blocker (`type:blocker` label, referencing the blocked task)
- [ ] Send blocker-escalation message to AMAMA via AI Maestro using the `agent-messaging` skill (include `blocker_issue_number`)
- [ ] Check if other unblocked tasks can be assigned to the waiting agent

**When the blocker is resolved:**
- [ ] Verify the blocker is actually resolved (do not assume)
- [ ] Add resolution comment on the blocked task issue
- [ ] Close the blocker issue (`gh issue close $BLOCKER_ISSUE --comment "Resolved: ..."`)
- [ ] Retrieve previous status from the blocker comment on the blocked task
- [ ] Remove `status:blocked` label from the task
- [ ] Restore previous status label (`$PREVIOUS_STATUS`) on the task
- [ ] Move task back to its PREVIOUS column on the Kanban board (not always "In Progress")
- [ ] Notify the assigned agent via AI Maestro that the blocker is resolved
- [ ] Log the resolution in the issue timeline
