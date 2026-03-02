# Operation: Respond to Feature Request


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Response Workflow](#response-workflow)
  - [Phase 1: Acknowledgment and Validation](#phase-1-acknowledgment-and-validation)
  - [Phase 2: Assessment](#phase-2-assessment)
  - [Phase 3: Response Based on Assessment](#phase-3-response-based-on-assessment)
- [Steps](#steps)
- [Response Tone Guidelines](#response-tone-guidelines)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [Decision Matrix](#decision-matrix)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-respond-feature-request` |
| Procedure | `proc-handle-feedback` |
| Workflow Step | Step 15 |
| Trigger | Feature request received via GitHub Issue |
| Actor | Orchestrator (EOA) |
| Target | Feature requester (human or external) |

---

## Purpose

Respond to feature requests with appreciation, scope assessment, and clear expectation setting. Feature requests are valuable input even when they cannot be implemented immediately.

---

## Prerequisites

- Feature request submitted as GitHub Issue
- Understanding of project scope and roadmap
- Authority to accept/defer/decline requests (or escalation path)

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `issue_number` | Yes | GitHub Issue number |
| `requester` | Yes | Who submitted the request |
| `feature_description` | Yes | What they're requesting |
| `use_case` | Optional | Why they need it |
| `current_workaround` | Optional | How they handle it now |

---

## Response Workflow

### Phase 1: Acknowledgment and Validation

Always acknowledge first:

```markdown
Thanks for the suggestion, @<requester>!

<validation_of_the_idea>

To help me understand the use case better:
1. <clarifying_question_about_use_case>

This helps us evaluate how it fits with the project direction.
```

### Phase 2: Assessment

Evaluate the request against:

| Criterion | Question |
|-----------|----------|
| Alignment | Does this fit the project's purpose? |
| Scope | How much effort would this require? |
| Priority | How many users would benefit? |
| Dependencies | Does this require other features first? |
| Alternatives | Can this be achieved differently? |

### Phase 3: Response Based on Assessment

**If Accepting for Roadmap**:
```markdown
Great idea! This aligns with where we're heading.

I've added this to our backlog with the label `enhancement`. While I can't give a specific timeline, here's the current plan:

- **Priority**: <high/medium/low>
- **Depends on**: <any_dependencies>

You can track progress on this issue. Feel free to add any additional context.
```

**If Deferring**:
```markdown
Thanks for this suggestion! It's an interesting idea.

Right now, we're focused on <current_priorities>, so this won't be in the immediate roadmap. However, I'm keeping this issue open for future consideration.

In the meantime, <possible_workaround_or_alternative>.

If the use case becomes more pressing, feel free to add more context here.
```

**If Declining**:
```markdown
Thanks for taking the time to suggest this!

After consideration, this doesn't fit with the current project direction because <reason>.

<possible_alternative_or_related_project>

I'm closing this issue, but feel free to continue the discussion if there's additional context that might change this assessment.
```

**If Needs User Decision**:
```markdown
Thanks for the suggestion, @<requester>!

This is an interesting feature that could add value. I'm flagging this for the project maintainer to review.

@<maintainer> - please review this feature request when you have a chance.

I'll update this issue once we have a decision.
```

---

## Steps

1. **Post acknowledgment** within 48 hours

2. **Label the issue**:
   - `type:enhancement`
   - `status:backlog` initially
   - Update based on decision

3. **Assess against criteria** listed above

4. **Make or request decision**:
   - Within scope authority → decide
   - Outside scope → escalate to maintainer/user

5. **Communicate decision** with reasoning

6. **Update labels** to reflect status:
   - `status:accepted` + priority label
   - `status:deferred`
   - Close if declined

---

## Response Tone Guidelines

| Aspect | Good | Bad |
|--------|------|-----|
| Initial response | "Thanks for the suggestion!" | "This has been asked before" |
| Declining | "This doesn't fit current direction" | "This is out of scope" |
| Deferring | "We'll keep this open for future" | "Maybe someday" |
| Alternatives | "In the meantime, you could..." | No alternative offered |

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Acknowledgment posted | GitHub comment | Initial response |
| Issue labeled | GitHub labels | type:enhancement + status |
| Decision communicated | GitHub comment | Accept/defer/decline |
| Escalation (if needed) | User notification | Maintainer review request |

---

## Success Criteria

- Requester acknowledged within 48 hours
- Request validated (they feel heard)
- Clear decision communicated with reasoning
- No false promises about timelines
- Alternative provided if declining

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Duplicate request | Feature already requested | Link to existing issue |
| Vague request | Not enough detail | Ask clarifying questions |
| Out of scope | Not project's domain | Suggest alternative tools/projects |
| Maintainer unresponsive | Escalation stuck | Follow up after 1 week |

---

## Important Rules

1. **Never dismiss** the request without explanation
2. **Never promise specific timelines** for features
3. **Always thank** for the contribution
4. **Provide alternatives** when declining
5. **Keep issues open** if there's any chance of future implementation

---

## Decision Matrix

| Alignment | Effort | Priority | Decision |
|-----------|--------|----------|----------|
| High | Low | High | Accept |
| High | High | High | Accept, milestone |
| High | Any | Low | Defer |
| Low | Any | Any | Decline |
| Medium | Low | High | Accept |
| Medium | High | Any | Defer |

---

## Next Operations

- Accepted → Create module/task for implementation
- Deferred → No immediate action, keep tracking
- Declined → Close issue with explanation
- Escalated → Wait for maintainer decision
