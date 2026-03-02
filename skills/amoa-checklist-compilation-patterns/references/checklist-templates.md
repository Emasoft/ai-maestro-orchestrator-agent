# Checklist Templates


## Contents

- [Table of Contents](#table-of-contents)
- [1. Standard Checklist Template](#1-standard-checklist-template)
- [Prerequisites](#prerequisites)
- [Section 1: [Category Name]](#section-1-category-name)
  - [Subsection 1.1: [Specific Area]](#subsection-11-specific-area)
  - [Subsection 1.2: [Specific Area]](#subsection-12-specific-area)
- [Section 2: [Category Name]](#section-2-category-name)
- [Completion Criteria](#completion-criteria)
- [Notes and Issues](#notes-and-issues)
- [Sign-Off](#sign-off)
- [2. Priority-Annotated Checklist Template](#2-priority-annotated-checklist-template)
- [Critical Items (🔴)](#critical-items-)
- [Important Items (🟡)](#important-items-)
- [Optional Items (🟢)](#optional-items-)
- [Summary](#summary)
- [3. Dependency-Ordered Checklist Template](#3-dependency-ordered-checklist-template)
- [Phase 1: Foundation (No Dependencies)](#phase-1-foundation-no-dependencies)
- [Phase 2: Core (Depends on Phase 1)](#phase-2-core-depends-on-phase-1)
- [Phase 3: Integration (Depends on Phase 2)](#phase-3-integration-depends-on-phase-2)
- [Phase 4: Verification (Depends on Phase 3)](#phase-4-verification-depends-on-phase-3)
- [Dependency Graph](#dependency-graph)
- [4. Test Coverage Checklist Template](#4-test-coverage-checklist-template)
- [Unit Tests](#unit-tests)
  - [Function: `function_name_1()`](#function-function_name_1)
  - [Function: `function_name_2()`](#function-function_name_2)
  - [Class: `ClassName`](#class-classname)
    - [Method: `__init__()`](#method-__init__)
    - [Method: `method_name()`](#method-method_name)
- [Integration Tests](#integration-tests)
  - [Interface: [Interface Name]](#interface-interface-name)
  - [External Dependency: [Dependency Name]](#external-dependency-dependency-name)
- [Coverage Metrics](#coverage-metrics)
- [Missing Coverage](#missing-coverage)

---

Ready-to-use templates for different checklist types.

---

## Table of Contents

- 1. Standard Checklist Template
  - 1.1 Basic structure with metadata
  - 1.2 Verification criteria format
- 2. Priority-Annotated Checklist Template
  - 2.1 Priority legend and color coding
  - 2.2 Organized by priority level
- 3. Dependency-Ordered Checklist Template
  - 3.1 Phase-based organization
  - 3.2 Dependency tracking format
- 4. Test Coverage Checklist Template
  - 4.1 Function-level test tracking
  - 4.2 Coverage metrics section

---

## 1. Standard Checklist Template

Use this template for general-purpose verification checklists.

```markdown
# [Module/Task Name] Checklist

**Version:** 1.0
**Created:** YYYY-MM-DD
**Source:** [Link to requirements/specs]
**Purpose:** [Brief description of what this checklist verifies]

---

## Prerequisites

Before starting verification, ensure:
- [ ] Prerequisite item 1
- [ ] Prerequisite item 2

---

## Section 1: [Category Name]

### Subsection 1.1: [Specific Area]

- [ ] **Item 1:** [Description]
  - **Verify:** [How to verify this item]
  - **Expected:** [What should be observed when verified]
  - **Command:** `[command to run if applicable]`

- [ ] **Item 2:** [Description]
  - **Verify:** [How to verify this item]
  - **Expected:** [What should be observed when verified]

### Subsection 1.2: [Specific Area]

- [ ] **Item 3:** [Description]
  - **Verify:** [How to verify this item]
  - **Expected:** [What should be observed when verified]
  - **Note:** [Any important context or caveats]

---

## Section 2: [Category Name]

[Similar structure continues...]

---

## Completion Criteria

This checklist is complete when:
- [ ] All mandatory items are checked
- [ ] All verification procedures have been executed
- [ ] All issues discovered have been addressed or documented
- [ ] Checklist results have been reported to orchestrator

---

## Notes and Issues

[Space for recording notes, issues discovered, or deviations during verification]

---

## Sign-Off

- **Verified By:** [Agent/Human name]
- **Verification Date:** YYYY-MM-DD
- **Status:** [COMPLETE / INCOMPLETE / BLOCKED]
- **Blockers:** [Any issues preventing completion]
```

---

## 2. Priority-Annotated Checklist Template

Use this template when items have different priority levels and some may be optional.

```markdown
# [Module/Task Name] Priority Checklist

**Version:** 1.0
**Created:** YYYY-MM-DD
**Source:** [Link to requirements/specs]

**Legend:**
- 🔴 CRITICAL - Must be completed, blocks progression
- 🟡 IMPORTANT - Should be completed, may block quality gates
- 🟢 OPTIONAL - Nice to have, does not block progression

---

## Critical Items (🔴)

These items MUST be completed before progression is allowed.

- [ ] 🔴 **Item 1:** [Description]
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

- [ ] 🔴 **Item 2:** [Description]
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

---

## Important Items (🟡)

These items SHOULD be completed but may be deferred with documented reason.

- [ ] 🟡 **Item 3:** [Description]
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

- [ ] 🟡 **Item 4:** [Description]
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

---

## Optional Items (🟢)

These items are nice to have but do not block progression.

- [ ] 🟢 **Item 5:** [Description]
- [ ] 🟢 **Item 6:** [Description]

---

## Summary

| Priority | Total | Completed | Remaining |
|----------|-------|-----------|-----------|
| 🔴 Critical | _ | _ | _ |
| 🟡 Important | _ | _ | _ |
| 🟢 Optional | _ | _ | _ |

**Status:** [ ] PASS (all critical complete) [ ] FAIL
```

---

## 3. Dependency-Ordered Checklist Template

Use this template when items must be completed in a specific order due to dependencies.

```markdown
# [Module/Task Name] Dependency-Ordered Checklist

**Version:** 1.0
**Created:** YYYY-MM-DD
**Note:** Items must be completed in order due to dependencies.

---

## Phase 1: Foundation (No Dependencies)

These items have no prerequisites and can be started immediately.

- [ ] **1.1:** [Item with no dependencies]
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

- [ ] **1.2:** [Item with no dependencies]
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

---

## Phase 2: Core (Depends on Phase 1)

These items require Phase 1 to be complete.

- [ ] **2.1:** [Item depending on 1.1, 1.2]
  - **Requires:** Items 1.1, 1.2 complete
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

- [ ] **2.2:** [Item depending on 1.1]
  - **Requires:** Item 1.1 complete
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

---

## Phase 3: Integration (Depends on Phase 2)

These items require Phase 2 to be complete.

- [ ] **3.1:** [Item depending on 2.1, 2.2]
  - **Requires:** Items 2.1, 2.2 complete
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

---

## Phase 4: Verification (Depends on Phase 3)

Final verification items that require all previous phases.

- [ ] **4.1:** [Final verification item]
  - **Requires:** All previous phases complete
  - **Verify:** [How to verify]
  - **Expected:** [Expected result]

---

## Dependency Graph

```
Phase 1: [1.1] [1.2]
           \   /
            \ /
Phase 2:   [2.1] [2.2]
             \   /
              \ /
Phase 3:     [3.1]
               |
Phase 4:     [4.1]
```
```

---

## 4. Test Coverage Checklist Template

Use this template for tracking test coverage at the function level.

```markdown
# [Module Name] Test Coverage Checklist

**Version:** 1.0
**Created:** YYYY-MM-DD
**Target Coverage:** Line ≥ 80%, Branch ≥ 70%

---

## Unit Tests

### Function: `function_name_1()`

- [ ] Happy path test (standard input → expected output)
- [ ] Edge case: empty input
- [ ] Edge case: maximum size input
- [ ] Edge case: [specific boundary condition]
- [ ] Error case: invalid input type
- [ ] Error case: [specific error condition]
- [ ] Type validation test
- [ ] Performance test (if applicable)

### Function: `function_name_2()`

- [ ] Happy path test
- [ ] Edge case: [specific edge case]
- [ ] Error case: [specific error condition]

### Class: `ClassName`

#### Method: `__init__()`
- [ ] Valid initialization test
- [ ] Invalid parameters test

#### Method: `method_name()`
- [ ] Happy path test
- [ ] Edge case tests
- [ ] Error case tests

---

## Integration Tests

### Interface: [Interface Name]

- [ ] Standard workflow test (happy path through full interface)
- [ ] Error handling test (error propagation across interfaces)
- [ ] Data validation test (data integrity through interface)
- [ ] Concurrent access test (if applicable)

### External Dependency: [Dependency Name]

- [ ] Connection test
- [ ] Timeout handling test
- [ ] Error response test

---

## Coverage Metrics

Run after all tests are written:

```bash
pytest --cov=src/[module] --cov-report=term --cov-branch
```

- [ ] Line coverage ≥ 80%
  - Current: ____%
- [ ] Branch coverage ≥ 70%
  - Current: ____%
- [ ] All public functions have tests
- [ ] All error paths have tests

---

## Missing Coverage

List any intentionally uncovered code with justification:

| Code Section | Reason Not Tested |
|--------------|-------------------|
| [section] | [justification] |
```
