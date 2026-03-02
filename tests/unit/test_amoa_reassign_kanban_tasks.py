#!/usr/bin/env python3
"""Tests for eoa_reassign_kanban_tasks.py -- Reassign GitHub Issues between agents.

These tests verify that the script correctly handles argument parsing,
dry-run mode, and JSON output format. Integration tests with GitHub
require a real gh CLI authentication.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the script under test
SCRIPT_PATH = Path(__file__).resolve().parents[2] / "OUTPUT_SKILLS" / "emasoft-orchestrator-agent" / "scripts" / "eoa_reassign_kanban_tasks.py"


def run_script(args, cwd, extra_env=None):
    """Run the reassign kanban tasks script with given args.

    Returns (exit_code, raw_stdout, raw_stderr).
    """
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=60,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


class TestRequiredArguments:
    """Test that required arguments are enforced."""

    def test_fails_without_from_agent(self, tmp_path):
        """Exit non-zero when --from-agent is missing."""
        code, stdout, stderr = run_script(["--to-agent", "impl-2"], tmp_path)
        assert code != 0

    def test_fails_without_to_agent(self, tmp_path):
        """Exit non-zero when --to-agent is missing."""
        code, stdout, stderr = run_script(["--from-agent", "impl-1"], tmp_path)
        assert code != 0

    def test_accepts_both_required_args(self, tmp_path):
        """Script accepts both --from-agent and --to-agent."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2", "--dry-run"],
            tmp_path,
        )
        # Should not fail on argument parsing (may fail on gh access)
        # With --dry-run it should not require gh access
        assert code == 0


class TestDryRunMode:
    """Test that --dry-run shows changes without making them."""

    def test_dry_run_produces_json_output(self, tmp_path):
        """Dry run should produce JSON summary."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2", "--dry-run"],
            tmp_path,
        )
        assert code == 0
        parsed = json.loads(stdout)
        assert isinstance(parsed, dict)
        assert "dry_run" in parsed or "reassigned" in parsed

    def test_dry_run_makes_no_changes(self, tmp_path):
        """Dry run should not make any actual GitHub changes."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2", "--dry-run"],
            tmp_path,
        )
        assert code == 0
        parsed = json.loads(stdout)
        # Dry run should indicate no actual changes were made
        if "dry_run" in parsed:
            assert parsed["dry_run"] is True


class TestOptionalArguments:
    """Test optional arguments are accepted."""

    def test_accepts_project_id(self, tmp_path):
        """Script accepts --project-id."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2",
             "--project-id", "PVT_kwDOtest", "--dry-run"],
            tmp_path,
        )
        assert code == 0

    def test_accepts_project_name(self, tmp_path):
        """Script accepts --project-name."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2",
             "--project-name", "My Project", "--dry-run"],
            tmp_path,
        )
        assert code == 0

    def test_accepts_handoff_url(self, tmp_path):
        """Script accepts --handoff-url."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2",
             "--handoff-url", "https://github.com/owner/repo/issues/42#issuecomment-123", "--dry-run"],
            tmp_path,
        )
        assert code == 0

    def test_accepts_reason(self, tmp_path):
        """Script accepts --reason."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2",
             "--reason", "load_balancing", "--dry-run"],
            tmp_path,
        )
        assert code == 0


class TestJsonOutputFormat:
    """Test the JSON output format."""

    def test_output_has_reassigned_count(self, tmp_path):
        """JSON output must have a 'reassigned' count."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2", "--dry-run"],
            tmp_path,
        )
        assert code == 0
        parsed = json.loads(stdout)
        assert "reassigned" in parsed
        assert isinstance(parsed["reassigned"], int)

    def test_output_has_failed_count(self, tmp_path):
        """JSON output must have a 'failed' count."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2", "--dry-run"],
            tmp_path,
        )
        assert code == 0
        parsed = json.loads(stdout)
        assert "failed" in parsed
        assert isinstance(parsed["failed"], int)

    def test_output_has_details_list(self, tmp_path):
        """JSON output must have a 'details' list."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-2", "--dry-run"],
            tmp_path,
        )
        assert code == 0
        parsed = json.loads(stdout)
        assert "details" in parsed
        assert isinstance(parsed["details"], list)


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_same_agent_from_and_to(self, tmp_path):
        """Exit non-zero when from-agent equals to-agent."""
        code, stdout, stderr = run_script(
            ["--from-agent", "impl-1", "--to-agent", "impl-1", "--dry-run"],
            tmp_path,
        )
        assert code == 1
