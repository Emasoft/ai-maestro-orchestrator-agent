#!/usr/bin/env python3
"""amoa_design_handoff.py — read-side of the architect→orchestrator design handoff.

orch #26 (read-side of architect #7): the architect (v2.11.0) creates an AI-Maestro
`epic` task on design completion and stamps its id into the design-handoff AMP message as
an OPTIONAL top-level `aimaestro_task_id` key inside the message `content` (sibling of
`type`/`message`), in both the `design_complete` and `handoff` message shapes. The
orchestrator (AMOA) reads that id here and later attaches its implementation child tasks
under the epic via `amp-kanban-create-task --parent "$EPIC"`, completing the
design-doc → epic → child-task → GitHub-issue traceability chain.

The key is ADDITIVE and OPTIONAL: it is absent on older handoffs and whenever AI-Maestro is
not in use. Absence is a first-class valid state — the orchestrator then behaves exactly as
before (an unlinked breakdown), with NO regression. This is why an absent key returns None
rather than raising: it is the documented contract, not a swallowed error. Genuinely wrong
shapes (non-object content, or the key present but not a non-empty string) DO raise — those
are real data defects, and mis-linking a child task under a bad parent id is worse than a
loud failure at ingestion time.
"""

import json
from typing import Any


def extract_aimaestro_task_id(content: dict[str, Any] | str) -> str | None:
    """Extract the optional AI-Maestro epic id from a design-handoff message `content`.

    Args:
        content: the AMP message `content`, either already parsed as a dict or as its raw
            JSON string (AMP delivers `content` as a JSON string, so both forms occur).

    Returns:
        The `aimaestro_task_id` string (stripped) when present and non-empty; None when the
        key is absent (the optional/additive contract — orch #26: absence ⇒ behave as today).

    Raises:
        TypeError: `content` is neither a dict nor a JSON object string.
        ValueError: `content` is a string that is not valid JSON, or `aimaestro_task_id`
            is present but is not a non-empty string (a real data defect, not the
            optional-absent case).
    """
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError as exc:
            # A malformed handoff message is a real defect, not the optional-absent case.
            raise ValueError(f"design-handoff content is not valid JSON: {exc}") from exc

    if not isinstance(content, dict):
        raise TypeError(
            "design-handoff content must be a JSON object (or its dict), got "
            f"{type(content).__name__}"
        )

    task_id = content.get("aimaestro_task_id")
    if task_id is None:
        # Optional/additive key absent: older handoff or AI-Maestro not in use. No regression.
        return None

    if not isinstance(task_id, str) or not task_id.strip():
        # Present but unusable as a --parent value: fail fast rather than mis-link a child.
        raise ValueError(
            f"aimaestro_task_id is present but not a non-empty string: {task_id!r}"
        )

    return task_id.strip()
