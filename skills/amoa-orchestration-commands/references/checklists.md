## Table of Contents
- Starting Orchestration checklist
- Monitoring Progress checklist
- Cancellation checklist

---

## Checklist: Starting Orchestration

- [ ] Plan Phase complete (`/approve-plan` executed)
- [ ] State file `design/state/exec-phase.md` exists
- [ ] Run `/start-orchestration` with optional `--project-id`
- [ ] Register AI agents with `/register-agent ai <agent_id> --session <session>`
- [ ] Assign modules with `/assign-module <module_id> <agent_id>`
- [ ] Execute Instruction Verification Protocol for each agent
- [ ] Begin polling with `/check-agents` every 10-15 minutes

---

## Checklist: Monitoring Progress

- [ ] Run `/orchestration-status` to see module completion
- [ ] Check for agents with incomplete instruction verification
- [ ] Review polling history for stuck agents
- [ ] Use `--verbose` flag for detailed diagnostics
- [ ] Check `/orchestrator-status` for pending tasks across sources

---

## Checklist: Cancellation

- [ ] Confirm you want to cancel (tasks may be incomplete)
- [ ] Run `/cancel-orchestrator`
- [ ] Verify state file removed
- [ ] Check no orphaned lock files in `.claude/`
- [ ] If needed, manually remove `design/state/loop.md`
