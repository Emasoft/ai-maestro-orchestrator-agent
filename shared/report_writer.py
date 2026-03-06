"""
report_writer.py - Token-efficient output utility for AMOA scripts.

WHY: Scripts that print verbose output flood parent agents/orchestrators with tokens.
This module redirects verbose output to timestamped report files and prints only
a 2-3 line summary + filepath to stdout, dramatically reducing token consumption.

Usage:
    # Option A: Direct write (for scripts being fully refactored)
    from shared.report_writer import write_report
    path = write_report(content="...", script_name="my_script", summary="All 5 checks passed")

    # Option B: Capture wrapper (for wrapping existing print-heavy functions)
    from shared.report_writer import capture_and_report
    exit_code = capture_and_report(
        fn=lambda: run_verbose_checks(),
        script_name="my_script",
        summary_fn=lambda output: f"Completed with {output.count('ERROR')} errors",
    )

    # Option C: Add --output-dir argument to argparse
    from shared.report_writer import add_output_dir_argument
    add_output_dir_argument(parser)

NO external dependencies - Python 3.8+ stdlib only.
"""

import argparse
import io
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# WHY: docs_dev/reports/ is gitignored and safe for verbose output
DEFAULT_REPORT_DIR = "docs_dev/reports"


def write_report(
    content: str,
    script_name: str,
    summary: str,
    output_dir: str = DEFAULT_REPORT_DIR,
    suffix: str = ".md",
) -> Path:
    """Write verbose content to a timestamped report file and print summary to stdout.

    WHY: Keeps stdout to 2-3 lines (summary + filepath) while preserving full output in a file.
    The parent agent/orchestrator only consumes the summary as tokens.

    Args:
        content: Full verbose output to write to file.
        script_name: Name of the calling script (used in filename).
        summary: 1-3 line summary to print to stdout.
        output_dir: Directory for report files (default: docs_dev/reports/).
        suffix: File extension (default: .md).

    Returns:
        Path to the written report file.
    """
    # WHY: Ensure the output directory exists
    report_dir = Path(output_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    # WHY: Timestamp in filename prevents collisions and aids debugging
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    clean_name = script_name.replace(".py", "").replace("/", "-")
    filename = f"{clean_name}-{timestamp}{suffix}"
    report_path = report_dir / filename

    # WHY: Write full content to file so nothing is lost
    report_path.write_text(content, encoding="utf-8")

    # WHY: Print only summary + path to stdout — this is what the parent agent sees
    print(f"[OK] {clean_name} - {summary}")
    print(f"Report: {report_path}")

    return report_path


def capture_and_report(
    fn: Callable[[], int],
    script_name: str,
    summary_fn: Callable[[str], str],
    output_dir: str = DEFAULT_REPORT_DIR,
) -> int:
    """Capture stdout from fn(), write to file, print summary.

    WHY: Wraps existing print-heavy functions without rewriting their internals.
    Redirects sys.stdout to StringIO during fn() execution, captures all output,
    writes it to a timestamped file, then prints a brief summary.

    Args:
        fn: Callable that prints to stdout and returns an exit code (int).
        script_name: Name for the report file.
        summary_fn: Callable that takes the full captured output and returns a 1-3 line summary.
        output_dir: Directory for report files.

    Returns:
        Exit code from fn(), unchanged.
    """
    # WHY: Capture stdout while preserving stderr for real-time error visibility
    captured = io.StringIO()
    original_stdout = sys.stdout

    try:
        sys.stdout = captured
        exit_code = fn()
    except Exception as e:
        # WHY: Restore stdout before handling the exception so error output works
        sys.stdout = original_stdout
        print(f"[ERROR] {script_name} - {e}", file=sys.stderr)
        raise
    finally:
        sys.stdout = original_stdout

    captured_text = captured.getvalue()

    # WHY: Generate summary from the captured output
    summary = summary_fn(captured_text)

    # WHY: Write full output to file, print summary to stdout
    write_report(
        content=captured_text,
        script_name=script_name,
        summary=summary,
        output_dir=output_dir,
    )

    return exit_code


def add_output_dir_argument(parser: argparse.ArgumentParser) -> None:
    """Add --output-dir argument to an argparse parser.

    WHY: Standardizes the output directory argument across all scripts.
    When --output-dir is provided, verbose output goes to a file in that directory.
    When omitted, scripts behave as before (print to stdout) for backward compatibility.
    """
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help=f"Write verbose output to a timestamped report file in this directory "
        f"instead of stdout. Default when set: {DEFAULT_REPORT_DIR}/",
    )


def should_use_report(args: argparse.Namespace) -> bool:
    """Check if the script should redirect output to a report file.

    WHY: Centralized check so scripts can conditionally use file output.
    Returns True if --output-dir was explicitly provided.
    """
    return getattr(args, "output_dir", None) is not None


def get_output_dir(args: argparse.Namespace) -> str:
    """Get the output directory from args, defaulting to DEFAULT_REPORT_DIR.

    WHY: When --output-dir is provided without a value, use the default.
    """
    output_dir = getattr(args, "output_dir", None)
    return output_dir if output_dir else DEFAULT_REPORT_DIR
