---
name: amoa-label-taxonomy
description: "Use when applying GitHub labels. Trigger with label query or assignment requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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

GitHub label taxonomy for AI Maestro orchestration. Format: `<category>:<value>` with cardinality rules.

## Prerequisites

GitHub CLI (`gh`) configured; AGENT_OPERATIONS.md for context.

## Instructions

1. Identify label category and check cardinality in usage-rules.md
2. If updating, remove conflicting labels first (`assign:*`, `status:*`)
3. Apply via `gh issue edit` and verify
4. Every issue MUST have: `status:*`, `priority:*`, `type:*`

Copy this checklist and track your progress:

- [ ] Check cardinality rules. See: [references/usage-rules.md](./references/usage-rules.md)
  <!-- TOC: Label Cardinality | Label Lifecycle | Common Mistakes to Avoid -->
- [ ] Remove conflicting labels, apply new label via `gh` CLI
- [ ] Verify label applied correctly

Categories: `assign:`(0-1) `status:`(1) `priority:`(1) `type:`(1) `component:`(1+) `effort:`(1) `platform:`(0+) `toolchain:`(0+) `review:`(0-1). Details: [label-categories-detailed.md](./references/label-categories-detailed.md)
<!-- TOC: Assignment Labels (`assign:*`) | Rules | Assignment Authority | Conflict Resolution | Status Labels (`status:*`) | Rules | Status Workflow | Priority Labels (`priority:*`) | Rules | Type Labels (`type:*`) | Rules | Component Labels (`component:*`) | Rules | Effort Labels (`effort:*`) | Rules | Platform Labels (`platform:*`) | Rules | Toolchain Labels (`toolchain:*`) | Rules | Review Labels (`review:*`) | Rules -->

Kanban: `backlog`→`todo`→`in-progress`→`ai-review`→`human-review`→`merge-release`→`done` (+`blocked`). CLI ref: [cli-commands.md](./references/cli-commands.md)
<!-- TOC: Create Labels | Query Labels | Update Labels | Validate Label Cardinality -->

## Output

Confirmations, query tables, validation reports. See: [references/error-handling-and-output.md](./references/error-handling-and-output.md)
<!-- TOC: Error Handling | Output Formats | Colors Reference -->

## Examples

See: [references/examples.md](./references/examples.md)
<!-- TOC: Example 1: Assign Task to Agent | Example 2: Update Status During Workflow | Example 3: Query Issues by Multiple Labels | Example 4: Validate Label Cardinality -->

**Input:** `gh issue edit 42 --remove-label "assign:implementer-1" --add-label "assign:implementer-2"`
**Output:** `Updated issue #42`

## Error Handling

See: [references/error-handling-and-output.md](./references/error-handling-and-output.md)
<!-- TOC: Error Handling | Output Formats | Colors Reference -->

## Resources

- [label-categories-detailed.md](./references/label-categories-detailed.md)
- [cli-commands.md](./references/cli-commands.md)
- [examples.md](./references/examples.md)
- [usage-rules.md](./references/usage-rules.md)
- [error-handling-and-output.md](./references/error-handling-and-output.md)
