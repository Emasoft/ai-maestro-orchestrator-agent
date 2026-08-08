#!/usr/bin/env python3
"""The dispatch precondition — never dispatch against an unsatisfiable NPT.

Implements TRDD-BYCN5PB7 (ai-maestro `rules/aimaestro/aimaestro-trdd-approval.md`,
Part B2) for this plugin:

    Before moving a TRDD to `dev` (i.e. handing a worker its build order), the
    dispatcher MUST ensure the BASE that worker branches from already satisfies
    every NPT that worker's TRDD declares. Never dispatch a worker whose declared
    NPT is satisfied only by an unmerged PR, an unpushed branch, or any base it
    does not branch from.

WHY THIS IS A RULE AND NOT ADVICE. Violating it produces a deadlock in which
nobody is wrong and nothing moves: the worker reads its NPT gate, correctly
refuses to build because the prerequisite is genuinely absent from its base, and
flags the dispatcher — while the dispatcher believes the work was delivered.
Observed live in the SCEN-031 re-run: requirements sat in an unmerged PR#4 while
`main` held only "Initial commit". The worker refusing was behaving CORRECTLY;
the defect was upstream, in the dispatch.

A CLOSED dependency is NOT a satisfied one. That is the whole point: this
plugin's pre-existing `check_dependencies_resolved` asked only whether the
dependency issue was CLOSED, which is true the moment someone clicks close —
including while the code that satisfies it sits in an unmerged PR, or is merged
to a branch the worker will never see.

The evaluation is a PURE function over already-fetched data so it can be tested
against real payload shapes without mocking GitHub. The I/O lives in the caller.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ClosingPR(TypedDict, total=False):
    """A pull request that closed a dependency issue."""

    number: int
    merged: bool
    baseRefName: str


class Dependency(TypedDict, total=False):
    """A dependency issue plus the PRs that closed it."""

    number: int
    state: str          # "OPEN" | "CLOSED"
    closing_prs: list[ClosingPR]


def evaluate_dispatch_precondition(
    base: str, dependencies: list[Dependency]
) -> tuple[bool, list[str]]:
    """Decide whether a card may be dispatched to `dev` against `base`.

    Args:
        base: the ref the worker will branch from (e.g. "main").
        dependencies: the card's declared prerequisites, each with its issue
            state and the PRs that closed it.

    Returns:
        (satisfied, reasons). `reasons` is empty when satisfied, and otherwise
        carries one human-readable line per unmet prerequisite — plural, because
        a dispatcher fixing one blocker only to hit the next on the following
        attempt is the slow version of the deadlock this exists to prevent.
    """
    reasons: list[str] = []

    for dep in dependencies:
        num = dep.get("number", "?")
        state = (dep.get("state") or "").upper()

        if state != "CLOSED":
            reasons.append(f"#{num} is still {state or 'UNKNOWN'} — the prerequisite is not done")
            continue

        closing = dep.get("closing_prs") or []
        if not closing:
            # Closed with no PR: a manual close, or work landed by direct push.
            # We cannot prove it reached `base`, and an unprovable prerequisite
            # is exactly what the rule forbids dispatching against. Say so
            # precisely rather than implying the work is missing — the dispatcher
            # needs to know which of the two it is.
            reasons.append(
                f"#{num} is CLOSED but no closing PR is recorded, so it cannot be "
                f"shown to be on '{base}' — confirm the work landed, or link the PR"
            )
            continue

        merged_to_base = [
            pr for pr in closing
            if pr.get("merged") and pr.get("baseRefName") == base
        ]
        if merged_to_base:
            continue

        unmerged = [pr for pr in closing if not pr.get("merged")]
        if unmerged:
            nums = ", ".join(f"#{pr.get('number', '?')}" for pr in unmerged)
            reasons.append(
                f"#{num} is satisfied only by UNMERGED PR {nums} — dispatching now "
                f"deadlocks the worker at its NPT gate (TRDD-BYCN5PB7)"
            )
        else:
            others = ", ".join(
                f"#{pr.get('number', '?')}->{pr.get('baseRefName', '?')}" for pr in closing
            )
            reasons.append(
                f"#{num} was merged to a different base ({others}), not '{base}' — "
                f"the worker will not see it"
            )

    return (not reasons, reasons)


def format_refusal(issue_number: int, base: str, reasons: list[str]) -> str:
    """Render a refusal the dispatcher can act on without re-deriving it."""
    body = "\n".join(f"  - {r}" for r in reasons)
    return (
        f"REFUSED to dispatch #{issue_number} to `dev` against '{base}' — "
        f"{len(reasons)} prerequisite(s) unmet:\n{body}\n"
        f"Land the prerequisites on '{base}' (merge the PR, or fix the base), "
        f"THEN dispatch. A worker dispatched now would correctly refuse to build."
    )


def dependency_from_gh(issue_json: dict[str, Any]) -> Dependency:
    """Adapt one `gh issue view --json number,state,closedByPullRequestsReferences` payload.

    Kept next to the evaluator so the field names GitHub returns are named in
    exactly one place; a rename upstream breaks here loudly instead of silently
    producing a dependency with no closing PRs, which would read as "closed but
    unprovable" and block dispatch for the wrong reason.
    """
    refs = issue_json.get("closedByPullRequestsReferences") or []
    return Dependency(
        number=int(issue_json.get("number", 0)),
        state=str(issue_json.get("state", "")),
        closing_prs=[
            ClosingPR(
                number=int(r.get("number", 0)),
                merged=bool(r.get("merged", False)),
                baseRefName=str(r.get("baseRefName", "")),
            )
            for r in refs
        ],
    )
