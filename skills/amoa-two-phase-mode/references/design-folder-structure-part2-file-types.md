# Design Folder Structure - Part 2: File Types and Locations

Detailed specification of all file types used in the design folder structure.

## Contents

- 3. File Types and Locations
  - 3.1 Templates (compilable documents)
  - 3.2 Handoffs (compiled communication files)
  - 3.3 RDD files (Requirements-Driven Design)
  - 3.4 Config files (implementer configuration)
  - 3.5 Specs (technical specifications)

---

## 3. File Types and Locations

### 3.1 Templates (compilable documents)

**Location**: `design/requirements/{platform}/templates/`

Templates contain placeholders to be compiled before sending to implementers.

**Naming convention**: `{purpose}-template.md`

**Examples**:
- `module-spec-template.md` - Module specification template
- `handoff-template.md` - Task handoff template
- `test-plan-template.md` - Test plan template
- `rdd-template.md` - RDD document template

**Placeholders format**:
```markdown
# Module: {{MODULE_NAME}}

## Requirements

{{REQUIREMENTS_LIST}}

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA}}

## Assigned To

- Agent: {{AGENT_ID}}
- Task UUID: {{TASK_UUID}}
- GitHub Issue: {{GITHUB_ISSUE}}
```

### 3.2 Handoffs (compiled communication files)

**Location**: `design/handoffs/{agent-id}/`

Handoffs are compiled from templates with all placeholders filled.

**Naming convention**: `{module-id}-handoff.md`

**What handoffs contain**:
- Fully compiled module specification
- Task-specific acceptance criteria
- Agent-specific configuration
- Links to relevant specs and RDD
- Clear success metrics

### 3.3 RDD files (Requirements-Driven Design)

**Location**: `design/requirements/{platform}/rdd/`

RDD documents link requirements to design decisions.

**Naming convention**: `{module-id}-rdd.md`

**RDD structure**:
```markdown
# RDD: {{MODULE_NAME}}

## Requirements Traceability

| Req ID | Requirement | Design Decision | Rationale |
|--------|-------------|-----------------|-----------|
| REQ-001 | User login | JWT tokens | Stateless auth |
| REQ-002 | Remember me | Refresh tokens | 7-day validity |

## Design Decisions

### Decision 1: {{DECISION_TITLE}}

**Requirement**: REQ-001
**Decision**: {{DECISION_TEXT}}
**Rationale**: {{WHY_THIS_DECISION}}
**Alternatives Considered**: {{ALTERNATIVES}}
**Trade-offs**: {{TRADE_OFFS}}
```

### 3.4 Config files (implementer configuration)

**Location**: `design/config/{platform}/`

Configuration files needed by implementers.

**Types**:
- Environment variables (`.env.example`, NOT actual secrets)
- Build configurations
- Linting rules
- Code style definitions

**CRITICAL**: Never commit actual secrets. Only commit `.example` files.

### 3.5 Specs (technical specifications)

**Location**: `design/requirements/{platform}/specs/`

Technical specifications for each module.

**Naming convention**: `{module-id}.md`

**Spec structure**:
```markdown
# Specification: {{MODULE_NAME}}

## Overview

{{BRIEF_DESCRIPTION}}

## Functional Requirements

{{REQUIREMENTS}}

## Technical Design

{{TECHNICAL_DETAILS}}

## API Endpoints

{{API_DEFINITION}}

## Data Models

{{DATA_MODELS}}

## Error Handling

{{ERROR_CASES}}

## Testing Requirements

{{TEST_CASES}}
```
