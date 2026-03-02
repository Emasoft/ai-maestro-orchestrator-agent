# Operation: Resolve Technical Disagreement


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Resolution Framework](#resolution-framework)
  - [Step 1: Understand Before Responding](#step-1-understand-before-responding)
  - [Step 2: Acknowledge Valid Points](#step-2-acknowledge-valid-points)
  - [Step 3: Present Your View Without Attacking](#step-3-present-your-view-without-attacking)
  - [Step 4: Propose Resolution Path](#step-4-propose-resolution-path)
- [Escalation Criteria](#escalation-criteria)
- [Steps](#steps)
- [Tone Transformations](#tone-transformations)
- [Output](#output)
- [Success Criteria](#success-criteria)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Error Handling](#error-handling)
- [Important Rules](#important-rules)
- [Resolution Documentation](#resolution-documentation)
- [Decision Reached](#decision-reached)
- [Next Operations](#next-operations)

## Metadata

| Field | Value |
|-------|-------|
| Operation ID | `op-resolve-technical-disagreement` |
| Procedure | `proc-handle-feedback` |
| Workflow Step | Step 15 |
| Trigger | Disagreement about technical approach arises |
| Actor | Orchestrator (EOA) or involved party |
| Target | Other party in disagreement |

---

## Purpose

Resolve technical disagreements professionally without damaging relationships. Focus on finding the best solution, not winning the argument.

---

## Prerequisites

- Technical disagreement exists
- Both parties have stated positions
- Understanding of both viewpoints
- Willingness to find resolution

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `context` | Yes | Where disagreement arose (PR, issue, discussion) |
| `your_position` | Yes | What you believe is correct |
| `their_position` | Yes | What the other party believes |
| `stakes` | Yes | What's at risk (blocking PR, design decision, etc.) |
| `their_reasoning` | Optional | Why they hold their position |

---

## Resolution Framework

### Step 1: Understand Before Responding

Before stating your position, ensure you understand theirs:

```markdown
Let me make sure I understand your concern:

You're suggesting <their_position> because <their_reasoning>.

Is that accurate, or am I missing something?
```

### Step 2: Acknowledge Valid Points

Find what's correct in their position:

```markdown
I think you're right that <valid_point>.

My concern is specifically about <your_specific_concern>.
```

### Step 3: Present Your View Without Attacking

Use "I" statements, not "you" accusations:

| Wrong | Right |
|-------|-------|
| "You're wrong because..." | "I think there might be an issue because..." |
| "That won't work" | "I'm worried that might cause X" |
| "You're not considering..." | "One thing I'm thinking about is..." |

```markdown
I think <your_position> might work better here because:

1. <reason_1>
2. <reason_2>

What do you think about that consideration?
```

### Step 4: Propose Resolution Path

Offer a way forward:

```markdown
Here are a few options I see:

1. **Try your approach first**: <their_approach> - we can revisit if issues arise
2. **Try my approach**: <your_approach> - and benchmark against current
3. **Compromise**: <middle_ground_if_exists>
4. **Get external input**: Ask <tech_lead/architect> for perspective

Which of these works for you?
```

---

## Escalation Criteria

Escalate to a third party when:

| Situation | Escalate To |
|-----------|-------------|
| Blocking PR > 48 hours | Tech lead or maintainer |
| Architectural disagreement | Architect (EAA) |
| Both parties equally valid | Senior engineer |
| Getting personal/emotional | Team lead for mediation |

**Escalation template**:

```markdown
@<third_party> - We have different perspectives on <topic> and would value your input.

**Position A** (@<person_a>): <summary>
**Position B** (@<person_b>): <summary>

Both approaches have merit. Could you help us decide?
```

---

## Steps

1. **Pause before responding** - Read their message twice

2. **Verify understanding** - Restate their position

3. **Acknowledge valid points** - Find common ground

4. **State your concern** - Use "I" statements

5. **Propose options** - Give paths forward

6. **Escalate if stuck** - Bring in third party

7. **Accept decision** - Move forward without resentment

---

## Tone Transformations

| Disagreement Phrase | Better Alternative |
|--------------------|-------------------|
| "That's wrong" | "I see it differently" |
| "You should" | "What if we" |
| "Obviously" | "From my perspective" |
| "That doesn't make sense" | "Help me understand" |
| "I already told you" | "Let me clarify what I meant" |

---

## Output

| Output | Format | Description |
|--------|--------|-------------|
| Understanding confirmed | Comment/message | Their position restated |
| Your position stated | Comment/message | Respectful disagreement |
| Options proposed | Comment/message | Paths to resolution |
| Resolution reached | Comment/message | Agreed approach |
| Escalation (if needed) | Third party tagged | External input requested |

---

## Success Criteria

- Both parties feel heard
- Focus stayed on technical merits
- Personal attacks avoided
- Resolution reached or escalated appropriately
- Working relationship preserved

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Harmful |
|--------------|------------------|
| Repeating same argument louder | Doesn't add new information |
| Bringing up past disagreements | Derails current discussion |
| Appealing to authority only | "I'm senior so I'm right" |
| Silent treatment | Blocks progress, builds resentment |
| Passive aggressive agreement | "Fine, but don't blame me when it fails" |

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Other party gets personal | "Let's keep this focused on the technical aspects" |
| Discussion going in circles | "We seem stuck - should we get another perspective?" |
| You realize you're wrong | "Actually, I think you're right about X" |
| Time pressure building | "We need to decide by X - let's find a path forward" |

---

## Important Rules

1. **Separate the idea from the person** - Disagree with approach, not person
2. **Stay curious** - They might know something you don't
3. **Be willing to be wrong** - Your goal is best solution, not winning
4. **Document the decision** - Whatever is decided, record the reasoning
5. **Move on cleanly** - No "I told you so" if issues arise later

---

## Resolution Documentation

When resolution is reached, document it:

```markdown
## Decision Reached

**Context**: <what_was_disagreed_about>

**Decision**: <what_we_agreed>

**Reasoning**: <why_this_approach>

**Participants**: @<person_a>, @<person_b>

**Date**: <date>
```

---

## Next Operations

- Resolution reached → Continue with agreed approach
- Escalated → Wait for third party input
- Cannot resolve → Document disagreement, follow maintainer's call
