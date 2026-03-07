## Table of Contents
- [PROCEDURE 1: Create Project Board](#procedure-1-create-project-board)
- [PROCEDURE 2: Add or Modify Columns](#procedure-2-add-or-modify-columns)
- [PROCEDURE 3: Move Items Between Columns](#procedure-3-move-items-between-columns)
- [PROCEDURE 4: Sync Kanban Status](#procedure-4-sync-kanban-status)

---

### PROCEDURE 1: Create Project Board

**When to use:** When setting up a new project's kanban board for the first time.

**Steps:**
1. Verify gh auth has project scopes (pre-flight check)
2. Create the GitHub Project via `gh project create`
3. Add the 8 standard columns using `gh-project-add-columns.py`
4. Link the repository to the project
5. Register the project number in `.github/project.json`

### PROCEDURE 2: Add or Modify Columns

**When to use:** When adding new status columns to an existing project board.

**CRITICAL WARNING:** The `updateProjectV2Field` GraphQL mutation REPLACES all options. If you do not include existing option IDs in the mutation, ALL existing column assignments will be lost. See [kanban-pitfalls.md](kanban-pitfalls.md) Section 3.2 for details.

**Steps:**
1. ALWAYS use the safe column adder script: `scripts/gh-project-add-columns.py`
2. NEVER manually call `updateProjectV2Field` without preserving existing option IDs
3. Verify existing assignments survived after the mutation

**Script usage:**
```bash
# Add new columns safely (preserves existing columns and their assignments)
python3 scripts/gh-project-add-columns.py --project <number> --field "Status" --add "AI Review" --add "Human Review"
```

### PROCEDURE 3: Move Items Between Columns

**When to use:** When updating a task's kanban status (e.g., moving from "In Progress" to "AI Review").

**Steps:**
1. Get the project item ID and field ID
2. Get the option ID for the target column
3. Execute `gh project item-edit` with the correct IDs
4. If moving to "Done", check if the linked issue was auto-closed (see pitfalls)

### PROCEDURE 4: Sync Kanban Status

**When to use:** When synchronizing label-based status with the GitHub Project board, or vice versa.

**Steps:**
1. Run the sync script: `amoa_sync_kanban.py`
2. Verify label status matches board column
3. Resolve any conflicts (board takes precedence for manual moves)
