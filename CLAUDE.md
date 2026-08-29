# ai-maestro-orchestrator-agent — plugin instructions

## GitHub authorship — PRRD G1.2 (binds every skill, command, and spawned sub-agent)

Every agent on this host writes to GitHub through ONE shared human-owner
identity, so a reader cannot tell which agent authored what. Therefore: **the
first line of every issue, comment, PR, review, or release note you post
begins with a one-line self-identification** naming the agent/role/plugin that
wrote it. The wording comes from G1.2 itself — a second wording is a defect,
not a style choice:

```
_Posted by the Claude responsible for the **<plugin-or-role>** project (via the shared owner gh auth)._
```

**Keep the `<plugin-or-role>` placeholder in any template another agent
copies** — a remote implementer working on a different project who pastes a
line naming *this* plugin has just filed a false attribution, produced by the
rule whose whole purpose is truthful attribution. Fill the placeholder in only
where the poster really is this plugin posting as itself; that filled-in form
(with the `ORCHESTRATOR role` clause) is one instantiation of G1.2, never the
rule.

Two constraints on that line, both load-bearing:

1. **No `@` sigil, ever.** A bare `@name` outside a code span pages a real
   account, and our governance vocabulary collides with GitHub's username
   namespace by construction (`orchestrator`, `manager`, `maintainer` are all
   real accounts registered years ago). Name the role in plain words. The
   mechanical guard is `tests/unit/test_no_github_mentions.py`; it scans
   published text only, and its ALLOWED set is not the fix when it reddens.
2. **A template is copied OUT of its fence.** Backticks neutralize a mention
   in prose but not in a template body an agent pastes into a real comment, so
   a template carries no `@` at all — use `@<username>` (provably inert: a
   username cannot begin with `<`) when a placeholder is genuinely needed.

This contract covers every skill in this plugin and every sub-agent it spawns;
the shipped templates model the line in their concrete examples so an agent
copying one inherits it.

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
