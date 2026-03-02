---
operation: select-agent-for-task
procedure: proc-decompose-design
workflow-instruction: Step 10 - Design Decomposition
parent-skill: eoa-orchestration-patterns
parent-plugin: emasoft-orchestrator-agent
version: 1.0.0
---

# Select Agent for Task


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify Task Category](#step-1-identify-task-category)
  - [Step 2: Check Language Requirements](#step-2-check-language-requirements)
  - [Step 3: Verify Parallelization Safety](#step-3-verify-parallelization-safety)
  - [Step 4: Determine Output Requirements](#step-4-determine-output-requirements)
  - [Step 5: Select Agent Using Formula](#step-5-select-agent-using-formula)
- [Checklist](#checklist)
- [Examples](#examples)
  - [Example: Python API Development](#example-python-api-development)
  - [Example: JavaScript Test Writing](#example-javascript-test-writing)
  - [Example: Code Search](#example-code-search)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## When to Use

Trigger this operation when:
- You have classified a task and need to assign it
- You need to choose between multiple specialized agents
- You are delegating work to implementer agents

## Prerequisites

- Task has been classified (simple/medium/complex)
- Task requirements are clear
- Available agents are known

## Procedure

### Step 1: Identify Task Category

Determine the primary task category:

| Category | Description | Example Tasks |
|----------|-------------|---------------|
| **Development** | Writing new code or features | Implement endpoint, add feature |
| **Quality** | Fixing code issues, linting | Fix lint errors, format code |
| **Testing** | Writing or running tests | Write unit tests, run e2e tests |
| **Search** | Finding code, patterns, information | Find all usages, search logs |
| **DevOps** | Infrastructure, deployment | Docker setup, CI pipeline |
| **Documentation** | Writing docs, README | Generate API docs |

### Step 2: Check Language Requirements

Match the task language to the appropriate agent:

| Language | Developer Agent | Test Writer | Code Fixer |
|----------|-----------------|-------------|------------|
| Python | python-developer | python-test-writer | python-code-fixer |
| JavaScript/TS | js-developer | js-test-writer | js-code-fixer |
| Go | go-developer | go-test-writer | go-code-fixer |
| Rust | rust-developer | rust-test-writer | rust-code-fixer |

### Step 3: Verify Parallelization Safety

Before spawning multiple agents, verify:

| Check | Safe | Unsafe |
|-------|------|--------|
| Git operations | One agent with git | Multiple agents with git |
| Same file | Reading only | Multiple agents writing |
| Dependencies | Independent | Shared mutable state |

**Rule:** Never spawn multiple agents that access git simultaneously.

### Step 4: Determine Output Requirements

Specify minimal output requirements:

```
Return a minimal report: 1-2 lines max, no code blocks, no verbose output.
Format: `[DONE/FAILED] task_name - brief_result`.
If you need to report details, write them to a .md file in docs_dev/ and tell me the filename.
```

### Step 5: Select Agent Using Formula

**Selection Formula:**
```
Agent = Category + Language + Specialization
```

**Examples:**
- Development + Python + API = python-developer
- Quality + Python + Lint = python-code-fixer
- Testing + JavaScript + Unit = js-test-writer
- Search + Any + Code = hound-agent or serena-agent
- Search + Any + Logs = log-auditor

## Checklist

Copy this checklist and track your progress:
- [ ] Identify task category (dev/quality/test/search/devops/docs)
- [ ] Determine language requirements
- [ ] Check parallelization safety (no git conflicts)
- [ ] Specify minimal output requirements in prompt
- [ ] Select agent using formula
- [ ] Include one clear task with success criteria

## Examples

### Example: Python API Development

**Task:** "Implement user profile endpoint"
**Category:** Development
**Language:** Python
**Agent:** python-developer

**Prompt:**
```
Implement the user profile endpoint in src/api/profile.py.

Requirements:
- GET /api/profile returns current user profile
- PATCH /api/profile updates user profile fields
- Include validation for email and username

Return a minimal report: 1-2 lines max.
Format: [DONE/FAILED] implement-profile-endpoint - brief_result
```

### Example: JavaScript Test Writing

**Task:** "Write tests for auth module"
**Category:** Testing
**Language:** JavaScript
**Agent:** js-test-writer

**Prompt:**
```
Write unit tests for src/auth/login.ts.

Requirements:
- Test successful login flow
- Test invalid credentials handling
- Test session creation
- CREATE EXACTLY 5 TESTS (do not create 30 per function!)

Return a minimal report: 1-2 lines max.
Format: [DONE/FAILED] auth-tests - brief_result
```

### Example: Code Search

**Task:** "Find all usages of deprecated API"
**Category:** Search
**Agent:** hound-agent (for large searches) or serena-agent (for symbol search)

**Prompt:**
```
Find all usages of the deprecated `legacyAuth()` function across the codebase.

Return: List of file paths and line numbers.
Write results to docs_dev/legacy-auth-usages.md
Report: [DONE/FAILED] legacy-auth-search - count of usages found
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Wrong agent selected | Misidentified language/category | Re-assess task, select correct agent |
| Agent returns verbose output | Missing minimal output instruction | Always include output format in prompt |
| Git conflict | Multiple agents with git access | Serialize git operations, one agent at a time |
| 30 tests created | Missing test count specification | Always specify exact test count for test-writers |

## Related Operations

- [op-classify-task-complexity.md](op-classify-task-complexity.md) - Classify before selecting
- [op-define-scope-boundaries.md](op-define-scope-boundaries.md) - Define clear scope for agent
- [op-identify-task-dependencies.md](op-identify-task-dependencies.md) - Check dependencies before parallelizing
