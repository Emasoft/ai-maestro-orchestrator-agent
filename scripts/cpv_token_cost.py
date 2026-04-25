#!/usr/bin/env python3
"""CPV Token Cost Reporter — accurate per-API-call token measurement.

Parses a Claude Code agent transcript (JSONL) to sum the full usage breakdown
(input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens)
from every assistant message, then computes exact cost using per-model pricing.

Dual-mode:
  1. SubagentStop hook: reads hook JSON from stdin, parses agent_transcript_path,
     outputs {"systemMessage": cost_summary} for display in orchestrator context.
  2. CLI: uv run python scripts/cpv_token_cost.py --transcript /path/to/agent.jsonl
  3. Library: from scripts.cpv_token_cost import parse_transcript, estimate_cost
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ── Per-model pricing (USD per million tokens, as of 2025-12) ──
MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-6":   {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    "claude-opus-4-5":   {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    "claude-sonnet-4-6": {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "claude-sonnet-4-5": {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "claude-haiku-4-5":  {"input": 1.0,  "output": 5.0,  "cache_write": 1.25,  "cache_read": 0.10},
    "claude-sonnet-4":   {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "claude-opus-4":     {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4-1":   {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-haiku-3-5":  {"input": 0.80, "output": 4.0,  "cache_write": 1.00,  "cache_read": 0.08},
}
DEFAULT_PRICING: dict[str, float] = {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30}


def get_pricing(model_name: str) -> dict[str, float]:
    """Look up pricing for a model name, with fuzzy matching."""
    if not model_name:
        return DEFAULT_PRICING
    if model_name in MODEL_PRICING:
        return MODEL_PRICING[model_name]
    # Try prefix/substring match
    for key, pricing in MODEL_PRICING.items():
        if key in model_name or model_name.startswith(key):
            return pricing
    # Fuzzy family match
    ml = model_name.lower()
    if "opus" in ml and ("4-6" in ml or "4.6" in ml):
        return MODEL_PRICING["claude-opus-4-6"]
    if "opus" in ml and ("4-5" in ml or "4.5" in ml):
        return MODEL_PRICING["claude-opus-4-5"]
    if "opus" in ml:
        return MODEL_PRICING["claude-opus-4-1"]
    if "sonnet" in ml:
        return MODEL_PRICING["claude-sonnet-4-6"]
    if "haiku" in ml:
        return MODEL_PRICING["claude-haiku-4-5"]
    return DEFAULT_PRICING


class TokenUsage:
    """Token usage summary from a parsed transcript."""

    __slots__ = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                 "cache_read_input_tokens", "message_count", "model")

    def __init__(self) -> None:
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.cache_creation_input_tokens: int = 0
        self.cache_read_input_tokens: int = 0
        self.message_count: int = 0
        self.model: str = "unknown"

    def to_dict(self) -> dict[str, int | str]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "message_count": self.message_count,
            "model": self.model,
        }

    def total_tokens(self) -> int:
        return (self.input_tokens + self.output_tokens
                + self.cache_creation_input_tokens + self.cache_read_input_tokens)


def parse_transcript(path: str | Path) -> TokenUsage:
    """Parse a JSONL transcript and sum token usage from all assistant messages."""
    result = TokenUsage()
    model_counts: dict[str, int] = {}
    seen_ids: set[str] = set()

    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") != "assistant":
                    continue
                msg = entry.get("message", {})
                if not isinstance(msg, dict):
                    continue

                # Deduplicate by message id
                mid = msg.get("id", "")
                if mid:
                    if mid in seen_ids:
                        continue
                    seen_ids.add(mid)

                usage = msg.get("usage", {})
                if not usage:
                    continue

                result.input_tokens += usage.get("input_tokens", 0)
                result.output_tokens += usage.get("output_tokens", 0)
                result.cache_creation_input_tokens += usage.get("cache_creation_input_tokens", 0)
                result.cache_read_input_tokens += usage.get("cache_read_input_tokens", 0)
                result.message_count += 1

                model = msg.get("model", "unknown")
                model_counts[model] = model_counts.get(model, 0) + 1
    except (OSError, IOError):
        pass

    # Most-used model
    if model_counts:
        result.model = max(model_counts, key=lambda m: model_counts[m])
    return result


def estimate_cost(usage: TokenUsage, model: str = "") -> float:
    """Compute exact USD cost from the 4-category token breakdown."""
    p = get_pricing(model or usage.model)
    return (
        (usage.input_tokens / 1e6) * p["input"]
        + (usage.output_tokens / 1e6) * p["output"]
        + (usage.cache_creation_input_tokens / 1e6) * p["cache_write"]
        + (usage.cache_read_input_tokens / 1e6) * p["cache_read"]
    )


def fmt_tok(n: int) -> str:
    """Format token count with K/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1e6:.1f}M"
    if n >= 1_000:
        return f"{n / 1e3:.1f}K"
    return str(n)


def format_cost_line(usage: TokenUsage, model: str = "") -> str:
    """One-line cost summary for terminal display."""
    cost = estimate_cost(usage, model)
    m = model or usage.model
    # Shorten model name for display
    short_model = m.replace("claude-", "").split("-2")[0]
    return (
        f"Tokens: {fmt_tok(usage.total_tokens())} "
        f"(in:{fmt_tok(usage.input_tokens)} out:{fmt_tok(usage.output_tokens)} "
        f"cw:{fmt_tok(usage.cache_creation_input_tokens)} cr:{fmt_tok(usage.cache_read_input_tokens)}) "
        f"| Cost: ${cost:.4f} | Model: {short_model}"
    )


def main() -> int:
    """Entry point — hook mode (stdin JSON) or CLI mode (--transcript)."""
    # CLI mode: --transcript PATH
    if "--transcript" in sys.argv:
        idx = sys.argv.index("--transcript")
        if idx + 1 >= len(sys.argv):
            print("Error: --transcript requires a path argument", file=sys.stderr)
            return 1
        transcript_path = sys.argv[idx + 1]
        if not Path(transcript_path).exists():
            print(f"Error: transcript not found: {transcript_path}", file=sys.stderr)
            return 1
        usage = parse_transcript(transcript_path)
        if usage.message_count == 0:
            print("No assistant messages found in transcript.", file=sys.stderr)
            return 1
        print(format_cost_line(usage))
        return 0

    # Hook mode: read JSON from stdin
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 1

    # Get the agent's own transcript path (SubagentStop provides this)
    agent_transcript = hook_input.get("agent_transcript_path", "")
    session_transcript = hook_input.get("transcript_path", "")

    # Prefer agent transcript; fall back to session transcript
    transcript = ""
    if agent_transcript and Path(agent_transcript).exists():
        transcript = agent_transcript
    elif session_transcript and Path(session_transcript).exists():
        transcript = session_transcript

    if not transcript:
        return 0

    usage = parse_transcript(transcript)
    if usage.message_count == 0:
        return 0

    cost_line = format_cost_line(usage)
    # Output as systemMessage so it appears in the orchestrator's context
    print(json.dumps({"systemMessage": f"  {cost_line}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
