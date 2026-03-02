# Operation: Respond to Bug Report


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Response Workflow](#response-workflow)
  - [Phase 1: Acknowledgment (Within 24 hours)](#phase-1-acknowledgment-within-24-hours)
  - [Phase 2: Reproduction Attempt](#phase-2-reproduction-attempt)
  - [Phase 3: Status Update](#phase-3-status-update)
  - [Phase 4: Resolution Communication](#phase-4-resolution-communication)
- [Steps](#steps)
- [Response Tone Guidelines](#response-tone-guidelines)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-respond-bug-report` |
| Procedure | `proc-handle-feedback` |
| Workflow Step | Step 15 |
| Trigger | Bug report received via GitHub Issue |
| Actor | Orchestrator (EOA) or any assigned agent |
| Target | Bug reporter (human or external) |

---

## Purpose

Respond professionally to bug reports with acknowledgment, reproduction status, and next steps. Good bug response builds trust with users and contributors.

---

## Prerequisites

- Bug report submitted as GitHub Issue
- Access to the codebase to attempt reproduction
- Understanding of the reported behavior

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `issue_number` | Yes | GitHub Issue number |
| `reporter` | Yes | Who submitted the bug |
| `bug_description` | Yes | What the reporter describes |
| `reproduction_steps` | Optional | Steps to reproduce (if provided) |
| `environment_info` | Optional | OS, version, etc. |

---

## Response Workflow

### Phase 1: Acknowledgment (Within 24 hours)

Post initial acknowledgment immediately:

```markdown
Thanks for reporting this, @<reporter>!

I'm looking into this issue. A few questions to help me reproduce:

1. <specific_question_about_environment>
2. <specific_question_about_steps>

I'll update this issue once I can confirm the behavior.
```

### Phase 2: Reproduction Attempt

Try to reproduce the bug:

1. Follow reported steps exactly
2. Try in same environment if specified
3. Document what you observe
4. Note any differences from reported behavior

### Phase 3: Status Update

Based on reproduction result:

**If Reproduced**:
```markdown
I can confirm this issue. Here's what I observed:

<your_observation>

This appears to be caused by <initial_hypothesis>.

I'm marking this as `confirmed` and will work on a fix.
```

**If Cannot Reproduce**:
```markdown
I wasn't able to reproduce this yet. Here's what I tried:

- Environment: <your_environment>
- Steps: <steps_followed>
- Result: <what_you_saw>

Could you provide:
1. <specific_additional_info_needed>
2. <any_logs_or_screenshots>

This will help me narrow down the issue.
```

**If More Info Needed**:
```markdown
Thanks for the report! To investigate this, I need a bit more information:

1. <question_1>
2. <question_2>

Once I have these details, I can dig deeper into what's happening.
```

### Phase 4: Resolution Communication

When fix is ready:

```markdown
This has been fixed in PR #<pr_number>.

**What was the issue**: <brief_explanation>

**How it was fixed**: <brief_fix_description>

The fix will be available in version <version> (or: is now deployed).

Thanks again for reporting this - it helped improve the project!
```

---

## Steps

1. **Post acknowledgment** within 24 hours

2. **Label the issue**:
   - `type:bug`
   - `status:backlog` initially
   - Update to `status:confirmed` or `status:blocked`

3. **Attempt reproduction** with documented steps

4. **Update issue** with reproduction status

5. **If confirmed**, add to backlog or assign for fix

6. **Communicate resolution** when fixed

---

## Response Tone Guidelines

| Aspect | Good | Bad |
|--------|------|-----|
| Acknowledgment | "Thanks for reporting this!" | "We already know about this" |
| Clarification | "Could you provide...?" | "You didn't give enough info" |
| Timeline | "I'll look into this soon" | "This will be fixed tomorrow" |
| Closing | "This helped improve the project!" | No acknowledgment |

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Acknowledgment posted | GitHub comment | Initial response |
| Issue labeled | GitHub labels | type:bug + status label |
| Reproduction status | confirmed / cannot-reproduce / blocked | Investigation result |
| Resolution comment | GitHub comment | When fix is available |

---

## Success Criteria

- Reporter acknowledged within 24 hours
- Appropriate labels applied
- Clear communication of status and next steps
- Reporter feels heard and valued
- No specific date promises made

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| No response after 48h | Reporter inactive | Follow up once, then mark as blocked |
| Duplicate bug | Already reported | Link to original, close as duplicate |
| Not a bug | Feature works as designed | Explain behavior, offer documentation |
| Stale issue | No activity for 30+ days | Post update, close if no response |

---

## Important Rules

1. **Never blame the user** for the bug or poor reporting
2. **Never promise specific dates** for fixes
3. **Always thank** for the report
4. **Ask one question at a time** to avoid overwhelming
5. **Explain WHY** you need additional information

---

## Next Operations

- Bug confirmed → Create implementation task
- Bug is duplicate → Link and close
- Not a bug → Close with explanation
- Fix merged → Post resolution comment
