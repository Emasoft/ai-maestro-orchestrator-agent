# Module Management Commands

Dynamic module manipulation commands for EOA orchestration. Enables adding, modifying, removing, prioritizing, and reassigning modules during the Orchestration Phase.

## When to Use

- User requests new features mid-orchestration
- Requirements or acceptance criteria change
- Module needs cancellation before work starts
- Priority needs to change
- Module needs different agent assignment
- Understanding how modules sync with GitHub Issues

## Key Principle

**Every module maps 1:1 to a GitHub Issue.** All module operations automatically sync with GitHub.

## Commands

| Command | Purpose | Restrictions |
|---------|---------|--------------|
| `/add-module` | Create new module + issue | None |
| `/modify-module` | Update specs/priority | Cannot modify completed |
| `/remove-module` | Delete pending module | Pending status only |
| `/prioritize-module` | Change priority level | None |
| `/reassign-module` | Transfer to new agent | Cannot reassign completed |

## Quick Examples

```bash
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical
/modify-module auth-core --criteria "Support JWT with 24h expiry"
/remove-module oauth-facebook
/prioritize-module auth-core --priority critical
/reassign-module auth-core --to implementer-2
```

## Scripts

- `scripts/module_operations.py` - Programmatic module operations
- `scripts/github_sync.py` - GitHub Issue synchronization

## Requirements

- Python 3.8+ with PyYAML
- gh CLI (authenticated)
- AI Maestro for agent notifications

## See Also

- [SKILL.md](./SKILL.md) - Complete documentation
- [references/](./references/) - Detailed reference documents
