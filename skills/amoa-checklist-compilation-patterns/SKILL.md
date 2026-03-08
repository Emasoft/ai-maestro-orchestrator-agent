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

Compiles verification checklists from project requirements: module, quality gate, test coverage, review, release, task assignment.

## Prerequisites

- Access to requirements documentation (USER_REQUIREMENTS.md or similar)

## Instructions

1. Read the project requirements documentation
2. Identify the checklist type needed (module, quality gate, review, test coverage, release, task)
3. Consult the appropriate reference from Contents below
4. Extract verification points, structure by logical groupings, and define acceptance criteria
5. Add mandatory RULE 14 compliance section
6. Apply the template from checklist-templates.md
7. Review, write to project docs or GitHub issue, and report results

Copy this checklist and track your progress:

- [ ] Read the project requirements documentation
- [ ] Identify the checklist type needed
- [ ] Consult the appropriate reference from Contents below
- [ ] Extract verification points and define acceptance criteria
- [ ] Add mandatory RULE 14 compliance section
- [ ] Apply the template and review

## Contents

1. [checklist-types-reference.md](references/checklist-types-reference.md) - All 6 checklist types
  <!-- TOC: Module Completion Checklists | Quality Gate Checklists | Review Checklists | Test Coverage Checklists | Release Readiness Checklists | Task Assignment Checklists | Checklist Type Selection Guide -->
2. [checklist-templates.md](references/checklist-templates.md) - Templates
  <!-- TOC: Standard Checklist Template | Priority-Annotated Checklist Template | Dependency-Ordered Checklist Template | Test Coverage Checklist Template -->
3. [checklist-compilation-workflow.md](references/checklist-compilation-workflow.md) - 4-phase workflow
  <!-- TOC: Phase 1: Requirements Gathering | Phase 2: Checklist Structuring | Phase 3: Format and Document | Phase 4: Quality Assurance | Step-by-Step Procedure -->
4. [checklist-best-practices.md](references/checklist-best-practices.md) - Principles, pitfalls, maintenance
  <!-- TOC: Checklist Design Principles | Common Pitfalls to Avoid | Checklist Maintenance -->
5. [checklist-examples.md](references/checklist-examples.md) - Examples and walkthroughs
  <!-- TOC: Complete Example: SVG Parser Quality Gate Checklist | Compilation Process Walkthrough | Orchestrator Interaction Example -->
6. [skill-quick-reference.md](references/skill-quick-reference.md) - Quick reference, error handling
  <!-- TOC: Inline Examples | Output Deliverables | Error Handling | Progress Tracking Checklist -->

## RULE 14 Compliance

Every checklist MUST append this section:
```
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

## Examples

**Input:** "Compile a quality gate checklist for the auth-core module"
**Output:** Checklist at `docs/checklists/auth-core-quality-gate.md` with grouped items, acceptance criteria, and RULE 14 section.

See [checklist-examples.md](references/checklist-examples.md) for walkthroughs.
<!-- TOC: Complete Example: SVG Parser Quality Gate Checklist | Compilation Process Walkthrough | Orchestrator Interaction Example -->

## Error Handling

- **Missing requirements**: Halt, report `[ERROR] No USER_REQUIREMENTS.md found`
- **Unresolvable criteria**: Flag ambiguous items, request clarification
- **Incomplete modules**: Partial checklist with `[PENDING]` markers

## Output

Markdown checklist with grouped items, acceptance criteria, and RULE 14 section.

## Resources

- [checklist-types-reference.md](references/checklist-types-reference.md)
<!-- TOC: Module Completion Checklists | Quality Gate Checklists -->
- [checklist-templates.md](references/checklist-templates.md)
<!-- TOC: Standard Checklist Template | Priority-Annotated Checklist Template -->
- [checklist-compilation-workflow.md](references/checklist-compilation-workflow.md)
<!-- TOC: Phase 1: Requirements Gathering | Step-by-Step Procedure -->
- [checklist-best-practices.md](references/checklist-best-practices.md)
<!-- TOC: Checklist Design Principles | Common Pitfalls to Avoid -->
- [checklist-examples.md](references/checklist-examples.md)
<!-- TOC: Compilation Process Walkthrough | Orchestrator Interaction Example -->
- [skill-quick-reference.md](references/skill-quick-reference.md)
<!-- TOC: Inline Examples | Error Handling -->

