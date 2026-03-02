---
name: eoa-label-taxonomy
description: GitHub label taxonomy for multi-agent systems. Use when managing labels for issue tracking and coordination. Trigger with label requests.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: eoa-main
workflow-instruction: "support"
procedure: "support-skill"
---

# EOA Label Taxonomy

## Overview

This skill defines the complete label taxonomy for the emasoft multi-agent orchestration system. Labels serve two purposes: issue classification (type, priority, component) and agent coordination (assignment, status tracking). All labels follow the `<category>:<value>` format with strict cardinality rules to prevent conflicts and enable precise filtering.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow context
2. Access to GitHub CLI (`gh`) configured for the repository
3. Understanding of the emasoft agent roles (EOA, ECOS, EIA, EAMA)
4. Read **eoa-messaging-templates** for message formats using labels
5. Read **eoa-task-distribution** for assignment workflow

## Instructions

1. Determine the operation type (create, query, update)
2. Identify the label category (`assign:*`, `status:*`, `priority:*`, etc.)
3. Check cardinality rules for the category (section 3.1)
4. If updating, remove conflicting labels first (especially `assign:*` and `status:*`)
5. Apply the new label using `gh` CLI
6. Verify the label was applied correctly
7. Log the label change if tracking is required

See sections below for detailed category definitions and CLI commands.

### Checklist

Copy this checklist and track your progress:

**Label Operation Workflow:**
- [ ] Determine operation type (create, query, update)
- [ ] Identify the label category (`assign:*`, `status:*`, `priority:*`, etc.)
- [ ] Check cardinality rules for the category (section 3.1)
- [ ] If updating, remove conflicting labels first (especially `assign:*` and `status:*`)
- [ ] Apply the new label using `gh` CLI
- [ ] Verify the label was applied correctly
- [ ] Log the label change if tracking is required

**Label Lifecycle Checks:**
- [ ] Issue created: Set `type:*`, `status:backlog`, optional `component:*`
- [ ] Issue triaged: Set `priority:*`, `effort:*`, `platform:*`/`toolchain:*` if relevant
- [ ] Issue assigned: Add `assign:<agent>`, change `status:todo` → `status:in-progress`
- [ ] Issue in AI review: Change `status:in-progress` → `status:ai-review`
- [ ] Issue in human review: Change `status:ai-review` → `status:human-review` (BIG tasks only)
- [ ] Issue ready to merge: Change review status → `status:merge-release`
- [ ] Issue completed: Remove `assign:*`, change `status:merge-release` → `status:done`

---

## 1. Label System Overview

### What Labels Are For

Labels in the emasoft multi-agent system serve TWO purposes:

1. **Issue Classification** - Categorize what the issue IS (type, priority, component)
2. **Agent Coordination** - Track who is WORKING on the issue (assignment, status)

### Label Anatomy

All labels follow this format:

```
<category>:<value>
```

Examples:
- `status:in-progress` - Category is `status`, value is `in-progress`
- `assign:implementer-1` - Category is `assign`, value is `implementer-1`

### Why Prefixes Matter

Prefixes enable:
- Filtering: `gh issue list --label "assign:implementer-1"`
- Grouping: All `status:*` labels show workflow state
- Clarity: Instantly know what a label represents

---

## 2. Label Categories Summary

**Full category details**: [label-categories-detailed.md](./references/label-categories-detailed.md)
- Assignment labels (`assign:*`) - Agent assignment tracking
- Status labels (`status:*`) - Workflow state
- Priority labels (`priority:*`) - Urgency level
- Type labels (`type:*`) - Kind of work
- Component labels (`component:*`) - Affected code areas
- Effort labels (`effort:*`) - Size estimate
- Platform labels (`platform:*`) - Target platforms
- Toolchain labels (`toolchain:*`) - Required tools
- Review labels (`review:*`) - PR review status

### Key Categories Quick Reference

| Prefix | Purpose | Cardinality | Example |
|--------|---------|-------------|---------|
| `assign:` | Who is working on it | 0-1 | `assign:implementer-1` |
| `status:` | Current workflow state | 1 | `status:in-progress` |
| `priority:` | Urgency level | 1 | `priority:high` |
| `type:` | Kind of work | 1 | `type:bug` |
| `component:` | Affected code areas | 1+ | `component:api` |
| `effort:` | Size estimate | 1 | `effort:m` |
| `platform:` | Target platforms | 0+ | `platform:linux` |
| `toolchain:` | Required tools | 0+ | `toolchain:python` |
| `review:` | PR review status | 0-1 | `review:approved` |

### Kanban Columns (Canonical 8-Column System)

The full workflow uses these 8 status columns:

| # | Column Code | Display Name | Label | Description |
|---|-------------|-------------|-------|-------------|
| 1 | `backlog` | Backlog | `status:backlog` | Entry point for new tasks |
| 2 | `todo` | Todo | `status:todo` | Ready to start |
| 3 | `in-progress` | In Progress | `status:in-progress` | Active work |
| 4 | `ai-review` | AI Review | `status:ai-review` | Integrator agent reviews ALL tasks |
| 5 | `human-review` | Human Review | `status:human-review` | User reviews BIG tasks only (via EAMA) |
| 6 | `merge-release` | Merge/Release | `status:merge-release` | Ready to merge |
| 7 | `done` | Done | `status:done` | Completed |
| 8 | `blocked` | Blocked | `status:blocked` | Blocked at any stage |

**Task Routing Rules:**
- **Small tasks**: In Progress -> AI Review -> Merge/Release -> Done
- **Big tasks**: In Progress -> AI Review -> Human Review -> Merge/Release -> Done
- **Human Review** is requested via EAMA (Assistant Manager asks user to test/review)
- Not all tasks go through Human Review -- only significant changes requiring human judgment

---

## 3. Usage Rules

### 3.1 Label Cardinality

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

### 3.2 Label Lifecycle

**When Issue Created:**
1. Set `type:*` based on issue content
2. Set `status:backlog`
3. Optionally set `component:*` if known

**When Issue Triaged:**
1. Set `priority:*`
2. Set `effort:*`
3. Set `platform:*` and `toolchain:*` if relevant
4. Change `status:backlog` → `status:todo` (or keep in backlog)

**When Issue Assigned:**
1. Add `assign:<agent-name>`
2. Change `status:todo` → `status:in-progress`

**When Work Done, AI Reviews:**
1. Change `status:in-progress` → `status:ai-review`
2. Integrator (EIA) reviews ALL tasks

**When Human Review Needed (BIG tasks only):**
1. Change `status:ai-review` → `status:human-review`
2. User reviews the task

**When Ready to Merge:**
1. Change review status → `status:merge-release`
2. Ready to merge and release

**When Issue Completed:**
1. Remove `assign:*` label
2. Change `status:merge-release` → `status:done`

### 3.3 Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|------------------|
| Multiple `assign:*` labels | Remove old before adding new |
| Missing `status:*` label | Every issue needs exactly one |
| Changing `type:*` mid-work | Create new issue instead |
| Using `agent:*` prefix | Use `assign:*` for assignments |
| Forgetting to update status | Update status at each workflow transition |

---

## 4. Quick Reference

### Minimum Required Labels

Every issue MUST have:
1. `status:*` - One status label
2. `priority:*` - One priority label
3. `type:*` - One type label

### Colors Reference

| Category | Suggested Color |
|----------|-----------------|
| `assign:` | Various blues/purples |
| `status:` | Workflow colors (green=ready, yellow=progress, red=blocked) |
| `priority:` | Urgency colors (red=critical, orange=high, yellow=normal, green=low) |
| `type:` | Category colors |
| `component:` | Light pastels |
| `effort:` | Size-based (green=small, red=large) |
| `platform:` | Neutral grays |
| `toolchain:` | Language brand colors |
| `review:` | Review state colors |

---

## 5. CLI Commands

**Full command reference**: [cli-commands.md](./references/cli-commands.md)
- Create labels for all categories
- Query labels (list issues by label)
- Update labels (reassign, change status)
- Validate label cardinality

**Quick commands**:
```bash
# Assign task to agent
gh issue edit 42 --add-label "assign:implementer-1"

# Update status
gh issue edit 42 --remove-label "status:todo" --add-label "status:in-progress"

# Query assigned issues
gh issue list --label "assign:implementer-1"
```

---

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Label list | JSON from `gh issue view` | `{"labels": [{"name": "assign:implementer-1"}]}` |
| Label query results | Table/list from `gh issue list` | Issues matching filter criteria |
| Label creation | CLI confirmation | `✓ Label "assign:implementer-1" created` |
| Label update | CLI confirmation | `✓ Updated labels for #42` |
| Validation result | Boolean/message | "Valid: issue has exactly 1 status label" |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Multiple `assign:*` labels on one issue | Concurrent updates or incorrect removal | Remove all `assign:*` labels, then add the correct one |
| Missing `status:*` label | Label removed accidentally or never set | Set the appropriate status label based on current workflow state |
| Multiple `status:*` labels | Concurrent updates | Remove all `status:*` labels, then add the correct one |
| `gh` command fails | No auth or repo not found | Run `gh auth login` and verify repo access |
| Label conflict during reassignment | Old label not removed first | Use `gh issue edit --remove-label "old" --add-label "new"` in single command |
| Invalid label name | Typo or wrong format | Check label format: `<category>:<value>` (no spaces) |

---

## Examples

**Full examples**: [examples.md](./references/examples.md)
- Example 1: Assign task to agent
- Example 2: Update status during workflow
- Example 3: Query issues by multiple labels
- Example 4: Validate label cardinality

**Quick example - Reassign task**:
```bash
# Remove old assignment and add new in single command
gh issue edit 42 --remove-label "assign:implementer-1" --add-label "assign:implementer-2"
```

---

## Resources

- **[label-categories-detailed.md](./references/label-categories-detailed.md)** - Full category definitions
- **[cli-commands.md](./references/cli-commands.md)** - Complete CLI reference
- **[examples.md](./references/examples.md)** - Usage examples
- **AGENT_OPERATIONS.md** - Core orchestrator workflow context
- **eoa-messaging-templates** - Message templates using labels
- **eoa-task-distribution** - Assignment workflow
- **eoa-progress-monitoring** - Status tracking
