#!/usr/bin/env python3
"""The release must carry the tag Claude Code's dependency resolver looks for.

A plugin that depends on this one declares
`{"name": "ai-maestro-orchestrator-agent", "version": "^1.9.0"}`. Claude Code
resolves that by listing THIS repo's tags, filtering to those starting with
`ai-maestro-orchestrator-agent--v`, and taking the highest one satisfying the
range (https://code.claude.com/docs/en/plugin-dependencies.md, since CC 2.1.110).

The plain `v{version}` tag does not match that filter. Without the
`{name}--v{version}` tag, every constrained dependent fails to install with
"no git tag satisfying <range>" while the repo is visibly full of tags — a
silent, total outage for downstream plugins (TRDD-JT3U4ZVM, issue #28). These
tests pin the two halves that must hold: the tag NAME is derived from the
manifest, and it is pushed atomically with the release.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import publish  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def test_plugin_name_comes_from_the_manifest_not_the_directory():
    """get_plugin_name reads the manifest `name`, not the repo/dir name."""
    # The resolver filters on the manifest's `name`, and a repo/dir name can
    # differ from it — so reading the manifest is load-bearing, not cosmetic.
    assert publish.get_plugin_name(ROOT) == "ai-maestro-orchestrator-agent"


def test_plugin_name_is_none_when_there_is_no_manifest(tmp_path):
    """get_plugin_name returns None for a directory with no plugin.json."""
    assert publish.get_plugin_name(tmp_path) is None


def test_dependency_tag_has_the_name_prefix_the_resolver_filters_on():
    """The derived dep tag starts with `{name}--v` and differs from `v{version}`."""
    name = publish.get_plugin_name(ROOT)
    version = publish.get_current_version(ROOT)
    dep_tag = f"{name}--v{version}"
    assert dep_tag.startswith("ai-maestro-orchestrator-agent--v")
    # ...and it is NOT the plain release tag, which is what we shipped for
    # years and what the resolver ignores.
    assert dep_tag != f"v{version}"


def test_publish_pushes_the_dependency_tag_atomically_with_the_release():
    """publish.py pushes HEAD + release tag + dep tag in one --atomic push."""
    # Pins the fix at the point it actually matters. A future edit that creates
    # the tag but forgets to push it leaves the release unresolvable downstream,
    # which is indistinguishable from not tagging at all.
    src = (ROOT / "scripts" / "publish.py").read_text(encoding="utf-8")
    assert '"git", "push", "--atomic", "origin", "HEAD", tag, dep_tag' in src


def test_publish_never_passes_a_tag_name_where_the_cli_wants_a_path():
    """publish.py must not call `claude plugin tag <tag>` (positional arg is a PATH)."""
    # `claude plugin tag [options] [path]` takes a PATH; passing the tag name
    # and discarding the result with check=False silently does nothing for
    # every release. This repo creates the tag with git directly instead.
    src = (ROOT / "scripts" / "publish.py").read_text(encoding="utf-8")
    assert '"claude", "plugin", "tag", tag' not in src


if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-q", __file__]))
