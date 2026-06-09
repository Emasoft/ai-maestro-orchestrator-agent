# Markdown memory — ORCHESTRATOR recall/write protocol

The harness `# Memory` directive (injected each session) tells you how to
**WRITE** memories. This rule is the missing half for the **ORCHESTRATOR
(AMOA)** role: how to **RECALL** them, the **discipline** that makes recall
work, and the **tool** (`memgrep`) that powers it. Together they are "the
memory system": authoring (directive + `orchestrator-memory-write`) + recall
(this rule + `orchestrator-memory-recall`) + the search tool (memgrep) + the
note corpus.

## The one law that makes memory work: index by the QUESTION, not the answer

A memory is found from the SYMPTOM, not the solution. When you write a note,
its `description:` (and `title`/`tags`) MUST carry the words a future session
will have when the problem RECURS — the user's words, the error text, the
symptom — NOT the jargon of the fix.

- WRONG `description`: "OAuth creds live in the macOS keychain services".
  (Findable only if you already know the answer is "keychain".)
- RIGHT `description`: "rotator failed, had to log in manually — where are the
  creds / why did the swap fail" + the keychain fact in the BODY.

Two-hop recall: a symptom query lands you on the note; the note's BODY gives
the answer. The `description` is the load-bearing surface — `memgrep recall`
ranks on `description + title + tags` ONLY (the `metadata.type` taxonomy does
NOT affect ranking). Put symptom vocabulary in `description`; put the answer
in the body.

## Recall BEFORE acting (the protocol)

Before debugging a recurring problem, making a design decision, dispatching a
task, or acting on a recurring alert, RECALL first — "have we hit this
before?". Cheap, and it's the whole point of having a memory.

```bash
# memdir is the harness per-project memory dir:
MEMDIR="$HOME/.claude/projects/<project-slug>/memory"   # slug = project path, dashed
SYMPTOM="the user's words / the error / the symptom"     # NOT the answer's jargon

if command -v memgrep >/dev/null 2>&1; then
  memgrep recall "$SYMPTOM" "$MEMDIR"      # notes ranked best-first as: path — description
else
  grep -rliE "$SYMPTOM" "$MEMDIR"          # fallback: plain grep, degrade-not-break
fi
```

Read the top 1-3 notes the recall returns; the answer is in their bodies. If
recall returns nothing, the memory doesn't exist yet — consider writing one
after you solve the problem (per the `# Memory` directive and the
`orchestrator-memory-write` skill).

## ORCHESTRATOR-specific obligations (when recall/write fire in YOUR loop)

The generic protocol above applies to every agent. As the **team-layer
ORCHESTRATOR**, you additionally:

1. **Recall before task dispatch.** Before assigning a module/task to an
   implementer, recall with the task's symptom vocabulary ("have we hit this
   before?"). Surface the top notes to the assignee inside the
   task-requirements-document / assignment message so the implementer starts
   with the prior lessons, not from zero.
2. **Recall before reassignment or escalation.** A stalled or failed task may
   match a known gotcha — recall the failure symptom before burning an
   escalation on a problem a past session already solved.
3. **Write coordination gotchas when learned.** After resolving a
   coordination failure (agent misunderstanding, label/kanban drift, polling
   blind spot, handoff loss), capture it with `orchestrator-memory-write` —
   one fact per note, symptom-indexed description.
4. **Never block on the binary.** memgrep missing is NEVER a blocker: the
   grep fallback runs instead. Recall degrades, never breaks.

## memgrep — the recall engine

`memgrep` is `rg` for markdown (gitignore-aware tree walk, per-line regex,
markdown-structural filters, boolean `--where`, link semijoin, and the memory
subcommands `recall`/`find`/`index`/`fact`). Its teaching doc is
`tools/memgrep/SKILL.md` in `ai-maestro-janitor`.

- **Availability:** memgrep is a Rust binary. If `command -v memgrep` is
  empty, install it once:
  `cargo install --path <…>/ai-maestro-janitor/tools/memgrep` (puts it on
  `~/.cargo/bin`). Until then, the plain-`grep` fallback works on note
  frontmatter + bodies — recall degrades, never breaks.
- **recall** `memgrep recall "SYMPTOM" <memdir>` — symptom-ranked notes,
  precision-first (surface matches suppress body-only matches unless nothing
  matched the surface), printed `path — description`, best first. Useful
  flags: `--sort score|ocd|lmd`, `--order asc|desc`, `--since`/`--until`
  (over `--date-field ocd|lmd`), `--top N`, `--no-notes`, `--full-notes`.
- **find** `memgrep find "+must -exclude optional" <memdir>` — note-level
  `+`/`-`/wildcard/phrase keyword search (NOT line grep); `--only-notes`
  searches only the resolved `[^N]` lessons.
- **index/reindex** — builds the optional `.memgrep/index.db` SQLite sidecar
  (gitignored); recall auto-uses it when fresh.

## Read-the-notes rule — a memory's lessons are part of the memory

When you read ANY memory, you MUST also read **all the notes/lessons attached
to it** — every `[^N]` footnote reference and the `## Notes and lessons
learned` entries they point to. Reading a memory's facts without its lessons
is incomplete: the lessons are *why* the facts are the way they are and *what
errors not to repeat*. This is FREE — memgrep auto-resolves footnotes on
`recall` and `find` and APPENDS each returned note's lessons; one call yields
the facts AND every linked WHY.

## The note format (recall-relevant fields)

The `# Memory` directive is the authoring source-of-truth. On disk, notes are:

```yaml
---
name: <kebab-slug>                 # == filename stem
description: "<symptom surface — the load-bearing recall field>"
metadata:
  node_type: memory
  type: user | feedback | project | reference
---
<body: the one fact; for feedback/project add **Why:** and **How to apply:**>
```

`MEMORY.md` is the human index (`- [Title](file.md) — hook`, one line per
note) loaded each session. Recall does not need the index — it scans the
notes directly.

## Correcting a memory — the 2-step non-destructive protocol

When a new discovery CONTRADICTS an existing memory: (1) **clean the fact in
place** — the body is always the current truth; (2) **demote the error to a
lesson** — record the WHY of the wrong belief as a `[^N]` entry under
`## Notes and lessons learned` at the bottom of the page, with `[ocd:… lmd:…]`
dates. The fact is corrected, the error is never deleted — it becomes the
guardrail against the next repeat. See `orchestrator-memory-write`.

## Evaluating / improving the system: the dual-test method

- **Test A — cold-recall:** simulate a session with NO prior recollection;
  build the query ONLY from the symptom/user's words, never the answer's
  jargon. Tests "is the right note findable from the symptom?".
- **Test B — write-then-recall:** author a note, then retrieve it. Tests the
  round-trip.

**Contamination warning:** after you WRITE a note you are biased toward its
wording — your own cold-recall is no longer cold. Do cold-recall from a clean
framing, or have the symptom come from the user verbatim.

## Why this rule exists

The memory system has a recall engine (memgrep), a live note corpus, and the
harness authoring directive — but without a durable role rule, a fresh
ORCHESTRATOR session is blind to the recall half and re-derives the same
facts (architecture, gotchas, prior decisions) every time. This rule makes
"recall before acting" and "index by symptom" a standing discipline, with a
tool command that degrades to grep when the binary isn't present.
