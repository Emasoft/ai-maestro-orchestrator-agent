---
operation: decompose-goals-to-modules
procedure: proc-decompose-design
workflow-instruction: Step 10 - Design Decomposition
parent-skill: eoa-two-phase-mode
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Decompose Goals to Modules


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify Natural Boundaries](#step-1-identify-natural-boundaries)
  - [Step 2: Define Module Structure](#step-2-define-module-structure)
  - [Step 3: Verify Module Independence](#step-3-verify-module-independence)
  - [Step 4: Apply MECE Principle](#step-4-apply-mece-principle)
  - [Step 5: Document in State File](#step-5-document-in-state-file)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: E-Commerce Feature](#example-e-commerce-feature)
  - [Example: Authentication System](#example-authentication-system)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You have a project goal that requires multiple implementation units
- You are in Plan Phase and need to break down requirements
- You need to define independently implementable units of work

## Prerequisites

- Project goal is documented and locked
- USER_REQUIREMENTS.md is being created or exists
- Architecture design is at least sketched

## Procedure

### Step 1: Identify Natural Boundaries

Look for natural separation points:

| Boundary Type | Indicators | Example |
|---------------|------------|---------|
| **Functional** | Different user-facing features | Login vs Profile |
| **Technical** | Different technologies/layers | API vs Database |
| **Domain** | Different business domains | Users vs Orders |
| **Platform** | Different deployment targets | Web vs Mobile |
| **Team** | Different skill requirements | Frontend vs Backend |

### Step 2: Define Module Structure

For each module, define:

```yaml
module:
  id: "unique-kebab-case-id"
  name: "Human Readable Name"
  description: "What this module does"
  priority: "high|medium|low"
  acceptance_criteria: "Clear completion conditions"
  dependencies: ["list", "of", "module-ids"]
  status: "planned"
  estimated_effort: "simple|medium|complex"
```

### Step 3: Verify Module Independence

Each module must satisfy:

| Criterion | Description | Validation |
|-----------|-------------|------------|
| **Independent** | Can be implemented without other modules running | Check dependencies list |
| **Testable** | Has clear success/failure conditions | Review acceptance criteria |
| **Assignable** | Can be assigned to one agent/developer | Check scope size |
| **Completable** | Has finite, achievable scope | Verify deliverables |

### Step 4: Apply MECE Principle

Modules should be **Mutually Exclusive, Collectively Exhaustive**:

- **Mutually Exclusive:** No overlapping responsibilities
- **Collectively Exhaustive:** All requirements covered

**Validation Questions:**
1. Does any requirement fall between modules? (gap)
2. Do any two modules address the same requirement? (overlap)
3. Is the sum of modules equal to the project goal? (coverage)

### Step 5: Document in State File

Update the plan phase state file:

```yaml
modules:
  - id: "auth-core"
    name: "Core Authentication"
    description: "User login, logout, password reset"
    priority: "high"
    acceptance_criteria: |
      - Users can login with email/password
      - Users receive JWT token valid for 24h
      - Password reset flow works via email
    dependencies: []
    status: "planned"

  - id: "oauth-google"
    name: "Google OAuth2"
    description: "Google sign-in integration"
    priority: "medium"
    acceptance_criteria: |
      - Users can sign in with Google
      - Token refresh works correctly
    dependencies: ["auth-core"]
    status: "pending"
```

## Checklist

Copy this checklist and track your progress:
- [ ] Identify natural boundaries in the requirements
- [ ] Create module list with unique IDs
- [ ] Define name and description for each module
- [ ] Set priority (high/medium/low) for each
- [ ] Write acceptance criteria (testable, unambiguous)
- [ ] Identify dependencies between modules
- [ ] Verify MECE: no gaps, no overlaps
- [ ] Verify each module is independently assignable
- [ ] Update state file with module definitions

## Examples

### Example: E-Commerce Feature

**Goal:** "Implement shopping cart with checkout"

**Module Decomposition:**

| Module ID | Name | Priority | Dependencies |
|-----------|------|----------|--------------|
| cart-core | Cart Management | high | - |
| cart-persistence | Cart Storage | high | cart-core |
| checkout-flow | Checkout UI | high | cart-core |
| payment-integration | Payment Gateway | high | checkout-flow |
| order-confirmation | Order Processing | medium | payment-integration |

**MECE Validation:**
- No gaps: All checkout requirements covered
- No overlaps: Each module owns distinct functionality
- Coverage: cart-core + persistence + checkout + payment + confirmation = full feature

### Example: Authentication System

**Goal:** "Implement user authentication with OAuth2"

**Module Decomposition:**

```yaml
modules:
  - id: "auth-core"
    name: "Core Authentication"
    description: "Email/password login, session management"
    priority: "high"
    acceptance_criteria: |
      - Login with email/password
      - JWT token generation and validation
      - Session management
    dependencies: []

  - id: "oauth-google"
    name: "Google OAuth2"
    acceptance_criteria: |
      - Google sign-in button
      - Token exchange
      - Account linking
    dependencies: ["auth-core"]

  - id: "oauth-github"
    name: "GitHub OAuth2"
    acceptance_criteria: |
      - GitHub sign-in button
      - Token exchange
      - Account linking
    dependencies: ["auth-core"]

  - id: "auth-tests"
    name: "Authentication Tests"
    acceptance_criteria: |
      - Unit tests for all auth functions
      - Integration tests for OAuth flows
      - E2E login flow tests
    dependencies: ["auth-core", "oauth-google", "oauth-github"]
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Module too large | Scope not properly decomposed | Split into smaller modules |
| Module too small | Over-decomposition | Merge related modules |
| Circular dependencies | Poor boundary design | Refactor to extract shared base |
| Gap in coverage | Missing requirement | Add module or expand existing |
| Overlap detected | Unclear boundaries | Clarify ownership, update descriptions |

## Related Operations

- [op-define-acceptance-criteria.md](op-define-acceptance-criteria.md) - Define criteria for each module
- [op-identify-task-dependencies.md](../eoa-orchestration-patterns/references/op-identify-task-dependencies.md) - Analyze dependencies
- [op-prioritize-task-assignments.md](op-prioritize-task-assignments.md) - Set module priorities
