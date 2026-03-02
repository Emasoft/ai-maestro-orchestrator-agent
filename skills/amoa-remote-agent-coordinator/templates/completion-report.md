# Completion Report Template

## Purpose

This template shows remote agents the EXACT format for reporting task completion to the orchestrator.

---

## Required Format

```
[DONE] {TASK_ID} - {brief_result}

## Summary
{1-3 bullet points of what was accomplished}

## Verification
{command} -> {output/result}

## Artifacts
- PR: {url}
- Branch: {branch_name}
- Files Changed: {count}

## Checklist Status
- [x] All requirements implemented
- [x] Tests pass
- [x] PR created and ready for review
```

---

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| TASK_ID | YES | The exact task ID from delegation |
| brief_result | YES | 5-10 words max describing outcome |
| Summary | YES | 1-3 bullet points of work done |
| Verification | YES | Actual command + output proving it works |
| Artifacts | YES | PR URL, branch, files changed |
| Checklist Status | YES | All items from original task |

---

## Examples

### Example 1: Feature Implementation

```
[DONE] GH-42-auth-implementation - JWT auth with refresh tokens complete

## Summary
- Implemented JWT authentication with 24h expiry
- Added refresh token support with 7-day rotation
- Created login/logout/refresh endpoints

## Verification
cargo test auth:: -> 12 tests passed, 0 failed
cargo run -- --help -> Shows auth commands

## Artifacts
- PR: https://github.com/org/repo/pull/43
- Branch: feature/GH-42-auth
- Files Changed: 8 (3 new, 5 modified)

## Checklist Status
- [x] JWT token generation
- [x] Token validation middleware
- [x] Refresh token rotation
- [x] Login endpoint
- [x] Logout endpoint
- [x] Tests for all endpoints
- [x] Documentation updated
```

### Example 2: Bug Fix

```
[DONE] GH-15-fix-null-crash - Null pointer fixed with proper validation

## Summary
- Added null check before dereferencing user object
- Added test case for null user scenario

## Verification
cargo test test_null_user -> PASSED
cargo clippy -> No warnings

## Artifacts
- PR: https://github.com/org/repo/pull/16
- Branch: fix/GH-15-null-crash
- Files Changed: 2

## Checklist Status
- [x] Identify root cause
- [x] Implement fix
- [x] Add regression test
- [x] Verify fix locally
```

---

## Verification Commands by Language

| Language | Verification Command |
|----------|---------------------|
| Rust | `cargo test && cargo clippy` |
| Python | `pytest tests/ && mypy src/` |
| JavaScript | `npm test && npm run lint` |
| TypeScript | `npm test && tsc --noEmit` |
| Go | `go test ./... && go vet ./...` |

---

## Common Mistakes to Avoid

| Wrong | Why It's Wrong |
|-------|----------------|
| `[DONE] Task complete` | Missing task ID and brief result |
| No verification section | Cannot prove task actually works |
| `Tests pass` without command | Must show actual command output |
| PR not created | Task not complete until PR ready |
| Missing checklist | Cannot verify all requirements met |

---

## If Task Cannot Be Completed

Use `[FAILED]` status instead:

```
[FAILED] GH-42-auth-implementation - Blocked by missing database schema

## Summary
- Attempted JWT implementation
- Blocked: User table does not exist yet

## Blockers
1. Database migration for users table pending (GH-40)
2. Cannot proceed without user model

## Partial Progress
- Branch: feature/GH-42-auth (partial work saved)
- Files: src/auth/ (skeleton structure)

## Recommendation
Wait for GH-40 completion, then resume this task
```

---

## Report Delivery

1. Write detailed report to: `docs_dev/reports/{TASK_ID}_completion.md`
2. Send summary (1-2 lines) to orchestrator
3. Include path to detailed report in message
