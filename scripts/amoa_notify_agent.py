#!/usr/bin/env python3
"""
AMOA Notify Agent -- Send AI Maestro Message to a Specific Agent

Sends an arbitrary message to a specific agent via the AI Maestro AMP wrapper
scripts. This is a general-purpose notification utility, unlike the poll-specific
scripts (amoa_poll_agent.py, amoa_check_remote_agents.py).

NO external dependencies -- Python 3.8+ stdlib only.
Uses amp-send.sh wrapper script (globally installed at ~/.local/bin/).

Usage:
    python3 amoa_notify_agent.py AGENT_ID --subject "Subject" --message "Body"
    python3 amoa_notify_agent.py AGENT_ID --subject "Task Update" --message "Module X complete" --priority high
    python3 amoa_notify_agent.py AGENT_ID --subject "Question" --message "Need clarification" --type request

Exit codes:
    0 - Message sent successfully
    1 - Error (network failure, invalid arguments, API error, etc.)

Examples:
    # Send a normal-priority info message:
    python3 amoa_notify_agent.py implementer-1 \
        --subject "Module assignment" \
        --message "You have been assigned module auth-login"

    # Send a high-priority request:
    python3 amoa_notify_agent.py amcos-chief-of-staff-one \
        --subject "Agent replacement needed" \
        --message "implementer-3 is unresponsive, requesting replacement" \
        --priority high --type request

    # Send an urgent status update:
    python3 amoa_notify_agent.py amama-main-manager \
        --subject "Orchestration complete" \
        --message "All modules verified, ready for user review" \
        --priority urgent --type status
"""

import argparse
import os
import shutil
import subprocess
import sys

# Map our message type names to amp-send.sh --type values.
# amp-send.sh accepts: request | response | notification | task | status
# This script's CLI accepts: request | info | status
# "info" maps to "notification" in amp-send.sh parlance.
_TYPE_MAP = {
    "request": "request",
    "info": "notification",
    "status": "status",
}


def _find_amp_send() -> str:
    """Locate the amp-send.sh wrapper script.

    Uses shutil.which() first (respects PATH), then falls back to the
    canonical install location at ~/.local/bin/amp-send.sh.

    Returns:
        Absolute path to amp-send.sh.

    Raises:
        FileNotFoundError: If amp-send.sh cannot be found anywhere.
    """
    # Try PATH first
    path = shutil.which("amp-send.sh")
    if path:
        return path

    # Fallback to canonical location
    fallback = os.path.expanduser("~/.local/bin/amp-send.sh")
    if os.path.isfile(fallback) and os.access(fallback, os.X_OK):
        return fallback

    raise FileNotFoundError(
        "amp-send.sh not found on PATH or at ~/.local/bin/amp-send.sh -- "
        "ensure AI Maestro AMP scripts are installed"
    )


def send_message(
    agent_id: str,
    subject: str,
    message: str,
    priority: str,
    message_type: str,
) -> tuple:
    """Send a message to an agent via the amp-send.sh AMP wrapper script.

    Args:
        agent_id: The target agent identifier (full session name).
        subject: The message subject line.
        message: The message body text.
        priority: Message priority: "normal", "high", or "urgent".
        message_type: Message content type: "request", "info", or "status".

    Returns:
        Tuple of (success, detail_message).
        success is True if amp-send.sh exited with code 0.
        detail_message contains the script output or error description.
    """
    # Resolve amp-send.sh location
    try:
        amp_send_path = _find_amp_send()
    except FileNotFoundError as exc:
        return False, str(exc)

    # Map message_type to amp-send.sh --type value
    amp_type = _TYPE_MAP.get(message_type, "notification")

    # Build the command: amp-send <recipient> <subject> <message> [options]
    cmd = [
        amp_send_path,
        agent_id,
        subject,
        message,
        "--priority", priority,
        "--type", amp_type,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45,
        )
    except subprocess.TimeoutExpired:
        return False, "amp-send.sh timed out after 45 seconds"

    stdout_text = result.stdout.strip()
    stderr_text = result.stderr.strip()

    if result.returncode == 0:
        # Success -- return whatever amp-send.sh printed
        detail = stdout_text if stdout_text else "Message sent successfully"
        return True, detail
    else:
        # Failure -- combine stderr and stdout for diagnostics
        parts = []
        if stderr_text:
            parts.append(stderr_text)
        if stdout_text:
            parts.append(stdout_text)
        error_detail = " | ".join(parts) if parts else "Unknown error"
        return False, "amp-send.sh failed (exit {}): {}".format(
            result.returncode, error_detail
        )


def main() -> int:
    """Main entry point for agent notification.

    Parses arguments, sends the message, and returns the appropriate exit code.

    Returns:
        0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(
        description="Send AI Maestro message to a specific agent"
    )
    parser.add_argument(
        "agent_id",
        help="Target agent identifier (full session name, e.g. 'implementer-1' or 'amcos-chief-of-staff-one')",
    )
    parser.add_argument(
        "--subject",
        required=True,
        help="Message subject line",
    )
    parser.add_argument(
        "--message",
        required=True,
        help="Message body text",
    )
    parser.add_argument(
        "--priority",
        choices=["normal", "high", "urgent"],
        default="normal",
        help="Message priority (default: normal)",
    )
    parser.add_argument(
        "--type",
        dest="message_type",
        choices=["request", "info", "status"],
        default="info",
        help="Message content type (default: info)",
    )
    args = parser.parse_args()

    # Validate inputs are non-empty
    if not args.agent_id.strip():
        print("ERROR: agent_id must not be empty", file=sys.stderr)
        return 1
    if not args.subject.strip():
        print("ERROR: --subject must not be empty", file=sys.stderr)
        return 1
    if not args.message.strip():
        print("ERROR: --message must not be empty", file=sys.stderr)
        return 1

    # Send the message
    success, detail = send_message(
        agent_id=args.agent_id.strip(),
        subject=args.subject.strip(),
        message=args.message.strip(),
        priority=args.priority,
        message_type=args.message_type,
    )

    if success:
        print(detail)
        return 0
    else:
        print("ERROR: {}".format(detail), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
