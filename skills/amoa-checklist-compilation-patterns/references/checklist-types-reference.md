# Checklist Types Reference


## Contents

- [Table of Contents](#table-of-contents)
- [1. Module Completion Checklists](#1-module-completion-checklists)
  - [1.1 When to Use](#11-when-to-use)
  - [1.2 Standard Elements](#12-standard-elements)
- [2. Quality Gate Checklists](#2-quality-gate-checklists)
  - [2.1 When to Use](#21-when-to-use)
  - [2.2 Standard Elements](#22-standard-elements)
- [3. Review Checklists](#3-review-checklists)
  - [3.1 When to Use](#31-when-to-use)
  - [3.2 Standard Elements](#32-standard-elements)
- [4. Test Coverage Checklists](#4-test-coverage-checklists)
  - [4.1 When to Use](#41-when-to-use)
  - [4.2 Standard Elements](#42-standard-elements)
- [5. Release Readiness Checklists](#5-release-readiness-checklists)
  - [5.1 When to Use](#51-when-to-use)
  - [5.2 Standard Elements](#52-standard-elements)
- [6. Task Assignment Checklists](#6-task-assignment-checklists)
  - [6.1 When to Use](#61-when-to-use)
  - [6.2 Standard Elements](#62-standard-elements)
- [Checklist Type Selection Guide](#checklist-type-selection-guide)

---

Detailed reference for the six standard checklist types used by the Checklist Compiler Agent.

---

## Table of Contents

- 1. Module Completion Checklists
  - 1.1 When to use module completion checklists
  - 1.2 Standard elements for module completion
- 2. Quality Gate Checklists
  - 2.1 When to use quality gate checklists
  - 2.2 Standard elements for quality gates
- 3. Review Checklists
  - 3.1 When to use review checklists
  - 3.2 Standard elements for reviews
- 4. Test Coverage Checklists
  - 4.1 When to use test coverage checklists
  - 4.2 Standard elements for test coverage
- 5. Release Readiness Checklists
  - 5.1 When to use release readiness checklists
  - 5.2 Standard elements for release readiness
- 6. Task Assignment Checklists
  - 6.1 When to use task assignment checklists
  - 6.2 Standard elements for task assignment

---

## 1. Module Completion Checklists

### 1.1 When to Use

Use module completion checklists when verifying that a module is complete and ready for integration into the larger system.

### 1.2 Standard Elements

| Element | Description | Verification Method |
|---------|-------------|---------------------|
| Implementation status | All functions/classes implemented | Compare spec vs. implementation |
| Documentation completeness | Docstrings, comments, README | Docstring checker script |
| Test coverage requirements | Unit tests, integration tests | Coverage report |
| Error handling verification | Exceptions, edge cases | Code review + tests |
| Type annotations completeness | Python typing, TypeScript types | Type checker (mypy, tsc) |
| Dependencies documentation | requirements.txt, package.json | File existence check |
| Interface compliance | API contracts, type signatures | Contract tests |
| Performance baselines | Response times, memory usage | Benchmark tests |
| Security considerations | Input validation, sanitization | Security scan |
| Integration points verified | Imports, exports, APIs | Integration tests |

---

## 2. Quality Gate Checklists

### 2.1 When to Use

Use quality gate checklists when verifying that quality standards are met before progression to the next phase (e.g., before merging, before release).

### 2.2 Standard Elements

| Element | Description | Verification Method |
|---------|-------------|---------------------|
| Code quality metrics | Complexity, maintainability | Static analysis tools |
| Test pass rates | 100% pass for critical paths | Test runner |
| Code coverage thresholds | Line coverage, branch coverage | Coverage report |
| Linting compliance | No errors, warnings within limits | Linter (ruff, eslint) |
| Type checking status | No type errors | Type checker |
| Documentation standards | All public APIs documented | Documentation checker |
| Security scans | No high/critical vulnerabilities | Security scanner |
| Performance benchmarks | Response times, memory usage | Benchmark suite |
| Dependency audit | No known vulnerabilities | Dependency checker |
| Build success | Clean builds, no warnings | Build system |

---

## 3. Review Checklists

### 3.1 When to Use

Use review checklists when conducting thorough reviews of code, documentation, and deliverables (e.g., PR reviews, documentation reviews).

### 3.2 Standard Elements

| Element | Description | Verification Method |
|---------|-------------|---------------------|
| Code structure review | Organization, modularity, SoC | Manual review |
| Naming conventions | Consistent, descriptive, standard | Manual review + linter |
| Error handling patterns | Comprehensive, appropriate | Code review |
| Resource management | Cleanup, disposal, memory leaks | Code review + profiler |
| Concurrency safety | Thread-safe, race conditions | Code review + tests |
| API design | Intuitive, consistent, documented | Design review |
| Documentation accuracy | Matches implementation, up-to-date | Manual comparison |
| Example completeness | Working examples, edge cases | Example execution |
| Test quality | Comprehensive, maintainable, clear | Test review |
| Commit quality | Atomic, well-described, reversible | Git log review |

---

## 4. Test Coverage Checklists

### 4.1 When to Use

Use test coverage checklists when ensuring comprehensive test coverage across all aspects of a module.

### 4.2 Standard Elements

| Element | Description | Verification Method |
|---------|-------------|---------------------|
| Unit test coverage | All functions/methods tested | Coverage report |
| Integration test coverage | All interfaces tested | Integration test suite |
| Edge case coverage | Boundary conditions, error cases | Test review |
| Performance test coverage | Stress tests, load tests | Performance test suite |
| Security test coverage | Injection, validation, authorization | Security test suite |
| Regression test coverage | Previous bugs, known issues | Regression test suite |
| Happy path scenarios | Standard use cases | Functional tests |
| Sad path scenarios | Error conditions, failures | Error tests |
| Data validation tests | Input validation, type checking | Validation tests |
| Mock/stub verification | All external dependencies covered | Test review |

---

## 5. Release Readiness Checklists

### 5.1 When to Use

Use release readiness checklists when verifying that a release is ready for deployment to production or distribution.

### 5.2 Standard Elements

| Element | Description | Verification Method |
|---------|-------------|---------------------|
| All features implemented | Feature checklist complete | Feature verification |
| All tests passing | No failing, no skipped critical | Test runner |
| Documentation updated | README, CHANGELOG, API docs | Documentation review |
| Version numbers updated | package.json, setup.py, etc. | Version check script |
| Dependencies updated | No outdated critical dependencies | Dependency check |
| Security audit complete | No high/critical vulnerabilities | Security scan |
| Performance validated | Meets performance baselines | Benchmark comparison |
| Backward compatibility | Migration paths documented | Compatibility tests |
| Rollback plan documented | How to revert if needed | Plan review |
| Deployment checklist | Step-by-step deployment guide | Checklist review |

---

## 6. Task Assignment Checklists

### 6.1 When to Use

Use task assignment checklists when verifying that a task is properly defined and ready for delegation to an agent or developer.

### 6.2 Standard Elements

| Element | Description | Verification Method |
|---------|-------------|---------------------|
| Clear objective stated | What needs to be done | Clarity review |
| Success criteria defined | How to know when done | Criteria review |
| Input requirements specified | What agent needs to start | Input checklist |
| Output requirements specified | What agent must produce | Output specification |
| Constraints documented | What agent must NOT do | Constraint list |
| Dependencies identified | What must be done first | Dependency graph |
| Tools required | What tools agent needs access to | Tool list |
| Context provided | Relevant background information | Context document |
| Verification method specified | How work will be verified | Verification plan |
| Reporting format specified | How agent should report | Report template |

---

## Checklist Type Selection Guide

| Scenario | Recommended Type |
|----------|------------------|
| Module ready for integration | Module Completion |
| Before merging to main branch | Quality Gate |
| PR or code review | Review |
| Test planning for new module | Test Coverage |
| Preparing for deployment | Release Readiness |
| Delegating to subagent | Task Assignment |
