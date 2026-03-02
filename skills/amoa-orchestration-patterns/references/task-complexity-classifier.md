# Task Complexity Classifier


## Contents

- [Task Complexity Assessment](#task-complexity-assessment)
- [Use-Case Quick Reference](#use-case-quick-reference)
- [Simple Task](#simple-task)
  - [Criteria](#criteria)
  - [Action](#action)
  - [Example Pattern](#example-pattern)
- [Medium Task](#medium-task)
  - [Criteria](#criteria)
  - [Action](#action)
  - [Example Pattern](#example-pattern)
- [Complex Task](#complex-task)
  - [Criteria](#criteria)
  - [Action](#action)
  - [Example Pattern](#example-pattern)
- [Decision Matrix](#decision-matrix)
- [Examples](#examples)
  - [Simple Task Examples](#simple-task-examples)
  - [Medium Task Examples](#medium-task-examples)
  - [Complex Task Examples](#complex-task-examples)
- [Classification Process](#classification-process)
  - [Step 1: Initial Assessment](#step-1-initial-assessment)
  - [Step 2: Count Complexity Signals](#step-2-count-complexity-signals)
  - [Step 3: Apply Classification](#step-3-apply-classification)
  - [Step 4: Choose Action Pattern](#step-4-choose-action-pattern)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
  - [Over-Planning Simple Tasks](#over-planning-simple-tasks)
  - [Under-Planning Complex Tasks](#under-planning-complex-tasks)
  - [Treating All Medium Tasks as Complex](#treating-all-medium-tasks-as-complex)
- [Practical Tips](#practical-tips)
  - [When in Doubt](#when-in-doubt)
  - [Escalation Signals](#escalation-signals)
  - [De-escalation Signals](#de-escalation-signals)
- [Summary](#summary)

---

## Task Complexity Assessment

Understanding task complexity helps orchestrators make efficient delegation decisions. This classification system evaluates tasks based on scope, dependencies, and coordination requirements rather than time estimates.

## Use-Case Quick Reference

**When to use this guide:**
- When deciding if a task needs planning → [Classification Process](#classification-process)
- If task involves single language with standard libs → [Simple Task](#simple-task)
- When task requires external packages and architecture → [Medium Task](#medium-task)
- If task spans multiple languages or platforms → [Complex Task](#complex-task)
- When uncertain between complexity levels → [Practical Tips](#practical-tips) > When in Doubt
- If you're over-planning a simple task → [Anti-Patterns to Avoid](#anti-patterns-to-avoid) > Over-Planning Simple Tasks
- When task becomes simpler during planning → [Practical Tips](#practical-tips) > De-escalation Signals
- If you need examples to compare against → [Examples](#examples)

---

## Simple Task

**Estimated Effort**: Minimal

### Criteria

- **Single language**: Only one programming language or technology involved
- **Standard dependencies**: No external dependencies beyond standard libraries or well-established core packages
- **No multi-platform native code**: Runs on a single platform or uses platform-agnostic code
- **Clear, well-defined scope**: Requirements are explicit and unambiguous with no architectural decisions needed
- **Single focused session**: Can be completed in one uninterrupted work session without context switching
- **Minimal files**: Typically affects 1-3 files maximum
- **No integration points**: Does not require coordination with external services, APIs, or systems
- **Straightforward testing**: Tests are obvious and simple to write

### Action

**Skip formal planning** - Delegate directly to developer agent with clear instructions

### Example Pattern

```
Simple task detected:
→ Direct delegation to specialized agent
→ No planning overhead
→ Fast execution
```

---

## Medium Task

**Estimated Effort**: Moderate

### Criteria

- **Single language with library dependencies**: Requires external packages or frameworks beyond standard library
- **Basic architecture needed**: Some design decisions required but within established patterns
- **Tests required**: Needs comprehensive test coverage with multiple test cases
- **Multiple files but single module**: Affects several files but all within one cohesive module or component
- **Established patterns**: Can follow existing codebase conventions and structures
- **Some coordination**: May need to verify compatibility with other components
- **Documentation needed**: Requires updating or creating documentation

### Action

**Brief planning** - Quick architecture review, then single developer agent handles implementation

### Example Pattern

```
Medium task detected:
→ 5-minute planning phase (architecture sketch)
→ Delegate to single developer agent
→ Parallel testing agent for test writing
→ Brief review before completion
```

---

## Complex Task

**Estimated Effort**: Significant

### Criteria

- **Multiple languages or platforms**: Involves polyglot development (e.g., Python + JavaScript, native + web)
- **Multi-platform native code**: Requires platform-specific implementations (Windows/macOS/Linux)
- **External integrations**: Must coordinate with external services, APIs, databases, or third-party systems
- **Multiple developers/agents needed**: Work must be parallelized across multiple specialized agents
- **Architecture decisions required**: Fundamental design choices that affect system structure
- **Cross-module impact**: Changes ripple across multiple modules or services
- **Complex dependency management**: Intricate version compatibility or build system requirements
- **Substantial testing infrastructure**: Needs integration tests, end-to-end tests, or test environment setup

### Action

**Full planning process** - Comprehensive planning, team orchestration, phased execution, continuous integration

### Example Pattern

```
Complex task detected:
→ Planning phase: Architecture design, dependency analysis, task breakdown
→ Team formation: Assign specialized agents to parallel workstreams
→ Coordination: Regular checkpoints, integration verification
→ Testing: Multi-layer testing strategy (unit, integration, e2e)
→ Review: Comprehensive code review and validation
```

---

## Decision Matrix

| Characteristic | Simple | Medium | Complex |
|---|---|---|---|
| **Languages** | 1 | 1 | 2+ or polyglot |
| **Dependencies** | Standard lib only | External packages | Multiple frameworks, external integrations |
| **Files Affected** | 1-3 | 4-10 | 10+ or cross-module |
| **Platform Scope** | Single | Single (platform-agnostic) | Multi-platform native |
| **Architecture** | None needed | Minor adjustments | Major design decisions |
| **Agents Required** | 1 | 1-2 | 3+ specialized agents |
| **Testing Scope** | Basic unit tests | Comprehensive unit tests | Unit + integration + e2e |
| **Integration Points** | None | Optional | Multiple required |
| **Documentation** | Inline comments | Module-level docs | Architecture docs + API docs |
| **Coordination** | None | Minimal verification | Active orchestration |
| **Scope Clarity** | Crystal clear | Well-defined | Requires refinement |
| **Risk Level** | Low | Medium | High (needs validation) |

---

## Examples

### Simple Task Examples

**Example 1: Add logging to existing function**
- Single Python file
- Uses standard `logging` library
- Clear requirement: "Add debug logging to track function entry/exit"
- No architecture changes
- Simple test: verify log messages appear
- **Classification**: Simple → Direct delegation

**Example 2: Fix typo in documentation**
- Single markdown file
- No code changes
- Explicit location and correction
- No testing needed
- **Classification**: Simple → Direct delegation

**Example 3: Add CLI argument to script**
- Single Python file using `argparse`
- Standard library only
- Clear specification of new argument
- Simple test to verify parsing
- **Classification**: Simple → Direct delegation

---

### Medium Task Examples

**Example 1: Implement new API endpoint**
- Single language (Python/FastAPI)
- External dependency (FastAPI framework)
- Multiple files: route handler, service layer, tests
- Database integration using existing ORM
- Follows established patterns in codebase
- Needs comprehensive tests (unit + integration)
- **Classification**: Medium → Brief planning + single developer agent

**Example 2: Add caching layer to existing service**
- Single language (Node.js)
- External dependency (Redis client)
- Multiple files: service layer modifications, cache wrapper, tests
- Architecture decision: cache key strategy (but follows patterns)
- Integration with existing service
- Needs cache invalidation tests
- **Classification**: Medium → Brief planning + developer agent + testing agent

**Example 3: Create data export feature**
- Single language (Python)
- External dependencies (pandas, openpyxl)
- Multiple files: export service, formatters, tests
- Some design decisions (export format, pagination)
- Integration with existing data models
- Comprehensive testing for various export scenarios
- **Classification**: Medium → Brief planning + single developer agent

---

### Complex Task Examples

**Example 1: Cross-platform desktop application**
- Multiple languages (Rust + JavaScript/Electron)
- Platform-specific native code (Windows/macOS/Linux)
- External integrations (system APIs, IPC)
- Multiple agents needed: Rust developer, JS developer, platform specialists
- Architecture decisions: IPC protocol, state management, update mechanism
- Cross-module impact: native bindings, UI layer, business logic
- Complex testing: unit, integration, platform-specific e2e tests
- **Classification**: Complex → Full planning + team orchestration

**Example 2: Microservices migration**
- Multiple languages (existing monolith + new services)
- Multiple frameworks and databases
- External integrations: service mesh, message queue, API gateway
- Multiple agents: backend developers, DevOps, database specialists
- Architecture decisions: service boundaries, communication patterns, data consistency
- Cross-module impact: affects entire system architecture
- Complex testing: contract testing, integration tests, chaos engineering
- **Classification**: Complex → Full planning + phased execution + continuous validation

**Example 3: Real-time collaborative editing feature**
- Multiple languages (Python backend + TypeScript frontend)
- External integrations: WebSocket server, CRDT library, persistence layer
- Multiple agents: backend developer, frontend developer, real-time systems specialist
- Architecture decisions: conflict resolution algorithm, state synchronization, scaling strategy
- Cross-module impact: data models, API layer, client state management
- Complex testing: concurrency tests, network partition scenarios, performance benchmarks
- Substantial infrastructure: test environment with multiple concurrent clients
- **Classification**: Complex → Full planning + specialized team + extensive testing

**Example 4: CI/CD pipeline with multi-cloud deployment**
- Multiple languages (YAML configs + shell scripts + Python automation)
- Multi-platform (AWS + GCP + on-premises)
- External integrations: GitHub Actions, Docker, Kubernetes, Terraform
- Multiple agents: DevOps engineer, security specialist, infrastructure architect
- Architecture decisions: deployment strategy, rollback procedures, monitoring approach
- Cross-module impact: all repositories and deployment targets
- Complex testing: deployment tests, rollback tests, security scans
- **Classification**: Complex → Full planning + team coordination + validation gates

---

## Classification Process

### Step 1: Initial Assessment
Ask these questions:
1. How many languages/platforms are involved?
2. What dependencies are required?
3. How many files/modules will be affected?
4. Are there external integration points?
5. What architecture decisions are needed?

### Step 2: Count Complexity Signals
Count how many "complex" signals are present:
- Multiple languages: +1
- Multi-platform native: +1
- External integrations: +1
- Cross-module changes: +1
- Architecture decisions: +1
- 10+ files affected: +1

**Scoring**:
- 0-1 signals: Simple
- 2-3 signals: Medium
- 4+ signals: Complex

### Step 3: Apply Classification
Use the decision matrix and examples to validate your assessment.

### Step 4: Choose Action Pattern
- **Simple**: Direct delegation
- **Medium**: Brief planning + single agent
- **Complex**: Full planning + team orchestration

---

## Anti-Patterns to Avoid

### Over-Planning Simple Tasks
**Don't**: Spend more time planning than executing
- Simple tasks don't need architecture diagrams
- Skip formal planning documentation
- Direct delegation is faster and efficient

### Under-Planning Complex Tasks
**Don't**: Dive into complex tasks without planning
- Complex tasks without plans lead to rework
- Missing integration points cause failures
- Lack of coordination wastes parallel effort

### Treating All Medium Tasks as Complex
**Don't**: Apply full planning to medium tasks
- Medium tasks benefit from brief planning, not full design docs
- Single developer can handle with light coordination
- Over-orchestration adds unnecessary overhead

---

## Practical Tips

### When in Doubt
If you're uncertain between two levels, consider:
- **Can one agent handle it?** → Probably not Complex
- **Are requirements crystal clear?** → Probably Simple
- **Do you need to coordinate multiple workstreams?** → Probably Complex

### Escalation Signals
Start with lower complexity assumption, escalate if you encounter:
- Unexpected integration requirements
- Cross-cutting concerns discovered mid-task
- Multiple blocking dependencies
- Architecture assumptions proven wrong

### De-escalation Signals
If a Complex task becomes simpler during planning:
- External integration already handled by library
- Multi-platform abstraction layer exists
- Fewer files affected than anticipated
→ Re-classify and adjust approach

---

## Summary

Task complexity classification enables efficient orchestration by matching planning effort to task requirements:

- **Simple tasks**: Minimal planning overhead, fast execution
- **Medium tasks**: Light planning, focused execution
- **Complex tasks**: Comprehensive planning, coordinated execution

The goal is not perfect classification, but **appropriate planning investment** for the task at hand.
