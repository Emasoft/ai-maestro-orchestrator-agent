#!/usr/bin/env python3
"""Gitignore-aware file filtering for plugin validation.

Provides a GitignoreFilter class that loads .gitignore patterns once
and exposes helpers to filter os.walk, rglob, and iterdir results.
All validators should use this to skip gitignored files/directories.

Usage:
    gi = GitignoreFilter(plugin_root)
    for path in gi.walk_files(plugin_root, skip_dirs={"__pycache__"}):
        # path is a Path object, gitignored files are excluded
        ...

    for path in gi.rglob(plugin_root, "*.pyc"):
        # gitignored matches excluded
        ...
"""

from __future__ import annotations

from pathlib import Path

from cpv_validation_common import is_path_gitignored, parse_gitignore


class GitignoreFilter:
    """Gitignore-aware file filter — loads patterns once, reuses for all scans.

    Uses pathlib exclusively for cross-platform compatibility.
    """

    def __init__(self, plugin_root: Path) -> None:
        self.root = plugin_root.resolve()
        gitignore_path = self.root / ".gitignore"
        self.patterns = parse_gitignore(gitignore_path) if gitignore_path.is_file() else []

    def is_ignored(self, path: Path) -> bool:
        """Check if a path should be skipped based on .gitignore patterns."""
        if not self.patterns:
            return False
        try:
            # Use PurePosixPath-style forward slashes for gitignore matching
            rel = path.relative_to(self.root).as_posix()
        except ValueError:
            return False
        return is_path_gitignored(rel, self.patterns)

    def is_dir_ignored(self, dirpath: Path) -> bool:
        """Check if a directory should be skipped — appends trailing / for dir-only patterns."""
        if not self.patterns:
            return False
        try:
            rel = dirpath.relative_to(self.root).as_posix()
        except ValueError:
            return False
        # Check both with and without trailing slash (gitignore treats dir/ specially)
        return is_path_gitignored(rel, self.patterns) or is_path_gitignored(rel + "/", self.patterns)

    def _walk_pathlib(
        self,
        directory: Path,
        skip_dirs: set[str],
        skip_hidden: bool,
    ):
        """Recursive directory walk using pathlib only (cross-platform).

        Yields (dirpath: Path, subdirs: list[str], files: list[str]).
        Compatible with os.walk() return signature but uses Path objects.
        """
        subdirs: list[str] = []
        files: list[str] = []

        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_dir():
                if skip_hidden and entry.name.startswith("."):
                    continue
                if entry.name in skip_dirs:
                    continue
                if self.is_dir_ignored(entry):
                    continue
                subdirs.append(entry.name)
            elif entry.is_file():
                if not self.is_ignored(entry):
                    files.append(entry.name)

        yield str(directory), subdirs, files

        # Recurse into non-ignored subdirectories
        for subdir_name in subdirs:
            yield from self._walk_pathlib(directory / subdir_name, skip_dirs, skip_hidden)

    def walk(
        self,
        root: Path | None = None,
        skip_dirs: set[str] | None = None,
        skip_hidden: bool = True,
    ):
        """Gitignore-aware directory walk using pathlib (cross-platform).

        Yields (dirpath: str, dirnames: list[str], filenames: list[str]).
        Automatically prunes gitignored directories and files.
        """
        root = root or self.root
        extra_skip = skip_dirs or set()
        yield from self._walk_pathlib(root, extra_skip, skip_hidden)

    def rglob(self, pattern: str, root: Path | None = None):
        """Gitignore-aware rglob — yields Path objects that are not gitignored."""
        root = root or self.root
        for path in root.rglob(pattern):
            if not self.is_ignored(path):
                yield path

    def iterdir(self, directory: Path | None = None, skip_hidden: bool = False):
        """Gitignore-aware iterdir — yields Path objects that are not gitignored."""
        directory = directory or self.root
        for item in directory.iterdir():
            if skip_hidden and item.name.startswith("."):
                continue
            if not self.is_ignored(item):
                yield item
