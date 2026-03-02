---
procedure: support-skill
workflow-instruction: support
---

# Operation: Compile Module Completion Checklist


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Gather Module Requirements](#step-1-gather-module-requirements)
  - [Step 2: Create Implementation Section](#step-2-create-implementation-section)
- [Implementation](#implementation)
  - [Step 3: Create Testing Section](#step-3-create-testing-section)
- [Testing](#testing)
  - [Step 4: Create Documentation Section](#step-4-create-documentation-section)
- [Documentation](#documentation)
  - [Step 5: Create Type Safety Section](#step-5-create-type-safety-section)
- [Type Safety](#type-safety)
  - [Step 6: Add RULE 14 Compliance Section](#step-6-add-rule-14-compliance-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 7: Assemble Complete Checklist](#step-7-assemble-complete-checklist)
- [Implementation](#implementation)
- [Testing](#testing)
- [Documentation](#documentation)
- [Type Safety](#type-safety)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Implementation](#implementation)
- [Testing](#testing)
- [Documentation](#documentation)
- [Type Safety](#type-safety)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when you need to create a checklist that verifies a module is ready for integration.

## Prerequisites

- USER_REQUIREMENTS.md or equivalent requirements document exists
- Module scope and acceptance criteria are defined
- Understanding of module's public API and dependencies

## Procedure

### Step 1: Gather Module Requirements

Extract from USER_REQUIREMENTS.md:
- Module name and purpose
- Required functionality
- API specifications
- Integration points
- Performance requirements

### Step 2: Create Implementation Section

```markdown
## Implementation
- [ ] All acceptance criteria implemented
- [ ] No TODO comments remaining in code
- [ ] Error handling complete for all edge cases
- [ ] Input validation implemented
- [ ] Return types match specifications
- [ ] Dependencies properly imported/injected
```

### Step 3: Create Testing Section

```markdown
## Testing
- [ ] Unit tests written and passing
- [ ] Coverage >= 80% for module code
- [ ] Integration tests for external dependencies
- [ ] Edge cases covered (null, empty, overflow)
- [ ] Error conditions tested
- [ ] Mock objects properly isolated
```

### Step 4: Create Documentation Section

```markdown
## Documentation
- [ ] API documentation updated (docstrings)
- [ ] README updated if needed
- [ ] Changelog entry added
- [ ] Usage examples provided
- [ ] Architecture notes updated (if design changed)
```

### Step 5: Create Type Safety Section

```markdown
## Type Safety
- [ ] Type hints on all public functions
- [ ] Type hints on all public class methods
- [ ] Type checker passes (mypy/pyright/tsc)
- [ ] No `Any` types without justification
- [ ] Generic types properly constrained
```

### Step 6: Add RULE 14 Compliance Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 7: Assemble Complete Checklist

```markdown
# Module: <module-name> Completion Checklist

**Generated**: <timestamp>
**Module**: <module-name>
**Version**: <version>

## Implementation
[items from Step 2]

## Testing
[items from Step 3]

## Documentation
[items from Step 4]

## Type Safety
[items from Step 5]

## Requirement Compliance (RULE 14)
[items from Step 6]

---
**Verification**: All items must be checked before module is considered complete.
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Checklist | Markdown | Complete module completion checklist |
| Item Count | Number | Total verification items |
| Categories | Array | Sections in the checklist |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Requirements unclear | USER_REQUIREMENTS.md incomplete | Request clarification from user |
| Module scope undefined | No clear boundaries | Define module interface first |
| Too many items | Module too large | Break into sub-modules |

## Example

```markdown
# Module: auth-core Completion Checklist

**Generated**: 2024-01-15T10:30:00Z
**Module**: auth-core
**Version**: 1.0.0

## Implementation
- [ ] Login endpoint accepts username/password
- [ ] JWT tokens generated with proper claims
- [ ] Token validation middleware implemented
- [ ] Password hashing using bcrypt
- [ ] Rate limiting on login attempts
- [ ] No TODO comments remaining
- [ ] Error handling for invalid credentials

## Testing
- [ ] Unit tests pass (target: 85% coverage)
- [ ] Integration tests with mock database
- [ ] Edge cases: empty password, long username
- [ ] Security tests: SQL injection, timing attacks
- [ ] Load test: 100 concurrent logins

## Documentation
- [ ] API endpoint documentation
- [ ] Token format specification
- [ ] Error response documentation
- [ ] Security considerations documented

## Type Safety
- [ ] All functions have type hints
- [ ] User model properly typed
- [ ] Token payload typed
- [ ] mypy passes with no errors

## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All authentication requirements addressed
- [ ] Using specified JWT library (jose)
- [ ] No features removed from spec
```

## Checklist

- [ ] Read USER_REQUIREMENTS.md
- [ ] Identify module boundaries
- [ ] Create implementation items from acceptance criteria
- [ ] Create testing items with coverage targets
- [ ] Create documentation items
- [ ] Create type safety items
- [ ] Add RULE 14 compliance section
- [ ] Review for completeness
- [ ] Write to project docs or GitHub issue
