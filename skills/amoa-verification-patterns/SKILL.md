---
name: amoa-verification-patterns
description: "Use when verifying implementations. Trigger with verification, testing, or evidence requests."
license: Apache-2.0
compatibility: "Python 3.8+, Bash, Git. Optional: Selenium, Docker, SQLite/PostgreSQL."
metadata:
  author: Emasoft
  version: "1.0.0"
agent: amoa-main
context: fork
user-invocable: false
---

# Verification Patterns for AMOA

## Overview

Evidence-based verification for proving code and systems work correctly. Collect measurable, reproducible evidence -- not assumptions.

## Prerequisites

- Python 3.8+, Bash, Git
- Optional: Selenium (E2E), Docker (containerized tests), SQLite/PostgreSQL (integration)

## Output

Verification reports with pass/fail status, collected evidence, and formatted results per test-report-format.md.

## Core Patterns

1. **Evidence-based** -- [evidence-based-verification.md](./references/evidence-based-verification.md)
  <!-- TOC: What is Evidence | Evidence-Based Verification Steps -->
2. **Exit code proof** -- [exit-code-proof.md](./references/exit-code-proof.md)
  <!-- TOC: What is an Exit Code | Exit Code Proof Steps -->
3. **E2E testing** -- [end-to-end-testing.md](./references/end-to-end-testing.md)
  <!-- TOC: What is E2E Testing | E2E Testing Steps -->
4. **Integration** -- [integration-verification.md](./references/integration-verification.md)
  <!-- TOC: What is Integration Verification | Integration Verification Steps -->

## Principles

See: [verification-principles.md](./references/verification-principles.md)
<!-- TOC: Principle 1: Never Trust Assumptions | Principle 2: Measure What Matters | Principle 3: Reproducibility | Principle 4: Fail Fast | Principle 5: Document Evidence -->

## Instructions

1. Select the appropriate verification pattern (evidence-based, exit code, E2E, or integration)
2. Set up the test environment per testing-protocol.md
3. Execute verification and collect measurable evidence
4. Format results per evidence-format.md and test-report-format.md
5. Report pass/fail with evidence; escalate failures immediately (fail-fast)
6. Update GitHub issues per github-integration.md and clean up test environment

Copy this checklist and track your progress:

- [ ] Select the appropriate verification pattern
- [ ] Set up the test environment
- [ ] Execute verification and collect evidence
- [ ] Format results and report pass/fail
- [ ] Update GitHub issues and clean up environment

## Examples

**Input:** Agent receives verification request for a new function.
**Output:** Verification report with pass/fail, collected evidence, formatted results.

See [examples.md](./references/examples.md) for worked examples.
<!-- TOC: Example 1: Evidence-Based Verification | Example 2: Exit Code Proof -->

## Resources

- [combining-patterns.md](./references/combining-patterns.md) -- Combining patterns
  <!-- TOC: Pattern Combinations | Verification Pyramid | Complete Strategy Example -->
- [cross-platform-support.md](./references/cross-platform-support.md) -- Cross-platform
  <!-- TOC: Platform-Specific Behavior | UTF-8 Encoding | Platform Detection | Path Handling | Command Execution -->
- [troubleshooting.md](./references/troubleshooting.md) -- Troubleshooting
  <!-- TOC: E2E Test is Flaky | Exit Code is 0 but Process Failed -->
- [docker-troubleshooting.md](./references/docker-troubleshooting.md) -- Docker
  <!-- TOC: Checking container logs | Configuring DNS settings -->
- [quick-reference.md](./references/quick-reference.md) -- Quick reference & checklist
  <!-- TOC: Pattern Selection Guide | Exit Codes | Output Format | Error Handling | Verification Checklist | Script Output Rules -->

## Error Handling

Fail-fast: failures propagate immediately, no fallbacks. See:

- [troubleshooting.md](./references/troubleshooting.md)
  <!-- TOC: E2E Test is Flaky | Integration Test Fails with Timeout -->
- [docker-troubleshooting.md](./references/docker-troubleshooting.md)
  <!-- TOC: Checking container logs | Using environment files -->
