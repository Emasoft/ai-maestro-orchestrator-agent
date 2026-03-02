#!/usr/bin/env python3
"""
main.py - Main entry point for Orchestrator Agent Stop Hook (Modular Version).

This is the refactored version of eoa_orchestrator_stop_check.py, split into
focused modules for maintainability. The hook checks multiple task sources
before allowing the orchestrator to exit.

Usage:
    python -m eoa_stop_check.main < hook_input.json

The hook reads JSON from stdin and outputs a decision to stdout.
"""
# mypy: disable-error-code="import-not-found"

import json
import os
import subprocess
import sys
from pathlib import Path

from .utils import (
    debug,
    info,
    warn,
    error,
    critical,
    fail_safe_exit,
    conservative_block_exit,
    ORCHESTRATOR_STATE_FILE,
    RALPH_STATE_FILE,
    RECURSION_MARKER,
)
from .lock import acquire_lock, release_lock
from .phase import (
    check_plan_phase_completion,
    check_orchestration_phase_completion,
    check_all_verifications,
    check_config_feedback_requests,
    check_completion_signals,
    build_phase_block_prompt,
    build_verification_block_prompt,
    build_config_feedback_block_prompt,
    parse_frontmatter,
    update_state_file,
)
from .tasks import (
    check_claude_tasks,
    check_github_projects,
    check_task_file,
    check_todo_list,
)


# Global error tracking flag
CRITICAL_ERROR_OCCURRED = False


def cleanup() -> None:
    """Clean up resources on exit.

    Releases the lock file to prevent deadlocks on subsequent runs.
    """
    release_lock()


def main() -> int:
    """Main entry point for orchestrator stop hook.

    Reads JSON from stdin, checks task sources, outputs decision.

    Returns:
        Exit code: 0 for success
    """
    global CRITICAL_ERROR_OCCURRED

    # Recursion guard - prevent infinite loops from nested Claude instances
    if RECURSION_MARKER == "ACTIVE":
        return 0

    os.environ["ORCHESTRATOR_RECURSION_GUARD"] = "ACTIVE"

    # Startup logging
    info("FIRED: Stop hook triggered - checking orchestrator state")
    debug(f"Hook started, PID={os.getpid()}")
    debug(f"Working directory: {os.getcwd()}")

    # Dependency checks for required external tools
    for cmd in ["jq", "perl"]:
        try:
            subprocess.run(
                [cmd, "--version"], capture_output=True, timeout=5, check=True
            )
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            warn(f"{cmd} is required but not installed")
            fail_safe_exit(f"{cmd} not installed")

    debug("Dependencies OK: jq, perl")

    # Acquire lock to prevent concurrent execution
    if not acquire_lock():
        cleanup()
        return 0

    # Get script directory for helper scripts
    script_path = Path(__file__).resolve()
    hook_dir = script_path.parent
    script_dir = hook_dir.parent  # Parent of eoa_stop_check is scripts/

    if not script_dir.is_dir():
        warn(f"Scripts directory not found: {script_dir}")
        script_dir = Path("")

    debug(f"Hook dir: {hook_dir}")
    debug(f"Script dir: {script_dir}")

    # Read and validate hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
        else:
            hook_input = {}
    except json.JSONDecodeError:
        warn("Invalid JSON in hook input - using empty object")
        hook_input = {}

    # Check if orchestrator loop is active
    state_file_path = Path(ORCHESTRATOR_STATE_FILE)

    if not state_file_path.exists():
        debug("No active orchestrator loop (state file not found)")
        info("No orchestrator loop active - allowing exit")
        cleanup()
        return 0

    info("Orchestrator loop active - checking task sources")

    # ==================================================================
    # TWO-PHASE MODE CHECKS (v2.4.0)
    # These checks take priority over regular task source checking
    # ==================================================================

    # Check Plan Phase first
    plan_should_block, plan_reason = check_plan_phase_completion()
    if plan_should_block:
        assert plan_reason is not None
        info(f"Blocking exit due to Plan Phase: {plan_reason}")
        output = build_phase_block_prompt("plan", plan_reason)
        print(json.dumps(output, indent=2))
        cleanup()
        return 0

    # Check Orchestration Phase
    orch_should_block, orch_reason = check_orchestration_phase_completion()
    if orch_should_block:
        assert orch_reason is not None
        info(f"Blocking exit due to Orchestration Phase: {orch_reason}")
        output = build_phase_block_prompt("orchestration", orch_reason)
        print(json.dumps(output, indent=2))
        cleanup()
        return 0

    # GAP 1 FIX: Check Instruction Verification Status
    verification_ok, verification_reason = check_all_verifications()
    if not verification_ok:
        assert verification_reason is not None
        info(f"Blocking exit due to verification: {verification_reason}")
        output = build_verification_block_prompt(verification_reason)
        print(json.dumps(output, indent=2))
        cleanup()
        return 0

    # GAP 4 FIX: Check Config Feedback Requests
    config_ok, config_reason = check_config_feedback_requests()
    if not config_ok:
        assert config_reason is not None
        info(f"Blocking exit due to config feedback: {config_reason}")
        output = build_config_feedback_block_prompt(config_reason)
        print(json.dumps(output, indent=2))
        cleanup()
        return 0

    debug("Two-Phase Mode checks passed (or not in phase mode)")

    # ==================================================================
    # END TWO-PHASE MODE CHECKS
    # ==================================================================

    # Coexistence check - detect Ralph Wiggum conflict
    if Path(RALPH_STATE_FILE).exists():
        warn("Both orchestrator-loop AND ralph-loop are active simultaneously!")
        warn("This may cause conflicts. Consider using only one at a time.")

    # Parse state file
    fields = parse_frontmatter(state_file_path)

    iteration = int(fields.get("iteration", "0"))
    max_iterations = int(fields.get("max_iterations", "100"))
    completion_promise = fields.get("completion_promise", "null")
    task_file = fields.get("task_file", "null")
    check_github = fields.get("check_github", "true")
    github_project_id = fields.get("github_project_id", "")
    verification_mode = fields.get("verification_mode", "false")
    verification_remaining = int(fields.get("verification_remaining", "0"))

    debug(
        f"Parsed state: iteration={iteration}, max={max_iterations}, "
        f"check_github={check_github}"
    )
    debug(
        f"Verification state: mode={verification_mode}, remaining={verification_remaining}"
    )

    # Check max iterations (Escalation Threshold - NOT an auto-exit, per RULE 13)
    if max_iterations > 0 and iteration >= max_iterations:
        warn(f"Iteration threshold ({max_iterations}) reached - ESCALATING to user")
        print(f"""ORCHESTRATOR ESCALATION - ITERATION THRESHOLD REACHED

The orchestrator has completed {iteration} iterations without finishing all tasks.
This is NOT an automatic exit - per RULE 13, there are no deadlines or time limits.

CURRENT STATE:
- Iteration count: {iteration}/{max_iterations}
- Tasks may still be pending (checking below)

REQUIRED ACTION:
1. Review all task sources manually
2. If ALL tasks are truly complete, output: ALL_TASKS_COMPLETE
3. If tasks remain, continue working on them
4. The orchestrator will NOT auto-exit based on iteration count

This threshold exists to alert you, NOT to force exit. Quality over speed.""")
        info("Escalation triggered but continuing task check (RULE 13 compliant)")

    # Get transcript and check for completion signals
    transcript_path = hook_input.get("transcript_path", "")

    if check_completion_signals(transcript_path, completion_promise):
        state_file_path.unlink(missing_ok=True)
        cleanup()
        return 0

    # Collect pending tasks from all sources
    pending_sources: list[str] = []
    total_pending = 0
    sample_tasks: list[str] = []
    helper_script_failures = 0

    # SOURCE 1: Claude Code Native Tasks
    if transcript_path:
        claude_count, claude_tasks = check_claude_tasks(transcript_path)
        if claude_count > 0:
            total_pending += claude_count
            pending_sources.append(f"ClaudeTasks: {claude_count} pending tasks")
            sample_tasks.extend(claude_tasks)

    # SOURCE 2: GitHub Projects
    if check_github != "false" and script_dir:
        gh_count, gh_tasks = check_github_projects(script_dir, github_project_id)
        if gh_count == -1:
            helper_script_failures += 1
        elif gh_count > 0:
            total_pending += gh_count
            pending_sources.append(f"GitHub: {gh_count} project items")
            sample_tasks.extend(gh_tasks)

    # SOURCE 3: Task File
    file_count, file_tasks = check_task_file(task_file)
    if file_count > 0:
        total_pending += file_count
        pending_sources.append(f"TaskFile: {file_count} items")
        sample_tasks.extend(file_tasks)

    # SOURCE 4: Claude's Internal TODO List
    todo_count = check_todo_list(transcript_path)
    if todo_count > 0:
        total_pending += todo_count
        pending_sources.append(f"TodoList: {todo_count} session items")

    # Handle helper script failures with conservative blocking
    if helper_script_failures > 0:
        error(
            f"{helper_script_failures} helper script(s) failed - applying conservative blocking"
        )
        conservative_block_exit(
            f"Helper scripts failed ({helper_script_failures} failures). "
            "Cannot reliably determine task status."
        )

    if CRITICAL_ERROR_OCCURRED:
        conservative_block_exit("Critical errors occurred during task checking")

    # Decision logic
    info(f"Total pending tasks: {total_pending} from {len(pending_sources)} sources")

    # Verification loop - quadruple-check before allowing exit
    if total_pending == 0:
        # No pending tasks - check verification mode
        if verification_mode != "true":
            # Enter verification mode with 4 loops
            info("All tasks complete - entering verification mode (4 loops)")

            next_iteration = iteration + 1
            if not update_state_file(
                state_file_path,
                {
                    "iteration": next_iteration,
                    "verification_mode": "true",
                    "verification_remaining": 4,
                },
            ):
                conservative_block_exit("State file update failed")

            verification_prompt = """VERIFICATION LOOP 1 of 4 - MANDATORY REVIEW BEFORE EXIT

All task sources show 0 pending tasks. However, before allowing exit,
the orchestrator must complete 4 verification loops to quadruple-check
the quality and correctness of all changes made.

Examine your changes in depth. Check for:
- Errors and missing elements
- Wrong references and violations of TDD principles
- Incongruences and inconsistent naming
- Redundant stuff and duplicated parts
- Partial or incomplete planning
- Risks without safeguards
- Workarounds, hacks, fallbacks and cheap solutions instead of proper
  architectural fixes of the root causes and design improvements
- Outdated elements and unverified assumptions
- Non up-to-date documentation
- Logical flaws and adherence to user requirements
- Potential issues and edge cases

Audit your changes for potential alternatives and things you may have missed.

IMPORTANT (RULE 0 COMPLIANT): The orchestrator does NOT fix issues directly.
Instead:
1. IDENTIFY all issues found during this review
2. DOCUMENT them in a verification report
3. DELEGATE fixing to remote agents via AI Maestro (for code issues)
4. Track delegated fixes until completion
5. Re-verify in next loop that issues are resolved

This is verification loop 1 of 4. You cannot exit until all 4 loops complete."""

            system_msg = (
                "Orchestrator VERIFICATION MODE 1/4 | "
                "All tasks complete - mandatory review phase"
            )

            output = {
                "decision": "block",
                "reason": verification_prompt,
                "systemMessage": system_msg,
            }

            print(json.dumps(output, indent=2))
            debug("Blocked exit, entered verification mode (loop 1/4)")
            cleanup()
            return 0

        elif verification_remaining > 0:
            # In verification mode with loops remaining
            new_remaining = verification_remaining - 1
            current_loop = 4 - verification_remaining + 1

            info(
                f"Verification loop {current_loop}/4 - {new_remaining} loops remaining"
            )

            if new_remaining == 0:
                # Last verification loop complete - allow exit
                info("All 4 verification loops complete - allowing exit")
                print(
                    "Orchestrator: All tasks complete. Verified 4 times. Loop complete.",
                    file=sys.stderr,
                )
                state_file_path.unlink(missing_ok=True)
                cleanup()
                return 0

            # Update state file
            next_iteration = iteration + 1
            if not update_state_file(
                state_file_path,
                {"iteration": next_iteration, "verification_remaining": new_remaining},
            ):
                conservative_block_exit("State file update failed")

            verification_prompt = f"""VERIFICATION LOOP {current_loop} of 4 - CONTINUE MANDATORY REVIEW

Continue your thorough review of all changes. {new_remaining} verification loop(s) remaining.

Examine your changes in depth. Check for:
- Errors and missing elements
- Wrong references and violations of TDD principles
- Incongruences and inconsistent naming
- Redundant stuff and duplicated parts
- Partial or incomplete planning
- Risks without safeguards
- Workarounds, hacks, fallbacks and cheap solutions instead of proper
  architectural fixes of the root causes and design improvements
- Outdated elements and unverified assumptions
- Non up-to-date documentation
- Logical flaws and adherence to user requirements
- Potential issues and edge cases

Audit your changes for potential alternatives and things you may have missed.

IMPORTANT (RULE 0 COMPLIANT): The orchestrator does NOT fix issues directly.
Instead:
1. IDENTIFY all issues found during this review
2. DOCUMENT them in a verification report
3. DELEGATE fixing to remote agents via AI Maestro (for code issues)
4. Track delegated fixes until completion
5. Re-verify in next loop that issues are resolved

This is verification loop {current_loop} of 4. You cannot exit until all 4 loops complete."""

            system_msg = (
                f"Orchestrator VERIFICATION MODE {current_loop}/4 | "
                f"{new_remaining} loops remaining"
            )

            output = {
                "decision": "block",
                "reason": verification_prompt,
                "systemMessage": system_msg,
            }

            print(json.dumps(output, indent=2))
            debug(f"Blocked exit, verification loop {current_loop}/4")
            cleanup()
            return 0

        else:
            # All verification loops complete - allow exit
            info("All verification loops already complete - allowing exit")
            print(
                "Orchestrator: All tasks complete. All verification loops done. Exiting.",
                file=sys.stderr,
            )
            state_file_path.unlink(missing_ok=True)
            cleanup()
            return 0

    # Block exit - continue orchestration
    next_iteration = iteration + 1
    info(f"Blocking exit, continuing to iteration {next_iteration}")

    # Update iteration in state file
    if not update_state_file(state_file_path, {"iteration": next_iteration}):
        conservative_block_exit("State file update failed")

    # Build sources summary
    sources_summary = "\n".join(f"  - {src}" for src in pending_sources)

    # Build sample tasks list (max 5)
    tasks_preview = ""
    if sample_tasks:
        tasks_preview = "\n".join(f"  {task}" for task in sample_tasks[:5])

    # Build prompt to continue
    prompt = f"""ORCHESTRATOR CONTINUATION - DO NOT STOP

You have pending tasks that require completion. As an orchestrator, you must:

1. Review ALL task sources below - there are uncompleted items
2. Prioritize: GitHub Project issues > Claude Tasks > Session TODO
3. Continue working on pending tasks systematically
4. Delegate to subagents where appropriate
5. Mark tasks complete as you finish them
6. Only stop when ALL tasks across ALL sources are complete

PENDING TASK SOURCES:
{sources_summary}"""

    if tasks_preview:
        prompt += f"\n\nSAMPLE PENDING TASKS:\n{tasks_preview}"

    prompt += """

If you believe all tasks are truly complete across all sources, output: ALL_TASKS_COMPLETE

Otherwise, continue working on the next highest-priority pending task.

DEBUGGING: If issues occur, check logs at: .claude/orchestrator-hook.log"""

    # Build system message
    system_msg = (
        f"Orchestrator iteration {next_iteration}/{max_iterations} | "
        f"{total_pending} pending tasks across {len(pending_sources)} sources"
    )

    # Output JSON to block the stop and feed prompt back
    output = {"decision": "block", "reason": prompt, "systemMessage": system_msg}

    print(json.dumps(output, indent=2))
    debug("Blocked exit, JSON response sent")
    cleanup()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        critical(f"Unhandled exception: {e}")
        fail_safe_exit(f"Unhandled exception: {e}")
