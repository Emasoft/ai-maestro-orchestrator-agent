# ai-maestro-orchestrator-agent — plugin instructions

## Memory

This plugin uses the GLOBAL, janitor-hosted wiki-memory system — it ships **no
memory skills of its own**. Recall/write/update via the global
`janitor-memory-recall` / `janitor-memory-write` / `janitor-memory-update`
skills, governed by the `~/.claude/rules/markdown-memory-recall.md` rule (the
janitor installs that rule every session, and it carries the full proactive
contract: recall-before-acting, write/update-after-solving, maintain-the-
project-wikimem, and scope routing private→LOCAL / project-shared→PROJECT /
cross-project→USER, unsure→LOCAL).

The orchestrator (AMOA) role adds these obligations on top of the generic
contract — they are NOT covered by the global rule:

1. **Recall before task dispatch.** Before assigning a module/task to an
   implementer, recall with the task's SYMPTOM vocabulary ("have we hit this
   before?"). Surface the top matching notes to the assignee **inside the
   assignment message / task-requirements-document** so the implementer starts
   from the prior lessons, not from zero.
2. **Recall before reassignment or escalation.** A stalled or failed task may
   match a known gotcha — recall the failure symptom before burning an
   escalation on a problem a past session already solved.
3. **Write coordination gotchas when learned.** After resolving a coordination
   failure (agent misunderstanding, label/kanban drift, polling blind spot,
   handoff loss), capture it — one fact per note, symptom-indexed `description`,
   answer in the body.
4. **Never block on the binary.** `memgrep` missing is never a blocker; recall
   degrades to a grep fallback.

When recalling from a shell, build `ROOTS` as a **zsh-portable array** (the
old space-joined-string form returns 0 results silently on zsh):

```bash
ROOTS=(); for d in "$LOCAL_MEM" "$PROJECT_MEM" "$USER_MEM"; do [ -d "$d" ] && ROOTS+=("$d"); done
memgrep recall "$SYMPTOM" "${ROOTS[@]}"
```
