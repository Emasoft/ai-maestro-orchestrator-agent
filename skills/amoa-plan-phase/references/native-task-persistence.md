# Native Task Persistence Principle

## Contents
- 1. Overview - Why use Claude Code native Tasks
- 2. Task Tool Reference - TaskCreate, TaskUpdate, TaskList, TaskGet
- 3. Task Lifecycle - Creating, tracking, and completing tasks
- 4. Persistence Across Compacting - How tasks survive context limits
- 5. Stop Hook Integration - How orchestrator checks task completion
- 6. Best Practices - Effective task management patterns

---

## 1. Overview

**CRITICAL REQUIREMENT**: All instructions and work items must be scheduled as Claude Code native Tasks using TaskCreate. This ensures persistence across context compacting.

### Why Native Tasks?

Claude Code provides built-in task management tools that:
- **Persist across context compacting** - Tasks survive when conversation history is summarized
- **Integrate with the orchestrator** - Stop hooks can query task status via transcript
- **Support dependencies** - Tasks can block other tasks with `addBlockedBy`
- **Track progress** - Status flows from `pending` to `in-progress` to `completed`

### Key Advantages

Claude Code native Tasks:
- Do NOT require file I/O operations
- Do NOT need external scripts to parse
- Are automatically tracked by Claude Code runtime
- Appear in conversation summaries after compacting

---

## 2. Task Tool Reference

### TaskCreate

Creates a new task with pending status.

```
TaskCreate(
  subject="Brief task title",
  description="Detailed description of what needs to be done",
  activeForm="Doing the task"  # Present participle for status display
)
```

**Parameters:**
- `subject` (required): Brief imperative title (e.g., "Implement login validation")
- `description` (required): Detailed requirements and acceptance criteria
- `activeForm` (recommended): Present continuous form shown during execution (e.g., "Implementing login validation")

### TaskUpdate

Updates an existing task's status or properties.

```
TaskUpdate(
  taskId="<task-id>",
  status="in-progress"  # or "completed" or "pending"
)
```

**Status Values:**
- `pending` - Task not yet started
- `in-progress` - Task currently being worked on
- `completed` - Task finished successfully

**Dependency Parameters:**
- `addBlockedBy`: List of task IDs that must complete before this task can start
- `addBlocks`: List of task IDs that this task blocks

### TaskList

Returns all tasks with their current status.

```
TaskList()
```

Returns:
- Task IDs
- Subject lines
- Current status
- Owner (if assigned)
- Blocked-by relationships

### TaskGet

Retrieves full details of a specific task.

```
TaskGet(taskId="<task-id>")
```

Returns:
- Full description
- All status fields
- Dependency information
- Metadata

---

## 3. Task Lifecycle

### Creating Tasks

When starting a workflow, create all required tasks upfront:

```
1. TaskCreate(subject="Design authentication module", ...)
2. TaskCreate(subject="Implement login endpoint", ...)
3. TaskCreate(subject="Write authentication tests", ...)
4. TaskUpdate(taskId="2", addBlockedBy=["1"])  # Login blocked by design
5. TaskUpdate(taskId="3", addBlockedBy=["2"])  # Tests blocked by implementation
```

### Working on Tasks

Before starting work:
```
TaskUpdate(taskId="1", status="in-progress")
```

After completing work:
```
TaskUpdate(taskId="1", status="completed")
```

### Checking Progress

Periodically review task status:
```
TaskList()
```

This shows all tasks and their current state, helping identify:
- What's completed
- What's in progress
- What's blocked
- What's ready to start

---

## 4. Persistence Across Compacting

### How It Works

When Claude Code's context window fills up, it performs **compacting**:
1. Conversation history is summarized
2. Important state is preserved
3. Tasks are included in the preserved state

### What Gets Preserved

- Task IDs
- Subject lines
- Current status
- Blocking relationships

### What May Be Lost

- Full task descriptions (use TaskGet to retrieve)
- Detailed metadata
- Creation timestamps

### Best Practice

After context compacting:
1. Run `TaskList()` to see current state
2. Use `TaskGet(taskId)` for any task you need full details on
3. Continue working from the preserved state

---

## 5. Stop Hook Integration

The orchestrator stop hook checks task completion status to prevent premature exit.

### How Tasks Are Checked

The `check_claude_tasks()` function in `tasks.py`:

1. Reads the transcript JSON file
2. Finds all `"todos"` arrays (there may be multiple from different turns)
3. Uses the **last** todos array (most recent state)
4. Counts tasks with `status: "pending"` or `status: "in-progress"`
5. Returns count and sample task subjects

### Blocking Logic

If pending tasks > 0:
- Exit is blocked
- Claude receives a prompt listing pending task sources
- Orchestration continues

If pending tasks = 0:
- Verification mode begins (4 loops)
- After all verification loops pass, exit is allowed

### Transcript Parsing

The hook parses JSON patterns like:
```json
"todos": [
  {"id": "1", "subject": "Task A", "status": "completed"},
  {"id": "2", "subject": "Task B", "status": "pending"}
]
```

---

## 6. Best Practices

### Task Naming

- Use imperative form: "Implement X" not "Implementing X"
- Be specific: "Add email validation to signup form" not "Fix validation"
- Include context: "Fix login timeout (issue #123)"

### Task Granularity

- One task = one logical unit of work
- Tasks should be completable in a single focus session
- If a task needs multiple subtasks, create separate tasks with dependencies

### Using Dependencies

```
# Task 2 cannot start until Task 1 completes
TaskUpdate(taskId="2", addBlockedBy=["1"])

# Task 3 blocks Task 4 and Task 5
TaskUpdate(taskId="3", addBlocks=["4", "5"])
```

### Status Discipline

1. **Always** set `in-progress` before starting work
2. **Always** set `completed` after finishing
3. **Never** leave tasks in `in-progress` if you're not actively working on them
4. Use `pending` for tasks waiting to be started or blocked

### Verification Before Completion

Before marking a task completed:
1. Verify the work meets acceptance criteria
2. Run any relevant tests
3. Check that dependent tasks can now proceed
4. Update any documentation

---

## Summary

**Key Points:**
1. Use Claude Code native Tasks (TaskCreate, TaskUpdate, TaskList, TaskGet)
2. Tasks persist across context compacting
3. The orchestrator stop hook checks task status via transcript
4. Follow the lifecycle: create → in-progress → completed
5. Use dependencies to enforce task ordering
