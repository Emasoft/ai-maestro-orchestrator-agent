#!/usr/bin/env python3
"""The dispatch precondition (TRDD-BYCN5PB7): a CLOSED dependency is not a satisfied one.

The rule these pin: never dispatch a worker whose declared NPT is satisfied only
by an unmerged PR, an unpushed branch, or a base it does not branch from. The
failure it prevents is a deadlock where nobody is wrong — the worker correctly
refuses at its NPT gate while the dispatcher believes the work was delivered.

The evaluator is pure, so these run against real `gh` payload SHAPES with no
mocking of GitHub itself.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))

from amoa_dispatch_gate import (  # noqa: E402
    dependency_from_gh,
    evaluate_dispatch_precondition,
    format_refusal,
)


def test_no_dependencies_dispatches_freely():
    """A card with no prerequisites has nothing to be unsatisfied."""
    ok, reasons = evaluate_dispatch_precondition("main", [])
    assert ok and reasons == []


def test_merged_to_the_dispatch_base_is_satisfied():
    ok, reasons = evaluate_dispatch_precondition("main", [
        {"number": 4, "state": "CLOSED",
         "closing_prs": [{"number": 9, "merged": True, "baseRefName": "main"}]},
    ])
    assert ok, reasons


def test_open_dependency_blocks():
    ok, reasons = evaluate_dispatch_precondition("main", [
        {"number": 4, "state": "OPEN", "closing_prs": []},
    ])
    assert not ok
    assert "still OPEN" in reasons[0]


def test_the_scen031_case_closed_but_pr_unmerged():
    """The exact live failure: requirements in an unmerged PR while main holds nothing.

    This is the case a CLOSED-only check waves through, and it is the one that
    produced a real stalled run.
    """
    ok, reasons = evaluate_dispatch_precondition("main", [
        {"number": 4, "state": "CLOSED",
         "closing_prs": [{"number": 4, "merged": False, "baseRefName": "main"}]},
    ])
    assert not ok
    assert "UNMERGED" in reasons[0]
    assert "BYCN5PB7" in reasons[0]


def test_merged_to_a_different_base_blocks():
    """Merged is not enough — it must be merged into the base the worker branches from."""
    ok, reasons = evaluate_dispatch_precondition("main", [
        {"number": 4, "state": "CLOSED",
         "closing_prs": [{"number": 9, "merged": True, "baseRefName": "develop"}]},
    ])
    assert not ok
    assert "different base" in reasons[0]
    assert "develop" in reasons[0]


def test_closed_with_no_closing_pr_blocks_but_says_why():
    """Unprovable is not the same as missing, and the dispatcher needs to know which."""
    ok, reasons = evaluate_dispatch_precondition("main", [
        {"number": 4, "state": "CLOSED", "closing_prs": []},
    ])
    assert not ok
    assert "no closing PR" in reasons[0]
    assert "confirm the work landed" in reasons[0]


def test_all_unmet_prerequisites_are_reported_together():
    """Reporting one blocker at a time is the slow version of the same deadlock."""
    ok, reasons = evaluate_dispatch_precondition("main", [
        {"number": 1, "state": "OPEN", "closing_prs": []},
        {"number": 2, "state": "CLOSED",
         "closing_prs": [{"number": 7, "merged": False, "baseRefName": "main"}]},
        {"number": 3, "state": "CLOSED",
         "closing_prs": [{"number": 8, "merged": True, "baseRefName": "main"}]},
    ])
    assert not ok
    assert len(reasons) == 2, reasons  # #3 is satisfied and must not be reported


def test_one_satisfied_pr_among_several_is_enough():
    """A dependency closed by several PRs needs only one that reached the base."""
    ok, _ = evaluate_dispatch_precondition("main", [
        {"number": 4, "state": "CLOSED", "closing_prs": [
            {"number": 7, "merged": False, "baseRefName": "main"},
            {"number": 8, "merged": True, "baseRefName": "main"},
        ]},
    ])
    assert ok


def test_gh_payload_adapter_reads_real_field_names():
    """The adapter must read GitHub's actual field names, not invented ones."""
    dep = dependency_from_gh({
        "number": 4,
        "state": "CLOSED",
        "closedByPullRequestsReferences": [
            {"number": 9, "merged": True, "baseRefName": "main"},
        ],
    })
    assert dep["number"] == 4
    assert dep["closing_prs"][0]["baseRefName"] == "main"
    ok, _ = evaluate_dispatch_precondition("main", [dep])
    assert ok


def test_adapter_missing_refs_field_does_not_read_as_satisfied():
    """If GitHub renames the field, we must block — never silently dispatch.

    A rename that produced an empty closing_prs list must land in the
    'closed but unprovable' branch, which blocks. The dangerous failure would be
    an adapter that turned a missing field into an apparent success.
    """
    dep = dependency_from_gh({"number": 4, "state": "CLOSED"})
    ok, reasons = evaluate_dispatch_precondition("main", [dep])
    assert not ok
    assert "no closing PR" in reasons[0]


def test_refusal_message_names_the_fix():
    msg = format_refusal(12, "main", ["#4 is satisfied only by UNMERGED PR #4"])
    assert "REFUSED to dispatch #12" in msg
    assert "main" in msg
    assert "THEN dispatch" in msg
