---
name: amoa-label-taxonomy
description: "Use when applying GitHub labels. Trigger with label query or assignment requests."
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

Label taxonomy for AI Maestro multi-agent orchestration. Format: `<category>:<value>` with cardinality rules.

## Prerequisites

1. **AGENT_OPERATIONS.md** for orchestrator workflow context
2. GitHub CLI (`gh`) configured for the repository

## Instructions

1. Determine the operation type (create, query, or update labels)
2. Identify the label category (`assign:*`, `status:*`, `priority:*`, etc.)
3. Check cardinality rules in usage-rules.md before applying
4. If updating, remove conflicting labels first (especially `assign:*` and `status:*`)
5. Apply the label using `gh` CLI and verify it was applied correctly

Copy this checklist and track your progress:

- [ ] Determine the operation type (create, query, update)
- [ ] Identify the label category (`assign:*`, `status:*`, `priority:*`, etc.)
- [ ] Check cardinality rules. See: [references/usage-rules.md](./references/usage-rules.md)
  <!-- TOC: Label Cardinality | Label Lifecycle | Common Mistakes to Avoid -->
- [ ] If updating, remove conflicting labels first (especially `assign:*` and `status:*`)
- [ ] Apply the new label using `gh` CLI
- [ ] Verify the label was applied correctly

## Label Categories

Details: [label-categories-detailed.md](./references/label-categories-detailed.md)
<!-- TOC: assign | status | priority | type | component | effort | platform | toolchain | review -->

| Prefix | Purpose | Card. |
|--------|---------|-------|
| `assign:` | Who is working on it | 0-1 |
| `status:` | Workflow state | 1 |
| `priority:` | Urgency level | 1 |
| `type:` | Kind of work | 1 |
| `component:` | Affected areas | 1+ |
| `effort:` | Size estimate | 1 |
| `platform:` | Target platforms | 0+ |
| `toolchain:` | Required tools | 0+ |
| `review:` | PR review status | 0-1 |

Every issue MUST have: `status:*`, `priority:*`, `type:*`.

## Kanban (8 Columns)

`backlog` → `todo` → `in-progress` → `ai-review` → `human-review` → `merge-release` → `done` (+ `blocked`)

Small tasks skip `human-review`. Big tasks go through all stages.

## Usage Rules

See: [references/usage-rules.md](./references/usage-rules.md)
<!-- TOC: Label Cardinality | Label Lifecycle | Common Mistakes to Avoid -->

## CLI Commands

See: [references/cli-commands.md](./references/cli-commands.md)
<!-- TOC: Create Labels | Query Labels | Update Labels | Validate Label Cardinality -->

```bash
# Assign task
gh issue edit 42 --add-label "assign:implementer-1"
# Update status
gh issue edit 42 --remove-label "status:todo" --add-label "status:in-progress"
# Query assigned issues
gh issue list --label "assign:implementer-1"
```

## Output

Label operation confirmations, query result tables, and validation reports. See: [references/error-handling-and-output.md](./references/error-handling-and-output.md)
<!-- TOC: Error Handling | Output Formats | Colors Reference -->

## Error Handling

Invalid labels, cardinality violations, and missing required labels. See: [references/error-handling-and-output.md](./references/error-handling-and-output.md)
<!-- TOC: Error Handling | Output Formats | Colors Reference -->

## Examples

See: [references/examples.md](./references/examples.md)
<!-- TOC: Example 1: Assign Task to Agent | Example 4: Validate Label Cardinality -->

**Input:** `gh issue edit 42 --remove-label "assign:implementer-1" --add-label "assign:implementer-2"`
**Output:** `Updated issue #42` (reassignment)

**Input:** `gh issue list --label "status:blocked" --label "priority:high"`
**Output:** Table of high-priority blocked issues.

## Resources

- [label-categories-detailed.md](./references/label-categories-detailed.md) — Full category definitions
  <!-- TOC: assign | status | priority | type | component | effort | platform | toolchain | review -->
- [cli-commands.md](./references/cli-commands.md) — CLI reference
  <!-- TOC: Create Labels | Query Labels | Update Labels | Validate Label Cardinality -->
- [examples.md](./references/examples.md) — Usage examples
  <!-- TOC: Example 1: Assign Task to Agent | Example 4: Validate Label Cardinality -->
- [usage-rules.md](./references/usage-rules.md) — Cardinality, lifecycle, mistakes
  <!-- TOC: Label Cardinality | Label Lifecycle | Common Mistakes to Avoid -->
- [error-handling-and-output.md](./references/error-handling-and-output.md) — Errors, output, colors
  <!-- TOC: Error Handling | Output Formats | Colors Reference -->
- **AGENT_OPERATIONS.md** — Orchestrator workflow context

Scripts emit only `[OK/ERROR] name - summary` to stdout; verbose output goes to `docs_dev/reports/`.
