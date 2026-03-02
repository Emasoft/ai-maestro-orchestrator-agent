"""
lock.py - Lock file management for orchestrator stop hook.

Provides:
- Lock file configuration
- PID liveness checking
- Lock acquisition with stale lock detection
- Lock release functionality
"""
# mypy: disable-error-code="import-not-found"

import os
import time
from pathlib import Path

from .utils import debug, warn, ensure_claude_dir


# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Lock file to prevent concurrent execution
LOCK_FILE = ".claude/orchestrator-hook.lock"


# ==============================================================================
# PID LIVENESS CHECK
# ==============================================================================


def is_pid_alive(pid: int) -> bool:
    """Check if a process is still running.

    Args:
        pid: Process ID to check

    Returns:
        True if process exists, False otherwise
    """
    if not isinstance(pid, int) or pid <= 0:
        return False

    try:
        # kill with signal 0 doesn't actually kill, just checks existence
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


# ==============================================================================
# LOCK ACQUISITION
# ==============================================================================


def acquire_lock() -> bool:
    """Acquire lock with PID liveness checking.

    Returns:
        True if lock acquired, False otherwise
    """
    if not ensure_claude_dir():
        warn("Cannot create .claude directory for lock file")
        return False

    lock_path = Path(LOCK_FILE)

    if lock_path.exists():
        try:
            lock_pid_str = lock_path.read_text(encoding="utf-8").strip()
            lock_pid = int(lock_pid_str)

            # Check if the process holding the lock is still alive
            if is_pid_alive(lock_pid):
                # Process is alive - check lock age as secondary measure
                lock_mtime = lock_path.stat().st_mtime
                now = time.time()
                lock_age = int(now - lock_mtime)

                if lock_age < 60:
                    debug(f"Lock held by live process {lock_pid} (age={lock_age}s)")
                    warn(
                        f"Concurrent execution detected (PID {lock_pid} alive) - allowing exit"
                    )
                    return False
                else:
                    # Process alive but lock very old - possible stuck process
                    warn(
                        f"Lock held by possibly stuck process {lock_pid} (age={lock_age}s) - taking over"
                    )
            else:
                # Process not alive - stale lock
                debug(f"Stale lock from dead process {lock_pid} - removing")

            # Remove stale lock
            lock_path.unlink(missing_ok=True)
        except (ValueError, OSError):
            # Invalid lock file content or read error - remove it
            lock_path.unlink(missing_ok=True)

    # Create lock file with our PID
    try:
        lock_path.write_text(str(os.getpid()), encoding="utf-8")
        debug(f"Lock acquired, PID={os.getpid()}")
        return True
    except OSError:
        warn("Failed to create lock file")
        return False


# ==============================================================================
# LOCK RELEASE
# ==============================================================================


def release_lock() -> None:
    """Release the lock file if it exists and belongs to this process.

    This function safely removes the lock file, checking that the current
    process is the owner before removal to prevent accidentally removing
    another process's lock.
    """
    lock_path = Path(LOCK_FILE)

    if not lock_path.exists():
        debug("Lock file does not exist - nothing to release")
        return

    try:
        # Verify we own this lock before removing
        lock_pid_str = lock_path.read_text(encoding="utf-8").strip()
        lock_pid = int(lock_pid_str)

        if lock_pid == os.getpid():
            lock_path.unlink(missing_ok=True)
            debug(f"Lock released, PID={os.getpid()}")
        else:
            # Lock belongs to another process - don't remove it
            debug(
                f"Lock belongs to PID {lock_pid}, not removing (we are PID {os.getpid()})"
            )
    except (ValueError, OSError):
        # If we can't read or parse the lock file, try to remove it anyway
        # since it's likely corrupted
        try:
            lock_path.unlink(missing_ok=True)
            debug(f"Removed corrupted lock file, PID={os.getpid()}")
        except OSError:
            pass
