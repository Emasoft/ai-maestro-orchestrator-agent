---
name: amoa-orchestration-guardrails
description: "Use when enforcing orchestrator boundaries, rules, and delegation patterns. Trigger with guardrail, rule, or boundary requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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
  <!-- TOC: Table of Contents | Core Principle | 1 What the Orchestrator Does | 2 Why This Rule Exists | Forbidden Actions for Orchestrators | 1 Actions That Violate RULE 15 | 2 Correct Approach for Each Forbidden Action | Allowed Actions for Orchestrators | 1 Actions That Are Always Allowed | 2 When Each Action is Appropriate | Small Experiments (ALLOWED with Limits) | 1 What Qualifies as a Small Experiment | 2 Size Limits for Experiments | 3 Experiment Workflow | 4 Example Experiments | Self-Check Before ANY Action | 1 The Self-Check Procedure | 2 What to Do When Self-Check Fails | Exception: Emergency Research Commands | 1 Allowed Research Commands | 2 Forbidden Implementation Commands | Practical Examples | 1 WRONG Approach (Orchestrator Does Implementation) | 2 CORRECT Approach (Orchestrator Researches and Delegates) | Enforcement Mechanism | See Also -->
  - 1. Core Principle
    - 1.1 What the Orchestrator Does
    - 1.2 Why This Rule Exists
  - 2. Forbidden Actions for Orchestrators
    - 2.1 Actions That Violate RULE 15
  - ...
- [user-requirements-immutable.md](./references/user-requirements-immutable.md)
  <!-- TOC: Table of Contents | Core Principle | 1 What Immutable Requirements Means | 2 Why This Rule Exists | Orchestration Requirement Enforcement | 1 At Project Start | Requirements | Notes | 2 During Planning | 3 During Execution | 4 At Review | Orchestrator Forbidden Actions | 1 Actions That Violate RULE 14 | 2 Consequences of Violations | Requirement Issue Workflow | 1 When to Use This Workflow | 2 The Workflow Diagram | 3 Step-by-Step Process | Requirement Immutability Enforcement Points | 1 By Phase | 2 Evidence Required at Each Phase | Troubleshooting | User Changes Requirements Mid-Project | Requirements Conflict With Each Other | Agent Delivers Something Different Than Required | See Also -->
  - 1. Core Principle
    - 1.1 What Immutable Requirements Means
    - 1.2 Why This Rule Exists
  - 2. Orchestration Requirement Enforcement
    - 2.1 At Project Start
  - ...
- [rule-14-enforcement.md](./references/rule-14-enforcement.md)
  <!-- TOC: 1 When handling user requirements in any workflow | 2 When detecting potential requirement deviations | 3 When a technical constraint conflicts with a requirement | 4 When documenting requirement compliance -->
  - 1.1 Core Rule
  - 1.2 Detecting Deviations
  - 1.3 When Technical Constraints Conflict
  - 1.4 Requirement Compliance Documentation
  - Requirement Compliance
  - ...
- [orchestrator-exclusive-communications.md](./references/orchestrator-exclusive-communications.md)
  <!-- TOC: Table of Contents | Core Principle | 1 What This Rule Means | 2 Why This Rule Exists | Orchestrator-Exclusive Actions | 1 Actions ONLY the Orchestrator Can Perform | 2 Why Each Action is Exclusive | Sub-Agent Restrictions | 1 What Sub-Agents CANNOT Do | 2 What Sub-Agents CAN Do | Communication Flow | 1 Correct Communication Pattern | 2 Forbidden Communication Pattern | Practical Examples | 1 WRONG Approach (Sub-Agent Sends Messages) | 2 CORRECT Approach (Sub-Agent Reports to Orchestrator) | 3 CORRECT Approach (Sub-Agent Prepares Template) | Enforcement Mechanism | 1 What to Include in Sub-Agent Prompts | 2 What to Check Before Spawning Sub-Agents | Standardized Rules for Sub-Agent GitHub Interactions | 1 When Sub-Agents Can Use GitHub | 2 Standardized Comment Format | 3 Rules for Opening Bug Reports | 4 Rules for Issue Triage | 5 What Sub-Agents CANNOT Do on GitHub | See Also -->
  - 1. Core Principle
    - 1.1 What This Rule Means
    - 1.2 Why This Rule Exists
  - 2. Orchestrator-Exclusive Actions
    - 2.1 Actions ONLY the Orchestrator Can Perform
  - ...
- [orchestrator-guardrails.md](./references/orchestrator-guardrails.md)
  <!-- TOC: Table of Contents | Part 1: Role Definition and Action Classification | Part 2: Decision Trees | Part 3: Common Scenarios | Part 4: Violation Detection and Examples | Quick Reference Summary | What Orchestrators DO: | What Orchestrators DO NOT DO: | Decision Rule: | Related Documents -->
    - Part 1: Role Definition and Action Classification
    - Part 2: Decision Trees
    - Part 3: Common Scenarios
    - Part 4: Violation Detection and Examples
  - Quick Reference Summary
  - ...
- [non-blocking-patterns.md](./references/non-blocking-patterns.md)
  <!-- TOC: Overview | RULE 17: Orchestrator Must Remain Responsive (IRON RULE) | Async Task Delegation Patterns | 1 Background Bash Pattern | 2 Task Agent with Timeout | 3 Fire-and-Forget Pattern for Non-Critical Tasks | Polling Instead of Blocking | 1 Progress Polling Protocol | 2 Status Check Without Blocking | Automatic Escalation Triggers | 1 When Orchestrator Has Been Unresponsive | 2 Self-Check for Responsiveness | Parallel Agent Spawning | 1 Batch Spawning Pattern | 2 Maximum Concurrent Agents | Message Queue Processing | 1 AI Maestro Priority Queue | 2 Non-Blocking Message Check | Graceful Handoff Pattern | 1 Complete Handoff | 2 Instruction Document Template | Objective | Requirements | Success Criteria | Report Format | Timeout | Emergency Response Availability | 1 Always Available For | 2 Interrupt Protocol | Task Tracking for Async Operations | 1 Tracking Document Format | In Progress | Pending Check | 2 Task Completion Verification | Quick Reference Checklist | Anti-Patterns to Avoid | Summary -->
  - Overview
  - RULE 17: Orchestrator Must Remain Responsive (IRON RULE)
  - 1. Async Task Delegation Patterns
    - 1.1 Background Bash Pattern
    - 1.2 Task Agent with Timeout
  - ...
- [delegation-checklist.md](./references/delegation-checklist.md)
  <!-- TOC: Table of Contents | 0 General Delegation Checklist | Pre-Delegation Requirements | Delegation Document Contents | Post-Delegation Actions | 0 Infrastructure Tasks | 1 Docker Setup Delegation | Task: Docker Multi-Platform Setup | Objective | Required Services | Volume Mounts | Commands Per Service | Acceptance Criteria | 2 CI/CD Pipeline Delegation | Task: CI/CD Pipeline Setup | Trigger Events | Matrix Configuration | Jobs | 3 Development Environment Delegation | 0 Code Tasks | 1 New Feature Delegation | Task: Implement Directory Sorting Feature | Interface Contract | Files to Modify | Test Requirements | 2 Bug Fix Delegation | Task: Fix Windows Path Handling Bug | Bug Description | Reproduction | Root Cause Analysis | Verification | 3 Refactoring Delegation | 0 Testing Tasks | 1 Test Suite Setup Delegation | 2 Test Execution Delegation | 3 Test Fix Delegation | 0 Documentation Tasks | 0 Pre-Delegation Self-Check | Final Checklist Before Sending | Pre-Send Self-Check | RULE 15 Compliance | Delegation Quality | Communication Protocol | Tracking | Quick Reference: Orchestrator Role | Related Documents -->
  - 1.0 General Delegation Checklist
    - Pre-Delegation Requirements
    - Delegation Document Contents
    - Post-Delegation Actions
  - 2.0 Infrastructure Tasks
  - ...
- [workflow-checklists.md](./references/workflow-checklists.md)
  <!-- TOC: Checklist: Receiving New Task | Checklist: Delegating Task | Checklist: Monitoring Delegated Task | Checklist: Verifying Task Completion | Checklist: Reporting Results | Quick Reference: Checklist Selection | Notes -->
  - Table of Contents (Use-Case Oriented)
  - Checklist: Receiving New Task
  - Checklist: Delegating Task
  - Checklist: Monitoring Delegated Task
  - Checklist: Verifying Task Completion
  - ...
- [sub-agent-role-boundaries-template.md](./references/sub-agent-role-boundaries-template.md)
  <!-- TOC: YAML Frontmatter Structure | Purpose Section | Purpose | Role Boundaries with Orchestrator Section | Role Boundaries with Orchestrator | What Agent Can/Cannot Do Section | What This Agent Can Do | What This Agent CANNOT Do | When Invoked Section | When Invoked | Invocation Scenarios | Step-by-Step Procedure Section | Step-by-Step Procedure | [Step 1: [Action Name]](#step-1-action-name) | [Step 2: [Action Name]](#step-2-action-name) | [Step 3: [Action Name]](#step-3-action-name) | Step 1: Receive Input | Step 2: Analyze Content | Output Format Section | Output Format | IRON RULES Section (Optional - for agents with strict requirements) | IRON RULES | Examples Section | Examples | Additional Sections (Optional) | AI Maestro Integration (if applicable) | AI Maestro Integration | Docker Requirements (if applicable) | Docker Containerization | Template Usage Checklist | Design Philosophy -->
  - YAML Frontmatter Structure
  - Purpose Section
  - Purpose
  - Purpose
  - Role Boundaries with Orchestrator Section
  - ...
