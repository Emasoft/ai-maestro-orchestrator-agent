"""
phase.py - Two-phase mode checking for Orchestrator Agent Stop Hook.

This module handles the Plan Phase and Orchestration Phase state checking,
instruction verification, and config feedback request validation.

Two-Phase Mode (v2.4.0):
  - Plan Phase: Blocks exit until all requirements documented and plan approved
  - Orchestration Phase: Blocks exit until all modules implemented
  - Dynamic tracking: Checks CURRENT state, not original state
  - User can add/modify/remove requirements and modules dynamically
"""
# mypy: disable-error-code="import-not-found"

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .utils import debug, info, warn, error, fail_safe_exit


# ==============================================================================
# PHASE STATE FILE CONSTANTS
# ==============================================================================

# Two-Phase Mode state files (in .claude directory, gitignored)
PLAN_PHASE_STATE_FILE = ".claude/orchestrator-plan-phase.local.md"
EXEC_PHASE_STATE_FILE = ".claude/orchestrator-exec-phase.local.md"


# ==============================================================================
# STATE FILE PARSING
# ==============================================================================


def parse_frontmatter(state_file_path: Path) -> dict[str, str]:
    """Parse YAML frontmatter from markdown state file.

    Extracts key-value pairs from the YAML frontmatter section at the
    beginning of a markdown file (between --- markers).

    Args:
        state_file_path: Path to state file containing YAML frontmatter

    Returns:
        Dictionary of frontmatter fields (all values as strings)

    Raises:
        Triggers fail_safe_exit on read errors or corrupted frontmatter
    """
    try:
        content = state_file_path.read_text(encoding="utf-8")
    except OSError:
        error("Failed to read state file")
        fail_safe_exit("State file read error")

    # Extract frontmatter between --- markers
    frontmatter_match = re.search(
        r"^---\n(.*?)\n---", content, re.DOTALL | re.MULTILINE
    )

    if not frontmatter_match:
        warn("State file has no valid frontmatter - removing corrupted file")
        state_file_path.unlink(missing_ok=True)
        fail_safe_exit("State file corrupted (no frontmatter)")

    # fail_safe_exit calls sys.exit(), this assert helps mypy understand control flow
    assert frontmatter_match is not None

    frontmatter = frontmatter_match.group(1)

    # Parse individual fields (simple key: value format)
    fields: dict[str, str] = {}
    for line in frontmatter.split("\n"):
        match = re.match(r"^(\w+):\s*(.+)$", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip('"')
            fields[key] = value

    return fields


def get_orchestration_status_via_script() -> dict[str, Any] | None:
    """Get accurate orchestration status by calling the dedicated check script.

    GAP 3 FIX: The parse_frontmatter() function cannot parse nested YAML structures.
    This function calls eoa_check_orchestration_phase.py which has full YAML parsing
    via PyYAML to get accurate module counts.

    Returns:
        Dictionary with orchestration status containing:
        - is_complete: bool - whether orchestration is complete
        - modules_total: int - total number of modules
        - modules_completed: int - number of completed modules
        - incomplete_modules: list - details of incomplete modules
        - blocking_reasons: list - reasons blocking completion
        Or None if script call fails
    """
    # Determine script path relative to this module's location
    script_dir = Path(__file__).parent.parent
    check_script = script_dir / "eoa_check_orchestration_phase.py"

    if not check_script.exists():
        warn(f"Orchestration check script not found: {check_script}")
        return None

    try:
        result = subprocess.run(
            ["python3", str(check_script), "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode in (0, 2):  # 0 = complete, 2 = incomplete
            output = result.stdout.strip()
            if output:
                parsed: dict[str, Any] = json.loads(output)
                return parsed

        # Check stderr for errors
        if result.stderr:
            warn(f"Orchestration check script error: {result.stderr}")
        return None

    except subprocess.TimeoutExpired:
        warn("Orchestration check script timed out")
        return None
    except json.JSONDecodeError as e:
        warn(f"Failed to parse orchestration check script output: {e}")
        return None
    except Exception as e:
        warn(f"Error calling orchestration check script: {e}")
        return None


# ==============================================================================
# PLAN PHASE CHECKING
# ==============================================================================


def check_plan_phase_completion() -> tuple[bool, str | None]:
    """Check if Plan Phase is active and complete.

    The Plan Phase blocks exit until:
    - All requirements are documented (requirements_complete: true)
    - Plan is approved by user (status: approved)
    - Phase is marked complete (plan_phase_complete: true)

    Returns:
        Tuple of (should_block, blocking_reason):
        - (False, None) if not in plan phase or plan is complete
        - (True, reason) if plan phase is active but incomplete
    """
    plan_path = Path(PLAN_PHASE_STATE_FILE)

    if not plan_path.exists():
        debug("Plan Phase state file not found - not in plan phase")
        return (False, None)

    debug("Plan Phase state file found - checking completion")

    try:
        fields = parse_frontmatter(plan_path)

        # Check if plan phase is marked complete
        if fields.get("plan_phase_complete", "false") == "true":
            debug("Plan Phase marked complete")
            return (False, None)

        # Check plan status
        status = fields.get("status", "drafting")
        if status == "approved":
            debug("Plan approved but plan_phase_complete not set")
            return (False, None)

        # Collect blocking reasons
        blocking_reasons = []

        # Check requirements
        if fields.get("requirements_complete", "false") != "true":
            blocking_reasons.append("Requirements incomplete")

        # Check user approval
        if status not in ("approved", "complete"):
            blocking_reasons.append(f"Plan not approved (status: {status})")

        if blocking_reasons:
            reason = f"Plan Phase incomplete: {', '.join(blocking_reasons)}"
            info(reason)
            return (True, reason)

        return (False, None)

    except Exception as e:
        warn(f"Error checking plan phase: {e}")
        return (False, None)


# ==============================================================================
# ORCHESTRATION PHASE CHECKING
# ==============================================================================


def check_orchestration_phase_completion() -> tuple[bool, str | None]:
    """Check if Orchestration Phase is active and complete.

    The Orchestration Phase blocks exit until:
    - All modules are implemented (all_modules_complete: true)
    - Verification loops are complete (if in verification mode)

    Uses script-based checking for accurate nested YAML parsing.

    Returns:
        Tuple of (should_block, blocking_reason):
        - (False, None) if not in orchestration phase or all modules complete
        - (True, reason) if orchestration phase is active but incomplete
    """
    exec_path = Path(EXEC_PHASE_STATE_FILE)

    if not exec_path.exists():
        debug("Orchestration Phase state file not found - not in orchestration phase")
        return (False, None)

    debug("Orchestration Phase state file found - checking completion")

    try:
        fields = parse_frontmatter(exec_path)

        # Check if all modules complete
        if fields.get("all_modules_complete", "false") == "true":
            # Check verification loops
            if fields.get("verification_mode", "false") == "true":
                remaining = int(fields.get("verification_loops_remaining", "0"))
                if remaining > 0:
                    reason = f"Orchestration verification in progress: {remaining} loops remaining"
                    info(reason)
                    return (True, reason)
            debug("Orchestration Phase complete")
            return (False, None)

        # GAP 3 FIX: Use script-based check for accurate module counting
        # The simple frontmatter parsing cannot handle nested YAML structures
        # so we call the dedicated script with full PyYAML parsing
        orch_status = get_orchestration_status_via_script()

        if orch_status:
            # Use accurate counts from the script
            if not orch_status.get("is_complete", True):
                blocking_reasons = orch_status.get("blocking_reasons", [])
                modules_total = orch_status.get("modules_total", 0)
                modules_completed = orch_status.get("modules_completed", 0)
                incomplete_modules = orch_status.get("incomplete_modules", [])

                if blocking_reasons:
                    reason = (
                        f"Orchestration Phase incomplete: {'; '.join(blocking_reasons)}"
                    )
                elif modules_total > 0:
                    pending = modules_total - modules_completed
                    reason = f"Orchestration Phase incomplete: {pending}/{modules_total} modules pending"
                else:
                    reason = "Orchestration Phase incomplete"

                # Add details about incomplete modules
                if incomplete_modules:
                    module_list = [
                        f"{m.get('id', 'unknown')} ({m.get('status', 'unknown')})"
                        for m in incomplete_modules[:3]
                    ]  # Limit to 3 for brevity
                    if len(incomplete_modules) > 3:
                        module_list.append(
                            f"... and {len(incomplete_modules) - 3} more"
                        )
                    reason += f". Modules: {', '.join(module_list)}"

                info(reason)
                return (True, reason)

            # Script says complete
            return (False, None)

        # Fallback to simple frontmatter counts if script call fails
        modules_total = int(fields.get("modules_total", "0"))
        modules_completed = int(fields.get("modules_completed", "0"))

        if modules_total > 0 and modules_completed < modules_total:
            pending = modules_total - modules_completed
            reason = f"Orchestration Phase incomplete: {pending}/{modules_total} modules pending"
            info(reason)
            return (True, reason)

        # No blocking reasons found
        return (False, None)

    except Exception as e:
        warn(f"Error checking orchestration phase: {e}")
        return (False, None)


# ==============================================================================
# VERIFICATION CHECKING
# ==============================================================================


def check_all_verifications() -> tuple[bool, str | None]:
    """Check if all instruction verifications are complete.

    GAP 1 FIX: This includes:
    1. Initial instruction verification for active assignments
    2. Instruction update verifications for mid-implementation changes

    The Instruction Verification Protocol is MANDATORY. Before any agent can
    report progress or before the orchestrator can exit, all verifications
    must be complete.

    Returns:
        Tuple of (is_ok, message):
        - (True, None) if all verifications complete or not in orchestration phase
        - (False, reason) if any verification is pending
    """
    exec_path = Path(EXEC_PHASE_STATE_FILE)

    if not exec_path.exists():
        debug("Not in orchestration phase - skipping verification check")
        return (True, None)

    try:
        # Use full YAML parsing for nested structures
        content = exec_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return (True, None)

        end_idx = content.find("---", 3)
        if end_idx == -1:
            return (True, None)

        try:
            import yaml

            state = yaml.safe_load(content[3:end_idx]) or {}
        except ImportError:
            warn("PyYAML not available - using basic parsing")
            state = parse_frontmatter(exec_path)
        except Exception as e:
            warn(f"YAML parsing error: {e}")
            # Conservative: block if we can't parse state
            return (False, "Unable to parse verification state - blocking for safety")

        # Ensure state is a dict (YAML could return other types)
        if not isinstance(state, dict):
            return (True, None)

        # Check if in orchestration phase
        if state.get("phase") != "orchestration":
            return (True, None)

        # Track incomplete verifications
        incomplete: list[str] = []

        # Check 1: Initial instruction verification for active assignments
        active_assignments = state.get("active_assignments", [])
        if isinstance(active_assignments, list):
            for assignment in active_assignments:
                if not isinstance(assignment, dict):
                    continue
                agent = assignment.get("agent", "unknown")
                module = assignment.get("module", "unknown")
                verification = assignment.get("instruction_verification", {})

                if isinstance(verification, dict):
                    status = verification.get("status", "pending")
                    authorized_at = verification.get("authorized_at")
                else:
                    status = "pending"
                    authorized_at = None

                if status != "verified" or not authorized_at:
                    incomplete.append(f"initial:{agent}/{module}")

        # Check 2: Instruction update verifications
        instruction_updates = state.get("instruction_updates", [])
        if isinstance(instruction_updates, list):
            for update in instruction_updates:
                if not isinstance(update, dict):
                    continue
                update_agent = update.get("agent", "unknown")
                update_module = update.get("module", "unknown")
                update_status = update.get("verification_status", "pending")
                update_id = update.get("update_id", "unknown")

                if update_status != "verified":
                    incomplete.append(
                        f"update:{update_agent}/{update_module}#{update_id}"
                    )

        if incomplete:
            reason = f"Verification incomplete for: {', '.join(incomplete)}"
            info(reason)
            return (False, reason)

        return (True, None)

    except Exception as e:
        warn(f"Error checking verifications: {e}")
        # Conservative: block on error to prevent premature exit
        return (False, f"Verification check error - blocking for safety: {e}")


# ==============================================================================
# CONFIG FEEDBACK CHECKING
# ==============================================================================


def check_config_feedback_requests() -> tuple[bool, str | None]:
    """Check if there are unresolved config feedback requests.

    GAP 4 FIX: Config feedback requests are sent by implementers when they need:
    - Clarification on configuration values
    - Approval for configuration changes
    - Guidance on environment-specific settings

    These MUST be addressed before the orchestrator exits to avoid leaving
    agents blocked.

    Returns:
        Tuple of (is_ok, message):
        - (True, None) if no pending config feedback requests
        - (False, reason) if there are unresolved requests
    """
    exec_path = Path(EXEC_PHASE_STATE_FILE)

    if not exec_path.exists():
        debug("Not in orchestration phase - skipping config feedback check")
        return (True, None)

    try:
        # Use full YAML parsing for nested structures
        content = exec_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return (True, None)

        end_idx = content.find("---", 3)
        if end_idx == -1:
            return (True, None)

        try:
            import yaml

            state = yaml.safe_load(content[3:end_idx]) or {}
        except ImportError:
            warn("PyYAML not available - skipping config feedback check")
            return (True, None)
        except Exception as e:
            warn(f"YAML parsing error in config feedback check: {e}")
            return (True, None)

        # Check if in orchestration phase
        if state.get("phase") != "orchestration":
            return (True, None)

        # Check for unresolved config feedback
        config_feedback = state.get("config_feedback", [])
        unresolved = []

        for feedback in config_feedback:
            if not feedback.get("resolved", False):
                agent = feedback.get("agent", "unknown")
                module = feedback.get("module", "unknown")
                request_type = feedback.get("type", "config")
                feedback_id = feedback.get("feedback_id", "unknown")
                unresolved.append(f"{agent}/{module} ({request_type}#{feedback_id})")

        if unresolved:
            reason = f"Unresolved config feedback requests: {', '.join(unresolved)}"
            info(reason)
            return (False, reason)

        return (True, None)

    except Exception as e:
        warn(f"Error checking config feedback: {e}")
        # Non-blocking on error for config feedback (less critical than verification)
        return (True, None)


# ==============================================================================
# BLOCK PROMPT BUILDERS
# ==============================================================================


def build_phase_block_prompt(phase: str, reason: str) -> dict[str, str | bool]:
    """Build a block prompt for phase-related blocking.

    Creates a JSON-serializable dict that instructs Claude to block exit
    and display phase completion guidance.

    Args:
        phase: "plan" or "orchestration" - which phase is incomplete
        reason: Human-readable blocking reason

    Returns:
        JSON output dict for blocking with:
        - decision: "block"
        - reason: Full prompt text
        - systemMessage: Brief status message
    """
    if phase == "plan":
        prompt = f"""PLAN PHASE INCOMPLETE - CANNOT EXIT

{reason}

The orchestrator is in Plan Phase mode. You must complete ALL of the following
before exiting:

1. Complete USER_REQUIREMENTS.md with all requirements
2. Define all modules with acceptance criteria
3. Get user approval via /approve-plan

Use these commands to progress:
- /planning-status - View current progress
- /add-requirement - Add new requirements
- /approve-plan - Submit plan for approval (when ready)

You cannot exit until the plan is complete and approved."""
        system_msg = f"Orchestrator PLAN PHASE | {reason}"

    else:  # orchestration
        prompt = f"""ORCHESTRATION PHASE INCOMPLETE - CANNOT EXIT

{reason}

The orchestrator is in Orchestration Phase mode. You must complete ALL modules
before exiting.

Use these commands to check progress:
- /orchestration-status - View module and agent status
- /check-agents - Poll all active agents for progress

Actions you can take:
- Assign modules to agents: /assign-module <module> <agent>
- Check on agent progress and unblock them
- Review completed work
- Mark modules complete when verified

You cannot exit until all modules are implemented and verified."""
        system_msg = f"Orchestrator ORCHESTRATION PHASE | {reason}"

    return {
        "decision": "block",
        "reason": prompt,
        "systemMessage": system_msg,
    }


def build_verification_block_prompt(reason: str) -> dict[str, str | bool]:
    """Build a block prompt for verification-related blocking.

    Creates a JSON-serializable dict that instructs Claude to block exit
    and complete the Instruction Verification Protocol.

    Args:
        reason: Human-readable blocking reason describing incomplete verifications

    Returns:
        JSON output dict for blocking with:
        - decision: "block"
        - reason: Brief reason
        - continue: True (to continue operation)
        - systemMessage: Full prompt with resolution guidance
    """
    prompt = f"""INSTRUCTION VERIFICATION INCOMPLETE - CANNOT EXIT

{reason}

The Instruction Verification Protocol is MANDATORY. Before any agent can
report progress or before the orchestrator can exit:

1. INITIAL VERIFICATION: Each agent must repeat requirements and receive
   authorization before starting implementation.

2. UPDATE VERIFICATION: When instructions change mid-implementation, agents
   must acknowledge and confirm understanding of the changes.

Actions to resolve:
- /check-agents - See which agents have pending verifications
- For initial: Send verification request to unverified agents
- For updates: Confirm agent acknowledged the instruction changes

You cannot exit until all verifications are complete."""

    return {
        "decision": "block",
        "reason": reason,
        "continue": True,
        "systemMessage": f"Orchestrator VERIFICATION | {reason}\n\n{prompt}",
    }


def build_config_feedback_block_prompt(reason: str) -> dict[str, str | bool]:
    """Build a block prompt for config feedback blocking.

    Creates a JSON-serializable dict that instructs Claude to block exit
    and address pending config feedback from implementer agents.

    Args:
        reason: Human-readable blocking reason listing unresolved feedback

    Returns:
        JSON output dict for blocking with:
        - decision: "block"
        - reason: Brief reason
        - continue: True (to continue operation)
        - systemMessage: Full prompt with resolution guidance
    """
    prompt = f"""CONFIG FEEDBACK PENDING - CANNOT EXIT

{reason}

Implementer agents have requested configuration feedback that has not been resolved.
These requests MUST be addressed before exiting to avoid leaving agents blocked.

Types of config feedback:
- Configuration value clarification
- Environment-specific settings approval
- Deployment configuration decisions
- Integration settings confirmation

Actions to resolve:
- Review pending config feedback in the orchestration state file
- Provide the requested configuration decisions
- Mark each feedback item as resolved after addressing it

Use /check-agents to see which agents are waiting for config feedback."""

    return {
        "decision": "block",
        "reason": reason,
        "continue": True,
        "systemMessage": f"Orchestrator CONFIG FEEDBACK | {reason}\n\n{prompt}",
    }


# ==============================================================================
# COMPLETION SIGNAL CHECKING
# ==============================================================================


def check_completion_signals(transcript_path: str, completion_promise: str) -> bool:
    """Check transcript for completion signals.

    Scans the transcript file for explicit completion markers:
    - <promise>...</promise> tags matching the configured completion promise
    - ALL_TASKS_COMPLETE marker in the last assistant message

    Args:
        transcript_path: Path to transcript JSON file
        completion_promise: Expected completion promise text

    Returns:
        True if completion signal detected, False otherwise
    """
    if not transcript_path or not Path(transcript_path).exists():
        return False

    try:
        content = Path(transcript_path).read_text(encoding="utf-8")

        # Find last assistant message
        assistant_messages = re.findall(r'"role":\s*"assistant".*', content)
        if not assistant_messages:
            return False

        last_message = assistant_messages[-1]

        # Try to extract text content
        try:
            # Simplified extraction - the actual message might be complex
            text_match = re.search(r'"text":\s*"([^"]*)"', last_message)
            if not text_match:
                return False

            last_output = text_match.group(1)

            # Check for completion promise (if configured)
            if completion_promise and completion_promise != "null":
                promise_match = re.search(
                    r"<promise>(.*?)</promise>", last_output, re.DOTALL
                )
                if promise_match:
                    promise_text = promise_match.group(1).strip()
                    if promise_text == completion_promise:
                        info(
                            f"Completion promise detected: <promise>{completion_promise}</promise>"
                        )
                        return True

            # Check for ALL_TASKS_COMPLETE marker
            if "ALL_TASKS_COMPLETE" in last_output:
                info("ALL_TASKS_COMPLETE marker detected")
                return True

        except (json.JSONDecodeError, AttributeError):
            pass

    except OSError:
        pass

    return False


# ==============================================================================
# STATE FILE UPDATE
# ==============================================================================


def update_state_file(state_file_path: Path, updates: dict[str, str | int]) -> bool:
    """Update fields in state file.

    Performs an atomic update of YAML frontmatter fields in a state file.
    Uses temp file + rename pattern for safety.

    Args:
        state_file_path: Path to state file
        updates: Dictionary of field updates (key: new_value)

    Returns:
        True if successful, False otherwise
    """
    import os

    temp_path: Path | None = None
    try:
        content = state_file_path.read_text(encoding="utf-8")

        # Update each field
        for key, value in updates.items():
            pattern = rf"^{key}:\s*.*$"
            replacement = f"{key}: {value}"
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Write to temp file first
        temp_path = Path(f"{state_file_path}.tmp.{os.getpid()}")
        temp_path.write_text(content, encoding="utf-8")

        # Atomic replace
        temp_path.replace(state_file_path)
        return True
    except OSError:
        error("Failed to update state file")
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        return False
