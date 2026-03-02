# PR Comment Writing Guide

## Contents

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

## 1.1 Writing Constructive Code Review Comments

Code review comments shape team culture. Every comment teaches something - either about code quality, or about how teammates treat each other. Write comments that make developers *want* to improve.

### 1.1.1 The Praise-Suggestion-Question Framework

Structure comments to maximize learning while minimizing defensiveness:

**Praise**: Acknowledge what works before addressing issues
```
Nice error handling here - catching the specific exception types makes debugging much easier.
```

**Suggestion**: Offer alternatives, not mandates
```
One option: we could extract this validation into a separate function. That would let us reuse it in the registration flow too.
```

**Question**: Invite dialogue about non-obvious code
```
I'm curious about the caching strategy here - is there a reason we're caching at this layer rather than in the service?
```

**Combined example**:
```
The retry logic looks solid - I like that you're using exponential backoff.

One thought: we might want to add a maximum retry count to prevent infinite loops if the service is completely down. Something like `maxRetries: 3` in the config.

Was there a specific reason for choosing 1 second as the initial delay? I'm wondering if we should make that configurable too.
```

### 1.1.2 Balancing Thoroughness with Developer Time

**Problem**: Exhaustive reviews create long feedback cycles and demoralize authors.

**Guidelines**:
- Limit comments to 5-10 per review round
- Group related issues into a single comment
- Prioritize: correctness > security > performance > style
- Save nitpicks for a final "polish" round after core issues are resolved

**If you find many issues**:
```
I noticed a few patterns we should discuss before diving into line-by-line feedback. Can we have a quick sync to align on the approach? Main areas:

1. Error handling strategy
2. Test coverage for edge cases
3. Naming conventions

Once we're aligned, I'll do a detailed review.
```

---

## 1.2 Tone Guidelines for Professional Reviews

### 1.2.1 Avoiding Pedantic or Condescending Language

**Words that trigger defensiveness**:
- "Obviously..." (implies the reader is slow)
- "Simply..." (dismisses complexity)
- "Just..." (minimizes effort required)
- "Actually..." (implies correction of ignorance)
- "As I mentioned before..." (implies the reader wasn't paying attention)

**Reframings**:

| Pedantic | Professional |
|----------|-------------|
| "Obviously, you should use async here" | "This would benefit from async/await" |
| "Simply add error handling" | "We need to handle the case where the API returns an error" |
| "Just refactor this" | "This section is doing a lot - breaking it into smaller functions would help readability" |
| "Actually, that's not how it works" | "I think there might be a misunderstanding about X - here's how it behaves" |

### 1.2.2 Using "We" Instead of "You"

**Why "we" works**: It frames the review as collaboration, not criticism. You're on the same team working toward the same goal.

**"You" statements** (accusatory):
- "You forgot to handle null"
- "You should add tests"
- "Your code doesn't follow the style guide"

**"We" statements** (collaborative):
- "We need to handle the null case here"
- "We should add tests for this flow"
- "This doesn't quite match our style guide - let's update it"

**Alternative framings**:
- "This code..." instead of "Your code..."
- "The function..." instead of "Your function..."
- "Let's consider..." instead of "You should consider..."

---

## 1.3 When to Request Changes Versus Suggest

### 1.3.1 Blocking Issues That Require Changes

**Request changes when**:
- The code has a bug that will cause runtime errors
- Security vulnerabilities exist
- The change will break existing functionality
- The change doesn't meet acceptance criteria
- Tests are missing for critical paths
- The code violates compliance requirements

**Format for blocking comments**:
```
[BLOCKING] This will cause a runtime error when `user` is undefined.

The destructuring on line 45 assumes `user` is always present, but the API can return null when the session expires.

Suggested fix:
const { name, email } = user ?? { name: 'Guest', email: '' };

Or add an early return:
if (!user) return handleLoggedOutState();
```

### 1.3.2 Non-Blocking Suggestions and Nits

**Use suggestions when**:
- The code works but could be clearer
- There's a more idiomatic approach
- Performance could improve (non-critical path)
- Style preferences apply

**Format for suggestions**:
```
[Suggestion] Consider using `Array.prototype.find()` here instead of the for loop - it's a bit more readable for this use case.

Current:
for (const item of items) {
  if (item.id === targetId) return item;
}

Alternative:
return items.find(item => item.id === targetId);

Not blocking - the current code works fine.
```

**Format for nits**:
```
[Nit] Typo in the variable name: `recieved` → `received`
```

### 1.3.3 Praise-Only Approvals

Sometimes the best review is approval with acknowledgment:

```
LGTM!

A few things I really liked:
- The error messages are super clear - users will actually understand what went wrong
- Good test coverage for the edge cases
- Nice use of the strategy pattern for the payment processors

Ship it! 🚀
```

---

## 1.4 Acknowledging Good Code Patterns

**Why it matters**: Positive reinforcement teaches what "good" looks like and motivates continued excellence.

**What to acknowledge**:
- Clever but readable solutions
- Good test coverage
- Clear documentation
- Proactive error handling
- Performance optimizations
- Accessibility considerations
- Security best practices

**Examples**:

```
Nice catch on the race condition - initializing the mutex before starting the goroutines prevents the subtle bug we had in the auth service.
```

```
Love this abstraction. Separating the transport layer from the business logic means we can swap REST for GraphQL later without touching the core.
```

```
Great defensive coding - validating the input at the API boundary means downstream code can trust the data shape.
```

```
The test names read like documentation. `should_reject_expired_tokens_with_clear_error_message` tells me exactly what this tests without reading the implementation.
```

---

## 1.5 Avoiding Accusatory Language

### 1.5.1 Why "You" Statements Feel Like Attacks

Human brains process "you" + negative as personal criticism:
- "You made a mistake" triggers fight-or-flight
- "There's a mistake here" triggers problem-solving

Code reviews with "you" statements have measurably higher:
- Response latency (defensiveness slows engagement)
- Comment threads (arguing instead of fixing)
- Abandonment rate (developers stop responding)

### 1.5.2 Reframing with "This" and "We"

**Pattern**: Replace "You [verb]" with "This [noun]" or "We [should]"

| Accusatory | Neutral |
|------------|---------|
| "You didn't handle the error" | "This error case isn't handled" |
| "You should use a const here" | "This could be a const" |
| "You forgot to add tests" | "We need tests for this flow" |
| "Your logic is wrong" | "This logic doesn't match the spec" |
| "You didn't follow the pattern" | "This diverges from our pattern in X" |
| "You broke the build" | "The build is broken - looks related to X" |

**Even better**: Focus on the code, not the author

| About the author | About the code |
|------------------|----------------|
| "You wrote this confusingly" | "This section is hard to follow" |
| "You made this too complex" | "This has more complexity than needed" |
| "You duplicated code" | "This logic also exists in util.js" |

---

## 1.6 Examples of Good Versus Bad Comments

### Example 1: Missing Error Handling

**Bad**:
```
You forgot to handle errors. This is going to crash in production.
```

**Good**:
```
This async call can throw if the network is unavailable. We should wrap it in a try/catch to show users a friendly error instead of crashing.

Something like:
try {
  const data = await fetchUserData(userId);
  return processData(data);
} catch (error) {
  logger.error('Failed to fetch user data', { userId, error });
  throw new UserFacingError('Unable to load your data. Please try again.');
}
```

### Example 2: Code Style

**Bad**:
```
Wrong indentation. Use 2 spaces not 4.
```

**Good**:
```
[Nit] Our codebase uses 2-space indentation - this file has 4 spaces. Running `npm run format` should fix it automatically.
```

### Example 3: Architecture Concern

**Bad**:
```
This is the wrong approach. You should use dependency injection.
```

**Good**:
```
I have a concern about testability here. The `EmailService` is instantiated directly, which means tests need a real SMTP server.

What if we passed the email service as a parameter?

// Current
function notifyUser(userId: string) {
  const emailService = new EmailService();
  // ...
}

// Proposed
function notifyUser(userId: string, emailService: EmailServiceInterface) {
  // ...
}

This would let us mock the email service in tests. Thoughts?
```

### Example 4: Performance Issue

**Bad**:
```
This is going to be slow. You're doing N+1 queries.
```

**Good**:
```
Heads up: this loop makes a database query on each iteration. With 100 users, that's 100 queries. This pattern is called "N+1" and can cause significant slowdowns.

We can batch this into a single query:

// Before: N+1 queries
for (const user of users) {
  const orders = await db.orders.findByUser(user.id);
}

// After: 2 queries
const userIds = users.map(u => u.id);
const ordersByUser = await db.orders.findByUsers(userIds);

Want me to help refactor this?
```

### Example 5: Security Vulnerability

**Bad**:
```
SQL injection vulnerability. Fix this.
```

**Good**:
```
[BLOCKING - Security] This query is vulnerable to SQL injection.

The `userId` parameter is interpolated directly into the query string:
const query = `SELECT * FROM users WHERE id = ${userId}`;

An attacker could pass `1; DROP TABLE users;--` as the userId.

Use parameterized queries instead:
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);

Happy to pair on this if you'd like to walk through the fix together.
```

---

## Summary: PR Comment Quality Checklist

Before submitting a code review comment:

- [ ] Does it focus on the code, not the person?
- [ ] Is it specific with line numbers and examples?
- [ ] Does it explain *why* (not just *what*)?
- [ ] Is the severity clear (blocking vs suggestion vs nit)?
- [ ] Would you be comfortable receiving this comment?
- [ ] Have you acknowledged something positive too?
