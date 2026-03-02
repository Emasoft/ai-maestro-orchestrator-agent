# Technical Explanation Guide

## Contents

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

## 3.1 Explaining Technical Decisions

Technical decisions shape software for years. Documenting *why* matters more than documenting *what* - the code shows what, but only documentation explains why.

### 3.1.1 The Context-Decision-Consequences Format

This structure makes technical explanations clear and complete:

**Context**: What situation led to needing a decision?
**Decision**: What did we decide?
**Consequences**: What are the results (both positive and negative)?

**Example**:

```markdown
## Context
Our authentication tokens were being validated on every API request, adding 50-100ms of latency. With 1000+ requests per second, this created significant load on the auth service.

## Decision
Implement token caching with a 5-minute TTL in the API gateway.

## Consequences
**Positive**:
- Reduced auth service load by 90%
- Improved average API response time by 60ms

**Negative**:
- Token revocation has a 5-minute delay (security tradeoff)
- Cache invalidation adds complexity to the auth service
- Memory usage in API gateway increased by ~200MB

**Mitigations**:
- Critical actions (password change, logout) force cache invalidation
- Monitoring added for cache hit rates and memory usage
```

### 3.1.2 Acknowledging Tradeoffs Honestly

Every technical decision has tradeoffs. Hiding them creates problems later when someone hits the downside.

**Bad explanation** (hides tradeoffs):
```markdown
We use MongoDB for its flexibility and scalability.
```

**Good explanation** (honest about tradeoffs):
```markdown
We chose MongoDB over PostgreSQL. Here's why:

**What we gained**:
- Schema flexibility: Our data model evolves frequently in early development
- Horizontal scaling: Built-in sharding for our multi-tenant architecture
- Developer velocity: JSON documents match our API contracts

**What we gave up**:
- ACID transactions across collections (we use saga pattern instead)
- Complex joins (we denormalize data, accepting storage overhead)
- Mature tooling for migrations (we built custom migration scripts)

**When to revisit this decision**:
- If we need cross-document transactions frequently
- If data model stabilizes and flexibility becomes less important
- If we hit storage cost concerns from denormalization
```

### 3.1.3 Referencing Alternatives Considered

Show that you evaluated options, not just picked the first idea.

**Template**:
```markdown
## Alternatives Considered

### Option A: Build custom solution
- Pros: Full control, no dependencies
- Cons: 3-month development time, ongoing maintenance
- Verdict: Too expensive for current team size

### Option B: Use library X
- Pros: Battle-tested, good documentation
- Cons: GPL license incompatible with our MIT project
- Verdict: License blocker

### Option C: Use library Y (selected)
- Pros: MIT license, active maintenance, meets 90% of requirements
- Cons: Missing feature Z (we'll contribute or work around)
- Verdict: Best balance of capability vs cost

### Option D: Use managed service
- Pros: Zero maintenance
- Cons: $500/month, data leaves our infrastructure
- Verdict: Cost prohibitive at current scale, revisit at 10x traffic
```

---

## 3.2 Justifying Architectural Choices

Architecture decisions have long-term consequences. Justifications should connect to business needs, not just technical preferences.

### 3.2.1 Connecting to Requirements

Always trace architecture back to actual requirements, not hypothetical ones.

**Weak justification** (no connection to requirements):
```markdown
We use microservices because it's the modern approach.
```

**Strong justification** (connected to requirements):
```markdown
We split the billing service from the user service because:

**Requirement**: Different teams own billing vs user management
- Separate repos allow independent release cycles
- Team autonomy prevents coordination bottlenecks

**Requirement**: Billing must have 99.99% uptime, user profiles can have 99.9%
- Independent scaling and failover
- Billing issues don't cascade to user service

**Requirement**: PCI compliance for billing
- Smaller audit scope by isolating payment data
- Different security posture per service
```

### 3.2.2 Explaining Scalability and Maintainability

Be specific about scaling assumptions and maintenance expectations.

**Example**:
```markdown
## Scalability Assumptions

This architecture is designed for:
- 10,000 - 100,000 concurrent users
- 1,000 - 10,000 requests per second
- 10TB - 100TB of stored data

**At 10x current scale**: Works with horizontal scaling, no architecture changes needed.

**At 100x current scale**: Database layer needs sharding, consider read replicas. Event bus may need partitioning.

**Beyond 1000x**: Fundamental rearchitecture needed. Current approach won't scale economically.

## Maintainability Considerations

**Adding new features**:
- New endpoints are straightforward (follow existing patterns)
- New background jobs require queue configuration
- New integrations may need circuit breakers

**Common maintenance tasks**:
- Database migrations: Use Flyway, follow versioning convention
- Configuration changes: Through environment variables, no redeploy needed
- Dependency updates: Monthly security patches, quarterly major updates
```

### 3.2.3 Addressing Security Implications

Security is not optional. Address it explicitly in architectural explanations.

**Example**:
```markdown
## Security Model

**Authentication**: JWT tokens with RS256 signing
- Why: Asymmetric signing allows services to verify tokens without access to signing key
- Trade-off: Larger tokens than symmetric encryption

**Authorization**: Role-based access control (RBAC)
- Roles: Admin, Member, Guest
- Enforcement: Gateway level for API, service level for data access
- Audit: All access decisions logged for compliance

**Data Protection**:
- At rest: AES-256 encryption for PII fields
- In transit: TLS 1.3 required for all connections
- Key management: AWS KMS with automatic rotation

**Known Limitations**:
- Service-to-service communication trusts internal network (no mTLS yet)
- Logging may contain PII in error messages (sanitization in progress)
```

---

## 3.3 Providing Context for Non-Obvious Code

Some code looks wrong but is right. Some code is technical debt. Distinguish them clearly.

### 3.3.1 When Comments Are Necessary

Comments explain *why*, not *what*. Use them for:
- Non-obvious behavior
- Workarounds for bugs
- Performance optimizations that sacrifice readability
- Compliance requirements

**Bad comment** (explains what):
```javascript
// Loop through users
for (const user of users) {
```

**Good comment** (explains why):
```javascript
// Process users in insertion order because the payment provider
// requires chronological processing for batch reconciliation.
// See: https://payprovider.com/docs/batch-processing#ordering
for (const user of users) {
```

**Necessary comment** (non-obvious constraint):
```javascript
// IMPORTANT: This timeout must be longer than the database
// connection timeout (30s) or we get false-positive health check
// failures during connection pool recovery.
// See incident post-mortem: wiki.company.com/incidents/2024-01-15
const HEALTH_CHECK_TIMEOUT = 45000;
```

### 3.3.2 Linking to Issues or ADRs

Connect code to its history:

```javascript
// Workaround for Safari bug with flex containers in overflow scroll.
// Track removal: https://github.com/org/project/issues/1234
// Safari bug report: https://bugs.webkit.org/show_bug.cgi?id=XXXXX
const useFlexWorkaround = isSafari && version < 16;
```

```python
# This query uses a suboptimal index because MySQL's optimizer
# chooses poorly for our data distribution.
# ADR: docs/decisions/ADR-0012-force-index-user-queries.md
# When to revisit: After MySQL 9.0 upgrade (better optimizer)
cursor.execute("SELECT /*+ INDEX(users idx_created_at) */ ...")
```

### 3.3.3 Explaining Workarounds and Technical Debt

Mark technical debt clearly so future developers know what's intentional vs accidental:

```javascript
// TODO(tech-debt): This string manipulation should use a proper
// parser. We're shipping this workaround for the v2.0 deadline,
// but it fails on nested brackets.
// Ticket: JIRA-4567
// Effort to fix: ~3 days
// Risk until fixed: Edge case failures for <1% of users
function parseConfig(input) {
  return input.split('=')[1]; // WRONG but works for current use cases
}
```

```python
# HACK: Sleep to avoid rate limiting from external API.
# The correct fix is implementing exponential backoff with jitter,
# but we're awaiting the rate-limit-handler library update.
# Tracking: #789
# Remove after: rate-limit-handler >= 2.0.0
import time
time.sleep(0.5)
```

---

## 3.4 Linking to Relevant Documentation

Good explanations point to sources. Great explanations point to the *right* sources.

### 3.4.1 Internal Wiki and ADRs

Architecture Decision Records (ADRs) document the *why* behind major decisions:

```markdown
This service uses event sourcing. For background on why, see:
- [ADR-0005: Event Sourcing for Audit Requirements]\(../docs/adr/ADR-0005.md\)
- [Event Sourcing Guide]\(wiki.company.com/engineering/patterns/event-sourcing\)

Key implications for this code:
- State is derived from events, never stored directly
- All mutations must go through the event store
- Queries use read models (eventually consistent)
```

### 3.4.2 External Specifications

Reference authoritative sources for standards and protocols:

```markdown
This implements OAuth 2.0 Authorization Code Flow with PKCE:
- Spec: [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749) Section 4.1
- PKCE Extension: [RFC 7636](https://tools.ietf.org/html/rfc7636)
- Our implementation guide: [wiki/auth/oauth-implementation](...)

Deviations from spec:
- We use 128-bit code verifiers (spec allows 43-128)
- Token lifetime is 1 hour (spec doesn't specify)
```

### 3.4.3 Code Examples in the Codebase

Point to existing patterns:

```markdown
## How to Add a New API Endpoint

Follow the existing pattern in `src/api/users.ts`:

1. **Define types**: See `src/types/user.ts` for request/response types
2. **Implement handler**: See `handleGetUser()` for standard patterns
3. **Add validation**: See `userValidation.ts` for Joi schemas
4. **Register route**: See `routes.ts` for route registration
5. **Add tests**: See `users.test.ts` for testing approach

The Users API is our reference implementation. New endpoints should follow its structure unless there's a documented reason to diverge.
```

---

## 3.5 Using Code Examples Effectively

Code examples teach better than prose. Use them well.

### 3.5.1 Before/After Comparisons

Show transformation clearly:

```markdown
## Refactoring: Extract Validation Logic

**Before** (validation mixed with business logic):
```javascript
function processOrder(order) {
  if (!order.items || order.items.length === 0) {
    throw new Error('Order must have items');
  }
  if (order.total < 0) {
    throw new Error('Total cannot be negative');
  }
  if (!order.customer?.email) {
    throw new Error('Customer email required');
  }

  // Actual business logic buried after validation
  return chargeCustomer(order);
}
```

**After** (validation separated):
```javascript
function validateOrder(order) {
  const errors = [];
  if (!order.items?.length) errors.push('Order must have items');
  if (order.total < 0) errors.push('Total cannot be negative');
  if (!order.customer?.email) errors.push('Customer email required');

  if (errors.length) {
    throw new ValidationError(errors);
  }
}

function processOrder(order) {
  validateOrder(order);
  return chargeCustomer(order);
}
```

**Benefits**:
- Validation logic is testable in isolation
- Error messages can be collected and returned together
- Business logic is clearer
```

### 3.5.2 Minimal Reproducible Examples

Strip down to essentials:

```markdown
## The Bug

**Full context not needed**. The bug is in how we handle null:

```javascript
// Bug: crashes when user.address is null
const city = user.address.city; // TypeError: Cannot read 'city' of null

// Fix: optional chaining
const city = user.address?.city ?? 'Unknown';
```

**Why this happens**: The API returns `null` for users without addresses, not `undefined` or an empty object. Our type definitions said `address: Address` but should say `address: Address | null`.
```

### 3.5.3 Annotated Code Blocks

Add inline explanations:

```markdown
## Request Flow Explanation

```javascript
async function handleRequest(req, res) {
  // 1. AUTHENTICATION: Verify JWT token
  //    - Throws 401 if invalid or expired
  //    - Attaches user to request
  const user = await authenticate(req);

  // 2. AUTHORIZATION: Check permissions
  //    - Uses RBAC model
  //    - Throws 403 if insufficient permissions
  await authorize(user, 'orders:read');

  // 3. VALIDATION: Sanitize and validate input
  //    - Returns 400 with details if invalid
  //    - Prevents injection attacks
  const params = validate(req.query, orderQuerySchema);

  // 4. BUSINESS LOGIC: The actual work
  //    - Database operations happen here
  //    - May throw domain-specific errors
  const orders = await orderService.findByUser(user.id, params);

  // 5. RESPONSE: Format and send
  //    - Standard envelope format
  //    - Includes pagination metadata
  res.json({ data: orders, meta: { total: orders.length } });
}
```

Each numbered step can fail independently. See error handling guide for how each failure type is handled.
```

---

## Summary: Technical Explanation Checklist

Before sharing a technical explanation:

- [ ] Is the *why* clear, not just the *what*?
- [ ] Are tradeoffs acknowledged honestly?
- [ ] Were alternatives considered and documented?
- [ ] Is it connected to actual requirements?
- [ ] Are security implications addressed?
- [ ] Are non-obvious parts commented with context?
- [ ] Does it link to relevant documentation?
- [ ] Are code examples minimal and annotated?
