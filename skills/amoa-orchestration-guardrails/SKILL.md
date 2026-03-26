---
name: amoa-orchestration-guardrails
description: "Use when enforcing orchestrator boundaries, rules, and delegation patterns. Trigger with guardrail, rule, or boundary requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed, task agents, GitHub issues.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Orchestration Guardrails Skill

## Overview

Enforces orchestrator boundaries: no implementation, immutable requirements, delegation rules, and communication protocols.

## Prerequisites

AI Maestro running, GitHub CLI (`gh`) authenticated.

## Output

Guardrail validation reports, rule violation alerts, delegation checklists.

## Instructions

1. Before any action, run self-check from orchestrator-no-implementation.md
2. Verify requirements are immutable per rule-14-enforcement.md
3. Ensure all communication flows through orchestrator per orchestrator-exclusive-communications.md
4. Use delegation-checklist.md for task handoff validation

Copy this checklist and track your progress:

- [ ] Self-check: am I implementing or delegating?
- [ ] Requirements immutable (RULE 14)?
- [ ] Communication via orchestrator only?
- [ ] Delegation checklist complete?

## Examples

**Input:** Orchestrator about to run `npm test` directly.
**Output:** RULE 15 violation detected -- delegate testing to worker agent instead.

## Error Handling

Rule violation detected: stop, reassess, delegate to worker agent.

## Resources

- [orchestrator-no-implementation.md](./references/orchestrator-no-implementation.md)
  - 1. Core Principle
    - 1.1 What the Orchestrator Does
    - 1.2 Why This Rule Exists
  - 2. Forbidden Actions for Orchestrators
    - 2.1 Actions That Violate RULE 15
  - ...
- [user-requirements-immutable.md](./references/user-requirements-immutable.md)
  - 1. Core Principle
    - 1.1 What Immutable Requirements Means
    - 1.2 Why This Rule Exists
  - 2. Orchestration Requirement Enforcement
    - 2.1 At Project Start
  - ...
- [rule-14-enforcement.md](./references/rule-14-enforcement.md)
  - 1.1 Core Rule
  - 1.2 Detecting Deviations
  - 1.3 When Technical Constraints Conflict
  - 1.4 Requirement Compliance Documentation
  - Requirement Compliance
  - ...
- [orchestrator-exclusive-communications.md](./references/orchestrator-exclusive-communications.md)
  - 1. Core Principle
    - 1.1 What This Rule Means
    - 1.2 Why This Rule Exists
  - 2. Orchestrator-Exclusive Actions
    - 2.1 Actions ONLY the Orchestrator Can Perform
  - ...
- [orchestrator-guardrails.md](./references/orchestrator-guardrails.md)
    - Part 1: Role Definition and Action Classification
    - Part 2: Decision Trees
    - Part 3: Common Scenarios
    - Part 4: Violation Detection and Examples
  - Quick Reference Summary
  - ...
- [non-blocking-patterns.md](./references/non-blocking-patterns.md)
  - Overview
  - RULE 17: Orchestrator Must Remain Responsive (IRON RULE)
  - 1. Async Task Delegation Patterns
    - 1.1 Background Bash Pattern
    - 1.2 Task Agent with Timeout
  - ...
- [delegation-checklist.md](./references/delegation-checklist.md)
  - 1.0 General Delegation Checklist
    - Pre-Delegation Requirements
    - Delegation Document Contents
    - Post-Delegation Actions
  - 2.0 Infrastructure Tasks
  - ...
- [workflow-checklists.md](./references/workflow-checklists.md)
  - Table of Contents (Use-Case Oriented)
  - Checklist: Receiving New Task
  - Checklist: Delegating Task
  - Checklist: Monitoring Delegated Task
  - Checklist: Verifying Task Completion
  - ...
- [sub-agent-role-boundaries-template.md](./references/sub-agent-role-boundaries-template.md)
  - YAML Frontmatter Structure
  - Purpose Section
  - Purpose
  - Purpose
  - Role Boundaries with Orchestrator Section
  - ...
