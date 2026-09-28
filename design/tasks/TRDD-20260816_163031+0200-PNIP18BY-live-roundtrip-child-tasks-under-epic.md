---
trdd-id: PNIP18BY
title: Verify on a live server that implementation child tasks read back under the AI-Maestro epic
column: backburner
scope: project
project-id: ai-maestro-orchestrator-agent
created: 2026-08-16T16:30:31+0200
updated: 2026-09-28T22:04:21+0200
current-owner: ai-maestro-orchestrator-agent
task-type: feature
approval-tier: 0
created-by: ai-maestro-orchestrator-agent
relevant-rules: []
external-refs: [orch#26, architect#7, ai-maestro#77, TRDD-6B3K7S69]
npt: []
eht: []
blocked-by: []
release-via: none
review-after: 2026-09-15
---

# Verify on a live server that implementation child tasks read back under the AI-Maestro epic

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-16

S Split out of TRDD-6B3K7S69 on 2026-08-16. That card landed the READ/PARSE half of orch#26
(`extract_aimaestro_task_id`, `shared/amoa_design_handoff.py:25`, commit `45e409e`) plus the
attach PROCEDURE doc, and every dev-session-runnable acceptance box was checked. Its one
remaining box was a DEPLOYMENT-time check that cannot run from a dev checkout at all.

C Carrying that box on the parent left a completed card permanently one box short — the
completion gate would have had to be either violated (retro-ticked) or left standing forever
on work nobody can do here. Splitting is the honest third option: the parent closes on what it
actually delivered, and the live check stays tracked instead of quietly disappearing.

### Attempt log — do NOT read the untouched boxes as "nobody tried"
- **2026-08-29 — UNPERFORMABLE, not merely unperformed. The server went hung → deliberately
  stopped, and the two observations below disagree because the state changed between them — that
  disagreement is the finding, so do not collapse them into one.**
  - *Peer-reported (ai-maestro session, ~15:05+0200, NOT verified by this card's author):* server
    **bound but not answering** — `pm2 jlist` online, `lsof -nP -iTCP:23000 -sTCP:LISTEN` showing
    node pid 21004 LISTENING on `*:23000`, yet `GET /api/sessions` → HTTP 000 after a full 15.0 s
    on two probes (5 s and 15 s).
  - *First-hand, this card's author, 2026-08-29T15:12:26+0200:* **nothing bound at all.**
    `curl --max-time 15 http://localhost:23000/api/sessions` → `000` in **0.000334 s**, `curl_exit=7`
    ("Couldn't connect … after 0 ms") — a REFUSED connection, not a hang. `lsof … -sTCP:LISTEN` on
    23000 returns empty, pid 21004 no longer exists, and `pm2 jlist` reports `ai-maestro`
    **stopped**.
  - *Why it stopped — do NOT read this as a crash-loop.* `pm2 jlist` further reports
    `exit_code: 130` (128+2 = **SIGINT**, i.e. deliberately interrupted), `unstable_restarts: 0`,
    and `created_at`/`pm_uptime` = 2026-08-28T21:44:15, **the previous day**. So the
    `restart_time: 9` counter is CUMULATIVE since yesterday, not nine restarts in the seven
    minutes between the two observations. An earlier draft of this entry read that counter as a
    rate and called the server "flapping"; that was wrong and is corrected here. The evidence
    supports exactly one reading: it was hung, then somebody stopped it.
  - No AMCOS-spawned agent binding was available on the host under either observation. Nothing was
    ticked. **A timeout or a refusal on the read-back step is strictly WORSE evidence than no
    attempt** — both are indistinguishable from "the child was not linked" — so the round-trip
    could only have produced a result this card forbids. `review-after` stands.
  - **Do not treat "the server was up" as sufficient at next attempt.** The load-bearing fact is
    not the restart count — it is that at ~15:05 the process was **online and LISTENING while not
    answering**, so every liveness proxy (`pm2 status`, a LISTEN check, a successful TCP connect)
    read healthy on a server that could not complete a request. The precondition is therefore that
    `GET /api/sessions` ANSWERS, checked immediately before AND again after the round-trip, so a
    stop or a wedge mid-run cannot be mistaken for a linkage failure.

- **2026-08-29T22:59:50+0200 — PARKED WITH A NAMED REASON, which supersedes "unperformable today".**
  Re-measured first-hand: `curl --max-time 15 http://localhost:23000/api/sessions` → `000` in
  0.000229 s, `curl_exit=7` (REFUSED); nothing LISTENING on 23000; `pm2 jlist` → `ai-maestro`
  stopped, `exit_code: 130`, `unstable_restarts: 0`. Then asked the ai-maestro session, which
  replied, PARAPHRASING ITS OWN HANDOFF, **"Server STOPPED by owner directive — do NOT restart"**
  — **and its own author has since confirmed there is NO user artifact behind it.** Asked for the
  path and verbatim line, that session answered: `~/ai-maestro/.janitor/state/agent-handoff.md:71`,
  a file that is `git check-ignore`-positive — untracked, no history, written by that session
  itself. The sentence is rev 41 carried forward from rev 40, authored by a PREVIOUS session of
  the same agent, injected into its context by the SessionStart hook and relayed to us as a
  directive. Its author's words: *"a paraphrase of a paraphrase … Restore nothing on my account
  — the weaker wording is the true one."* So the DIRECTIVE is peer-asserted, not verified;
  `exit_code: 130` proves only that SOMEONE sent SIGINT, never who or why. Cite the 130, never
  the directive. **Do not re-derive this from the filesystem** — one grep here was structurally
  incapable of hitting (`~/.claude/projects/*/[a-z]*/agent-handoff.md` cannot match
  `<project>/.janitor/state/…`: wrong depth, and `[a-z]*` excludes a leading dot by construction),
  so its silence was guaranteed rather than evidential. The answer came from ASKING THE AUTHOR,
  which no search could have produced, because the finding was that the source is weaker than the
  claim. What IS first-hand: a peer that
  owns that service asked us not to restart it, and it is another team's service — sufficient to
  decline, insufficient to assert. Earlier wording here, on orch#24 and in commit `86b8c81` said
  "owner directive" flatly; that overstated the evidence and is corrected here rather than there
  (a commit message cannot be rewritten without rewriting history).
  in as many words, and that it will not restart it or ask the owner to on our behalf.
  So the blocker is a DECISION, not a fault — nobody should keep re-diagnosing this as breakage.
  Two facts that session supplied, to save the next attempt a debugging hour:
  - **A restart does NOT rebuild.** `server.mjs` and `lib/*.mjs` load at runtime and go live on
    `pm2 restart` alone; `lib/*.ts`, `app/`, `services/`, `components/` are bundled into `.next`
    and need `yarn build` first. If the round-trip depends on route behaviour, **verify by effect,
    not by commit**.
  - **There is no `/api/health`.** `/api/v1/health`, `/api/agents/health` and `/api/hosts/health`
    exist but answer different questions, so `GET /api/sessions` remains the probe.

### NEXT ACTION
Nothing runnable from a dev session. When a live AI-Maestro server and an AMCOS-spawned agent
binding are available: send a design-handoff carrying `content.aimaestro_task_id`, create an
implementation child with `amp-kanban-create-task "<child>" --parent "$EPIC"`, then read the
epic back and assert the child appears under it.

### What proves this card
The child task, created with `--parent "$EPIC"` from an id parsed out of a real design-handoff,
is returned as a child of that epic when the epic is read back from the live server. Anything
short of a real server round-trip does not close this card — a mocked or replayed response
proves nothing about the traceability chain this exists to verify.

### Load-bearing facts inherited from 6B3K7S69 (do not re-derive)
- Key path is `content.aimaestro_task_id`, top-level of `content`, NOT under `content.data`.
  The SHIPPED v2.11.0 template wins over architect#7's original proposal.
- The id is an opaque string (e.g. `PVTI_laDOABcd1234`); do not assume a UUID shape.
- Attach only via the frozen verb `amp-kanban-create-task ... --parent` — never a raw
  `/api/*` call (R23, Plugin Abstraction Principle).
- Not blocked by ai-maestro#46: identity resolves via `AGENT_WORK_DIR/$PWD → name → uuid`;
  the colliding address was display-only (ai-maestro#77, 2026-07-23).
FRESH CHECK 2026-09-28 21:59 — server :23000 is UP (curl 200) for the first time this session; AMP identity probe STILL FAILS: 'AMP identity could not be resolved for this session (36 agents registered). This session is not bound to any agent, so an amp-* command here would have to ASSERT an identity rather than prove one.' The identity blocker (36 registered agents, none is this dev session) persists independently of server state — the two blockers were never the same blocker. Card remains backburner/parked: unperformable FROM THIS SESSION (identity unbound). DELEGATION ROUTE UNTESTED, and round-7 review flags the wording: the box text ('verify on a live server that implementation child tasks read back under the AI-Maestro epic') is session-agnostic on its face — whether its intent requires the ORCHESTRATOR role-plugin's own roundtrip (the parent TRDD-6B3K7S69 split rationale reading) or tolerates a bound peer running the read-back is UNDECIDED here. Next touch should either test delegation (ask ai-maestro-00 to run the read-back) or re-derive the box's intent from the parent card. Also: review-after 2026-09-15 is expired — a trdd-drift run may resurface this card; that re-surfacing is expected and should not re-litigate the park.
DELEGATION PROBE RESULT 2026-09-28 ~22:20 — ai-maestro-00 (a bound-name peer session, though itself AMP-unbound) ran the read-back three ways, verbatim: (1) amp-kanban-list → exit 1, identity refused BY DESIGN, the guard explicitly rejects --id (would spoof a real agent); (2) AMP_HOST=1 → exit 1 'Could not determine team ID' — its host has ZERO teams (~/.aimaestro/teams/teams.json teams:[]), no AI-Maestro epic exists there; (3) AMP_HOST=1 --team nil-uuid → exit 1 HTTP 401, no bearer token. ANSWER TO THE ROUND-7 QUESTION: the box does NOT tolerate a foreign reader — identity binding is enforced, not bypassable, and the only sanctioned routes are a server-spawned session with injected AIM_AGENT_ID or an authenticated host token. The acceptance box requires exactly the deployment-time condition the parent split predicted: a live server AND a spawned AMOA session. Both probes (mine + the peer's) are now recorded; the card is decided, not merely parked — it waits on infrastructure, and no further session-level experiment can close it.

## Why this is a standalone card and NOT an `eht:` of 6B3K7S69

`~/.claude/rules/trdd-design-tasks.md` §9 defines an EHT as a post-condition whose parent
**cannot reach `complete` until every EHT is terminal**. Filing this as an EHT would therefore
reproduce the exact block the split exists to remove — the parent would stay open on a check
that needs infrastructure this repo does not have. It is filed as a derived standalone card
(`created-by: 6B3K7S69`) so the lineage is greppable while the parent closes on its own merits.

## Acceptance criteria
- [ ] A design-handoff carrying `content.aimaestro_task_id` is received from a live architect.
- [ ] An implementation child is created with `amp-kanban-create-task --parent "$EPIC"`.
- [ ] Reading the epic back from the live server returns that child under it.
- [ ] The absence case still behaves as today (no epic id → unlinked breakdown, no error).
      **SPLIT 2026-08-29 — half of this is already proven, half is not unit-testable at all.**
      *Proven, no server and no AMP identity needed:* the PARSE contract. `test_absent_key_returns_none`
      and `test_null_value_returns_none` (`tests/unit/test_amoa_design_handoff.py:53,59`) assert that a
      handoff missing the key, and one carrying an explicit `null`, both return `None` rather than
      raising. Both pass in the 212-test suite.
      *NOT proven, and NOT closable by a unit test:* the "→ unlinked breakdown, no error" half.
      **CORRECTION 2026-08-29T23:5x — an earlier revision of this line claimed `extract_aimaestro_task_id`
      "has no production caller". THAT WAS FALSE.** The consumer is documented and shipped:
      `skills/amoa-kanban-management/references/kanban-procedures.md:67-72` (PROCEDURE 5) imports it and
      reads the epic, and `skills/amoa-kanban-management/SKILL.md:74` carries the same in its TOC —
      including the absence branch verbatim: *"When the epic id is None, create the children unparented —
      no regression."* `skills/amoa-messaging-templates/references/message-templates.md:245,257,260`
      documents the wire key. So box 4's behaviour is SPECIFIED; what is missing is a RUN of it.
      *Why the false claim happened — TWO defects, multiplicative, and the second is the dangerous one:*
      the caller search was `grep -rn … | grep -v '^./tests/' | head`.
      (a) **The exclusion filter was DEAD.** `grep -rn` emitted **no `./` prefix** on any line, so the
      anchored regex `^./tests/` could never match `tests/unit/…`. Measured: 22 hits, **0** matching
      `^\./`. Seven test lines therefore survived a filter that claimed to remove them.
      (b) `head` then capped the result at 10 — and those 7 surviving test lines ate the window, so every
      `skills/` consumer fell outside it.
      **Neither alone would have hidden them.** With a working filter the consumers sit inside the first
      10; without `head` they print regardless. So the guard "don't pipe to `head`" is NOT sufficient —
      a prefix-anchored `grep -v` that silently matches nothing looks exactly like one that worked, and
      it is what spent the truncation window. Check both: capture to a file and inspect it
      (`~/.claude/rules`: never measure output from a truncated result), and verify any anchored filter
      actually matches the emitter's real output shape. `git grep` (no pager, all tracked types, no
      prefix ambiguity) surfaced the consumers immediately.
      The BOX-4 VERDICT IS UNCHANGED and now rests on the right reason: the consumer is a PROCEDURE an
      agent executes against a live server, not Python a test can call, so the behaviour is observable
      only in the live round-trip, exactly like boxes 1–3. Do NOT tick this box on the two passing tests:
      they prove the function returns `None`, never that a breakdown proceeds unlinked without error.

## Notes and lessons learned
