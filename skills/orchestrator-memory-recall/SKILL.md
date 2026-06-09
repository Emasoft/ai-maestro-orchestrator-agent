---
name: orchestrator-memory-recall
description: "Use when recalling durable project memories from a SYMPTOM before dispatching a task, debugging a recurring problem, or escalating. Trigger with 'have we hit this before', 'recall memories about X', 'did we already solve this', or before re-deriving architecture/gotchas. Searches markdown memory notes with memgrep, degrading to a grep fallback when memgrep is absent. Loaded by ai-maestro-orchestrator-agent-main-agent"
license: Apache-2.0
compatibility: Optional memgrep binary (cargo install); degrades to grep fallback without it.
metadata:
  author: Emasoft
  version: 1.0.0
user-invocable: true
---

# Orchestrator memory-recall

## Overview

Recall is the FIRST step before dispatching a task, debugging a recurring
problem, making a design decision, or escalating — "have we hit this before?".
It searches the project's curated markdown memory notes (the `memory/` dir the
harness maintains) and returns the notes whose `description`/`title`/`tags`
best match your SYMPTOM. The answer is in the matched note's body. This is
distinct from conversation/transcript search: it recalls *curated,
symptom-indexed notes*, not raw chat history.

**The one law:** query with the SYMPTOM — the user's words, the error text,
the problem — NOT the answer's jargon. Full protocol:
[rules/memory-protocol.md](../../rules/memory-protocol.md).

## Prerequisites

None hard. `memgrep` (Rust binary) gives ranked recall when present; without
it the skill degrades to a plain-text fallback — recall degrades, never
breaks. Install once: `cargo install --path <ai-maestro-janitor>/tools/memgrep`.

## Instructions

1. Build a SYMPTOM query from the user's words / the error / the problem
   (never the answer's jargon).
2. Run the helper (it resolves the harness per-project memory dir, uses
   memgrep when installed, falls back otherwise):

   ```bash
   uv run --script "${CLAUDE_PLUGIN_ROOT}/scripts/amoa_memory.py" recall "$SYMPTOM"
   ```

   Equivalent inline shell (when the helper is unavailable):

   ```bash
   MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
   [ -d "$MEMDIR" ] || MEMDIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/memory"
   if command -v memgrep >/dev/null 2>&1; then
     memgrep recall "$SYMPTOM" "$MEMDIR"
   else
     grep -rliE "$SYMPTOM" "$MEMDIR" 2>/dev/null
   fi
   ```

3. Read the top 1-3 notes returned — the fact you need is in their bodies,
   and each note's `[^N]` lessons are part of the memory (read them too).
4. ORCHESTRATOR wiring: when recalling before a task dispatch, surface the
   top matching notes to the assignee inside the assignment message /
   task-requirements-document so the implementer starts from prior lessons.
5. If recall returns nothing, the memory doesn't exist yet — solve the
   problem, then capture it with `orchestrator-memory-write`.

Copy this checklist and track your progress:

- [ ] Build SYMPTOM query (user's/error's words, not the fix's jargon)
- [ ] Run recall via helper script (memgrep or fallback)
- [ ] Read top notes WITH their lessons; surface to assignee if dispatching

## Output

A short ranked list of `path — description` lines, best first. Read the top
few; do NOT dump full note bodies into the conversation — open the one you
need. Zero matches prints nothing and is a valid result, not an error.

## Error Handling

- memgrep absent → automatic fallback (surface-match ranking over
  description/title/tags, then body-only matches). Never a blocker.
- Memory dir absent → empty result ("no memories yet"), exit 0.
- Helper script unavailable → use the inline shell from step 2.

## Examples

**Input:** "the implementer keeps failing the same kanban label step — have we hit this before?"
**Output:** `…/memory/project_kanban-label-cardinality.md — assign label rejected / agent kept re-adding duplicate status labels` (read that note before re-debugging)

```text
User: recall what we decided about polling intervals
User: did we already solve the replacement-handoff context loss?
User: have we hit this gh project scope error before?
```

## Scope

ONLY searches + surfaces existing memory notes (read-only). Does NOT write
notes (use `orchestrator-memory-write`). Degrades to the fallback when
memgrep is absent; never blocks on a missing binary.

## Resources

- [rules/memory-protocol.md](../../rules/memory-protocol.md) — the recall
  protocol (the one law, the schema, the read-the-notes rule, dual-test method)
- `scripts/amoa_memory.py` — the recall/write helper this skill runs
- `orchestrator-memory-write` — the WRITE side (authoring + correction protocol)
