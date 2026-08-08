#!/usr/bin/env python3
"""
AMOA Kanban Manager

Manages GitHub Project kanban for task assignment and tracking.
Only AMOA (Orchestrator) should use this script.

Usage:
    python amoa_kanban_manager.py create-task --title <title> --body <body> --agent <name> [--priority <p>]
    python amoa_kanban_manager.py assign-task --issue <number> --agent <name>
    python amoa_kanban_manager.py update-status --issue <number> --status <status>
    python amoa_kanban_manager.py set-dependency --issue <number> --blocked-by <issue>
    python amoa_kanban_manager.py check-ready-tasks
    python amoa_kanban_manager.py notify-agent --issue <number> --agent <name>
    python amoa_kanban_manager.py sync-from-github
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

# The ratified kanban vocabulary lives in shared/ so BOTH the top-level scripts
# and the skill-bundled ones (different path depths) import the same module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))

# AI Maestro sync integration (same-directory import, resolved at runtime)
from amoa_aimaestro_sync import (  # noqa: E402  (path injected above, on purpose)
    bulk_sync,
    notify_sync_result,
    sync_task,
)
from amoa_dispatch_gate import (  # noqa: E402  (path injected above, on purpose)
    Dependency,
    dependency_from_gh,
    evaluate_dispatch_precondition,
    format_refusal,
)
from amoa_kanban_vocab import (  # noqa: E402  (path injected above, on purpose)
    KANBAN_COLUMNS,
    LEGACY_STATUS_MIGRATION,
    assert_orchestrator_may_transition,
    resolve_column,
)
from amoa_trdd_link import (  # noqa: E402  (path injected above, on purpose)
    add_external_ref,
    crosses_zone,
    extract_trdd_id,
    find_trdd,
    set_column,
    zone_for_column,
)

# GitHub configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "Emasoft")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

# Project configuration
PROJECT_ID = os.environ.get("GITHUB_PROJECT_ID", "")
TEAM_ID = os.environ.get("AIMAESTRO_TEAM_ID", "")

# The kanban columns come from amoa_kanban_vocab (the ratified 17, issue #27).
# This script used to define its own 8-entry status→display-name map; that map
# was the pre-2026-06-20 vocabulary and disagreed with the TRDD `column:` states
# and the ai-maestro server TaskStatus, so a task moved here landed in a column
# the other surfaces did not recognize.
#
# Status LABELS remain `status:<column>` — the label vocabulary is now the
# ratified column set. Legacy label names stay in the REMOVAL set below so a
# stale `status:in-progress` is stripped when the task moves to `status:dev`;
# without that, an issue would carry two status labels and the board would read
# whichever it hit first.
STATUS_LABEL_VOCAB: tuple[str, ...] = (
    *KANBAN_COLUMNS,
    *LEGACY_STATUS_MIGRATION,
)



def get_timestamp() -> str:
    """Get current ISO8601 timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Run a GitHub CLI command."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "GH_TOKEN": GITHUB_TOKEN},
    )
    return result.returncode, result.stdout, result.stderr


def check_gh_project_scopes() -> bool:
    """Verify gh auth has project scopes before kanban operations.

    The default gh auth login does not include 'project' and 'read:project'
    scopes. Without them, all GitHub Projects V2 operations will fail.
    Scopes must be added by a human via interactive browser:
        gh auth refresh -h github.com -s project,read:project
    """
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    if "project" not in combined:
        print(
            "ERROR: gh auth is missing 'project' and 'read:project' scopes.\n"
            "A human must run: gh auth refresh -h github.com -s project,read:project\n"
            "This requires interactive browser approval and cannot be automated.",
            file=sys.stderr,
        )
        return False
    return True


def load_team_registry(repo_path: str | None = None) -> dict[str, Any]:
    """Load team registry from repository."""
    if repo_path:
        registry_path = Path(repo_path) / ".ai-maestro" / "team-registry.json"
    else:
        # Try current directory
        registry_path = Path(".ai-maestro") / "team-registry.json"

    if not registry_path.exists():
        raise FileNotFoundError(f"Team registry not found: {registry_path}")

    with open(registry_path, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def get_agent_address(registry: dict[str, Any], agent_name: str) -> str | None:
    """Get AI Maestro address for an agent from registry."""
    # Check team agents
    for agent in registry.get("agents", []):
        if agent["name"] == agent_name:
            return cast(str, agent["ai_maestro_address"])

    # Check shared agents
    for agent in registry.get("shared_agents", []):
        if agent["name"] == agent_name:
            return cast(str, agent["ai_maestro_address"])

    return None


def send_ai_maestro_message(
    to: str,
    subject: str,
    content: dict[str, Any],
    priority: str = "normal",
) -> bool:
    """Send a message via AI Maestro AMP CLI."""
    try:
        msg_type = (
            content.get("type", "notification")
            if isinstance(content, dict)
            else "notification"
        )
        msg_text = (
            content.get("message", str(content))
            if isinstance(content, dict)
            else str(content)
        )
        result = subprocess.run(
            [
                "amp-send",
                to,
                subject,
                msg_text,
                "--priority",
                priority,
                "--type",
                msg_type,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to send message: {e}", file=sys.stderr)
        return False


def create_task_issue(
    title: str,
    body: str,
    assigned_agent: str,
    priority: str = "normal",
    dependencies: list[int] | None = None,
    task_requirements_doc: str | None = None,
    trdd_id: str | None = None,
) -> dict[str, Any] | None:
    """Create a GitHub issue for a task.

    Args:
        trdd_id: the `TRDD-<id8>` this card implements, for a TRDD-backed task.
            Appended to the TITLE rather than the body, per the ratified linkage
            shape — a title survives body edits that would drop a marker line,
            and it keeps the id greppable from `gh issue list` output alone.
            This is what makes the board→TRDD write-through resolvable at all:
            without it, a move has no card to land in. Optional because not
            every issue is TRDD-backed.
    """
    if trdd_id:
        canonical = trdd_id.upper()
        # Idempotent: re-creating or retitling must not stack the citation.
        if f"TRDD-{canonical}" not in title:
            title = f"{title} (TRDD-{canonical})"

    # Build labels
    labels = [f"assign:{assigned_agent}", f"priority:{priority}"]

    # Build body with agent identity section
    full_body = f"""{body}

---

## Task Assignment

| Field | Value |
|-------|-------|
| Assigned Agent | `{assigned_agent}` |
| Priority | {priority} |
| Assigned At | {get_timestamp()} |
| Assigned By | amoa-orchestrator |

"""

    if dependencies:
        dep_list = ", ".join([f"#{d}" for d in dependencies])
        full_body += f"\n**Dependencies**: Blocked by {dep_list}\n"

    if task_requirements_doc:
        full_body += f"""
---

## Task Requirements Document

{task_requirements_doc}
"""

    # Create issue via gh CLI
    args = [
        "issue",
        "create",
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--title",
        title,
        "--body",
        full_body,
        "--label",
        ",".join(labels),
    ]

    returncode, stdout, stderr = run_gh_command(args)

    if returncode != 0:
        print(f"Failed to create issue: {stderr}", file=sys.stderr)
        return None

    # Parse issue URL to get number
    # stdout is like: https://github.com/owner/repo/issues/42
    issue_url = stdout.strip()
    issue_number = int(issue_url.split("/")[-1])

    # Sync to AI Maestro
    if TEAM_ID:
        sync_task(
            team_id=TEAM_ID,
            issue_number=issue_number,
            issue_title=title,
            status="todo",
            agent_id=assigned_agent,
            priority=priority,
        )

    return {
        "number": issue_number,
        "url": issue_url,
        "title": title,
        "assigned_agent": assigned_agent,
        "priority": priority,
        "dependencies": dependencies or [],
        "created_at": get_timestamp(),
    }


def assign_task_to_agent(issue_number: int, agent_name: str) -> bool:
    """Assign a task (issue) to an agent by adding the label.

    Removes any existing assign:* labels first to prevent
    multiple assignment labels on reassignment.
    """
    # 1. Get current labels to find existing assign:* labels
    args = [
        "issue",
        "view",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json",
        "labels",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        print("Failed to get issue labels", file=sys.stderr)
        return False

    # 2. Find and remove existing assign:* labels
    current_labels = json.loads(stdout).get("labels", [])
    labels_to_remove = [
        label["name"] for label in current_labels if label["name"].startswith("assign:")
    ]

    for label in labels_to_remove:
        args = [
            "issue",
            "edit",
            str(issue_number),
            "--repo",
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--remove-label",
            label,
        ]
        run_gh_command(args)  # Ignore errors on removal

    # 3. Add the new assign label
    args = [
        "issue",
        "edit",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--add-label",
        f"assign:{agent_name}",
    ]

    returncode, _, stderr = run_gh_command(args)

    if returncode != 0:
        print(f"Failed to assign task: {stderr}", file=sys.stderr)
        return False

    # Sync assignment to AI Maestro
    if TEAM_ID:
        view_args = ["issue", "view", str(issue_number), "--repo", f"{GITHUB_OWNER}/{GITHUB_REPO}", "--json", "title,labels"]
        rc, out, _ = run_gh_command(view_args)
        if rc == 0:
            data = json.loads(out)
            title = data.get("title", f"Issue #{issue_number}")
            labels = data.get("labels", [])
            # An issue with no status label has not been triaged onto the board
            # yet -> `backburner` (the ratified entry column; the old default was
            # the pre-2026-06-20 "backlog", which the server no longer accepts).
            status = "backburner"
            for lbl in labels:
                if lbl.get("name", "").startswith("status:"):
                    status = lbl["name"].removeprefix("status:")
            # A live issue may still carry a legacy `status:in-progress` label, so
            # resolve before syncing. An unrecognized label is a data error worth
            # surfacing, but it must not abort the assignment that already
            # succeeded above -> report and skip the sync.
            try:
                column = resolve_column(status)
            except ValueError as exc:
                print(f"WARNING: issue #{issue_number} not synced: {exc}", file=sys.stderr)
            else:
                sync_task(team_id=TEAM_ID, issue_number=issue_number, issue_title=title, status=column, agent_id=agent_name)

    return True


def update_task_status(
    issue_number: int, status: str, approved_by: str | None = None
) -> bool:
    """Update task status by changing labels.

    Args:
        issue_number: the GitHub issue backing the card.
        status: target column (ratified or a known legacy value).
        approved_by: the approver, when this transition was already granted by a
            MANAGER or the USER. Supplying it turns this call from a decision the
            orchestrator ORIGINATES into a mirror of one already made, which is
            what makes a governed transition legitimate here. It is recorded on
            the issue so the approval is auditable from the board, not only from
            whatever conversation granted it. Leave it None for ordinary
            mechanical moves.
    """

    # Resolve to a ratified column: a legacy value migrates, an unknown value is
    # rejected here rather than written to the board as a bogus `status:` label
    # nobody consumes (issue #27 — no silent default column).
    try:
        column = resolve_column(status)
    except ValueError as exc:
        print(f"Invalid status: {exc}", file=sys.stderr)
        return False

    # Remove old status labels (ratified AND legacy) and add the resolved one.
    status_labels = [f"status:{s}" for s in STATUS_LABEL_VOCAB]

    # Get current labels
    args = [
        "issue",
        "view",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json",
        "labels",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        return False

    current_labels = json.loads(stdout).get("labels", [])
    labels_to_remove = [
        label["name"] for label in current_labels if label["name"] in status_labels
    ]

    # EDITOR AUTHORITY GATE (alignment contract, "Orchestrator-plugin alignment":
    # an ORCHESTRATOR moves and re-assigns; it does NOT silently perform USER- or
    # MANAGER-gated transitions).
    #
    # This is the gate the resolve_column invariant demands. On a GitHub-issue
    # -native board the `status:` label IS the state, so this call ORIGINATES the
    # decision rather than mirroring one — which is exactly the case the invariant
    # says must be gated. `approved_by` is how an already-approved transition is
    # RECORDED: with it we are mirroring somebody else's decision, and mirroring
    # is exempt (approval-defaults §A). Without it, a release-pipeline or
    # abandonment transition would land with no approver anywhere in the record.
    from_column = None
    for label in labels_to_remove:
        try:
            from_column = resolve_column(label.removeprefix("status:"))
            break
        except ValueError:
            continue  # a stale label outside the vocabulary tells us nothing
    if approved_by is None:
        try:
            assert_orchestrator_may_transition(from_column, column)
        except PermissionError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return False

    # Remove old status labels
    for label in labels_to_remove:
        args = [
            "issue",
            "edit",
            str(issue_number),
            "--repo",
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--remove-label",
            label,
        ]
        run_gh_command(args)

    # Add new status label
    args = [
        "issue",
        "edit",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--add-label",
        f"status:{column}",
    ]

    returncode, _, stderr = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to update status: {stderr}", file=sys.stderr)
        return False

    # Record a governed transition's approver ON THE BOARD. Written only after
    # the label change succeeds, so we never claim an approval for a move that
    # did not happen. A failure to comment is not fatal — the transition is
    # already real, and losing the audit line is better than reporting the whole
    # move as failed and inviting a retry that double-applies it.
    if approved_by is not None:
        run_gh_command([
            "issue", "comment", str(issue_number),
            "--repo", f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--body",
            f"_Posted by the Claude developing **ai-maestro-orchestrator-agent** "
            f"(via the shared owner gh auth)._\n\n"
            f"Status → `{column}`"
            + (f" (from `{from_column}`)" if from_column else "")
            + f", approved by **{approved_by}**, recorded {get_timestamp()}.",
        ])

    # TRDD WRITE-THROUGH — the SSOT half of the alignment contract ("every board
    # mutation lands in the TRDD file (and its folder), not only in a mirror").
    #
    # Deliberately placed AFTER the authority gate above, so it is gated by
    # construction: every column decision that reaches here has either passed
    # `assert_orchestrator_may_transition` or carries an explicit `approved_by`.
    # That is the condition MANAGER ruling orch#27 attached to originating TRDD
    # writes, and putting this call anywhere earlier would silently void it.
    #
    # Also after the label write, not before: if the mirror fails we return
    # early and the TRDD is never touched, so the two cannot disagree with the
    # TRDD claiming a move the board did not make.
    _write_through_to_trdd(issue_number, column, from_column)

    # Sync status change to AI Maestro
    if TEAM_ID:
        # Get issue title for sync
        view_args = ["issue", "view", str(issue_number), "--repo", f"{GITHUB_OWNER}/{GITHUB_REPO}", "--json", "title"]
        rc, out, _ = run_gh_command(view_args)
        title = json.loads(out).get("title", f"Issue #{issue_number}") if rc == 0 else f"Issue #{issue_number}"
        # Ship the RESOLVED column: the server's TaskStatus is the same ratified
        # vocabulary, so sending the caller's raw legacy value would re-introduce
        # the split this fix removes.
        sync_task(team_id=TEAM_ID, issue_number=issue_number, issue_title=title, status=column)

    return True


def close_issue_safely(issue_number: int, comment: str = "Task completed.") -> bool:
    """Close an issue with a guard for Done-column auto-close.

    GitHub Projects V2 auto-closes issues when moved to the Done column.
    This function checks the issue state before attempting to close it,
    preventing redundant close attempts and misleading error logs.
    """
    # Check current state
    args = [
        "issue",
        "view",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json",
        "state",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to check issue #{issue_number} state", file=sys.stderr)
        return False

    state = json.loads(stdout).get("state", "OPEN")

    if state == "CLOSED":
        print(
            f"INFO: Issue #{issue_number} is already closed "
            f"(likely auto-closed by Done column)"
        )
        return True

    # Close with comment
    args = [
        "issue",
        "close",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--comment",
        comment,
    ]

    returncode, _, stderr = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to close issue #{issue_number}: {stderr}", file=sys.stderr)
        return False

    return True


def set_task_dependency(issue_number: int, blocked_by: list[int]) -> bool:
    """Set task dependencies by adding a comment and label."""

    # Add blocked label
    args = [
        "issue",
        "edit",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--add-label",
        "blocked",
    ]
    run_gh_command(args)

    # Add comment with dependencies
    dep_list = ", ".join([f"#{d}" for d in blocked_by])
    comment = f"**Dependencies**: This task is blocked by {dep_list}"

    args = [
        "issue",
        "comment",
        str(issue_number),
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--body",
        comment,
    ]

    returncode, _, stderr = run_gh_command(args)
    if returncode != 0:
        print(f"Failed to set dependency: {stderr}", file=sys.stderr)
        return False

    return True


# Git calls here are single, local, and fast (`git mv`); a bounded timeout keeps
# a hung git from wedging a board move. Mirrors shared/thresholds.py TIMEOUTS.GIT
# — kept as a local constant so this script has no import-time dependency on a
# module it otherwise does not need.
GIT_TIMEOUT_SECONDS = 30


def get_project_root() -> Path:
    """The repo root whose `design/` holds this project's TRDD corpus.

    `CLAUDE_PROJECT_DIR` when the harness sets it, else the CWD. Never an
    absolute path baked in: R52.1 confines writes to the agent's own working
    directory, and a hardcoded root is how a tool starts writing into somebody
    else's tree.
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


def run_command(args: list[str]) -> tuple[int, str, str]:
    """Run a non-gh command (git), returning (returncode, stdout, stderr)."""
    result = subprocess.run(args, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS)
    return result.returncode, result.stdout, result.stderr


def _write_through_to_trdd(
    issue_number: int, column: str, from_column: str | None
) -> bool:
    """Land a board move in the TRDD that backs the issue, and in its folder.

    Returns True when a TRDD was updated, False when the card has none. A card
    with no TRDD behind it is legitimate (not every issue is TRDD-backed), so
    absence is reported, never raised.

    Best-effort by design: the mirror has already moved by the time we get here,
    so a failure to reach the TRDD must not report the whole transition as
    failed and invite a retry that re-applies the label. It logs loudly instead —
    a silent divergence between board and SSOT is exactly what this contract
    exists to prevent, so it must be visible even though it is not fatal.
    """
    rc, stdout, _ = run_gh_command([
        "issue", "view", str(issue_number),
        "--repo", f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--json", "title,body,url",
    ])
    if rc != 0:
        print(f"WARNING: TRDD write-through skipped for #{issue_number}: cannot read issue",
              file=sys.stderr)
        return False

    data = json.loads(stdout)
    # Title first: the ratified linkage puts the id there because a title
    # survives body edits that would drop a body marker.
    trdd_id = extract_trdd_id(data.get("title", "")) or extract_trdd_id(data.get("body", ""))
    if not trdd_id:
        return False

    design_root = get_project_root() / "design"
    trdd_path = find_trdd(trdd_id, design_root)
    if trdd_path is None:
        print(
            f"WARNING: issue #{issue_number} cites {trdd_id} but no such TRDD exists "
            f"under {design_root} — board and SSOT are now out of step",
            file=sys.stderr,
        )
        return False

    try:
        set_column(trdd_path, column, get_timestamp())
        add_external_ref(trdd_path, data.get("url", ""))
    except ValueError as exc:
        print(f"WARNING: cannot write {trdd_path}: {exc}", file=sys.stderr)
        return False

    # The folder is part of the state, so a zone crossing needs a `git mv` — a
    # frontmatter-only edit would leave a completed card sitting in tasks/,
    # where every board query still counts it as open work.
    if crosses_zone(from_column, column):
        dest_dir = design_root / zone_for_column(column)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / trdd_path.name
        rc_mv, _, err = run_command(["git", "mv", str(trdd_path), str(dest)])
        if rc_mv != 0:
            print(
                f"WARNING: {trdd_path.name} needs to move to {dest_dir.name}/ but "
                f"`git mv` failed: {err.strip()}",
                file=sys.stderr,
            )
        else:
            print(f"  Moved {trdd_path.name} -> design/{dest_dir.name}/")

    return True


def check_dispatch_precondition(
    issue_number: int, dependencies: list[int], base: str = "main"
) -> bool:
    """Enforce TRDD-BYCN5PB7 before a card is handed to a worker as a build order.

    Stricter than check_dependencies_resolved on purpose: that function asks only
    whether the dependency issue is CLOSED, which is true the moment somebody
    clicks close — including while the code satisfying it sits in an unmerged PR.
    Dispatching on that produces the deadlock the rule exists to prevent: the
    worker reads its NPT gate, correctly refuses to build because the prerequisite
    is genuinely absent from its base, and the dispatcher believes it shipped.

    Fetches each dependency's closing PRs, then defers to the pure evaluator in
    shared/amoa_dispatch_gate.py.
    """
    deps: list[Dependency] = []
    for dep in dependencies:
        returncode, stdout, stderr = run_gh_command([
            "issue", "view", str(dep),
            "--repo", f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--json", "number,state,closedByPullRequestsReferences",
        ])
        if returncode != 0:
            # Fail CLOSED. An unreadable prerequisite is an unproven one, and the
            # whole rule is about not dispatching against prerequisites we cannot
            # show are met. Treating a query failure as "probably fine" would
            # reintroduce the deadlock through the error path.
            print(
                f"REFUSED to dispatch #{issue_number}: cannot read dependency "
                f"#{dep} ({stderr.strip() or 'gh query failed'})",
                file=sys.stderr,
            )
            return False
        deps.append(dependency_from_gh(json.loads(stdout)))

    satisfied, reasons = evaluate_dispatch_precondition(base, deps)
    if not satisfied:
        print(format_refusal(issue_number, base, reasons), file=sys.stderr)
    return satisfied


def check_dependencies_resolved(dependencies: list[int]) -> bool:
    """Check if all dependencies are resolved (closed).

    NOTE: closed-ness alone does NOT authorize a dispatch — use
    check_dispatch_precondition for that (TRDD-BYCN5PB7). This remains the right
    check for readiness DISPLAY (get_ready_tasks), where the question is "has the
    blocking work been declared done", not "will the worker's base contain it".
    """

    for dep in dependencies:
        args = [
            "issue",
            "view",
            str(dep),
            "--repo",
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "--json",
            "state",
        ]

        returncode, stdout, _ = run_gh_command(args)
        if returncode != 0:
            return False

        state = json.loads(stdout).get("state", "")
        if state != "CLOSED":
            return False

    return True


def get_ready_tasks(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Get tasks that are ready to be worked on (dependencies resolved)."""

    # Get all open issues with assign labels
    args = [
        "issue",
        "list",
        "--repo",
        f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "--state",
        "open",
        "--json",
        "number,title,labels,body",
        "--limit",
        "100",
    ]

    returncode, stdout, _ = run_gh_command(args)
    if returncode != 0:
        return []

    issues = json.loads(stdout)
    ready_tasks = []

    for issue in issues:
        labels = [label["name"] for label in issue.get("labels", [])]

        # Check if assigned to an agent
        assigned_agent = None
        for label in labels:
            if label.startswith("assign:"):
                assigned_agent = label.replace("assign:", "")
                break

        if not assigned_agent:
            continue

        # A task is ready iff its column is `todo` (or it carries no status label
        # yet — untriaged but assigned). Every other column means deferred
        # (`backburner`), already underway (`dev`/`testing`/…), blocked, or done.
        #
        # This replaces a hardcoded `status:in-progress`/`status:ai-review`
        # exclusion list that (a) named pre-2026-06-20 columns which no longer
        # exist, and (b) was already redundant with the `is_todo` test below it —
        # so the whole check reduces to "is the resolved column `todo`". Legacy
        # labels still on live issues resolve through the shared vocabulary
        # (issue #27).
        if "blocked" in labels:  # the bare, non-status label some issues carry
            continue

        status_labels = [
            lbl.removeprefix("status:") for lbl in labels if lbl.startswith("status:")
        ]
        if status_labels:
            try:
                columns = {resolve_column(s) for s in status_labels}
            except ValueError as exc:
                # An unrecognized status label means the issue's placement is
                # unknown; dispatching it could double-assign work already in
                # flight, so skip it loudly rather than guess it is ready.
                print(
                    f"WARNING: issue #{issue.get('number')} skipped: {exc}",
                    file=sys.stderr,
                )
                continue
            is_todo = columns == {"todo"}
        else:
            is_todo = True

        if is_todo:
            # Verify agent exists in registry
            address = get_agent_address(registry, assigned_agent)
            if address:
                ready_tasks.append(
                    {
                        "number": issue["number"],
                        "title": issue["title"],
                        "assigned_agent": assigned_agent,
                        "agent_address": address,
                    }
                )

    return ready_tasks


def notify_agent_of_task(
    registry: dict[str, Any],
    issue_number: int,
    agent_name: str,
    task_title: str,
    task_requirements_doc: str | None = None,
) -> bool:
    """Notify an agent that they have a task assigned."""

    address = get_agent_address(registry, agent_name)
    if not address:
        print(f"Agent not found in registry: {agent_name}", file=sys.stderr)
        return False

    # Get agent info from registry
    agent_info = None
    for agent in registry.get("agents", []):
        if agent["name"] == agent_name:
            agent_info = agent
            break

    team_name = registry.get("team", {}).get("name", "unknown-team")
    repo_url = registry.get("team", {}).get("project", {}).get("repository", "")

    content = {
        "type": "task-assignment",
        "message": f"You have been assigned task #{issue_number}: {task_title}",
        "task": {
            "issue_number": issue_number,
            "issue_url": f"{repo_url}/issues/{issue_number}",
            "title": task_title,
        },
        "sender_identity": {
            "name": "amoa-orchestrator",
            "role": "orchestrator",
            "plugin": "ai-maestro-orchestrator-agent",
            "team": team_name,
        },
        "recipient_identity": {
            "name": agent_name,
            "role": agent_info["role"] if agent_info else "unknown",
            "plugin": agent_info["plugin"] if agent_info else "unknown",
        },
        "instructions": "Please review the task and begin work. Report progress to me (orchestrator). Let me know if you need clarifications.",
    }

    if task_requirements_doc:
        content["task_requirements_document"] = task_requirements_doc

    return send_ai_maestro_message(
        to=address,
        subject=f"[TASK ASSIGNED] #{issue_number}: {task_title}",
        content=content,
        priority="high",
    )


def request_pr_review(
    registry: dict[str, Any],
    pr_number: int,
    pr_title: str,
    task_issue: int,
    submitting_agent: str,
) -> bool:
    """Request PR review from integrator."""

    # Find integrator
    integrator_address = None
    for agent in registry.get("shared_agents", []):
        if agent["role"] == "integrator":
            integrator_address = agent["ai_maestro_address"]
            break

    if not integrator_address:
        print("Integrator not found in registry", file=sys.stderr)
        return False

    team_name = registry.get("team", {}).get("name", "unknown-team")
    repo_url = registry.get("team", {}).get("project", {}).get("repository", "")

    content = {
        "type": "pr-review-request",
        "message": f"Please review PR #{pr_number}: {pr_title}",
        "pull_request": {
            "number": pr_number,
            "url": f"{repo_url}/pull/{pr_number}",
            "title": pr_title,
            "related_issue": task_issue,
        },
        "submitting_agent": submitting_agent,
        "sender_identity": {
            "name": "amoa-orchestrator",
            "role": "orchestrator",
            "plugin": "ai-maestro-orchestrator-agent",
            "team": team_name,
        },
        "instructions": "Review the PR for compliance with task requirements. Run tests. Merge if approved, reject with detailed feedback if not.",
    }

    return send_ai_maestro_message(
        to=integrator_address,
        subject=f"[PR REVIEW] #{pr_number}: {pr_title}",
        content=content,
        priority="high",
    )


def report_to_manager(message_type: str, message: str, details: dict[str, Any]) -> bool:
    """Report to the manager (AMAMA)."""

    content = {
        "type": message_type,
        "message": message,
        "details": details,
        "sender_identity": {
            "name": "amoa-orchestrator",
            "role": "orchestrator",
            "plugin": "ai-maestro-orchestrator-agent",
        },
    }

    return send_ai_maestro_message(
        to="amama-assistant-manager",
        subject=f"[{message_type.upper()}] {message[:50]}...",
        content=content,
        priority="normal",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AMOA Kanban Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create task
    create_parser = subparsers.add_parser("create-task", help="Create a new task")
    create_parser.add_argument("--title", required=True, help="Task title")
    create_parser.add_argument("--body", required=True, help="Task description")
    create_parser.add_argument("--agent", required=True, help="Agent to assign")
    create_parser.add_argument("--priority", default="normal", help="Priority level")
    create_parser.add_argument(
        "--blocked-by", type=int, nargs="*", help="Blocking issues"
    )
    create_parser.add_argument("--requirements-doc", help="Path to requirements doc")
    create_parser.add_argument("--notify", action="store_true", help="Notify agent")

    # Assign task
    assign_parser = subparsers.add_parser("assign-task", help="Assign task to agent")
    assign_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    assign_parser.add_argument("--agent", required=True, help="Agent name")
    assign_parser.add_argument("--notify", action="store_true", help="Notify agent")

    # Update status
    status_parser = subparsers.add_parser("update-status", help="Update task status")
    status_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    # Legacy values stay accepted (update_task_status migrates them) so existing
    # callers and scripts do not break on the vocabulary change; the resolved
    # ratified column is what gets written.
    status_parser.add_argument(
        "--status", required=True, choices=list(STATUS_LABEL_VOCAB)
    )

    # Set dependency
    dep_parser = subparsers.add_parser("set-dependency", help="Set task dependency")
    dep_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    dep_parser.add_argument(
        "--blocked-by", type=int, nargs="+", required=True, help="Blocking issues"
    )

    # Check ready tasks
    ready_parser = subparsers.add_parser(
        "check-ready-tasks", help="Check tasks ready for work"
    )
    ready_parser.add_argument(
        "--notify", action="store_true", help="Notify agents of ready tasks"
    )

    # Notify agent
    notify_parser = subparsers.add_parser(
        "notify-agent", help="Notify agent about task"
    )
    notify_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    notify_parser.add_argument("--agent", required=True, help="Agent name")

    # Request PR review
    pr_parser = subparsers.add_parser(
        "request-pr-review", help="Request PR review from integrator"
    )
    pr_parser.add_argument("--pr", type=int, required=True, help="PR number")
    pr_parser.add_argument("--title", required=True, help="PR title")
    pr_parser.add_argument(
        "--issue", type=int, required=True, help="Related issue number"
    )
    pr_parser.add_argument("--agent", required=True, help="Submitting agent")

    # Full sync with AI Maestro
    sync_parser_am = subparsers.add_parser("sync-to-aimaestro", help="Full sync GitHub→AI Maestro")
    sync_parser_am.add_argument("--team-id", default=TEAM_ID, help="AI Maestro team ID")

    args = parser.parse_args()

    # Pre-flight check: verify gh auth has project scopes
    if not check_gh_project_scopes():
        return 1

    # Load team registry
    try:
        registry = load_team_registry()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "create-task":
            requirements_doc = None
            if args.requirements_doc:
                with open(args.requirements_doc, encoding="utf-8") as f:
                    requirements_doc = f.read()

            result = create_task_issue(
                title=args.title,
                body=args.body,
                assigned_agent=args.agent,
                priority=args.priority,
                dependencies=args.blocked_by,
                task_requirements_doc=requirements_doc,
            )

            if result:
                print(f"Created task: #{result['number']} - {result['url']}")

                if args.notify:
                    notify_agent_of_task(
                        registry,
                        result["number"],
                        args.agent,
                        args.title,
                        requirements_doc,
                    )
                    print(f"Notified agent: {args.agent}")

                return 0
            return 1

        elif args.command == "assign-task":
            if assign_task_to_agent(args.issue, args.agent):
                print(f"Assigned #{args.issue} to {args.agent}")

                if args.notify:
                    # Get issue title
                    rc, stdout, _ = run_gh_command(
                        [
                            "issue",
                            "view",
                            str(args.issue),
                            "--repo",
                            f"{GITHUB_OWNER}/{GITHUB_REPO}",
                            "--json",
                            "title",
                        ]
                    )
                    title = (
                        json.loads(stdout).get("title", "Unknown")
                        if rc == 0
                        else "Unknown"
                    )

                    notify_agent_of_task(registry, args.issue, args.agent, title)
                    print(f"Notified agent: {args.agent}")

                return 0
            return 1

        elif args.command == "update-status":
            if update_task_status(args.issue, args.status):
                # Report the RESOLVED column, not the raw arg: telling the user
                # "status to done" while the label says `status:complete` is how
                # a vocabulary split gets papered over. resolve_column cannot
                # raise here — update_task_status already accepted the value.
                column = resolve_column(args.status)
                print(f"Updated #{args.issue} status to {column}")
                # Terminal column -> close the issue safely (guards against the
                # board's own Done-column auto-close). `done`/`completed` are the
                # legacy spellings that migrate to `complete`.
                if column == "complete":
                    close_issue_safely(args.issue)
                return 0
            return 1

        elif args.command == "set-dependency":
            if set_task_dependency(args.issue, args.blocked_by):
                print(f"Set #{args.issue} blocked by {args.blocked_by}")
                return 0
            return 1

        elif args.command == "check-ready-tasks":
            ready_tasks = get_ready_tasks(registry)
            print(f"Found {len(ready_tasks)} ready tasks:")
            for task in ready_tasks:
                print(
                    f"  #{task['number']}: {task['title']} -> {task['assigned_agent']}"
                )

                if args.notify:
                    notify_agent_of_task(
                        registry, task["number"], task["assigned_agent"], task["title"]
                    )
                    print(f"    Notified {task['assigned_agent']}")

            return 0

        elif args.command == "notify-agent":
            # Get issue title
            rc, stdout, _ = run_gh_command(
                [
                    "issue",
                    "view",
                    str(args.issue),
                    "--repo",
                    f"{GITHUB_OWNER}/{GITHUB_REPO}",
                    "--json",
                    "title",
                ]
            )
            title = json.loads(stdout).get("title", "Unknown") if rc == 0 else "Unknown"

            if notify_agent_of_task(registry, args.issue, args.agent, title):
                print(f"Notified {args.agent} about #{args.issue}")
                return 0
            return 1

        elif args.command == "request-pr-review":
            if request_pr_review(registry, args.pr, args.title, args.issue, args.agent):
                print(f"Requested PR review for #{args.pr}")
                return 0
            return 1

        elif args.command == "sync-to-aimaestro":
            team_id = getattr(args, "team_id", TEAM_ID)
            if not team_id:
                print("ERROR: --team-id or AIMAESTRO_TEAM_ID required", file=sys.stderr)
                return 1
            counts = bulk_sync(team_id)
            notify_sync_result(team_id, counts)
            print(json.dumps(counts, indent=2))
            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
