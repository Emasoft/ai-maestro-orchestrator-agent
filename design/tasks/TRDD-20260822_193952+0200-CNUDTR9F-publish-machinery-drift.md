---
trdd-id: CNUDTR9F
title: Publish machinery drift — frozen CPV pin, unregenerated pre-push hook, dead install path, false header
column: publish
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-22T19:39:52+0200
updated: 2026-08-25T17:26:00+0200
current-owner: ai-maestro-orchestrator-agent
created-by: ai-maestro-orchestrator-agent
task-type: infra
approval-tier: 2
relevant-rules: []
external-refs: [ai-maestro#142, ai-maestro TRDD-6WTIA4ZT, CPV#169]
npt: []
eht: []
blocked-by: []
release-via: publish
---

# Publish machinery drift — frozen CPV pin, unregenerated pre-push hook, dead install path, false header

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-25

**All four findings FIXED and verified.** USER approved start 2026-08-25; hub (ai-maestro
session) approved the sequencing. Commits: 13af808 (F1 — pin v2.159.0→v5.8.0 at all 5 sites;
v5.8.0 = latest, entrypoints verified against its tree), fde32fb (F2/F3/F4 — git-hooks/pre-push
replaced VERBATIM from CPV v5.8.0 `generate_plugin_repo.py::gen_pre_push_hook` (mechanical
extraction, no hand-patch); core.hooksPath→git-hooks; false-header .githooks/pre-push removed;
install_hook() now sets hooksPath only — the dead .git/hooks copy is gone; docs swept).

**Acceptance, measured:** c1 grep-count 5/0 (new/old pin) · c2 wholesale template live ·
c3 install_hook writes only what git reads · c4 lying header gone (residual template-wording
imprecision filed upstream as CPV#214; the fail-open trufflehog edge on `HEAD:refs/heads/x`
push shapes filed as CPV#213) · c5 behavioural: feature-branch dry-run push → trufflehog
scanned base=origin/main..HEAD (14 chunks) → ALLOWED exit 0; main dry-run push → BLOCKED at
G0 (no publish ancestry) exit 1. ruff clean, pytest 205/205, CPV v5.8.0 `--strict` preview on
this tree: 0 CRITICAL / 0 MAJOR / 0 MINOR / 0 NIT (30 WARNING, non-blocking) — the feared
3-major debt avalanche did not materialize.

**NEXT ACTION:** run `uv run python scripts/publish.py --patch` (release-via: publish); on
green Release CI → `published`, archive as itself.

**Do NOT hand-patch the vendored hook.** The correct adoption replaces it wholesale from the
CPV v5.4.0+ template; a hand-patch turns the real adoption into a merge conflict against a file
nobody can diff cleanly (hub's caution, accepted).

---

## Why this exists

Discovered 2026-08-22 while answering a hub claim that this repo had not adopted the fleet
"branch-aware pre-push" fix. The hub's *symptom* was right and its *prescribed fix* was wrong;
verifying which was which surfaced four separate defects in the publish machinery. Each is
independently true and each outlives the others, so they are listed separately rather than as
one "update publish.py" blob.

Every fact below was measured first-hand on this tree, and independently re-measured by the hub
session against the same tree. Where our numbers disagreed, the hub's were right — see F1.

## The four findings

### F1 — CPV pin is FROZEN, ~3 majors stale

`scripts/publish.py` hardcodes `claude-plugins-validation@v2.159.0` in **5** places
(`grep -c` → 5; `grep -o | wc -l` → 5). CPV latest is **v5.7.1**; the branch-aware pre-push fix
landed in **v5.4.0** (`gh release list --repo Emasoft/claude-plugins-validation`).

Consequence: the `--strict` gate cannot "get stricter over time" — it is pinned. `v1.13.12`
published cleanly on 2026-08-22 against a ~3-major-old validator.

> **Self-correction, recorded because the method matters more than the number.** This TRDD's
> author first reported **4** sites. That count came from a `grep … | head -15` whose output was
> truncated at the display, not from a count — the exact failure
> `~/.claude/rules/never-tail-on-error-messages.md` warns about. The hub's `grep -c` was right.
> Count with `-c`/`-o | wc -l`; never read a total off a `head`-limited listing.

### F2 — nothing regenerates the LIVE pre-push hook

- `git config core.hooksPath` → `.githooks` — so `.githooks/pre-push` (66 lines) is the live hook.
- `grep -c '\.githooks' scripts/publish.py` → **0**. publish.py never writes that path.
- Control needle: `grep -c 'git-hooks' scripts/publish.py` → 9. The needle works; the absence is real.
- `v1.13.12` was published 2026-08-22 and did not touch the file.

Consequence: **cutting a release is a no-op for this hook.** Any adoption plan of the form
"take a newer CPV and publish" verifies nothing and would report an adoption that did not happen.

### F3 — `--install-hook` targets a path git does not read (silent no-op, reports success)

`publish.py:566` copies `git-hooks/pre-push` — a **different** directory (hyphen, not dot; 12
lines, a stub) — into `.git/hooks/pre-push`. That file **does not exist** (`ls` → No such file),
and `core.hooksPath=.githooks` means git would not read it if it did.

Consequence: `--install-hook` has silently done nothing for as long as `core.hooksPath` has been
set, **and printed a success line every time**. This is a finding in its own right: it is
orthogonal to the CPV pin and will outlive the bump. It also means "I ran --install-hook" is not
evidence that any hook was installed.

### F4 — the live hook's header is FALSE, and that is what manufactured the wrong belief

`.githooks/pre-push` lines 3-4 assert verbatim:

> `Auto-generated by scripts/publish.py. Do NOT edit by hand — every`
> `publish.py run rewrites this file from its inline template.`

There is no inline template and no rewrite (F2). The file lies about its own provenance.

**This is the reusable finding, not a footnote.** Two independent sessions read that header, took
it as mechanism, and built a fix path on it; one was about to send "and it regenerates the hook"
into an owner release ask before it was caught. A false self-describing header is worse than an
absent one: it answers the question convincingly enough that nobody greps for the write site.
A comment is a claim to verify, never evidence — and it is the one artifact no test ever reds.

Related shape already known to this project: `~/.claude/rules/cli-verify-on-path.md` (verify
behaviour, not the file you believe is running).

## What "fixed" means (acceptance)

1. `grep -c 'claude-plugins-validation@v[0-9]' scripts/publish.py` → all sites on one current
   pin, and that pin ≥ v5.4.0.
2. The live `.githooks/pre-push` is the v5.4.0+ branch-aware form, taken **wholesale from the
   template**, not hand-patched.
3. Either `--install-hook` writes the path `core.hooksPath` actually names, or it is removed.
   A flag that prints success while doing nothing is not acceptable in either direction.
4. No file in the repo claims to be auto-generated by a writer that does not write it.
5. A feature branch push is observed either succeeding (branch-aware gate) or being refused with
   the correct reason — **measured behaviourally**, never inferred from the hook's text.

## Risk

Bumping the pin lands ~3 majors of accumulated strictness in one step; expect remediation rounds
(precedent: the v1.7.0 publish surfaced 20 CRITICAL / 28 MAJOR / 104 MINOR / 98 NIT of
pre-existing debt when the gate jumped versions). Sequence the pin bump separately from the hook
replacement so a failure is attributable to one of them.

## Cross-references

- `ai-maestro#142` — CLOSED 2026-08-14; filed the side-branch symptom. Its stated cause
  ("publish.py pushes HEAD") is **not sufficient** here: under the installed hook both clauses
  bind (the hook refuses every non-publish push on any branch, AND publish.py pushes HEAD), so
  the symptom cannot discriminate the cause. Reading the hook is the only reliable method.
- `ai-maestro TRDD-6WTIA4ZT` — the hub's card carrying the same fleet finding.
- LOCAL memory `project_push-refused-publish-policy` — lesson `ATOM-XYYM-YUQO` records F1/F2/F4
  as a guardrail; its `description:` was extended so the lesson is recallable by symptom.

## Approval log

- 2026-08-25T14:01:00+0200 — USER APPROVED start (tier 2 satisfied — USER outranks MANAGER).
  `todo → dev`, self-assigned. Plan: pin bump (F1) and hook replacement (F2/F4) as SEPARATE
  commits per the Risk section; F3 fixed alongside the hook commit; acceptance measured
  behaviourally (criterion 5) via `git push --dry-run` on both a feature ref and main.
- 2026-08-25T17:26:00+0200 — dev→testing→publish. Testing evidence: ruff clean, pytest
  205/205, both behavioural probes correct, CPV v5.8.0 strict preview 0/0/0/0. Review lane
  closed under the USER's standing directive of 2026-08-25 ("complete all pending tasks and
  TRDDs — you can decide yourself"); hub approved sequencing in-session. Entering the release
  pipeline (publish.py --patch).
