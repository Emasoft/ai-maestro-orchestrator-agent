---
name: amoa-verification-patterns
description: "Use when verifying implementations. Trigger with verification, testing, or evidence requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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

- [ ] Select pattern, set up environment
- [ ] Execute verification, collect evidence
- [ ] Format results, report pass/fail
- [ ] Update GitHub issues, clean up

## Examples

**Input:** Agent receives verification request for a new function.
**Output:** Verification report with pass/fail, collected evidence, formatted results.

See [examples.md](./references/examples.md) for worked examples.
<!-- TOC: Example 1: Evidence-Based Verification | Example 2: Exit Code Proof -->

## Resources

- [combining-patterns.md](./references/combining-patterns.md) -- Combining patterns
  - 5.1 Pattern Combinations
  - 5.2 Verification Pyramid
  - 5.3 Complete Verification Strategy Example
- [cross-platform-support.md](./references/cross-platform-support.md) -- Cross-platform
  - 6.1 Platform-Specific Behavior
  - 6.2 UTF-8 Encoding
  - 6.3 Platform Detection
  - 6.4 Path Handling
  - ...
- [troubleshooting.md](./references/troubleshooting.md) -- Troubleshooting
  - 10.1 Tests Pass Locally but Fail in CI/CD
  - 10.2 Exit Code is 0 but Process Failed
  - 10.3 Integration Test Fails with Timeout
  - 10.4 E2E Test is Flaky
  - ...
- [docker-troubleshooting.md](./references/docker-troubleshooting.md) -- Docker
    - 1. Assessing Docker Container Needs for a Project
    - 2. Selecting Appropriate Base Images
    - 3. Applying Docker Best Practices
    - 4. Configuring Multi-Service Environments
  - ...
- [quick-reference.md](./references/quick-reference.md) -- Quick reference & checklist
  - Pattern Selection Guide
  - Exit Codes
  - Output Format
  - Error Handling
  - ...

## Error Handling

Fail-fast: failures propagate immediately, no fallbacks. See troubleshooting.md and docker-troubleshooting.md in Resources.
