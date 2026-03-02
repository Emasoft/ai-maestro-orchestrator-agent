# Delegation Checklist Reference


## Contents

- [Table of Contents](#table-of-contents)
- [1.0 General Delegation Checklist](#10-general-delegation-checklist)
  - [Pre-Delegation Requirements](#pre-delegation-requirements)
  - [Delegation Document Contents](#delegation-document-contents)
  - [Post-Delegation Actions](#post-delegation-actions)
- [2.0 Infrastructure Tasks](#20-infrastructure-tasks)
  - [2.1 Docker Setup Delegation](#21-docker-setup-delegation)
- [Task: Docker Multi-Platform Setup](#task-docker-multi-platform-setup)
  - [Objective](#objective)
  - [Required Services](#required-services)
  - [Volume Mounts](#volume-mounts)
  - [Commands Per Service](#commands-per-service)
  - [Acceptance Criteria](#acceptance-criteria)
  - [2.2 CI/CD Pipeline Delegation](#22-cicd-pipeline-delegation)
- [Task: CI/CD Pipeline Setup](#task-cicd-pipeline-setup)
  - [Objective](#objective)
  - [Trigger Events](#trigger-events)
  - [Matrix Configuration](#matrix-configuration)
  - [Jobs](#jobs)
  - [Acceptance Criteria](#acceptance-criteria)
  - [2.3 Development Environment Delegation](#23-development-environment-delegation)
- [3.0 Code Tasks](#30-code-tasks)
  - [3.1 New Feature Delegation](#31-new-feature-delegation)
- [Task: Implement Directory Sorting Feature](#task-implement-directory-sorting-feature)
  - [Objective](#objective)
  - [Interface Contract](#interface-contract)
  - [Files to Modify](#files-to-modify)
  - [Test Requirements](#test-requirements)
  - [3.2 Bug Fix Delegation](#32-bug-fix-delegation)
- [Task: Fix Windows Path Handling Bug](#task-fix-windows-path-handling-bug)
  - [Bug Description](#bug-description)
  - [Reproduction](#reproduction)
  - [Root Cause Analysis](#root-cause-analysis)
  - [Files to Modify](#files-to-modify)
  - [Verification](#verification)
  - [3.3 Refactoring Delegation](#33-refactoring-delegation)
- [4.0 Testing Tasks](#40-testing-tasks)
  - [4.1 Test Suite Setup Delegation](#41-test-suite-setup-delegation)
  - [4.2 Test Execution Delegation](#42-test-execution-delegation)
  - [4.3 Test Fix Delegation](#43-test-fix-delegation)
- [5.0 Documentation Tasks](#50-documentation-tasks)
- [6.0 Pre-Delegation Self-Check](#60-pre-delegation-self-check)
  - [Final Checklist Before Sending](#final-checklist-before-sending)
- [Pre-Send Self-Check](#pre-send-self-check)
  - [RULE 15 Compliance](#rule-15-compliance)
  - [Delegation Quality](#delegation-quality)
  - [Communication Protocol](#communication-protocol)
  - [Tracking](#tracking)
- [Quick Reference: Orchestrator Role](#quick-reference-orchestrator-role)
- [Related Documents](#related-documents)

---

**Purpose**: Checklists for delegating common task types while maintaining RULE 15 compliance.

---

## Table of Contents

- 1.0 General Delegation Checklist
- 2.0 Infrastructure Tasks
  - 2.1 Docker Setup
  - 2.2 CI/CD Pipeline
  - 2.3 Development Environment
- 3.0 Code Tasks
  - 3.1 New Feature
  - 3.2 Bug Fix
  - 3.3 Refactoring
- 4.0 Testing Tasks
  - 4.1 Test Suite Setup
  - 4.2 Test Execution
  - 4.3 Test Fix
- 5.0 Documentation Tasks
- 6.0 Pre-Delegation Self-Check

---

## 1.0 General Delegation Checklist

Use this checklist before EVERY delegation:

### Pre-Delegation Requirements

- [ ] **RULE 15 Self-Check**: Am I delegating (not implementing)?
- [ ] **Research Complete**: I understand what needs to be done
- [ ] **Requirements Clear**: I can describe exactly what is needed
- [ ] **Success Criteria Defined**: I know how to verify completion
- [ ] **Agent Selected**: I know which agent should do this work

### Delegation Document Contents

- [ ] **Task Overview**: Clear summary of what to do
- [ ] **Context**: Why this task exists
- [ ] **Scope**: Exact boundaries (DO and DO NOT)
- [ ] **Files to Modify**: Specific file paths
- [ ] **Acceptance Criteria**: How to know when done
- [ ] **Verification Commands**: Commands to run to verify
- [ ] **Git Workflow**: Branch name, PR instructions
- [ ] **Communication Protocol**: ACK, status updates, completion report

### Post-Delegation Actions

- [ ] **ACK Received**: Agent acknowledged within timeout
- [ ] **Task Tracked**: Added to project tracking system
- [ ] **Monitoring Scheduled**: Will check for status updates

---

## 2.0 Infrastructure Tasks

### 2.1 Docker Setup Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Check existing Docker files
Glob: pattern="**/Dockerfile*"
Glob: pattern="**/docker-compose*.yml"

# Check CI usage of Docker
Grep: pattern="docker" path=".github/workflows"

# Research required images
WebSearch: "electronuserland/builder docker images"
```

**Delegation Document Requirements**:

- [ ] **Images Needed**: List exact Docker image names and tags
- [ ] **Services Needed**: Define each service (build, test, etc.)
- [ ] **Volumes Required**: What needs to be mounted
- [ ] **Environment Variables**: What env vars are needed
- [ ] **Commands**: What each service should run
- [ ] **Integration Points**: How services connect to CI/CD

**Example Delegation**:
```markdown
## Task: Docker Multi-Platform Setup

### Objective
Create Docker Compose configuration for cross-platform builds.

### Required Services
1. `build-linux-x64` - electronuserland/builder:20
2. `build-windows-x64` - electronuserland/builder:wine
3. `test-linux-x64` - same as build, runs tests
4. `test-windows-x64` - same as build, runs tests

### Volume Mounts
- Project root: /project
- Electron cache: /root/.cache/electron

### Commands Per Service
[Provide exact commands for each service]

### Acceptance Criteria
- [ ] docker-compose.yml created
- [ ] All services build successfully
- [ ] Tests run in each container
- [ ] Documentation added to README
```

### 2.2 CI/CD Pipeline Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Check existing workflows
Read: .github/workflows/ci.yml

# Check project requirements
Read: package.json  # or Cargo.toml, etc.

# Research CI patterns
WebSearch: "GitHub Actions matrix builds electron"
```

**Delegation Document Requirements**:

- [ ] **Trigger Events**: push, PR, manual, schedule
- [ ] **Matrix Dimensions**: OS, architecture, language version
- [ ] **Jobs Required**: build, test, lint, deploy
- [ ] **Dependencies**: Which jobs depend on others
- [ ] **Secrets Needed**: What secrets are required
- [ ] **Artifact Handling**: What to upload/download

**Example Delegation**:
```markdown
## Task: CI/CD Pipeline Setup

### Objective
Create GitHub Actions workflow for cross-platform CI.

### Trigger Events
- push to main
- pull_request to main

### Matrix Configuration
| OS | Platform | Architecture |
|----|----------|--------------|
| macos-14 | mac | arm64 |
| macos-13 | mac | x64 |
| ubuntu-latest | linux | x64 |
| windows-latest | win | x64 |

### Jobs
1. `build-rust-cli` - Build Rust CLI for all platforms
2. `build-electron` - Build Electron app (needs rust CLI)
3. `test-electron` - Run tests on built apps

### Acceptance Criteria
- [ ] Workflow file created
- [ ] All matrix combinations pass
- [ ] Artifacts uploaded correctly
- [ ] PR created with documentation
```

### 2.3 Development Environment Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Check existing tooling
Read: package.json
Read: tsconfig.json
Read: .eslintrc.json

# Understand project structure
Glob: pattern="src/**/*.ts" | head -20
```

**Delegation Document Requirements**:

- [ ] **Language/Runtime**: Versions and installation
- [ ] **Package Manager**: npm, pnpm, yarn, cargo, etc.
- [ ] **Linters/Formatters**: ESLint, Prettier, ruff, etc.
- [ ] **Build Tools**: tsc, webpack, vite, cargo, etc.
- [ ] **Test Framework**: jest, vitest, pytest, etc.
- [ ] **Editor Config**: .editorconfig, VSCode settings

---

## 3.0 Code Tasks

### 3.1 New Feature Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Understand existing architecture
Read: src/main/index.ts
Grep: pattern="export class" path="src/"

# Find related functionality
SERENA: find_symbol "FeatureManager"
```

**Delegation Document Requirements**:

- [ ] **Feature Description**: What the feature does
- [ ] **Architecture Fit**: How it fits existing code
- [ ] **Interface Contract**: Function signatures, types
- [ ] **Files to Create/Modify**: Exact paths
- [ ] **Dependencies**: New packages needed (if any)
- [ ] **Test Requirements**: What tests to write
- [ ] **Documentation**: What docs to update

**Example Delegation**:
```markdown
## Task: Implement Directory Sorting Feature

### Objective
Add sorting capability to directory listing.

### Interface Contract
```typescript
// New function in src/main/file-system.ts
function sortEntries(
  entries: FileEntry[],
  sortBy: 'name' | 'size' | 'date',
  order: 'asc' | 'desc'
): FileEntry[]
```

### Files to Modify
- src/main/file-system.ts - Add sortEntries function
- src/shared/types.ts - Add SortOptions type
- src/renderer/components/FileList.tsx - Add sort controls

### Test Requirements
- [ ] Unit tests for sortEntries with each sort field
- [ ] Test ascending and descending order
- [ ] Test with empty array
- [ ] Test with single item
```

### 3.2 Bug Fix Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Read error logs or CI output
Read: test-logs/failure.log

# Find affected code
Grep: pattern="functionName" output_mode="content"

# Understand the bug context
Read: src/module/affected-file.ts
```

**Delegation Document Requirements**:

- [ ] **Bug Description**: What's broken
- [ ] **Reproduction Steps**: How to trigger
- [ ] **Expected Behavior**: What should happen
- [ ] **Actual Behavior**: What happens now
- [ ] **Root Cause Analysis**: Likely cause (from research)
- [ ] **Affected Files**: Where fix likely needs to go
- [ ] **Verification**: How to confirm fix works

**Example Delegation**:
```markdown
## Task: Fix Windows Path Handling Bug

### Bug Description
Path separators break on Windows when listing directories.

### Reproduction
1. Run app on Windows
2. Navigate to C:\Users\...
3. Observe: Path shows C:/Users/... with wrong separators

### Root Cause Analysis
The `normalizePath()` function uses `/` unconditionally.
Should use `path.sep` for OS-specific separator.

### Files to Modify
- src/main/file-system.ts:42 - normalizePath function

### Verification
- [ ] Unit test with Windows-style paths passes
- [ ] Manual test on Windows shows correct separators
```

### 3.3 Refactoring Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Understand current structure
SERENA: get_symbols_overview "src/legacy/module.ts"

# Find all usages
SERENA: find_referencing_symbols "LegacyClass" "src/legacy/module.ts"
```

**Delegation Document Requirements**:

- [ ] **Refactoring Goal**: Why refactoring
- [ ] **Before State**: Current structure
- [ ] **After State**: Desired structure
- [ ] **Affected Files**: All files that need changes
- [ ] **Breaking Changes**: What interfaces change
- [ ] **Migration Path**: How callers should update
- [ ] **Test Coverage**: Ensure tests cover refactored code

---

## 4.0 Testing Tasks

### 4.1 Test Suite Setup Delegation

**Delegation Document Requirements**:

- [ ] **Test Framework**: Which framework to use
- [ ] **Test Directory Structure**: Where tests go
- [ ] **Configuration**: Test config files needed
- [ ] **Scripts**: npm/cargo scripts to add
- [ ] **CI Integration**: How tests run in CI
- [ ] **Coverage Requirements**: Minimum coverage threshold

### 4.2 Test Execution Delegation

**Delegation Document Requirements**:

- [ ] **Which Tests**: Unit, integration, e2e, all?
- [ ] **Environment Setup**: What needs to be running
- [ ] **Commands**: Exact test commands
- [ ] **Output Format**: How to report results
- [ ] **Failure Handling**: What to do if tests fail

### 4.3 Test Fix Delegation

**Orchestrator Research Phase** (ALLOWED):
```bash
# Read test failure output
Read: test-logs/latest.log

# Find the failing test
Grep: pattern="FAIL.*test_name"
```

**Delegation Document Requirements**:

- [ ] **Failing Test**: Name and location
- [ ] **Failure Output**: Error message and stack trace
- [ ] **Root Cause Analysis**: Why it's failing
- [ ] **Fix Approach**: How to fix
- [ ] **Verification**: Run test, should pass

---

## 5.0 Documentation Tasks

**Note**: Documentation tasks are the ONE area where orchestrators MAY do work directly, but ONLY for orchestrator-level documentation (plans, specs, delegation docs).

**Orchestrator CAN Write**:
- Project plans and specifications
- Task delegation documents
- Architecture decision records
- Meeting notes and summaries
- Status reports

**Orchestrator Should DELEGATE**:
- API documentation (from code)
- README updates (about code changes)
- Code comments and docstrings
- Changelog entries (from commits)
- Tutorial content (requires running code)

---

## 6.0 Pre-Delegation Self-Check

### Final Checklist Before Sending

Run through this checklist for EVERY delegation:

```markdown
## Pre-Send Self-Check

### RULE 15 Compliance
- [ ] I am NOT writing code myself
- [ ] I am NOT running builds myself
- [ ] I am NOT editing source files myself
- [ ] All implementation will be done by the agent

### Delegation Quality
- [ ] Task description is clear and complete
- [ ] Acceptance criteria are verifiable
- [ ] All necessary context is provided
- [ ] File paths are specific (not vague)
- [ ] Commands are exact (not pseudocode)

### Communication Protocol
- [ ] ACK instructions included
- [ ] Reporting requirements clear
- [ ] Priority stated (no deadlines per RULE 13)
- [ ] Escalation path defined

### Tracking
- [ ] Task added to project tracker
- [ ] Related GitHub issue linked
- [ ] Will monitor for status updates
```

---

## Quick Reference: Orchestrator Role

| Phase | Orchestrator DOES | Orchestrator DOES NOT |
|-------|-------------------|----------------------|
| Research | Read files, search code, understand architecture | Run builds, install deps |
| Experimentation | Small tests (<20 lines, <5 min) in /tmp or scripts_dev/ | Large experiments, test suites, infrastructure |
| Planning | Write specs, create delegation docs | Write code, create scripts |
| Delegation | Send task instructions | Implement tasks |
| Monitoring | Check status, review PRs | Fix issues directly |
| Review | Approve/reject work | Make code changes |

---

## Related Documents

- [orchestrator-guardrails.md](./orchestrator-guardrails.md) - Role boundary details
- [agent-selection-guide.md](./agent-selection-guide.md) - Which agent for which task
- [TASK_DELEGATION_TEMPLATE.md](../../eoa-remote-agent-coordinator/templates/handoff/TASK_DELEGATION_TEMPLATE.md) - Delegation template
