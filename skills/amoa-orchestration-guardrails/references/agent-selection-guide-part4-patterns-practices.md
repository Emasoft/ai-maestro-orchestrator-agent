# Agent Selection Guide - Part 4: Anti-Patterns & Best Practices


## Contents

- [Use-Case Quick Reference for This Section](#use-case-quick-reference-for-this-section)
- [Anti-Patterns](#anti-patterns)
  - [WRONG Agent Selections](#wrong-agent-selections)
    - [Anti-Pattern 1: Using Orchestrator for Blocking Tasks](#anti-pattern-1-using-orchestrator-for-blocking-tasks)
    - [Anti-Pattern 2: Using Wrong Language Agent](#anti-pattern-2-using-wrong-language-agent)
    - [Anti-Pattern 3: Parallel Git Operations](#anti-pattern-3-parallel-git-operations)
    - [Anti-Pattern 4: Missing Test Count Specification](#anti-pattern-4-missing-test-count-specification)
    - [Anti-Pattern 5: Verbose Agent Output](#anti-pattern-5-verbose-agent-output)
    - [Anti-Pattern 6: Using Scripts to Edit Files](#anti-pattern-6-using-scripts-to-edit-files)
- [Best Practices](#best-practices)
  - [1. Always Specify Minimal Output](#1-always-specify-minimal-output)
  - [2. Batch Related Tasks](#2-batch-related-tasks)
  - [3. Chain Agents for Complex Workflows](#3-chain-agents-for-complex-workflows)
  - [4. Use Appropriate Search Agents](#4-use-appropriate-search-agents)
  - [5. Prevent Git Conflicts](#5-prevent-git-conflicts)
  - [6. Test Writer Agent Best Practices](#6-test-writer-agent-best-practices)
  - [7. Code Fixer Agent Best Practices](#7-code-fixer-agent-best-practices)
  - [8. Log Auditor Best Practices](#8-log-auditor-best-practices)
  - [9. Agent Coordination Patterns](#9-agent-coordination-patterns)
    - [Pattern A: Fan-Out (Parallel)](#pattern-a-fan-out-parallel)
    - [Pattern B: Pipeline (Sequential)](#pattern-b-pipeline-sequential)
    - [Pattern C: Map-Reduce](#pattern-c-map-reduce)
    - [Pattern D: Supervisor-Worker](#pattern-d-supervisor-worker)
- [Related Files](#related-files)

---

## Use-Case Quick Reference for This Section

**When to use this file:**
- If multiple agents conflict on git operations
- When test-writer creates too many tests
- If agent returns verbose output and crashes orchestrator
- When you need to run tests without blocking
- If you need to fix code quality issues
- When learning agent coordination patterns

---

## Anti-Patterns

### WRONG Agent Selections

#### Anti-Pattern 1: Using Orchestrator for Blocking Tasks

**WRONG:**
```
User: "Run the test suite"
Orchestrator: [Runs tests directly, blocks for 10 minutes]
```

**CORRECT:**
```
User: "Run the test suite"
Orchestrator: [Spawns test-runner agent]
test-runner: [Runs tests, writes to logs/test_2025-01-01_14-30-00.log]
test-runner: [Calls log-auditor with log path]
log-auditor: [Returns summary]
test-runner: → "[DONE] test-suite - 45/50 passed, see logs/test_2025-01-01_14-30-00.log"
```

---

#### Anti-Pattern 2: Using Wrong Language Agent

**WRONG:**
```
Task: "Fix TypeScript type errors"
Selected: python-code-fixer
```

**CORRECT:**
```
Task: "Fix TypeScript type errors"
Selected: js-code-fixer
```

---

#### Anti-Pattern 3: Parallel Git Operations

**WRONG:**
```
[Spawn 10 agents that all run git commands]
Result: Auth conflicts, corrupted git state
```

**CORRECT:**
```
[Spawn agents for file edits only]
[One final agent runs git commit after all edits complete]
```

---

#### Anti-Pattern 4: Missing Test Count Specification

**WRONG:**
```
Prompt: "Write tests for user module"
Result: Agent creates 30 tests per function (hundreds of tests!)
```

**CORRECT:**
```
Prompt: "Write 10 tests total for user module (2 per function)"
Result: Agent creates exactly 10 tests
```

---

#### Anti-Pattern 5: Verbose Agent Output

**WRONG:**
```
Agent returns: [500 lines of test output, stack traces, verbose logs]
Result: Orchestrator context consumed, crashes
```

**CORRECT:**
```
Agent returns: "[DONE] python-code-fixer - Fixed 12 issues in auth.py"
Details in: docs_dev/code-fix-report-2025-01-01.md
```

---

#### Anti-Pattern 6: Using Scripts to Edit Files

**WRONG:**
```
Orchestrator: [Creates Python script to edit files with regex]
Result: Bugs, corrupted files, no visibility into changes
```

**CORRECT:**
```
Orchestrator: [Spawns python-code-fixer agent per file]
Result: Visible edits, proper formatting, type-safe changes
```

---

## Best Practices

### 1. Always Specify Minimal Output

Every agent prompt must include:
```
"Return a minimal report: 1-2 lines max, no code blocks, no verbose output.
Format: `[DONE/FAILED] task_name - brief_result`.
If you need to report details, write them to a .md file in docs_dev/
or scripts_dev/ and just tell me the filename.
NEVER return more than 2 lines of text to the orchestrator."
```

---

### 2. Batch Related Tasks

**GOOD:**
```
[Spawn 20 python-code-fixer agents in parallel, one per file]
All complete in ~30 seconds
```

**BAD:**
```
[Spawn 1 python-code-fixer agent to fix 20 files sequentially]
Takes 10 minutes
```

---

### 3. Chain Agents for Complex Workflows

```
Workflow: Run tests → Analyze failures → Fix code → Re-run tests

Agent Chain:
1. test-runner → runs tests, writes logs/test_TIMESTAMP.log
2. log-auditor → reads logs, identifies failing tests
3. python-code-fixer → fixes identified issues
4. test-runner → re-runs tests, confirms fixes
```

---

### 4. Use Appropriate Search Agents

```
SERENA MCP (know names):
- find_symbol("UserAuthentication")
- find_referencing_symbols("login_user")

CONTEXT MCP (vague descriptions):
- "Find the function that validates email addresses"
- "Locate the class that handles database connections"

HOUND AGENT (large files):
- Search 500KB XML config files
- Find patterns in large JSON datasets
```

---

### 5. Prevent Git Conflicts

```
RULE: Only ONE agent can perform git operations at a time

Sequential Git Operations:
1. [All edit agents complete]
2. [Spawn ONE git-commit agent]
3. [Git agent commits all changes]

NEVER:
[Multiple agents running `git add`, `git commit` simultaneously]
```

---

### 6. Test Writer Agent Best Practices

```
ALWAYS SPECIFY TEST COUNT:
WRONG: "Write tests for calculator.py"
CORRECT: "Write 8 tests for calculator.py (2 per function: add, subtract, multiply, divide)"

SPECIFY TEST TYPES:
WRONG: "Write tests for API"
CORRECT: "Write 5 unit tests and 3 integration tests for API endpoints"

PROVIDE CONTEXT:
WRONG: "Write tests"
CORRECT: "Write 10 tests for auth.py focusing on edge cases:
    - empty passwords
    - SQL injection
    - rate limiting
    - session expiry"
```

---

### 7. Code Fixer Agent Best Practices

```
WHEN TO USE:
- After ANY file edits (always)
- Before git commits (always)
- After merging branches
- After dependency updates

HOW TO USE:
- One agent per file (parallel safe)
- Specify exact file paths
- Run AFTER edits, BEFORE tests

EXAMPLE:
[Edit auth.py, models.py, utils.py]
[Spawn 3 python-code-fixer agents in parallel]
  Agent 1: "Fix auth.py"
  Agent 2: "Fix models.py"
  Agent 3: "Fix utils.py"
[All complete, code is clean]
```

---

### 8. Log Auditor Best Practices

```
USE FOR:
- Test run analysis
- CI/CD failure diagnosis
- Error pattern detection
- Performance bottleneck identification

INPUT:
- Path to log file (always)
- Optional: specific patterns to search

OUTPUT:
- Error count + types
- Critical issues (always)
- Recommendations (if applicable)

EXAMPLE:
test-runner → logs/test_2025-01-01.log
log-auditor(logs/test_2025-01-01.log) →
  "[DONE] log-audit - 3 failures: 2x AssertionError (auth.py:42, auth.py:67),
   1x TimeoutError (api.py:103). Details in docs_dev/log-audit-2025-01-01.md"
```

---

### 9. Agent Coordination Patterns

#### Pattern A: Fan-Out (Parallel)
```
Orchestrator
├─→ Agent 1 (file1.py)
├─→ Agent 2 (file2.py)
├─→ Agent 3 (file3.py)
└─→ Agent 4 (file4.py)

All agents run simultaneously, return minimal reports.
Use when: Editing multiple independent files
```

#### Pattern B: Pipeline (Sequential)
```
Orchestrator → Agent 1 → Agent 2 → Agent 3 → Agent 4

Each agent depends on previous output.
Use when: Edit → Fix → Test → Commit
```

#### Pattern C: Map-Reduce
```
Orchestrator
├─→ Worker 1 (chunk 1) ┐
├─→ Worker 2 (chunk 2) ├─→ Aggregator → Result
├─→ Worker 3 (chunk 3) ┘

Workers process in parallel, aggregator combines.
Use when: Large dataset analysis, bulk operations
```

#### Pattern D: Supervisor-Worker
```
Orchestrator → Supervisor Agent
                ├─→ Worker 1
                ├─→ Worker 2
                └─→ Worker 3

Supervisor manages workers, reports summary to orchestrator.
Use when: Complex multi-step tasks with dependencies
```

---

## Related Files

- [Part 1: Language Agents](./agent-selection-guide-part1-language-agents.md) - Language-specific developer agents
- [Part 2: Specialized Agents](./agent-selection-guide-part2-specialized-agents.md) - Code quality, search, testing, DevOps agents
- [Part 3: Decision & Selection](./agent-selection-guide-part3-decision-selection.md) - Decision tree and selection checklist
- [Part 5: Advanced Topics](./agent-selection-guide-part5-advanced.md) - Advanced topics and troubleshooting
- [Index](./agent-selection-guide.md) - Main overview and quick reference
