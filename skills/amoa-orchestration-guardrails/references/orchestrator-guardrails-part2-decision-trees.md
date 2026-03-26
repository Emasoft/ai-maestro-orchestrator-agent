# Orchestrator Guardrails - Part 2: Decision Trees


## Contents

- [3.0 Decision Trees](#30-decision-trees)
  - [3.1 Before Any Command](#31-before-any-command)
  - [3.2 Before Any File Edit](#32-before-any-file-edit)
  - [3.3 Before Any Git Operation](#33-before-any-git-operation)

---

**Parent Document**: [orchestrator-guardrails.md](./orchestrator-guardrails.md)

---

## 3.0 Decision Trees

### 3.1 Before Any Command

```
About to run a command?
│
├─ Is it READ-ONLY? (git log, ls, cat, gh issue view)
│   └─ YES → PROCEED
│
├─ Is it a SMALL EXPERIMENT? (< 20 lines, < 5 min, verification only)
│   ├─ YES, and in /tmp or scripts_dev/ → PROCEED
│   └─ NO, or production code → STOP → Delegate instead
│
├─ Does it MODIFY files? (edit, write, create)
│   └─ YES → STOP → Delegate instead
│
├─ Does it RUN/BUILD something? (npm, cargo, docker up)
│   └─ YES → STOP → Delegate instead
│
├─ Does it INSTALL something? (npm install, pip install)
│   └─ YES → STOP → Delegate instead
│
└─ Does it COMMIT/PUSH? (git commit, git push)
    └─ YES → STOP → Delegate instead
```

### 3.2 Before Any File Edit

```
About to edit a file?
│
├─ Is it a .md documentation file?
│   ├─ Is it a PLAN or SPEC or DELEGATION doc?
│   │   └─ YES → PROCEED (orchestrator output)
│   └─ NO → STOP → Delegate instead
│
├─ Is it a TEMP EXPERIMENT file?
│   ├─ Is it in /tmp or scripts_dev/ AND < 20 lines?
│   │   └─ YES → PROCEED (delete after verification)
│   └─ NO → STOP → Delegate instead
│
├─ Is it source code? (.py, .ts, .rs, .go, .js, etc.)
│   └─ YES → STOP → Create delegation doc instead
│
├─ Is it configuration? (yaml, json, toml config files)
│   └─ YES → STOP → Document requirements, delegate
│
└─ Is it a script? (.sh, .py scripts)
    └─ YES → STOP → Document requirements, delegate
```

### 3.3 Before Any Git Operation

```
About to do a git operation?
│
├─ Is it git log / git status / git diff (read)?
│   └─ YES → PROCEED (research)
│
├─ Is it git checkout (switch branch)?
│   └─ YES → PROCEED (navigation for research)
│
├─ Is it git add / git commit / git push?
│   └─ YES → STOP → Delegate to task subagent
│
├─ Is it git merge / git rebase?
│   └─ YES → STOP → Delegate to task subagent
│
└─ Is it gh pr create / gh pr merge?
    └─ YES → STOP → Delegate to task subagent
```

---

**Previous**: [Part 1: Role Definition and Action Classification](./orchestrator-guardrails-part1-role-and-actions.md)

**Next**: [Part 3: Common Scenarios](./orchestrator-guardrails-part3-scenarios.md)
