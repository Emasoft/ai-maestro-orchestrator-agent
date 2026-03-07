## Table of Contents
- [Principle 1: Never Trust Assumptions](#principle-1-never-trust-assumptions)
- [Principle 2: Measure What Matters](#principle-2-measure-what-matters)
- [Principle 3: Reproducibility](#principle-3-reproducibility)
- [Principle 4: Fail Fast](#principle-4-fail-fast)
- [Principle 5: Document Evidence](#principle-5-document-evidence)

---

## Principle 1: Never Trust Assumptions
Do not assume code works. Do not say "this should work" or "probably works." Verify every claim with evidence.

## Principle 2: Measure What Matters
Collect evidence that answers the question: "Does the system do what it is supposed to do?" Track:
- Return values
- Output data
- Side effects (files created, state changes)
- Performance metrics
- Error conditions

## Principle 3: Reproducibility
Evidence is only valid if it can be reproduced. If you verify something once, you should be able to verify it again with the same result.

## Principle 4: Fail Fast
If something fails during verification, stop immediately and report the failure. Do not continue as if it succeeded.

## Principle 5: Document Evidence
Record what you verified, when you verified it, and what the results were. This documentation becomes your proof.
