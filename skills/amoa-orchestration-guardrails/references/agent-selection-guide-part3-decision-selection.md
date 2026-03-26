# Agent Selection Guide - Part 3: Decision Tree & Selection


## Contents

- [Use-Case Quick Reference for This Section](#use-case-quick-reference-for-this-section)
- [Selection Decision Tree](#selection-decision-tree)
  - [Step 1: Identify Task Category](#step-1-identify-task-category)
  - [Step 2: Check Language Requirements](#step-2-check-language-requirements)
  - [Step 3: Verify Parallelization Safety](#step-3-verify-parallelization-safety)
  - [Step 4: Determine Output Requirements](#step-4-determine-output-requirements)
  - [Step 5: Select Agent](#step-5-select-agent)
- [Agent Selection Checklist](#agent-selection-checklist)
- [Minimal Output Requirement Template](#minimal-output-requirement-template)
- [Related Files](#related-files)

---

## Use-Case Quick Reference for This Section

**When to use this file:**
- When you need to decide which agent to use for a task
- When you need to identify the task category
- When you need to verify parallelization safety
- When you need to determine output requirements
- Before spawning any agent (use the checklist)

---

## Selection Decision Tree

### Step 1: Identify Task Category

```
Task Category?
├── Code Development
│   ├── New Feature → Language-specific developer agent
│   ├── Bug Fix → Language-specific developer agent
│   ├── Refactoring → Language-specific developer agent + code-fixer
│   └── Performance → Language-specific developer agent + profiler
├── Code Quality
│   ├── Lint/Format → code-fixer agent
│   ├── Type Checking → code-fixer agent
│   └── Security Scan → security-scanner agent
├── Testing
│   ├── Write Tests → test-writer agent
│   ├── Run Tests → test-runner agent
│   └── Coverage Analysis → coverage-analyzer agent
├── Search/Analysis
│   ├── Large Files → hound-agent
│   ├── Code Elements (known names) → serena-agent
│   ├── Code Elements (unknown names) → context-agent
│   └── Log Analysis → log-auditor
├── DevOps
│   ├── CI/CD → github-actions-agent
│   ├── Containers → docker-agent
│   ├── Orchestration → kubernetes-agent
│   └── Infrastructure → terraform-agent
└── Documentation
    ├── API Docs → doc-generator
    ├── README → readme-writer
    └── Tutorials → tutorial-writer
```

---

### Step 2: Check Language Requirements

```
Language?
├── Python → python-* agents
├── JavaScript/TypeScript → js-* agents
├── Go → go-* agents
├── Rust → rust-* agents
├── Swift (macOS/iOS) → macos-developer / ios-developer
├── Kotlin (Android) → android-developer
├── C# (Windows) → windows-developer
└── Multiple → Separate agents per language
```

---

### Step 3: Verify Parallelization Safety

```
Can this task run in parallel with other tasks?
├── YES (Safe)
│   ├── Different files → Parallel OK
│   ├── Read-only operations → Parallel OK
│   └── Independent modules → Parallel OK
├── NO (Conflicts)
│   ├── Same files → Sequential required
│   ├── Git operations → Sequential required (auth conflicts)
│   ├── Database migrations → Sequential required
│   └── Shared resources → Sequential required
└── MAYBE (Depends)
    ├── Tests → Check test isolation
    ├── Builds → Check build artifacts
    └── Deployments → Check environment locks
```

---

### Step 4: Determine Output Requirements

```
What output does orchestrator need?
├── Minimal Report
│   ├── Status: [DONE/FAILED]
│   ├── Brief result (1-2 lines)
│   └── File paths if applicable
├── Detailed Report (write to file)
│   ├── Save to docs_dev/*.md
│   ├── Return only filename
│   └── Orchestrator reads if needed
└── Structured Data
    ├── Test results → table format
    ├── Coverage → percentage
    └── Metrics → JSON/YAML
```

---

### Step 5: Select Agent

```
SELECTION FORMULA:

Agent = f(TaskType, Language, ParallelSafe, OutputFormat)

Examples:
1. "Fix Python lint errors in auth.py"
   → python-code-fixer (TaskType=CodeQuality, Language=Python, ParallelSafe=YES, OutputFormat=Minimal)

2. "Write 10 tests for payment module"
   → python-test-writer (TaskType=Testing, Language=Python, ParallelSafe=YES, OutputFormat=Minimal + specify count)

3. "Search for authentication patterns in large XML configs"
   → hound-agent (TaskType=Search, FileSize=Large, ParallelSafe=YES, OutputFormat=Minimal)

4. "Run test suite and analyze failures"
   → test-runner (TaskType=Testing, Language=Any, ParallelSafe=NO, OutputFormat=LogFile + log-auditor)

5. "Implement user registration API"
   → python-developer OR js-developer (TaskType=Development, Language=Python/JS, ParallelSafe=MAYBE, OutputFormat=Minimal)
```

---

## Agent Selection Checklist

Before spawning an agent, verify:

- [ ] Task type identified (dev, test, search, devops, docs)
- [ ] Language determined (python, js, go, rust, etc.)
- [ ] Correct agent selected from capability matrix
- [ ] Parallel safety checked (won't conflict with other agents)
- [ ] Output format specified (minimal report + optional file)
- [ ] Test count specified (if test-writer agent)
- [ ] File paths provided (if code-fixer agent)
- [ ] Dependencies identified (if pipeline/sequential)
- [ ] Timeout appropriate (default 20min for all agents)
- [ ] Context preserved (agent won't consume orchestrator context)

---

## Minimal Output Requirement Template

Every agent prompt MUST include:

```
"Return a minimal report: 1-2 lines max, no code blocks, no verbose output.
Format: `[DONE/FAILED] task_name - brief_result`.
If you need to report details, write them to a .md file in docs_dev/
or scripts_dev/ and just tell me the filename.
NEVER return more than 2 lines of text to the orchestrator."
```

---

## Related Files

- [Part 1: Language Agents](./agent-selection-guide-part1-language-agents.md) - Language-specific developer agents
- [Part 2: Specialized Agents](./agent-selection-guide-part2-specialized-agents.md) - Code quality, search, testing, DevOps agents
- [Part 4: Patterns & Practices](./agent-selection-guide-part4-patterns-practices.md) - Anti-patterns and best practices
- [Part 5: Advanced Topics](./agent-selection-guide-part5-advanced.md) - Advanced topics and troubleshooting
- [Index](./agent-selection-guide.md) - Main overview and quick reference
