## Table of Contents
- [Step-by-Step Instructions](#step-by-step-instructions)
- [Distribution Checklist](#distribution-checklist)

---

## Step-by-Step Instructions

Follow these steps to distribute tasks to agents:

1. Query all issues with `status:ready` label
2. Sort ready tasks by priority (critical > high > normal > low)
3. For each task in priority order:
   1. Check if dependencies are resolved (blockedBy list is empty)
   2. If blocked, skip to next task
   3. If ready, evaluate available agents for skill match
   4. Select agent with best match score and lowest current load
   5. Remove any existing `assign:*` label from the issue
   6. Add `assign:<agent-name>` label to the issue
   7. Update issue status from `status:ready` to `status:in-progress`
   8. Send task assignment message via AI Maestro using the `agent-messaging` skill (see assignment protocol)
   9. Wait for agent ACK before considering next task
   10. Log assignment in delegation log file

## Distribution Checklist

Copy this checklist and track your progress:

**Task Distribution Workflow:**
- [ ] Query all issues with `status:ready` label
- [ ] Sort ready tasks by priority (critical > high > normal > low)
- [ ] Check if task dependencies are resolved (blockedBy list empty)
- [ ] If blocked, skip to next task
- [ ] Evaluate available agents for skill match
- [ ] Check agent availability (active, hibernated, offline)
- [ ] Check agent capacity (0-2 tasks acceptable, 3+ at capacity)
- [ ] Select agent with best match score and lowest load
- [ ] Remove any existing `assign:*` label from the issue
- [ ] Add `assign:<agent-name>` label to the issue
- [ ] Update issue status from `status:ready` to `status:in-progress`
- [ ] Send task assignment message via AI Maestro using the `agent-messaging` skill
- [ ] Wait for agent ACK before considering next task
- [ ] Log assignment in delegation log file
