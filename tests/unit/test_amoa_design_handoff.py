#!/usr/bin/env python3
"""Unit tests for the design-handoff read-side (shared/amoa_design_handoff.py).

Guards orch #26 (read-side of architect #7): the orchestrator must READ the optional
`aimaestro_task_id` epic id the architect stamps into the design-handoff message content,
tolerate its absence with no regression, and fail loudly on a genuinely malformed value.
"""

import sys
from pathlib import Path

import pytest

# The helper lives in shared/ (not scripts/) so skill-bundled code at a different path
# depth imports the same module — the same convention as test_amoa_kanban_vocab.py.
SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from amoa_design_handoff import extract_aimaestro_task_id  # noqa: E402

# The two shipped architect message shapes (v2.11.0, ai-maestro-message-templates §1.3/§1.4).
# aimaestro_task_id is a TOP-LEVEL key in content, sibling of type/message.
DESIGN_COMPLETE = {
    "type": "design_complete",
    "aimaestro_task_id": "PVTI_laDOABcd1234",
    "message": "[DONE] Design for Widget complete. Ready for AMOA assignment.",
}
HANDOFF = {
    "type": "handoff",
    "aimaestro_task_id": "PVTI_laDOABcd1234",
    "message": "Design handoff ready for Widget. Awaiting AMOA assignment.",
}


def test_extracts_id_from_design_complete_dict():
    """A design_complete content dict yields its aimaestro_task_id verbatim."""
    assert extract_aimaestro_task_id(DESIGN_COMPLETE) == "PVTI_laDOABcd1234"


def test_extracts_id_from_handoff_dict():
    """A handoff content dict yields its aimaestro_task_id verbatim."""
    assert extract_aimaestro_task_id(HANDOFF) == "PVTI_laDOABcd1234"


def test_extracts_id_from_json_string():
    """content delivered as a JSON string (AMP's wire form) is parsed and the id read."""
    import json

    assert extract_aimaestro_task_id(json.dumps(HANDOFF)) == "PVTI_laDOABcd1234"


def test_absent_key_returns_none():
    """An older handoff without the additive key returns None — no regression."""
    legacy = {"type": "handoff", "message": "Design handoff ready."}
    assert extract_aimaestro_task_id(legacy) is None


def test_null_value_returns_none():
    """An explicit null aimaestro_task_id is treated as absent (None), not an error."""
    assert extract_aimaestro_task_id({"type": "handoff", "aimaestro_task_id": None}) is None


def test_id_is_stripped_of_surrounding_whitespace():
    """A padded id is returned trimmed so it is safe to pass to --parent."""
    padded = {"type": "handoff", "aimaestro_task_id": "  PVTI_x9  "}
    assert extract_aimaestro_task_id(padded) == "PVTI_x9"


def test_empty_string_id_raises():
    """A present-but-empty id is a real defect and fails fast (ValueError)."""
    with pytest.raises(ValueError):
        extract_aimaestro_task_id({"type": "handoff", "aimaestro_task_id": "   "})


def test_non_string_id_raises():
    """A present-but-non-string id (e.g. a number) fails fast (ValueError)."""
    with pytest.raises(ValueError):
        extract_aimaestro_task_id({"type": "handoff", "aimaestro_task_id": 12345})


def test_non_object_content_raises():
    """content that is not a JSON object (e.g. a list) fails fast (TypeError)."""
    with pytest.raises(TypeError):
        extract_aimaestro_task_id(["not", "an", "object"])  # type: ignore[arg-type]


def test_malformed_json_string_raises():
    """A content string that is not valid JSON fails fast (ValueError)."""
    with pytest.raises(ValueError):
        extract_aimaestro_task_id("{not valid json")


def test_json_string_scalar_raises():
    """A JSON string that parses to a scalar (not an object) fails fast (TypeError)."""
    with pytest.raises(TypeError):
        extract_aimaestro_task_id('"just a string"')
