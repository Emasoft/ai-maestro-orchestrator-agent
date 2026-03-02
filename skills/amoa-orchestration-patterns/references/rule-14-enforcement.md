# RULE 14: User Requirements Are Immutable

## Contents

- 1.1 When handling user requirements in any workflow
- 1.2 When detecting potential requirement deviations
- 1.3 When a technical constraint conflicts with a requirement
- 1.4 When documenting requirement compliance

## 1.1 Core Rule

**RULE 14: User requirements are immutable.** No agent may modify, reinterpret, downgrade, or omit any user requirement without explicit written approval from the user.

This applies to:
- Functional requirements (what the system must do)
- Non-functional requirements (performance, security, scale targets)
- Constraints (technology choices, budget limits, timeline)
- Success criteria (acceptance conditions)

## 1.2 Detecting Deviations

A requirement deviation occurs when:
- An implementation does not match the requirement specification
- A workaround is applied that changes the expected behavior
- A requirement is marked as "out of scope" without user approval
- A requirement is reinterpreted to mean something different
- A partial implementation is accepted as "complete"

**Action on deviation detected:**
1. STOP the current task
2. Document the deviation in a Requirement Issue Report
3. Escalate to ECOS (or directly to the user if ECOS is unavailable)
4. BLOCK progress on the affected requirement until user decides

## 1.3 When Technical Constraints Conflict

If a technical constraint makes a requirement infeasible:
1. Document the constraint clearly (what, why, evidence)
2. Propose alternatives that satisfy the requirement intent
3. Send escalation to ECOS with `priority: "urgent"`
4. Wait for user decision — do NOT proceed with a workaround

**Forbidden actions:**
- Silently dropping a requirement
- Implementing a "close enough" alternative without approval
- Marking a requirement as "done" when it was modified

## 1.4 Requirement Compliance Documentation

Every workflow output MUST include requirement compliance status:

```markdown
## Requirement Compliance
- Requirements addressed: X/Y
- Deviations: [list or NONE]
- Pending user decisions: [list or NONE]
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| Requirement clear and feasible | Implement as specified |
| Requirement ambiguous | Escalate for clarification, BLOCK until resolved |
| Requirement infeasible | Document constraint, propose alternatives, escalate |
| Requirement conflicts with another | Escalate both, let user prioritize |
| Implementation deviates | Stop, document, escalate |
