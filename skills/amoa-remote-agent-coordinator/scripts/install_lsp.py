#!/usr/bin/env python3
"""Manage LSP servers for remote agents.

This script handles TWO separate concerns:
1. GLOBAL BINARY INSTALLATION: Installing LSP binaries system-wide (once per machine)
2. LOCAL LSP ACTIVATION: Activating/deactivating LSP plugins per project

The ORCHESTRATOR:
- Installs binaries globally (shared across all projects)
- NEVER activates LSP locally (it doesn't write code)
- Instructs remote agents on which LSP plugins to activate

REMOTE AGENTS:
- Use pre-installed global binaries
- Activate only the LSP plugins needed for their assigned project
- Deactivate unneeded LSP plugins to save resources

Python Requirements: 3.9+ (requires list[str] type hint syntax)

Usage:
    # ORCHESTRATOR: Install binaries globally (system-wide)
    python install_lsp.py --install-binaries --languages python,typescript,go

    # ORCHESTRATOR: Install ALL supported LSP binaries globally
    python install_lsp.py --install-binaries --all

    # ORCHESTRATOR: Verify global binaries are installed
    python install_lsp.py --verify-binaries

    # ORCHESTRATOR: Generate activation instructions for remote agent
    python install_lsp.py --project-path /path/to/project --generate-instructions

    # REMOTE AGENT: Activate LSP for project languages
    python install_lsp.py --project-path /path/to/project --activate

    # REMOTE AGENT: Activate specific languages only
    python install_lsp.py --activate --languages python,typescript

    # REMOTE AGENT: Deactivate specific languages
    python install_lsp.py --deactivate --languages java,kotlin

    # REMOTE AGENT: Deactivate ALL LSP plugins
    python install_lsp.py --deactivate-all

    # REMOTE AGENT: Sync (activate needed, deactivate others)
    python install_lsp.py --project-path /path/to/project --sync

    # List status (global binaries + local activation)
    python install_lsp.py --status
"""

# WHY: from __future__ import annotations enables PEP 604 union syntax (X | None)
# and forward references without quotes, ensuring compatibility with Python 3.9+.
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# Type alias for LSP configuration dictionaries
# WHY: Using dict[str, Any] allows flexible config structure while maintaining type safety
# at call sites. A TypedDict would be more precise but overly complex for optional fields.
LSPConfig = dict[str, Any]

# LSP configurations per language
# Covers all 13 languages supported including Apple platforms (December 2025)
# Reference: https://code.claude.com/docs/en/plugins-reference#lsp-servers
LSP_CONFIGS: dict[str, LSPConfig] = {
    # === Core languages (most common) ===
    "python": {
        "binary": "pyright-langserver",
        "alt_binary": "pyright",  # Alternative binary name to check
        "install_cmd": ["pip", "install", "pyright"],
        "uninstall_cmd": ["pip", "uninstall", "-y", "pyright"],
        "plugin": "pyright-lsp",
        "extensions": [".py", ".pyi"],
        "package_manager": "pip",
    },
    "typescript": {
        "binary": "typescript-language-server",
        "install_cmd": [
            "npm",
            "install",
            "-g",
            "typescript-language-server",
            "typescript",
        ],
        "uninstall_cmd": [
            "npm",
            "uninstall",
            "-g",
            "typescript-language-server",
            "typescript",
        ],
        "plugin": "typescript-lsp",
        "extensions": [".ts", ".tsx", ".js", ".jsx"],
        "package_manager": "npm",
    },
    "go": {
        "binary": "gopls",
        "install_cmd": ["go", "install", "golang.org/x/tools/gopls@latest"],
        # Note: go clean -i doesn't fully uninstall, but we avoid shell expansion issues
        "uninstall_cmd": ["go", "clean", "-i", "golang.org/x/tools/gopls"],
        "plugin": "gopls-lsp",
        "extensions": [".go"],
        "package_manager": "go",
        "uninstall_note": "Manual removal may be needed: rm $(go env GOPATH)/bin/gopls",
    },
    "rust": {
        "binary": "rust-analyzer",
        "install_cmd": ["rustup", "component", "add", "rust-analyzer"],
        "uninstall_cmd": ["rustup", "component", "remove", "rust-analyzer"],
        "plugin": "rust-lsp",
        "extensions": [".rs"],
        "package_manager": "rustup",
    },
    # === JVM languages ===
    "java": {
        "binary": "jdtls",
        "install_cmd_darwin": ["brew", "install", "jdtls"],
        # SDKMAN requires sourcing shell - use brew or manual install instead
        "install_cmd_linux": ["brew", "install", "jdtls"],
        # Windows: use Chocolatey or Scoop - manual install recommended
        "install_cmd_windows": ["choco", "install", "jdtls", "-y"],
        "uninstall_cmd_darwin": ["brew", "uninstall", "jdtls"],
        "uninstall_cmd_linux": ["brew", "uninstall", "jdtls"],
        "uninstall_cmd_windows": ["choco", "uninstall", "jdtls", "-y"],
        "plugin": "jdtls-lsp",
        "extensions": [".java"],
        "package_manager": "brew/choco",
        "note": "Eclipse JDT Language Server. Requires JDK 11+. Windows: install Chocolatey first.",
    },
    "kotlin": {
        "binary": "kotlin-language-server",
        "install_cmd_darwin": ["brew", "install", "kotlin-language-server"],
        "install_cmd": ["npm", "install", "-g", "kotlin-language-server"],
        "uninstall_cmd_darwin": ["brew", "uninstall", "kotlin-language-server"],
        "uninstall_cmd": ["npm", "uninstall", "-g", "kotlin-language-server"],
        "plugin": "kotlin-lsp",
        "extensions": [".kt", ".kts"],
        "package_manager": "brew/npm",
        "note": "Requires JDK 11+.",
    },
    # === Systems languages ===
    "cpp": {
        "binary": "clangd",
        "install_cmd_darwin": ["brew", "install", "llvm"],
        # Linux requires sudo for apt - script will prefix automatically
        "install_cmd_linux": ["apt", "install", "-y", "clangd"],
        # Windows: use Chocolatey for LLVM/clangd
        "install_cmd_windows": ["choco", "install", "llvm", "-y"],
        "uninstall_cmd_darwin": ["brew", "uninstall", "llvm"],
        "uninstall_cmd_linux": ["apt", "remove", "-y", "clangd"],
        "uninstall_cmd_windows": ["choco", "uninstall", "llvm", "-y"],
        "plugin": "clangd-lsp",
        "extensions": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
        "package_manager": "brew/apt/choco",
        "note": "LLVM clangd for C/C++ projects. Linux requires sudo. Windows: install Chocolatey first.",
        "requires_sudo_linux": True,
    },
    "objectivec": {
        "binary": "clangd",
        # Objective-C uses clangd (same as C/C++)
        "install_cmd_darwin": ["brew", "install", "llvm"],
        "install_cmd_linux": ["apt", "install", "-y", "clangd"],
        "install_cmd_windows": ["choco", "install", "llvm", "-y"],
        "uninstall_cmd_darwin": ["brew", "uninstall", "llvm"],
        "uninstall_cmd_linux": ["apt", "remove", "-y", "clangd"],
        "uninstall_cmd_windows": ["choco", "uninstall", "llvm", "-y"],
        "plugin": "clangd-lsp",
        "extensions": [".m", ".mm"],
        "package_manager": "brew/apt/choco",
        "note": "Objective-C uses clangd (same binary as C/C++). macOS recommended.",
        "requires_sudo_linux": True,
        "shared_binary": "clangd",  # Shares binary with cpp
    },
    "swift": {
        "binary": "sourcekit-lsp",
        # sourcekit-lsp is bundled with Xcode/Swift toolchain
        "install_cmd_darwin": ["xcode-select", "--install"],
        # Linux: install Swift toolchain which includes sourcekit-lsp
        "install_cmd_linux": [
            "swift",
            "--version",
        ],  # Check only - manual install required
        "uninstall_cmd_darwin": None,  # Cannot uninstall Xcode tools easily
        "uninstall_cmd_linux": None,
        "plugin": "sourcekit-lsp",
        "extensions": [".swift"],
        "package_manager": "xcode/swift-toolchain",
        "note": "Bundled with Xcode (macOS) or Swift toolchain (Linux). Install Xcode or download Swift from swift.org.",
    },
    "csharp": {
        "binary": "csharp-ls",
        "alt_binary": "OmniSharp",
        "install_cmd": ["dotnet", "tool", "install", "-g", "csharp-ls"],
        "uninstall_cmd": ["dotnet", "tool", "uninstall", "-g", "csharp-ls"],
        "plugin": "omnisharp-lsp",
        "extensions": [".cs", ".csx"],
        "package_manager": "dotnet",
        "note": "Requires .NET SDK 6.0+.",
    },
    # === Web languages ===
    "php": {
        "binary": "intelephense",
        "install_cmd": ["npm", "install", "-g", "intelephense"],
        "uninstall_cmd": ["npm", "uninstall", "-g", "intelephense"],
        "plugin": "intelephense-lsp",
        "extensions": [".php", ".phtml"],
        "package_manager": "npm",
        "note": "Free tier has core LSP functionality.",
    },
    "ruby": {
        "binary": "solargraph",
        "install_cmd": ["gem", "install", "solargraph"],
        "uninstall_cmd": ["gem", "uninstall", "-x", "solargraph"],
        "plugin": "solargraph-lsp",
        "extensions": [".rb", ".rake", ".gemspec"],
        "package_manager": "gem",
        "note": "Requires Ruby 2.7+. Run 'solargraph download-core' after install.",
    },
    "html": {
        "binary": "vscode-html-language-server",
        "install_cmd": ["npm", "install", "-g", "vscode-langservers-extracted"],
        "uninstall_cmd": ["npm", "uninstall", "-g", "vscode-langservers-extracted"],
        "plugin": "html-lsp",
        "extensions": [".html", ".htm", ".xhtml"],
        "package_manager": "npm",
        "note": "Standalone servers (not VS Code dependent).",
        "shared_package": "vscode-langservers-extracted",  # Shared with css
    },
    "css": {
        "binary": "vscode-css-language-server",
        "install_cmd": ["npm", "install", "-g", "vscode-langservers-extracted"],
        "uninstall_cmd": ["npm", "uninstall", "-g", "vscode-langservers-extracted"],
        "plugin": "css-lsp",
        "extensions": [".css", ".scss", ".less"],
        "package_manager": "npm",
        "note": "Standalone servers (not VS Code dependent).",
        "shared_package": "vscode-langservers-extracted",  # Shared with html
    },
}

# Supported languages (all 13 Claude Code LSP languages including Apple platforms)
SUPPORTED_LANGUAGES = [
    "python",
    "typescript",
    "go",
    "rust",  # Core
    "java",
    "kotlin",  # JVM
    "cpp",
    "objectivec",
    "swift",
    "csharp",  # Systems (including Apple platforms)
    "php",
    "ruby",
    "html",
    "css",  # Web
]

# Extension to language mapping for auto-detection
EXTENSION_MAP = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "typescript",
    ".jsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".c": "cpp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".m": "objectivec",
    ".mm": "objectivec",  # Objective-C and Objective-C++
    ".swift": "swift",
    ".cs": "csharp",
    ".csx": "csharp",
    ".php": "php",
    ".phtml": "php",
    ".rb": "ruby",
    ".rake": "ruby",
    ".gemspec": "ruby",
    ".html": "html",
    ".htm": "html",
    ".xhtml": "html",
    ".css": "css",
    ".scss": "css",
    ".less": "css",
}


def get_platform() -> str:
    """Return 'darwin' for macOS, 'linux' for Linux, 'windows' for Windows."""
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    return "linux"


def detect_languages(project_path: Path) -> list[str]:
    """Detect languages used in project by scanning file extensions.

    Returns empty list if project path doesn't exist or isn't accessible.
    """
    if not project_path.exists():
        print(f"[WARNING] Project path does not exist: {project_path}")
        return []

    if not project_path.is_dir():
        print(f"[WARNING] Project path is not a directory: {project_path}")
        return []

    languages = set()
    for ext, lang in EXTENSION_MAP.items():
        # Check if any files with this extension exist
        try:
            if any(project_path.rglob(f"*{ext}")):
                languages.add(lang)
        except (PermissionError, OSError):
            # Handle permission errors and other OS errors (e.g., too many open files)
            continue
    return sorted(languages)


def is_binary_installed(binary: str) -> bool:
    """Check if binary is in PATH using cross-platform shutil.which()."""
    # WHY: shutil.which is the canonical cross-platform way to check for executables in PATH.
    # Unlike subprocess calls to 'which' or 'where', it works on Windows/Mac/Linux uniformly.
    return shutil.which(binary) is not None


def get_installed_languages() -> list[str]:
    """Return list of languages with LSP servers installed."""
    installed = []
    for lang, config in LSP_CONFIGS.items():
        binary = config["binary"]
        alt_binary = config.get("alt_binary")
        if is_binary_installed(binary) or (
            alt_binary and is_binary_installed(alt_binary)
        ):
            installed.append(lang)
    return installed


def get_install_command(config: LSPConfig, plat: str) -> list[str] | None:
    """Get the appropriate install command for the platform."""
    # Try platform-specific first
    platform_key = f"install_cmd_{plat}"
    if platform_key in config:
        result: list[str] = config[platform_key]
        return result
    # Fall back to generic
    if "install_cmd" in config:
        result = config["install_cmd"]
        return result
    return None


def get_uninstall_command(config: LSPConfig, plat: str) -> list[str] | None:
    """Get the appropriate uninstall command for the platform."""
    # Try platform-specific first
    platform_key = f"uninstall_cmd_{plat}"
    if platform_key in config:
        result: list[str] | None = config[platform_key]
        return result
    # Fall back to generic
    if "uninstall_cmd" in config:
        result = config["uninstall_cmd"]
        return result
    return None


def install_language(lang: str, verbose: bool = True) -> bool:
    """Install LSP server for a language."""
    if lang not in LSP_CONFIGS:
        if verbose:
            print(f"[ERROR] Unknown language: {lang}")
        return False

    config = LSP_CONFIGS[lang]
    binary = config["binary"]

    # Check if already installed
    if is_binary_installed(binary):
        if verbose:
            print(f"[OK] {lang}: {binary} already installed")
        return True

    # Get install command
    plat = get_platform()
    cmd = get_install_command(config, plat)

    if not cmd:
        if verbose:
            print(f"[ERROR] {lang}: No install command for {plat}")
        return False

    # Prefix sudo for apt commands on Linux (requires_sudo_linux flag)
    if plat == "linux" and config.get("requires_sudo_linux") and cmd[0] == "apt":
        cmd = ["sudo"] + cmd

    if verbose:
        print(f"[INSTALLING] {lang}: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=not verbose, timeout=300)
        if verbose:
            print(f"[INSTALLED] {lang}: {binary}")
        return True
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"[FAILED] {lang}: Command returned non-zero exit code: {e}")
        return False
    except FileNotFoundError as e:
        if verbose:
            print(f"[FAILED] {lang}: Command not found: {cmd[0]} - {e}")
        return False
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"[FAILED] {lang}: Install command timed out after 300 seconds")
        return False


def uninstall_language(lang: str, verbose: bool = True) -> bool:
    """Uninstall LSP server for a language."""
    if lang not in LSP_CONFIGS:
        if verbose:
            print(f"[ERROR] Unknown language: {lang}")
        return False

    config = LSP_CONFIGS[lang]
    binary = config["binary"]

    # Check if installed
    if not is_binary_installed(binary):
        alt_binary = config.get("alt_binary")
        if not alt_binary or not is_binary_installed(alt_binary):
            if verbose:
                print(f"[OK] {lang}: {binary} not installed (nothing to uninstall)")
            return True

    # Check for shared packages (html/css share vscode-langservers-extracted)
    shared_pkg = config.get("shared_package")
    if shared_pkg:
        # Check if any other language using this package is still needed
        for other_lang, other_config in LSP_CONFIGS.items():
            if other_lang != lang and other_config.get("shared_package") == shared_pkg:
                if is_binary_installed(other_config["binary"]):
                    if verbose:
                        print(
                            f"[SKIP] {lang}: Shared package still needed by {other_lang}"
                        )
                    return True

    # Get uninstall command
    plat = get_platform()
    cmd = get_uninstall_command(config, plat)

    if cmd is None:
        # Check if uninstall is intentionally unavailable (e.g., Swift bundled with Xcode)
        platform_key = f"uninstall_cmd_{plat}"
        if platform_key in config and config[platform_key] is None:
            # Intentionally no uninstall - not an error
            note = config.get("note", "Cannot be uninstalled on this platform.")
            if verbose:
                print(f"[SKIP] {lang}: {note}")
            return True
        # No command available for this platform - actual error
        if verbose:
            print(f"[ERROR] {lang}: No uninstall command for {plat}")
        return False

    # Prefix sudo for apt commands on Linux (requires_sudo_linux flag)
    if plat == "linux" and config.get("requires_sudo_linux") and cmd[0] == "apt":
        cmd = ["sudo"] + cmd

    if verbose:
        print(f"[UNINSTALLING] {lang}: {' '.join(cmd)}")

    # Show uninstall note if present (e.g., for Go manual cleanup)
    uninstall_note = config.get("uninstall_note")
    if uninstall_note and verbose:
        print(f"[NOTE] {lang}: {uninstall_note}")

    try:
        subprocess.run(cmd, check=True, capture_output=not verbose, timeout=120)
        if verbose:
            print(f"[UNINSTALLED] {lang}: {binary}")
        return True
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"[FAILED] {lang}: Command returned non-zero exit code: {e}")
        return False
    except FileNotFoundError as e:
        if verbose:
            print(f"[FAILED] {lang}: Command not found: {cmd[0]} - {e}")
        return False
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"[FAILED] {lang}: Uninstall command timed out after 120 seconds")
        return False


def generate_agent_instructions(project_path: Path) -> str:
    """Generate instructions for remote agent to activate required LSP plugins.

    This generates instructions for LOCAL ACTIVATION only - binaries must
    already be installed globally by the orchestrator.
    """
    detected = detect_languages(project_path)
    global_installed = get_installed_languages()

    instructions = f"""# LSP Activation Instructions for Remote Agent

## IMPORTANT: Global vs Local

- **Global binaries**: Installed system-wide by orchestrator (already done)
- **Local activation**: YOU must activate LSP plugins for your project

The orchestrator has already installed the required binaries globally.
Your job is to ACTIVATE the LSP plugins locally for this project.

## Project Analysis
Project path: {project_path}
Detected languages: {", ".join(detected) if detected else "none"}

## Global Binary Status

"""

    if not detected:
        instructions += "No source files detected. No LSP activation required.\n"
        return instructions

    # Check which binaries are available
    missing_binaries = []
    for lang in detected:
        config = LSP_CONFIGS[lang]
        binary = config["binary"]
        if lang in global_installed:
            instructions += f"- [x] {lang}: `{binary}` available globally\n"
        else:
            instructions += f"- [ ] {lang}: `{binary}` NOT INSTALLED GLOBALLY\n"
            missing_binaries.append(lang)

    if missing_binaries:
        instructions += f"""
## WARNING: Missing Global Binaries

The following binaries are NOT installed globally. Contact orchestrator:
- {", ".join(missing_binaries)}

Orchestrator must run:
```bash
python install_lsp.py --install-binaries --languages {",".join(missing_binaries)}
```
"""

    # Quote path for shell safety (handles spaces in paths)
    quoted_path = f'"{project_path}"' if " " in str(project_path) else str(project_path)

    # Local activation instructions
    instructions += f"""
## Your Task: Local Activation

Run this command to activate LSP plugins for this project:

```bash
python install_lsp.py --project-path {quoted_path} --activate
```

Or to sync (activate needed, deactivate others):

```bash
python install_lsp.py --project-path {quoted_path} --sync
```

## What Happens

1. A local state file is created at `{project_path}/.claude/lsp-state.json`
2. LSP plugins are activated ONLY for the detected languages
3. Other LSP plugins are deactivated to save resources

## Verification

After activation, verify your setup:

```bash
python install_lsp.py --status --project-path {quoted_path}
```

## Quality Checklist

Before starting work:
- [ ] Run `--sync` to activate only needed LSP plugins
- [ ] Verify no LSP errors in source files
- [ ] All type annotations resolve correctly

Before submitting work:
- [ ] All LSP diagnostics resolved
- [ ] Type checking passes for all languages
- [ ] Run `--deactivate-all` when switching to another project
"""

    return instructions


def get_lsp_state_file(project_path: Path | None = None) -> Path:
    """Get the path to the LSP state file for a project.

    State file tracks which LSP plugins are activated locally.
    Located at: <project>/.claude/lsp-state.json
    """
    # WHY: State files are stored in .claude/ subdirectory to follow Claude Code conventions.
    # This ensures LSP activation state persists per-project and is discoverable by other tools.
    if project_path:
        return project_path / ".claude" / "lsp-state.json"
    return Path.cwd() / ".claude" / "lsp-state.json"


def get_activated_languages(project_path: Path | None = None) -> list[str]:
    """Get list of locally activated LSP languages for a project."""
    state_file = get_lsp_state_file(project_path)
    if state_file.exists():
        try:
            with open(state_file, encoding="utf-8") as f:
                state: dict[str, Any] = json.load(f)
                activated: list[str] = state.get("activated", [])
                return activated
        except (json.JSONDecodeError, KeyError, OSError):
            pass
    return []


def save_activated_languages(
    languages: list[str], project_path: Path | None = None
) -> None:
    """Save the list of activated LSP languages for a project."""
    state_file = get_lsp_state_file(project_path)
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "activated": sorted(languages),
                "note": "LSP plugins activated for this project. Managed by install_lsp.py.",
            },
            f,
            indent=2,
        )


def activate_lsp(
    languages: list[str], project_path: Path | None = None, verbose: bool = True
) -> int:
    """Activate LSP plugins for specified languages locally.

    This creates/updates a local state file and outputs instructions for
    enabling the LSP plugins in Claude Code.
    """
    activated = 0
    current = set(get_activated_languages(project_path))
    missing_binaries = []

    for lang in languages:
        if lang not in LSP_CONFIGS:
            if verbose:
                print(f"[ERROR] Unknown language: {lang}")
            continue

        config = LSP_CONFIGS[lang]
        binary = config["binary"]
        alt_binary = config.get("alt_binary")

        # Check if binary is installed globally
        if not is_binary_installed(binary) and not (
            alt_binary and is_binary_installed(alt_binary)
        ):
            missing_binaries.append((lang, binary))
            if verbose:
                print(f"[WARNING] {lang}: Binary '{binary}' not installed globally")
            continue

        if lang in current:
            if verbose:
                print(f"[OK] {lang}: Already activated")
        else:
            current.add(lang)
            activated += 1
            if verbose:
                print(f"[ACTIVATED] {lang}: {config['plugin']}")

    # Save updated state
    save_activated_languages(list(current), project_path)

    if missing_binaries and verbose:
        print("\n[WARNING] Missing global binaries. Ask orchestrator to run:")
        print(
            f"  python install_lsp.py --install-binaries --languages {','.join(lang for lang, _ in missing_binaries)}"
        )

    return activated


def deactivate_lsp(
    languages: list[str], project_path: Path | None = None, verbose: bool = True
) -> int:
    """Deactivate LSP plugins for specified languages locally."""
    deactivated = 0
    current = set(get_activated_languages(project_path))

    for lang in languages:
        if lang not in LSP_CONFIGS:
            if verbose:
                print(f"[ERROR] Unknown language: {lang}")
            continue

        config = LSP_CONFIGS[lang]

        if lang not in current:
            if verbose:
                print(f"[OK] {lang}: Not activated (nothing to deactivate)")
        else:
            current.discard(lang)
            deactivated += 1
            if verbose:
                print(f"[DEACTIVATED] {lang}: {config['plugin']}")

    # Save updated state
    save_activated_languages(list(current), project_path)
    return deactivated


def sync_lsp_activation(
    needed_languages: list[str], project_path: Path | None = None, verbose: bool = True
) -> tuple[int, int]:
    """Sync local LSP activation: activate needed, deactivate unneeded.

    Returns: (activated_count, deactivated_count)
    """
    current = set(get_activated_languages(project_path))
    needed = set(needed_languages)

    to_activate = needed - current
    to_deactivate = current - needed

    if verbose:
        print("\n=== LSP Activation Sync ===")
        print(f"Currently activated: {sorted(current) or 'none'}")
        print(f"Needed for project:  {sorted(needed) or 'none'}")
        print(f"To activate:         {sorted(to_activate) or 'none'}")
        print(f"To deactivate:       {sorted(to_deactivate) or 'none'}")
        print()

    activated = activate_lsp(list(to_activate), project_path, verbose)
    deactivated = deactivate_lsp(list(to_deactivate), project_path, verbose)

    return activated, deactivated


def show_status(project_path: Path | None = None, as_json: bool = False) -> None:
    """Show global binary status and local activation status."""
    global_installed = get_installed_languages()
    local_activated = get_activated_languages(project_path)

    status = {
        "global_binaries_installed": global_installed,
        "local_lsp_activated": local_activated,
        "supported_languages": SUPPORTED_LANGUAGES,
    }

    if as_json:
        print(json.dumps(status, indent=2))
    else:
        print("=== LSP Status ===\n")
        print("Global Binaries (installed system-wide):")
        for lang in SUPPORTED_LANGUAGES:
            installed = lang in global_installed
            marker = "[x]" if installed else "[ ]"
            print(f"  {marker} {lang}")

        print(f"\nLocal Activation (this project: {project_path or Path.cwd()}):")
        for lang in SUPPORTED_LANGUAGES:
            activated = lang in local_activated
            marker = "[x]" if activated else "[ ]"
            print(f"  {marker} {lang}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage LSP servers for remote agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ORCHESTRATOR Commands (global binaries):
  Install binaries:      python install_lsp.py --install-binaries --languages python,typescript
  Install all:           python install_lsp.py --install-binaries --all
  Verify binaries:       python install_lsp.py --verify-binaries
  Uninstall binaries:    python install_lsp.py --uninstall-binaries --languages java,kotlin
  Generate instructions: python install_lsp.py --project-path ./project --generate-instructions

REMOTE AGENT Commands (local activation):
  Activate for project:  python install_lsp.py --project-path ./project --activate
  Activate specific:     python install_lsp.py --activate --languages python,typescript
  Deactivate specific:   python install_lsp.py --deactivate --languages java,kotlin
  Deactivate all:        python install_lsp.py --deactivate-all
  Sync (activate/deact): python install_lsp.py --project-path ./project --sync

Status:
  Show status:           python install_lsp.py --status
  JSON output:           python install_lsp.py --status --json
        """,
    )
    # Common options
    parser.add_argument(
        "--project-path", type=Path, help="Project path (for detection/activation)"
    )
    parser.add_argument("--languages", help="Comma-separated languages")
    parser.add_argument("--all", action="store_true", help="All supported languages")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")

    # Orchestrator commands (global binaries)
    parser.add_argument(
        "--install-binaries", action="store_true", help="Install LSP binaries globally"
    )
    parser.add_argument(
        "--uninstall-binaries",
        action="store_true",
        help="Uninstall LSP binaries globally",
    )
    parser.add_argument(
        "--verify-binaries", action="store_true", help="Verify global binaries"
    )
    parser.add_argument(
        "--generate-instructions",
        action="store_true",
        help="Generate agent instructions",
    )

    # Remote agent commands (local activation)
    parser.add_argument("--activate", action="store_true", help="Activate LSP locally")
    parser.add_argument(
        "--deactivate", action="store_true", help="Deactivate LSP locally"
    )
    parser.add_argument(
        "--deactivate-all", action="store_true", help="Deactivate ALL LSP locally"
    )
    parser.add_argument("--sync", action="store_true", help="Sync local activation")
    parser.add_argument(
        "--status", action="store_true", help="Show global + local status"
    )

    # Legacy compatibility (map to new commands)
    parser.add_argument(
        "--verify-only", action="store_true", help="(Legacy) Same as --verify-binaries"
    )
    parser.add_argument(
        "--list-installed", action="store_true", help="(Legacy) Same as --status"
    )

    args = parser.parse_args()
    verbose = not args.quiet

    # === STATUS COMMANDS ===

    # Show status (new) or list-installed (legacy)
    if args.status or args.list_installed:
        show_status(args.project_path, args.json)
        return 0

    # === ORCHESTRATOR COMMANDS (Global Binaries) ===

    # Generate instructions for remote agent
    if args.generate_instructions:
        if not args.project_path:
            print("Error: --project-path required for --generate-instructions")
            return 1
        instructions = generate_agent_instructions(args.project_path)
        print(instructions)
        return 0

    # Verify global binaries (new) or verify-only (legacy)
    if args.verify_binaries or args.verify_only:
        if args.languages:
            languages = [lang.strip() for lang in args.languages.split(",")]
        elif args.all:
            languages = SUPPORTED_LANGUAGES
        else:
            languages = get_installed_languages()

        success = True
        for lang in languages:
            if lang not in LSP_CONFIGS:
                continue
            config = LSP_CONFIGS[lang]
            binary = config["binary"]
            alt_binary = config.get("alt_binary")
            is_installed = is_binary_installed(binary) or (
                alt_binary and is_binary_installed(alt_binary)
            )
            if is_installed:
                if verbose:
                    print(f"[OK] {lang}: {binary} installed globally")
            else:
                if verbose:
                    print(f"[MISSING] {lang}: {binary} not installed globally")
                success = False
        return 0 if success else 1

    # Install global binaries
    if args.install_binaries:
        if args.all:
            languages = SUPPORTED_LANGUAGES
        elif args.languages:
            languages = [lang.strip() for lang in args.languages.split(",")]
        else:
            print("Error: --install-binaries requires --languages or --all")
            return 1

        if verbose:
            print("Installing LSP binaries globally...")
        success = True
        for lang in languages:
            if not install_language(lang, verbose):
                success = False
        return 0 if success else 1

    # Uninstall global binaries
    if args.uninstall_binaries:
        if args.all:
            languages = SUPPORTED_LANGUAGES
        elif args.languages:
            languages = [lang.strip() for lang in args.languages.split(",")]
        else:
            print("Error: --uninstall-binaries requires --languages or --all")
            return 1

        if verbose:
            print("Uninstalling LSP binaries globally...")
        success = True
        for lang in languages:
            if not uninstall_language(lang, verbose):
                success = False
        return 0 if success else 1

    # === REMOTE AGENT COMMANDS (Local Activation) ===

    # Deactivate all LSP plugins locally
    if args.deactivate_all:
        if verbose:
            print("Deactivating ALL LSP plugins locally...")
        current = get_activated_languages(args.project_path)
        deactivate_lsp(current, args.project_path, verbose)
        return 0

    # Determine target languages
    if args.languages:
        languages = [lang.strip() for lang in args.languages.split(",")]
    elif args.project_path:
        # Validate project path exists before detecting languages
        if not args.project_path.exists():
            print(f"Error: Project path does not exist: {args.project_path}")
            return 1
        if not args.project_path.is_dir():
            print(f"Error: Project path is not a directory: {args.project_path}")
            return 1
        languages = detect_languages(args.project_path)
        if verbose:
            print(f"Detected languages: {languages}")
        if not languages:
            print(f"Warning: No supported languages detected in {args.project_path}")
    elif args.all:
        languages = SUPPORTED_LANGUAGES
    else:
        print("Error: Specify --project-path, --languages, or --all")
        return 1

    # Activate LSP locally
    if args.activate:
        activated = activate_lsp(languages, args.project_path, verbose)
        if verbose:
            print(f"\n=== Summary: {activated} LSP plugins activated ===")
        return 0

    # Deactivate specific LSP locally
    if args.deactivate:
        deactivated = deactivate_lsp(languages, args.project_path, verbose)
        if verbose:
            print(f"\n=== Summary: {deactivated} LSP plugins deactivated ===")
        return 0

    # Sync local activation (activate needed, deactivate others)
    if args.sync:
        activated, deactivated = sync_lsp_activation(
            languages, args.project_path, verbose
        )
        if verbose:
            print("\n=== Summary ===")
            print(f"Activated: {activated} | Deactivated: {deactivated}")
        return 0

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
