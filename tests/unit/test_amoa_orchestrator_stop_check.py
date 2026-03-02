#!/usr/bin/env python3
"""Tests for eoa_orchestrator_stop_check.py -- Phase-aware stop hook enforcement.

These tests verify that the standalone stop check script correctly reads
orchestration state and makes allow/block decisions based on phase status.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Path to the script under test
SCRIPT_PATH = Path(__file__).resolve().parents[2] / "OUTPUT_SKILLS" / "emasoft-orchestrator-agent" / "scripts" / "eoa_orchestrator_stop_check.py"


def run_script(cwd, extra_env=None):
    """Run the stop check script in the given working directory.

    Returns (exit_code, stdout_parsed_json_or_None, raw_stdout, raw_stderr).
    """
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=30,
    )
    stdout = result.stdout.strip()
    try:
        parsed = json.loads(stdout) if stdout else None
    except json.JSONDecodeError:
        parsed = None
    return result.returncode, parsed, stdout, result.stderr


class TestNoStateFile:
    """When no orchestration state file exists, the script should allow stop."""

    def test_allows_stop_when_no_state_file(self, tmp_path):
        """Allow stop (exit 0) when no .emasoft/orchestration-state.json exists."""
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0
        if parsed is not None:
            assert parsed.get("decision") == "allow"


class TestPlanPhaseBlocking:
    """When in Plan Phase and plan is incomplete, the script should block stop."""

    def _write_state(self, tmp_path, state_data):
        state_dir = tmp_path / ".emasoft"
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / "orchestration-state.json"
        state_file.write_text(json.dumps(state_data), encoding="utf-8")
        return state_file

    def test_blocks_stop_when_plan_phase_incomplete(self, tmp_path):
        """Block stop (exit 2) when in plan phase and plan_phase_complete is false."""
        self._write_state(tmp_path, {
            "phase": "plan",
            "plan_phase_complete": False,
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 2
        assert parsed is not None
        assert parsed["decision"] == "block"
        assert "plan" in parsed["reason"].lower()

    def test_allows_stop_when_plan_phase_complete(self, tmp_path):
        """Allow stop (exit 0) when plan phase is marked complete."""
        self._write_state(tmp_path, {
            "phase": "plan",
            "plan_phase_complete": True,
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0
        if parsed is not None:
            assert parsed["decision"] == "allow"


class TestOrchestrationPhaseBlocking:
    """When in Orchestration Phase, block if modules are incomplete."""

    def _write_state(self, tmp_path, state_data):
        state_dir = tmp_path / ".emasoft"
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / "orchestration-state.json"
        state_file.write_text(json.dumps(state_data), encoding="utf-8")
        return state_file

    def test_blocks_when_modules_incomplete(self, tmp_path):
        """Block stop (exit 2) when orchestration phase has incomplete modules."""
        self._write_state(tmp_path, {
            "phase": "orchestration",
            "plan_phase_complete": True,
            "modules_status": [
                {"id": "auth-core", "status": "in-progress"},
                {"id": "token-refresh", "status": "complete"},
            ],
            "verification_loops_remaining": 0,
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 2
        assert parsed is not None
        assert parsed["decision"] == "block"

    def test_blocks_when_verification_loops_remaining(self, tmp_path):
        """Block stop (exit 2) when all modules complete but verification loops remain."""
        self._write_state(tmp_path, {
            "phase": "orchestration",
            "plan_phase_complete": True,
            "modules_status": [
                {"id": "auth-core", "status": "complete"},
                {"id": "token-refresh", "status": "complete"},
            ],
            "verification_loops_remaining": 2,
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 2
        assert parsed is not None
        assert parsed["decision"] == "block"

    def test_allows_when_all_modules_complete_no_verification(self, tmp_path):
        """Allow stop (exit 0) when all modules complete and no verification loops."""
        self._write_state(tmp_path, {
            "phase": "orchestration",
            "plan_phase_complete": True,
            "modules_status": [
                {"id": "auth-core", "status": "complete"},
                {"id": "token-refresh", "status": "complete"},
            ],
            "verification_loops_remaining": 0,
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0
        if parsed is not None:
            assert parsed["decision"] == "allow"


class TestUnknownPhase:
    """When phase is unknown, the script should allow stop."""

    def _write_state(self, tmp_path, state_data):
        state_dir = tmp_path / ".emasoft"
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / "orchestration-state.json"
        state_file.write_text(json.dumps(state_data), encoding="utf-8")
        return state_file

    def test_allows_stop_on_unknown_phase(self, tmp_path):
        """Allow stop (exit 0) when phase is an unrecognized value."""
        self._write_state(tmp_path, {
            "phase": "unknown_phase_xyz",
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0
        if parsed is not None:
            assert parsed["decision"] == "allow"


class TestOutputFormat:
    """Verify the JSON output contains all required fields."""

    def _write_state(self, tmp_path, state_data):
        state_dir = tmp_path / ".emasoft"
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / "orchestration-state.json"
        state_file.write_text(json.dumps(state_data), encoding="utf-8")
        return state_file

    def test_block_output_has_required_fields(self, tmp_path):
        """Block output must contain decision, reason, systemMessage, outputToUser."""
        self._write_state(tmp_path, {
            "phase": "plan",
            "plan_phase_complete": False,
        })
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 2
        assert parsed is not None
        assert "decision" in parsed
        assert "reason" in parsed
        assert "systemMessage" in parsed
        assert "outputToUser" in parsed

    def test_allow_output_has_decision(self, tmp_path):
        """Allow output must contain decision field."""
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0
        if parsed is not None:
            assert "decision" in parsed
            assert parsed["decision"] == "allow"


class TestCorruptStateFile:
    """Handle corrupt or invalid state files gracefully."""

    def test_allows_stop_on_corrupt_json(self, tmp_path):
        """Allow stop (exit 0) when state file contains invalid JSON."""
        state_dir = tmp_path / ".emasoft"
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / "orchestration-state.json"
        state_file.write_text("this is not json {{{", encoding="utf-8")
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0

    def test_allows_stop_on_empty_state(self, tmp_path):
        """Allow stop (exit 0) when state file is empty."""
        state_dir = tmp_path / ".emasoft"
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / "orchestration-state.json"
        state_file.write_text("", encoding="utf-8")
        code, parsed, stdout, stderr = run_script(tmp_path)
        assert code == 0
