# Agent Selection Guide - Part 2: Specialized Agents


## Contents

- [Use-Case Quick Reference for This Section](#use-case-quick-reference-for-this-section)
- [Specialized Agents](#specialized-agents)
  - [Code Quality Agents](#code-quality-agents)
  - [Search and Analysis Agents](#search-and-analysis-agents)
  - [Testing Agents](#testing-agents)
  - [DevOps and Infrastructure Agents](#devops-and-infrastructure-agents)
  - [Documentation Agents](#documentation-agents)
- [Agent Capability Matrix](#agent-capability-matrix)
  - [Core Capabilities](#core-capabilities)
  - [Tool Expertise](#tool-expertise)
  - [Domain Expertise (Star Rating: 1-5)](#domain-expertise-star-rating-1-5)
- [Related Files](#related-files)

---

## Use-Case Quick Reference for This Section

**When to use this file:**
- When choosing between search agents (hound, SERENA, context)
- When you need to select a code quality agent
- When you need to select a testing agent
- When you need DevOps or infrastructure agents
- When you need documentation agents
- When checking agent capabilities and tool expertise

---

## Specialized Agents

### Code Quality Agents

| Agent Name | Purpose | Input | Output | When to Use |
|------------|---------|-------|--------|-------------|
| `python-code-fixer` | Fix Python lint/type/format issues | File paths | Issues fixed count | After editing Python files |
| `js-code-fixer` | Fix JS/TS lint/type/format issues | File paths | Issues fixed count | After editing JS/TS files |
| `go-code-fixer` | Fix Go lint/format issues | File paths | Issues fixed count | After editing Go files |
| `rust-code-fixer` | Fix Rust lint/format issues | File paths | Issues fixed count | After editing Rust files |

**Code Fixer Agent Rules:**
- ALWAYS run after editing source files
- Run BEFORE committing code
- Can run in parallel (different files)
- Must report minimal output

---

### Search and Analysis Agents

| Agent Name | Purpose | Input | Output | When to Use |
|------------|---------|-------|--------|-------------|
| `hound-agent` | Deep file searches | Query + file patterns | Match count + file paths | Large files (>30KB), complex patterns |
| `log-auditor` | Analyze log files | Log file path | Summary + error count | After test runs, CI failures, debugging |
| `context-agent` | Find code elements from vague descriptions | Description | Element paths + snippets | Don't know exact names |
| `serena-agent` | Find code elements by name | Symbol name | Element details + references | Know exact names |

**Search Agent Selection Rules:**
- Use `hound-agent` for large files (>30KB): xml, html, json, txt, md, svg, css
- Use `log-auditor` for log analysis after test runs
- Use `context-agent` when you don't know element names
- Use `serena-agent` when you know exact symbol names

---

### Testing Agents

| Agent Name | Purpose | Input | Output | When to Use |
|------------|---------|-------|--------|-------------|
| `python-test-writer` | Write Python tests | Module path + test count | Test count + file paths | Python test coverage needed |
| `js-test-writer` | Write JS/TS tests | Module path + test count | Test count + file paths | JS/TS test coverage needed |
| `test-runner` | Execute tests + audit logs | Test command | Pass/fail count + log path | Running test suites |
| `ci-monitor` | Monitor CI/CD pipelines | Workflow name | Status + log path | Watching GitHub Actions |

**Testing Agent Selection Rules:**
- ALWAYS specify test count when using test-writer agents
- Default test count is 30 per function (too many!)
- Use `test-runner` to avoid blocking orchestrator
- Use `ci-monitor` for async CI/CD watching

---

### DevOps and Infrastructure Agents

| Agent Name | Purpose | Input | Output | When to Use |
|------------|---------|-------|--------|-------------|
| `docker-agent` | Docker operations | Dockerfile path + command | Container ID + status | Building/running containers |
| `kubernetes-agent` | K8s operations | Manifest path + command | Resource status | Deploying to K8s |
| `terraform-agent` | Infrastructure as Code | Terraform files + command | Apply status + resources | Cloud infrastructure |
| `github-actions-agent` | GitHub Actions | Workflow path + event | Run ID + status | CI/CD automation |

**DevOps Agent Selection Rules:**
- Use specialized agents for each tool
- Never mix infrastructure tools in one agent
- Always validate manifests before apply

---

### Documentation Agents

| Agent Name | Purpose | Input | Output | When to Use |
|------------|---------|-------|--------|-------------|
| `doc-generator` | Generate docs from code | Source paths + format | Doc file paths | Auto-generating API docs |
| `readme-writer` | Write README files | Project path + sections | README path | Creating project documentation |
| `tutorial-writer` | Write tutorials | Topic + examples | Tutorial path | Creating user guides |

**Documentation Agent Selection Rules:**
- Use `doc-generator` for API documentation
- Use `readme-writer` for project READMEs
- Use `tutorial-writer` for user-facing guides

---

## Agent Capability Matrix

### Core Capabilities

| Agent | Read Files | Edit Files | Run Tests | Fix Code | Git Ops | API Calls | Parallel Safe |
|-------|-----------|-----------|-----------|----------|---------|-----------|---------------|
| `python-developer` | Yes | Yes | Yes | Yes | Yes | Yes | Warning (git conflicts) |
| `python-code-fixer` | Yes | Yes | No | Yes | No | No | Yes |
| `python-test-writer` | Yes | Yes | Yes | No | No | No | Yes |
| `js-developer` | Yes | Yes | Yes | Yes | Yes | Yes | Warning (git conflicts) |
| `js-code-fixer` | Yes | Yes | No | Yes | No | No | Yes |
| `js-test-writer` | Yes | Yes | Yes | No | No | No | Yes |
| `hound-agent` | Yes | No | No | No | No | No | Yes |
| `log-auditor` | Yes | No | No | No | No | No | Yes |
| `test-runner` | Yes | No | Yes | No | No | No | Warning (test conflicts) |

### Tool Expertise

| Agent | Linters | Formatters | Type Checkers | Test Frameworks | Build Tools |
|-------|---------|-----------|---------------|-----------------|-------------|
| `python-developer` | ruff, pylint | black, isort | mypy, pyright | pytest, unittest | uv, poetry, setuptools |
| `python-code-fixer` | ruff, pylint | black, ruff format | mypy, pyright | - | - |
| `js-developer` | eslint, tslint | prettier, dprint | tsc, flow | vitest, jest | pnpm, npm, webpack, vite |
| `js-code-fixer` | eslint | prettier | tsc | - | - |
| `go-developer` | golangci-lint | gofmt, goimports | go vet | go test | go build, make |
| `rust-developer` | clippy | rustfmt | cargo check | cargo test | cargo build |

### Domain Expertise (Star Rating: 1-5)

| Agent | Web Dev | CLI Tools | Data Science | DevOps | Mobile | Desktop |
|-------|---------|-----------|--------------|--------|--------|---------|
| `python-developer` | 3 | 5 | 3 | 4 | 1 | 2 |
| `js-developer` | 5 | 3 | 2 | 3 | 2 | 3 |
| `go-developer` | 3 | 5 | 1 | 5 | 1 | 2 |
| `rust-developer` | 2 | 5 | 1 | 4 | 1 | 3 |
| `data-scientist` | 1 | 2 | 5 | 1 | 1 | 1 |
| `ios-developer` | 1 | 1 | 1 | 1 | 5 | 3 |
| `android-developer` | 1 | 1 | 1 | 1 | 5 | 1 |

---

## Related Files

- [Part 1: Language Agents](./agent-selection-guide-part1-language-agents.md) - Language-specific developer agents
- [Part 3: Decision & Selection](./agent-selection-guide-part3-decision-selection.md) - Decision tree and selection checklist
- [Part 4: Patterns & Practices](./agent-selection-guide-part4-patterns-practices.md) - Anti-patterns and best practices
- [Part 5: Advanced Topics](./agent-selection-guide-part5-advanced.md) - Advanced topics and troubleshooting
- [Index](./agent-selection-guide.md) - Main overview and quick reference
