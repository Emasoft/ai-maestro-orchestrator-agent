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
  <!-- TOC: RULE 15: No Implementation by Orchestrator (ABSOLUTE) | Core Principle | What the Orchestrator Does | Why This Rule Exists | Forbidden Actions for Orchestrators | Correct Approach for Each Forbidden Action | Allowed Actions for Orchestrators | Small Experiments (ALLOWED with Limits) | Self-Check Before ANY Action | Exception: Emergency Research Commands | Practical Examples | Enforcement Mechanism | See Also -->
- [user-requirements-immutable.md](./references/user-requirements-immutable.md)
  <!-- TOC: Core Principle | Enforcement | Forbidden Actions | Issue Workflow -->
- [rule-14-enforcement.md](./references/rule-14-enforcement.md)
  <!-- TOC: RULE 14: User Requirements Are Immutable | Core Rule | Detecting Deviations | When Technical Constraints Conflict | Requirement Compliance Documentation | Quick Reference -->
- [orchestrator-exclusive-communications.md](./references/orchestrator-exclusive-communications.md)
  <!-- TOC: Core Principle | Sub-Agent Restrictions | Communication Flow -->
- [orchestrator-guardrails.md](./references/orchestrator-guardrails.md)
  <!-- TOC: Orchestrator Guardrails Reference | Part 1: Role Definition and Action Classification | Part 2: Decision Trees | Part 3: Common Scenarios | Part 4: Violation Detection and Examples | Quick Reference Summary | Related Documents -->
- [non-blocking-patterns.md](./references/non-blocking-patterns.md)
  <!-- TOC: Summary | Overview -->
- [delegation-checklist.md](./references/delegation-checklist.md)
  <!-- TOC: Tracking | Objective -->
- [workflow-checklists.md](./references/workflow-checklists.md)
  <!-- TOC: Workflow Checklists | Checklist: Receiving New Task | Checklist: Delegating Task | Checklist: Monitoring Delegated Task | Checklist: Verifying Task Completion | Checklist: Reporting Results | Quick Reference: Checklist Selection | Notes -->
- [sub-agent-role-boundaries-template.md](./references/sub-agent-role-boundaries-template.md)
  <!-- TOC: AMOA Sub-Agent Role Boundaries Template | YAML Frontmatter Structure | Purpose Section | Role Boundaries with Orchestrator Section | What Agent Can/Cannot Do Section | When Invoked Section | Step-by-Step Procedure Section | Output Format Section | IRON RULES Section | Examples Section | Additional Sections | Template Usage Checklist | Design Philosophy -->
