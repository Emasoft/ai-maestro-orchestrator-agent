<!-- Location justification (M13): the orchestrator's dispatch limits are a
GUARDRAIL, not a task-distribution mechanic — exceeding them degrades silently
rather than erroring, so it belongs with the other boundary rules the
orchestrator self-checks against before acting. Linked from the skill's
SKILL.md Resources. -->

# Subagent Platform Limits

## Contents

- [When deciding how many agents to dispatch at once](#concurrency-dispatch-at-most-16-at-a-time)
- [When a dispatched agent wants to spawn its own agents](#nesting-bundled-agents-do-not-fan-out)
- [When estimating how many agents a session can spawn in total](#lifetime-spawns-no-longer-capped)
- [When you think a dispatched agent has stalled](#a-queued-agent-looks-exactly-like-a-slow-one)
- [When updating these numbers](#where-these-numbers-live)

## Why this file exists

Claude Code enforces limits on subagents that AMOA dispatches. Every one of them
**degrades silently**: past a limit, work queues or is refused without an error
the orchestrator can see. An orchestrator that does not know the numbers cannot
tell "the platform is throttling me" from "the agent is stuck", and will
misdiagnose the first as the second.

## Concurrency: dispatch at most 16 at a time

Claude Code caps **concurrently running** subagents at **20** by default (since
CC 2.1.217), overridable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`.

**AMOA targets 16, not 20** — four slots of deliberate headroom. At exactly the
cap the orchestrator consumes the platform's entire budget, leaving nothing for
a subagent spawned by anything else in the session (a skill, a hook, the user's
own request). Those spawns do not fail loudly; they **queue**.

Dispatch in waves of ≤16 and let a wave drain before starting the next. If the
env var raises the cap, the headroom scales with it — never dispatch at the cap
itself, whatever the cap is.

## Nesting: bundled agents do not fan out

Subagents may themselves spawn subagents, **3 levels deep by default** (CC
2.1.219). This has swung twice — nesting was disabled outright in 2.1.217, and
was depth 1 before that — so do not rely on a remembered value.

Depth 3 multiplied by the concurrency cap means a single dispatch can fan out
far wider than the orchestrator's accounting expects: the orchestrator counts
the agents it dispatched, not the agents those agents dispatched.

**Therefore: every agent AMOA bundles is told not to fan out further.** Put this
in the subagent's prompt explicitly — it is not inherited, and it is not the
default. The orchestrator is the only component with a whole-session view of the
budget, so the orchestrator is the only component that may spend it.

## Lifetime spawns: no longer capped

The separate per-session cap of 200 total subagent spawns was **removed in CC
2.1.224**. Lifetime spawn count is no longer a constraint; concurrency is the
only live limit.

Do not carry forward a plan that rations dispatches against a 200-spawn budget —
it is optimizing against a limit that no longer exists, at the cost of
parallelism that does.

## Background is now the default — keep saying it anyway

Since **CC 2.1.232**, a non-teammate agent spawn in an interactive session runs
in the background by default. That does not change RULE 17; it ratifies it. Keep
passing `run_in_background: true` explicitly all the same: the defaults on this
surface have swung repeatedly (see the nesting note above, which swung twice),
and a dispatch that reads as background only because of a default becomes a
blocking dispatch the day the default moves back. Explicit costs one key and
cannot silently invert.

## `subagent_type: "fork"` is not a fresh context — AMOA does not use it

Also **CC 2.1.232**: forking is on by default, and a `subagent_type: "fork"`
subagent inherits **the full conversation and the prompt cache**. It is not a
clean cheap worker; it is a copy of the dispatcher.

Two consequences, and they are why AMOA dispatches named agent types instead:

- **Confidentiality.** A fork sees everything in the orchestrator's context —
  including other agents' assignments, their credentials-adjacent context, and
  any user material the orchestrator is holding. A per-module implementer must
  not receive the whole board.
- **Cost accounting.** A fork rides the inherited cache rather than starting
  from a small base, so it does not behave like the bounded fresh contexts the
  token-budget rules assume. Budgeting a fork as if it were a fresh spawn
  understates it.

**Therefore: do not reach for `context`/`subagent_type: "fork"` on the Agent
tool to get a "cheap clone".** It is the opposite. Dispatch a named agent type
and pass what it needs in the prompt. (This is distinct from the `context: fork`
frontmatter on this plugin's own SKILLs, which is a different surface and is
deliberately pinned with `background: false` — see `tests/unit/test_skill_frontmatter.py`.)

## A queued agent looks exactly like a slow one

This is the operational consequence that matters, and the reason the headroom
above is not fussiness.

When the concurrency cap is reached, an excess spawn **queues silently**. From
the orchestrator's side there is no error, no rejection, and no distinguishing
signal — a queued agent and a genuinely slow agent produce identical
observations. So before escalating, replacing, or reassigning an agent that
appears stalled, first ask: *how many agents are currently in flight?* If the
answer is at or near the cap, the agent is probably waiting for a slot, and
replacing it makes the queue longer rather than shorter.

## Where these numbers live

`shared/thresholds.py` — `PLATFORM_MAX_CONCURRENT_SUBAGENTS`,
`CONCURRENCY_HEADROOM`, `MAX_CONCURRENT_AGENTS`, `MAX_AGENT_SPAWN_DEPTH`,
`BUNDLED_AGENTS_MAY_FAN_OUT`.

**Those constants are reference values, not enforcement.** No script reads them;
nothing in AMOA can refuse an over-cap dispatch. The orchestrator reading *this
file* is the enforcement mechanism. If the platform limits change, update both
the constants and this prose — updating only the constants changes nothing about
how the orchestrator behaves.

## See Also

- [delegation-checklist.md](./delegation-checklist.md) — validate a handoff before dispatching
- [non-blocking-patterns.md](./non-blocking-patterns.md) — keeping the orchestrator responsive while agents run
- [sub-agent-role-boundaries-template.md](./sub-agent-role-boundaries-template.md) — where the no-fan-out instruction goes in a subagent prompt
