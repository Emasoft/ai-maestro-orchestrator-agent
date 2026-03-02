---
name: eoa-developer-communication
description: "Trigger with developer communication needs. Use when communicating with human developers in code reviews, issues, technical discussions, and status updates. Covers effective communication patterns."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  tags: "communication, code-review, documentation, collaboration"
  audience: AI agents working with human developers
  prerequisites: None
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "Steps 14, 15, 22"
procedure: "proc-clarify-tasks, proc-handle-feedback, proc-handle-failed-pr"
---

# Developer Communication Skill

## Overview

This skill teaches effective communication with **human developers**

## Prerequisites

- Understanding of code review processes
- Access to communication channels (GitHub, Slack, etc.)
- Familiarity with professional communication standards

## Output

| Field | Description | Format |
|-------|-------------|--------|
| Communication Type | The type of developer communication (PR comment, issue response, technical explanation, status update, etc.) | String |
| Tone Assessment | Evaluation of message tone (respectful, specific, constructive) | Pass/Fail with notes |
| Blocking Status | Whether feedback is blocking or non-blocking | "Blocking" or "Non-blocking" |
| Message Content | The actual communication to send | Formatted text (Markdown) |
| References | Links to relevant code, issues, or documentation | List of URLs |

## Instructions

1. **Identify the communication type** - Determine if you are writing a PR comment, issue response, technical explanation, status update, or conflict resolution message.

2. **Understand the human-AI communication differences** - Recognize that human communication differs fundamentally from structured AI-to-AI message templates:

   | Aspect | AI-to-AI Communication | Human Communication |
   |--------|------------------------|---------------------|
   | Format | Structured JSON/templates | Natural language |
   | Tone | Neutral, task-focused | Warm, respectful, contextual |
   | Context | Explicit, complete | Often implicit, requires inference |
   | Feedback | Direct status codes | Nuanced, face-saving |
   | Timing | Immediate processing | Async, variable attention |

3. **Use the decision tree** - Navigate the decision tree below to select the appropriate reference document for your specific communication scenario.

4. **Apply the key principles** - Before drafting your message, review and apply all six key principles listed in the "Key Principles of Developer Communication" section.

5. **Draft your message** - Write your communication following the patterns and templates in the relevant reference document.

6. **Run the pre-send checklist** - Before sending, verify your message against the "Checklist: Before Sending Any Communication" to ensure quality and professionalism.

7. **Send and monitor** - Deliver the message through the appropriate channel and monitor for responses or follow-up needs.

---

## Key Principles of Developer Communication

### 1. Assume Good Intent

Every developer you interact with is trying to do good work. Code that seems "wrong" may reflect constraints, legacy decisions, or knowledge you lack.

**Instead of**: "This approach is wrong"
**Use**: "I noticed this pattern - was there a specific reason for this approach? I was thinking X might work because..."

### 2. Be Specific, Not Vague

Vague feedback wastes time and creates frustration. Always provide concrete examples.

**Instead of**: "This code could be cleaner"
**Use**: "Consider extracting lines 45-52 into a `validateUserInput()` function - it would make the login flow easier to test"

### 3. Separate Blocking from Non-Blocking

Clearly distinguish required changes from suggestions. Use explicit markers.

**Blocking**: "This will cause a null pointer exception when `user` is undefined"
**Non-blocking**: "Nit: Consider using `const` here instead of `let`"

### 4. Acknowledge Good Work

Recognition builds trust and encourages best practices. Point out what's done well.

**Example**: "Nice job handling the edge case for empty arrays here - that would have been easy to miss"

### 5. Provide Context for Your Feedback

Explain *why* something matters, not just *what* to change.

**Instead of**: "Use dependency injection"
**Use**: "Using dependency injection here would let us mock the database in tests, reducing test runtime from 30s to 2s"

---

## Decision Tree: Choosing Communication Type

```
Is this about code you're reviewing?
├── YES → See pr-comment-writing.md
│   ├── Is it a blocking issue? → Request Changes
│   ├── Is it a suggestion? → Comment (non-blocking)
│   └── Is it praise? → Approve with comment
│
└── NO → Is this about an issue/ticket?
    ├── YES → See issue-communication.md
    │   ├── Bug report? → Acknowledge, reproduce, respond
    │   ├── Feature request? → Thank, set expectations
    │   └── Question? → Answer or redirect
    │
    └── NO → Is this explaining technical decisions?
        ├── YES → See technical-explanation.md
        │
        └── NO → Is this a conflict or disagreement?
            ├── YES → See conflict-resolution.md
            │
            └── NO → Is this a progress/status update?
                ├── YES → See status-updates.md
                │
                └── NO → See templates-for-humans.md for general formats
```

---

## Reference Documents

### PR Comment Writing
**File**: [references/pr-comment-writing.md](references/pr-comment-writing.md)

**Use when**: Writing code review comments on Pull Requests

**Contents**:
- 1.1 Writing constructive code review comments
  - 1.1.1 The praise-suggestion-question framework
  - 1.1.2 Balancing thoroughness with developer time
- 1.2 Tone guidelines for professional reviews
  - 1.2.1 Avoiding pedantic or condescending language
  - 1.2.2 Using "we" instead of "you"
- 1.3 When to request changes versus suggest
  - 1.3.1 Blocking issues that require changes
  - 1.3.2 Non-blocking suggestions and nits
  - 1.3.3 Praise-only approvals
- 1.4 Acknowledging good code patterns
- 1.5 Avoiding accusatory language
  - 1.5.1 Why "you" statements feel like attacks
  - 1.5.2 Reframing with "this" and "we"
- 1.6 Examples of good versus bad comments

---

### Issue Communication
**File**: [references/issue-communication.md](references/issue-communication.md)

**Use when**: Responding to bug reports, feature requests, or questions in issue trackers

**Contents**:
- 2.1 Bug report response workflow
  - 2.1.1 Acknowledgment template
  - 2.1.2 Reproduction confirmation
  - 2.1.3 Investigation updates
  - 2.1.4 Resolution communication
- 2.2 Feature request acknowledgment
  - 2.2.1 Thanking and validating the idea
  - 2.2.2 Setting scope expectations
  - 2.2.3 Linking to roadmap or discussions
- 2.3 Asking clarifying questions
  - 2.3.1 One question at a time rule
  - 2.3.2 Providing response options
  - 2.3.3 Explaining why you need the information
- 2.4 Setting expectations on timeline
  - 2.4.1 Never promise specific dates
  - 2.4.2 Using priority and milestone indicators
  - 2.4.3 Managing stale issues
- 2.5 Closing issues gracefully
  - 2.5.1 Duplicate handling
  - 2.5.2 Won't-fix explanations
  - 2.5.3 Inviting future feedback

---

### Technical Explanation
**File**: [references/technical-explanation.md](references/technical-explanation.md)

**Use when**: Explaining architecture, design decisions, or non-obvious code to humans

**Contents**:
- 3.1 Explaining technical decisions
  - 3.1.1 The context-decision-consequences format
  - 3.1.2 Acknowledging tradeoffs honestly
  - 3.1.3 Referencing alternatives considered
- 3.2 Justifying architectural choices
  - 3.2.1 Connecting to requirements
  - 3.2.2 Explaining scalability and maintainability
  - 3.2.3 Addressing security implications
- 3.3 Providing context for non-obvious code
  - 3.3.1 When comments are necessary
  - 3.3.2 Linking to issues or ADRs
  - 3.3.3 Explaining workarounds and technical debt
- 3.4 Linking to relevant documentation
  - 3.4.1 Internal wiki and ADRs
  - 3.4.2 External specifications
  - 3.4.3 Code examples in the codebase
- 3.5 Using code examples effectively
  - 3.5.1 Before/after comparisons
  - 3.5.2 Minimal reproducible examples
  - 3.5.3 Annotated code blocks

---

### Conflict Resolution
**File**: [references/conflict-resolution.md](references/conflict-resolution.md)

**Use when**: Disagreeing with another developer's approach or resolving technical disputes

**Contents**:
- 4.1 Disagreeing professionally
  - 4.1.1 Separating the idea from the person
  - 4.1.2 Starting with understanding
  - 4.1.3 Using "I think" not "You're wrong"
- 4.2 Offering alternatives
  - 4.2.1 The "Yes, and" technique
  - 4.2.2 Presenting options without attachment
  - 4.2.3 Showing concrete examples
- 4.3 Finding compromise
  - 4.3.1 Identifying shared goals
  - 4.3.2 Proposing incremental solutions
  - 4.3.3 Time-boxing experiments
- 4.4 Escalation paths
  - 4.4.1 When to bring in a third party
  - 4.4.2 Technical leads and architects
  - 4.4.3 Documenting the disagreement
- 4.5 When to involve maintainers
  - 4.5.1 Stalled discussions
  - 4.5.2 Blocking PRs
  - 4.5.3 Community conduct issues

---

### Status Updates
**File**: [references/status-updates.md](references/status-updates.md)

**Use when**: Reporting progress, communicating blockers, or providing completion updates

**Contents**:
- 5.1 Progress report format
  - 5.1.1 What was done (concrete deliverables)
  - 5.1.2 What's next (clear next steps)
  - 5.1.3 Blockers (actionable items)
- 5.2 Blocker communication
  - 5.2.1 Describing the blocker clearly
  - 5.2.2 What you've tried
  - 5.2.3 What you need to unblock
- 5.3 ETA setting and adjustment
  - 5.3.1 Ranges not points
  - 5.3.2 Early communication of delays
  - 5.3.3 Explaining scope changes
- 5.4 Completion notification
  - 5.4.1 Summary of changes
  - 5.4.2 Testing performed
  - 5.4.3 What reviewers should focus on
- 5.5 Post-mortem communication
  - 5.5.1 Blameless retrospective format
  - 5.5.2 What we learned
  - 5.5.3 Action items and owners

---

### Templates for Humans
**File**: [references/templates-for-humans.md](references/templates-for-humans.md)

**Use when**: Writing PRs, commits, release notes, or migration guides for human readers

**Contents**:
- 6.1 Pull Request description template
  - 6.1.1 Summary section
  - 6.1.2 Changes section with bullets
  - 6.1.3 Testing section
  - 6.1.4 Screenshots for UI changes
- 6.2 Commit message guidelines
  - 6.2.1 Conventional commits format
  - 6.2.2 Subject line rules
  - 6.2.3 Body content guidelines
- 6.3 Release notes format
  - 6.3.1 User-facing language
  - 6.3.2 Grouping by type
  - 6.3.3 Linking to issues and PRs
- 6.4 Breaking change communication
  - 6.4.1 Warning users in advance
  - 6.4.2 Deprecation notices
  - 6.4.3 Migration timeline
- 6.5 Migration guide structure
  - 6.5.1 Before/after examples
  - 6.5.2 Step-by-step instructions
  - 6.5.3 Common issues and solutions

---

## Quick Reference: Communication Tone

| Situation | Wrong Tone | Right Tone |
|-----------|------------|------------|
| Code issue | "This is wrong" | "This might cause X - what if we tried Y?" |
| Suggestion | "You should do X" | "One option would be X - thoughts?" |
| Bug found | "You broke the build" | "The build is failing - looks like it's related to X" |
| Disagreement | "That won't work" | "I have concerns about X because of Y - how about Z?" |
| Confusion | "This doesn't make sense" | "Help me understand the reasoning behind X?" |
| Urgency | "Fix this now" | "This is blocking deployment - can we prioritize?" |

---

## Checklist: Before Sending Any Communication

Copy this checklist and track your progress:

- [ ] Is the tone respectful and professional?
- [ ] Did I assume good intent?
- [ ] Is feedback specific with examples?
- [ ] Did I separate blocking from non-blocking?
- [ ] Did I explain *why*, not just *what*?
- [ ] Is there anything to acknowledge or praise?
- [ ] Would I feel good receiving this message?

---

## Examples

### Example 1: Constructive Code Review Comment

**Wrong:**
> "This code is inefficient and poorly structured."

**Right:**
> "I noticed this loop processes items sequentially. Consider using `Promise.all()` for parallel execution - it could reduce the response time from ~500ms to ~100ms based on similar patterns elsewhere in the codebase."

### Example 2: Acknowledging Good Work

> "Nice catch on the null check at line 42 - that edge case would have caused issues in production. The error message is also very clear."

---

## Error Handling

| Situation | Issue | Resolution |
|-----------|-------|------------|
| Misunderstood feedback | Developer responds defensively | Clarify intent, acknowledge their perspective |
| Unclear requirements | Developer delivers wrong implementation | Provide concrete examples and success criteria |
| Communication breakdown | No response for 48+ hours | Follow up with direct message, check availability |

---

## Resources

- [pr-comment-writing.md](references/pr-comment-writing.md) - Code review comment patterns
- [issue-communication.md](references/issue-communication.md) - Bug report and feature request handling
- [technical-explanation.md](references/technical-explanation.md) - Explaining technical decisions
- [conflict-resolution.md](references/conflict-resolution.md) - Handling disagreements
- [status-updates.md](references/status-updates.md) - Progress reporting
- [templates-for-humans.md](references/templates-for-humans.md) - PR and commit templates
