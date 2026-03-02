#!/usr/bin/env python3
"""
smart_exec.py

A “smart runner” that:
- Detects available executors on this machine (uvx/uv, pipx, bunx/bun x, pnpm dlx, npx, npm exec, yarn dlx, deno, docker, pwsh/powershell)
- Chooses the best executor for a requested tool (linter/formatter/type-checker/etc.)
- Executes it via subprocess, preserving exit code

Notes:
- Uses Bun's documented `-p/--package` support when binary name != package name (e.g. @stoplight/spectral -> spectral).  (see: https://bun.com/docs/pm/bunx)
- Uses npm's recommended `npm exec --package=... -- <cmd>` form.  (see: https://docs.npmjs.com/cli/v8/commands/npm-exec)
- Supports Deno built-ins (`deno lint/fmt/check`) as truly “no install” tools, plus `deno run npm:` for npm CLIs
- Support PowerShell “download to temp + import” execution for module-based tools (e.g. PSScriptAnalyzer)
- Support special commands: `executors`, `db`, and `which` subcommands + JSON output + dry-run mode

Examples:
  ./smart_exec.py executors
  ./smart_exec.py db
  ./smart_exec.py which ruff check .
  ./smart_exec.py run ruff check .
  ./smart_exec.py run eslint .
  ./smart_exec.py run prettier --check .
  ./smart_exec.py run npm-package-json-lint .
  ./smart_exec.py run deno-fmt -- --check
  ./smart_exec.py run Invoke-ScriptAnalyzer -- -Path . -Recurse

Notes:
- “No install” here means: no project dependency changes and no global install of the tool itself.
  Executors may still download/cache packages/binaries (npm cache, uv cache, docker images, etc.).
- Heuristics are adjustable: edit TOOL_DB and PRIORITY.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass

# ----------------------------
# Data model
# ----------------------------


@dataclass(frozen=True)
class ToolSpec:
    # What user types (logical name)
    name: str
    # ecosystem hint: "python", "node", "deno_builtin", "powershell_module", "native"
    ecosystem: str
    # package to fetch (PyPI or npm); None for built-ins
    package: str | None = None
    # actual command/binary to invoke (may differ from package)
    command: str | None = None
    # whether to prefer "latest" (where supported)
    prefer_latest: bool = True
    # optional docker fallback: (image, argv_prefix)
    docker: tuple[str, list[str]] | None = None


# A starting tool database. Extend freely.
TOOL_DB: dict[str, ToolSpec] = {
    # ---- Python tools (PyPI) ----
    "ruff": ToolSpec("ruff", "python", package="ruff", command="ruff"),
    "mypy": ToolSpec("mypy", "python", package="mypy", command="mypy"),
    "black": ToolSpec("black", "python", package="black", command="black"),
    "isort": ToolSpec("isort", "python", package="isort", command="isort"),
    "pyright": ToolSpec("pyright", "python", package="pyright", command="pyright"),
    "sqlfluff": ToolSpec("sqlfluff", "python", package="sqlfluff", command="sqlfluff"),
    "yamllint": ToolSpec("yamllint", "python", package="yamllint", command="yamllint"),
    # ---- Node tools (npm) ----
    "eslint": ToolSpec("eslint", "node", package="eslint", command="eslint"),
    "prettier": ToolSpec("prettier", "node", package="prettier", command="prettier"),
    "stylelint": ToolSpec("stylelint", "node", package="stylelint", command="stylelint"),
    "htmlhint": ToolSpec("htmlhint", "node", package="htmlhint", command="htmlhint"),
    "markdownlint-cli2": ToolSpec(
        "markdownlint-cli2", "node", package="markdownlint-cli2", command="markdownlint-cli2"
    ),
    "textlint": ToolSpec("textlint", "node", package="textlint", command="textlint"),
    "jsonlint": ToolSpec("jsonlint", "node", package="jsonlint", command="jsonlint"),
    "yaml-lint": ToolSpec("yaml-lint", "node", package="yaml-lint", command="yaml-lint"),
    "biome": ToolSpec("biome", "node", package="@biomejs/biome", command="biome"),
    "@biomejs/biome": ToolSpec("@biomejs/biome", "node", package="@biomejs/biome", command="biome"),
    "spectral": ToolSpec("spectral", "node", package="@stoplight/spectral", command="spectral"),
    "@stoplight/spectral": ToolSpec("@stoplight/spectral", "node", package="@stoplight/spectral", command="spectral"),
    # npm-package-json-lint: CLI name != package name
    "npm-package-json-lint": ToolSpec(
        "npm-package-json-lint", "node", package="npm-package-json-lint", command="npmPkgJsonLint"
    ),
    "npmPkgJsonLint": ToolSpec("npmPkgJsonLint", "node", package="npm-package-json-lint", command="npmPkgJsonLint"),
    "sort-package-json": ToolSpec(
        "sort-package-json", "node", package="sort-package-json", command="sort-package-json"
    ),
    "tsc": ToolSpec("tsc", "node", package="typescript", command="tsc"),
    # ---- Deno built-ins ----
    "deno-lint": ToolSpec("deno-lint", "deno_builtin", package=None, command="lint", prefer_latest=False),
    "deno-fmt": ToolSpec("deno-fmt", "deno_builtin", package=None, command="fmt", prefer_latest=False),
    "deno-check": ToolSpec("deno-check", "deno_builtin", package=None, command="check", prefer_latest=False),
    # ---- Native-ish tools (prefer wrappers; docker fallback included) ----
    "shellcheck": ToolSpec(
        "shellcheck",
        "native",
        package="shellcheck",  # npm wrapper exists
        command="shellcheck",
        docker=("koalaman/shellcheck:stable", ["shellcheck"]),
    ),
    "hadolint": ToolSpec(
        "hadolint",
        "native",
        package="hadolint",  # npm wrapper exists
        command="hadolint",
        docker=("hadolint/hadolint", ["hadolint"]),
    ),
    "xmllint": ToolSpec(
        "xmllint",
        "native",
        package=None,
        command="xmllint",
        docker=("alpine", ["sh", "-lc", "apk add --no-cache libxml2-utils >/dev/null && xmllint --noout"]),
    ),
    # ---- PowerShell module tools ----
    "PSScriptAnalyzer": ToolSpec(
        "PSScriptAnalyzer", "powershell_module", package="PSScriptAnalyzer", command="Invoke-ScriptAnalyzer"
    ),
    "Invoke-ScriptAnalyzer": ToolSpec(
        "Invoke-ScriptAnalyzer", "powershell_module", package="PSScriptAnalyzer", command="Invoke-ScriptAnalyzer"
    ),
}


# Executor preference per ecosystem
PRIORITY: dict[str, list[str]] = {
    "python": ["uvx", "uv", "pipx"],
    "node": ["bunx", "pnpm", "npx", "npm", "yarn", "deno"],
    "deno_builtin": ["deno"],
    "native": ["direct", "bunx", "pnpm", "npx", "npm", "yarn", "deno", "docker"],
    "powershell_module": ["pwsh", "powershell"],
}


# ----------------------------
# Executor detection
# ----------------------------


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def have(cmd: str) -> bool:
    return which(cmd) is not None


def detect_executors() -> dict[str, bool]:
    # bunx may be an executable, or `bun x` is available via bun itself
    bunx_ok = have("bunx") or have("bun")
    return {
        "uvx": have("uvx"),
        "uv": have("uv"),
        "pipx": have("pipx"),
        "bunx": bunx_ok,
        "pnpm": have("pnpm"),
        "npx": have("npx"),
        "npm": have("npm"),
        "yarn": have("yarn"),
        "deno": have("deno"),
        "docker": have("docker"),
        "pwsh": have("pwsh"),
        "powershell": have("powershell"),  # Windows PowerShell 5.1
    }


def get_version(cmd: list[str]) -> str | None:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if p.returncode != 0:
            return None
        out = (p.stdout or "").strip().splitlines()
        return out[0].strip() if out else None
    except Exception:
        return None


def executor_versions() -> dict[str, str | None]:
    v: dict[str, str | None] = {}
    if have("uvx"):
        v["uvx"] = get_version(["uvx", "--version"])
    elif have("uv"):
        v["uv"] = get_version(["uv", "--version"])
    if have("pipx"):
        v["pipx"] = get_version(["pipx", "--version"])
    if have("bun"):
        v["bun"] = get_version(["bun", "--version"])
    if have("pnpm"):
        v["pnpm"] = get_version(["pnpm", "--version"])
    if have("npm"):
        v["npm"] = get_version(["npm", "--version"])
    if have("npx"):
        v["npx"] = get_version(["npx", "--version"])
    if have("yarn"):
        v["yarn"] = get_version(["yarn", "--version"])
    if have("deno"):
        v["deno"] = get_version(["deno", "--version"])
    if have("docker"):
        v["docker"] = get_version(["docker", "--version"])
    if have("pwsh"):
        v["pwsh"] = get_version(["pwsh", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])
    if have("powershell"):
        v["powershell"] = get_version(["powershell", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])
    return v


# ----------------------------
# Command builders
# ----------------------------


def bunx_argv(pkg: str, cmd: str, tool_args: list[str]) -> list[str]:
    # Bun supports -p/--package for package != command. (see: https://bun.com/docs/pm/bunx )
    base = ["bunx"] if have("bunx") else ["bun", "x"]
    if cmd == pkg:
        return base + [pkg] + tool_args
    return base + ["-p", pkg, cmd] + tool_args


def pnpm_dlx_argv(pkg: str, cmd: str, tool_args: list[str]) -> list[str]:
    # pnpm dlx runs the default bin; if cmd differs, place cmd explicitly.
    if cmd == pkg:
        return ["pnpm", "dlx", pkg] + tool_args
    return ["pnpm", "dlx", pkg, cmd] + tool_args


def yarn_dlx_argv(pkg: str, cmd: str, tool_args: list[str]) -> list[str]:
    if cmd == pkg:
        return ["yarn", "dlx", pkg] + tool_args
    return ["yarn", "dlx", "-p", pkg, cmd] + tool_args


def npx_argv(pkg: str, cmd: str, tool_args: list[str]) -> list[str]:
    if cmd == pkg:
        return ["npx", "--yes", pkg] + tool_args
    return ["npx", "--yes", "-p", pkg, cmd] + tool_args


def npm_exec_argv(pkg: str, cmd: str, tool_args: list[str]) -> list[str]:
    # npm exec --package=<pkg> -- <cmd> [args...]   (see: https://docs.npmjs.com/cli/v8/commands/npm-exec )
    return ["npm", "exec", "--yes", f"--package={pkg}", "--", cmd] + tool_args


def deno_npm_argv(pkg: str, cmd: str, tool_args: list[str], latest: bool = True) -> list[str]:
    ver = "@latest" if latest else ""
    spec = f"npm:{pkg}{ver}"
    return ["deno", "run", "-A", spec, "--", cmd] + tool_args


def uvx_argv(pkg: str, cmd: str, tool_args: list[str], latest: bool = True) -> list[str]:
    # uvx TOOL@latest ... (when pkg==cmd), else uvx --from <pkg> <cmd> ...
    if have("uvx"):
        if pkg == cmd:
            suffix = "@latest" if latest else ""
            return ["uvx", f"{pkg}{suffix}"] + tool_args
        return ["uvx", "--from", pkg, cmd] + tool_args

    if have("uv"):
        if pkg == cmd:
            suffix = "@latest" if latest else ""
            return ["uv", "tool", "run", f"{pkg}{suffix}"] + tool_args
        return ["uv", "tool", "run", "--from", pkg, cmd] + tool_args

    raise RuntimeError("uvx/uv not available")


def pipx_run_argv(pkg: str, tool_args: list[str]) -> list[str]:
    # pipx can't reliably pick an arbitrary bin from a package; best effort:
    return ["pipx", "run", pkg] + tool_args


def deno_builtin_argv(subcmd: str, tool_args: list[str]) -> list[str]:
    return ["deno", subcmd] + tool_args


def docker_argv(image: str, prefix: list[str], tool_args: list[str]) -> list[str]:
    cwd = os.getcwd()
    return ["docker", "run", "--rm", "-v", f"{cwd}:/w", "-w", "/w", image] + prefix + tool_args


def ps_quote(s: str) -> str:
    # Single-quote escaping for PowerShell: ' -> ''
    return "'" + s.replace("'", "''") + "'"


def powershell_module_argv(module: str, cmdlet: str, cmdlet_args: list[str]) -> list[str]:
    """
    Download module to temp dir, import it, run cmdlet.
    """
    shell = "pwsh" if have("pwsh") else "powershell"
    if not have(shell):
        raise RuntimeError("No PowerShell found (pwsh or powershell)")

    arg_str = " ".join(ps_quote(a) for a in cmdlet_args)
    ps = f"""
$dir = Join-Path $env:TEMP ("psmods_" + [guid]::NewGuid().ToString("n"))
Save-Module -Name {ps_quote(module)} -Path $dir -Force | Out-Null
$psd1 = Get-ChildItem -Path (Join-Path $dir {ps_quote(module)}) -Recurse -Filter "{module}.psd1" |
  Select-Object -First 1 -ExpandProperty FullName
Import-Module $psd1 -Force | Out-Null
{cmdlet} {arg_str}
"""
    return [shell, "-NoProfile", "-Command", ps.strip()]


# ----------------------------
# Selection logic
# ----------------------------


def resolve_tool(tool_name: str) -> ToolSpec:
    if tool_name in TOOL_DB:
        return TOOL_DB[tool_name]
    # Default guess: node (common for random CLIs); can be overridden via --ecosystem.
    return ToolSpec(name=tool_name, ecosystem="node", package=tool_name, command=tool_name)


def build_argv_for_executor(executor: str, spec: ToolSpec, tool_args: list[str]) -> list[str] | None:
    cmd = spec.command or spec.name
    pkg = spec.package or spec.name

    if executor == "direct":
        return [cmd] + tool_args if have(cmd) else None

    if executor in ("uvx", "uv"):
        if spec.ecosystem != "python":
            return None
        return uvx_argv(pkg, cmd, tool_args, latest=spec.prefer_latest) if (have("uvx") or have("uv")) else None

    if executor == "pipx":
        if spec.ecosystem != "python":
            return None
        if not have("pipx"):
            return None
        # If cmd!=pkg, we pass cmd as first arg (best-effort; uvx is better for cmd!=pkg).
        return pipx_run_argv(pkg, [cmd] + tool_args if cmd != pkg else tool_args)

    if executor == "bunx":
        if spec.ecosystem not in ("node", "native"):
            return None
        return bunx_argv(pkg, cmd, tool_args) if (have("bunx") or have("bun")) else None

    if executor == "pnpm":
        if spec.ecosystem not in ("node", "native"):
            return None
        return pnpm_dlx_argv(pkg, cmd, tool_args) if have("pnpm") else None

    if executor == "npx":
        if spec.ecosystem not in ("node", "native"):
            return None
        return npx_argv(pkg, cmd, tool_args) if have("npx") else None

    if executor == "npm":
        if spec.ecosystem not in ("node", "native"):
            return None
        return npm_exec_argv(pkg, cmd, tool_args) if have("npm") else None

    if executor == "yarn":
        if spec.ecosystem not in ("node", "native"):
            return None
        return yarn_dlx_argv(pkg, cmd, tool_args) if have("yarn") else None

    if executor == "deno":
        if not have("deno"):
            return None
        if spec.ecosystem == "deno_builtin":
            return deno_builtin_argv(cmd, tool_args)
        if spec.ecosystem in ("node", "native"):
            return deno_npm_argv(pkg, cmd, tool_args, latest=spec.prefer_latest)
        return None

    if executor == "docker":
        if not have("docker") or spec.docker is None:
            return None
        image, prefix = spec.docker
        return docker_argv(image, prefix, tool_args)

    if executor in ("pwsh", "powershell"):
        if spec.ecosystem != "powershell_module":
            return None
        if not have(executor):
            return None
        return powershell_module_argv(spec.package or spec.name, cmd, tool_args)

    return None


def choose_best(spec: ToolSpec, tool_args: list[str], executors: dict[str, bool]) -> tuple[list[str], str]:
    # Prefer direct if already available (fast, avoids downloads)
    direct_cmd = spec.command or spec.name
    if have(direct_cmd):
        return [direct_cmd] + tool_args, "direct"

    for ex in PRIORITY.get(spec.ecosystem, []):
        argv = build_argv_for_executor(ex, spec, tool_args)
        if argv is not None:
            return argv, ex

    # Last chance: docker if configured
    if executors.get("docker") and spec.docker is not None:
        argv = build_argv_for_executor("docker", spec, tool_args)
        if argv is not None:
            return argv, "docker"

    raise RuntimeError(f"No suitable executor found for tool '{spec.name}' (ecosystem={spec.ecosystem}).")


# ----------------------------
# CLI
# ----------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="smart_exec.py")
    sub = p.add_subparsers(dest="subcmd", required=True)

    p_run = sub.add_parser("run", help="Run a tool using the best available executor")
    p_run.add_argument("--dry-run", action="store_true", help="Print command and exit without running")
    p_run.add_argument("--json", action="store_true", help="Print selection info as JSON to stdout")
    p_run.add_argument(
        "--ecosystem",
        choices=["python", "node", "native", "deno_builtin", "powershell_module"],
        help="Override the tool ecosystem classification",
    )
    p_run.add_argument("tool", help="Tool to run (e.g. ruff, eslint, shellcheck)")
    p_run.add_argument("tool_args", nargs=argparse.REMAINDER, help="Arguments passed to the tool")

    p_which = sub.add_parser("which", help="Show how the runner would execute a tool")
    p_which.add_argument(
        "--ecosystem",
        choices=["python", "node", "native", "deno_builtin", "powershell_module"],
        help="Override the tool ecosystem classification",
    )
    p_which.add_argument("--json", action="store_true")
    p_which.add_argument("tool", help="Tool to resolve")
    p_which.add_argument("tool_args", nargs=argparse.REMAINDER)

    sub.add_parser("executors", help="List detected executors (availability + versions)")
    p_db = sub.add_parser("db", help="List known tools in the built-in database")
    p_db.add_argument("--json", action="store_true")

    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    ns = parse_args(argv)
    ex = detect_executors()

    if ns.subcmd == "executors":
        info = {"available": ex, "versions": executor_versions(), "platform": platform.platform()}
        print(json.dumps(info, indent=2))
        return 0

    if ns.subcmd == "db":
        if ns.json:
            out = {k: TOOL_DB[k].__dict__ for k in sorted(TOOL_DB)}
            print(json.dumps(out, indent=2))
        else:
            for k in sorted(TOOL_DB):
                t = TOOL_DB[k]
                print(f"{k:24} ecosystem={t.ecosystem:16} package={t.package or '-':22} command={t.command or '-'}")
        return 0

    # which/run
    spec = resolve_tool(ns.tool)
    if getattr(ns, "ecosystem", None):
        spec = ToolSpec(
            name=spec.name,
            ecosystem=ns.ecosystem,
            package=spec.package,
            command=spec.command,
            prefer_latest=spec.prefer_latest,
            docker=spec.docker,
        )

    tool_args = list(ns.tool_args)
    # Strip a single leading '--' (common “end of options” marker)
    if tool_args[:1] == ["--"]:
        tool_args = tool_args[1:]

    try:
        argv2, chosen = choose_best(spec, tool_args, ex)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    payload = {
        "tool": spec.name,
        "ecosystem": spec.ecosystem,
        "chosen_executor": chosen,
        "argv": argv2,
    }

    if ns.subcmd == "which" or getattr(ns, "dry_run", False):
        if getattr(ns, "json", False):
            print(json.dumps(payload, indent=2))
        else:
            print(f"[executor] {chosen}", file=sys.stderr)
            print("[argv] " + " ".join(shlex.quote(a) for a in argv2))
        return 0

    if getattr(ns, "json", False):
        print(json.dumps(payload, indent=2))

    print(f"[executor] {chosen}", file=sys.stderr)
    print("[exec] " + " ".join(shlex.quote(a) for a in argv2), file=sys.stderr)

    p = subprocess.run(argv2)
    return p.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
