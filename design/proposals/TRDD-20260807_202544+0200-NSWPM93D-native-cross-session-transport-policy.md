---
trdd-id: NSWPM93D
title: Decide AMOA policy for Claude Code native cross-session messaging alongside AMP
column: proposal
approval-tier: 2
created: 2026-08-07T20:25:44+0200
updated: 2026-08-07T21:18:00+0200
current-owner: ai-maestro-orchestrator-agent
task-type: docs
scope: project
project-id: ai-maestro-orchestrator-agent
relevant-rules: []
external-refs: [https://github.com/Emasoft/ai-maestro-plugin/issues/61]
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
to CORE as `ai-maestro#76`, adding that R42.1's ban on injecting **queued input**
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

- [ ] MANAGER records a ruling (option 1, 2, or 3) with a one-line rationale.
- [ ] If option 2, the exception set is enumerated and the recording mechanism named.
- [ ] The ruling lands in the PRRD (silver) so it is greppable and binding.
- [ ] AMOA's skills are updated to match — and, if option 1, say explicitly what to do when AMP is down.

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
session, returned **24**, including it at `cwd=/Users/emanuelesabetta/ai-maestro`.
Addressing it by that row's name (plus the ` [ref]` the tool demands) **delivered**.

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

<!-- Still awaiting MANAGER on item (1). Tier 2: touches the audit trail. -->
