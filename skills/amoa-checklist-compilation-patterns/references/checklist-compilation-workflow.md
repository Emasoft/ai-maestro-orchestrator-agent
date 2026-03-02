# Checklist Compilation Workflow


## Contents

- [Table of Contents](#table-of-contents)
- [1. Phase 1: Requirements Gathering](#1-phase-1-requirements-gathering)
  - [1.1 Reading Source Requirements](#11-reading-source-requirements)
  - [1.2 Identifying Verification Points](#12-identifying-verification-points)
  - [1.3 Categorizing Requirements](#13-categorizing-requirements)
- [2. Phase 2: Checklist Structuring](#2-phase-2-checklist-structuring)
  - [2.1 Creating Hierarchical Structure](#21-creating-hierarchical-structure)
  - [2.2 Defining Verification Criteria](#22-defining-verification-criteria)
  - [2.3 Adding Context and Guidance](#23-adding-context-and-guidance)
- [3. Phase 3: Format and Document](#3-phase-3-format-and-document)
  - [3.1 Applying Standard Formatting](#31-applying-standard-formatting)
  - [3.2 Adding Metadata](#32-adding-metadata)
  - [3.3 Writing Verification Procedures](#33-writing-verification-procedures)
- [4. Phase 4: Quality Assurance](#4-phase-4-quality-assurance)
  - [4.1 Checklist Self-Check](#41-checklist-self-check)
  - [4.2 Consistency Check](#42-consistency-check)
  - [4.3 Documentation Check](#43-documentation-check)
- [5. Step-by-Step Procedure](#5-step-by-step-procedure)
  - [5.1 Steps 1-5: From Assignment to Structuring](#51-steps-1-5-from-assignment-to-structuring)
    - [Step 1: Receive Assignment from Orchestrator](#step-1-receive-assignment-from-orchestrator)
    - [Step 2: Read Source Requirements and Context](#step-2-read-source-requirements-and-context)
    - [Step 3: Extract and Categorize Verification Points](#step-3-extract-and-categorize-verification-points)
    - [Step 4: Structure Checklist Hierarchy](#step-4-structure-checklist-hierarchy)
    - [Step 5: Define Verification Criteria](#step-5-define-verification-criteria)
  - [5.2 Steps 6-10: From Formatting to Delivery](#52-steps-6-10-from-formatting-to-delivery)
    - [Step 6: Apply Formatting and Add Metadata](#step-6-apply-formatting-and-add-metadata)
    - [Step 7: Quality Assurance Self-Check](#step-7-quality-assurance-self-check)
    - [Step 8: Write Checklist Document](#step-8-write-checklist-document)
    - [Step 9: Prepare Summary Report](#step-9-prepare-summary-report)
    - [Step 10: Report Completion to Orchestrator](#step-10-report-completion-to-orchestrator)

---

Detailed workflow for compiling verification checklists from requirements and specifications.

---

## Table of Contents

- 1. Phase 1: Requirements Gathering
  - 1.1 Reading source requirements
  - 1.2 Identifying verification points
  - 1.3 Categorizing requirements
- 2. Phase 2: Checklist Structuring
  - 2.1 Creating hierarchical structure
  - 2.2 Defining verification criteria
  - 2.3 Adding context and guidance
- 3. Phase 3: Format and Document
  - 3.1 Applying standard formatting
  - 3.2 Adding metadata
  - 3.3 Writing verification procedures
- 4. Phase 4: Quality Assurance
  - 4.1 Checklist self-check
  - 4.2 Consistency check
  - 4.3 Documentation check
- 5. Step-by-Step Procedure
  - 5.1 Steps 1-5: From assignment to structuring
  - 5.2 Steps 6-10: From formatting to delivery

---

## 1. Phase 1: Requirements Gathering

### 1.1 Reading Source Requirements

1. **Read module specifications** from requirements documents
2. **Read project standards** from CLAUDE.md and similar docs
3. **Read existing checklists** to understand patterns and standards
4. **Read task descriptions** to understand verification needs

### 1.2 Identifying Verification Points

1. **Extract explicit requirements** that need verification
2. **Identify implicit quality standards** from project context
3. **Note dependencies and prerequisites** for verification
4. **Recognize critical vs. non-critical** verification items

### 1.3 Categorizing Requirements

1. **Group requirements by verification type** (completion, quality, review)
2. **Organize by priority** (critical, important, nice-to-have)
3. **Order by logical verification sequence** (dependencies first)
4. **Separate automated vs. manual** verification items

---

## 2. Phase 2: Checklist Structuring

### 2.1 Creating Hierarchical Structure

1. **Organize items into logical sections** (Implementation, Testing, Documentation)
2. **Create subsections for detailed breakdowns** (Unit Tests, Integration Tests)
3. **Use consistent numbering and indentation**
4. **Maintain clear parent-child relationships** for nested items

### 2.2 Defining Verification Criteria

For each item, specify:

| Criterion | Description | Example |
|-----------|-------------|---------|
| HOW to verify | Specific method or command | Run `pytest tests/` |
| Tools to use | Required tools or scripts | Coverage report |
| Pass/fail criteria | Clear, unambiguous | Coverage ≥ 80% |
| Expected outputs | What success looks like | All tests pass |

### 2.3 Adding Context and Guidance

1. **Brief explanations** for non-obvious items
2. **Links to documentation** or standards
3. **Common pitfalls** to watch for
4. **Examples** where helpful

---

## 3. Phase 3: Format and Document

### 3.1 Applying Standard Formatting

| Element | Format |
|---------|--------|
| Unchecked item | `- [ ]` |
| Checked item | `- [x]` |
| Nested items | 2 or 4 spaces indentation |
| Section headers | Bold (`**`) |
| Notes | Italic (`*`) |
| Commands | Code blocks (`` ` ``) |

### 3.2 Adding Metadata

Include at the top of every checklist:
- **Creation date** and **version**
- **Source documents** referenced
- **Intended audience** (human reviewers, automated agents)
- **Modification history** section

### 3.3 Writing Verification Procedures

For each item, document:
1. **Exact commands** to run
2. **Expected results** or outputs
3. **Prerequisites** or setup needed
4. **Troubleshooting** for common failures

---

## 4. Phase 4: Quality Assurance

### 4.1 Checklist Self-Check

Verify all items are:
- [ ] **Actionable** - can be checked/verified
- [ ] **Unambiguous** - clear pass/fail criteria
- [ ] **Complete** - all requirements covered
- [ ] **Ordered** - dependencies respected

### 4.2 Consistency Check

Verify:
- [ ] **Consistent formatting** throughout
- [ ] **Consistent terminology** usage
- [ ] **Consistent level of detail** across sections
- [ ] **Consistent numbering** and structure

### 4.3 Documentation Check

Verify:
- [ ] All **verification procedures documented**
- [ ] All **links and references valid**
- [ ] All **technical terms defined** or explained
- [ ] All **examples correct** and helpful

---

## 5. Step-by-Step Procedure

### 5.1 Steps 1-5: From Assignment to Structuring

#### Step 1: Receive Assignment from Orchestrator

**Action:** Read and parse the orchestrator's request.

**Verification:**
- [ ] Checklist type clearly identified (completion/quality/review/test/release)
- [ ] Source requirements documents specified
- [ ] Output location and filename specified
- [ ] Target module/task name identified
- [ ] Special instructions noted

**If fails:** Request clarification with specific questions.

---

#### Step 2: Read Source Requirements and Context

**Action:** Use Read tool to gather all necessary input documents.

**Verification:**
- [ ] All specified requirement documents successfully read
- [ ] CLAUDE.md or project standards read
- [ ] Existing similar checklists read for consistency
- [ ] All technical specifications understood

**If fails:** Report missing documents, request alternatives.

---

#### Step 3: Extract and Categorize Verification Points

**Action:** Analyze requirements and identify all verification items.

**Verification:**
- [ ] All explicit requirements extracted
- [ ] Implicit quality standards identified
- [ ] Items categorized by type
- [ ] Items prioritized (critical/important/optional)
- [ ] Dependencies identified
- [ ] Verification method determined for each

**If fails:** Review source documents again or request clarification.

---

#### Step 4: Structure Checklist Hierarchy

**Action:** Organize verification points into logical sections.

**Verification:**
- [ ] Logical sections created
- [ ] Subsections for detailed breakdowns
- [ ] Items ordered by dependency
- [ ] Consistent numbering applied
- [ ] Parent-child relationships clear

**If fails:** Reorganize for clarity and logical flow.

---

#### Step 5: Define Verification Criteria

**Action:** Specify HOW to verify each item.

**Verification:**
- [ ] Each item has explicit verification method
- [ ] Verification commands specified
- [ ] Expected results documented
- [ ] Pass/fail criteria are unambiguous
- [ ] Prerequisites noted

**If fails:** Revise for more explicit, measurable criteria.

---

### 5.2 Steps 6-10: From Formatting to Delivery

#### Step 6: Apply Formatting and Add Metadata

**Action:** Format checklist using standard markdown template.

**Verification:**
- [ ] Markdown checkboxes used consistently
- [ ] Consistent indentation applied
- [ ] Bold/italic formatting appropriate
- [ ] Code blocks used for commands
- [ ] Version, date, source added

**If fails:** Review and correct inconsistencies.

---

#### Step 7: Quality Assurance Self-Check

**Action:** Review compiled checklist against quality criteria.

**Verification:**
- [ ] All items are atomic (verify ONE thing)
- [ ] All items are actionable
- [ ] All items are unambiguous
- [ ] Consistent terminology
- [ ] No vague or non-verifiable items

**If fails:** Revise to address quality issues.

---

#### Step 8: Write Checklist Document

**Action:** Use Write tool to save checklist.

**Verification:**
- [ ] File written to correct location
- [ ] Filename follows convention
- [ ] File is valid markdown
- [ ] File is complete (no truncation)

**If fails:** Retry write or report filesystem issues.

---

#### Step 9: Prepare Summary Report

**Action:** Create concise summary of compiled checklist.

**Verification:**
- [ ] Summary includes checklist purpose
- [ ] Total item count reported
- [ ] Items breakdown by priority
- [ ] Estimated verification effort noted
- [ ] Recommendations included

**If fails:** Review checklist for accurate statistics.

---

#### Step 10: Report Completion to Orchestrator

**Action:** Deliver formatted completion report.

**Verification:**
- [ ] Status clearly stated (DONE/FAILED)
- [ ] Checklist location specified
- [ ] Summary statistics provided
- [ ] Issues or missing info reported
- [ ] Format: `[DONE] checklist-compiler - [brief summary]`

**If fails:** Revise report for clarity.
