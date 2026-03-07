## Table of Contents

- [Communication Tone Quick Reference](#communication-tone-quick-reference)
- [Examples of Constructive Communication](#examples-of-constructive-communication)
- [Error Handling in Communication](#error-handling-in-communication)
- [Pre-Send Checklist](#pre-send-checklist)

---

# Communication Tone Quick Reference

| Situation | Wrong Tone | Right Tone |
|-----------|------------|------------|
| Code issue | "This is wrong" | "This might cause X - what if we tried Y?" |
| Suggestion | "You should do X" | "One option would be X - thoughts?" |
| Bug found | "You broke the build" | "The build is failing - looks like it's related to X" |
| Disagreement | "That won't work" | "I have concerns about X because of Y - how about Z?" |
| Confusion | "This doesn't make sense" | "Help me understand the reasoning behind X?" |
| Urgency | "Fix this now" | "This is blocking deployment - can we prioritize?" |

---

## Examples of Constructive Communication

### Example 1: Constructive Code Review Comment

**Wrong:**
> "This code is inefficient and poorly structured."

**Right:**
> "I noticed this loop processes items sequentially. Consider using `Promise.all()` for parallel execution - it could reduce the response time from ~500ms to ~100ms based on similar patterns elsewhere in the codebase."

### Example 2: Acknowledging Good Work

> "Nice catch on the null check at line 42 - that edge case would have caused issues in production. The error message is also very clear."

---

## Error Handling in Communication

| Situation | Issue | Resolution |
|-----------|-------|------------|
| Misunderstood feedback | Developer responds defensively | Clarify intent, acknowledge their perspective |
| Unclear requirements | Developer delivers wrong implementation | Provide concrete examples and success criteria |
| Communication breakdown | No response for 48+ hours | Follow up with direct message, check availability |

---

## Pre-Send Checklist

Before sending any communication, verify:

- [ ] Is the tone respectful and professional?
- [ ] Did I assume good intent?
- [ ] Is feedback specific with examples?
- [ ] Did I separate blocking from non-blocking?
- [ ] Did I explain *why*, not just *what*?
- [ ] Is there anything to acknowledge or praise?
- [ ] Would I feel good receiving this message?
