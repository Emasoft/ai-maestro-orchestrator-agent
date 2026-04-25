"""
amoa_stop_check - Modular orchestrator stop check system.

This package provides the stop hook functionality for Orchestrator Agent,
split into focused modules for maintainability.

Modules:
    utils: Logging, JSON parsing, retry logic
    lock: Lock file management
    phase: Two-phase mode checking (Plan + Orchestration)
    tasks: Task checking (Claude Tasks, GitHub Projects, Task File, TODO)
"""
# mypy: disable-error-code="import-not-found"
# Note: Relative imports work at runtime but mypy can't resolve them
# when linting individual files in a package

from .lock import acquire_lock, is_pid_alive, release_lock
from .phase import (
    build_config_feedback_block_prompt,
    build_phase_block_prompt,
    build_verification_block_prompt,
    check_all_verifications,
    check_completion_signals,
    check_config_feedback_requests,
    check_orchestration_phase_completion,
    check_plan_phase_completion,
    parse_frontmatter,
    update_state_file,
)
from .tasks import (
    check_claude_tasks,
    check_github_projects,
    check_task_file,
    check_todo_list,
)
from .utils import (
    DEBUG,
    EXEC_PHASE_STATE_FILE,
    LOCK_FILE,
    LOG_FILE,
    MAX_RETRIES,
    # Configuration constants
    ORCHESTRATOR_STATE_FILE,
    PLAN_PHASE_STATE_FILE,
    RALPH_STATE_FILE,
    RECURSION_MARKER,
    RETRY_DELAY,
    conservative_block_exit,
    critical,
    debug,
    ensure_claude_dir,
    error,
    fail_safe_exit,
    info,
    log,
    retry_command,
    rotate_log_if_needed,
    safe_json_field,
    warn,
)

__all__ = [
    # Utils - Logging
    "log",
    "debug",
    "info",
    "warn",
    "error",
    "critical",
    # Utils - Functions
    "ensure_claude_dir",
    "rotate_log_if_needed",
    "safe_json_field",
    "retry_command",
    "fail_safe_exit",
    "conservative_block_exit",
    # Utils - Constants
    "ORCHESTRATOR_STATE_FILE",
    "RALPH_STATE_FILE",
    "PLAN_PHASE_STATE_FILE",
    "EXEC_PHASE_STATE_FILE",
    "LOCK_FILE",
    "LOG_FILE",
    "DEBUG",
    "RECURSION_MARKER",
    "MAX_RETRIES",
    "RETRY_DELAY",
    # Lock
    "acquire_lock",
    "release_lock",
    "is_pid_alive",
    # Phase - Checking
    "check_plan_phase_completion",
    "check_orchestration_phase_completion",
    "check_all_verifications",
    "check_config_feedback_requests",
    "check_completion_signals",
    # Phase - Building
    "build_phase_block_prompt",
    "build_verification_block_prompt",
    "build_config_feedback_block_prompt",
    # Phase - State
    "update_state_file",
    "parse_frontmatter",
    # Tasks
    "check_claude_tasks",
    "check_github_projects",
    "check_task_file",
    "check_todo_list",
]
