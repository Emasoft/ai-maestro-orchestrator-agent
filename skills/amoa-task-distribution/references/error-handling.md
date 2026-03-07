## Table of Contents
- [Error Table](#error-table)

---

## Error Table

| Error | Cause | Solution |
|-------|-------|----------|
| No available agents | All agents at capacity or offline | Wait for agent capacity or escalate to user |
| Circular dependency detected | Task A blocks B, B blocks A | Report to user for manual resolution |
| Agent does not ACK assignment | Agent unresponsive or hibernated | Send reminder, then escalate to **amoa-progress-monitoring** |
| Skill mismatch | No agent has required toolchain | Escalate to user or reassign with training |
| Dependency never completes | Blocking task stuck | Escalate to **amoa-progress-monitoring** for blocker resolution |
| Label conflict (multiple assign:*) | Concurrent update | Remove all `assign:*` labels, reapply correct one |
