---
operation: prioritize-task-assignments
procedure: proc-create-task-plan
workflow-instruction: Step 12 - Task Plan Creation
parent-skill: eoa-two-phase-mode
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Prioritize Task Assignments


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Apply Priority Criteria](#step-1-apply-priority-criteria)
  - [Step 2: Calculate Priority Score](#step-2-calculate-priority-score)
  - [Step 3: Apply Dependency Constraints](#step-3-apply-dependency-constraints)
  - [Step 4: Group into Execution Phases](#step-4-group-into-execution-phases)
  - [Step 5: Document Priority Decisions](#step-5-document-priority-decisions)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: E-Commerce Prioritization](#example-e-commerce-prioritization)
  - [Example: Risk-Based Priority Adjustment](#example-risk-based-priority-adjustment)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- Multiple modules/tasks need to be ordered for implementation
- You need to decide which tasks to assign first
- Resources are limited and prioritization is needed

## Prerequisites

- Modules are defined with dependencies
- Understanding of project constraints (timeline, resources)
- Knowledge of critical path requirements

## Procedure

### Step 1: Apply Priority Criteria

Evaluate each task against these criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Blocking Impact** | High | How many tasks does this block? |
| **User Value** | High | Direct user-facing benefit? |
| **Technical Risk** | Medium | Unknown/risky implementation? |
| **Effort** | Medium | Simple, medium, or complex? |
| **Dependencies** | Low | How many dependencies does it have? |

### Step 2: Calculate Priority Score

For each module, calculate a priority score:

```
Priority Score =
  (Blocking Impact * 3) +
  (User Value * 3) +
  (Technical Risk * 2) +
  (1 / Effort) * 1 +
  (1 / Dependencies) * 1
```

**Scoring Values:**
- Blocking Impact: 0 (none), 1 (few), 2 (many), 3 (critical path)
- User Value: 0 (internal), 1 (indirect), 2 (direct), 3 (core feature)
- Technical Risk: 0 (known), 1 (some unknowns), 2 (many unknowns), 3 (experimental)
- Effort: 1 (simple), 2 (medium), 3 (complex)
- Dependencies: 0 (none), 1 (few), 2 (many)

### Step 3: Apply Dependency Constraints

Even high-priority tasks cannot start if dependencies are unmet:

```
Effective Priority = Priority Score * Dependency Factor

Where:
- Dependency Factor = 1.0 if all dependencies met
- Dependency Factor = 0.0 if any dependency unmet
```

### Step 4: Group into Execution Phases

Based on dependencies and priorities:

```yaml
execution_phases:
  phase_1:  # Foundation (no dependencies)
    - id: "auth-core"
      priority: "high"
      reason: "Blocks all OAuth modules"

  phase_2:  # Can start after phase_1 (parallel)
    - id: "oauth-google"
      priority: "medium"
      reason: "User value, blocked by auth-core"
    - id: "oauth-github"
      priority: "medium"
      reason: "User value, blocked by auth-core"

  phase_3:  # Depends on phase_2
    - id: "auth-tests"
      priority: "low"
      reason: "Requires all auth modules complete"
```

### Step 5: Document Priority Decisions

Update the state file with priority reasoning:

```yaml
modules:
  - id: "auth-core"
    priority: "high"
    priority_score: 15
    priority_reasoning: |
      - Blocks: oauth-google, oauth-github, auth-tests (3 modules)
      - User value: Core login feature (high)
      - Risk: Well-understood implementation (low)
      - Effort: Medium complexity
    execution_phase: 1

  - id: "oauth-google"
    priority: "medium"
    priority_score: 10
    priority_reasoning: |
      - Blocks: auth-tests only
      - User value: Popular sign-in option (medium)
      - Risk: External API dependency (medium)
      - Effort: Medium complexity
    execution_phase: 2
```

## Checklist

Copy this checklist and track your progress:
- [ ] List all modules requiring prioritization
- [ ] Evaluate each against priority criteria
- [ ] Calculate priority scores
- [ ] Apply dependency constraints
- [ ] Group into execution phases
- [ ] Document priority reasoning for each module
- [ ] Update state file with priorities
- [ ] Review with user for alignment

## Examples

### Example: E-Commerce Prioritization

**Modules:**
1. Cart Core - Foundation for shopping
2. Checkout Flow - User payment
3. Inventory Check - Stock validation
4. Order Confirmation - Post-purchase
5. Email Notifications - Optional feature

**Priority Analysis:**

| Module | Blocks | User Value | Risk | Effort | Score | Phase |
|--------|--------|------------|------|--------|-------|-------|
| Cart Core | 4 | High | Low | Medium | 18 | 1 |
| Checkout Flow | 2 | High | Medium | Complex | 14 | 2 |
| Inventory Check | 1 | Medium | Low | Simple | 10 | 2 |
| Order Confirm | 1 | Medium | Low | Medium | 8 | 3 |
| Email Notif | 0 | Low | Low | Simple | 4 | 4 |

### Example: Risk-Based Priority Adjustment

**Scenario:** Technical risk should be addressed early

**Original Priority:**
1. Module A (score: 15, risk: low)
2. Module B (score: 12, risk: high)
3. Module C (score: 10, risk: low)

**Adjusted Priority (risk-first):**
1. Module B (score: 12, risk: high) - Validate early
2. Module A (score: 15, risk: low)
3. Module C (score: 10, risk: low)

**Reasoning:** High-risk modules should be tackled early to identify blockers before too much dependent work is done.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Priority conflict | Two modules need same resource | Serialize or find parallel path |
| Dependency deadlock | Circular priority requirements | Break cycle, redefine boundaries |
| Underestimated priority | Module blocking more than expected | Re-evaluate, adjust phase assignment |
| Resource constraint | Not enough agents for parallel work | Serialize highest priority first |

## Related Operations

- [op-identify-task-dependencies.md](../eoa-orchestration-patterns/references/op-identify-task-dependencies.md) - Dependencies affect priority
- [op-schedule-claude-tasks.md](op-schedule-claude-tasks.md) - Priority determines task order
- [op-select-agent-for-task.md](../eoa-orchestration-patterns/references/op-select-agent-for-task.md) - Agent selection after prioritization
