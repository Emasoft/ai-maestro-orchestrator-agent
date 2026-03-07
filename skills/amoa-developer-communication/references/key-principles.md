## Table of Contents

- [1. Assume Good Intent](#1-assume-good-intent)
- [2. Be Specific, Not Vague](#2-be-specific-not-vague)
- [3. Separate Blocking from Non-Blocking](#3-separate-blocking-from-non-blocking)
- [4. Acknowledge Good Work](#4-acknowledge-good-work)
- [5. Provide Context for Your Feedback](#5-provide-context-for-your-feedback)

---

# Key Principles of Developer Communication

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
