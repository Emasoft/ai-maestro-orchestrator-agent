# Templates for Human Communication - Part 1: PR Descriptions

## Contents

- 6.1 Pull Request description template
  - 6.1.1 Summary section
  - 6.1.2 Changes section with bullets
  - 6.1.3 Testing section
  - 6.1.4 Screenshots for UI changes

---

## 6.1 Pull Request Description Template

PR descriptions are documentation for future you and future contributors. Write them for someone who has no context.

### 6.1.1 Summary Section

Lead with *what* and *why* in plain language.

**Template**:
```markdown
## Summary

[1-2 sentences: What this PR does and why]

Closes #[issue-number]
```

**Example**:
```markdown
## Summary

Adds rate limiting to the API authentication endpoints to prevent brute force attacks. Users are now limited to 5 login attempts per minute per IP address.

Closes #123
```

**What to include**:
- The problem being solved (not just the solution)
- Link to related issue or discussion
- Business context if not obvious

### 6.1.2 Changes Section with Bullets

Break down the changes into scannable bullet points.

**Template**:
```markdown
## Changes

### New Features
- [Feature 1]
- [Feature 2]

### Modifications
- [Modified component 1]: [What changed]
- [Modified component 2]: [What changed]

### Removed
- [Removed item]: [Why]

### Dependencies
- Added: [package@version] for [purpose]
- Updated: [package] from [old] to [new]
- Removed: [package] (no longer needed because [reason])
```

**Example**:
```markdown
## Changes

### New Features
- Rate limiting middleware for auth endpoints
- Redis-based rate limit tracking (configurable per-endpoint)
- Custom error response for rate-limited requests (429 Too Many Requests)

### Modifications
- `src/middleware/index.ts`: Added rate limiter to middleware chain
- `src/config/index.ts`: New rate limiting configuration options

### Dependencies
- Added: `rate-limiter-flexible@2.4.1` for rate limiting implementation
- Added: `ioredis@5.3.2` for Redis connection
```

### 6.1.3 Testing Section

Describe what testing was done so reviewers know what's covered.

**Template**:
```markdown
## Testing

### Automated Tests
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All existing tests pass

### Manual Testing
- [Scenario 1]: [Expected behavior] ✅
- [Scenario 2]: [Expected behavior] ✅

### Test Coverage
- New code coverage: [X]%
- Areas not covered: [What and why]
```

**Example**:
```markdown
## Testing

### Automated Tests
- [x] Unit tests added for rate limiter middleware
- [x] Integration tests for rate limit behavior across multiple requests
- [x] All existing tests pass (CI green)

### Manual Testing
- Exceeded rate limit: Returns 429 with correct retry-after header ✅
- Under rate limit: Requests succeed normally ✅
- Redis connection failure: Falls back to allowing requests (fail-open) ✅

### Test Coverage
- New code coverage: 92%
- Areas not covered: Redis cluster failover (requires integration environment)
```

### 6.1.4 Screenshots for UI Changes

Visual changes need visual documentation.

**Template**:
```markdown
## Screenshots

### Before
[Screenshot or "N/A - new feature"]

### After
[Screenshot]

### Mobile/Responsive
[Screenshot if applicable]
```

**Example**:
```markdown
## Screenshots

### Before
Rate limit errors showed generic 500 page:
![Before screenshot](url-to-before.png)

### After
Custom error page with retry information:
![After screenshot](url-to-after.png)

### Mobile
Responsive design on mobile:
![Mobile screenshot](url-to-mobile.png)
```

---

**Next**: See [templates-for-humans-part2-commit-messages.md](templates-for-humans-part2-commit-messages.md) for commit message guidelines.
