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
  <!-- TOC: Table of Contents | 1 What is Evidence | 2 Evidence-Based Verification Steps | 2.1 Step 1: Define the Expected Outcome | 2.2 Step 2: Run the Code | 2.3 Step 3: Collect Evidence | 2.4 Step 4: Compare Evidence to Expectation | 2.5 Step 5: Document Results | 3 Evidence-Based Verification Example | 4 When to Use Evidence-Based Verification -->
2. **Exit code proof** -- [exit-code-proof.md](./references/exit-code-proof.md)
  <!-- TOC: Table of Contents | 1 What is an Exit Code | 2 Why Exit Codes Matter | 3 Exit Code Proof Steps | 3.1 Step 1: Run the Process | 3.2 Step 2: Check the Exit Code | 3.3 Step 3: Interpret the Result | 3.4 Step 4: Act on the Result | 4 Exit Code Proof Examples | 4.1 Bash Script Example | 4.2 Python Script Example | 5 Setting Exit Codes in Your Code | 5.1 Bash | 5.2 Python | 6 When to Use Exit Code Proof -->
3. **E2E testing** -- [end-to-end-testing.md](./references/end-to-end-testing.md)
  <!-- TOC: Table of Contents | 1 What is E2E Testing | 2 Why E2E Testing Matters | 3 E2E Testing Steps | 3.1 Step 1: Define a Complete User Workflow | 3.2 Step 2: Prepare Test Environment | 3.3 Step 3: Execute the Workflow | 3.4 Step 4: Verify Final Outcome | 3.5 Step 5: Clean Up | 4 E2E Testing Examples | 4.1 Web Application with Selenium | 4.2 Data Processing Pipeline | 5 When to Use E2E Testing -->
4. **Integration** -- [integration-verification.md](./references/integration-verification.md)
  <!-- TOC: Table of Contents | 1 What is Integration Verification | 2 Why Integration Verification Matters | 3 Integration Verification Steps | 3.1 Step 1: Identify Components to Test | 3.2 Step 2: Prepare Test Environment | 3.3 Step 3: Define Integration Points | 3.4 Step 4: Execute Component Interactions | 3.5 Step 5: Verify Results | 3.6 Step 6: Clean Up | 4 Integration Verification Examples | 4.1 API and Database Integration | 4.2 Microservices Communication | 5 When to Use Integration Verification -->

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
  <!-- TOC: Table of Contents | 1 Pattern Combinations | 2 Verification Pyramid | 3 Complete Verification Strategy Example -->
  - 5.1 Pattern Combinations
  - 5.2 Verification Pyramid
  - 5.3 Complete Verification Strategy Example
- [cross-platform-support.md](./references/cross-platform-support.md) -- Cross-platform
  <!-- TOC: Table of Contents | 1 Platform-Specific Behavior | 2 UTF-8 Encoding | 3 Platform Detection | 4 Path Handling | 5 Command Execution -->
  - 6.1 Platform-Specific Behavior
  - 6.2 UTF-8 Encoding
  - 6.3 Platform Detection
  - 6.4 Path Handling
  - ...
- [troubleshooting.md](./references/troubleshooting.md) -- Troubleshooting
  <!-- TOC: Table of Contents | 1 Tests Pass Locally but Fail in CI/CD | 2 Exit Code is 0 but Process Failed | 3 Integration Test Fails with Timeout | 4 E2E Test is Flaky | 5 Verification Requires Access to Internal State -->
  - 10.1 Tests Pass Locally but Fail in CI/CD
  - 10.2 Exit Code is 0 but Process Failed
  - 10.3 Integration Test Fails with Timeout
  - 10.4 E2E Test is Flaky
  - ...
- [docker-troubleshooting.md](./references/docker-troubleshooting.md) -- Docker
  <!-- TOC: 1 Identifying target platforms (Linux, Windows, macOS) | 2 Determining container purpose (dev, testing, CI/CD, production) | 3 Checking existing Docker configurations | 4 Listing required dependencies and tools | 1 Python base images (`python:3.12-slim`, `python:3.12-bookworm`) | 2 Node.js base images (`node:22-slim`, `node:22-bookworm`) | 3 Go base images (`golang:1.23-bookworm`) | 4 Rust base images (`rust:1.83-bookworm`) | 5 Multi-platform base images (`ubuntu:24.04`) | 1 Using multi-stage builds to reduce image size | 2 Pinning dependency versions for reproducibility | 3 Using non-root users for security | 4 Adding health checks to containers | 5 Minimizing Docker layers | 1 Specifying service architecture in docker-compose.yml | 2 Documenting required environment variables | 3 Setting up volume requirements for code mounting | 4 Configuring resource limits | 5 Implementing health check requirements | 1 Checking Docker disk usage with `docker system df` | 2 Removing unused data with `docker system prune` | 3 Cleaning up unused volumes | 4 Adjusting Docker Desktop disk limits | 1 Verifying network configuration with `docker network ls` | 2 Configuring DNS settings | 3 Testing connectivity from containers | 4 Restarting Docker daemon | 1 Identifying host user ID mismatches | 2 Creating container users with matching UIDs | 3 Building images with user ID arguments | 4 Running containers as current user | 1 Using `.dockerignore` to exclude unnecessary files | 2 Ordering Dockerfile commands for cache efficiency | 3 Separating dependency installation from source code copying | 4 Enabling BuildKit for faster builds | 1 Checking container logs | 2 Running containers with interactive shell | 3 Verifying CMD/ENTRYPOINT configuration | 4 Keeping containers alive for debugging | 1 Defining environment variables in Dockerfile | 2 Passing variables at runtime | 3 Using environment files | 4 Verifying environment variables inside containers -->
    - 1. Assessing Docker Container Needs for a Project
    - 2. Selecting Appropriate Base Images
    - 3. Applying Docker Best Practices
    - 4. Configuring Multi-Service Environments
  - ...
- [quick-reference.md](./references/quick-reference.md) -- Quick reference & checklist
  <!-- TOC: Pattern Selection Guide | Exit Codes | Output Format | Error Handling | Verification Checklist | Script Output Rules -->
  - Pattern Selection Guide
  - Exit Codes
  - Output Format
  - Error Handling
  - ...

## Error Handling

Fail-fast: failures propagate immediately, no fallbacks. See troubleshooting.md and docker-troubleshooting.md in Resources.
