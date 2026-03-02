#!/usr/bin/env python3
"""
EOA Notify Agent -- Send AI Maestro Message to a Specific Agent

Sends an arbitrary message to a specific agent via the AI Maestro messaging
API. This is a general-purpose notification utility, unlike the poll-specific
scripts (eoa_poll_agent.py, eoa_check_remote_agents.py).

NO external dependencies -- Python 3.8+ stdlib only.
Uses curl subprocess to send HTTP requests to the AI Maestro API.

Usage:
    python3 eoa_notify_agent.py AGENT_ID --subject "Subject" --message "Body"
    python3 eoa_notify_agent.py AGENT_ID --subject "Task Update" --message "Module X complete" --priority high
    python3 eoa_notify_agent.py AGENT_ID --subject "Question" --message "Need clarification" --type request

Exit codes:
    0 - Message sent successfully
    1 - Error (network failure, invalid arguments, API error, etc.)

Examples:
    # Send a normal-priority info message:
    python3 eoa_notify_agent.py implementer-1 \
        --subject "Module assignment" \
        --message "You have been assigned module auth-login"

    # Send a high-priority request:
    python3 eoa_notify_agent.py ecos-chief-of-staff-one \
        --subject "Agent replacement needed" \
        --message "implementer-3 is unresponsive, requesting replacement" \
        --priority high --type request

    # Send an urgent status update:
    python3 eoa_notify_agent.py eama-main-manager \
        --subject "Orchestration complete" \
        --message "All modules verified, ready for user review" \
        --priority urgent --type status
"""

import argparse
import json
import os
import subprocess
import sys


# Default AI Maestro API base URL
DEFAULT_API_URL = "http://localhost:23000"


def get_api_url() -> str:
    """Get the AI Maestro API base URL from environment or default.

    Reads the AIMAESTRO_API environment variable. Falls back to
    http://localhost:23000 if not set.

    Returns:
        The base URL string (without trailing slash).
    """
    url = os.environ.get("AIMAESTRO_API", DEFAULT_API_URL)
    # Remove trailing slash if present
    return url.rstrip("/")


def send_message(
    agent_id: str,
    subject: str,
    message: str,
    priority: str,
    message_type: str,
) -> tuple[bool, str]:
    """Send a message to an agent via the AI Maestro API using curl.

    Args:
        agent_id: The target agent identifier (full session name).
        subject: The message subject line.
        message: The message body text.
        priority: Message priority: "normal", "high", or "urgent".
        message_type: Message content type: "request", "info", or "status".

    Returns:
        Tuple of (success, detail_message).
        success is True if the API returned a successful response.
        detail_message contains the API response or error description.
    """
    api_url = get_api_url()
    endpoint = "{}/api/messages".format(api_url)

    # Build the JSON payload
    payload = {
        "to": agent_id,
        "subject": subject,
        "priority": priority,
        "content": {
            "type": message_type,
            "message": message,
        },
    }

    payload_json = json.dumps(payload)

    try:
        result = subprocess.run(
            [
                "curl",
                "-s",          # Silent mode (no progress bar)
                "-S",          # Show errors even in silent mode
                "-X", "POST",
                endpoint,
                "-H", "Content-Type: application/json",
                "-d", payload_json,
                "-w", "\n%{http_code}",  # Append HTTP status code on new line
                "--connect-timeout", "10",
                "--max-time", "30",
            ],
            capture_output=True,
            text=True,
            timeout=45,
        )
    except FileNotFoundError:
        return False, "curl command not found -- install curl to use this script"
    except subprocess.TimeoutExpired:
        return False, "Request timed out after 45 seconds"

    if result.returncode != 0:
        stderr_text = result.stderr.strip()
        return False, "curl failed with exit code {}: {}".format(
            result.returncode, stderr_text
        )

    # Parse response: body lines + last line is HTTP status code
    output_lines = result.stdout.strip().split("\n")
    if len(output_lines) < 1:
        return False, "Empty response from API"

    http_code = output_lines[-1].strip()
    response_body = "\n".join(output_lines[:-1]).strip()

    # Check HTTP status code
    try:
        status_int = int(http_code)
    except ValueError:
        return False, "Could not parse HTTP status code: {}".format(http_code)

    if 200 <= status_int < 300:
        return True, "Message sent (HTTP {}): {}".format(status_int, response_body)
    else:
        return False, "API returned HTTP {}: {}".format(status_int, response_body)


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
        help="Target agent identifier (full session name, e.g. 'implementer-1' or 'ecos-chief-of-staff-one')",
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
