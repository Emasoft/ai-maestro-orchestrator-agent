#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""SessionStart hook: install plugin-shipped rules into the active scope.

Plugin-shipped rule files under `<plugin_root>/rules/*.md` are NOT picked up
automatically by Claude Code — the rule loader only reads
`~/.claude/rules/*.md` (user scope) and `<project>/.claude/rules/*.md`
(project/local scope). This hook copies the plugin's rules into whichever
scope's rules directory matches where the plugin is installed, so the rules
become active on the next session start.

Adapted from ai-maestro-janitor's `scripts/lib/rules_installer.py` (the
reference implementation named in issue #12); same size-based idempotency:

  * destination exists with the SAME byte size  -> skip (up to date)
  * destination exists with a DIFFERENT size    -> overwrite (rule update)
  * no rules/ dir, no installed scope, any I/O error -> silent no-op

This hook must NEVER block a session: every failure path exits 0.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

PLUGIN_NAME = "ai-maestro-orchestrator-agent"


def _detect_install_scopes() -> list[str]:
    """Return every scope whose settings.json references this plugin."""
    scopes: list[str] = []
    user_settings = Path.home() / ".claude" / "settings.json"
    if user_settings.is_file():
        try:
            if PLUGIN_NAME in user_settings.read_text(encoding="utf-8"):
                scopes.append("user")
        except OSError:
            pass
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if project_dir:
        for scope, rel in (
            ("local", ".claude/settings.local.json"),
            ("project", ".claude/settings.json"),
        ):
            f = Path(project_dir) / rel
            if f.is_file():
                try:
                    if PLUGIN_NAME in f.read_text(encoding="utf-8"):
                        scopes.append(scope)
                except OSError:
                    pass
    return scopes


def _target_rules_dir(scope: str) -> Path | None:
    """Map an install scope to its .claude/rules/ directory."""
    if scope == "user":
        return Path.home() / ".claude" / "rules"
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if project_dir and scope in ("local", "project"):
        return Path(project_dir) / ".claude" / "rules"
    return None


def install_rules(plugin_root: Path) -> list[str]:
    """Copy <plugin_root>/rules/*.md into every active scope's rules dir."""
    src_dir = plugin_root / "rules"
    if not src_dir.is_dir():
        return []
    rule_files = sorted(
        p for p in src_dir.iterdir() if p.is_file() and p.suffix == ".md"
    )
    if not rule_files:
        return []
    scopes = _detect_install_scopes()
    if not scopes:
        return []

    # local + project both resolve to <project>/.claude/rules/ — dedupe by path.
    targets: dict[str, Path] = {}
    for scope in scopes:
        td = _target_rules_dir(scope)
        if td is not None:
            targets[str(td)] = td

    copied: list[str] = []
    for td in targets.values():
        try:
            td.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue
        for src in rule_files:
            dst = td / src.name
            if dst.exists():
                try:
                    if dst.stat().st_size == src.stat().st_size:
                        continue
                except OSError:
                    continue
            try:
                # Atomic publish: temp file in the SAME dir + os.replace, so
                # concurrent session-starts never expose a half-written rule.
                fd, tmp_name = tempfile.mkstemp(dir=str(td), suffix=".tmp")
                with os.fdopen(fd, "wb") as fh:
                    fh.write(src.read_bytes())
                os.replace(tmp_name, dst)
                copied.append(str(dst))
            except OSError:
                continue
    return copied


def main() -> int:
    # Consume (and ignore) the hook's stdin JSON payload — required so the
    # harness never blocks on an unread pipe.
    try:
        sys.stdin.read()
    except OSError:
        pass

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    if not plugin_root:
        return 0
    try:
        copied = install_rules(Path(plugin_root))
    except Exception:  # noqa: BLE001 — a hook must never crash the session
        return 0
    if copied:
        print(
            json.dumps(
                {
                    "systemMessage": (
                        f"[{PLUGIN_NAME}] installed/updated rule(s): "
                        + ", ".join(Path(c).name for c in copied)
                    )
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
