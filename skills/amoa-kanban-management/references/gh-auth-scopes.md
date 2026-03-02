# GitHub CLI Authentication and OAuth Scopes

## Table of Contents

- 1.1 Why project scopes are required - Default gh auth login does not include them
- 1.2 Complete list of required OAuth scopes - All scopes needed for agent operations
- 1.3 How to check current scopes - Verifying your authentication
- 1.4 How to add missing scopes - Interactive browser flow required
- 1.5 Pre-flight validation command - One-liner to check before operations
- 1.6 Scope provisioning is a manual pre-deployment step - Cannot be automated by agents
- 1.7 Troubleshooting - Common scope-related errors

---

## 1.1 Why project scopes are required

The GitHub CLI (`gh`) default authentication via `gh auth login` grants scopes for repository operations (issues, PRs, code) but does NOT include scopes for GitHub Projects V2. GitHub Projects V2 is a separate feature that requires its own OAuth scopes.

Without these scopes, any command that touches GitHub Projects will fail with:

```
error: your authentication token is missing required scopes [project read:project]
```

This affects:
- `gh project create`
- `gh project list`
- `gh project item-list`
- `gh project item-add`
- `gh project item-edit`
- `gh project field-list`
- `gh api graphql` with ProjectV2 queries/mutations

---

## 1.2 Complete list of required OAuth scopes

The following table lists ALL OAuth scopes required for the full agent ecosystem operations:

| Scope | Required By | Purpose |
|-------|------------|---------|
| `repo` | All agents | Repository access (issues, PRs, code, actions) |
| `project` | EOA, ECOS | Create, modify, and delete GitHub Projects V2 boards |
| `read:project` | EOA, ECOS | Read GitHub Projects V2 data (items, fields, columns) |
| `read:org` | ECOS (if org) | Read organization data for org-level projects |
| `workflow` | EIA | Trigger and manage GitHub Actions workflows |

**Minimum scopes for kanban operations:** `repo`, `project`, `read:project`

---

## 1.3 How to check current scopes

Run this command to see what scopes your current authentication includes:

```bash
gh auth status
```

Example output with project scopes:
```
github.com
  ✓ Logged in to github.com account Emasoft (/Users/user/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_****
  - Token scopes: 'gist', 'project', 'read:org', 'read:project', 'repo', 'workflow'
```

If you do NOT see `project` and `read:project` in the "Token scopes" line, you need to add them (see Section 1.4).

**Quick check (scriptable):**

```bash
# Returns exit code 0 if project scopes present, 1 if missing
gh auth status 2>&1 | grep -q "project" && echo "OK" || echo "MISSING"
```

---

## 1.4 How to add missing scopes

Adding scopes requires an interactive browser-based OAuth flow. This CANNOT be done programmatically or in a non-interactive terminal session (like tmux without a display).

**Command to add project scopes:**

```bash
gh auth refresh -h github.com -s project,read:project
```

**What happens when you run this command:**

1. The terminal displays a one-time code (e.g., `ABCD-1234`)
2. A browser window opens (or a URL is printed for manual navigation)
3. You log in to GitHub in the browser
4. You enter the one-time code
5. You authorize the new scopes
6. The terminal confirms the scopes were added

**After adding scopes, verify:**

```bash
gh auth status
# Should now show 'project' and 'read:project' in Token scopes
```

---

## 1.5 Pre-flight validation command

Use this one-liner before any kanban operation to validate scopes:

```bash
gh auth status 2>&1 | grep -q "project" || { echo "ERROR: Missing project scope. Run: gh auth refresh -h github.com -s project,read:project"; exit 1; }
```

**For Python scripts**, use this pre-flight check:

```python
import subprocess
import sys

def check_gh_project_scopes() -> bool:
    """Verify gh auth has project scopes. Returns True if scopes present."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    if "project" not in combined:
        print(
            "ERROR: gh auth is missing 'project' and 'read:project' scopes.\n"
            "A human must run: gh auth refresh -h github.com -s project,read:project\n"
            "This requires interactive browser approval and cannot be automated.",
            file=sys.stderr,
        )
        return False
    return True
```

---

## 1.6 Scope provisioning is a manual pre-deployment step

**This is critical for agent deployment:**

Scope provisioning CANNOT be automated by agents because:

1. `gh auth refresh` requires an interactive browser-based OAuth flow
2. Non-interactive sessions (tmux, SSH without display forwarding) will fail
3. The human operator must approve the scope change in the browser

**Deployment procedure:**

Before deploying ANY agent that manages GitHub Project boards (EOA, ECOS), the human operator MUST:

1. Open a terminal with browser access (NOT inside tmux or SSH)
2. Run: `gh auth refresh -h github.com -s project,read:project`
3. Complete the browser-based approval
4. Verify: `gh auth status` shows project scopes
5. Only THEN deploy agents that use kanban operations

**This is a ONE-TIME operation per machine.** Once the scopes are added, they persist across all `gh` CLI sessions on that machine until the token is revoked or replaced.

---

## 1.7 Troubleshooting

### Error: `your authentication token is missing required scopes [project read:project]`

**Cause:** gh auth does not have project scopes.
**Fix:** Run `gh auth refresh -h github.com -s project,read:project` in an interactive terminal.

### Error: `gh auth refresh` fails with "could not prompt"

**Cause:** Running in a non-interactive session (tmux, SSH, agent subprocess).
**Fix:** Run the command in a terminal with browser access. This CANNOT be done from within an agent session.

### Error: `gh auth refresh` opens browser but authorization fails

**Cause:** The GitHub account may have SSO requirements or organization policies.
**Fix:**
1. Check if your organization requires SSO: `gh auth status`
2. If SSO is required, visit `https://github.com/settings/tokens` and authorize the token for SSO
3. Retry the refresh command

### Error: Scopes were added but commands still fail

**Cause:** Token may have been cached or a different token is being used.
**Fix:**
1. Check which token is active: `gh auth status`
2. If using `GH_TOKEN` environment variable, update it
3. Try: `gh auth logout` then `gh auth login` with all required scopes

### Error: `gh project list` returns empty but projects exist

**Cause:** The `--owner` flag may be wrong, or the project is organization-owned.
**Fix:**
1. Check project ownership: `gh project list --owner <your-username>`
2. For org projects: `gh project list --owner <org-name>`
3. Add `read:org` scope if querying organization projects
