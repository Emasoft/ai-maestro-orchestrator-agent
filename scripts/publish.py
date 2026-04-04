#!/usr/bin/env python3
"""Smart publish pipeline: auto-detect → test → lint → validate → consistency → bump → commit → push.

Auto-detects plugin name, version, marketplace, git root, and plugin root.
Handles subfolder plugins where git root != plugin root.

Usage:
  uv run python scripts/publish.py --patch            # bump patch and publish
  uv run python scripts/publish.py --minor            # bump minor and publish
  uv run python scripts/publish.py --major            # bump major and publish
  uv run python scripts/publish.py --patch --dry-run   # preview only
  uv run python scripts/publish.py --patch --skip-tests # skip pytest step

Exit codes:
    0 - Success
    1 - Any step failed (fail-fast)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ── ANSI colors ──────────────────────────────────────────────────────────────

_USE_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
RED = "\033[0;31m" if _USE_COLOR else ""
GREEN = "\033[0;32m" if _USE_COLOR else ""
YELLOW = "\033[1;33m" if _USE_COLOR else ""
BLUE = "\033[0;34m" if _USE_COLOR else ""
BOLD = "\033[1m" if _USE_COLOR else ""
NC = "\033[0m" if _USE_COLOR else ""

# Lazy-initialized gitignore filter for file scanning
_gi = None


def _get_gi(root: Path):  # noqa: ANN202
    """Get or create GitignoreFilter for the given root."""
    global _gi  # noqa: PLW0603
    if _gi is None:
        try:
            from gitignore_filter import GitignoreFilter
            _gi = GitignoreFilter(root)
        except ImportError:
            # Fallback: return a simple walker that skips common dirs
            return None
    return _gi


# ── Auto-detection ───────────────────────────────────────────────────────────


def detect_git_root() -> Path:
    """Find the git repository root (handles subfolder plugins)."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"{RED}✗ Not inside a git repository{NC}", file=sys.stderr)
        sys.exit(1)
    return Path(result.stdout.strip())


def detect_plugin_root() -> Path:
    """Find the plugin root by walking up from this script to find .claude-plugin/plugin.json."""
    script_dir = Path(__file__).resolve().parent  # scripts/
    candidates = [script_dir.parent] + list(script_dir.parent.parents)
    for candidate in candidates:
        if (candidate / ".claude-plugin" / "plugin.json").exists():
            return candidate
        # Stop at filesystem root
        if candidate == candidate.parent:
            break
    # Fallback: assume parent of scripts/
    return script_dir.parent


def detect_plugin_info(plugin_root: Path) -> dict:
    """Read plugin metadata from .claude-plugin/plugin.json."""
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        return {"name": "unknown", "version": "0.0.0"}
    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        return {
            "name": data.get("name", "unknown"),
            "version": data.get("version", "0.0.0"),
            "description": data.get("description", ""),
            "author": data.get("author", {}).get("name", "") if isinstance(data.get("author"), dict) else data.get("author", ""),
            "repository": data.get("repository", ""),
        }
    except Exception:
        return {"name": "unknown", "version": "0.0.0"}


def detect_marketplace(git_root: Path) -> dict:
    """Auto-detect marketplace info from git remote and plugin structure."""
    info: dict = {"org": "", "repo": "", "url": "", "marketplace_name": ""}

    # Parse git remote URL
    result = subprocess.run(
        ["git", "-C", str(git_root), "remote", "get-url", "origin"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        url = result.stdout.strip()
        info["url"] = url
        # Parse org/repo from SSH or HTTPS URL
        m = re.search(r"[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
        if m:
            info["org"] = m.group(1)
            info["repo"] = m.group(2)

    # Detect marketplace name from marketplace.json if this IS a marketplace
    mkt_json = git_root / ".claude-plugin" / "marketplace.json"
    if mkt_json.exists():
        try:
            mkt = json.loads(mkt_json.read_text(encoding="utf-8"))
            info["marketplace_name"] = mkt.get("name", "")
        except Exception:
            pass

    # If no marketplace.json, derive from org name
    if not info["marketplace_name"] and info["org"]:
        info["marketplace_name"] = f"{info['org']}-plugins"

    return info


def detect_cpv_scripts() -> Path | None:
    """Find the latest CPV (claude-plugins-validation) scripts directory.

    Searches the Claude plugin cache for the latest installed version.
    Returns the scripts/ directory path, or None if CPV is not installed.
    """
    home = Path.home()
    cache_base = home / ".claude" / "plugins" / "cache"

    # Search known marketplace locations for CPV
    for marketplace in ("emasoft-plugins", "ai-maestro-plugins", "buildwithclaude"):
        cpv_dir = cache_base / marketplace / "claude-plugins-validation"
        if cpv_dir.exists():
            # Find latest version by semver sort
            versions = []
            for d in cpv_dir.iterdir():
                if d.is_dir() and (d / "scripts" / "validate_plugin.py").exists():
                    versions.append(d)
            if versions:
                # Sort by version number (lexicographic works for semver dirs)
                latest = sorted(versions, key=lambda p: p.name)[-1]
                return latest / "scripts"

    return None


def detect_default_branch(git_root: Path) -> str:
    """Detect the default branch (main or master)."""
    result = subprocess.run(
        ["git", "-C", str(git_root), "symbolic-ref", "refs/remotes/origin/HEAD"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        # refs/remotes/origin/main -> main
        return result.stdout.strip().split("/")[-1]
    # Fallback: check if main exists
    result = subprocess.run(
        ["git", "-C", str(git_root), "rev-parse", "--verify", "origin/main"],
        capture_output=True, text=True, timeout=10,
    )
    return "main" if result.returncode == 0 else "master"


# ── Helpers ──────────────────────────────────────────────────────────────────


def run(cmd: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command, print it, stream output, and fail fast on error."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        print(f"\n{RED}✗ FAILED (exit {result.returncode}): {' '.join(cmd)}{NC}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


# ── Semver helpers ───────────────────────────────────────────────────────────


def parse_semver(version: str) -> tuple[int, int, int] | None:
    """Parse 'X.Y.Z' into (major, minor, patch), or None if invalid."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def bump_semver(current: str, bump_type: str) -> str | None:
    """Bump version by type ('major', 'minor', 'patch'). Returns new version or None."""
    parts = parse_semver(current)
    if parts is None:
        return None
    major, minor, patch = parts
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return None


# ── Version read/write ───────────────────────────────────────────────────────


def get_current_version(plugin_root: Path) -> str | None:
    """Read current version from .claude-plugin/plugin.json."""
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        return None
    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        v = data.get("version")
        return v if isinstance(v, str) else None
    except Exception:
        return None


def update_plugin_json(plugin_root: Path, new_version: str) -> tuple[bool, str]:
    """Update version field in plugin.json."""
    path = plugin_root / ".claude-plugin" / "plugin.json"
    if not path.exists():
        return False, "plugin.json not found"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        old = data.get("version", "unknown")
        data["version"] = new_version
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return True, f"plugin.json: {old} -> {new_version}"
    except Exception as e:
        return False, f"plugin.json error: {e}"


def update_pyproject_toml(plugin_root: Path, new_version: str) -> tuple[bool, str]:
    """Update version field in pyproject.toml."""
    path = plugin_root / "pyproject.toml"
    if not path.exists():
        return True, "pyproject.toml not found (skipped)"
    try:
        content = path.read_text(encoding="utf-8")
        pattern = r'^(version\s*=\s*["\'])(\d+\.\d+\.\d+)(["\'])$'
        old_version = None

        def _replace(m: re.Match[str]) -> str:
            nonlocal old_version
            old_version = m.group(2)
            return f"{m.group(1)}{new_version}{m.group(3)}"

        new_content, count = re.subn(pattern, _replace, content, flags=re.MULTILINE)
        if count == 0:
            return True, "pyproject.toml has no version field (skipped)"
        path.write_text(new_content, encoding="utf-8")
        return True, f"pyproject.toml: {old_version} -> {new_version}"
    except Exception as e:
        return False, f"pyproject.toml error: {e}"


def update_python_versions(plugin_root: Path, new_version: str) -> list[tuple[bool, str]]:
    """Update __version__ = 'X.Y.Z' in all Python files."""
    gi = _get_gi(plugin_root)
    results: list[tuple[bool, str]] = []

    # Use gitignore filter if available, else walk manually
    if gi is not None:
        py_files = list(gi.rglob("*.py"))
    else:
        py_files = [
            p for p in plugin_root.rglob("*.py")
            if not any(part.startswith(".") or part in ("node_modules", "__pycache__", "dist", "build", ".git")
                       for part in p.relative_to(plugin_root).parts)
        ]

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            pattern = r'^(__version__\s*=\s*["\'])(\d+\.\d+\.\d+)(["\'])$'
            old_v = None

            def _replace(m: re.Match[str]) -> str:
                nonlocal old_v
                old_v = m.group(2)
                return f"{m.group(1)}{new_version}{m.group(3)}"

            new_content, count = re.subn(pattern, _replace, content, flags=re.MULTILINE)
            if count > 0:
                py_file.write_text(new_content, encoding="utf-8")
                rel = py_file.relative_to(plugin_root)
                results.append((True, f"{rel}: {old_v} -> {new_version}"))
        except Exception as e:
            rel = py_file.relative_to(plugin_root)
            results.append((False, f"{rel}: {e}"))
    return results


# ── Version consistency check ────────────────────────────────────────────────


def check_version_consistency(plugin_root: Path) -> tuple[bool, str]:
    """Check all version sources match. Returns (ok, message)."""
    versions: dict[str, str] = {}

    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if pj.exists():
        try:
            v = json.loads(pj.read_text(encoding="utf-8")).get("version")
            if isinstance(v, str):
                versions["plugin.json"] = v
        except Exception:
            pass

    pp = plugin_root / "pyproject.toml"
    if pp.exists():
        try:
            m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', pp.read_text(encoding="utf-8"), re.MULTILINE)
            if m:
                versions["pyproject.toml"] = m.group(1)
        except Exception:
            pass

    gi = _get_gi(plugin_root)
    py_files = list(gi.rglob("*.py")) if gi else [
        p for p in plugin_root.rglob("*.py")
        if not any(part.startswith(".") or part in ("node_modules", "__pycache__", "dist", "build", ".git")
                   for part in p.relative_to(plugin_root).parts)
    ]
    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if m:
                rel = str(py_file.relative_to(plugin_root))
                versions[rel] = m.group(1)
        except Exception:
            pass

    if not versions:
        return True, "No version sources found"

    unique = set(versions.values())
    if len(unique) == 1:
        return True, f"All {len(versions)} sources consistent: {next(iter(unique))}"

    lines = ["Version mismatch detected:"]
    for src, ver in sorted(versions.items()):
        lines.append(f"  {src}: {ver}")
    return False, "\n".join(lines)


# ── Bump all files ───────────────────────────────────────────────────────────


def do_bump(plugin_root: Path, new_version: str, dry_run: bool = False) -> bool:
    """Bump version across all files. Returns True on success."""
    if dry_run:
        print(f"  [DRY-RUN] Would bump to {new_version}")
        return True

    all_results: list[tuple[bool, str]] = []
    all_results.append(update_plugin_json(plugin_root, new_version))
    all_results.append(update_pyproject_toml(plugin_root, new_version))
    all_results.extend(update_python_versions(plugin_root, new_version))

    errors = 0
    for ok, msg in all_results:
        status = f"{GREEN}[OK]{NC}" if ok else f"{RED}[ERROR]{NC}"
        print(f"  {status} {msg}")
        if not ok:
            errors += 1

    return errors == 0


# ── Main pipeline ────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smart publish pipeline: auto-detect -> test -> lint -> validate -> bump -> commit -> push",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --patch              # 1.0.0 -> 1.0.1, commit, push
  %(prog)s --minor              # 1.0.0 -> 1.1.0, commit, push
  %(prog)s --major              # 1.0.0 -> 2.0.0, commit, push
  %(prog)s --patch --dry-run    # preview only, no changes
  %(prog)s --patch --skip-tests # skip pytest step
        """,
    )
    bump_group = parser.add_mutually_exclusive_group(required=True)
    bump_group.add_argument("--major", action="store_true", help="Bump major version")
    bump_group.add_argument("--minor", action="store_true", help="Bump minor version")
    bump_group.add_argument("--patch", action="store_true", help="Bump patch version")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest step")
    args = parser.parse_args()

    bump_type = "major" if args.major else "minor" if args.minor else "patch"

    # ── Step 0: Auto-detect everything ──
    print(f"\n{BLUE}{BOLD}=== Smart Publish Pipeline ==={NC}")
    git_root = detect_git_root()
    plugin_root = detect_plugin_root()
    plugin_info = detect_plugin_info(plugin_root)
    marketplace = detect_marketplace(git_root)
    default_branch = detect_default_branch(git_root)
    is_subfolder = git_root != plugin_root

    print(f"  Plugin name:    {BOLD}{plugin_info['name']}{NC}")
    print(f"  Plugin version: {plugin_info['version']}")
    print(f"  Git root:       {git_root}")
    if is_subfolder:
        print(f"  Plugin root:    {plugin_root} {YELLOW}(subfolder plugin){NC}")
    else:
        print(f"  Plugin root:    {plugin_root}")
    print(f"  Remote:         {marketplace['url']}")
    print(f"  Org/Repo:       {marketplace['org']}/{marketplace['repo']}")
    print(f"  Default branch: {default_branch}")
    print()

    # ── Step 1: Clean working tree ──
    print(f"\n{BLUE}=== Step 1: Check working tree ==={NC}")
    result = run(["git", "status", "--porcelain"], cwd=git_root, check=False)
    dirty = result.stdout.strip()
    if dirty:
        dirty_files = {line.split()[-1] for line in dirty.splitlines() if line.strip()}
        if dirty_files == {"uv.lock"}:
            print(f"{YELLOW}Auto-committing uv.lock (modified by uv run){NC}")
            run(["git", "add", "uv.lock"], cwd=git_root)
            run(["git", "commit", "-m", "chore: update uv.lock"], cwd=git_root)
        else:
            print(f"{RED}x Uncommitted changes detected. Commit or stash first.{NC}", file=sys.stderr)
            print(dirty)
            return 1
    print(f"{GREEN}ok Working tree clean{NC}")

    # ── Step 2: Tests ──
    if not args.skip_tests:
        tests_dir = plugin_root / "tests"
        if tests_dir.exists() and any(tests_dir.rglob("test_*.py")):
            print(f"\n{BLUE}=== Step 2: Run tests ==={NC}")
            run(["python3", "-m", "pytest", "tests/", "-x", "-q", "--tb=short"], cwd=plugin_root)
            print(f"{GREEN}ok All tests passed{NC}")
        else:
            print(f"\n{YELLOW}=== Step 2: Tests skipped (no tests/ directory or test files) ==={NC}")
    else:
        print(f"\n{YELLOW}=== Step 2: Tests skipped (--skip-tests) ==={NC}")

    # ── Step 3: Lint (prefers local lint_files.py, falls back to CPV's copy) ──
    local_lint = plugin_root / "scripts" / "lint_files.py"
    cpv_scripts_for_lint = detect_cpv_scripts()
    cpv_lint = cpv_scripts_for_lint / "lint_files.py" if cpv_scripts_for_lint else None
    lint_script = local_lint if local_lint.exists() else cpv_lint
    if lint_script and lint_script.exists():
        print(f"\n{BLUE}=== Step 3: Lint files ==={NC}")
        run(["python3", str(lint_script), str(plugin_root)], cwd=plugin_root)
        print(f"{GREEN}ok Linting passed{NC}")
    else:
        print(f"\n{YELLOW}=== Step 3: Lint skipped (no lint_files.py found locally or in CPV) ==={NC}")

    # ── Step 4: Validate plugin via CPV (remote — uses installed CPV, not local copy) ──
    cpv_scripts = detect_cpv_scripts()
    if cpv_scripts:
        cpv_validate = cpv_scripts / "validate_plugin.py"
        print(f"\n{BLUE}=== Step 4: CPV Validate plugin (--strict) ==={NC}")
        print(f"  Using CPV from: {cpv_scripts.parent.name}")
        run(["python3", str(cpv_validate), str(plugin_root), "--strict"], cwd=cpv_scripts)
        print(f"{GREEN}ok CPV validation passed{NC}")
    else:
        print(f"\n{RED}=== Step 4: FAILED — CPV (claude-plugins-validation) not installed ==={NC}")
        print(f"  Install it: claude plugin install claude-plugins-validation emasoft-plugins --scope user")
        return 1

    # ── Step 5: Version consistency ──
    print(f"\n{BLUE}=== Step 5: Check version consistency ==={NC}")
    ok, msg = check_version_consistency(plugin_root)
    print(f"  {msg}")
    if not ok:
        print(f"{RED}x Fix version mismatches before publishing.{NC}", file=sys.stderr)
        return 1
    print(f"{GREEN}ok Version consistency OK{NC}")

    # ── Step 6: Bump version ──
    current = get_current_version(plugin_root)
    if current is None:
        print(f"{RED}x Cannot read current version from plugin.json{NC}", file=sys.stderr)
        return 1

    new_version = bump_semver(current, bump_type)
    if new_version is None:
        print(f"{RED}x Current version '{current}' is not valid semver{NC}", file=sys.stderr)
        return 1

    print(f"\n{BLUE}=== Step 6: Bump version ({bump_type}: {current} -> {new_version}) ==={NC}")
    if not do_bump(plugin_root, new_version, dry_run=args.dry_run):
        print(f"{RED}x Version bump failed{NC}", file=sys.stderr)
        return 1
    print(f"{GREEN}ok Version bumped to {new_version}{NC}")

    if args.dry_run:
        print(f"\n{GREEN}ok Dry run complete -- no changes made.{NC}")
        return 0

    # ── Step 7: Commit ──
    print(f"\n{BLUE}=== Step 7: Commit version bump ==={NC}")
    run(["git", "add", "-A"], cwd=git_root)
    run(["git", "commit", "-m", f"chore: bump version to {new_version}"], cwd=git_root)
    print(f"{GREEN}ok Committed v{new_version}{NC}")

    # ── Step 8: Push ──
    print(f"\n{BLUE}=== Step 8: Push to origin/{default_branch} ==={NC}")
    os.environ["CPV_PUBLISH_PIPELINE"] = "1"
    run(["git", "push", "origin", "HEAD"], cwd=git_root)
    print(f"\n{GREEN}ok Published v{new_version} ({plugin_info['name']}){NC}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
