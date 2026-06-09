#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""AMOA memory helper — the executable core of the memory skills.

Implements the AI-Maestro markdown-memory protocol (rules/memory-protocol.md)
for the ORCHESTRATOR role:

  recall  — symptom-ranked note recall. Delegates to `memgrep recall` when the
            binary is on PATH; otherwise degrades to a built-in plain-text
            fallback (description/title/tags surface match ranked first, then
            body-only matches) so recall degrades, never breaks.
  write   — author a schema-valid memory note (name/description/metadata
            frontmatter + body) and append the MEMORY.md index line.

Stdlib-only on purpose: the fallback path must work on a machine with nothing
installed but Python. The frontmatter writer/parser below handles exactly the
flat note schema from the memory protocol — it is NOT a general YAML parser,
which is why notes are always written through this script (one source of
truth for the schema).

Exit codes: 0 = success (recall with zero matches is still success);
2 = bad invocation/validation; 3 = refused (duplicate note without --update).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

VALID_TYPES = ("user", "feedback", "project", "reference")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")


def default_memdir() -> Path:
    """Resolve the harness per-project memory dir, falling back to ./memory.

    Mirrors the janitor reference: $HOME/.claude/projects/<dashed-cwd>/memory
    when it exists, else <git-root-or-cwd>/memory.
    """
    cwd = Path.cwd().resolve()
    slug = str(cwd).replace("/", "-")
    harness_dir = Path.home() / ".claude" / "projects" / slug / "memory"
    if harness_dir.is_dir():
        return harness_dir
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(root) / "memory"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return cwd / "memory"


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Extract flat `key: value` pairs from a note's YAML frontmatter block.

    Handles the memory-note schema only (flat keys + one nested `metadata:`
    level). Values keep their unquoted form; surrounding quotes are stripped.
    """
    fields: dict[str, str] = {}
    if not text.startswith("---"):
        return fields
    end = text.find("\n---", 3)
    if end == -1:
        return fields
    for line in text[3:end].splitlines():
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip().strip("\"'")
        if value:
            fields[key] = value
    return fields


def cmd_recall(args: argparse.Namespace) -> int:
    """Recall notes matching a symptom: memgrep when present, fallback otherwise."""
    memdir = Path(args.memdir) if args.memdir else default_memdir()
    if not memdir.is_dir():
        # An absent memory dir means "no memories yet" — empty result, not error.
        return 0

    memgrep = shutil.which("memgrep")
    if memgrep and not args.no_memgrep:
        cmd = [memgrep, "recall", args.symptom, str(memdir), "--top", str(args.top)]
        return subprocess.run(cmd).returncode

    # ── Fallback: degrade, never break ──
    # Rank surface (description/title/tags/name) matches above body-only
    # matches, like memgrep's precision-first behavior; within a band, rank
    # by number of distinct symptom words hit.
    words = [w for w in re.split(r"\W+", args.symptom.lower()) if len(w) > 2]
    if not words:
        return 0
    surface_hits: list[tuple[int, str, str]] = []
    body_hits: list[tuple[int, str, str]] = []
    for note in sorted(memdir.rglob("*.md")):
        if note.name in ("MEMORY.md", "memory-index.md"):
            continue
        try:
            text = note.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_frontmatter(text)
        surface = " ".join(
            fm.get(k, "") for k in ("description", "title", "tags", "name")
        ).lower()
        body = text.lower()
        s_score = sum(1 for w in words if w in surface)
        b_score = sum(1 for w in words if w in body)
        desc = fm.get("description", "")
        if s_score > 0:
            surface_hits.append((s_score, str(note), desc))
        elif b_score > 0:
            body_hits.append((b_score, str(note), desc))
    ranked = sorted(surface_hits, key=lambda t: -t[0]) or sorted(
        body_hits, key=lambda t: -t[0]
    )
    for _, path, desc in ranked[: args.top]:
        print(f"{path} — {desc}" if desc else path)
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    """Write a schema-valid memory note and append its MEMORY.md index line."""
    if args.type not in VALID_TYPES:
        print(
            f"error: type must be one of {', '.join(VALID_TYPES)} (got {args.type!r})",
            file=sys.stderr,
        )
        return 2
    if not SLUG_RE.match(args.slug):
        print(
            f"error: slug must be kebab/snake-case (got {args.slug!r})", file=sys.stderr
        )
        return 2
    if not args.description.strip():
        print("error: description must not be empty", file=sys.stderr)
        return 2

    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    if not (body or "").strip():
        print(
            "error: body must not be empty (use --body or --body-file)", file=sys.stderr
        )
        return 2

    memdir = Path(args.memdir) if args.memdir else default_memdir()
    memdir.mkdir(parents=True, exist_ok=True)

    name = f"{args.type}_{args.slug}"
    note_path = memdir / f"{name}.md"
    if note_path.exists() and not args.update:
        print(
            f"refused: {note_path} already exists — update the existing note "
            "(re-run with --update) instead of duplicating it",
            file=sys.stderr,
        )
        return 3

    description = args.description.replace('"', "'").strip()
    note = (
        "---\n"
        f"name: {name}\n"
        f'description: "{description}"\n'
        "metadata:\n"
        "  node_type: memory\n"
        f"  type: {args.type}\n"
        "---\n\n"
        f"{body.strip()}\n"
    )
    tmp = note_path.with_suffix(".md.tmp")
    tmp.write_text(note, encoding="utf-8")
    os.replace(tmp, note_path)

    # Append the index line unless an entry for this note already exists.
    index = memdir / "MEMORY.md"
    title = args.title or args.slug.replace("-", " ").replace("_", " ").capitalize()
    line = f"- [{title}]({name}.md) — {args.hook or description}\n"
    existing = index.read_text(encoding="utf-8") if index.exists() else ""
    if f"({name}.md)" not in existing:
        with index.open("a", encoding="utf-8") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write(line)

    print(note_path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_recall = sub.add_parser("recall", help="symptom-ranked note recall")
    p_recall.add_argument("symptom", help="the SYMPTOM in the user's/error's words")
    p_recall.add_argument(
        "--memdir", help="memory dir (default: harness per-project dir)"
    )
    p_recall.add_argument("--top", type=int, default=10, help="max notes to return")
    p_recall.add_argument(
        "--no-memgrep",
        action="store_true",
        help="force the built-in fallback even when memgrep is installed",
    )
    p_recall.set_defaults(func=cmd_recall)

    p_write = sub.add_parser("write", help="author a schema-valid memory note")
    p_write.add_argument(
        "--type", required=True, help="user|feedback|project|reference"
    )
    p_write.add_argument(
        "--slug", required=True, help="kebab-case slug (no type prefix)"
    )
    p_write.add_argument(
        "--description",
        required=True,
        help="SYMPTOM-indexed description — the words a future session will search with",
    )
    p_write.add_argument("--body", help="the one fact (inline)")
    p_write.add_argument("--body-file", help="read the body from a file instead")
    p_write.add_argument("--title", help="index title (default: derived from slug)")
    p_write.add_argument(
        "--hook", help="MEMORY.md one-line hook (default: description)"
    )
    p_write.add_argument(
        "--memdir", help="memory dir (default: harness per-project dir)"
    )
    p_write.add_argument(
        "--update", action="store_true", help="allow overwriting an existing note"
    )
    p_write.set_defaults(func=cmd_write)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
