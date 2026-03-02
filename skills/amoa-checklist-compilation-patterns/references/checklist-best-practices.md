# Checklist Best Practices


## Contents

- [Table of Contents](#table-of-contents)
- [1. Checklist Design Principles](#1-checklist-design-principles)
  - [1.1 Atomic Items](#11-atomic-items)
  - [1.2 Clear Criteria](#12-clear-criteria)
  - [1.3 Actionable Language](#13-actionable-language)
  - [1.4 Logical Organization](#14-logical-organization)
  - [1.5 Appropriate Detail](#15-appropriate-detail)
- [2. Common Pitfalls to Avoid](#2-common-pitfalls-to-avoid)
  - [2.1 Vague Items](#21-vague-items)
  - [2.2 Non-Verifiable Items](#22-non-verifiable-items)
  - [2.3 Compound Items](#23-compound-items)
  - [2.4 Assumption-Based Items](#24-assumption-based-items)
  - [2.5 Missing Verification Procedures](#25-missing-verification-procedures)
- [3. Checklist Maintenance](#3-checklist-maintenance)
  - [3.1 Versioning Checklists](#31-versioning-checklists)
  - [3.2 Creating Reusable Templates](#32-creating-reusable-templates)

---

Design principles, common pitfalls, and maintenance guidelines for checklists.

---

## Table of Contents

- 1. Checklist Design Principles
  - 1.1 Atomic items
  - 1.2 Clear criteria
  - 1.3 Actionable language
  - 1.4 Logical organization
  - 1.5 Appropriate detail
- 2. Common Pitfalls to Avoid
  - 2.1 Vague items
  - 2.2 Non-verifiable items
  - 2.3 Compound items
  - 2.4 Assumption-based items
  - 2.5 Missing verification procedures
- 3. Checklist Maintenance
  - 3.1 Versioning checklists
  - 3.2 Creating reusable templates

---

## 1. Checklist Design Principles

### 1.1 Atomic Items

Each checklist item should verify **ONE thing**.

| Approach | Example |
|----------|---------|
| ❌ Wrong | "Write tests and documentation" |
| ✅ Correct | Split into: "Write unit tests" AND "Write API documentation" |

**Why:** Atomic items enable clear pass/fail tracking and prevent partial completion ambiguity.

### 1.2 Clear Criteria

Pass/fail should be **unambiguous**.

| Approach | Example |
|----------|---------|
| ❌ Wrong | "Good test coverage" |
| ✅ Correct | "Test coverage ≥ 80% line coverage" |

**Include:**
- Specific metrics where applicable
- Examples of what "done" looks like
- Threshold values for measurable criteria

### 1.3 Actionable Language

Use **verbs** that clearly indicate the action.

| Verb | Use For |
|------|---------|
| Verify | Checking that something exists or meets criteria |
| Check | Quick validation of state or condition |
| Ensure | Confirming a condition holds |
| Confirm | Final validation before sign-off |
| Run | Executing a command or script |

**Examples:**
- ✅ "Verify all public functions have docstrings"
- ✅ "Run `pytest tests/` and confirm 100% pass"
- ❌ "Test the code" (too vague)

### 1.4 Logical Organization

Structure checklists for efficient verification.

**Grouping:**
- Group related items together
- Order by dependency (prerequisites first)
- Use consistent categorization across checklists

**Standard Section Order:**
1. Prerequisites
2. Implementation
3. Testing
4. Documentation
5. Quality
6. Security

### 1.5 Appropriate Detail

Balance completeness with readability.

| Approach | When to Use |
|----------|-------------|
| Brief | Item is self-explanatory, verifier is expert |
| Detailed | Item is complex, verifier may be unfamiliar |
| Linked | Very detailed, link to separate procedure doc |

**Rule:** Provide enough detail to verify correctly without overwhelming.

---

## 2. Common Pitfalls to Avoid

### 2.1 Vague Items

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| "Code is good quality" | "Code passes `ruff check` with no errors" |
| "Tests are comprehensive" | "All public functions have unit tests" |
| "Documentation is complete" | "All public APIs have docstrings with examples" |

### 2.2 Non-Verifiable Items

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| "Consider performance implications" | "Function executes in < 100ms for 1000-item input" |
| "Think about edge cases" | "Edge case tests exist for empty input, max size, boundary" |
| "Code is maintainable" | "Complexity score < 10 per function (cyclomatic)" |

### 2.3 Compound Items

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| "Write tests and documentation" | Item 1: "Write unit tests" |
| | Item 2: "Write API documentation" |
| "Setup and configure environment" | Item 1: "Install dependencies" |
| | Item 2: "Configure environment variables" |

### 2.4 Assumption-Based Items

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| "Ensure proper error handling" | "Verify all functions raise ValueError for invalid inputs" |
| "Handle all edge cases" | List specific edge cases to test |
| "Follow best practices" | Reference specific practices with criteria |

### 2.5 Missing Verification Procedures

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| "Database schema is correct" | "Run `python scripts/validate_schema.py` and verify 0 errors" |
| "API is secure" | "Run security scan with `safety check` and verify no high/critical" |
| "Performance is acceptable" | "Run benchmark: `pytest benchmarks/` and verify < 100ms avg" |

---

## 3. Checklist Maintenance

### 3.1 Versioning Checklists

When requirements change, update checklists properly:

1. **Increment version number**
   - Minor changes: 1.0 → 1.1
   - Major changes: 1.0 → 2.0

2. **Add version date**

3. **Document changes** in Version History section:
   ```markdown
   ## Version History

   | Version | Date | Changes |
   |---------|------|---------|
   | 1.0 | 2025-01-01 | Initial release |
   | 1.1 | 2025-01-15 | Added security section |
   | 2.0 | 2025-02-01 | Major restructure for new requirements |
   ```

4. **Archive old versions** for reference (don't delete)

### 3.2 Creating Reusable Templates

Create templates for common patterns:

| Template | Use For |
|----------|---------|
| Module completion | New modules ready for integration |
| Quality gate | Milestone reviews, merge approval |
| Release readiness | All releases |
| Code review | PR reviews |
| Test coverage | Test planning |
| Task assignment | Delegating to subagents |

**Template Storage:**
- Store in `docs_dev/checklists/templates/`
- Reference in SKILL.md for discoverability
- Keep templates updated with project standards

**Template Naming:**
```
template-[type]-[variant].md

Examples:
template-quality-gate-standard.md
template-quality-gate-security-focused.md
template-module-completion-python.md
```
