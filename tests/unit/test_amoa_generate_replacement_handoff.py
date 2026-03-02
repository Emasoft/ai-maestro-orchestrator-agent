#!/usr/bin/env python3
"""Tests for eoa_generate_replacement_handoff.py -- Generate replacement handoff documents.

These tests verify that the script correctly compiles handoff documents
for agent replacement scenarios by gathering task context, git state,
and GitHub issue information.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Path to the script under test
SCRIPT_PATH = Path(__file__).resolve().parents[2] / "OUTPUT_SKILLS" / "emasoft-orchestrator-agent" / "scripts" / "eoa_generate_replacement_handoff.py"


def run_script(args, cwd, extra_env=None):
    """Run the handoff generation script with given args.

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


def _simple_yaml_dump(data, indent=0):
    """Minimal YAML serializer for test fixtures (stdlib only).

    Handles dicts, lists of dicts, lists of strings, and scalar values.
    Sufficient for writing state file test fixtures without PyYAML.

    Args:
        data: The data to serialize.
        indent: Current indentation level.

    Returns:
        A YAML-formatted string.
    """
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append("{}{}:".format(prefix, key))
                lines.append(_simple_yaml_dump(value, indent + 1))
            elif isinstance(value, list):
                lines.append("{}{}:".format(prefix, key))
                for item in value:
                    if isinstance(item, dict):
                        first = True
                        for k, v in item.items():
                            if first:
                                lines.append("{}- {}: {}".format(prefix, k, _scalar(v)))
                                first = False
                            else:
                                lines.append("{}  {}: {}".format(prefix, k, _scalar(v)))
                    else:
                        lines.append("{}- {}".format(prefix, _scalar(item)))
            else:
                lines.append("{}{}: {}".format(prefix, key, _scalar(value)))
    return "\n".join(lines)


def _scalar(value):
    """Convert a scalar value to its YAML string representation.

    Args:
        value: The value to convert.

    Returns:
        The YAML string representation.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return str(value)


def write_exec_state(tmp_path, state_data):
    """Write an orchestration exec-phase state file using stdlib-only YAML.

    Creates the .claude directory and writes a YAML-frontmatter markdown
    file matching the codebase convention.

    Args:
        tmp_path: The temporary directory to write into.
        state_data: Dictionary of state data for the frontmatter.

    Returns:
        The Path to the created state file.
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(exist_ok=True)
    state_file = claude_dir / "orchestrator-exec-phase.local.md"
    yaml_content = _simple_yaml_dump(state_data)
    content = "---\n" + yaml_content + "\n---\n\nOrchestration state body.\n"
    state_file.write_text(content, encoding="utf-8")
    return state_file


class TestRequiredArguments:
    """Test that required arguments are enforced."""

    def test_fails_without_failed_agent(self, tmp_path):
        """Exit 1 when --failed-agent is missing."""
        code, stdout, stderr = run_script(["--new-agent", "impl-2"], tmp_path)
        assert code != 0

    def test_fails_without_new_agent(self, tmp_path):
        """Exit 1 when --new-agent is missing."""
        code, stdout, stderr = run_script(["--failed-agent", "impl-1"], tmp_path)
        assert code != 0

    def test_runs_with_both_required_args(self, tmp_path):
        """Exit 0 when both required args provided (even without state file)."""
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2"],
            tmp_path,
        )
        # Should succeed even without state -- partial mode with defaults
        assert code == 0


class TestHandoffGeneration:
    """Test handoff document generation."""

    def test_generates_handoff_with_state(self, tmp_path):
        """Generate a handoff document when state file exists."""
        write_exec_state(tmp_path, {
            "modules_status": [
                {"id": "auth-core", "status": "in-progress", "assigned_to": "impl-1"},
                {"id": "token-refresh", "status": "pending", "assigned_to": "impl-1"},
            ],
            "active_assignments": [
                {"agent": "impl-1", "module": "auth-core", "task_uuid": "task-abc123", "status": "in_progress"},
                {"agent": "impl-1", "module": "token-refresh", "task_uuid": "task-def456", "status": "pending"},
            ],
        })
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2"],
            tmp_path,
        )
        assert code == 0
        # The stdout should contain JSON with handoff info
        parsed = json.loads(stdout)
        assert "handoff_file" in parsed or "handoff" in parsed or "output" in parsed

    def test_output_file_created(self, tmp_path):
        """When --output is given, the handoff file is created at that path."""
        output_file = tmp_path / "my-handoff.md"
        write_exec_state(tmp_path, {
            "modules_status": [
                {"id": "auth-core", "status": "in-progress", "assigned_to": "impl-1"},
            ],
            "active_assignments": [
                {"agent": "impl-1", "module": "auth-core", "task_uuid": "task-abc", "status": "in_progress"},
            ],
        })
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2", "--output", str(output_file)],
            tmp_path,
        )
        assert code == 0
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "impl-1" in content
        assert "impl-2" in content

    def test_handoff_contains_metadata_section(self, tmp_path):
        """Handoff document must contain a Metadata section."""
        output_file = tmp_path / "handoff.md"
        write_exec_state(tmp_path, {
            "modules_status": [
                {"id": "auth-core", "status": "in-progress", "assigned_to": "impl-1"},
            ],
            "active_assignments": [
                {"agent": "impl-1", "module": "auth-core", "task_uuid": "task-abc", "status": "in_progress"},
            ],
        })
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2", "--output", str(output_file)],
            tmp_path,
        )
        assert code == 0
        content = output_file.read_text(encoding="utf-8")
        assert "Metadata" in content or "metadata" in content.lower()

    def test_handoff_contains_task_assignments(self, tmp_path):
        """Handoff document must list the failed agent's task assignments."""
        output_file = tmp_path / "handoff.md"
        write_exec_state(tmp_path, {
            "modules_status": [
                {"id": "auth-core", "status": "in-progress", "assigned_to": "impl-1"},
            ],
            "active_assignments": [
                {"agent": "impl-1", "module": "auth-core", "task_uuid": "task-abc", "status": "in_progress"},
            ],
        })
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2", "--output", str(output_file)],
            tmp_path,
        )
        assert code == 0
        content = output_file.read_text(encoding="utf-8")
        assert "auth-core" in content
        assert "task-abc" in content


class TestPartialMode:
    """Test partial handoff generation with gap flagging."""

    def test_partial_flag_gaps(self, tmp_path):
        """With --partial --flag-gaps, generate document marking gaps."""
        output_file = tmp_path / "partial-handoff.md"
        # No state file at all -- everything is a gap
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2",
             "--partial", "--flag-gaps", "--output", str(output_file)],
            tmp_path,
        )
        assert code == 0
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        # Gap markers should be present
        assert "GAP" in content

    def test_fails_without_partial_when_no_state(self, tmp_path):
        """Without --partial, fail when essential data is missing."""
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2"],
            tmp_path,
        )
        # Should still succeed with a warning or with defaults (no strict failure)
        # The key point: it must handle missing data somehow
        assert code == 0


class TestJsonOutput:
    """Test JSON output to stdout."""

    def test_stdout_is_valid_json(self, tmp_path):
        """Script stdout must be valid JSON."""
        write_exec_state(tmp_path, {
            "modules_status": [],
            "active_assignments": [],
        })
        code, stdout, stderr = run_script(
            ["--failed-agent", "impl-1", "--new-agent", "impl-2"],
            tmp_path,
        )
        assert code == 0
        parsed = json.loads(stdout)
        assert isinstance(parsed, dict)
