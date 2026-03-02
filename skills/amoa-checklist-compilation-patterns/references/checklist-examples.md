# Checklist Compilation Examples


## Contents

- [Table of Contents](#table-of-contents)
- [1. Complete Example: SVG Parser Quality Gate Checklist](#1-complete-example-svg-parser-quality-gate-checklist)
  - [1.1 Scenario and Requirements](#11-scenario-and-requirements)
  - [1.2 Compiled Checklist Document](#12-compiled-checklist-document)
- [Prerequisites](#prerequisites)
- [Section 1: Implementation Completeness](#section-1-implementation-completeness)
- [Section 2: Test Coverage and Pass Rate](#section-2-test-coverage-and-pass-rate)
- [Section 3: Code Quality](#section-3-code-quality)
- [Section 4: Documentation](#section-4-documentation)
- [Section 5: Security](#section-5-security)
- [Completion Criteria](#completion-criteria)
- [Sign-Off](#sign-off)
- [2. Compilation Process Walkthrough](#2-compilation-process-walkthrough)
  - [2.1 Reading Requirements](#21-reading-requirements)
  - [2.2 Identifying Verification Points](#22-identifying-verification-points)
  - [2.3 Structuring the Checklist](#23-structuring-the-checklist)
  - [2.4 Writing the Document](#24-writing-the-document)
- [3. Orchestrator Interaction Example](#3-orchestrator-interaction-example)
  - [3.1 Request from Orchestrator](#31-request-from-orchestrator)
  - [3.2 Completion Report Format](#32-completion-report-format)

---

Complete examples demonstrating the checklist compilation process.

---

## Table of Contents

- 1. Complete Example: SVG Parser Quality Gate Checklist
  - 1.1 Scenario and requirements
  - 1.2 Compiled checklist document
- 2. Compilation Process Walkthrough
  - 2.1 Reading requirements
  - 2.2 Identifying verification points
  - 2.3 Structuring the checklist
  - 2.4 Writing the document
- 3. Orchestrator Interaction Example
  - 3.1 Request from orchestrator
  - 3.2 Completion report format

---

## 1. Complete Example: SVG Parser Quality Gate Checklist

### 1.1 Scenario and Requirements

**Orchestrator Request:**
"Create a quality gate checklist for the `svg-parser` module before merging to main."

**Source Documents:**
- `docs/specs/svg-parser-spec.md`
- `CLAUDE.md` for project standards
- Existing quality gate checklists for patterns

### 1.2 Compiled Checklist Document

```markdown
# SVG Parser Module - Quality Gate Checklist

**Version:** 1.0
**Created:** 2025-01-15
**Source:** docs/specs/svg-parser-spec.md
**Purpose:** Verify svg-parser module meets quality standards before merge to main

---

## Prerequisites

- [ ] Feature branch is up to date with main
- [ ] No merge conflicts with main

---

## Section 1: Implementation Completeness

- [ ] **All spec functions implemented**
  - **Verify:** Compare function list in spec vs. implementation
  - **Expected:** All 12 functions from spec present in `svg_parser.py`

- [ ] **All spec classes implemented**
  - **Verify:** Compare class list in spec vs. implementation
  - **Expected:** All 3 classes (SVGElement, SVGAttribute, SVGParser) present

- [ ] **All public APIs have docstrings**
  - **Verify:** Run `python scripts/check_docstrings.py src/svg_parser.py`
  - **Expected:** Output: "All public APIs documented: 15/15"

---

## Section 2: Test Coverage and Pass Rate

- [ ] **All tests passing**
  - **Verify:** Run `pytest tests/test_svg_parser.py -v`
  - **Expected:** 100% pass rate, 0 failures, 0 errors

- [ ] **Test coverage ≥ 80%**
  - **Verify:** Run `pytest --cov=src/svg_parser --cov-report=term`
  - **Expected:** Coverage report shows ≥ 80% line coverage

- [ ] **Branch coverage ≥ 70%**
  - **Verify:** Run `pytest --cov=src/svg_parser --cov-report=term --cov-branch`
  - **Expected:** Branch coverage ≥ 70%

---

## Section 3: Code Quality

- [ ] **Ruff linting passes**
  - **Verify:** Run `uv run ruff check src/svg_parser.py`
  - **Expected:** Output: "All checks passed!"

- [ ] **Type checking passes**
  - **Verify:** Run `uv run mypy src/svg_parser.py`
  - **Expected:** Output: "Success: no issues found"

- [ ] **Code formatting correct**
  - **Verify:** Run `uv run ruff format --check src/svg_parser.py`
  - **Expected:** Output: "Would reformat 0 files"

---

## Section 4: Documentation

- [ ] **README updated**
  - **Verify:** Check README.md includes svg-parser usage examples
  - **Expected:** Section "SVG Parser Usage" present with examples

- [ ] **API documentation generated**
  - **Verify:** Run `python scripts/generate_docs.py`
  - **Expected:** File `docs/api/svg-parser.md` created and complete

---

## Section 5: Security

- [ ] **No known vulnerabilities in dependencies**
  - **Verify:** Run `uv pip list | safety check --stdin`
  - **Expected:** Output: "No known security vulnerabilities found"

- [ ] **Input validation implemented**
  - **Verify:** Review code for validation of external inputs
  - **Expected:** All parse functions validate input before processing

---

## Completion Criteria

- [ ] All critical items (marked above) are checked
- [ ] All verification commands have been run
- [ ] All verification commands produced expected results
- [ ] Any failures have been addressed and re-verified

---

## Sign-Off

- **Verified By:** _____________
- **Verification Date:** _____________
- **Status:** [ ] PASS [ ] FAIL
- **Notes:** _____________
```

---

## 2. Compilation Process Walkthrough

### 2.1 Reading Requirements

**Documents Read:**
1. `docs/specs/svg-parser-spec.md` - Module specification
2. `CLAUDE.md` - Project standards (coverage thresholds, linting rules)
3. `docs_dev/checklists/existing-quality-gate.md` - Pattern reference

**Key Information Extracted:**
- 12 functions required by spec
- 3 classes required (SVGElement, SVGAttribute, SVGParser)
- Project standard: 80% line coverage, 70% branch coverage
- Linting: ruff check, mypy type checking
- Security: safety check for dependencies

### 2.2 Identifying Verification Points

| Requirement | Verification Type | Priority |
|-------------|-------------------|----------|
| Functions implemented | Automated (script) | Critical |
| Classes implemented | Automated (script) | Critical |
| Docstrings complete | Automated (script) | Important |
| Tests passing | Automated (pytest) | Critical |
| Coverage thresholds | Automated (coverage) | Critical |
| Linting passes | Automated (ruff) | Critical |
| Type checking | Automated (mypy) | Critical |
| Formatting | Automated (ruff format) | Important |
| Documentation | Manual review | Important |
| Security scan | Automated (safety) | Important |
| Input validation | Manual review | Important |

### 2.3 Structuring the Checklist

**Section Organization:**
1. Prerequisites (blocking checks first)
2. Implementation Completeness (core functionality)
3. Test Coverage and Pass Rate (quality validation)
4. Code Quality (standards compliance)
5. Documentation (user-facing completeness)
6. Security (safety verification)

### 2.4 Writing the Document

**Formatting Applied:**
- Markdown checkboxes for all items
- Bold for item names
- Indented sub-items for verification details
- Code blocks for commands
- Clear pass/fail expected results

---

## 3. Orchestrator Interaction Example

### 3.1 Request from Orchestrator

```markdown
**Orchestrator Request:**
"Create a module completion checklist for the `data-validator` module.
Requirements are in `docs/specs/data-validator-spec.md`.
Output checklist to `docs_dev/checklists/data-validator-completion.md`."
```

### 3.2 Completion Report Format

**Response to Orchestrator (3 lines max):**

```markdown
[DONE] checklist-compiler - Created data-validator-completion.md with 45 items (15 critical, 20 important, 10 optional)
Details written to: docs_dev/checklists/data-validator-completion.md
```

**What Orchestrator Receives:**
- Status: DONE
- Brief summary: checklist name, item counts
- File location for the detailed checklist

**What Goes in the File:**
- Full checklist document
- All 45 items with verification procedures
- All metadata and sign-off sections

**What Orchestrator Does Next:**
- Assigns checklist to validation agent
- OR reviews checklist before assignment
- OR requests revisions if needed
