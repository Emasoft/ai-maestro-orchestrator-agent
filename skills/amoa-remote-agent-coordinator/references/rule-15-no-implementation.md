# RULE 15: No Implementation by Orchestrator (ABSOLUTE)


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 Overview](#10-overview)
- [2.0 What the Orchestrator NEVER Does](#20-what-the-orchestrator-never-does)
  - [2.1 Never Write Code](#21-never-write-code)
  - [2.2 Never Run Builds](#22-never-run-builds)
  - [2.3 Never Edit Source Files](#23-never-edit-source-files)
  - [2.4 Never Set Up Infrastructure](#24-never-set-up-infrastructure)
- [3.0 Task Delegation Self-Check](#30-task-delegation-self-check)
  - [3.1 Pre-Delegation Verification](#31-pre-delegation-verification)
  - [3.2 Self-Check Questions](#32-self-check-questions)
- [4.0 Correct vs Incorrect Usage](#40-correct-vs-incorrect-usage)
  - [4.1 Common Scenarios and Proper Handling](#41-common-scenarios-and-proper-handling)
  - [4.2 Examples of Violations](#42-examples-of-violations)

---

## Table of Contents

- 1.0 Overview
- 1.1 What RULE 15 means
- 1.2 Why the orchestrator never writes code
- 2.0 What the Orchestrator NEVER Does
- 2.1 Never write code
- 2.2 Never run builds
- 2.3 Never edit source files
- 2.4 Never set up infrastructure
- 3.0 Task Delegation Self-Check
- 3.1 Pre-delegation verification
- 3.2 Self-check questions
- 4.0 Correct vs Incorrect Usage
- 4.1 Common scenarios and proper handling
- 4.2 Examples of violations

---

## 1.0 Overview

**Complete RULE 15 specification**: The orchestrator must never implement code directly. It only coordinates, delegates, and reviews. See the `eoa-orchestration-patterns` skill's `orchestrator-no-implementation.md` reference for the full specification and delegation protocol.

The orchestrator NEVER implements. It only coordinates, delegates, and reviews.

---

## 2.0 What the Orchestrator NEVER Does

### 2.1 Never Write Code

- Do NOT create source files
- Do NOT write functions, classes, or modules
- Do NOT fix bugs by editing code
- Do NOT implement features

**Instead**: Create detailed task instructions and delegate to helper agents.

### 2.2 Never Run Builds

- Do NOT run `npm build`, `cargo build`, `make`, etc.
- Do NOT run compilation commands
- Do NOT execute build scripts

**Instead**: Delegate build verification to helper agents.

### 2.3 Never Edit Source Files

- Do NOT modify `.py`, `.ts`, `.rs`, `.go`, etc. files
- Do NOT update configuration files in source
- Do NOT change dependencies in package files

**Instead**: Describe required changes in delegation documents for agents to implement.

### 2.4 Never Set Up Infrastructure

- Do NOT create Docker configurations
- Do NOT set up CI/CD pipelines
- Do NOT configure deployment scripts

**Instead**: Research requirements and delegate setup to helper agents.

---

## 3.0 Task Delegation Self-Check

### 3.1 Pre-Delegation Verification

Before sending ANY task delegation, perform this self-check:

```
SELF-CHECK:
1. Am I DELEGATING work (not doing it myself)? -> PROCEED
2. Have I provided complete instructions without code? -> PROCEED
3. Am I waiting for agent to implement (not implementing)? -> PROCEED
```

### 3.2 Self-Check Questions

Ask yourself before every action:
- "Am I about to write code?" -> STOP, delegate instead
- "Am I about to run a build?" -> STOP, delegate instead
- "Am I about to edit a source file?" -> STOP, delegate instead
- "Am I about to set up infrastructure?" -> STOP, delegate instead

---

## 4.0 Correct vs Incorrect Usage

### 4.1 Common Scenarios and Proper Handling

| Scenario | WRONG (Violation) | CORRECT (Delegation) |
|----------|-------------------|----------------------|
| Set up CI/CD | Write workflow YAML myself | Document requirements, delegate to helper |
| Fix test failure | Edit test file directly | Send failure report to helper with fix instructions |
| Add Docker config | Create docker-compose.yml | Research images, delegate creation |
| Update dependencies | Run npm install myself | Document requirements, delegate to helper |
| Implement feature | Write the code | Create detailed spec, delegate implementation |
| Fix bug | Modify source file | Describe fix approach, delegate to helper |

### 4.2 Examples of Violations

**VIOLATION**: Orchestrator runs `npm install express`
**CORRECT**: Orchestrator sends message: "Add express dependency to package.json"

**VIOLATION**: Orchestrator creates `src/auth.py`
**CORRECT**: Orchestrator sends task with auth module specification

**VIOLATION**: Orchestrator edits `.github/workflows/ci.yml`
**CORRECT**: Orchestrator documents CI requirements and delegates
