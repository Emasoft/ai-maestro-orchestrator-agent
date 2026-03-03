#!/usr/bin/env python3
"""sync_cpv_validators.py — Fetch latest validation scripts from CPV repo.

Downloads the 20 validation-chain files from Emasoft/claude-plugins-validation
into this plugin's scripts/ directory. Requires gh CLI and network access.
Fail-safe: exits 0 even on errors so it never blocks a push.
"""

from __future__ import annotations

import base64
import shutil
import stat
import subprocess
from pathlib import Path

REPO = "Emasoft/claude-plugins-validation"
REF = "master"

# The 20 files that form the validation chain
FILES = [
    "cpv_validation_common.py",
    "gitignore_filter.py",
    "smart_exec.py",
    "validate_plugin.py",
    "validate_agent.py",
    "validate_command.py",
    "validate_documentation.py",
    "validate_encoding.py",
    "validate_enterprise.py",
    "validate_hook.py",
    "validate_lsp.py",
    "validate_marketplace_pipeline.py",
    "validate_marketplace.py",
    "validate_mcp.py",
    "validate_rules.py",
    "validate_scoring.py",
    "validate_security.py",
    "validate_skill_comprehensive.py",
    "validate_skill.py",
    "validate_xref.py",
]


def main() -> int:
    script_dir = Path(__file__).resolve().parent

    # Check prerequisites
    if not shutil.which("gh"):
        print("Warning: gh CLI not found. Skipping CPV sync.")
        return 0

    synced = 0
    failed = 0

    for file in FILES:
        # Fetch file content via GitHub API (base64 encoded)
        api_path = f"repos/{REPO}/contents/scripts/{file}?ref={REF}"
        try:
            result = subprocess.run(
                ["gh", "api", api_path, "--jq", ".content"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            content = result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            print(f"Warning: Could not fetch {file}")
            failed += 1
            continue

        if not content or content == "null":
            print(f"Warning: Could not fetch {file}")
            failed += 1
            continue

        # Decode base64 — GitHub API returns base64 with embedded newlines
        try:
            decoded = base64.b64decode(content).decode("utf-8")
        except Exception:
            print(f"Warning: Failed to decode {file}")
            failed += 1
            continue

        # Write to scripts/ and make executable
        dest = script_dir / file
        dest.write_text(decoded)
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        synced += 1

    print(f"CPV sync complete: {synced} synced, {failed} failed (of {len(FILES)} total)")

    # Clean up old validation_common.py if cpv_validation_common.py exists
    old = script_dir / "validation_common.py"
    new = script_dir / "cpv_validation_common.py"
    if new.is_file() and old.is_file():
        old.unlink()
        print("Removed old validation_common.py (replaced by cpv_validation_common.py)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
