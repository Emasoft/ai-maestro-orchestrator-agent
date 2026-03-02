# Agent Selection Guide - Part 5: Advanced Topics & Troubleshooting


## Contents

- [Use-Case Quick Reference for This Section](#use-case-quick-reference-for-this-section)
- [Advanced Topics](#advanced-topics)
  - [Agent Composition](#agent-composition)
  - [Agent Lifecycle](#agent-lifecycle)
  - [Agent Constraints](#agent-constraints)
  - [Agent Communication](#agent-communication)
- [Troubleshooting](#troubleshooting)
  - [Agent Selection Errors](#agent-selection-errors)
  - [Selection Conflicts](#selection-conflicts)
- [Quick Reference Card](#quick-reference-card)
  - [Most Common Agent Selections](#most-common-agent-selections)
  - [Agent Output Templates](#agent-output-templates)
- [Summary: Golden Rules](#summary-golden-rules)
- [Remember](#remember)
- [Related Files](#related-files)

---

## Use-Case Quick Reference for This Section

**When to use this file:**
- When you need to understand agent composition and delegation
- When you need to understand agent lifecycle
- When you encounter agent selection errors
- When you have selection conflicts between agents
- When debugging agent behavior

---

## Advanced Topics

### Agent Composition

Agents can delegate to other agents:
```
python-developer
  ├─→ python-code-fixer (fix own code)
  ├─→ python-test-writer (write tests)
  └─→ test-runner (validate implementation)
```

---

### Agent Lifecycle

1. **Spawn**: Orchestrator creates agent with clear task
2. **Execute**: Agent performs task autonomously
3. **Report**: Agent returns minimal report
4. **Cleanup**: Agent exits, resources released

---

### Agent Constraints

| Constraint | Value |
|------------|-------|
| Max parallel agents | 20 |
| Tasks per agent | 1 only |
| Max context per agent | 30KB |
| Default timeout | 20 minutes |
| Max output to orchestrator | 2 lines |

---

### Agent Communication

Agents communicate via:
- File system (shared workspace)
- Git (code changes)
- Log files (execution details)
- Report files (analysis results)
- Return values (minimal status)

Agents do NOT communicate via:
- Direct messaging
- Shared memory
- Network sockets
- Orchestrator context

---

## Troubleshooting

### Agent Selection Errors

| Problem | Solution |
|---------|----------|
| Wrong agent selected, task fails | Review decision tree, check capability matrix |
| Agent returns verbose output, crashes orchestrator | Add minimal output requirement to prompt |
| Multiple agents conflict on git operations | Serialize git operations, parallelize file edits only |
| Test-writer creates too many tests | Always specify exact test count in prompt |
| Agent blocks orchestrator | Use Task subagent pattern, don't run directly |

---

### Selection Conflicts

**Q:** Need both Python and JavaScript work, which agent?
**A:** Spawn both `python-developer` AND `js-developer`, separate tasks

**Q:** Large file search, SERENA or hound-agent?
**A:** hound-agent for files >30KB, SERENA for code symbols only

**Q:** Fix code AND write tests, one agent or two?
**A:** Two agents: `python-test-writer` then `python-code-fixer` (TDD: write/update tests first, then fix code to pass tests)

**Q:** Run tests AND commit, one agent or two?
**A:** Two agents: `test-runner` then `git-commit-agent` (sequential)

---

## Quick Reference Card

### Most Common Agent Selections

| User Request | Selected Agent | Key Parameters |
|--------------|----------------|----------------|
| "Fix lint errors in foo.py" | `python-code-fixer` | file_path=foo.py |
| "Write tests for bar module" | `python-test-writer` | module=bar, count=10 |
| "Search large XML configs" | `hound-agent` | pattern=..., files=*.xml |
| "Run test suite" | `test-runner` | command="pytest tests/" |
| "Analyze test failures" | `log-auditor` | log_path=logs/test_*.log |
| "Implement user auth" | `python-developer` | feature="user auth" |
| "Fix TypeScript types" | `js-code-fixer` | file_path=types.ts |
| "Deploy to production" | `github-actions-agent` | workflow="deploy.yml" |

---

### Agent Output Templates

**python-code-fixer:**
```
[DONE] python-code-fixer - Fixed 12 lint issues, 3 type errors in auth.py
```

**python-test-writer:**
```
[DONE] python-test-writer - Created 10 tests in tests/test_auth.py (coverage: 85%)
```

**hound-agent:**
```
[DONE] hound-agent - Found 23 matches in 7 files, results in docs_dev/search-results-2025-01-01.md
```

**log-auditor:**
```
[DONE] log-auditor - 3 test failures identified, analysis in docs_dev/log-audit-2025-01-01.md
```

**test-runner:**
```
[DONE] test-runner - 47/50 tests passed, failures logged to logs/test_2025-01-01_14-30-00.log
```

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

---

## Related Files

- [Part 1: Language Agents](./agent-selection-guide-part1-language-agents.md) - Language-specific developer agents
- [Part 2: Specialized Agents](./agent-selection-guide-part2-specialized-agents.md) - Code quality, search, testing, DevOps agents
- [Part 3: Decision & Selection](./agent-selection-guide-part3-decision-selection.md) - Decision tree and selection checklist
- [Part 4: Patterns & Practices](./agent-selection-guide-part4-patterns-practices.md) - Anti-patterns and best practices
- [Index](./agent-selection-guide.md) - Main overview and quick reference
