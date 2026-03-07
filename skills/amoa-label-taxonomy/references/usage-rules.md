## Table of Contents
- Label Cardinality
- Label Lifecycle
- Common Mistakes to Avoid

---

# Usage Rules

## Label Cardinality

| Category | Cardinality | Meaning |
|----------|-------------|---------|
| `assign:*` | 0 or 1 | At most one assignment |
| `status:*` | 1 | Exactly one status |
| `priority:*` | 1 | Exactly one priority |
| `type:*` | 1 | Exactly one type |
| `component:*` | 1+ | One or more components |
| `effort:*` | 1 | Exactly one effort |
| `platform:*` | 0+ | Zero or more platforms |
| `toolchain:*` | 0+ | Zero or more toolchains |
| `review:*` | 0 or 1 | At most one review status |

## Label Lifecycle

**When Issue Created:**
1. Set `type:*` based on issue content
2. Set `status:backlog`
3. Optionally set `component:*` if known

**When Issue Triaged:**
1. Set `priority:*`
2. Set `effort:*`
3. Set `platform:*` and `toolchain:*` if relevant
4. Change `status:backlog` -> `status:todo` (or keep in backlog)

**When Issue Assigned:**
1. Add `assign:<agent-name>`
2. Change `status:todo` -> `status:in-progress`

**When Work Done, AI Reviews:**
1. Change `status:in-progress` -> `status:ai-review`
2. Integrator (AMIA) reviews ALL tasks

**When Human Review Needed (BIG tasks only):**
1. Change `status:ai-review` -> `status:human-review`
2. User reviews the task

**When Ready to Merge:**
1. Change review status -> `status:merge-release`
2. Ready to merge and release

**When Issue Completed:**
1. Remove `assign:*` label
2. Change `status:merge-release` -> `status:done`

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|------------------|
| Multiple `assign:*` labels | Remove old before adding new |
| Missing `status:*` label | Every issue needs exactly one |
| Changing `type:*` mid-work | Create new issue instead |
| Using `agent:*` prefix | Use `assign:*` for assignments |
| Forgetting to update status | Update status at each workflow transition |
