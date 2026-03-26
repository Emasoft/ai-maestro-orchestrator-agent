---
name: amoa-checklist-compilation-patterns
description: "Use when compiling verification checklists from requirements. Trigger with checklist or verification requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
agent: amoa-main
---

# Checklist Compiler Skill

## Overview

Compiles verification checklists from project requirements.

## Prerequisites

- Access to USER_REQUIREMENTS.md

## Instructions

1. Read requirements and identify checklist type needed
2. Consult the appropriate reference from Contents below
3. Extract verification points, structure by groups, define acceptance criteria
4. Apply template from checklist-templates.md, append RULE 14 section, and output

Copy this checklist and track your progress:

- [ ] Read requirements and identify checklist type
- [ ] Extract verification points and define criteria
- [ ] Apply template, append RULE 14 section
- [ ] Write to project docs or GitHub issue

## Contents

1. [checklist-types-reference.md](references/checklist-types-reference.md)
  <!-- TOC: Module Completion Checklists | Quality Gate Checklists | Review Checklists | Test Coverage Checklists | Release Readiness Checklists | Task Assignment Checklists | Checklist Type Selection Guide -->
2. [checklist-templates.md](references/checklist-templates.md)
  <!-- TOC: Standard Checklist Template | Priority-Annotated Checklist Template | Dependency-Ordered Checklist Template | Test Coverage Checklist Template -->
3. [checklist-compilation-workflow.md](references/checklist-compilation-workflow.md)
  <!-- TOC: Phase 1: Requirements Gathering | Phase 2: Checklist Structuring | Phase 3: Format and Document | Phase 4: Quality Assurance | Step-by-Step Procedure -->
4. [checklist-best-practices.md](references/checklist-best-practices.md)
  <!-- TOC: Checklist Design Principles | Common Pitfalls to Avoid | Checklist Maintenance -->
5. [checklist-examples.md](references/checklist-examples.md)
  <!-- TOC: Checklist Compilation Examples | Table of Contents | Complete Example: SVG Parser Quality Gate Checklist | Scenario and Requirements | Compiled Checklist Document | Prerequisites | Section 1: Implementation Completeness | Section 2: Test Coverage and Pass Rate | Section 3: Code Quality | Section 4: Documentation | Section 5: Security | Completion Criteria | Sign-Off | Compilation Process Walkthrough | Reading Requirements | Identifying Verification Points | Structuring the Checklist | Writing the Document | Orchestrator Interaction Example | Request from Orchestrator | Completion Report Format -->
6. [skill-quick-reference.md](references/skill-quick-reference.md)
  <!-- TOC: Inline Examples | Output Deliverables | Error Handling | Progress Tracking Checklist -->

## Examples

**Input:** "Compile a quality gate checklist for auth-core"
**Output:** Checklist at project docs/checklists/ directory (e.g., auth-core-quality-gate.md) with grouped items, criteria, RULE 14 section.

See checklist-examples.md in Contents above for walkthroughs.

## Error Handling

- Missing requirements: halt with `[ERROR] No USER_REQUIREMENTS.md found`
- Ambiguous criteria: flag and request clarification
- Incomplete modules: partial checklist with `[PENDING]` markers

## Output

Markdown checklist with grouped items, criteria, and RULE 14 section.

## Resources

See Contents section above for all reference files.
