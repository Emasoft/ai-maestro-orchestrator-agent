# Templates for Human Communication - Part 2: Commit Messages

## Contents

- 6.2 Commit message guidelines
  - 6.2.1 Conventional commits format
  - 6.2.2 Subject line rules
  - 6.2.3 Body content guidelines

---

## 6.2 Commit Message Guidelines

Commit messages are the permanent record of *why* changes were made. Write them for future archeologists.

### 6.2.1 Conventional Commits Format

Use a standard format that enables automated tooling.

**Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes nor adds |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Build process, dependencies, config |

**Scopes** (optional, project-specific):
- `auth`, `api`, `ui`, `db`, `config`, etc.

### 6.2.2 Subject Line Rules

The subject is the most important part. Make it useful.

**Rules**:
1. **50 characters or less** (hard limit: 72)
2. **Imperative mood**: "Add feature" not "Added feature"
3. **No period** at the end
4. **Capitalize** first letter
5. **Complete the sentence**: "This commit will [subject]"

**Good subjects**:
```
feat(auth): Add rate limiting to login endpoint
fix(api): Handle null user in profile response
docs: Update API reference for v2 endpoints
refactor(db): Extract query builders into separate module
```

**Bad subjects**:
```
fixed bug                    # Too vague
Added the new feature.       # Past tense, period, too vague
update stuff                 # Too vague, lowercase
feat(auth): Add rate limiting to the login endpoint to prevent brute force attacks by limiting requests to 5 per minute per IP  # Too long
```

### 6.2.3 Body Content Guidelines

The body explains *why* the change was made.

**Template**:
```
<type>(<scope>): <subject>

[Why this change is needed]

[What approach was taken and why]

[Any important caveats or side effects]
```

**Example**:
```
feat(auth): Add rate limiting to login endpoint

Our security audit identified brute force attacks as a risk for
password-based authentication. Users were making thousands of
login attempts to guess passwords.

This commit adds rate limiting using Redis-backed counters.
Configuration:
- 5 requests per minute per IP (configurable)
- 429 response with Retry-After header
- Fail-open if Redis is unavailable

Alternative considered: In-memory rate limiting (rejected because
it doesn't work across multiple server instances).

Related: #123, security-audit-2024-Q1
```

---

**Previous**: See [templates-for-humans-part1-pr-descriptions.md](templates-for-humans-part1-pr-descriptions.md) for PR description templates.

**Next**: See [templates-for-humans-part3-release-notes.md](templates-for-humans-part3-release-notes.md) for release notes format.
