#!/usr/bin/env python3
"""
utils.py - Utility functions for Orchestrator Agent stop check hook.

This module contains shared configuration constants and utility functions
used by the orchestrator stop check hook and related scripts.

Functions:
    - ensure_claude_dir: Ensure .claude directory exists
    - rotate_log_if_needed: Rotate log file if too large
    - log, debug, info, warn, error, critical: Logging functions
    - safe_json_field: Safe JSON field extraction
    - retry_command: Execute command with retries
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import NoReturn, Optional


# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

# State file locations (in .claude directory, gitignored)
ORCHESTRATOR_STATE_FILE = ".claude/orchestrator-loop.local.md"
RALPH_STATE_FILE = ".claude/ralph-loop.local.md"  # Ralph Wiggum's state file

# Two-Phase Mode state files
PLAN_PHASE_STATE_FILE = ".claude/orchestrator-plan-phase.local.md"
EXEC_PHASE_STATE_FILE = ".claude/orchestrator-exec-phase.local.md"

# Lock file to prevent concurrent execution
LOCK_FILE = ".claude/orchestrator-hook.lock"

# Log file for debugging (rotated when exceeds 100KB)
LOG_FILE = ".claude/orchestrator-hook.log"
LOG_MAX_SIZE = 102400  # 100KB

# Debug mode (set ORCHESTRATOR_DEBUG=1 to enable)
DEBUG = os.environ.get("ORCHESTRATOR_DEBUG", "0") == "1"

# Recursion guard marker
RECURSION_MARKER = os.environ.get("ORCHESTRATOR_RECURSION_GUARD", "")

# Retry configuration for transient failures
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


# ==============================================================================
# DIRECTORY UTILITIES
# ==============================================================================


def ensure_claude_dir() -> bool:
    """Ensure .claude directory exists with proper error handling.

    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        Path(".claude").mkdir(exist_ok=True)
        return True
    except OSError:
        print("CRITICAL: Cannot create .claude directory", file=sys.stderr)
        return False


# ==============================================================================
# LOGGING FUNCTIONS
# ==============================================================================


def rotate_log_if_needed() -> None:
    """Rotate log if too large (with error handling)."""
    log_path = Path(LOG_FILE)
    if not log_path.exists():
        return

    try:
        size = log_path.stat().st_size
        if size > LOG_MAX_SIZE:
            try:
                log_path.rename(f"{LOG_FILE}.old")
            except OSError:
                # Log rotation failed - truncate instead
                log_path.write_text("", encoding="utf-8")
    except OSError:
        pass


def log(level: str, msg: str) -> None:
    """Log message to file with timestamp (with fallback to stderr).

    Args:
        level: Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
        msg: Message to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}\n"

    # Try to ensure .claude dir exists
    ensure_claude_dir()

    # Try to rotate log
    rotate_log_if_needed()

    # Try to write to log file, fall back to stderr on failure
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except OSError:
        # Logging to file failed - write to stderr for visibility
        print(f"[{timestamp}] [{level}] (LOG_FAIL) {msg}", file=sys.stderr)


def debug(msg: str) -> None:
    """Debug log (only if DEBUG=1).

    Args:
        msg: Debug message
    """
    if DEBUG:
        log("DEBUG", msg)


def info(msg: str) -> None:
    """Info log.

    Args:
        msg: Info message
    """
    log("INFO", msg)


def warn(msg: str) -> None:
    """Warning log (also prints to stderr).

    Args:
        msg: Warning message
    """
    log("WARN", msg)
    print(f"Orchestrator Hook Warning: {msg}", file=sys.stderr)


def error(msg: str) -> None:
    """Error log (also prints to stderr).

    Args:
        msg: Error message
    """
    log("ERROR", msg)
    print(f"Orchestrator Hook Error: {msg}", file=sys.stderr)


def critical(msg: str) -> None:
    """Critical error log (prints to stderr).

    Note: This function logs the critical error but does NOT set any global flags.
    The caller is responsible for tracking critical error state if needed.

    Args:
        msg: Critical error message
    """
    log("CRITICAL", msg)
    print(f"Orchestrator Hook CRITICAL: {msg}", file=sys.stderr)


# ==============================================================================
# JSON UTILITIES
# ==============================================================================


def safe_json_field(json_str: str, field_path: str, default: str) -> str:
    """Validate JSON and extract a field, return default on failure.

    Args:
        json_str: JSON string to parse
        field_path: jq-style field path (e.g., '.pending_count')
        default: Default value if extraction fails

    Returns:
        Extracted field value or default
    """
    if not json_str:
        debug(f"Invalid JSON for field {field_path}, using default: {default}")
        return default

    try:
        data = json.loads(json_str)
        # Simple field extraction (supports .field only, not complex paths)
        field_name = field_path.lstrip(".")
        value = data.get(field_name, default)
        return str(value) if value is not None else default
    except (json.JSONDecodeError, AttributeError):
        debug(f"JSON extraction failed for {field_path}, using default: {default}")
        return default


# ==============================================================================
# COMMAND EXECUTION UTILITIES
# ==============================================================================


def retry_command(description: str, command: list[str]) -> Optional[str]:
    """Execute a command with retries.

    Args:
        description: Human-readable description of the command
        command: Command to execute as list of arguments

    Returns:
        Command output on success, None on failure
    """
    for attempt in range(1, MAX_RETRIES + 1):
        debug(f"Attempt {attempt}/{MAX_RETRIES}: {description}")

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=30, check=True
            )
            debug(f"{description} succeeded on attempt {attempt}")
            return result.stdout
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            if attempt < MAX_RETRIES:
                debug(f"{description} failed, retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)

    warn(f"{description} failed after {MAX_RETRIES} attempts")
    return None


# ==============================================================================
# FAIL-SAFE EXIT (Prevents trapping user on unrecoverable errors)
# ==============================================================================


def fail_safe_exit(reason: str) -> NoReturn:
    """Allow exit on unrecoverable errors to prevent trapping user.

    This function is called when the hook encounters an error that cannot
    be recovered from (e.g., corrupted state file, failed reads). It logs
    the error and exits with code 0 to allow the user to exit cleanly.

    Note: This function does NOT return - it calls sys.exit(0).

    Args:
        reason: Reason for fail-safe exit
    """
    error(f"Fail-safe exit triggered: {reason}")
    info("Allowing exit to prevent user from being trapped")
    sys.exit(0)


def conservative_block_exit(reason: str) -> NoReturn:
    """Block exit when unable to reliably determine task status.

    This is used when helper scripts fail or critical errors occur during
    task checking. Rather than risk allowing exit with incomplete tasks,
    we conservatively block the exit.

    Note: This function does NOT return - it calls sys.exit(0) after printing
    a blocking JSON response.

    Args:
        reason: Reason for conservative blocking
    """
    error(f"Conservative block triggered: {reason}")

    # Build a blocking response that prompts the user to investigate
    prompt = f"""ORCHESTRATOR CONSERVATIVE BLOCK

Unable to reliably determine task completion status due to errors:
{reason}

RECOMMENDED ACTIONS:
1. Check .claude/orchestrator-hook.log for detailed error messages
2. Verify helper scripts exist and are executable:
   - Claude Code TaskList
   - eoa_check_github_projects.py
3. Manually verify task completion in all sources:
   - Claude Code Tasks
   - GitHub Project items
   - Session TODO list
4. If all tasks are truly complete, output: ALL_TASKS_COMPLETE
5. If issues persist, restart the session

The orchestrator is blocking exit to prevent premature completion with
unfinished tasks. This is a safety measure - please investigate."""

    system_msg = f"ORCHESTRATOR BLOCKED (CONSERVATIVE) | {reason}"

    output = {"decision": "block", "reason": prompt, "systemMessage": system_msg}

    print(json.dumps(output, indent=2))
    sys.exit(0)
