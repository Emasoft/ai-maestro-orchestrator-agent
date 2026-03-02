# Agent Selection Guide


## Contents

- [Overview](#overview)
- [Use-Case Quick Reference](#use-case-quick-reference)
- [Table of Contents](#table-of-contents)
  - [Part 1: Language-Specific Agents](#part-1-language-specific-agents)
  - [Part 2: Specialized Agents](#part-2-specialized-agents)
  - [Part 3: Decision Tree & Selection](#part-3-decision-tree-selection)
  - [Part 4: Anti-Patterns & Best Practices](#part-4-anti-patterns-best-practices)
  - [Part 5: Advanced Topics & Troubleshooting](#part-5-advanced-topics-troubleshooting)
- [Quick Navigation by Problem](#quick-navigation-by-problem)
- [Summary: Golden Rules](#summary-golden-rules)
- [Remember](#remember)

---

## Overview

This guide helps orchestrators select the right specialized agent for each task. Making the correct agent selection is critical for task success, efficient resource utilization, and avoiding context contamination.

---

## Use-Case Quick Reference

**When to use this guide:**
- When you need to delegate a task to a specialized agent
- If you're unsure which agent handles Python/JS/Go/Rust work
- When choosing between search agents (hound, SERENA, context)
- If multiple agents conflict on git operations
- When test-writer creates too many tests
- If agent returns verbose output and crashes orchestrator
- When you need to run tests without blocking
- If you need to fix code quality issues

---

## Table of Contents

This guide is split into 5 parts for efficient progressive disclosure:

### Part 1: Language-Specific Agents
**File:** [agent-selection-guide-part1-language-agents.md](./agent-selection-guide-part1-language-agents.md)

**Contents:**
- 1.1 Python Projects (developer, test-writer, code-fixer, data-scientist)
- 1.2 JavaScript/TypeScript Projects (developer, test-writer, code-fixer, frontend)
- 1.3 Go Projects (developer, test-writer, code-fixer)
- 1.4 Rust Projects (developer, test-writer, code-fixer)
- 1.5 Native Platform Development (macOS, iOS, Windows, Android)
- 1.6 Language Selection Quick Reference

---

### Part 2: Specialized Agents
**File:** [agent-selection-guide-part2-specialized-agents.md](./agent-selection-guide-part2-specialized-agents.md)

**Contents:**
- 2.1 Code Quality Agents (python-code-fixer, js-code-fixer, go-code-fixer, rust-code-fixer)
- 2.2 Search and Analysis Agents (hound-agent, log-auditor, context-agent, serena-agent)
- 2.3 Testing Agents (test-writer, test-runner, ci-monitor)
- 2.4 DevOps and Infrastructure Agents (docker, kubernetes, terraform, github-actions)
- 2.5 Documentation Agents (doc-generator, readme-writer, tutorial-writer)
- 2.6 Agent Capability Matrix (core capabilities, tool expertise, domain expertise)

---

### Part 3: Decision Tree & Selection
**File:** [agent-selection-guide-part3-decision-selection.md](./agent-selection-guide-part3-decision-selection.md)

**Contents:**
- 3.1 Step 1: Identify Task Category (dev, quality, testing, search, devops, docs)
- 3.2 Step 2: Check Language Requirements
- 3.3 Step 3: Verify Parallelization Safety
- 3.4 Step 4: Determine Output Requirements
- 3.5 Step 5: Select Agent (selection formula with examples)
- 3.6 Agent Selection Checklist (pre-spawn verification)
- 3.7 Minimal Output Requirement Template

---

### Part 4: Anti-Patterns & Best Practices
**File:** [agent-selection-guide-part4-patterns-practices.md](./agent-selection-guide-part4-patterns-practices.md)

**Contents:**
- 4.1 Anti-Pattern 1: Using Orchestrator for Blocking Tasks
- 4.2 Anti-Pattern 2: Using Wrong Language Agent
- 4.3 Anti-Pattern 3: Parallel Git Operations
- 4.4 Anti-Pattern 4: Missing Test Count Specification
- 4.5 Anti-Pattern 5: Verbose Agent Output
- 4.6 Anti-Pattern 6: Using Scripts to Edit Files
- 4.7 Best Practice: Always Specify Minimal Output
- 4.8 Best Practice: Batch Related Tasks
- 4.9 Best Practice: Chain Agents for Complex Workflows
- 4.10 Best Practice: Use Appropriate Search Agents
- 4.11 Best Practice: Prevent Git Conflicts
- 4.12 Best Practice: Test Writer Agent
- 4.13 Best Practice: Code Fixer Agent
- 4.14 Best Practice: Log Auditor
- 4.15 Agent Coordination Patterns (Fan-Out, Pipeline, Map-Reduce, Supervisor-Worker)

---

### Part 5: Advanced Topics & Troubleshooting
**File:** [agent-selection-guide-part5-advanced.md](./agent-selection-guide-part5-advanced.md)

**Contents:**
- 5.1 Agent Composition (agents delegating to other agents)
- 5.2 Agent Lifecycle (spawn, execute, report, cleanup)
- 5.3 Agent Constraints (max parallel, context limits, timeouts)
- 5.4 Agent Communication (file system, git, logs, reports)
- 5.5 Troubleshooting: Agent Selection Errors
- 5.6 Troubleshooting: Selection Conflicts
- 5.7 Quick Reference Card (common selections, output templates)
- 5.8 Summary: Golden Rules

---

## Quick Navigation by Problem

| If you need to... | Go to... |
|-------------------|----------|
| Select a Python/JS/Go/Rust agent | [Part 1: Language Agents](./agent-selection-guide-part1-language-agents.md) |
| Choose between search agents | [Part 2: Specialized Agents](./agent-selection-guide-part2-specialized-agents.md) Section 2.2 |
| Decide which agent for a task | [Part 3: Decision Tree](./agent-selection-guide-part3-decision-selection.md) |
| Avoid parallel git conflicts | [Part 4: Anti-Patterns](./agent-selection-guide-part4-patterns-practices.md) Section 4.3 |
| Specify test count properly | [Part 4: Best Practices](./agent-selection-guide-part4-patterns-practices.md) Section 4.12 |
| Prevent verbose output crashes | [Part 4: Anti-Patterns](./agent-selection-guide-part4-patterns-practices.md) Section 4.5 |
| Debug agent selection errors | [Part 5: Troubleshooting](./agent-selection-guide-part5-advanced.md) Section 5.5 |
| Understand agent coordination | [Part 4: Patterns](./agent-selection-guide-part4-patterns-practices.md) Section 4.15 |

---

## Summary: Golden Rules

1. **Right agent for right task** - use capability matrix
2. **Minimal output** - 2 lines max to orchestrator
3. **Parallel when safe** - check for conflicts first
4. **Specify test counts** - avoid 30-tests-per-function default
5. **Chain agents** - complex workflows need pipelines
6. **Write to files** - detailed output goes to docs_dev/
7. **One task per agent** - clear, verifiable completion
8. **Never block orchestrator** - delegate, don't execute
9. **Fix before commit** - always run code-fixer agents
10. **Audit logs** - use log-auditor for test/CI output

---

## Remember

You are the orchestrator. Your job is to SELECT and COORDINATE agents, not to DO the work yourself. Choose wisely, delegate clearly, stay free to handle user requests and urgent issues.
