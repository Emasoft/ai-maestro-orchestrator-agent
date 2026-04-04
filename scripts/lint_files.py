#!/usr/bin/env python3
"""Lint all source files in a repository — read-only, no auto-fix.

Single source of truth for all file linting across 15 language categories.
Called by the pre-push hook and CI workflows. Never modifies files.

Usage:
    python scripts/lint_files.py [repo_root]
    uv run python scripts/lint_files.py [repo_root]

Exit codes:
    0 - All linting passed (or linters not available — WARNING only)
    1 - Linting issues found

Supported languages:
    python, javascript, shell, go, rust, markdown, json, yaml,
    dockerfile, xml, css, html, sql, toml, powershell
"""

from __future__ import annotations

import argparse
import io
import json
import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from gitignore_filter import GitignoreFilter

# ---------------------------------------------------------------------------
# Terminal colors — respects NO_COLOR (https://no-color.org/) and non-TTY output
# ---------------------------------------------------------------------------


def _colors_supported() -> bool:
    """Return True only when the terminal supports ANSI escape sequences."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.name == "nt":  # type: ignore[unreachable]
        return bool(os.environ.get("WT_SESSION") or os.environ.get("ANSICON"))
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_USE_COLOR = _colors_supported()

RED = "\033[0;31m" if _USE_COLOR else ""
GREEN = "\033[0;32m" if _USE_COLOR else ""
YELLOW = "\033[1;33m" if _USE_COLOR else ""
BLUE = "\033[0;34m" if _USE_COLOR else ""
BOLD = "\033[1m" if _USE_COLOR else ""
NC = "\033[0m" if _USE_COLOR else ""

# ---------------------------------------------------------------------------
# Tool resolution via smart_exec TOOL_DB
# ---------------------------------------------------------------------------


def _resolve_tool(tool_name: str) -> list[str] | None:
    """Resolve a linting tool via smart_exec's TOOL_DB and executor chain.

    Tries: direct install -> uvx/pipx (Python) -> bunx/npx (Node) -> docker.

    Returns:
        Command prefix list or None if no executor is available.
    """
    # Add scripts dir to sys.path so we can import cpv_validation_common
    scripts_dir = str(Path(__file__).parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        from cpv_validation_common import resolve_tool_command
    except (ImportError, ModuleNotFoundError):
        return None  # Fall back to shutil.which() in callers
    return resolve_tool_command(tool_name)


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------


def detect_languages(repo_root: Path) -> dict[str, list[Path]]:
    """Detect which programming languages are present in the repo.

    Uses GitignoreFilter to respect .gitignore patterns instead of hardcoded exclude dirs.

    Returns:
        Dictionary mapping language name to list of files.
    """
    gi = GitignoreFilter(repo_root)

    languages: dict[str, list[Path]] = {}

    # Python
    py_files = list(gi.rglob("*.py"))
    if py_files:
        languages["python"] = py_files

    # JavaScript/TypeScript
    all_js: list[Path] = []
    for ext in ("*.js", "*.ts", "*.jsx", "*.tsx"):
        all_js.extend(gi.rglob(ext))
    if all_js:
        languages["javascript"] = all_js

    # Shell/Bash
    all_shell = list(gi.rglob("*.sh")) + list(gi.rglob("*.bash"))
    if all_shell:
        languages["shell"] = all_shell

    # Go
    go_files = list(gi.rglob("*.go"))
    if go_files:
        languages["go"] = go_files

    # Rust
    rs_files = list(gi.rglob("*.rs"))
    if rs_files:
        languages["rust"] = rs_files

    # Markdown
    all_md = list(gi.rglob("*.md")) + list(gi.rglob("*.mdx"))
    if all_md:
        languages["markdown"] = all_md

    # JSON
    json_files = list(gi.rglob("*.json"))
    if json_files:
        languages["json"] = json_files

    # YAML
    all_yaml = list(gi.rglob("*.yml")) + list(gi.rglob("*.yaml"))
    if all_yaml:
        languages["yaml"] = all_yaml

    # Dockerfile
    dockerfile_files = list(gi.rglob("Dockerfile")) + list(gi.rglob("Dockerfile.*")) + list(gi.rglob("*.dockerfile"))
    if dockerfile_files:
        languages["dockerfile"] = dockerfile_files

    # XML
    all_xml: list[Path] = []
    for ext in ("*.xml", "*.xhtml", "*.xsd", "*.xsl"):
        all_xml.extend(gi.rglob(ext))
    if all_xml:
        languages["xml"] = all_xml

    # CSS/SCSS/Less
    all_css: list[Path] = []
    for ext in ("*.css", "*.scss", "*.less"):
        all_css.extend(gi.rglob(ext))
    if all_css:
        languages["css"] = all_css

    # HTML
    all_html = list(gi.rglob("*.html")) + list(gi.rglob("*.htm"))
    if all_html:
        languages["html"] = all_html

    # SQL
    sql_files = list(gi.rglob("*.sql"))
    if sql_files:
        languages["sql"] = sql_files

    # TOML
    toml_files = list(gi.rglob("*.toml"))
    if toml_files:
        languages["toml"] = toml_files

    # PowerShell
    all_ps: list[Path] = []
    for ext in ("*.ps1", "*.psm1", "*.psd1"):
        all_ps.extend(gi.rglob(ext))
    if all_ps:
        languages["powershell"] = all_ps

    return languages


# ---------------------------------------------------------------------------
# Python tool installation (for auto-installing ruff, mypy, yamllint, etc.)
# ---------------------------------------------------------------------------


def install_python_tool(tool: str) -> bool:
    """Try to install a Python CLI tool via uv/pipx/pip.

    Returns:
        True if installation succeeded, False otherwise.
    """
    last_error = ""

    # uv tool install (preferred)
    if shutil.which("uv"):
        try:
            result = subprocess.run(
                ["uv", "tool", "install", "--python", "3.12", tool], capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                print(f"{GREEN}  ✔ {tool} installed via uv tool (Python 3.12){NC}")
                return True
            if "already installed" in result.stderr.lower():
                print(f"{GREEN}  ✔ {tool} already installed via uv tool{NC}")
                return True
            last_error = result.stderr.strip() or result.stdout.strip()
        except subprocess.TimeoutExpired:
            last_error = "uv tool timed out after 120s"
        except OSError as e:
            last_error = str(e)

    # pipx (fallback)
    if shutil.which("pipx"):
        try:
            result = subprocess.run(["pipx", "install", tool], capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"{GREEN}  ✔ {tool} installed via pipx{NC}")
                return True
            if "already installed" in result.stderr.lower() or "already installed" in result.stdout.lower():
                print(f"{GREEN}  ✔ {tool} already installed via pipx{NC}")
                return True
            last_error = result.stderr.strip() or result.stdout.strip()
        except subprocess.TimeoutExpired:
            last_error = "pipx timed out after 120s"
        except OSError as e:
            last_error = str(e)

    # pip install --user (last resort)
    for pip_cmd in ["pip3", "pip"]:
        if shutil.which(pip_cmd):
            try:
                result = subprocess.run(
                    [pip_cmd, "install", "--user", tool], capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    print(f"{GREEN}  ✔ {tool} installed via {pip_cmd} --user{NC}")
                    return True
                last_error = result.stderr.strip() or result.stdout.strip()
            except subprocess.TimeoutExpired:
                last_error = f"{pip_cmd} timed out after 120s"
            except OSError as e:
                last_error = str(e)

    if last_error:
        print(f"{RED}  Install error: {last_error[:200]}{NC}")
    return False


# ---------------------------------------------------------------------------
# Linter availability check (with cross-platform install hints)
# ---------------------------------------------------------------------------


def ensure_linter_installed(language: str, repo_root: Path) -> bool:
    """Ensure the linter for a language is installed. Auto-install if possible.

    Returns:
        True if linter is available, False if cannot be installed.
    """
    os_type = platform.system().lower()

    if language == "python":
        if not shutil.which("ruff"):
            print(f"{YELLOW}  Installing ruff...{NC}")
            if not install_python_tool("ruff"):
                print(f"{RED}  ✘ Could not install ruff{NC}")
                return False
        # mypy is optional
        if not shutil.which("mypy"):
            print(f"{YELLOW}  Installing mypy...{NC}")
            if not install_python_tool("mypy"):
                print(f"{YELLOW}  ⚠ Could not install mypy, type checking will be skipped{NC}")
        return True

    elif language == "javascript":
        local_eslint = repo_root / "node_modules" / ".bin" / "eslint"
        if local_eslint.exists() or shutil.which("eslint"):
            return True
        package_json = repo_root / "package.json"
        if package_json.exists():
            print(f"{YELLOW}  Installing eslint...{NC}")
            for pkg_mgr in ["bun", "npm", "pnpm"]:
                if shutil.which(pkg_mgr):
                    result = subprocess.run(
                        [pkg_mgr, "install", "eslint", "--save-dev"],
                        cwd=repo_root,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if result.returncode == 0:
                        print(f"{GREEN}  ✔ eslint installed via {pkg_mgr}{NC}")
                        return True
        print(f"{YELLOW}  ⚠ eslint not available, skipping JS/TS linting{NC}")
        return False

    elif language == "shell":
        if shutil.which("shellcheck"):
            return True
        print(f"{YELLOW}  Installing shellcheck...{NC}")
        pkg_managers: list[tuple[str, list[str]]] = []
        if os_type == "darwin":
            pkg_managers = [
                ("brew", ["brew", "install", "shellcheck"]),
                ("port", ["sudo", "port", "install", "shellcheck"]),
            ]
        elif os_type == "linux":
            pkg_managers = [
                ("apt-get", ["sudo", "apt-get", "install", "-y", "shellcheck"]),
                ("dnf", ["sudo", "dnf", "install", "-y", "ShellCheck"]),
                ("pacman", ["sudo", "pacman", "-S", "--noconfirm", "shellcheck"]),
                ("apk", ["sudo", "apk", "add", "shellcheck"]),
                ("brew", ["brew", "install", "shellcheck"]),
            ]
        elif os_type == "windows":
            pkg_managers = [
                ("scoop", ["scoop", "install", "shellcheck"]),
                ("choco", ["choco", "install", "shellcheck", "-y"]),
                ("winget", ["winget", "install", "--id", "koalaman.shellcheck", "-e"]),
            ]

        last_error = ""
        for pkg_mgr, cmd in pkg_managers:
            if shutil.which(pkg_mgr):
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                    if result.returncode == 0:
                        print(f"{GREEN}  ✔ shellcheck installed via {pkg_mgr}{NC}")
                        return True
                    last_error = f"{pkg_mgr}: {result.stderr.strip() or result.stdout.strip()}"
                except subprocess.TimeoutExpired:
                    last_error = f"{pkg_mgr}: timed out"
                except OSError as e:
                    last_error = f"{pkg_mgr}: {e}"

        install_hint = {
            "darwin": "brew install shellcheck",
            "linux": "apt install shellcheck  # or dnf/pacman/zypper",
            "windows": "scoop install shellcheck  # or choco/winget",
        }.get(os_type, "see https://github.com/koalaman/shellcheck#installing")
        if last_error:
            print(f"{YELLOW}  Last error: {last_error[:150]}{NC}")
        print(f"{YELLOW}  ⚠ shellcheck not installed (install via: {install_hint}){NC}")
        return False

    elif language == "go":
        if shutil.which("gofmt"):
            return True
        install_hint = {
            "darwin": "brew install go  # or download from go.dev/dl",
            "linux": "apt install golang  # or dnf/pacman, or download from go.dev/dl",
            "windows": "scoop install go  # or choco install golang, or download from go.dev/dl",
        }.get(os_type, "https://go.dev/dl/")
        print(f"{YELLOW}  ⚠ Go tools not installed (install via: {install_hint}){NC}")
        return False

    elif language == "rust":
        if shutil.which("cargo"):
            has_rustup = shutil.which("rustup") is not None
            if not shutil.which("rustfmt") and has_rustup:
                print(f"{YELLOW}  Installing rustfmt via rustup...{NC}")
                try:
                    subprocess.run(
                        ["rustup", "component", "add", "rustfmt"], capture_output=True, text=True, timeout=120
                    )
                except (subprocess.TimeoutExpired, OSError):
                    print(f"{YELLOW}  ⚠ rustfmt install failed{NC}")
            if not shutil.which("cargo-clippy") and has_rustup:
                print(f"{YELLOW}  Installing clippy via rustup...{NC}")
                try:
                    subprocess.run(
                        ["rustup", "component", "add", "clippy"], capture_output=True, text=True, timeout=120
                    )
                except (subprocess.TimeoutExpired, OSError):
                    print(f"{YELLOW}  ⚠ clippy install failed{NC}")
            return True
        install_hint = {
            "darwin": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "linux": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "windows": "Download rustup-init.exe from https://rustup.rs/",
        }.get(os_type, "https://rustup.rs/")
        print(f"{YELLOW}  ⚠ Rust/Cargo not installed (install via: {install_hint}){NC}")
        return False

    elif language == "markdown":
        if shutil.which("bun") or shutil.which("npx"):
            return True  # Will use bun x or npx at runtime
        if shutil.which("markdownlint"):
            return True
        print(f"{YELLOW}  Installing markdownlint-cli...{NC}")
        for pkg_mgr, cmd in [
            ("bun", ["bun", "add", "-g", "markdownlint-cli"]),
            ("npm", ["npm", "install", "-g", "markdownlint-cli"]),
        ]:
            if shutil.which(pkg_mgr):
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        print(f"{GREEN}  ✔ markdownlint-cli installed via {pkg_mgr}{NC}")
                        return True
                except (subprocess.TimeoutExpired, OSError):
                    pass
        print(f"{YELLOW}  ⚠ markdownlint not available (install via: npm install -g markdownlint-cli){NC}")
        return False

    elif language == "json":
        # JSON validation uses built-in Python json module — always available
        return True

    elif language == "yaml":
        if shutil.which("yamllint"):
            return True
        print(f"{YELLOW}  Installing yamllint...{NC}")
        if not install_python_tool("yamllint"):
            print(f"{YELLOW}  ⚠ Install via: uv tool install --python 3.12 yamllint  OR  pipx install yamllint{NC}")
            return False
        return True

    elif language == "dockerfile":
        if _resolve_tool("hadolint") is not None:
            return True
        hint = {
            "darwin": "brew install hadolint",
            "linux": "apt install hadolint  # or download from github.com/hadolint/hadolint",
            "windows": "scoop install hadolint  # or choco install hadolint",
        }.get(os_type, "https://github.com/hadolint/hadolint#install")
        print(f"{YELLOW}  ⚠ hadolint not found (install via: {hint}){NC}")
        return False

    elif language == "xml":
        if _resolve_tool("xmllint") is not None:
            return True
        hint = {
            "darwin": "brew install libxml2  # or xcode-select --install (ships with macOS CLT)",
            "linux": "apt install libxml2-utils  # or dnf install libxml2",
            "windows": "choco install libxml2  # or download from xmlsoft.org",
        }.get(os_type, "https://xmlsoft.org/downloads.html")
        print(f"{YELLOW}  ⚠ xmllint not found (install via: {hint}){NC}")
        return False

    elif language == "css":
        if _resolve_tool("stylelint") is not None:
            return True
        print(f"{YELLOW}  ⚠ stylelint not found (install via: npm install -g stylelint){NC}")
        return False

    elif language == "html":
        if _resolve_tool("htmlhint") is not None:
            return True
        print(f"{YELLOW}  ⚠ htmlhint not found (install via: npm install -g htmlhint){NC}")
        return False

    elif language == "sql":
        if _resolve_tool("sqlfluff") is not None:
            return True
        print(f"{YELLOW}  ⚠ sqlfluff not found (install via: uv tool install sqlfluff  OR  pipx install sqlfluff){NC}")
        return False

    elif language == "toml":
        # tomllib is stdlib in Python 3.11+; tomli is pip fallback for 3.10
        try:
            import tomllib  # noqa: F401  # type: ignore[reportUnusedImport]

            return True
        except ModuleNotFoundError:
            try:
                import tomli  # type: ignore[import-untyped,import-not-found]  # noqa: F401

                return True
            except ModuleNotFoundError:
                print(f"{YELLOW}  ⚠ TOML parser not found (need Python 3.11+ or: pip install tomli){NC}")
                return False

    elif language == "powershell":
        if _resolve_tool("PSScriptAnalyzer") is not None:
            return True
        if os_type == "windows":
            hint = "Install-Module -Name PSScriptAnalyzer -Scope CurrentUser"
        else:
            hint = (
                "brew install powershell/tap/powershell && pwsh -c 'Install-Module PSScriptAnalyzer -Scope CurrentUser'"
            )
        print(f"{YELLOW}  ⚠ PSScriptAnalyzer not found (install via: {hint}){NC}")
        return False

    return False


# ---------------------------------------------------------------------------
# 15 lint functions — ALL read-only, return bool (True = passed)
# ---------------------------------------------------------------------------


def lint_python(repo_root: Path, files: list[Path] | None = None) -> bool:  # noqa: ARG001
    """Lint Python files with ruff check + mypy (read-only, no --fix).

    Steps: 1) ruff check (no --fix), 2) mypy type-check
    Files are discovered internally via ruff/mypy; the files param is unused but
    kept for uniform dispatch signature.
    """
    # ruff check (read-only, no --fix)
    print(f"{BLUE}    [1/2] ruff check...{NC}")
    try:
        result = subprocess.run(
            ["ruff", "check", "--select=E,F,W", "--ignore=E501", str(repo_root)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"{RED}    Lint issues found{NC}")
            for line in (result.stdout or "").strip().splitlines()[:10]:
                if line.strip():
                    print(f"      {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    ruff check timed out{NC}")
        return False
    except FileNotFoundError:
        print(f"{RED}    ruff not found{NC}")
        return False

    # mypy type-check (optional, read-only)
    if shutil.which("mypy"):
        print(f"{BLUE}    [2/2] mypy...{NC}")
        try:
            result = subprocess.run(
                ["mypy", "--ignore-missing-imports", str(repo_root)], capture_output=True, text=True, timeout=180
            )
            if result.returncode != 0:
                print(f"{RED}    Type errors found:{NC}")
                for line in result.stdout.strip().splitlines()[:10]:
                    print(f"      {line}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}    mypy timed out, skipping{NC}")
    else:
        print(f"{YELLOW}    [2/2] mypy not installed, skipping typecheck{NC}")

    return True


def lint_javascript(repo_root: Path, files: list[Path] | None = None) -> bool:  # noqa: ARG001
    """Lint JavaScript/TypeScript files with eslint (read-only, no --fix).

    Files are discovered internally via eslint; the files param is unused but
    kept for uniform dispatch signature.
    """
    # Find eslint
    local_eslint = repo_root / "node_modules" / ".bin" / "eslint"
    if shutil.which("bun"):
        eslint_cmd = ["bun", "x", "eslint"]
    elif shutil.which("npx"):
        eslint_cmd = ["npx", "eslint"]
    elif local_eslint.exists():
        eslint_cmd = [str(local_eslint)]
    elif shutil.which("eslint"):
        eslint_cmd = ["eslint"]
    else:
        print(f"{YELLOW}    eslint not available, skipping{NC}")
        return True

    # Check if eslint config exists
    config_files = [
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.json",
        ".eslintrc.yml",
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
        "eslint.config.ts",
    ]
    has_config = any((repo_root / cfg).exists() for cfg in config_files)
    if not has_config:
        print(f"{YELLOW}    No eslint config found, skipping{NC}")
        return True

    # Read-only check (no --fix)
    print(f"{BLUE}    eslint...{NC}")
    try:
        result = subprocess.run(eslint_cmd + ["."], cwd=repo_root, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    eslint timed out{NC}")
        return True
    except FileNotFoundError:
        return True


def lint_shell(repo_root: Path, files: list[Path]) -> bool:  # noqa: ARG001
    """Lint shell scripts with shellcheck (read-only)."""
    print(f"{BLUE}    shellcheck...{NC}")
    all_passed = True
    for f in files:
        try:
            result = subprocess.run(["shellcheck", "-x", str(f)], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                all_passed = False
                print(f"{YELLOW}      {f.name}: issues found{NC}")
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}      {f.name}: shellcheck timed out{NC}")
        except FileNotFoundError:
            print(f"{YELLOW}    shellcheck not found{NC}")
            return True
    return all_passed


def lint_go(repo_root: Path, files: list[Path] | None = None) -> bool:  # noqa: ARG001
    """Lint Go files with gofmt -l (list mode) + go vet (read-only)."""
    # gofmt -l: list files whose formatting differs (read-only, no -w)
    print(f"{BLUE}    gofmt -l (check formatting)...{NC}")
    try:
        result = subprocess.run(["gofmt", "-l", "."], cwd=repo_root, capture_output=True, text=True, timeout=120)
        if result.stdout.strip():
            # Files need formatting
            print(f"{RED}    Files need formatting:{NC}")
            for line in result.stdout.strip().splitlines()[:5]:
                print(f"      {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    gofmt timed out{NC}")
    except FileNotFoundError:
        print(f"{RED}    gofmt not found{NC}")
        return False

    # go vet (read-only)
    print(f"{BLUE}    go vet...{NC}")
    try:
        result = subprocess.run(["go", "vet", "./..."], cwd=repo_root, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    go vet timed out{NC}")
        return True
    except FileNotFoundError:
        return True


def lint_rust(repo_root: Path, files: list[Path] | None = None) -> bool:  # noqa: ARG001
    """Lint Rust files with cargo fmt --check + cargo clippy (read-only)."""
    if not (repo_root / "Cargo.toml").exists():
        return True

    # cargo fmt --check (read-only: exits non-zero if changes needed)
    print(f"{BLUE}    cargo fmt --check...{NC}")
    try:
        result = subprocess.run(["cargo", "fmt", "--check"], cwd=repo_root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"{RED}    Formatting issues found (run 'cargo fmt' to fix){NC}")
            return False
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    cargo fmt --check timed out{NC}")
    except FileNotFoundError:
        print(f"{RED}    cargo not found{NC}")
        return False

    # cargo clippy (read-only, no --fix)
    print(f"{BLUE}    cargo clippy...{NC}")
    try:
        result = subprocess.run(["cargo", "clippy"], cwd=repo_root, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    cargo clippy timed out{NC}")
        return True
    except FileNotFoundError:
        return True


def lint_markdown(repo_root: Path, files: list[Path]) -> bool:
    """Lint Markdown files with markdownlint (read-only, no --fix)."""
    if not files:
        return True

    if shutil.which("bun"):
        lint_cmd = ["bun", "x", "markdownlint-cli"]
    elif shutil.which("npx"):
        lint_cmd = ["npx", "markdownlint-cli"]
    elif shutil.which("markdownlint"):
        lint_cmd = ["markdownlint"]
    else:
        print(f"{YELLOW}    markdownlint not available, skipping{NC}")
        return True

    file_paths = [str(f) for f in files]

    # Read-only check (no --fix)
    print(f"{BLUE}    markdownlint...{NC}")
    try:
        result = subprocess.run(lint_cmd + file_paths, cwd=repo_root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            output = (result.stdout or result.stderr or "").strip()
            if output:
                lines = output.splitlines()[:5]
                for line in lines:
                    print(f"{YELLOW}    {line}{NC}")
                if len(output.splitlines()) > 5:
                    print(f"{YELLOW}    ... and more{NC}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    markdownlint timed out{NC}")
        return True
    except FileNotFoundError:
        return True


def lint_json(repo_root: Path, files: list[Path]) -> bool:  # noqa: ARG001
    """Validate JSON syntax with Python json module (read-only)."""
    if not files:
        return True

    print(f"{BLUE}    json.load() validation...{NC}")
    invalid_files: list[tuple[Path, str]] = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fp:
                json.load(fp)
        except json.JSONDecodeError as e:
            invalid_files.append((f, str(e)))
        except UnicodeDecodeError as e:
            invalid_files.append((f, f"Binary/encoding error: {e}"))
        except OSError as e:
            invalid_files.append((f, f"I/O error: {e}"))

    if invalid_files:
        for fpath, err in invalid_files[:5]:
            print(f"{RED}    {fpath.name}: {err[:80]}{NC}")
        if len(invalid_files) > 5:
            print(f"{RED}    ... and {len(invalid_files) - 5} more{NC}")
        return False

    return True


def lint_yaml(repo_root: Path, files: list[Path]) -> bool:
    """Lint YAML files with yamllint (read-only)."""
    if not files:
        return True

    if not shutil.which("yamllint"):
        print(f"{YELLOW}    yamllint not available, skipping{NC}")
        return True

    file_paths = [str(f) for f in files]

    print(f"{BLUE}    yamllint...{NC}")
    try:
        result = subprocess.run(
            ["yamllint", "-d", "relaxed", "--format", "parsable"] + file_paths,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            lines = result.stdout.strip().splitlines()[:5] if result.stdout else []
            for line in lines:
                if "[error]" in line:
                    print(f"{RED}    {line}{NC}")
                else:
                    print(f"{YELLOW}    {line}{NC}")
            total_lines = len(result.stdout.strip().splitlines()) if result.stdout else 0
            if total_lines > 5:
                print(f"{YELLOW}    ... and {total_lines - 5} more{NC}")
            # Only fail on errors, not warnings
            if "[error]" in (result.stdout or ""):
                return False
        return True
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    yamllint timed out{NC}")
        return True
    except FileNotFoundError:
        print(f"{YELLOW}    yamllint not found{NC}")
        return True


def lint_dockerfile(repo_root: Path, files: list[Path]) -> bool:  # noqa: ARG001
    """Lint Dockerfiles with hadolint (read-only)."""
    cmd = _resolve_tool("hadolint")
    if not cmd:
        print(f"{YELLOW}    ⚠ hadolint not available, cannot lint Dockerfiles{NC}")
        return True

    all_passed = True
    print(f"{BLUE}    hadolint...{NC}")
    for f in files:
        try:
            result = subprocess.run(cmd + [str(f)], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                all_passed = False
                print(f"{YELLOW}      {f.name}: issues found{NC}")
                for line in (result.stdout or result.stderr or "").strip().splitlines()[:3]:
                    if line.strip():
                        print(f"        {line}")
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}      {f.name}: hadolint timed out{NC}")
        except OSError as e:
            print(f"{YELLOW}    hadolint execution error: {e}{NC}")
            return True
    return all_passed


def lint_xml(repo_root: Path, files: list[Path]) -> bool:  # noqa: ARG001
    """Lint XML files with xmllint --noout (read-only)."""
    cmd = _resolve_tool("xmllint")
    if not cmd:
        print(f"{YELLOW}    ⚠ xmllint not available, cannot lint XML files{NC}")
        return True

    all_passed = True
    print(f"{BLUE}    xmllint --noout...{NC}")
    for f in files:
        try:
            result = subprocess.run(cmd + ["--noout", str(f)], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                all_passed = False
                print(f"{YELLOW}      {f.name}: XML validation failed{NC}")
                for line in (result.stderr or "").strip().splitlines()[:3]:
                    if line.strip():
                        print(f"        {line}")
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}      {f.name}: xmllint timed out{NC}")
        except OSError as e:
            print(f"{YELLOW}    xmllint execution error: {e}{NC}")
            return True
    return all_passed


def lint_css(repo_root: Path, files: list[Path]) -> bool:
    """Lint CSS/SCSS/Less files with stylelint (read-only, no --fix)."""
    cmd = _resolve_tool("stylelint")
    if not cmd:
        print(f"{YELLOW}    ⚠ stylelint not available, cannot lint CSS/SCSS files{NC}")
        return True

    file_paths = [str(f) for f in files]

    print(f"{BLUE}    stylelint...{NC}")
    try:
        result = subprocess.run(cmd + file_paths, cwd=repo_root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 and result.stdout:
            for line in result.stdout.strip().splitlines()[:5]:
                print(f"{YELLOW}    {line}{NC}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    stylelint timed out{NC}")
        return True
    except OSError as e:
        print(f"{YELLOW}    stylelint execution error: {e}{NC}")
        return True


def lint_html(repo_root: Path, files: list[Path]) -> bool:
    """Lint HTML files with htmlhint (read-only)."""
    cmd = _resolve_tool("htmlhint")
    if not cmd:
        print(f"{YELLOW}    ⚠ htmlhint not available, cannot lint HTML files{NC}")
        return True

    file_paths = [str(f) for f in files]

    print(f"{BLUE}    htmlhint...{NC}")
    try:
        result = subprocess.run(cmd + file_paths, cwd=repo_root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 and result.stdout:
            for line in result.stdout.strip().splitlines()[:5]:
                print(f"{YELLOW}    {line}{NC}")
            total = len(result.stdout.strip().splitlines())
            if total > 5:
                print(f"{YELLOW}    ... and {total - 5} more{NC}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    htmlhint timed out{NC}")
        return True
    except OSError as e:
        print(f"{YELLOW}    htmlhint execution error: {e}{NC}")
        return True


def lint_sql(repo_root: Path, files: list[Path]) -> bool:
    """Lint SQL files with sqlfluff lint (read-only, no fix)."""
    cmd = _resolve_tool("sqlfluff")
    if not cmd:
        print(f"{YELLOW}    ⚠ sqlfluff not available, cannot lint SQL files{NC}")
        return True

    file_paths = [str(f) for f in files]

    print(f"{BLUE}    sqlfluff lint...{NC}")
    try:
        result = subprocess.run(
            cmd + ["lint", "--dialect", "ansi"] + file_paths, cwd=repo_root, capture_output=True, text=True, timeout=180
        )
        if result.returncode != 0 and result.stdout:
            for line in result.stdout.strip().splitlines()[:5]:
                print(f"{YELLOW}    {line}{NC}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}    sqlfluff lint timed out{NC}")
        return True
    except OSError as e:
        print(f"{YELLOW}    sqlfluff execution error: {e}{NC}")
        return True


def lint_toml(repo_root: Path, files: list[Path]) -> bool:  # noqa: ARG001
    """Validate TOML files using Python's tomllib (read-only)."""
    # tomllib is stdlib in Python 3.11+; fall back to tomli for 3.10
    try:
        import tomllib
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ModuleNotFoundError:
            print(
                f"{YELLOW}    ⚠ No TOML parser available (need Python 3.11+ or 'pip install tomli'), cannot lint TOML files{NC}"
            )
            return True

    print(f"{BLUE}    TOML syntax validation...{NC}")
    invalid_files: list[tuple[Path, str]] = []
    for f in files:
        try:
            with open(f, "rb") as fp:
                tomllib.load(fp)
        except tomllib.TOMLDecodeError as e:
            invalid_files.append((f, str(e)))
        except OSError as e:
            invalid_files.append((f, f"I/O error: {e}"))

    if invalid_files:
        for fpath, err in invalid_files[:5]:
            print(f"{RED}    {fpath.name}: {err[:80]}{NC}")
        if len(invalid_files) > 5:
            print(f"{RED}    ... and {len(invalid_files) - 5} more{NC}")
        return False

    return True


def lint_powershell(repo_root: Path, files: list[Path]) -> bool:  # noqa: ARG001
    """Lint PowerShell scripts with PSScriptAnalyzer (read-only)."""
    cmd = _resolve_tool("PSScriptAnalyzer")
    if not cmd:
        print(f"{YELLOW}    ⚠ PSScriptAnalyzer not available, cannot lint PowerShell files{NC}")
        return True

    all_passed = True
    print(f"{BLUE}    PSScriptAnalyzer...{NC}")
    for f in files:
        try:
            result = subprocess.run(cmd + ["-Path", str(f)], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                all_passed = False
                print(f"{YELLOW}      {f.name}: issues found{NC}")
                for line in (result.stdout or result.stderr or "").strip().splitlines()[:3]:
                    if line.strip():
                        print(f"        {line}")
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}      {f.name}: PSScriptAnalyzer timed out{NC}")
        except OSError as e:
            print(f"{YELLOW}    PSScriptAnalyzer execution error: {e}{NC}")
            return True
    return all_passed


# ---------------------------------------------------------------------------
# Orchestration — dispatch table + WARNING for missing linters
# ---------------------------------------------------------------------------


def get_repo_root() -> Path:
    """Get repository root via git."""
    try:
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError):
        pass
    return Path.cwd()


def run_linting(repo_root: Path) -> bool:
    """Detect languages and run appropriate linters (read-only).

    Returns:
        True if all linting passed, False if any linting issues found.
    """
    all_passed = True

    languages = detect_languages(repo_root)

    if not languages:
        print(f"{YELLOW}  No source files found to lint{NC}")
        return True

    print(f"{BLUE}  Detected languages: {', '.join(languages.keys())}{NC}")

    # Language -> lint function dispatch table (all read-only, return bool)
    _LINT_DISPATCH: dict[str, Callable[..., bool]] = {
        "python": lint_python,
        "javascript": lint_javascript,
        "shell": lint_shell,
        "go": lint_go,
        "rust": lint_rust,
        "markdown": lint_markdown,
        "json": lint_json,
        "yaml": lint_yaml,
        "dockerfile": lint_dockerfile,
        "xml": lint_xml,
        "css": lint_css,
        "html": lint_html,
        "sql": lint_sql,
        "toml": lint_toml,
        "powershell": lint_powershell,
    }

    for lang, files in languages.items():
        print(f"{BLUE}  [{lang.upper()}] ({len(files)} files){NC}")

        # Ensure linter is installed — emit WARNING if unavailable
        if not ensure_linter_installed(lang, repo_root):
            print(
                f"{YELLOW}  ⚠ WARNING: {len(files)} {lang.upper()} file(s) cannot be validated — no linter available for this format{NC}"
            )
            continue

        # Dispatch to language-specific linter
        lint_fn = _LINT_DISPATCH.get(lang)
        if lint_fn is None:
            print(
                f"{YELLOW}  ⚠ WARNING: {len(files)} {lang.upper()} file(s) cannot be validated — no lint function registered{NC}"
            )
            continue

        passed = lint_fn(repo_root, files)
        if not passed:
            all_passed = False

    return all_passed


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Lint all files in a repository (read-only). Returns 0 if pass, 1 if fail."""
    parser = argparse.ArgumentParser(
        description="Read-only file linting for plugin repositories.",
        epilog=(
            "Supports 15 languages: Python, JavaScript, Shell, Go, Rust, "
            "Markdown, JSON, YAML, Dockerfile, XML, CSS, HTML, SQL, TOML, PowerShell. "
            "All checks are read-only — no files are modified."
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=None,
        help="Repository root path (default: auto-detected via git)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for each linter",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        metavar="PATH",
        help="Save full output to file, print only compact summary to stdout",
    )
    args = parser.parse_args()

    repo_root = args.path.resolve() if args.path else get_repo_root()

    if not repo_root.is_dir():
        print(f"{RED}Error: {repo_root} is not a directory{NC}", file=sys.stderr)
        return 1

    # When --report is used, capture all output to file and print only a summary
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        # Capture all stdout to a StringIO buffer
        captured = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured
        try:
            print(f"{'=' * 60}")
            print("File Linting (read-only, no auto-fix)")
            print(f"{'=' * 60}")
            print()
            passed = run_linting(repo_root)
            print()
            if passed:
                print("All linting checks passed")
            else:
                print("Linting issues found")
        finally:
            sys.stdout = original_stdout
        # Write captured output to report file (strip ANSI codes for readability)
        import re

        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        report_content = ansi_escape.sub("", captured.getvalue())
        report_path.write_text(report_content, encoding="utf-8")
        # Print compact summary to real stdout
        verdict = "PASS" if passed else "FAIL"
        print(f"Lint: {verdict}")
        print(f"  Report: {report_path}")
        return 0 if passed else 1

    print(f"{BOLD}{'=' * 60}{NC}")
    print(f"{BOLD}File Linting (read-only, no auto-fix){NC}")
    print(f"{BOLD}{'=' * 60}{NC}")
    print()

    passed = run_linting(repo_root)

    print()
    if passed:
        print(f"{GREEN}✔ All linting checks passed{NC}")
    else:
        print(f"{RED}✘ Linting issues found{NC}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
