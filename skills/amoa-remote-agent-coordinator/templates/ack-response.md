# ACK Response Template

## Purpose

This template shows remote agents the EXACT format for acknowledging task delegations.

---

## Required Response Format

```
[ACK] {TASK_ID} - {STATUS}
Understanding: {1-line summary of what you will do}
```

---

## Status Values

| Status | When to Use |
|--------|-------------|
| `RECEIVED` | Task received, will begin work immediately |
| `CLARIFICATION_NEEDED` | Need more info before starting |
| `REJECTED` | Cannot accept task (explain why) |
| `QUEUED` | Have prior tasks, will start after completing them |

---

## Examples

### Example 1: RECEIVED (Ready to Start)

```
[ACK] GH-42-auth-implementation - RECEIVED
Understanding: Will implement JWT authentication with login/logout endpoints and refresh token support
```

### Example 2: CLARIFICATION_NEEDED (Questions)

```
[ACK] GH-42-auth-implementation - CLARIFICATION_NEEDED
Understanding: Implement JWT authentication system

Questions:
1. Should tokens expire after 24h or 7 days?
2. Should refresh tokens be stored in cookies or localStorage?
3. Is there an existing user model I should integrate with?
```

### Example 3: QUEUED (Busy with Prior Task)

```
[ACK] GH-42-auth-implementation - QUEUED
Understanding: JWT auth with login/logout and refresh tokens

Note: Currently completing GH-38, will start this in approximately 30 minutes.
Estimated start time: 14:30 UTC
```

### Example 4: REJECTED (Cannot Accept)

```
[ACK] GH-42-auth-implementation - REJECTED
Understanding: JWT authentication system

Reason: This task requires database schema modifications which are outside my assigned role.
Suggest: Reassign to database-agent or split into frontend/backend subtasks.
```

---

## Common Mistakes to Avoid

| Wrong | Correct |
|-------|---------|
| `ACK received` | `[ACK] GH-42-task - RECEIVED` |
| `Got it, will start` | `[ACK] GH-42-task - RECEIVED` + Understanding line |
| `[ACK] RECEIVED` | `[ACK] {task_id} - RECEIVED` (include task ID!) |
| Just starting work without ACK | MUST ACK first, then start |

---

## When NOT to ACK

You do NOT need to send an ACK for:
- Clarifying questions from orchestrator
- Feedback on your work
- Status inquiries
- General discussion

Only Task Delegations (with Task ID, Acceptance Criteria, Checklists) require ACK.

---

## After Sending ACK

1. Wait for orchestrator confirmation (if CLARIFICATION_NEEDED)
2. Begin work only after ACK is sent
3. Send progress updates at checkpoints
4. Send completion report when done
