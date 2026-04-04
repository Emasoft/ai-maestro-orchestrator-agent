#!/usr/bin/env python3
"""Unified publish pipeline: test → lint → validate → consistency-check → bump → commit → push.

Absorbs all logic from bump_version.py and check_version_consistency.py into a single script.

Usage:
  uv run python scripts/publish.py --patch            # bump patch and publish
  uv run python scripts/publish.py --minor            # bump minor and publish
  uv run python scripts/publish.py --major            # bump major and publish
  uv run python scripts/publish.py --patch --dry-run   # preview only
  uv run python scripts/publish.py --patch --skip-tests # skip pytest

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
NC = "\033[0m" if _USE_COLOR else ""

# Lazy-initialized gitignore filter for file scanning
_gi = None


def _get_gi(plugin_root: Path):  # noqa: ANN202
    """Get or create GitignoreFilter for the plugin root."""
    global _gi  # noqa: PLW0603
    if _gi is None:
        from gitignore_filter import GitignoreFilter
        _gi = GitignoreFilter(plugin_root)
    return _gi


# ── Helpers ──────────────────────────────────────────────────────────────────


def get_plugin_root() -> Path:
    """Resolve plugin root from this script's location (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command, print it, stream output, and fail fast on error."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        # Print stderr but don't double-print if it's just warnings
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        print(f"\n{RED}✗ FAILED (exit {result.returncode}): {' '.join(cmd)}{NC}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


# ── Semver helpers (absorbed from bump_version.py) ───────────────────────────


def parse_semver(version: str) -> tuple[int, int, int] | None:
    """Parse 'X.Y.Z' into (major, minor, patch), or None if invalid."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def semver_gt(a: str, b: str) -> bool:
    """Return True if version a > version b."""
    pa, pb = parse_semver(a), parse_semver(b)
    if pa is None or pb is None:
        return False
    return pa > pb


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


# ── Version read/write (absorbed from bump_version.py) ───────────────────────


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
        return True, f"plugin.json: {old} → {new_version}"
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
        return True, f"pyproject.toml: {old_version} → {new_version}"
    except Exception as e:
        return False, f"pyproject.toml error: {e}"


def update_python_versions(plugin_root: Path, new_version: str) -> list[tuple[bool, str]]:
    """Update __version__ = 'X.Y.Z' in all Python files."""
    gi = _get_gi(plugin_root)
    results: list[tuple[bool, str]] = []
    for py_file in gi.rglob("*.py"):
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
                results.append((True, f"{rel}: {old_v} → {new_version}"))
        except Exception as e:
            rel = py_file.relative_to(plugin_root)
            results.append((False, f"{rel}: {e}"))
    return results


# ── Version consistency check (absorbed from check_version_consistency.py) ───


def check_version_consistency(plugin_root: Path) -> tuple[bool, str]:
    """Check all version sources match. Returns (ok, message)."""
    versions: dict[str, str] = {}  # source_label → version

    # plugin.json
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if pj.exists():
        try:
            v = json.loads(pj.read_text(encoding="utf-8")).get("version")
            if isinstance(v, str):
                versions["plugin.json"] = v
        except Exception:
            pass

    # pyproject.toml
    pp = plugin_root / "pyproject.toml"
    if pp.exists():
        try:
            m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', pp.read_text(encoding="utf-8"), re.MULTILINE)
            if m:
                versions["pyproject.toml"] = m.group(1)
        except Exception:
            pass

    # Python __version__ variables
    gi = _get_gi(plugin_root)
    for py_file in gi.rglob("*.py"):
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

    # Mismatch — build detail
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
        description="Publish pipeline: test → lint → validate → consistency → bump → commit → push",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --patch              # 1.0.0 → 1.0.1, commit, push
  %(prog)s --minor              # 1.0.0 → 1.1.0, commit, push
  %(prog)s --major              # 1.0.0 → 2.0.0, commit, push
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

    root = get_plugin_root()
    bump_type = "major" if args.major else "minor" if args.minor else "patch"

    # ── Step 1: Clean working tree ──
    print(f"\n{BLUE}═══ Step 1: Check working tree ═══{NC}")
    result = run(["git", "status", "--porcelain"], cwd=root, check=False)
    dirty = result.stdout.strip()
    if dirty:
        # Auto-commit uv.lock if it's the only dirty file (uv run modifies it)
        dirty_files = {line.split()[-1] for line in dirty.splitlines() if line.strip()}
        if dirty_files == {"uv.lock"}:
            print(f"{YELLOW}Auto-committing uv.lock (modified by uv run){NC}")
            run(["git", "add", "uv.lock"], cwd=root)
            run(["git", "commit", "-m", "chore: update uv.lock"], cwd=root)
        else:
            print(f"{RED}✗ Uncommitted changes detected. Commit or stash first.{NC}", file=sys.stderr)
            print(dirty)
            return 1
    print(f"{GREEN}✓ Working tree clean{NC}")

    # ── Step 2: Tests ──
    if not args.skip_tests:
        print(f"\n{BLUE}═══ Step 2: Run tests ═══{NC}")
        run(["python3", "-m", "pytest", "tests/", "-x", "-q", "--tb=short"], cwd=root)
        print(f"{GREEN}✓ All tests passed{NC}")
    else:
        print(f"\n{YELLOW}═══ Step 2: Tests skipped (--skip-tests) ═══{NC}")

    # ── Step 3: Lint ──
    print(f"\n{BLUE}═══ Step 3: Lint files ═══{NC}")
    run(["python3", "scripts/lint_files.py", "."], cwd=root)
    print(f"{GREEN}✓ Linting passed{NC}")

    # ── Step 4: Validate ──
    validate_script = root / "scripts" / "validate_plugin.py"
    if validate_script.exists():
        print(f"\n{BLUE}═══ Step 4: Validate plugin (--strict) ═══{NC}")
        run(["python3", "scripts/validate_plugin.py", ".", "--strict"], cwd=root)
        print(f"{GREEN}✓ Plugin validation passed{NC}")
    else:
        print(f"\n{YELLOW}═══ Step 4: Validate plugin — skipped (scripts/validate_plugin.py not found) ═══{NC}")

    # ── Step 5: Version consistency ──
    print(f"\n{BLUE}═══ Step 5: Check version consistency ═══{NC}")
    ok, msg = check_version_consistency(root)
    print(f"  {msg}")
    if not ok:
        print(f"{RED}✗ Fix version mismatches before publishing.{NC}", file=sys.stderr)
        return 1
    print(f"{GREEN}✓ Version consistency OK{NC}")

    # ── Step 6: Bump version ──
    current = get_current_version(root)
    if current is None:
        print(f"{RED}✗ Cannot read current version from plugin.json{NC}", file=sys.stderr)
        return 1

    new_version = bump_semver(current, bump_type)
    if new_version is None:
        print(f"{RED}✗ Current version '{current}' is not valid semver{NC}", file=sys.stderr)
        return 1

    print(f"\n{BLUE}═══ Step 6: Bump version ({bump_type}: {current} → {new_version}) ═══{NC}")
    if not do_bump(root, new_version, dry_run=args.dry_run):
        print(f"{RED}✗ Version bump failed{NC}", file=sys.stderr)
        return 1
    print(f"{GREEN}✓ Version bumped to {new_version}{NC}")

    if args.dry_run:
        print(f"\n{GREEN}✓ Dry run complete — no changes made.{NC}")
        return 0

    # ── Step 7: Commit ──
    print(f"\n{BLUE}═══ Step 7: Commit version bump ═══{NC}")
    run(["git", "add", "-A"], cwd=root)
    run(["git", "commit", "-m", f"chore: bump version to {new_version}"], cwd=root)
    print(f"{GREEN}✓ Committed v{new_version}{NC}")

    # ── Step 8: Push ──
    print(f"\n{BLUE}═══ Step 8: Push to origin ═══{NC}")
    os.environ["CPV_PUBLISH_PIPELINE"] = "1"
    run(["git", "push", "origin", "HEAD"], cwd=root)
    print(f"\n{GREEN}✓ Published v{new_version}{NC}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
