#!/usr/bin/env python3
"""Real-subprocess tests for amoa_init_design_folders.py.

This script scaffolds a project's `design/` folder. Per the settled fleet
conventions it must create the 3-pillars layout:

* the 4-zone TRDD structure — `tasks/`, `proposals/`, `refused/`, `archived/`
  (each with a `.gitkeep` so the empty zone survives git on a fresh tree), and
* `requirements/` (the PRRD), plus the `handoffs/` + `config/` working folders.

It must NOT create a tracked `design/memory/` bank: memory lives in
LOCAL/PROJECT/USER scopes (ratified fleet memory convention), not under
`design/`. The retired `design/archive/` folder is superseded by `archived/`
and must not be created either.

No mocks: the actual script is invoked as a real subprocess writing into a
`tmp_path`-rooted `--root`, and every assertion is made against the real
filesystem state the subprocess leaves behind.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "amoa_init_design_folders.py"
)

# The 4 TRDD zones the 3-pillars convention requires under design/.
TRDD_ZONES = ("tasks", "proposals", "refused", "archived")


def run_init(root: Path, *extra_args: str):
    """Invoke amoa_init_design_folders.py as a real subprocess.

    Returns (exit_code, parsed_stdout_json, raw_stdout, raw_stderr).
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json", *extra_args],
        capture_output=True,
        text=True,
        check=False,
    )
    parsed = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, parsed, proc.stdout, proc.stderr


def test_creates_four_trdd_zones_each_with_gitkeep(tmp_path: Path) -> None:
    """init creates tasks/proposals/refused/archived, each with a .gitkeep."""
    root = tmp_path / "design"
    code, parsed, _, stderr = run_init(root)

    assert code == 0, stderr
    assert parsed is not None and parsed["success"] is True

    for zone in TRDD_ZONES:
        zone_dir = root / zone
        assert zone_dir.is_dir(), f"missing TRDD zone: {zone}"
        assert (zone_dir / ".gitkeep").is_file(), f"missing .gitkeep in {zone}"


def test_creates_requirements_and_working_folders(tmp_path: Path) -> None:
    """init keeps requirements/ (PRRD) plus the handoffs/ and config/ folders."""
    root = tmp_path / "design"
    code, parsed, _, stderr = run_init(root)

    assert code == 0, stderr
    assert (root / "requirements").is_dir()
    assert (root / "handoffs").is_dir()
    assert (root / "config").is_dir()
    # requirements still gets the shared-platform template subtree.
    assert (root / "requirements" / "shared" / "templates").is_dir()


def test_does_not_create_memory_bank(tmp_path: Path) -> None:
    """init must NOT scaffold a tracked design/memory/ bank (memory is LOCAL)."""
    root = tmp_path / "design"
    code, parsed, _, stderr = run_init(root)

    assert code == 0, stderr
    assert not (root / "memory").exists(), "design/memory/ must not be created"
    # No 'memory' key should appear anywhere in the reported created paths.
    all_paths = parsed["folders_created"] + parsed["templates_created"]
    assert not any("/memory" in p for p in all_paths), all_paths


def test_does_not_create_retired_archive_folder(tmp_path: Path) -> None:
    """The retired design/archive/ is superseded by archived/ and not created."""
    root = tmp_path / "design"
    code, _, _, stderr = run_init(root)

    assert code == 0, stderr
    assert not (root / "archive").exists(), "retired design/archive/ must not exist"
    assert (root / "archived").is_dir(), "design/archived/ must exist instead"


def test_index_yaml_written_without_memory_type(tmp_path: Path) -> None:
    """The index.yaml is written and its document type-map excludes memory."""
    import yaml

    root = tmp_path / "design"
    code, parsed, _, stderr = run_init(root)

    assert code == 0, stderr
    assert parsed["index_created"] is True

    index_file = root / "index.yaml"
    assert index_file.is_file()
    index = yaml.safe_load(index_file.read_text(encoding="utf-8"))
    assert "memory" not in index["documents"]
    assert "memory" not in index["stats"]["by_type"]
    assert "requirements" in index["documents"]
    assert "handoffs" in index["documents"]
