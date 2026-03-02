# Conflict Resolution Guide

## Contents

- 4.1 Disagreeing professionally
  - 4.1.1 Separating the idea from the person
  - 4.1.2 Starting with understanding
  - 4.1.3 Using "I think" not "You're wrong"
- 4.2 Offering alternatives
  - 4.2.1 The "Yes, and" technique
  - 4.2.2 Presenting options without attachment
  - 4.2.3 Showing concrete examples
- 4.3 Finding compromise
  - 4.3.1 Identifying shared goals
  - 4.3.2 Proposing incremental solutions
  - 4.3.3 Time-boxing experiments
- 4.4 Escalation paths
  - 4.4.1 When to bring in a third party
  - 4.4.2 Technical leads and architects
  - 4.4.3 Documenting the disagreement
- 4.5 When to involve maintainers
  - 4.5.1 Stalled discussions
  - 4.5.2 Blocking PRs
  - 4.5.3 Community conduct issues

---

## 4.1 Disagreeing Professionally

Disagreement is healthy in software development. It surfaces better solutions. The goal is to disagree in ways that improve outcomes without damaging relationships.

### 4.1.1 Separating the Idea from the Person

**The principle**: Critique the proposal, not the proposer. Ideas can be wrong without the person being incompetent.

**Attacking the person**:
```
You don't understand how databases work. This query approach is amateur.
```

**Critiquing the idea**:
```
This query approach has some performance concerns. Specifically:
- Full table scan on a 10M row table
- No index utilization
- Blocking reads during write operations

Here's an alternative that addresses these...
```

**Signs you're attacking the person**:
- Using "you" with negative verbs (you don't understand, you forgot, you failed)
- Questioning competence (amateur, basic mistake, obvious)
- Making it personal (you always, you never)

**Reframing technique**: Replace "You [negative]" with "This [concern]"

| Personal Attack | Idea Critique |
|-----------------|---------------|
| "You're overcomplicating this" | "This solution has more moving parts than I expected" |
| "You don't understand the requirements" | "I think this might not meet requirement X" |
| "Your design is flawed" | "This design has some concerns I'd like to discuss" |

### 4.1.2 Starting with Understanding

Before disagreeing, ensure you actually understand the proposal. Many conflicts arise from misunderstanding, not real disagreement.

**Framework**: Ask questions before stating objections

**Bad**: Immediate objection
```
That won't work. Caching introduces consistency problems.
```

**Good**: Seek understanding first
```
I want to make sure I understand the caching proposal.

Are you suggesting we cache at the API gateway level with a 5-minute TTL? If so, how are you thinking about handling cache invalidation when data changes?

I have some thoughts on consistency, but want to make sure I understand your approach first.
```

**Questions that demonstrate understanding**:
- "Just to confirm, you're proposing X because of Y?"
- "Help me understand how this handles edge case Z"
- "What alternatives did you consider before landing on this?"
- "What are the tradeoffs you're aware of?"

### 4.1.3 Using "I Think" Not "You're Wrong"

Framing matters. "I think" opens dialogue. "You're wrong" closes it.

**Closed framing** (assertion of truth):
```
That's incorrect. The database won't handle this load.
```

**Open framing** (perspective sharing):
```
I'm concerned the database might not handle this load. Based on our current query patterns and the 95th percentile response times, I think we'd see timeouts under this approach.

Am I missing something in the design that addresses this?
```

**Transition phrases that keep dialogue open**:
- "I see it differently..."
- "My concern is..."
- "From my experience..."
- "What if we considered..."
- "I might be wrong, but..."
- "Have we thought about..."

---

## 4.2 Offering Alternatives

Criticism without alternatives is just complaining. Always pair concerns with constructive suggestions.

### 4.2.1 The "Yes, And" Technique

From improv comedy: accept what's offered, then build on it. This keeps momentum and acknowledges the other person's contribution.

**"No, but"** (blocks momentum):
```
No, we can't use a single database. But I guess we could look at read replicas.
```

**"Yes, and"** (builds momentum):
```
Yes, a single database keeps things simple. And we could add read replicas later when query load increases, which gives us the simplicity now while keeping options open.
```

**Applying to technical disagreements**:

**Their proposal**: "Let's use MongoDB for this new service"

**"No, but" response**:
```
No, MongoDB won't work for our transactional needs. But we could use PostgreSQL.
```

**"Yes, and" response**:
```
Yes, MongoDB would give us the schema flexibility we need for this evolving data model. And if we're concerned about transactions, we could start with MongoDB for the parts that don't need transactions and PostgreSQL for the parts that do. Or we could evaluate MongoDB's multi-document transactions feature for our use case.

What aspects are most important to you - the flexibility or something else?
```

### 4.2.2 Presenting Options Without Attachment

Present alternatives as possibilities to explore, not as "the right answer."

**Attached** (my way is right):
```
We should use event sourcing. It's the correct approach for this problem.
```

**Detached** (exploring possibilities):
```
There are a few patterns we could use here:

**Option A: Traditional CRUD**
- Simpler to implement
- Team has experience
- Harder to audit historical changes

**Option B: Event Sourcing**
- Complete audit trail built-in
- More complex implementation
- Steeper learning curve

**Option C: Hybrid (CRUD + audit log)**
- Familiar patterns
- Explicit audit logging
- Two places to maintain consistency

I lean toward Option C as a middle ground, but I'm interested in what others think. What's most important for this use case?
```

### 4.2.3 Showing Concrete Examples

Abstract debates go nowhere. Concrete examples ground the discussion.

**Abstract** (hard to evaluate):
```
Functional programming would make this code more maintainable.
```

**Concrete** (easy to evaluate):
```
Here's how functional patterns might help with the data transformation code:

**Current approach** (imperative, mutable state):
```javascript
function processUsers(users) {
  const results = [];
  for (const user of users) {
    if (user.active) {
      const processed = {};
      processed.name = user.name.toUpperCase();
      processed.email = user.email.toLowerCase();
      results.push(processed);
    }
  }
  return results;
}
```

**Functional approach** (declarative, no mutation):
```javascript
const processUsers = (users) =>
  users
    .filter(user => user.active)
    .map(user => ({
      name: user.name.toUpperCase(),
      email: user.email.toLowerCase()
    }));
```

The functional version is:
- Shorter (6 lines vs 12)
- No mutable state (easier to reason about)
- Each transformation is explicit and testable

The tradeoff is familiarity - team members used to imperative style might find this harder to read initially.
```

---

## 4.3 Finding Compromise

Not every disagreement has a winner. Often the best solution incorporates insights from multiple perspectives.

### 4.3.1 Identifying Shared Goals

Most technical disagreements have shared goals underneath. Find them.

**Framework**: Ask "What are we both trying to achieve?"

**Example**: Disagreement about testing approach

Developer A: "We need 100% code coverage"
Developer B: "Coverage metrics are meaningless"

**Finding shared goals**:
```
It sounds like we both want confidence that the code works correctly. We just have different views on how to measure that.

Developer A: You want quantitative assurance that we haven't missed anything.
Developer B: You want meaningful tests, not tests written just to hit numbers.

What if we targeted 80% coverage as a baseline, but also required integration tests for critical paths? That gives us both a measurable floor and meaningful protection for what matters most.
```

### 4.3.2 Proposing Incremental Solutions

When you can't agree on a big decision, agree on a small step.

**Big decision** (hard to agree on):
```
Should we rewrite the entire service in Rust for performance?
```

**Incremental step** (easier to agree on):
```
Let's identify the specific bottleneck first. Could we:
1. Profile the current implementation to find the hot spots
2. Try optimizing in the current language first
3. If we hit limits, rewrite just that component in Rust
4. Evaluate whether the complexity is worth it

This gives us data to make the bigger decision. If Rust shows 10x improvement in the hot path, that's strong evidence. If it's only 2x, maybe not worth the complexity.
```

### 4.3.3 Time-Boxing Experiments

When neither side will budge, propose an experiment with a defined endpoint.

**Template**:
```
We have strong views on both sides. How about this:

**Experiment**: Build a proof-of-concept using [Approach A] over [timeframe]
**Success criteria**: [Specific, measurable outcomes]
**Decision point**: On [date], we evaluate against criteria and decide

If the experiment succeeds, we go with Approach A.
If it fails, we try Approach B.
If it's inconclusive, we discuss what we learned and decide next steps.

This way we're deciding based on evidence, not opinions.
```

**Example**:
```
Let's settle the "microservices vs monolith" debate with an experiment:

**Experiment**: Extract the payment service to its own deployment
**Timeframe**: 2 sprints (4 weeks)
**Success criteria**:
- Deployment takes <10 minutes
- No increase in end-to-end latency
- Team reports lower cognitive load when making payment changes

**Decision point**: Sprint 8 retro

If successful, we continue extracting services.
If not, we stay with the monolith and revisit in 6 months.
```

---

## 4.4 Escalation Paths

Some disagreements need a tiebreaker. Knowing when and how to escalate prevents endless debates.

### 4.4.1 When to Bring in a Third Party

**Escalate when**:
- Discussion is going in circles (same arguments repeated 3+ times)
- Neither party will compromise
- The decision is blocking other work
- Emotions are running high
- The stakes are significant (architecture, security, major refactoring)

**Don't escalate when**:
- You just want to win
- You haven't tried compromise
- The issue is minor (style preferences, naming)
- You haven't clearly articulated your position

**How to request escalation**:
```
I think we've reached an impasse on the caching architecture. We've both made our cases and tried to find middle ground, but we have fundamental disagreements about the consistency requirements.

Could we bring @architect-name into the discussion? They have context on the broader system and can help us decide.

@other-developer - does that sound fair to you?
```

### 4.4.2 Technical Leads and Architects

When escalating to leads or architects, present the disagreement fairly.

**Template for escalation**:
```markdown
## Summary
We need a decision on [topic]. @developer-a and I have different views and couldn't reach agreement.

## Context
[Brief background on why this decision matters]

## Position A (@developer-a)
[Their view, stated charitably]
- Key argument: [...]
- Supporting evidence: [...]

## Position B (mine)
[My view]
- Key argument: [...]
- Supporting evidence: [...]

## Where we agree
[Common ground, if any]

## What we need
A decision on [specific question] so we can move forward with [blocked work].

## Our recommendation
[Optional: If you have a joint recommendation despite disagreement]
```

### 4.4.3 Documenting the Disagreement

Even after resolution, document the disagreement and decision. Future developers benefit from understanding the debate.

**Template for decision record**:
```markdown
# Decision: [Topic]
**Date**: [Date]
**Participants**: [Names]
**Status**: Decided

## Background
[Why this decision was needed]

## Options Considered
### Option A: [Name]
- Proposed by: @developer-a
- Pros: [...]
- Cons: [...]

### Option B: [Name]
- Proposed by: @developer-b
- Pros: [...]
- Cons: [...]

## Decision
We chose **Option B** because [reasoning].

## Dissenting View
@developer-a preferred Option A because [their reasoning, stated fairly].

## When to Revisit
Revisit this decision if [conditions change].
```

---

## 4.5 When to Involve Maintainers

In open source, maintainers are the final authority. Know when to escalate to them.

### 4.5.1 Stalled Discussions

**Signs a discussion is stalled**:
- No activity for 2+ weeks
- Same arguments repeated without progress
- Clear disagreement with no path forward

**How to request maintainer input**:
```
This discussion seems to have stalled. We have two different approaches and haven't been able to reach consensus.

@maintainer - could you weigh in? Specifically:
1. Does this feature fit the project direction?
2. If yes, which approach aligns better with the codebase philosophy?

Summary of positions:
- Position A: [brief summary]
- Position B: [brief summary]

We're happy to implement whichever direction you prefer.
```

### 4.5.2 Blocking PRs

When a PR is blocked by unresolved disagreement:

**Good**:
```
@maintainer - This PR has been open for 3 weeks with ongoing discussion about [issue]. We haven't been able to resolve it.

Current state:
- Code is complete and tested
- Blocking issue: [description]
- @reviewer-a wants: [...]
- I implemented: [...]

Could you make a call on this so we can either merge or adjust?
```

**Bad**:
```
@maintainer - Please merge this, @reviewer-a is being unreasonable.
```

### 4.5.3 Community Conduct Issues

Some conflicts aren't about code but about behavior. These need maintainer involvement.

**When to escalate conduct issues**:
- Personal attacks or insults
- Harassment or discrimination
- Persistent bad faith engagement
- Violations of code of conduct

**How to report**:
```
@maintainer (or use private reporting channel if available)

I'm concerned about the tone in [link to discussion]. Specifically:
- [Quote specific problematic statement]
- [Impact: made me uncomfortable, shut down discussion, etc.]

I've tried to keep the conversation constructive but wanted to flag this for your awareness.
```

**Don't**:
- Respond to attacks with attacks
- Call out publicly if a private channel exists
- Escalate minor tone issues (save escalation for patterns)

---

## Summary: Conflict Resolution Checklist

When you find yourself in a technical disagreement:

- [ ] Do I understand their position fully? (Ask questions first)
- [ ] Am I critiquing the idea, not the person?
- [ ] Have I used "I think" framing instead of "You're wrong"?
- [ ] Have I offered concrete alternatives?
- [ ] Have we identified shared goals?
- [ ] Can we agree on an incremental step or experiment?
- [ ] Is escalation needed? If so, have I presented both sides fairly?
- [ ] Will I document the outcome for future reference?
