---
procedure: support-skill
workflow-instruction: support
---

# Operation: Compile Review Checklist


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Structure Section](#step-1-create-structure-section)
- [Code Structure](#code-structure)
  - [Step 2: Create Naming Section](#step-2-create-naming-section)
- [Naming Conventions](#naming-conventions)
  - [Step 3: Create Logic Section](#step-3-create-logic-section)
- [Code Logic](#code-logic)
  - [Step 4: Create Resource Management Section](#step-4-create-resource-management-section)
- [Resource Management](#resource-management)
  - [Step 5: Create Test Coverage Section](#step-5-create-test-coverage-section)
- [Test Coverage](#test-coverage)
  - [Step 6: Create Security Section](#step-6-create-security-section)
- [Security Considerations](#security-considerations)
  - [Step 7: Create Documentation Section](#step-7-create-documentation-section)
- [Documentation](#documentation)
  - [Step 8: Add RULE 14 Compliance Section](#step-8-add-rule-14-compliance-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 9: Assemble Complete Checklist](#step-9-assemble-complete-checklist)
- [Code Structure](#code-structure)
- [Naming Conventions](#naming-conventions)
- [Code Logic](#code-logic)
- [Resource Management](#resource-management)
- [Test Coverage](#test-coverage)
- [Security Considerations](#security-considerations)
- [Documentation](#documentation)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Code Structure](#code-structure)
- [Naming Conventions](#naming-conventions)
- [Code Logic](#code-logic)
- [Resource Management](#resource-management)
- [Test Coverage](#test-coverage)
- [Security Considerations](#security-considerations)
- [Documentation](#documentation)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when you need to create a checklist for conducting thorough code reviews.

## Prerequisites

- Code changes available for review (PR, diff, or file list)
- Understanding of project coding standards
- Knowledge of the feature/fix being implemented

## Procedure

### Step 1: Create Structure Section

```markdown
## Code Structure
- [ ] Code follows project architecture
- [ ] Files organized in correct directories
- [ ] Module boundaries respected
- [ ] No circular dependencies introduced
- [ ] Single responsibility principle followed
```

### Step 2: Create Naming Section

```markdown
## Naming Conventions
- [ ] Functions/methods named descriptively
- [ ] Variables have meaningful names
- [ ] Constants in UPPER_SNAKE_CASE
- [ ] Classes in PascalCase
- [ ] No abbreviations without context
```

### Step 3: Create Logic Section

```markdown
## Code Logic
- [ ] Logic is correct and complete
- [ ] Edge cases handled
- [ ] Error conditions handled gracefully
- [ ] No unreachable code
- [ ] No unnecessary complexity
- [ ] Early returns used appropriately
```

### Step 4: Create Resource Management Section

```markdown
## Resource Management
- [ ] No resource leaks (files, connections)
- [ ] Context managers used (with statements)
- [ ] Proper cleanup in finally blocks
- [ ] Memory usage reasonable
- [ ] No infinite loops possible
```

### Step 5: Create Test Coverage Section

```markdown
## Test Coverage
- [ ] New code has unit tests
- [ ] Edge cases have test coverage
- [ ] Error paths tested
- [ ] Integration tests if needed
- [ ] Tests are readable and maintainable
```

### Step 6: Create Security Section

```markdown
## Security Considerations
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Output properly sanitized
- [ ] Authentication/authorization checked
- [ ] No SQL injection vectors
- [ ] No XSS vulnerabilities
```

### Step 7: Create Documentation Section

```markdown
## Documentation
- [ ] Public APIs documented
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] Changelog entry if needed
- [ ] No outdated comments
```

### Step 8: Add RULE 14 Compliance Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 9: Assemble Complete Checklist

```markdown
# Code Review Checklist

**Generated**: <timestamp>
**PR/Commit**: <reference>
**Reviewer**: <reviewer-id>

## Code Structure
[items from Step 1]

## Naming Conventions
[items from Step 2]

## Code Logic
[items from Step 3]

## Resource Management
[items from Step 4]

## Test Coverage
[items from Step 5]

## Security Considerations
[items from Step 6]

## Documentation
[items from Step 7]

## Requirement Compliance (RULE 14)
[items from Step 8]

---
**Review Result**: [ ] APPROVED / [ ] CHANGES REQUESTED
**Comments**: <summary>
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Checklist | Markdown | Complete review checklist |
| Review Result | String | APPROVED or CHANGES_REQUESTED |
| Comments | String | Summary of review findings |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No code to review | PR empty or not accessible | Request code access |
| Standards unclear | No coding guidelines | Use industry standards |
| Too much code | Large PR | Request PR split |

## Example

```markdown
# Code Review Checklist

**Generated**: 2024-01-15T16:00:00Z
**PR**: #42 - Add authentication module
**Reviewer**: reviewer-1

## Code Structure
- [x] Code follows project architecture
- [x] Files in src/auth/ directory
- [x] Module boundaries respected
- [x] No circular dependencies
- [ ] Single responsibility: AuthService does too much

## Naming Conventions
- [x] Functions named descriptively
- [x] Variables meaningful
- [x] Constants UPPER_SNAKE_CASE
- [x] Classes PascalCase
- [x] No unclear abbreviations

## Code Logic
- [x] Logic correct for happy path
- [ ] Edge case: empty password not handled
- [x] Error conditions logged
- [x] No unreachable code
- [x] Complexity acceptable

## Resource Management
- [x] Database connections closed
- [x] Context managers used
- [x] Proper cleanup present
- [x] Memory usage fine
- [x] No infinite loops

## Test Coverage
- [x] Unit tests present
- [ ] Missing: test for expired token
- [x] Error paths tested
- [x] Integration tests present
- [x] Tests readable

## Security Considerations
- [x] No hardcoded secrets
- [ ] Input validation: username length not checked
- [x] Output sanitized
- [x] Auth checks present
- [x] No SQL injection
- [x] No XSS vectors

## Documentation
- [x] API documented
- [x] Complex auth flow commented
- [x] README updated
- [x] Changelog entry added
- [x] No stale comments

## Requirement Compliance (RULE 14)
- [x] USER_REQUIREMENTS.md current
- [x] All requirements addressed
- [x] Using approved JWT library
- [x] Full feature set

---
**Review Result**: [ ] APPROVED / [x] CHANGES REQUESTED
**Comments**:
- AuthService needs to be split (SRP violation)
- Add empty password validation
- Add expired token test case
- Add username length validation
```

## Checklist

- [ ] Obtain code to review (PR, diff)
- [ ] Create structure review items
- [ ] Create naming convention items
- [ ] Create logic review items
- [ ] Create resource management items
- [ ] Create test coverage items
- [ ] Create security review items
- [ ] Create documentation items
- [ ] Add RULE 14 compliance section
- [ ] Execute review against checklist
- [ ] Document findings
- [ ] Provide review result
