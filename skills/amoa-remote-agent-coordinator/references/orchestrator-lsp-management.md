# Orchestrator LSP Management Guide

How the orchestrator manages LSP servers for remote AI agents.

## Contents

- [When setting up the orchestrator for the first time](#when-setting-up-the-orchestrator-for-the-first-time)
- [When assigning a task to a remote agent](#when-assigning-a-task-to-a-remote-agent)
- [When an agent reports LSP problems](#when-an-agent-reports-lsp-problems)
- [When the agent completes work](#when-the-agent-completes-work)
- [When you need to understand the orchestrator's role](#when-you-need-to-understand-the-orchestrators-role)
- [When you need reference material](#when-you-need-reference-material)
- [When you need practical workflow examples](#when-you-need-practical-workflow-examples)
- [When you need to troubleshoot LSP issues](#when-you-need-to-troubleshoot-lsp-issues)
- [When implementing automated orchestration](#when-implementing-automated-orchestration)

---

## Critical Distinction: Global vs Local

**LSP management has TWO separate concerns:**

| Concern | Who Does It | Scope | Commands |
|---------|-------------|-------|----------|
| **Global Binaries** | Orchestrator | System-wide (once) | `--install-binaries`, `--uninstall-binaries` |
| **Local Activation** | Remote Agent | Per-project | `--activate`, `--deactivate`, `--sync` |

### Why This Matters

- **Orchestrator** installs binaries globally (shared across all projects)
- **Orchestrator** NEVER activates LSP locally (it doesn't write code)
- **Remote agents** activate only the LSP plugins needed for their assigned project
- **Remote agents** deactivate unneeded plugins to save resources

## When you need to understand the orchestrator's role

The orchestrator ensures:
1. All required binaries are installed globally (one-time setup)
2. Remote agents know which LSP plugins to activate locally

This optimizes:
- **Memory usage**: Agents only activate needed LSP plugins
- **Startup time**: Fewer active plugins = faster response
- **Resource isolation**: Each project has its own activation state
- **Clean handoffs**: Agents deactivate when switching projects

## When setting up the orchestrator for the first time

### Step 1: Install Global Binaries

Before any task assignment, ensure all required binaries are installed globally:

```bash
# Install ALL supported LSP binaries globally (recommended for orchestrator machine)
python install_lsp.py --install-binaries --all

# Or install specific languages needed for your projects
python install_lsp.py --install-binaries --languages python,typescript,go,rust

# Verify global binaries are available
python install_lsp.py --verify-binaries --all
```

## When assigning a task to a remote agent

### Step 1: Generate Activation Instructions

Before the assignment, generate activation instructions for the remote agent:

```bash
# Generate instructions showing what agent needs to activate
python install_lsp.py --project-path /path/to/project --generate-instructions

# Check current global binary status
python install_lsp.py --status --json
```

### Step 2: Include LSP Activation Instructions in Task Assignment

When assigning a task to a remote agent, include these activation instructions:

```markdown
## LSP Activation Required

Before starting work, activate LSP plugins for this project:

```bash
# Activate LSP for project languages (recommended)
python install_lsp.py --project-path /path/to/project --sync

# This will:
# - Activate LSP plugins for detected languages
# - Deactivate LSP plugins not needed for this project
# - Create local state file at .claude/lsp-state.json
```

Verify setup:
```bash
python install_lsp.py --status --project-path /path/to/project
```
```

## When the agent completes work

### Cleanup Instructions

Instruct the agent to clean up before moving to the next task:

```bash
# Agent should deactivate all LSP before switching projects
python install_lsp.py --deactivate-all

# Verify no LSP errors in modified files
/plugin errors
```

## When an agent reports LSP problems

Common issues and quick resolutions:

| Problem | Cause | Solution |
|---------|-------|----------|
| "Binary not found" | LSP binary not installed globally | Orchestrator: Run `--install-binaries` for that language |
| Wrong LSP activated | Incorrect local state | Agent: Run `--deactivate-all` then `--sync` |
| State file corrupted | Malformed `.claude/lsp-state.json` | Agent: Delete state file, run `--sync` again |
| Languages changed after branch switch | Activation cache out of sync | Agent: Run `--sync` to detect new languages |
| No type checking happening | LSP never activated | Agent: Run `--sync` to activate for project |

For detailed troubleshooting steps, see [When you need to troubleshoot LSP issues](#when-you-need-to-troubleshoot-lsp-issues) below.

---

## When you need reference material

### Orchestrator Commands (Global Binaries)

| Command | Purpose |
|---------|---------|
| `--install-binaries --all` | Install ALL LSP binaries globally |
| `--install-binaries --languages X,Y` | Install specific LSP binaries globally |
| `--uninstall-binaries --languages X,Y` | Remove specific LSP binaries globally |
| `--verify-binaries` | Verify global binaries are installed |
| `--generate-instructions` | Create activation instructions for agent |
| `--status --json` | Show status in JSON for automation |

### Remote Agent Commands (Local Activation)

| Command | Purpose |
|---------|---------|
| `--activate --project-path PATH` | Activate LSP for detected languages |
| `--activate --languages X,Y` | Activate specific LSP plugins |
| `--deactivate --languages X,Y` | Deactivate specific LSP plugins |
| `--deactivate-all` | Deactivate ALL LSP plugins (clean slate) |
| `--sync --project-path PATH` | Activate needed, deactivate others |
| `--status` | Show global + local activation status |

### Common Options

| Option | Purpose |
|--------|---------|
| `--project-path PATH` | Project to analyze/activate |
| `--languages X,Y,Z` | Specific languages to target |
| `--all` | All supported languages |
| `--json` | JSON output for automation |
| `-q, --quiet` | Suppress output |

## When you need practical workflow examples

### Example 1: Python-Only Project

Orchestrator assigns Python project to agent:

```
Orchestrator (one-time global setup):
  python install_lsp.py --install-binaries --all

Orchestrator generates instructions:
  python install_lsp.py --project-path /projects/python-app --generate-instructions

Instructions sent to agent:
  "Activate LSP for this Python project:
   python install_lsp.py --project-path /projects/python-app --sync

   This will:
   - Activate: python (pyright)
   - Deactivate: all others
   - State saved to: /projects/python-app/.claude/lsp-state.json"
```

### Example 2: Full-Stack TypeScript/Go Project

```
Orchestrator generates instructions:
  python install_lsp.py --project-path /projects/fullstack --generate-instructions

Instructions sent to agent:
  "Activate LSP for this full-stack project:
   python install_lsp.py --project-path /projects/fullstack --sync

   This will:
   - Activate: typescript, go, html, css
   - Deactivate: python, java, rust, etc."

After agent completes work:
  "Clean up before next assignment:
   python install_lsp.py --deactivate-all"
```

### Example 3: Multi-Language Monorepo

```
Orchestrator generates instructions:
  python install_lsp.py --project-path /projects/monorepo --generate-instructions

Instructions sent to agent:
  "This is a large monorepo with 5 languages.
   Activate all required LSP plugins:
   python install_lsp.py --project-path /projects/monorepo --sync

   Expected activated: python, typescript, go, rust, java

   Note: Higher resource usage expected due to multiple LSP plugins."
```

### Example 4: Agent Switching Projects

```
Agent finishing Project A (Python):
  python install_lsp.py --deactivate-all

Agent starting Project B (TypeScript/React):
  python install_lsp.py --project-path /projects/react-app --sync

  # Only typescript, html, css activated
  # Clean state from previous project
```

## Task Assignment Template

Include this in every task assignment:

```markdown
## Environment Setup

### LSP Activation
Required languages: {detected_languages}

Activate before starting:
```bash
python install_lsp.py --project-path {project_path} --sync
```

This creates a local state file at `{project_path}/.claude/lsp-state.json`.

### Verification
After activation, verify status:
```bash
python install_lsp.py --status --project-path {project_path}
/plugin errors  # Should show no errors
```

### Quality Gate
Before submitting work:
- [ ] All LSP diagnostics resolved
- [ ] Type checking passes for all languages
- [ ] No "any" types in TypeScript
- [ ] No "type: ignore" in Python

### Cleanup
After completing work:
```bash
python install_lsp.py --deactivate-all
```
```

## When implementing automated orchestration

For automated orchestration, use the JSON API:

```python
import subprocess
import json

# Get global + local status
result = subprocess.run(
    ["python", "install_lsp.py", "--status", "--json"],
    capture_output=True, text=True
)
status = json.loads(result.stdout)
# {
#   "global_binaries_installed": ["python", "typescript", ...],
#   "local_lsp_activated": ["python"],
#   "supported_languages": ["python", "typescript", ...]
# }

# Orchestrator: Install global binaries
subprocess.run([
    "python", "install_lsp.py",
    "--install-binaries", "--all"
], check=True)

# Remote agent: Sync activation for project
subprocess.run([
    "python", "install_lsp.py",
    "--project-path", "/path/to/project",
    "--sync", "-q"
], check=True)

# Remote agent: Cleanup after task
subprocess.run([
    "python", "install_lsp.py",
    "--deactivate-all", "-q"
], check=True)
```

## Shared Package Handling

Some LSP servers share packages (e.g., html and css both use `vscode-langservers-extracted`).

The script handles this automatically:
- When uninstalling `html`, it checks if `css` still needs the package
- Only uninstalls the shared package when NEITHER language is needed
- Prevents breaking one language when cleaning up another

## When you need to troubleshoot LSP issues

### When an agent reports "Binary not found"

This is a GLOBAL issue - the orchestrator needs to install the binary:

```bash
# Orchestrator: Install missing binary globally
python install_lsp.py --install-binaries --languages {language}

# Verify binary is in PATH
echo $PATH
which {binary_name}
```

### When an agent has the wrong LSP activated

This is a LOCAL issue - the agent needs to sync:

```bash
# Agent: Deactivate all, then sync fresh
python install_lsp.py --deactivate-all
python install_lsp.py --project-path /path/to/project --sync
```

### When activation state is corrupted

```bash
# Delete local state file and re-sync
rm -f /path/to/project/.claude/lsp-state.json
python install_lsp.py --project-path /path/to/project --sync
```

### When project languages change (after branch switch)

```bash
# Re-sync to detect new languages
python install_lsp.py --project-path . --sync
```

### When an agent started without LSP activation

If an agent is working without LSP (no type checking):

```bash
# Activate now
python install_lsp.py --project-path . --sync

# Verify activation
python install_lsp.py --status
```

## Best Practices

### For Orchestrator

1. **Install all binaries globally upfront**: Run `--install-binaries --all` once
2. **Never activate LSP locally**: Orchestrator doesn't write code
3. **Generate clear instructions**: Use `--generate-instructions` for each assignment
4. **Include cleanup step**: Always tell agents to `--deactivate-all` after work

### For Remote Agents

1. **Always sync before starting**: Run `--sync` to activate only needed LSP
2. **Verify activation**: Check `--status` shows correct languages activated
3. **Clean up after completion**: Run `--deactivate-all` before switching projects
4. **Report missing binaries**: If binary not found, ask orchestrator to install globally

### For Both

1. **One state file per project**: Located at `.claude/lsp-state.json`
2. **Never share activation state**: Each project manages its own activation
3. **Re-sync on branch switch**: Languages may change between branches

## Local State File

The activation state is stored at `<project>/.claude/lsp-state.json`:

```json
{
  "activated": ["python", "typescript"],
  "note": "LSP plugins activated for this project. Managed by install_lsp.py."
}
```

This file:
- Is local to each project
- Should be added to `.gitignore`
- Is managed automatically by `--activate`, `--deactivate`, and `--sync`

## Official Documentation

- [Claude Code LSP Servers](https://code.claude.com/docs/en/plugins-reference#lsp-servers)
- [Claude Code Plugins](https://code.claude.com/docs/en/plugins-reference)

## Supported Languages (13 total)

| Category | Languages |
|----------|-----------|
| **Core** | Python, TypeScript, Go, Rust |
| **JVM** | Java, Kotlin |
| **Systems** | C/C++, Objective-C, Swift, C# |
| **Web** | PHP, Ruby, HTML, CSS |

### Apple Platform Notes

- **Objective-C**: Uses `clangd` (same as C/C++). Install LLVM via brew/apt/choco.
- **Swift**: Uses `sourcekit-lsp` bundled with Xcode (macOS) or Swift toolchain (Linux).
  - macOS: `xcode-select --install`
  - Linux: Download Swift toolchain from swift.org
  - Cannot be uninstalled separately from Xcode/Swift toolchain
