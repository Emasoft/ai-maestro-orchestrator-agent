---
operation: classify-task-complexity
procedure: proc-decompose-design
workflow-instruction: Step 10 - Design Decomposition
parent-skill: eoa-orchestration-patterns
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Classify Task Complexity


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Initial Assessment](#step-1-initial-assessment)
  - [Step 2: Count Complexity Signals](#step-2-count-complexity-signals)
  - [Step 3: Apply Classification](#step-3-apply-classification)
  - [Step 4: Choose Action Pattern](#step-4-choose-action-pattern)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: Simple Task - Add Logging](#example-simple-task-add-logging)
  - [Example: Medium Task - New API Endpoint](#example-medium-task-new-api-endpoint)
  - [Example: Complex Task - Cross-Platform Feature](#example-complex-task-cross-platform-feature)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You receive a new task or feature request
- You need to decide how much planning investment a task requires
- You are unsure whether to delegate directly or plan first

## Prerequisites

- Task description or feature request available
- Understanding of the project's technology stack
- Knowledge of available agents and their capabilities

## Procedure

### Step 1: Initial Assessment

Ask these five questions:
1. How many languages/platforms are involved?
2. What dependencies are required (standard lib vs external vs integrations)?
3. How many files/modules will be affected?
4. Are there external integration points?
5. What architecture decisions are needed?

### Step 2: Count Complexity Signals

Count how many of these signals are present:
- Multiple languages: +1
- Multi-platform native code: +1
- External integrations (APIs, services): +1
- Cross-module changes: +1
- Architecture decisions required: +1
- 10+ files affected: +1

**Scoring:**
- 0-1 signals: Simple
- 2-3 signals: Medium
- 4+ signals: Complex

### Step 3: Apply Classification

| Classification | Characteristics | Action |
|----------------|-----------------|--------|
| **Simple** | Single language, standard libs, 1-3 files, clear scope | Skip formal planning, delegate directly |
| **Medium** | Single language with external deps, 4-10 files, basic architecture | Brief 5-minute planning, then single agent |
| **Complex** | Multiple languages/platforms, integrations, 10+ files, architecture decisions | Full planning process, team orchestration |

### Step 4: Choose Action Pattern

**Simple Task:**
```
Simple task detected:
-> Direct delegation to specialized agent
-> No planning overhead
-> Fast execution
```

**Medium Task:**
```
Medium task detected:
-> 5-minute planning phase (architecture sketch)
-> Delegate to single developer agent
-> Optional parallel testing agent
-> Brief review before completion
```

**Complex Task:**
```
Complex task detected:
-> Planning phase: Architecture design, dependency analysis, task breakdown
-> Team formation: Assign specialized agents to parallel workstreams
-> Coordination: Regular checkpoints, integration verification
-> Testing: Multi-layer testing strategy (unit, integration, e2e)
-> Review: Comprehensive code review and validation
```

## Checklist

Copy this checklist and track your progress:
- [ ] Read the task description completely
- [ ] Answer the 5 initial assessment questions
- [ ] Count complexity signals present
- [ ] Determine classification (Simple/Medium/Complex)
- [ ] Choose action pattern based on classification
- [ ] Document classification decision with reasoning

## Examples

### Example: Simple Task - Add Logging

**Task:** "Add debug logging to track function entry/exit in auth.py"

**Assessment:**
- Languages: 1 (Python)
- Dependencies: Standard `logging` library
- Files: 1 (auth.py)
- Integrations: None
- Architecture: None needed

**Signals:** 0
**Classification:** Simple
**Action:** Direct delegation to python-developer agent

### Example: Medium Task - New API Endpoint

**Task:** "Implement new API endpoint for user profile updates"

**Assessment:**
- Languages: 1 (Python/FastAPI)
- Dependencies: FastAPI framework, Pydantic
- Files: 4-6 (route, service, tests, schema)
- Integrations: Existing ORM
- Architecture: Minor (follows existing patterns)

**Signals:** 2 (external deps, some architecture)
**Classification:** Medium
**Action:** Brief planning + single developer agent

### Example: Complex Task - Cross-Platform Feature

**Task:** "Add real-time sync across web and mobile apps"

**Assessment:**
- Languages: 3 (Python backend, TypeScript web, Swift mobile)
- Dependencies: WebSocket server, sync library
- Files: 15+ across modules
- Integrations: External push notification service
- Architecture: Major (sync protocol, conflict resolution)

**Signals:** 5
**Classification:** Complex
**Action:** Full planning + team orchestration

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Under-classified task | Task more complex than assessed | Re-assess with more investigation, escalate classification |
| Over-classified task | Task simpler than assessed | De-escalate classification, reduce planning overhead |
| Unclear scope | Requirements ambiguous | Request clarification before classification |
| Missing context | Unknown tech stack | Research codebase before assessment |

## Related Operations

- [op-select-agent-for-task.md](op-select-agent-for-task.md) - Select agent after classification
- [op-decompose-goals-to-modules.md](op-decompose-goals-to-modules.md) - Decompose complex tasks
- [op-define-scope-boundaries.md](op-define-scope-boundaries.md) - Define boundaries for medium/complex tasks
