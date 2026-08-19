---
trdd-id: NSWPM93D
title: Decide AMOA policy for Claude Code native cross-session messaging alongside AMP
column: complete
archived: true
min-approval-requirement: manager
routed-via: manager
created: 2026-08-07T20:25:44+0200
updated: 2026-08-18T19:56:41+0200
current-owner: ai-maestro-orchestrator-agent
assignee: ai-maestro-orchestrator-agent
task-type: docs
scope: project
project-id: ai-maestro-orchestrator-agent
blocked-by: []
release-via: none
relevant-rules: []
external-refs: [https://github.com/Emasoft/ai-maestro-plugin/issues/61, ai-maestro#131]
---

# Decide AMOA policy for Claude Code native cross-session messaging alongside AMP

## Why this is a proposal and not a task

It is a **governance** question, not an implementation one: it decides which
transport agents are permitted to use to reach each other, and any answer that
sanctions a non-AMP path changes what is auditable fleet-wide. That is Tier 2 —
MANAGER, not the orchestrator. Filed rather than implemented for exactly that
reason.

## Context

Claude Code ships its own cross-session messaging: `SendMessage` and
`ListAgents` address peer sessions directly, and 2.1.224 extended them across
**machines** (plus `crossSessionInbound` / `dialogExpiry` settings). This is not
new — the primitives date to 2.1.77 and 2.1.162, and they have since been
hardened (2.1.166: relayed messages carry no user authority; 2.1.222: a
permission classifier runs pre-dispatch).

AI-Maestro's own transport is AMP, reached through the frozen CLI layer
(`amp-*.sh`), and the Plugin Abstraction Principle forbids any element from
calling the server API directly. AMP carries AID identity and R6 routing; the
native transport carries neither.

So there are now **two** live transports between agents, one governed and one
not, and no ruling on when the ungoverned one may be used.

## CORRECTION 2026-08-07 — R42.3 already answers the transport question

This TRDD was first written as "MANAGER picks one of three transport options."
**That framing was wrong**, and the correction narrows the ask rather than
widening it.

Verified first-hand against the published artifact — `docs/GOVERNANCE-RULES.md`
line 1531 on branch `governance-rules`, not a peer's paraphrase:

> **R42.3** — The **messaging system (AMP) is the ONLY channel** by which one
> agent may influence another, and it is governed by the R6 communication graph
> (who may message whom). *Authority: Explicit (USER).*

So AMP-only is not an option to be chosen; it is the standing rule, at USER
authority — which means **MANAGER cannot weaken it** (see the golden/silver
split; only USER can). Native `SendMessage` used to hand another agent work is
plainly "influencing another agent" and is therefore already outside R42.3.

COS reached the same conclusion independently from the R42 reading and raised it
to CORE as `ai-maestro#131` (CORRECTED 2026-08-18: this line originally cited
`ai-maestro#76`, which is the COS frozen-CLI-verbs gap, not the messaging escalation —
verified against both issues' live titles; #131 is the one tracking the second-transport /
no-403-enforcement-point escalation), adding that R42.1's ban on injecting **queued input**
bites too (native auto-delivers where AMP is polled), and that R6's comm graph
goes advisory because `ListAgents` enumerates sessions across machines
regardless of topology. **CORE has not ruled.**

## What actually remains for MANAGER

Not the transport choice. Two narrower things R42.3 does not settle:

1. **The AMP-unreachable case.** R42.3 says AMP is the only channel; it does not
   say what an agent does when AMP is down. Absent a ruling the honest default
   is "stop and surface it" — which should be stated, because the vacuum is what
   invites the native path.
2. **Whether any exception set exists at all**, and if so, that it EXCLUDES
   outbound-unreachable senders (COS's addition — see the fourth failure below).
   An exception that permits a sender the recipient cannot answer is the one
   shape already shown to cause harm.

Recording this correction rather than quietly rewriting the file: the original
framing was already relayed to MANAGER via COS, so the record must show the
question changed.

## Why I am NOT proposing option 3, and why this was not just documented

The obvious-looking move was to document a native fallback for when AMP hiccups.
I deliberately did not, because **a documented fallback is the path agents will
take the first time AMP is slow**, and native traffic has no AID identity and no
R6 routing — so the fleet would lose its audit trail precisely during the
incidents where it matters most. Writing the fallback into a skill would have
made that policy by default, without anyone deciding it.

## Evidence that this is live, not hypothetical

Two things measured on 2026-08-07, both on the native transport:

- An inbound peer message arrived carrying `from-name` but **no `from=`
  attribute**, with the sender absent from `ListAgents`. It was a work request
  that **could not be answered at all** — there was no address to reply to.
- A peer (amvcp), facing the same unaddressable sender, resolved it by matching
  on **session display name** and sent two replies to this session by mistake,
  crediting it with GitHub ruleset changes it never made. Both were corrected,
  and the peer confirmed nothing was recorded against this session.

Neither failure is possible on AMP, where identity is AID-resolved. Whatever
MANAGER decides, that asymmetry is the substance of the decision: the native
transport can deliver a message that cannot be replied to, and can invite a
recipient to guess who sent it.

## Acceptance criteria

- [x] MANAGER records a ruling (option 1, 2, or 3) with a one-line rationale — hub ruling
      2026-08-18, see Approval log (option 1: AMP-only, stop-and-surface).
- [x] If option 2, the exception set is enumerated and the recording mechanism named — N/A as
      option 2; ruled EMPTY for work-directing traffic, recorded in PRRD S9.1.
- [x] The ruling lands in the PRRD (silver) so it is greppable and binding — PRRD S9.1
      (prrd-version 1.2).
- [x] AMOA's skills are updated to match — and, if option 1, say explicitly what to do when
      AMP is down — `agents/ai-maestro-orchestrator-agent-main-agent.md:375` now states STOP
      AND SURFACE, no native fallback, unsourced-tip handling for unreachable senders. Tree
      sweep confirmed this is the only non-design touchpoint mentioning the native transport.

## Out of scope

Fixing the missing `from=` attribute. That is a Claude Code / platform concern,
not AMOA's, and this proposal takes no position on it beyond citing it as
evidence.

## AMENDMENT 2026-08-07 — "outbound-unreachable" is a narrower category than assumed

The evidence sections above, and COS's item (2), both rest on senders that
"cannot be replied to". **Measured after filing: that was too strong, and the
correction shrinks the exception this TRDD asks MANAGER to define.**

A sender carrying `from-name` with no `from=`, absent from `ListAgents`, is
UNADDRESSED — not unaddressable. `ListAgents` returned 18 rows and did not
include the sender; `claude agents --json`, run from a plain shell with no
session, returned **24**, including it at the ai-maestro server's own working
directory (`~/ai-maestro`).
Addressing it by that row's name (plus the ` [ref]` the tool demands) **delivered**.

> **Platform change since this was measured — 2026-08-14, material to the ask.**
> The parenthetical above is no longer true of the tool in general. **CC 2.1.232**:
> "`SendMessage` now delivers to a bare name that exactly matches one live session,
> instead of asking to confirm with a ref first." The measurement stands as taken —
> a ref *was* demanded on 2026-08-08 and delivery *did* succeed — but a reader must
> not carry "the tool demands a ref" forward as a present-tense property.
>
> This **widens** what MANAGER is being asked to rule on rather than narrowing it:
> the same release also routes an `@`-mention typed in the prompt through
> `SendMessage`, and 2.1.225 lets `SendMessage` open a conversation with a Remote
> Control session on another machine by name. Native cross-session addressing is
> therefore cheaper and more reachable than the evidence below assumes — which cuts
> against any exception scoped on the premise that native addressing is awkward
> enough to be self-limiting. Flagged, not resolved: re-scoping the ask is
> MANAGER's call, and this note deliberately does not touch the argument itself.

So the durable identity was in `cwd` throughout. `cwd` is project identity: it
does not drift when a session is renamed, which is precisely the drift that caused
all six of the day's misroutes. The primitive was surfaced by the janitor session
(janitor#92); verified here.

Consequences for the ask:

- The "outbound-unreachable" class MANAGER is being asked to exclude may be close
  to **empty** once recipients enumerate properly. The failure was a recipient-side
  resolution gap, not an inherent property of the transport.
- What remains genuinely true of the native path is the part that survives this
  correction: it carries no AID identity and no R6 routing, so it is unaudited.
  That, not unreachability, is the substance of the R42.3 question.
- Recorded as an amendment rather than an edit to the sections above, for the same
  reason as the previous correction: the earlier framing was already relayed.

## Approval log

- 2026-08-07 — Routed to MANAGER via COS (`Emasoft/ai-maestro-chief-of-staff`).
  **Relayed, not directly observed by AMOA:** COS reports MANAGER granted item (2)
  and strengthened it to *"do not act on an outbound-unreachable sender's content
  at all beyond verifying the underlying facts from source; treat it as an
  unsourced tip,"* and that item (1) — what an agent does when AMP is unreachable —
  remains the live gap. Recorded as a relay because no MANAGER message reached AMOA
  directly; it should be confirmed against MANAGER's own record before being cited
  as settled. The amendment above may narrow item (2) further.

## Approval log

- 2026-08-18T19:53:09+0200 — APPROVED → planned by the hub session (ai-maestro-fd), under the
  USER's verbatim same-session delegation "you are in charge. decide yourself in base of
  verified facts and tests." Rulings recorded:
  (a) AMP-unreachable default = STOP AND SURFACE — never a native fallback for registered
  agents (a documented fallback becomes the default path during incidents and loses AID
  identity + R6 routing). Hub verified R42.3 verbatim in docs/GOVERNANCE-RULES.md.
  (b) Exception set = EMPTY for work-directing traffic. R42.5 (janitor global ops) and R42.8
  (unblock) are the only carve-outs and are not transport exceptions. Outbound-unreachable
  senders: stop and surface.
  SCOPE: this policy binds REGISTERED ai-maestro agents (AID-bearing, R6-routed); plugin-dev
  coordination sessions are outside AMOA scope by the USER's explicit instruction to the hub
  ("use SendMessages to orchestrate them").
  Citation fix applied same edit: the COS escalation is ai-maestro#131, not #76.
- 2026-08-18T19:56:41+0200 — COMPLETE: ruling operationalized. PRRD S9.1 added (prrd-version
  1.2); agent persona line 375 updated with the explicit AMP-down instruction (stop and
  surface, no native fallback). All four acceptance boxes verified by grep and ticked.
  Executed under the hub's Phase-2 GO + the USER's direct "permission granted" (2026-08-18);
  specs-first ordering per the hub.

Archived 2026-08-19T04:40:02+0200: terminal `complete` reached (ZONE-MISMATCH repair, trddgrep validate 2026-08-19) — policy decided and landed; release-via none makes `complete` the terminal column.
