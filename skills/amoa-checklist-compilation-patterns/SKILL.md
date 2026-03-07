---
name: amoa-checklist-compilation-patterns
description: "Use when compiling verification checklists from requirements including module completion, quality gates, and test coverage checklists. Trigger with checklist compilation requests."
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

Compiles structured verification checklists from project requirements and specifications, supporting module completion, quality gates, test coverage, review, release readiness, and task assignment checklist types.

## Prerequisites

- Access to requirements documentation (USER_REQUIREMENTS.md or similar)
- Understanding of module acceptance criteria

---

## Instructions

1. Read the requirements documentation
2. Identify the checklist type needed (module completion, quality gate, review, test coverage, release readiness, or task assignment)
3. Consult the appropriate reference document from Contents below
4. Extract verification points and structure by logical groupings
5. Define clear acceptance criteria for each item
6. Add the mandatory RULE 14 compliance section
7. Apply the appropriate template from checklist-templates.md
8. Review for completeness, write to project docs or GitHub issue, and report results

---

## Contents

### Reference Documents

1. **[checklist-types-reference.md](references/checklist-types-reference.md)** - All 6 checklist types (module, quality gate, review, test coverage, release, task assignment)
2. **[checklist-templates.md](references/checklist-templates.md)** - Standard, priority-annotated, dependency-ordered, and test coverage templates
3. **[checklist-compilation-workflow.md](references/checklist-compilation-workflow.md)** - 4-phase workflow: gather, structure, format, QA
4. **[checklist-best-practices.md](references/checklist-best-practices.md)** - Design principles, pitfalls, maintenance
5. **[checklist-examples.md](references/checklist-examples.md)** - Complete examples and walkthroughs
6. **[skill-quick-reference.md](references/skill-quick-reference.md)** - Inline examples, output deliverables, error handling, progress checklist

---

## Quick Reference

| Type | Purpose |
|------|---------|
| Module Completion | Verify module ready for integration |
| Quality Gate | Verify standards before progression |
| Review | Conduct thorough code reviews |
| Test Coverage | Ensure comprehensive test coverage |
| Release Readiness | Verify release ready for deployment |
| Task Assignment | Verify task properly defined |

**Workflow:** Requirements -> Extract Points -> Structure -> Define Criteria -> Format -> QA -> Write -> Report

### RULE 14 Compliance

Every checklist MUST include:
```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

For inline examples, output deliverables, error handling, and progress tracking checklist, see: [skill-quick-reference.md](references/skill-quick-reference.md)

---

## Output

Produces a markdown checklist written to the project docs or a GitHub issue. Each checklist includes grouped verification items with acceptance criteria and a mandatory RULE 14 compliance section. See [skill-quick-reference.md](references/skill-quick-reference.md) for output deliverables.

## Examples

See [checklist-examples.md](references/checklist-examples.md) for complete walkthroughs and [skill-quick-reference.md](references/skill-quick-reference.md) for inline examples.

## Error Handling

Missing requirements docs or unresolvable acceptance criteria halt compilation with a report to the orchestrator. See the error handling section in [skill-quick-reference.md](references/skill-quick-reference.md).

---

## Resources

- [checklist-types-reference.md](references/checklist-types-reference.md)
- [checklist-templates.md](references/checklist-templates.md)
- [checklist-compilation-workflow.md](references/checklist-compilation-workflow.md)
- [checklist-best-practices.md](references/checklist-best-practices.md)
- [checklist-examples.md](references/checklist-examples.md)
- [skill-quick-reference.md](references/skill-quick-reference.md)

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
