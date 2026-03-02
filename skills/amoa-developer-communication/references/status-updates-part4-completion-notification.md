# Status Updates - Part 4: Completion Notification

## Contents
- 5.4 Completion notification
  - 5.4.1 Summary of changes
  - 5.4.2 Testing performed
  - 5.4.3 What reviewers should focus on

---

## 5.4 Completion Notification

When work is done, communicate clearly what changed and what to focus on in review.

### 5.4.1 Summary of Changes

Explain what the change does in terms a reviewer (or future you) can understand.

**Template**:
```
## Summary
[1-2 sentences describing what this does and why]

## Changes
- [Category]: [Change 1]
- [Category]: [Change 2]
- [Category]: [Change 3]

## Technical notes
[Anything unusual about the implementation]
```

**Example**:
```
## Summary
Implements JWT authentication for the API. Users can now login with email/password and receive a token for subsequent requests.

## Changes
- **New endpoints**: POST /auth/login, POST /auth/logout, POST /auth/refresh
- **Middleware**: Added authMiddleware for protected routes
- **Database**: New sessions table for token tracking
- **Config**: JWT secret and expiry configurable via env vars

## Technical notes
- Using RS256 algorithm for token signing (asymmetric)
- Tokens expire after 1 hour, refresh tokens after 7 days
- Rate limiting on login endpoint (5 attempts per minute)
```

### 5.4.2 Testing Performed

Describe what testing you did so reviewers know what's covered.

**Template**:
```
## Testing
- [ ] Unit tests: [coverage/status]
- [ ] Integration tests: [coverage/status]
- [ ] Manual testing: [what you tested]
- [ ] Edge cases: [specific scenarios tested]

## Not tested (known gaps)
- [What wasn't tested and why]
```

**Example**:
```
## Testing
- [x] Unit tests: 94% coverage on new code, all passing
- [x] Integration tests: Full auth flow tested against test database
- [x] Manual testing: Login, logout, token refresh, expired token handling
- [x] Edge cases: Invalid credentials, malformed tokens, concurrent sessions

## Not tested (known gaps)
- Load testing: Will do before production deploy
- Mobile clients: Need QA to test on iOS/Android
- Safari: Known to have cookie issues, needs verification
```

### 5.4.3 What Reviewers Should Focus On

Guide reviewers to the important parts.

**Template**:
```
## Review guidance

**Please focus on**:
- [Specific area 1]: [Why it needs scrutiny]
- [Specific area 2]: [Question you have]

**Less critical**:
- [Area that's straightforward]
- [Auto-generated code]

**Questions for reviewers**:
1. [Specific question about design choice]
2. [Concern you want feedback on]
```

**Example**:
```
## Review guidance

**Please focus on**:
- `src/auth/tokenService.ts`: Core token logic, security-critical
- `src/middleware/auth.ts`: Error handling approach, not sure if comprehensive
- Database migration: First time doing session management, want to validate schema

**Less critical**:
- Test files: Standard patterns, auto-generated boilerplate
- Config changes: Just adding env vars

**Questions for reviewers**:
1. Is RS256 the right algorithm choice? We could use HS256 for simplicity.
2. Should token refresh extend the refresh token expiry or keep original?
```

---

**Previous**: [Part 3: ETA Management](status-updates-part3-eta-management.md)
**Next**: [Part 5: Post-Mortem and Templates](status-updates-part5-postmortem-templates.md)
