---
name: orchestrator-memory-write
description: "Use when capturing a durable, reusable fact as a markdown memory note so a future session recalls it from the SYMPTOM. Trigger after solving a non-trivial coordination gotcha, learning a project constraint not derivable from code, or when the user says 'remember this', 'save a memory', 'capture this gotcha'. Writes a schema-valid note with a symptom-indexed description plus the MEMORY.md index line. Loaded by ai-maestro-orchestrator-agent-main-agent"
license: Apache-2.0
compatibility: No external dependencies (stdlib helper script).
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: true
---

# Orchestrator memory-write

## Overview

Capture ONE durable fact as a memory note so a future session — which will
have the SYMPTOM, not the answer — can recall it. The load-bearing decision
is the `description`: it MUST carry the words the problem will present with
(the user's words, the error, the symptom), because recall ranks on
`description` (+ `title` + `tags`). Put the symptom in `description`; put the
answer in the body.

Only capture what is NON-OBVIOUS and reusable: coordination gotchas,
constraints not in the code, confirmed preferences, hard-won debugging facts.
Do NOT capture what the repo already records (code structure, git history,
CLAUDE.md) or what only matters to the current conversation. Full protocol:
[rules/memory-protocol.md](../../rules/memory-protocol.md).

## Prerequisites

None. The helper script is stdlib-only.

## Instructions

1. Check for an existing note that already covers the fact (update it rather
   than duplicate) — run `orchestrator-memory-recall` with the symptom first.
2. Choose `type` ∈ `user | feedback | project | reference` and a kebab slug.
3. Write the note + index line via the helper:

   ```bash
   uv run --script "${CLAUDE_PLUGIN_ROOT}/scripts/amoa_memory.py" write \
     --type project \
     --slug kanban-label-cardinality \
     --description "assign label rejected / agent kept re-adding duplicate status labels" \
     --body "Exactly one status:* label per issue. Remove the old status label before adding the new one, or gh issue edit silently accumulates both. **Why:** cardinality rule in amoa-label-taxonomy. **How to apply:** always --remove-label before --add-label."
   ```

   The helper validates the schema (name/description/metadata.node_type/type),
   writes `<type>_<slug>.md` atomically, and appends the `MEMORY.md` index
   line. It REFUSES to overwrite an existing note unless `--update` is passed.
4. Correcting an existing memory (new discovery contradicts it) — 2-step
   non-destructive protocol: (1) clean the fact in place (the body is the
   current truth); (2) demote the error to a dated `[^N]` lesson under
   `## Notes and lessons learned` with the WHY. Re-run with `--update` after
   editing, or edit the note file directly.
5. Sanity-check: would a future session, having only the SYMPTOM, find this
   note by searching `description`? If the description reads like the
   *answer*, rewrite it to read like the *question*.

Copy this checklist and track your progress:

- [ ] Recall first — does a note already cover this? (update, don't duplicate)
- [ ] Write note via helper with SYMPTOM-indexed description
- [ ] Sanity-check the description reads like the question, not the answer

## Output

One note file + one MEMORY.md index line. The helper prints the note path.
Report the path and the one-line description; do NOT echo the whole note back
into the conversation.

## Error Handling

- Existing note with the same name → helper exits 3 (`refused`); re-run with
  `--update` only after deciding update-vs-new-note consciously.
- Invalid type/slug/empty description or body → helper exits 2 with the
  reason on stderr; fix the argument and re-run.

## Examples

**Input:** after fixing a flaky polling bug: `write --type project --slug polling-overdue-false-positive --description "polling reminder fired but agents were fine / overdue warning wrong" --body "..."`
**Output:** the helper prints the new note path (a `project_polling-overdue-false-positive.md` file inside the memory dir) and appends its MEMORY.md line

```text
User: remember this — implementers must ACK within 30 min or we reassign
User: save a memory about the gh project scope failure we just fixed
User: capture this gotcha for next time
```

## Scope

ONLY authors/updates memory notes + the MEMORY.md index. Does NOT recall
(use `orchestrator-memory-recall`). One fact per note. Symptom-indexed
description is mandatory — it is what makes the note recallable.

## Resources

- [rules/memory-protocol.md](../../rules/memory-protocol.md) — the protocol
  (the one law, schema, lessons-learned conventions, dual-test method)
- `scripts/amoa_memory.py` — the recall/write helper this skill runs
- `orchestrator-memory-recall` — the RECALL side (find a note before you
  duplicate or correct it)
