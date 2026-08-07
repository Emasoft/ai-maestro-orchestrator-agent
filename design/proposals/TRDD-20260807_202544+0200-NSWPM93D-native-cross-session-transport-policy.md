---
trdd-id: NSWPM93D
title: Decide AMOA policy for Claude Code native cross-session messaging alongside AMP
column: proposal
approval-tier: 2
created: 2026-08-07T20:25:44+0200
updated: 2026-08-07T20:25:44+0200
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

## The question for MANAGER

Pick one:

1. **AMP only.** Native `SendMessage`/`ListAgents` are not to be used for
   agent-to-agent work traffic. Requires saying what an agent should do when AMP
   is unreachable (today the honest answer is "stop and surface it").
2. **AMP primary, native permitted for a named exception set.** Requires
   defining the set narrowly and stating how native traffic is recorded, since
   it is invisible to AMP's audit trail.
3. **Both, agent's discretion.** Not recommended — see below.

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

## Approval log

<!-- Awaiting MANAGER. Tier 2: this decides transport policy and touches the audit trail. -->
