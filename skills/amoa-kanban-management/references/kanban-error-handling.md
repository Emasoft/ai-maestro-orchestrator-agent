## Table of Contents
- [Error Reference Table](#error-reference-table)
- [Output Specification](#output-specification)
- [Script Output Rules](#script-output-rules)

---

## Error Reference Table

| Error | Cause | Solution |
|-------|-------|----------|
| `missing required scopes [project read:project]` | gh auth lacks project scopes | See [gh-auth-scopes.md](gh-auth-scopes.md) Section 1.4 |
| `InputObject doesn't accept argument 'projectId'` | Wrong parameter name | Use `fieldId` only. See [github-projects-v2-graphql.md](github-projects-v2-graphql.md) Section 2.6 |
| Items lost column assignments after adding columns | Used raw `updateProjectV2Field` | See [kanban-pitfalls.md](kanban-pitfalls.md) Section 3.2 |
| Issue auto-closed when moved to Done | GitHub Projects V2 built-in automation | See [kanban-pitfalls.md](kanban-pitfalls.md) Section 3.1 |
| `gh auth refresh` fails in non-interactive session | Requires browser-based OAuth flow | Must be done by human before agent deployment |

---

## Output Specification

After executing kanban operations, the agent produces:

- **Board creation**: Project number (integer) and project URL. Store the project number in `.github/project.json` for future reference.
- **Column addition**: Confirmation message listing preserved columns and newly added columns. Verify no assignments were lost.
- **Item moves**: Updated item status. Verify the item appears in the target column with `gh project item-list`.
- **Status sync**: Reconciliation report showing label-to-column mappings and any conflicts resolved.
- **Error case**: Error message with cause and remediation steps (see table above).

---

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
