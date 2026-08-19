#!/usr/bin/env python3
"""The TRDD write gate (TRDD-8DH44UXH F2): trddgrep validate before any column write.

The property these pin is the exit trichotomy: 0 clean -> write, 1 findings ->
write only if none name THIS card, 2/missing-binary/timeout COULD NOT RUN ->
refuse with a DISTINCT reason. No mocks: the gate is exercised against the real
trddgrep binary and this repo's real corpus; the could-not-run branches are
produced by real conditions (empty PATH, empty corpus dir).
"""

import os
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for _d in (_ROOT / "scripts", _ROOT / "shared"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

# I001 suppressed: CPV's remote ruff runs default isort (no first-party
# knowledge for amoa_kanban_manager) and disagrees with the project config on
# this block's order; the path-hack above forces late imports either way.
import pytest  # noqa: E402, I001

from amoa_kanban_manager import _trdd_validate_gate  # noqa: E402

_HAVE_TRDDGREP = shutil.which("trddgrep") is not None


def test_missing_binary_is_could_not_run_not_clean(tmp_path, monkeypatch):
    """No trddgrep on PATH is the exit-2 class: refuse, never treat as clean."""
    monkeypatch.setitem(os.environ, "PATH", str(tmp_path / "empty-bin"))
    ok, reason = _trdd_validate_gate("AAAAAAAA", _ROOT)
    assert not ok
    assert "COULD NOT RUN" in reason


@pytest.mark.skipif(not _HAVE_TRDDGREP, reason="trddgrep not installed")
def test_missing_corpus_is_could_not_run(tmp_path):
    """A dir with no design/ corpus makes trddgrep exit 2: refuse distinctly."""
    ok, reason = _trdd_validate_gate("AAAAAAAA", tmp_path)
    assert not ok
    assert "could not run" in reason.lower()


@pytest.mark.skipif(not _HAVE_TRDDGREP, reason="trddgrep not installed")
def test_findings_on_other_cards_do_not_gate_this_write():
    """Corpus errors naming OTHER cards never freeze this card's mirror write."""
    ok, reason = _trdd_validate_gate("ZZZZZZZ0", _ROOT)
    assert ok, reason
