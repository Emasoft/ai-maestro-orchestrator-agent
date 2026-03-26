## Table of Contents

- 1 /add-module command syntax and arguments
- 2 /modify-module command syntax and restrictions
- 3 /remove-module command syntax and restrictions
- 4 /prioritize-module command syntax
- 5 /reassign-module command syntax and workflow

---

## 1 /add-module

**Usage**: `/add-module "<NAME>" --criteria "<TEXT>" [--priority LEVEL]`

| Argument | Required | Description |
|----------|----------|-------------|
| NAME | Yes | Display name for the module |
| --criteria | Yes | Acceptance criteria text |
| --priority | No | `critical`, `high`, `medium`, `low` (default: medium) |

**What Happens**:
1. Module entry created in state file
2. GitHub Issue created with labels
3. Stop hook updated to include new module

**Example**:
```bash
/add-module "Two-Factor Auth" --criteria "Support TOTP and SMS" --priority critical
```

## 2 /modify-module

**Usage**: `/modify-module <MODULE_ID> [--name NAME] [--criteria TEXT] [--priority LEVEL]`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to modify |
| --name | No | New display name |
| --criteria | No | New acceptance criteria |
| --priority | No | New priority level |

**Restrictions**:
- `pending` modules: All fields modifiable
- `in-progress` modules: Modifiable with agent notification
- `complete` modules: Cannot modify

**Example**:
```bash
/modify-module auth-core --criteria "Support JWT with 24h expiry" --priority high
```

## 3 /remove-module

**Usage**: `/remove-module <MODULE_ID> [--force]`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to remove |
| --force | No | Skip confirmation |

**Restrictions**:
- Only `pending` modules can be removed
- `in-progress` modules cannot be removed
- `complete` modules cannot be removed

**Example**:
```bash
/remove-module oauth-facebook
```

## 4 /prioritize-module

**Usage**: `/prioritize-module <MODULE_ID> --priority <LEVEL>`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module |
| --priority | Yes | `critical`, `high`, `medium`, `low` |

**Example**:
```bash
/prioritize-module auth-core --priority critical
```

## 5 /reassign-module

**Usage**: `/reassign-module <MODULE_ID> --to <AGENT_ID>`

| Argument | Required | Description |
|----------|----------|-------------|
| MODULE_ID | Yes | ID of module to reassign |
| --to | Yes | ID of new agent |

**What Happens**:
1. Old agent receives STOP notification
2. Assignment record transferred
3. New agent receives full assignment
4. Instruction Verification Protocol resets

**Example**:
```bash
/reassign-module auth-core --to implementer-2
```
