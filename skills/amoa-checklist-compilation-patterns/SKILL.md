---
name: amoa-checklist-compilation-patterns
description: "Use when compiling verification checklists from requirements. Trigger with checklist or verification requests. Loaded by ai-maestro-orchestrator-agent-main-agent"
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
  <!-- TOC: Table of Contents | Module Completion Checklists | 1 When to Use | 2 Standard Elements | Quality Gate Checklists | Review Checklists | Test Coverage Checklists | Release Readiness Checklists | Task Assignment Checklists | Checklist Type Selection Guide -->
2. [checklist-templates.md](references/checklist-templates.md)
  <!-- TOC: Table of Contents | Standard Checklist Template | Prerequisites | [Section 1: [Category Name]](#section-1-category-name) | [Subsection 1.1: [Specific Area]](#subsection-11-specific-area) | [Subsection 1.2: [Specific Area]](#subsection-12-specific-area) | [Section 2: [Category Name]](#section-2-category-name) | Completion Criteria | Notes and Issues | Sign-Off | Priority-Annotated Checklist Template | Critical Items (🔴) | Important Items (🟡) | Optional Items (🟢) | Summary | Dependency-Ordered Checklist Template | Phase 1: Foundation (No Dependencies) | Phase 2: Core (Depends on Phase 1) | Phase 3: Integration (Depends on Phase 2) | Phase 4: Verification (Depends on Phase 3) | Dependency Graph | Test Coverage Checklist Template | Unit Tests | Function: `function_name_1()` | Function: `function_name_2()` | Class: `ClassName` | Method: `__init__()` | Method: `method_name()` | Integration Tests | [Interface: [Interface Name]](#interface-interface-name) | [External Dependency: [Dependency Name]](#external-dependency-dependency-name) | Coverage Metrics | Missing Coverage -->
3. [checklist-compilation-workflow.md](references/checklist-compilation-workflow.md)
  <!-- TOC: Table of Contents | Phase 1: Requirements Gathering | 1 Reading Source Requirements | 2 Identifying Verification Points | 3 Categorizing Requirements | Phase 2: Checklist Structuring | 1 Creating Hierarchical Structure | 2 Defining Verification Criteria | 3 Adding Context and Guidance | Phase 3: Format and Document | 1 Applying Standard Formatting | 2 Adding Metadata | 3 Writing Verification Procedures | Phase 4: Quality Assurance | 1 Checklist Self-Check | 2 Consistency Check | 3 Documentation Check | Step-by-Step Procedure | 1 Steps 1-5: From Assignment to Structuring | Step 1: Receive Assignment from Orchestrator | Step 2: Read Source Requirements and Context | Step 3: Extract and Categorize Verification Points | Step 4: Structure Checklist Hierarchy | Step 5: Define Verification Criteria | 2 Steps 6-10: From Formatting to Delivery | Step 6: Apply Formatting and Add Metadata | Step 7: Quality Assurance Self-Check | Step 8: Write Checklist Document | Step 9: Prepare Summary Report | Step 10: Report Completion to Orchestrator -->
4. [checklist-best-practices.md](references/checklist-best-practices.md)
  <!-- TOC: Table of Contents | Checklist Design Principles | 1 Atomic Items | 2 Clear Criteria | 3 Actionable Language | 4 Logical Organization | 5 Appropriate Detail | Common Pitfalls to Avoid | 1 Vague Items | 2 Non-Verifiable Items | 3 Compound Items | 4 Assumption-Based Items | 5 Missing Verification Procedures | Checklist Maintenance | 1 Versioning Checklists | 2 Creating Reusable Templates -->
5. [checklist-examples.md](references/checklist-examples.md)
  <!-- TOC: Checklist Compilation Examples | Table of Contents | Complete Example: SVG Parser Quality Gate Checklist | 1 Scenario and Requirements | 2 Compiled Checklist Document | Prerequisites | Section 1: Implementation Completeness | Section 2: Test Coverage and Pass Rate | Section 3: Code Quality | Section 4: Documentation | Section 5: Security | Completion Criteria | Sign-Off | Compilation Process Walkthrough | 1 Reading Requirements | 2 Identifying Verification Points | 3 Structuring the Checklist | 4 Writing the Document | Orchestrator Interaction Example | 1 Request from Orchestrator | 2 Completion Report Format -->
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
