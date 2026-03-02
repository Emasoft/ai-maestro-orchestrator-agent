---
procedure: support-skill
workflow-instruction: support
---

# Operation: Compile Task Assignment Checklist


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create Objective Section](#step-1-create-objective-section)
- [Task Objective](#task-objective)
  - [Step 2: Create Acceptance Criteria Section](#step-2-create-acceptance-criteria-section)
- [Acceptance Criteria](#acceptance-criteria)
  - [Step 3: Create Context Section](#step-3-create-context-section)
- [Context Information](#context-information)
  - [Step 4: Create Constraints Section](#step-4-create-constraints-section)
- [Constraints](#constraints)
  - [Step 5: Create Resources Section](#step-5-create-resources-section)
- [Resources](#resources)
  - [Step 6: Create Handoff Section](#step-6-create-handoff-section)
- [Assignment Handoff](#assignment-handoff)
  - [Step 7: Add RULE 14 Compliance Section](#step-7-add-rule-14-compliance-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 8: Assemble Complete Checklist](#step-8-assemble-complete-checklist)
- [Task Objective](#task-objective)
- [Acceptance Criteria](#acceptance-criteria)
- [Context Information](#context-information)
- [Constraints](#constraints)
- [Resources](#resources)
- [Assignment Handoff](#assignment-handoff)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [Task Objective](#task-objective)
- [Acceptance Criteria](#acceptance-criteria)
- [Context Information](#context-information)
- [Constraints](#constraints)
- [Resources](#resources)
- [Assignment Handoff](#assignment-handoff)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when creating a checklist to verify a task is properly defined before assignment to an agent.

## Prerequisites

- Task has been identified (from issue, plan, or user request)
- Task scope is understood
- Target agent or agent type identified

## Procedure

### Step 1: Create Objective Section

```markdown
## Task Objective
- [ ] Goal is clearly stated
- [ ] Scope is well-defined
- [ ] Expected outcome documented
- [ ] Success criteria measurable
- [ ] Task is atomic (single deliverable)
```

### Step 2: Create Acceptance Criteria Section

```markdown
## Acceptance Criteria
- [ ] Functional requirements listed
- [ ] Non-functional requirements listed
- [ ] Testable criteria defined
- [ ] Edge cases identified
- [ ] Performance targets specified (if relevant)
```

### Step 3: Create Context Section

```markdown
## Context Information
- [ ] Related issues/PRs linked
- [ ] Prior work referenced
- [ ] Dependencies documented
- [ ] Blockers identified (if any)
- [ ] Architecture context provided
```

### Step 4: Create Constraints Section

```markdown
## Constraints
- [ ] Technology constraints documented
- [ ] Time constraints stated
- [ ] Resource constraints noted
- [ ] Compatibility requirements listed
- [ ] Style/convention requirements noted
```

### Step 5: Create Resources Section

```markdown
## Resources
- [ ] Required documentation linked
- [ ] API specifications available
- [ ] Design documents available
- [ ] Test data/fixtures available
- [ ] Access credentials provided (if needed)
```

### Step 6: Create Handoff Section

```markdown
## Assignment Handoff
- [ ] Agent selected and available
- [ ] Agent has required skills
- [ ] Agent has required access
- [ ] Communication channel established
- [ ] Deadline communicated
```

### Step 7: Add RULE 14 Compliance Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 8: Assemble Complete Checklist

```markdown
# Task Assignment Checklist: <task-name>

**Generated**: <timestamp>
**Task ID**: <issue-number or task-id>
**Assignee**: <agent-id>
**Priority**: <critical/high/normal/low>

## Task Objective
[items from Step 1]

## Acceptance Criteria
[items from Step 2]

## Context Information
[items from Step 3]

## Constraints
[items from Step 4]

## Resources
[items from Step 5]

## Assignment Handoff
[items from Step 6]

## Requirement Compliance (RULE 14)
[items from Step 7]

---
**Assignment Ready**: [ ] YES / [ ] NO (missing items)
**Missing Items**: <list if any>
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| Checklist | Markdown | Complete task assignment checklist |
| Assignment Ready | Boolean | Whether task is ready to assign |
| Missing Items | Array | Items that need attention before assignment |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Unclear objective | Task too vague | Request clarification from user |
| No acceptance criteria | Task not properly scoped | Define measurable criteria |
| Agent unavailable | Selected agent busy | Select alternative or queue task |
| Missing dependencies | Blocked by other work | Wait or reassign blocking work |

## Example

```markdown
# Task Assignment Checklist: Implement JWT Token Validation

**Generated**: 2024-01-15T09:00:00Z
**Task ID**: #42
**Assignee**: implementer-1
**Priority**: high

## Task Objective
- [x] Goal: Implement JWT validation middleware
- [x] Scope: Token parsing, signature verification, expiry check
- [x] Outcome: Middleware that rejects invalid tokens
- [x] Success: All 12 validation test cases pass
- [x] Atomic: Single middleware deliverable

## Acceptance Criteria
- [x] AC1: Valid tokens pass through
- [x] AC2: Expired tokens return 401
- [x] AC3: Tampered tokens return 401
- [x] AC4: Missing tokens return 401
- [x] AC5: Response time < 10ms
- [x] Edge: Clock skew tolerance of 60s

## Context Information
- [x] Related: Depends on #38 (auth module)
- [x] Prior work: Token generation in #40
- [x] Dependencies: jose library installed
- [x] Blockers: None
- [x] Architecture: Middleware pattern documented

## Constraints
- [x] Technology: Must use jose library
- [x] Time: Due by Jan 18
- [x] Resource: Single agent assignment
- [x] Compatibility: Python 3.10+
- [x] Style: Follow auth module patterns

## Resources
- [x] JWT spec: RFC 7519 linked
- [x] API spec: OpenAPI in docs/
- [x] Design doc: AUTH_DESIGN.md
- [x] Test data: fixtures/tokens.json
- [x] Access: No special access needed

## Assignment Handoff
- [x] implementer-1 selected
- [x] Agent has auth experience
- [x] Agent has repo access
- [x] AI Maestro channel ready
- [x] Deadline: Jan 18 communicated

## Requirement Compliance (RULE 14)
- [x] USER_REQUIREMENTS.md current
- [x] Section 3.2 addresses JWT validation
- [x] Using approved jose library
- [x] Full validation scope as specified

---
**Assignment Ready**: [x] YES / [ ] NO
**Missing Items**: None - ready for assignment
```

## Checklist

- [ ] Define clear task objective
- [ ] List all acceptance criteria
- [ ] Provide context and references
- [ ] Document constraints
- [ ] Link required resources
- [ ] Verify agent availability
- [ ] Add RULE 14 compliance section
- [ ] Review for completeness
- [ ] Proceed with assignment
