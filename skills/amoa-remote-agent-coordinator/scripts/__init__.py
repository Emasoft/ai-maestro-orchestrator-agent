#!/usr/bin/env python3
"""Package marker for the amoa-remote-agent-coordinator skill scripts.

WHY this file exists: the repo-wide type check (mypy, run by the CPV lint
engine over every scripts/ tree) maps module names from file basenames.
Two scripts here (validate_skill.py, amoa_register_agent.py) share their
basename with files in the top-level scripts/ directory; without a package
marker both map to the same bare module name and mypy aborts with
"Duplicate module named". With this marker the scripts in THIS directory
become the distinct `scripts.<name>` modules of this skill-local package,
while the top-level ones stay bare top-level modules — no duplicates, and
both copies keep being type-checked. The scripts remain directly runnable;
nothing imports this package at runtime.
"""
