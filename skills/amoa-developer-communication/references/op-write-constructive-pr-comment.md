# Operation: Write Constructive PR Comment


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Steps](#steps)
- [Comment Templates](#comment-templates)
  - [Blocking Issue (Request Changes)](#blocking-issue-request-changes)
  - [Non-Blocking Suggestion (Comment)](#non-blocking-suggestion-comment)
  - [Praise (Approve with Comment)](#praise-approve-with-comment)
- [Tone Transformations](#tone-transformations)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Pre-Send Checklist](#pre-send-checklist)
- [Error Handling](#error-handling)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-write-constructive-pr-comment` |
| Procedure | `proc-handle-feedback` |
| Workflow Step | Step 15 |
| Trigger | PR requires code review feedback |
| Actor | Orchestrator (EOA) or Integrator (EIA) |
| Target | Human developer or AI agent |

---

## Purpose

Write code review comments on Pull Requests that are constructive, specific, and actionable. Comments should help improve code quality without discouraging the contributor.

---

## Prerequisites

- PR open and ready for review
- Code changes accessible for review
- Understanding of project coding standards
- Knowledge of blocking vs. non-blocking feedback

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `pr_number` | Yes | GitHub PR number |
| `file_path` | Yes | File being commented on |
| `line_number` | Yes | Line or range of lines |
| `issue_type` | Yes | blocking / suggestion / praise |
| `observation` | Yes | What you noticed in the code |
| `reason` | Optional | Why it matters |
| `suggestion` | Optional | Proposed improvement |

---

## Steps

1. **Classify the feedback type**:
   - **Blocking**: Must be fixed before merge (bugs, security, breaking changes)
   - **Suggestion**: Optional improvement (style, optimization, clarity)
   - **Praise**: Recognition of good work (patterns, catches, clarity)

2. **Draft the comment** using the appropriate template

3. **Apply tone guidelines**:
   - Use "we" instead of "you"
   - Ask questions instead of commands
   - Provide context for why it matters
   - Assume good intent

4. **Post the comment** via gh CLI or GitHub API

5. **Track the feedback** for follow-up if blocking

---

## Comment Templates

### Blocking Issue (Request Changes)

```markdown
**[Blocking]** <short_description>

<observation>

This needs to be addressed because <reason>.

<suggested_fix_or_approach>
```

**Example**:
```markdown
**[Blocking]** Potential null pointer exception

This line accesses `user.email` but `user` could be undefined when the session expires.

This needs to be addressed because it will cause a runtime crash in production.

Consider adding a null check:
```javascript
const email = user?.email ?? 'unknown';
```
```

### Non-Blocking Suggestion (Comment)

```markdown
**[Suggestion]** <short_description>

<observation>

<why_it_might_be_better>

Feel free to ignore if there's a reason for the current approach.
```

**Example**:
```markdown
**[Suggestion]** Consider extracting validation logic

Lines 45-67 contain validation that's also used in the signup flow.

Extracting to a `validateUserInput()` function would reduce duplication and make both flows easier to test.

Feel free to ignore if there's a reason for keeping these separate.
```

### Praise (Approve with Comment)

```markdown
Nice work here! <specific_observation>

<why_it_matters>
```

**Example**:
```markdown
Nice work on the edge case handling here! The empty array check at line 42 would have been easy to miss.

This kind of defensive coding prevents subtle bugs in production.
```

---

## Tone Transformations

| Wrong | Right |
|-------|-------|
| "This is wrong" | "This might cause X - what if we tried Y?" |
| "You should do X" | "One option would be X - thoughts?" |
| "You broke the build" | "The build is failing - looks like it's related to X" |
| "This doesn't make sense" | "Help me understand the reasoning behind X?" |
| "Fix this" | "This is blocking deployment - can we prioritize?" |

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Comment posted | GitHub comment URL | Link to the comment |
| Feedback type | blocking / suggestion / praise | Classification |
| Follow-up needed | Yes / No | Whether response expected |

---

## Success Criteria

- Comment is specific (references exact lines and code)
- Tone is respectful and constructive
- Blocking vs. non-blocking is clearly marked
- Reason/context provided for changes requested
- Would feel good receiving this feedback

---

## Pre-Send Checklist

Before posting the comment, verify:

- [ ] Is the tone respectful and professional?
- [ ] Did I assume good intent?
- [ ] Is feedback specific with line references?
- [ ] Is blocking vs. non-blocking clearly marked?
- [ ] Did I explain WHY, not just WHAT?
- [ ] Is there anything to acknowledge or praise?
- [ ] Would I feel good receiving this comment?

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Comment too vague | Missing specifics | Add line numbers and examples |
| Tone perceived as harsh | Missing context | Add reasoning and soften language |
| No response to blocking | Developer missed it | Re-request review, tag developer |

---

## Next Operations

Depending on feedback type:
- Blocking feedback → Wait for response, track resolution
- Suggestion → No action needed unless discussed
- Praise only → Approve PR via `op-approve-pr.md`
