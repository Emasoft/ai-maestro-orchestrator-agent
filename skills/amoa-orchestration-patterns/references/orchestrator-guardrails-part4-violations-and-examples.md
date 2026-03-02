# Orchestrator Guardrails - Part 4: Violation Detection and Examples


## Contents

- [5.0 Violation Detection](#50-violation-detection)
  - [5.1 Warning Signs](#51-warning-signs)
  - [5.2 Recovery Procedure](#52-recovery-procedure)
- [6.0 Templates and Examples](#60-templates-and-examples)
  - [6.1 Correct Delegation Example](#61-correct-delegation-example)
  - [6.2 Infrastructure Task Example](#62-infrastructure-task-example)
  - [6.3 Bug Fix Delegation Example](#63-bug-fix-delegation-example)
- [Related Documents](#related-documents)

---

**Parent Document**: [orchestrator-guardrails.md](./orchestrator-guardrails.md)

---

## 5.0 Violation Detection

### 5.1 Warning Signs

You may be violating RULE 15 if you find yourself:

| Warning Sign | What's Happening | Recovery |
|--------------|------------------|----------|
| Writing code | Role confusion | STOP, create delegation doc |
| Running npm/cargo/pip | Implementation creep | STOP, delegate to agent |
| Editing source files | Role confusion | STOP, document changes for agent |
| "Just this one quick fix" | Rationalization | STOP, no exceptions |
| "It'll be faster if I do it" | Efficiency trap | STOP, delegation is your job |
| Creating config files | Infrastructure implementation | STOP, research and delegate |

### 5.2 Recovery Procedure

If you realize you've started implementation work:

1. **STOP immediately** - Don't finish the implementation
2. **Discard changes** - `git checkout .` or close without saving
3. **Document what was started** - Write brief notes
4. **Create delegation doc** - Convert work-in-progress to instructions
5. **Send to appropriate agent** - Via AI Maestro
6. **Log the violation** - For session summary

---

## 6.0 Templates and Examples

### 6.1 Correct Delegation Example

**Scenario**: User asks to add a new feature

**WRONG** (Orchestrator does implementation):
```
Orchestrator reads code
Orchestrator writes new feature file
Orchestrator runs tests
Orchestrator commits and pushes
→ RULE 15 VIOLATION
```

**CORRECT** (Orchestrator delegates):
```
1. Research: Read existing code to understand architecture
2. Plan: Create feature specification document
3. Delegate: Send task to helper-agent-generic:
   "Implement feature X per spec, create PR, report completion"
4. Monitor: Wait for completion report
5. Review: Check PR meets requirements
```

### 6.2 Infrastructure Task Example

**Scenario**: Set up Docker for cross-platform testing

**WRONG**:
```
Orchestrator creates docker-compose.yml
Orchestrator writes Dockerfiles
Orchestrator runs docker-compose up
→ RULE 15 VIOLATION
```

**CORRECT**:
```
1. Research:
   - What Docker images are needed? (electronuserland/builder, etc.)
   - What existing configs exist in project?
   - What CI workflows use Docker?

2. Document requirements:
   - Linux x64: electronuserland/builder:20
   - Windows: electronuserland/builder:wine
   - Services needed: build-linux, build-windows, test-linux, test-windows

3. Delegate to helper-agent-generic:
   "Create docker-compose.yml with these services [list].
    Create test scripts for parallel execution.
    Update CI workflow to use Docker builds.
    Create PR with all changes."

4. Monitor for completion
5. Review PR
```

### 6.3 Bug Fix Delegation Example

**Scenario**: Tests are failing in CI

**WRONG**:
```
Orchestrator reads test output
Orchestrator edits test file to fix
Orchestrator runs tests locally
Orchestrator commits fix
→ RULE 15 VIOLATION
```

**CORRECT**:
```
1. Research:
   - Read CI logs to understand failure
   - Identify affected files and functions
   - Understand root cause

2. Document issue:
   "Test X fails in CI with error Y.
    Root cause appears to be Z.
    Files affected: test_foo.py:42"

3. Delegate to helper-agent-generic:
   "Fix test failure in test_foo.py.
    Error: [exact error message]
    Likely cause: [analysis]
    Verify fix passes locally and in CI.
    Create PR."

4. Monitor for completion
5. Review PR
```

---

## Related Documents

- [RULE 15: Orchestrator No Implementation](./orchestrator-no-implementation.md)
- [delegation-checklist.md](./delegation-checklist.md)
- [agent-selection-guide.md](./agent-selection-guide.md)
- [task-instruction-format.md](../../eoa-remote-agent-coordinator/references/task-instruction-format.md)

---

**Previous**: [Part 3: Common Scenarios](./orchestrator-guardrails-part3-scenarios.md)

**Remember**: If you're unsure whether an action is allowed, it probably isn't. When in doubt, delegate.
