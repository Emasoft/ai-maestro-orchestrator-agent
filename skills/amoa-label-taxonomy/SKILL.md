---
name: amoa-label-taxonomy
description: GitHub label taxonomy for multi-agent systems. Use when managing labels for issue tracking and coordination. Trigger with label requests.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# AMOA Label Taxonomy

## Overview

Defines the label taxonomy for AI Maestro multi-agent orchestration. Labels classify issues (type, priority, component) and coordinate agents (assignment, status). All labels use `<category>:<value>` format with strict cardinality rules.

## Prerequisites

1. Read **AGENT_OPERATIONS.md** for orchestrator workflow context
2. Access to GitHub CLI (`gh`) configured for the repository
3. Understanding of ai-maestro agent roles (AMOA, AMCOS, AMIA, AMAMA)

## Instructions

1. Determine the operation type (create, query, update)
2. Identify the label category (`assign:*`, `status:*`, `priority:*`, etc.)
3. Check cardinality rules. See: [references/usage-rules.md](./references/usage-rules.md)
4. If updating, remove conflicting labels first (especially `assign:*` and `status:*`)
5. Apply the new label using `gh` CLI
6. Verify the label was applied correctly

---

## Label Categories Quick Reference

**Full category details**: [references/label-categories-detailed.md](./references/label-categories-detailed.md)

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

Every issue MUST have: `status:*`, `priority:*`, `type:*`.

## Kanban Columns (8-Column System)

| # | Label | Description |
|---|-------|-------------|
| 1 | `status:backlog` | Entry point for new tasks |
| 2 | `status:todo` | Ready to start |
| 3 | `status:in-progress` | Active work |
| 4 | `status:ai-review` | Integrator reviews ALL tasks |
| 5 | `status:human-review` | User reviews BIG tasks only |
| 6 | `status:merge-release` | Ready to merge |
| 7 | `status:done` | Completed |
| 8 | `status:blocked` | Blocked at any stage |

**Routing**: Small tasks skip human-review. Big tasks go through all stages.

---

## Usage Rules

Cardinality, lifecycle, and common mistakes. See: [references/usage-rules.md](./references/usage-rules.md)

## CLI Commands

**Full command reference**: [references/cli-commands.md](./references/cli-commands.md)

```bash
# Assign task
gh issue edit 42 --add-label "assign:implementer-1"
# Update status
gh issue edit 42 --remove-label "status:todo" --add-label "status:in-progress"
# Query assigned issues
gh issue list --label "assign:implementer-1"
```

## Error Handling

Label conflict errors, invalid category errors, and cardinality violations. See: [references/error-handling-and-output.md](./references/error-handling-and-output.md)

## Output

Output formats (stdout summary, JSON for hooks) and label color codes. See: [references/error-handling-and-output.md](./references/error-handling-and-output.md)

## Examples

**Full examples**: [references/examples.md](./references/examples.md)

```bash
# Reassign task
gh issue edit 42 --remove-label "assign:implementer-1" --add-label "assign:implementer-2"
```

---

## Resources

- [references/label-categories-detailed.md](./references/label-categories-detailed.md) - Full category definitions
- [references/cli-commands.md](./references/cli-commands.md) - Complete CLI reference
- [references/examples.md](./references/examples.md) - Usage examples
- [references/usage-rules.md](./references/usage-rules.md) - Cardinality, lifecycle, mistakes
- [references/error-handling-and-output.md](./references/error-handling-and-output.md) - Errors, output, colors
- **AGENT_OPERATIONS.md** - Orchestrator workflow context
- **amoa-messaging-templates** / **amoa-task-distribution** / **amoa-progress-monitoring**

## Script Output Rules

Scripts write verbose output to `docs_dev/reports/`, emit only `[OK/ERROR] name - summary` to stdout. Exception: `scripts/amoa_stop_check/` outputs JSON (hook requirement).
