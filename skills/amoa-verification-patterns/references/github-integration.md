# Integration with GitHub Projects


## Contents

- [Table of Contents](#table-of-contents)
- [9.1 Verification Results and Issue Status](#91-verification-results-and-issue-status)
- [9.2 Verification Evidence in Issue Comments](#92-verification-evidence-in-issue-comments)
- [Verification Report](#verification-report)
- [9.3 Automation Script Integration](#93-automation-script-integration)
- [9.4 Cross-Reference to Related Skills](#94-cross-reference-to-related-skills)

---

## Table of Contents

- [9.1 Verification Results and Issue Status](#91-verification-results-and-issue-status)
  - 9.1.1 Automatic status transitions
  - 9.1.2 Status mapping table
- [9.2 Verification Evidence in Issue Comments](#92-verification-evidence-in-issue-comments)
  - 9.2.1 Structured comment format
  - 9.2.2 Required fields
- [9.3 Automation Script Integration](#93-automation-script-integration)
  - 9.3.1 Using gh CLI for issue updates
  - 9.3.2 Pass and fail commands
- [9.4 Cross-Reference to Related Skills](#94-cross-reference-to-related-skills)
  - 9.4.1 Status management
  - 9.4.2 Plan verification

---

## 9.1 Verification Results and Issue Status

Verification outcomes trigger automatic status transitions:

| Verification Result | GitHub Action |
|---------------------|---------------|
| All tests pass (exit 0) | Move to "AI Review" if PR exists |
| Evidence collected | Add comment with evidence summary |
| Verification failed | Move to "Blocked", add failure label |
| Retry succeeded | Remove failure label, resume workflow |

---

## 9.2 Verification Evidence in Issue Comments

When verification completes, post structured comment:

```markdown
## Verification Report
- **Type**: {exit-code/evidence-based/integration/e2e}
- **Result**: PASSED/FAILED
- **Timestamp**: {ISO-8601}
- **Evidence**: {summary}
- **Script**: {script-name}
```

---

## 9.3 Automation Script Integration

Use `gh` CLI to update issues based on verification:

```bash
# On verification pass
gh issue edit {NUMBER} --add-label "verified"

# On verification fail
gh issue edit {NUMBER} --add-label "verification-failed"
gh issue comment {NUMBER} --body "Verification failed: {reason}"
```

---

## 9.4 Cross-Reference to Related Skills

- See `github-projects-sync/references/status-management.md` for status lifecycle
- See `planning-patterns/references/plan-verification-guide.md` for plan integration
