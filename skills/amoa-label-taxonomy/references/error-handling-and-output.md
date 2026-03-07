## Table of Contents
- Error Handling
- Output Formats
- Colors Reference

---

# Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Multiple `assign:*` labels on one issue | Concurrent updates or incorrect removal | Remove all `assign:*` labels, then add the correct one |
| Missing `status:*` label | Label removed accidentally or never set | Set the appropriate status label based on current workflow state |
| Multiple `status:*` labels | Concurrent updates | Remove all `status:*` labels, then add the correct one |
| `gh` command fails | No auth or repo not found | Run `gh auth login` and verify repo access |
| Label conflict during reassignment | Old label not removed first | Use `gh issue edit --remove-label "old" --add-label "new"` in single command |
| Invalid label name | Typo or wrong format | Check label format: `<category>:<value>` (no spaces) |

# Output Formats

| Output Type | Format | Example |
|-------------|--------|---------|
| Label list | JSON from `gh issue view` | `{"labels": [{"name": "assign:implementer-1"}]}` |
| Label query results | Table/list from `gh issue list` | Issues matching filter criteria |
| Label creation | CLI confirmation | `Label "assign:implementer-1" created` |
| Label update | CLI confirmation | `Updated labels for #42` |
| Validation result | Boolean/message | "Valid: issue has exactly 1 status label" |

# Colors Reference

| Category | Suggested Color |
|----------|-----------------|
| `assign:` | Various blues/purples |
| `status:` | Workflow colors (green=ready, yellow=progress, red=blocked) |
| `priority:` | Urgency colors (red=critical, orange=high, yellow=normal, green=low) |
| `type:` | Category colors |
| `component:` | Light pastels |
| `effort:` | Size-based (green=small, red=large) |
| `platform:` | Neutral grays |
| `toolchain:` | Language brand colors |
| `review:` | Review state colors |
