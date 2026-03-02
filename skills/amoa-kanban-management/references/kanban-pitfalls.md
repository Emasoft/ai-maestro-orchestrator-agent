# Kanban Pitfalls and Guards

## Table of Contents

- 3.1 Done column auto-closes linked issues - GitHub built-in automation
  - 3.1.1 How to detect if an issue was auto-closed
  - 3.1.2 Guard: check issue state before attempting gh issue close
- 3.2 updateProjectV2Field replaces ALL options - Data loss risk
  - 3.2.1 Why this happens - Option IDs are regenerated
  - 3.2.2 Safe column addition procedure
  - 3.2.3 Using gh-project-add-columns.sh script
- 3.3 gh auth refresh requires interactive browser - Cannot be automated
- 3.4 updateProjectV2Field does not accept projectId - Only fieldId

---

## 3.1 Done column auto-closes linked issues

### What happens

GitHub Projects V2 has a built-in automation feature: when a project item is moved to the "Done" column, GitHub automatically closes the linked issue. This is NOT a bug — it is expected GitHub behavior.

**Consequence for agents:** If an agent moves a task to "Done" on the kanban board and then tries to close the issue with `gh issue close`, the close command will either:
- Succeed silently (issue was already closed)
- Fail with a warning (depending on the GitHub API version)

Neither outcome is harmful, but it creates confusion in logs and may cause agents to report false errors.

### 3.1.1 How to detect if an issue was auto-closed

Check the issue state after moving to the Done column:

```bash
STATE=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json state -q '.state')
echo "Issue #$ISSUE_NUMBER state: $STATE"
# If STATE is "CLOSED", it was auto-closed by the Done column
```

You can also check the issue timeline to see who closed it:

```bash
gh api repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/timeline \
  --jq '.[] | select(.event == "closed") | {closed_by: .actor.login, created_at: .created_at}'
```

If `closed_by` is `github-project-automation[bot]`, it was auto-closed by the Projects V2 automation.

### 3.1.2 Guard: check issue state before attempting gh issue close

**ALWAYS check the issue state before attempting to close it.** This prevents redundant operations and misleading log entries.

**Bash guard:**

```bash
close_issue_safely() {
  local issue_number="$1"
  local repo="$2"
  local comment="${3:-Task completed.}"

  # Check current state
  local state
  state=$(gh issue view "$issue_number" --repo "$repo" --json state -q '.state')

  if [ "$state" = "CLOSED" ]; then
    echo "INFO: Issue #$issue_number is already closed (likely auto-closed by Done column)"
    return 0
  fi

  # Close with comment
  gh issue close "$issue_number" --repo "$repo" --comment "$comment"
}
```

**Python guard:**

```python
def close_issue_safely(issue_number: int, repo: str, comment: str = "Task completed.") -> bool:
    """Close an issue, but check if it's already closed first.

    GitHub Projects V2 auto-closes issues when moved to Done column.
    This guard prevents redundant close attempts.
    """
    # Check current state
    returncode, stdout, _ = run_gh_command([
        "issue", "view", str(issue_number),
        "--repo", repo,
        "--json", "state",
    ])
    if returncode != 0:
        return False

    state = json.loads(stdout).get("state", "OPEN")

    if state == "CLOSED":
        print(f"INFO: Issue #{issue_number} is already closed "
              f"(likely auto-closed by Done column)")
        return True

    # Close with comment
    returncode, _, stderr = run_gh_command([
        "issue", "close", str(issue_number),
        "--repo", repo,
        "--comment", comment,
    ])
    if returncode != 0:
        print(f"Failed to close issue: {stderr}", file=sys.stderr)
        return False

    return True
```

---

## 3.2 updateProjectV2Field replaces ALL options

### What happens

The GraphQL mutation `updateProjectV2Field` is used to modify field options (columns) on a GitHub Projects V2 board. **This mutation REPLACES the entire list of options.** It does NOT append.

If you send a mutation with only new columns (without including existing ones), ALL existing column assignments will be lost:

- Existing option IDs are regenerated with new random IDs
- Items that were in the old columns become unassigned
- The column names may look the same, but the internal IDs are different
- All items fall off the board into an unassigned state

**This is the most dangerous pitfall in GitHub Projects V2 management.**

### 3.2.1 Why this happens

GitHub Projects V2 identifies column assignments by option ID, not by option name. When you call `updateProjectV2Field` with `singleSelectOptions`, GitHub:

1. Looks at each option in the array
2. If an option has an `id` field that matches an existing option, it PRESERVES that option and its assignments
3. If an option has NO `id` field, it creates a NEW option with a new random ID
4. Any existing options NOT included in the array are DELETED

**Example of the problem:**

Before mutation, the Status field has:
```
Backlog (id: f75ad846) ← 5 items assigned
Todo (id: 47fc9ee4) ← 3 items assigned
In Progress (id: 98236657) ← 2 items assigned
Done (id: 0d8fcf92) ← 10 items assigned
```

If you send this mutation (WITHOUT existing IDs):
```json
{
  "singleSelectOptions": [
    {"name": "Backlog"},
    {"name": "Todo"},
    {"name": "In Progress"},
    {"name": "Done"},
    {"name": "AI Review"},
    {"name": "Human Review"}
  ]
}
```

After mutation:
```
Backlog (id: a1b2c3d4) ← 0 items (NEW ID, no assignments)
Todo (id: e5f6a7b8) ← 0 items (NEW ID, no assignments)
In Progress (id: c9d0e1f2) ← 0 items (NEW ID, no assignments)
Done (id: 3a4b5c6d) ← 0 items (NEW ID, no assignments)
AI Review (id: 7e8f9a0b) ← 0 items (new column)
Human Review (id: 1c2d3e4f) ← 0 items (new column)
```

**All 20 items lost their column assignments!**

### 3.2.2 Safe column addition procedure

To safely add columns, you MUST:

1. **Query existing options** with their IDs (see [github-projects-v2-graphql.md](github-projects-v2-graphql.md) Section 2.1)
2. **Build the options array** including ALL existing options with their IDs
3. **Append new options** without IDs (GitHub will generate IDs for them)
4. **Execute the mutation** with the complete options array
5. **Verify** that existing assignments survived

**Correct mutation payload (preserving existing IDs):**

```json
{
  "singleSelectOptions": [
    {"id": "f75ad846", "name": "Backlog"},
    {"id": "47fc9ee4", "name": "Todo"},
    {"id": "98236657", "name": "In Progress"},
    {"id": "0d8fcf92", "name": "Done"},
    {"name": "AI Review"},
    {"name": "Human Review"}
  ]
}
```

After this mutation, existing items retain their column assignments because the existing option IDs were preserved.

### 3.2.3 Using gh-project-add-columns.sh script

**ALWAYS use the provided helper script instead of calling the mutation directly:**

```bash
# The script handles all the safe preservation logic automatically
./scripts/gh-project-add-columns.sh \
  --project <project-number> \
  --field "Status" \
  --add "AI Review" \
  --add "Human Review" \
  --add "Merge/Release" \
  --add "Blocked"
```

**What the script does internally:**

1. Queries the project's Status field to get all existing options with their IDs
2. Checks if any of the new column names already exist (skips duplicates)
3. Builds the mutation payload with ALL existing options (preserving IDs) plus new options
4. Executes the `updateProjectV2Field` mutation
5. Re-queries the field to verify existing assignments survived
6. Reports success or failure with details

**The script is located at:** `scripts/gh-project-add-columns.sh` in the EOA plugin directory.

---

## 3.3 gh auth refresh requires interactive browser

The command `gh auth refresh -h github.com -s project,read:project` requires an interactive browser-based OAuth flow. This means:

1. **Cannot be run inside tmux** (unless tmux has access to a display)
2. **Cannot be run inside SSH** (unless X11 forwarding or equivalent is configured)
3. **Cannot be run by agents** (agents run in non-interactive contexts)
4. **Cannot be automated** (requires human interaction with a browser)

**Workaround:** This is a ONE-TIME setup step. The human operator must run this command ONCE on each machine before deploying agents. Once done, the scopes persist.

**See** [gh-auth-scopes.md](gh-auth-scopes.md) Section 1.4 for the full procedure.

---

## 3.4 updateProjectV2Field does not accept projectId

The `updateProjectV2Field` mutation input type (`UpdateProjectV2FieldInput`) does NOT accept a `projectId` parameter. Only `fieldId` is accepted.

**Wrong:**
```graphql
mutation {
  updateProjectV2Field(input: {
    projectId: "PVT_..."    # WILL CAUSE ERROR
    fieldId: "PVTF_..."
    name: "Status"
    singleSelectOptions: [...]
  }) { ... }
}
```

**Error message:**
```
InputObject 'UpdateProjectV2FieldInput' doesn't accept argument 'projectId'
```

**Correct:**
```graphql
mutation {
  updateProjectV2Field(input: {
    fieldId: "PVTF_..."     # Only fieldId needed
    name: "Status"
    singleSelectOptions: [...]
  }) { ... }
}
```

**Why this works:** The `fieldId` already uniquely identifies which project the field belongs to. The project context is implicit — there is no need to specify it separately.

**Other mutations that DO accept projectId:**
- `updateProjectV2ItemFieldValue` - requires both `projectId` and `itemId`
- `addProjectV2ItemById` - requires `projectId` and `contentId`
- `deleteProjectV2Item` - requires `projectId` and `itemId`

Only `updateProjectV2Field` (for modifying field configuration) takes just `fieldId`.
