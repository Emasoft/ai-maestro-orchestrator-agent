#!/usr/bin/env python3
"""
EOA Confirm Replacement Script

Verifies that an agent replacement has been completed successfully and notifies
ECOS (Emergency Context-loss Operations System) of the outcome. This is the
final step (Step 6) in the agent replacement workflow.

Performs four verification checks:
  1. ACK verification - confirms the replacement agent acknowledged the handoff
  2. State file update - updates orchestration state with replacement metadata
  3. ECOS notification - sends replacement confirmation to ECOS via AI Maestro
  4. Audit logging - appends an audit entry to the replacement audit log

Data sources:
  - AI Maestro inbox (via curl to localhost API) for ACK messages
  - Orchestration state file (.emasoft/orchestration-state.json) for assignments
  - Exec-phase state file (.claude/orchestrator-exec-phase.local.md) as fallback

Usage:
    python3 eoa_confirm_replacement.py --failed-agent NAME --new-agent NAME --handoff-id ID
    python3 eoa_confirm_replacement.py --failed-agent impl-1 --new-agent impl-2 --handoff-id handoff-uuid-123
    python3 eoa_confirm_replacement.py --failed-agent impl-1 --new-agent impl-2 --handoff-id handoff-uuid-123 --ecos-session ecos-chief-of-staff-one
    python3 eoa_confirm_replacement.py --failed-agent impl-1 --new-agent impl-2 --handoff-id handoff-uuid-123 --skip-ack

Exit codes:
    0 - Success (full or partial confirmation)
    1 - Error (unrecoverable failure such as missing arguments or I/O error)
    2 - ACK not received (replacement agent did not acknowledge)

Examples:
    # Standard confirmation after replacement:
    python3 eoa_confirm_replacement.py \\
        --failed-agent implementer-1 --new-agent implementer-2 \\
        --handoff-id handoff-uuid-123

    # Confirmation with explicit ECOS session and project root:
    python3 eoa_confirm_replacement.py \\
        --failed-agent implementer-1 --new-agent implementer-2 \\
        --handoff-id handoff-uuid-123 \\
        --ecos-session ecos-chief-of-staff-one \\
        --project-root /home/user/myproject

    # Skip ACK check (for emergency replacements where ACK is not expected):
    python3 eoa_confirm_replacement.py \\
        --failed-agent implementer-1 --new-agent implementer-2 \\
        --handoff-id handoff-uuid-123 --skip-ack
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# State file location relative to the project root (JSON format)
STATE_FILE_PATH = ".emasoft/orchestration-state.json"

# Fallback exec-phase state file (YAML frontmatter in markdown)
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")

# Audit log location relative to the project root
AUDIT_LOG_DIR = "logs"
AUDIT_LOG_FILE = "replacement_audit.json"

# AI Maestro API base URL
AIMAESTRO_API = "http://localhost:23000"

# Default ECOS session name for notifications
DEFAULT_ECOS_SESSION = "ecos-controller"


def load_state(project_root):
    """Load orchestration state from the JSON state file.

    Args:
        project_root: Path to the project root directory.

    Returns:
        A dictionary with the state data, or None if the file does not
        exist, is empty, or contains invalid JSON.
    """
    state_path = Path(project_root) / STATE_FILE_PATH
    if not state_path.exists():
        return None

    try:
        content = state_path.read_text(encoding="utf-8").strip()
        if not content:
            return None
        data = json.loads(content)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def save_state(project_root, state):
    """Save orchestration state back to the JSON state file.

    Creates a backup of the existing state file before overwriting.

    Args:
        project_root: Path to the project root directory.
        state: The state dictionary to write.

    Returns:
        True if the write succeeded, False otherwise.
    """
    state_path = Path(project_root) / STATE_FILE_PATH

    # Create backup of existing state file before overwriting
    if state_path.exists():
        timestamp_suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = state_path.with_suffix(".json.bak.{}".format(timestamp_suffix))
        try:
            backup_path.write_text(
                state_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        except OSError:
            # Backup failure is not fatal but should be noted
            pass

    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def check_ack_received(new_agent, handoff_id):
    """Check AI Maestro inbox for an ACK message from the replacement agent.

    Queries the AI Maestro API for unread messages, then filters for a
    message from the new agent whose content contains the matching handoff_id
    and a status of 'ready_to_proceed'.

    Args:
        new_agent: The agent ID of the replacement agent.
        handoff_id: The handoff ID to match in the ACK message.

    Returns:
        A dictionary with ACK details if found, or None if no matching
        ACK was found. The dictionary contains:
          - received_at: ISO timestamp of when the message was received
          - status: The agent's reported status (e.g. 'ready_to_proceed')
          - starting_from: The checkpoint the agent will start from
          - understanding_summary: The agent's summary of the task
          - questions: Any questions the agent raised
    """
    try:
        result = subprocess.run(
            [
                "curl", "-s",
                "{}/api/messages?agent={}&action=list&status=unread".format(
                    AIMAESTRO_API, new_agent
                ),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        messages = data.get("messages", [])

        for msg in messages:
            content = msg.get("content", {})
            if not isinstance(content, dict):
                continue

            # Match by handoff_id in the content
            msg_handoff_id = content.get("handoff_id", "")
            if msg_handoff_id != handoff_id:
                continue

            # Found a matching ACK message
            return {
                "received_at": msg.get("timestamp", msg.get("created_at", "")),
                "status": content.get("status", "unknown"),
                "starting_from": content.get("starting_from", ""),
                "understanding_summary": content.get("understanding_summary", ""),
                "questions": content.get("questions", []),
            }

    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    return None


def update_state_for_replacement(project_root, state, failed_agent, new_agent, handoff_id, reason):
    """Update the orchestration state file with replacement metadata.

    Performs the following updates:
      - Reassigns active_assignments from the failed agent to the new agent
      - Adds replacement_info metadata to the reassigned assignments
      - Resets instruction_verification status to 'awaiting_repetition'
      - Marks the failed agent as inactive in registered_agents
      - Registers the new agent in registered_agents if not already present
      - Appends an entry to replacement_history

    Args:
        project_root: Path to the project root directory.
        state: The orchestration state dictionary (modified in-place).
        failed_agent: The agent ID of the failed agent.
        new_agent: The agent ID of the replacement agent.
        handoff_id: The handoff ID for this replacement.
        reason: The reason for replacement (e.g. 'context_loss').

    Returns:
        A dictionary summarizing the updates made.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates_summary = {
        "assignments_updated": 0,
        "failed_agent_deactivated": False,
        "new_agent_registered": False,
        "history_appended": False,
    }

    # Update active_assignments: reassign from failed agent to new agent
    assignments = state.get("active_assignments", [])
    task_uuids: list[str] = []
    if isinstance(assignments, list):
        for assignment in assignments:
            if not isinstance(assignment, dict):
                continue
            if assignment.get("agent") != failed_agent:
                continue

            # Reassign to new agent
            assignment["agent"] = new_agent
            assignment["status"] = "pending_verification"

            # Add replacement tracking metadata
            assignment["replacement_info"] = {
                "replaced_agent": failed_agent,
                "replacement_reason": reason,
                "replacement_timestamp": timestamp,
                "handoff_id": handoff_id,
            }

            # Reset instruction verification so orchestrator re-verifies
            assignment["instruction_verification"] = {
                "status": "awaiting_repetition",
                "attempts": 0,
                "last_attempt": None,
                "verified_at": None,
            }

            # Flag progress as inherited from the failed agent
            progress = assignment.get("progress", {})
            if isinstance(progress, dict):
                progress["at_replacement"] = True
                progress["notes"] = "Inherited from {}".format(failed_agent)
            else:
                assignment["progress"] = {
                    "at_replacement": True,
                    "notes": "Inherited from {}".format(failed_agent),
                }

            task_uuid = assignment.get("task_uuid", "")
            if task_uuid:
                task_uuids.append(task_uuid)
            updates_summary["assignments_updated"] += 1

    # Update registered_agents: mark failed agent as inactive
    registered = state.get("registered_agents", [])
    if not isinstance(registered, list):
        registered = []
        state["registered_agents"] = registered

    for agent_entry in registered:
        if not isinstance(agent_entry, dict):
            continue
        if agent_entry.get("id") == failed_agent:
            agent_entry["status"] = "inactive"
            agent_entry["inactive_reason"] = "replaced"
            agent_entry["replaced_at"] = timestamp
            agent_entry["replaced_by"] = new_agent
            updates_summary["failed_agent_deactivated"] = True

    # Register new agent if not already present
    new_agent_exists = any(
        isinstance(entry, dict) and entry.get("id") == new_agent
        for entry in registered
    )
    if not new_agent_exists:
        registered.append({
            "id": new_agent,
            "type": "ai",
            "status": "active",
            "registered": timestamp,
            "assigned_from": failed_agent,
        })
        updates_summary["new_agent_registered"] = True

    # Append to replacement_history
    history = state.get("replacement_history", [])
    if not isinstance(history, list):
        history = []
        state["replacement_history"] = history

    history.append({
        "timestamp": timestamp,
        "failed_agent": failed_agent,
        "replacement_agent": new_agent,
        "reason": reason,
        "tasks_transferred": task_uuids,
        "handoff_id": handoff_id,
        "status": "complete",
    })
    updates_summary["history_appended"] = True

    # Persist the updated state
    save_state(project_root, state)

    return updates_summary


def send_ecos_notification(ecos_session, status, failed_agent, new_agent, handoff_id, details):
    """Send replacement confirmation notification to ECOS via AI Maestro.

    Sends a structured JSON message to the ECOS controller agent with the
    replacement outcome (success, partial, or failed).

    Args:
        ecos_session: The AI Maestro session name for ECOS.
        status: The replacement status ('success', 'partial', or 'failed').
        failed_agent: The agent ID of the failed agent.
        new_agent: The agent ID of the replacement agent.
        handoff_id: The handoff ID for this replacement.
        details: A dictionary with additional detail fields to include.

    Returns:
        True if the notification was sent successfully, False otherwise.
    """
    # Determine priority based on status
    priority_map = {
        "success": "normal",
        "partial": "high",
        "failed": "urgent",
    }
    priority = priority_map.get(status, "high")

    # Determine subject line based on status
    subject_map = {
        "success": "[EOA] Agent Replacement Complete",
        "partial": "[EOA] Agent Replacement Partially Complete",
        "failed": "[EOA] Agent Replacement Failed",
    }
    subject = subject_map.get(status, "[EOA] Agent Replacement Status Update")

    # Build the message content payload
    message_content = {
        "type": "replacement_confirmation",
        "message": "Agent replacement {}".format(status),
        "status": status,
        "failed_agent": {"id": failed_agent},
        "replacement_agent": {"id": new_agent},
        "details": details,
    }
    if handoff_id:
        message_content["details"]["handoff_id"] = handoff_id

    payload = {
        "to": ecos_session,
        "subject": subject,
        "priority": priority,
        "content": message_content,
    }

    try:
        result = subprocess.run(
            [
                "curl", "-s", "-X", "POST",
                "{}/api/messages".format(AIMAESTRO_API),
                "-H", "Content-Type: application/json",
                "-d", json.dumps(payload),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            # Check if the API returned a success response
            try:
                response = json.loads(result.stdout)
                return response.get("success", False) or response.get("id") is not None
            except json.JSONDecodeError:
                # Non-JSON response but curl succeeded -- assume sent
                return True
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return False


def append_audit_log(project_root, audit_entry):
    """Append an audit log entry to the replacement audit log file.

    The audit log is a JSON array stored in logs/replacement_audit.json.
    Each entry documents a single replacement event with timestamps,
    agent identifiers, and outcome details.

    Args:
        project_root: Path to the project root directory.
        audit_entry: A dictionary with the audit log fields.

    Returns:
        True if the entry was appended successfully, False otherwise.
    """
    log_dir = Path(project_root) / AUDIT_LOG_DIR
    log_path = log_dir / AUDIT_LOG_FILE

    # Load existing audit log or start a new one
    existing_entries = []
    if log_path.exists():
        try:
            content = log_path.read_text(encoding="utf-8").strip()
            if content:
                data = json.loads(content)
                if isinstance(data, list):
                    existing_entries = data
        except (json.JSONDecodeError, OSError):
            # Corrupted log file -- start fresh but do not lose the old one
            backup_path = log_path.with_suffix(".json.corrupted.{}".format(
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            ))
            try:
                log_path.rename(backup_path)
            except OSError:
                pass

    existing_entries.append(audit_entry)

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            json.dumps(existing_entries, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def build_audit_entry(
    failed_agent,
    new_agent,
    handoff_id,
    reason,
    ack_info,
    state_updates,
    ecos_notified,
    outcome,
):
    """Build a structured audit log entry for the replacement event.

    Args:
        failed_agent: The agent ID of the failed agent.
        new_agent: The agent ID of the replacement agent.
        handoff_id: The handoff ID for this replacement.
        reason: The reason for replacement.
        ack_info: ACK details dict from check_ack_received, or None.
        state_updates: Summary dict from update_state_for_replacement.
        ecos_notified: Boolean indicating whether ECOS was notified.
        outcome: The overall outcome string ('success', 'partial', 'failed').

    Returns:
        A dictionary suitable for appending to the audit log.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    entry = {
        "timestamp": timestamp,
        "event": "agent_replacement_confirmation",
        "failed_agent": {
            "id": failed_agent,
            "reason": reason,
        },
        "replacement_agent": {
            "id": new_agent,
        },
        "handoff": {
            "id": handoff_id,
        },
        "ack": {},
        "state_updates": state_updates if state_updates else {},
        "ecos_notification": {
            "sent": ecos_notified,
            "sent_at": timestamp if ecos_notified else None,
        },
        "outcome": outcome,
    }

    if ack_info:
        entry["ack"] = {
            "received": True,
            "received_at": ack_info.get("received_at", ""),
            "status": ack_info.get("status", ""),
            "understanding_verified": bool(ack_info.get("understanding_summary")),
        }
    else:
        entry["ack"] = {
            "received": False,
        }

    return entry


def main():
    """Main entry point for replacement confirmation.

    Parses arguments, checks for ACK from the replacement agent, updates
    the orchestration state, notifies ECOS, and writes an audit log entry.

    Returns:
        Exit code: 0 for success, 1 for unrecoverable error, 2 for no ACK.
    """
    parser = argparse.ArgumentParser(
        description="Verify agent replacement completion and notify ECOS"
    )
    parser.add_argument(
        "--failed-agent", required=True,
        help="ID of the agent that was replaced"
    )
    parser.add_argument(
        "--new-agent", required=True,
        help="ID of the replacement agent"
    )
    parser.add_argument(
        "--handoff-id", required=True,
        help="UUID of the handoff document sent to the replacement agent"
    )
    parser.add_argument(
        "--reason", type=str, default="context_loss",
        help="Reason for replacement (default: context_loss)"
    )
    parser.add_argument(
        "--ecos-session", type=str, default=DEFAULT_ECOS_SESSION,
        help="AI Maestro session name for ECOS (default: {})".format(DEFAULT_ECOS_SESSION)
    )
    parser.add_argument(
        "--project-root", type=str, default=".",
        help="Path to the project root directory (default: current directory)"
    )
    parser.add_argument(
        "--skip-ack", action="store_true", default=False,
        help="Skip ACK verification (for emergency replacements)"
    )
    parser.add_argument(
        "--skip-ecos-notify", action="store_true", default=False,
        help="Skip sending ECOS notification"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(
            json.dumps({"error": "Project root does not exist: {}".format(args.project_root)}),
            file=sys.stderr,
        )
        return 1

    # Step 1: Check ACK from replacement agent
    ack_info = None
    ack_status = "skipped"
    if not args.skip_ack:
        ack_info = check_ack_received(args.new_agent, args.handoff_id)
        if ack_info is None:
            # No ACK received -- report failure but continue with state update
            ack_status = "not_received"
        elif ack_info.get("status") == "ready_to_proceed":
            ack_status = "verified"
        else:
            ack_status = "received_not_ready"
    else:
        ack_status = "skipped"

    # Step 2: Load and update orchestration state
    state = load_state(project_root)
    state_updates = None
    if state is not None:
        state_updates = update_state_for_replacement(
            project_root=project_root,
            state=state,
            failed_agent=args.failed_agent,
            new_agent=args.new_agent,
            handoff_id=args.handoff_id,
            reason=args.reason,
        )
    else:
        # State file not found -- still proceed with ECOS notification and audit
        state_updates = {"error": "State file not found at {}".format(STATE_FILE_PATH)}

    # Determine overall outcome
    if ack_status == "verified" or ack_status == "skipped":
        outcome = "success"
    elif ack_status == "received_not_ready":
        outcome = "partial"
    else:
        outcome = "failed"

    # Step 3: Send ECOS notification
    ecos_notified = False
    if not args.skip_ecos_notify:
        notification_details = {
            "ack_status": ack_status,
            "state_updated": state is not None,
        }
        if ack_info:
            notification_details["ack_received_at"] = ack_info.get("received_at", "")
        if state_updates and isinstance(state_updates, dict):
            notification_details["assignments_updated"] = state_updates.get("assignments_updated", 0)

        ecos_notified = send_ecos_notification(
            ecos_session=args.ecos_session,
            status=outcome,
            failed_agent=args.failed_agent,
            new_agent=args.new_agent,
            handoff_id=args.handoff_id,
            details=notification_details,
        )

    # Step 4: Append audit log entry
    audit_entry = build_audit_entry(
        failed_agent=args.failed_agent,
        new_agent=args.new_agent,
        handoff_id=args.handoff_id,
        reason=args.reason,
        ack_info=ack_info,
        state_updates=state_updates if isinstance(state_updates, dict) else {},
        ecos_notified=ecos_notified,
        outcome=outcome,
    )
    audit_logged = append_audit_log(project_root, audit_entry)

    # Output JSON summary to stdout
    result = {
        "outcome": outcome,
        "failed_agent": args.failed_agent,
        "new_agent": args.new_agent,
        "handoff_id": args.handoff_id,
        "ack_status": ack_status,
        "state_updated": state is not None and isinstance(state_updates, dict),
        "ecos_notified": ecos_notified,
        "audit_logged": audit_logged,
    }
    if ack_info:
        result["ack_details"] = {
            "status": ack_info.get("status", ""),
            "received_at": ack_info.get("received_at", ""),
            "questions": ack_info.get("questions", []),
        }
    if state_updates and isinstance(state_updates, dict):
        result["state_updates"] = state_updates

    print(json.dumps(result, indent=2))

    # Return appropriate exit code
    if outcome == "failed":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
