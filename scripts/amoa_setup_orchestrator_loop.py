#!/usr/bin/env python3
"""
eoa_setup_orchestrator_loop.py - Initialize orchestrator loop state file.

Creates the state file that activates the Stop hook for continuous task-driven
development loops. Monitors multiple task sources (Claude Tasks, GitHub Projects, task files).

NO external dependencies - Python 3.8+ stdlib only.

Usage:
    # Basic usage with default settings
    python3 eoa_setup_orchestrator_loop.py Complete all pending tasks

    # With custom options
    python3 eoa_setup_orchestrator_loop.py --max-iterations 50 --task-file TODO.md

    # GitHub-only mode
    python3 eoa_setup_orchestrator_loop.py --check-tasks false --github-project 123

    # With completion promise
    python3 eoa_setup_orchestrator_loop.py --completion-promise "SPRINT COMPLETE"

Examples:
    # Start loop monitoring all sources
    python3 eoa_setup_orchestrator_loop.py Review all open PRs

    # Cancel active loop
    rm .claude/orchestrator-loop.local.md

Exit codes:
    0 - Success (loop started)
    1 - Error (invalid arguments or loop already active)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Namespace object containing parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Orchestrator Loop - Continuous task-driven development loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DESCRIPTION:
  Starts an orchestrator loop that prevents exit until ALL tasks are complete
  across multiple sources: Claude Tasks, GitHub Projects, task files, and TODO list.

  Unlike Ralph Wiggum (single prompt loop), the orchestrator:
  - Monitors multiple task sources simultaneously
  - Generates dynamic prompts based on pending tasks
  - Supports GitHub Projects integration
  - Tracks Claude Code native Tasks

STOPPING CONDITIONS:
  1. All tasks complete across all monitored sources
  2. Output: ALL_TASKS_COMPLETE
  3. Output: <promise>YOUR_PHRASE</promise> (if --completion-promise set)
  4. Max iterations reached (if --max-iterations set)

MONITORING:
  # Check current state:
  cat .claude/orchestrator-loop.local.md

  # Check iteration:
  grep '^iteration:' .claude/orchestrator-loop.local.md

  # View logs:
  tail -20 .claude/orchestrator-hook.log

CANCELLING:
  rm .claude/orchestrator-loop.local.md
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help="Initial prompt/task description (optional)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        metavar="N",
        help="Maximum iterations before auto-stop (default: 100, 0=unlimited)",
    )

    parser.add_argument(
        "--completion-promise",
        type=str,
        default="null",
        metavar="TEXT",
        help="Promise phrase to trigger completion (in <promise> tags)",
    )

    parser.add_argument(
        "--task-file",
        type=str,
        default="null",
        metavar="PATH",
        help="Markdown task file to monitor",
    )

    parser.add_argument(
        "--check-tasks",
        type=str,
        default="true",
        metavar="BOOL",
        help="Check Claude Code native Tasks (default: true)",
    )

    parser.add_argument(
        "--check-github",
        type=str,
        default="true",
        metavar="BOOL",
        help="Check GitHub Projects (default: true)",
    )

    parser.add_argument(
        "--github-project",
        type=str,
        default="",
        metavar="ID",
        help="Specific GitHub Project ID to check",
    )

    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> Optional[str]:
    """Validate parsed arguments.

    Args:
        args: Parsed argument namespace

    Returns:
        Error message string if validation fails, None if valid
    """
    if args.max_iterations < 0:
        return f"❌ Error: --max-iterations must be >= 0 (got: {args.max_iterations})"

    return None


def check_existing_loop(state_file: Path) -> Optional[str]:
    """Check if orchestrator loop is already active.

    Args:
        state_file: Path to state file

    Returns:
        Current iteration number if loop active, None otherwise
    """
    if not state_file.exists():
        return None

    try:
        content = state_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.startswith("iteration:"):
                return line.replace("iteration:", "").strip()
    except OSError:
        pass

    return "?"


def create_state_file(
    state_file: Path,
    max_iterations: int,
    completion_promise: str,
    task_file: str,
    check_tasks: str,
    check_github: str,
    github_project_id: str,
    prompt: str,
) -> None:
    """Create orchestrator loop state file with YAML frontmatter.

    Args:
        state_file: Path to state file
        max_iterations: Maximum iterations before auto-stop
        completion_promise: Promise phrase for completion
        task_file: Path to task file to monitor
        check_tasks: Whether to check Claude Code native Tasks
        check_github: Whether to check GitHub Projects
        github_project_id: GitHub Project ID to check
        prompt: Initial task prompt
    """
    # Ensure .claude directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate ISO 8601 timestamp
    started_at = datetime.now().astimezone().isoformat()

    # Create YAML frontmatter
    yaml_content = f"""---
iteration: 1
max_iterations: {max_iterations}
completion_promise: "{completion_promise}"
task_file: "{task_file}"
check_tasks: {check_tasks}
check_github: {check_github}
github_project_id: "{github_project_id}"
started_at: {started_at}
verification_mode: false
verification_remaining: 0
---

{prompt}
"""

    state_file.write_text(yaml_content, encoding="utf-8")


def display_startup_message(
    max_iterations: int,
    completion_promise: str,
    task_file: str,
    check_tasks: str,
    check_github: str,
    github_project_id: str,
    prompt: str,
    state_file: Path,
) -> None:
    """Display formatted startup message with configuration.

    Args:
        max_iterations: Maximum iterations setting
        completion_promise: Completion promise phrase
        task_file: Task file path
        check_tasks: Claude Tasks check setting
        check_github: GitHub check setting
        github_project_id: GitHub Project ID
        prompt: Initial prompt
        state_file: Path to state file
    """
    print("✅ Orchestrator loop started")
    print()
    print("═" * 63)
    print("ORCHESTRATOR LOOP ACTIVE")
    print("═" * 63)
    print()
    print("Configuration:")
    print(
        f"  Max iterations:      {max_iterations if max_iterations > 0 else 'unlimited'}"
    )
    print(
        f"  Completion promise:  {completion_promise if completion_promise != 'null' else 'none'}"
    )
    print(f"  Task file:           {task_file if task_file != 'null' else 'none'}")
    print(f"  Check Tasks:         {check_tasks}")
    print(f"  Check GitHub:        {check_github}")
    if github_project_id:
        print(f"  GitHub Project:      {github_project_id}")
    print()

    print("Task Sources Being Monitored:")
    if check_tasks == "true":
        print("  ✓ Claude Code native Tasks")
    if check_github == "true":
        print("  ✓ GitHub Projects (open items)")
    if task_file != "null":
        print(f"  ✓ Task file: {task_file}")
    print("  ✓ Claude TODO list (session)")
    print()

    print("Stopping Conditions:")
    print("  • All tasks complete across all sources")
    print("  • Output: ALL_TASKS_COMPLETE")
    if completion_promise != "null":
        print(f"  • Output: <promise>{completion_promise}</promise>")
    if max_iterations > 0:
        print(f"  • Max iterations: {max_iterations}")
    print()
    print(f"To cancel: rm {state_file}")
    print("═" * 63)

    # Display completion promise requirements if set
    if completion_promise != "null" and completion_promise:
        print()
        print("═" * 63)
        print("CRITICAL - Orchestrator Loop Completion Promise")
        print("═" * 63)
        print()
        print("To complete this loop, output this EXACT text:")
        print(f"  <promise>{completion_promise}</promise>")
        print()
        print("STRICT REQUIREMENTS (DO NOT VIOLATE):")
        print("  ✓ Use <promise> XML tags EXACTLY as shown above")
        print("  ✓ The statement MUST be completely and unequivocally TRUE")
        print("  ✓ Do NOT output false statements to exit the loop")
        print("  ✓ Do NOT lie even if you think you should exit")
        print()
        print("IMPORTANT - Do not circumvent the loop:")
        print("  Even if you believe you're stuck, the task is impossible,")
        print("  or you've been running too long - you MUST NOT output a")
        print("  false promise statement. The loop is designed to continue")
        print("  until the promise is GENUINELY TRUE. Trust the process.")
        print()
        print("  If the loop should stop, the promise statement will become")
        print("  true naturally. Do not force it by lying.")
        print("═" * 63)

    # Display initial task prompt
    if prompt:
        print()
        print("Initial Task:")
        print(prompt)


def main() -> int:
    """Main entry point for orchestrator loop setup.

    Returns:
        Exit code: 0 for success, 1 for error
    """
    args = parse_arguments()

    # Validate arguments
    error_msg = validate_arguments(args)
    if error_msg:
        print(error_msg, file=sys.stderr)
        return 1

    # Build prompt from arguments
    prompt = " ".join(args.prompt) if args.prompt else ""

    # State file location
    state_file = Path(".claude/orchestrator-loop.local.md")

    # Check for existing loop
    current_iter = check_existing_loop(state_file)
    if current_iter is not None:
        print(
            f"⚠️  Orchestrator loop already active (iteration: {current_iter})",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(f"   To cancel:  rm {state_file}", file=sys.stderr)
        print(
            f"   To restart: rm {state_file} && run this command again", file=sys.stderr
        )
        return 1

    # Create state file
    create_state_file(
        state_file=state_file,
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        task_file=args.task_file,
        check_tasks=args.check_tasks,
        check_github=args.check_github,
        github_project_id=args.github_project,
        prompt=prompt,
    )

    # Display startup message
    display_startup_message(
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        task_file=args.task_file,
        check_tasks=args.check_tasks,
        check_github=args.check_github,
        github_project_id=args.github_project,
        prompt=prompt,
        state_file=state_file,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
