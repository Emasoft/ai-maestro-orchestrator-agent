## Table of Contents
- [PROCEDURE 1: Create Project Board](#procedure-1-create-project-board)
- [PROCEDURE 2: Add or Modify Columns](#procedure-2-add-or-modify-columns)
- [PROCEDURE 3: Move Items Between Columns](#procedure-3-move-items-between-columns)
- [PROCEDURE 4: Sync Kanban Status](#procedure-4-sync-kanban-status)
- [PROCEDURE 5: Attach the Child Breakdown Under the Architect's Epic](#procedure-5-attach-the-child-breakdown-under-the-architects-epic)

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

### PROCEDURE 5: Attach the Child Breakdown Under the Architect's Epic

**When to use:** When breaking a received design-handoff into AI-Maestro implementation
tasks. The architect (architect#7) creates one `epic` task on the AI-Maestro kanban and
carries its id in the design-handoff message as the optional top-level `aimaestro_task_id`
key inside `content` (both `design_complete` and `handoff` shapes). Reading it lets AMOA
hang its child tasks under that epic, completing design-doc → epic → child → GitHub-issue
traceability. This is the read-side of orch#26.

**Steps:**
1. Read the epic id from the handoff with `extract_aimaestro_task_id` (None when absent)

   Absence is normal — older handoffs, or AI-Maestro not in use:
   ```python
   from amoa_design_handoff import extract_aimaestro_task_id  # shared/ on sys.path
   epic = extract_aimaestro_task_id(message_content)   # str | None
   ```
2. Create each first-level child under the epic with `amp-kanban-create-task --parent`

   Frozen verb only; never a raw `/api/*` call (R23):
   ```bash
   amp-kanban-create-task "<child subject>" \
     ${EPIC:+--parent "$EPIC"} \
     --task-type <feature|bugfix|refactor|infra|docs> --status backburner
   ```
3. When the epic id is None, create the children unparented — no regression

   Behave exactly as before AI-Maestro linkage existed. A handoff without the key
   must produce the same result it always did.

**Note (deployment-time):** confirming the children actually read back under the epic
(`parentTask` round-trips) needs a live AI-Maestro server + an AMCOS-spawned agent binding —
tracked as the deferred check on TRDD-6B3K7S69, parallel to the architect's TRDD-364ccafc
Phase 0.
