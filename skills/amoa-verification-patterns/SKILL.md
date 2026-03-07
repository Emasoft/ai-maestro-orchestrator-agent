---
name: amoa-verification-patterns
description: "Use when verifying implementations. Trigger with verification, testing, or evidence requests."
license: Apache-2.0
compatibility: "Requires Python 3.8+, Bash shell, Git. Supports Windows, macOS, and Linux. Optional dependencies: Selenium for E2E browser testing, Docker for service orchestration, SQLite/PostgreSQL for database examples. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: "1.0.0"
agent: amoa-main
context: fork
user-invocable: false
---

# Verification Patterns for AMOA (AI Maestro Orchestrator Agent)

## Overview

Evidence-based verification techniques for proving that code, systems, and operations work correctly. Verification is about collecting measurable, reproducible evidence -- not assumptions.

## Core Patterns

1. **Evidence-based verification** -- Collecting measurable proof. See: [references/evidence-based-verification.md](./references/evidence-based-verification.md)
2. **Exit code proof** -- Using process exit codes as success/failure signals. See: [references/exit-code-proof.md](./references/exit-code-proof.md)
3. **End-to-end testing** -- Testing complete workflows from input to output. See: [references/end-to-end-testing.md](./references/end-to-end-testing.md)
4. **Integration verification** -- Testing how components work together. See: [references/integration-verification.md](./references/integration-verification.md)

## Verification Principles

Never trust assumptions; measure what matters; ensure reproducibility; fail fast; document evidence. See: [references/verification-principles.md](./references/verification-principles.md)

## Prerequisites

- Python 3.8+ with Bash shell and Git
- Optional: Selenium (E2E), Docker (orchestration), SQLite/PostgreSQL (database examples)

## References

| Topic | Reference |
|-------|-----------|
| Combining patterns | [references/combining-patterns.md](./references/combining-patterns.md) |
| Cross-platform support | [references/cross-platform-support.md](./references/cross-platform-support.md) |
| Evidence format for handoff | [references/evidence-format.md](./references/evidence-format.md) |
| Testing protocol | [references/testing-protocol.md](./references/testing-protocol.md) |
| GitHub integration | [references/github-integration.md](./references/github-integration.md) |
| Troubleshooting | [references/troubleshooting.md](./references/troubleshooting.md) |
| Docker troubleshooting | [references/docker-troubleshooting.md](./references/docker-troubleshooting.md) |
| Automation scripts | [references/automation-scripts.md](./references/automation-scripts.md) |
| Test report format | [references/test-report-format.md](./references/test-report-format.md) |
| Examples | [references/examples.md](./references/examples.md) |
| Quick reference & checklist | [references/quick-reference.md](./references/quick-reference.md) |

## Instructions

1. Select the appropriate verification pattern from Core Patterns (evidence-based, exit code, E2E, or integration).
2. Set up the test environment per [references/testing-protocol.md](./references/testing-protocol.md).
3. Execute verification and collect measurable, reproducible evidence.
4. Format results per [references/evidence-format.md](./references/evidence-format.md) and [references/test-report-format.md](./references/test-report-format.md).
5. Report pass/fail with evidence; escalate failures immediately (fail-fast, no fallbacks).

## Examples

See [references/examples.md](./references/examples.md) for worked examples of each verification pattern, including evidence collection and reporting.

## Output

Verification results should follow the evidence format in [references/evidence-format.md](./references/evidence-format.md) and the test report format in [references/test-report-format.md](./references/test-report-format.md).

## Error Handling

Verification follows a fail-fast approach: failures propagate immediately with no fallbacks. See [references/troubleshooting.md](./references/troubleshooting.md) and [references/docker-troubleshooting.md](./references/docker-troubleshooting.md) for common issues.

## Resources

- [references/automation-scripts.md](./references/automation-scripts.md) -- Reusable verification scripts
- [references/github-integration.md](./references/github-integration.md) -- CI/CD integration
- [references/cross-platform-support.md](./references/cross-platform-support.md) -- Platform-specific guidance
