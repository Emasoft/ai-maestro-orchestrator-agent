## Table of Contents

- 1 Add new module mid-orchestration
- 2 Reassign a blocked module
- 3 Scripts reference for programmatic access

---

## 1 Add New Module Mid-Orchestration

```bash
# User requests two-factor authentication
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical

# System automatically creates GitHub Issue #43
# Module appears in pending queue with status: pending
```

## 2 Reassign Blocked Module

```bash
# Agent implementer-1 is blocked on auth-core
# Request progress report first
/check-agents --agent implementer-1

# Reassign to implementer-2
/reassign-module auth-core --to implementer-2

# Old agent notified to stop
# New agent receives full assignment with Instruction Verification Protocol reset
```

## 3 Scripts Reference

| Script | Purpose |
|--------|---------|
| `amoa_modify_module.py` | Add, modify, or remove modules |
| `amoa_assign_module.py` | Assign modules to agents |
| `amoa_reassign_module.py` | Reassign modules between agents |

```bash
# Add/modify/remove module
uv run scripts/amoa_modify_module.py add "Module Name" --criteria "Criteria"
uv run scripts/amoa_modify_module.py modify module-id --priority critical
uv run scripts/amoa_modify_module.py remove module-id

# Assign module to agent
uv run scripts/amoa_assign_module.py module-id --to implementer-1

# Reassign module between agents
uv run scripts/amoa_reassign_module.py module-id --from implementer-1 --to implementer-2
```
