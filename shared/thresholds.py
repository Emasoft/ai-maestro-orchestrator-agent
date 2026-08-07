"""
thresholds.py - Shared constants for Orchestrator Agent.

These thresholds configure behavior for task distribution,
agent coordination, and progress monitoring.
"""

import os

# ── Subagent concurrency and nesting ──
#
# THESE ARE REFERENCE VALUES, NOT ENFORCEMENT. No script reads them and nothing
# in AMOA can refuse an over-cap dispatch — the orchestrator honors them by
# reading the prose in
# skills/amoa-orchestration-guardrails/references/subagent-platform-limits.md.
# When a platform limit changes, update BOTH: changing only these constants
# changes nothing about how the orchestrator actually behaves.
#
# Claude Code caps concurrently-running subagents (20 by default since CC
# 2.1.217, overridable via CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS). The separate
# per-session cap of 200 total spawns was REMOVED in CC 2.1.224, so lifetime
# spawn count is no longer bounded for us — concurrency is the only live limit.
#
# WHY we deliberately sit BELOW the platform cap rather than matching it: at
# exactly the cap the orchestrator saturates the platform's own limit, leaving
# no slot for a subagent spawned by anything else in the session. Excess spawns
# then queue silently rather than erroring, so the orchestrator sees a stalled
# agent and cannot distinguish it from a slow one.
PLATFORM_MAX_CONCURRENT_SUBAGENTS = int(
    os.environ.get("CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS", "20")
)
CONCURRENCY_HEADROOM = 4
MAX_CONCURRENT_AGENTS = max(1, PLATFORM_MAX_CONCURRENT_SUBAGENTS - CONCURRENCY_HEADROOM)

# Subagents may themselves spawn subagents up to depth 3 by default (CC 2.1.219;
# nesting was disabled outright in CC 2.1.217, and depth 1 before that). Depth 3
# multiplied by the concurrency cap means one dispatch can fan out far wider than
# the orchestrator's accounting expects, so agents WE bundle must not fan out
# further — enforce this in every subagent prompt, not just here.
MAX_AGENT_SPAWN_DEPTH = 3
BUNDLED_AGENTS_MAY_FAN_OUT = False

# Task management
MAX_TASKS_PER_MODULE = 10
TASK_TIMEOUT_MINUTES = 30

# Polling configuration
POLL_INTERVAL_SECONDS = 30
MAX_POLL_RETRIES = 3
POLL_TIMEOUT_SECONDS = 10

# Verification thresholds
MAX_VERIFICATION_LOOPS = 4
VERIFICATION_TIMEOUT_SECONDS = 60

# Module management
MAX_MODULES = 50
MODULE_PRIORITY_LEVELS = 5

# Agent management
AGENT_REGISTRATION_TIMEOUT_SECONDS = 30
AGENT_HEARTBEAT_INTERVAL_SECONDS = 60
MAX_AGENT_FAILURES_BEFORE_REASSIGN = 3

# Stop hook configuration
STOP_VERIFICATION_LOOPS = 4


class VERIFICATION:
    """Verification thresholds for statistical and evidence validation.

    WHY: Centralizes verification constants used across verification-patterns scripts.
    WHY: Class-based access (VERIFICATION.ATTR) provides clear namespace separation.
    """

    # Statistical hypothesis testing defaults (A/B testing)
    STATISTICAL_ALPHA: float = 0.05  # Significance level (Type I error rate, 95% confidence)
    STATISTICAL_POWER: float = 0.80  # Statistical power (1 - Type II error rate)
    STATISTICAL_MDE: float = 0.05  # Minimum Detectable Effect (5%)

    # Evidence requirements
    MIN_EVIDENCE_ITEMS: int = 1  # Minimum evidence items required per verification

    # Requirements coverage
    MIN_REQUIREMENTS_COVERAGE: float = 0.80  # 80% minimum coverage threshold


class TIMEOUTS:
    """Timeout constants for various operations.

    WHY: Centralizes timeout values for consistent behavior across scripts.
    WHY: Class-based access (TIMEOUTS.ATTR) provides clear namespace separation.
    """

    # Git operations timeout (seconds)
    GIT: int = 30

    # API operations timeout (seconds)
    API: int = 60

    # File operations timeout (seconds)
    FILE: int = 10

    # Network operations timeout (seconds)
    NETWORK: int = 30
