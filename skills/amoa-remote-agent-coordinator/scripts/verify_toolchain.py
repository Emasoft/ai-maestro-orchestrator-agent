#!/usr/bin/env python3
"""Verify and generate toolchain requirements for remote agents.

PURPOSE: Checks if required tools are installed locally (orchestrator) and
generates toolchain verification scripts to send to remote agents.

USAGE:
  # Check orchestrator tools
  python verify_toolchain.py --check orchestrator

  # Generate verification script for remote agent
  python verify_toolchain.py --generate rust --output /tmp/check-toolchain.sh

  # Check specific language toolchain
  python verify_toolchain.py --check python

  # List all supported toolchains
  python verify_toolchain.py --list
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast


@dataclass
class Tool:
    """Represents a required tool."""

    name: str
    command: str
    version_flag: str = "--version"
    install_cmd: str = ""
    required: bool = True


# Orchestrator required tools
ORCHESTRATOR_TOOLS = [
    Tool("gh", "gh", "--version", "brew install gh"),
    Tool("jq", "jq", "--version", "brew install jq"),
    Tool("shellcheck", "shellcheck", "--version", "brew install shellcheck"),
    Tool("ruff", "ruff", "--version", "uv pip install ruff"),
    Tool(
        "skills-ref",
        "skills-ref",
        "--version",
        "uv pip install skills-ref",
        required=False,
    ),
]

# Language-specific toolchains
TOOLCHAINS = {
    "python": {
        "description": "Python development with uv",
        "tools": [
            Tool(
                "uv",
                "uv",
                "--version",
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
            ),
            Tool("python", "python3", "--version", "uv python install 3.12"),
            Tool("ruff", "ruff", "--version", "uv pip install ruff"),
            Tool("mypy", "mypy", "--version", "uv pip install mypy"),
            Tool("pytest", "pytest", "--version", "uv pip install pytest"),
        ],
        "setup_script": """
# Python Toolchain Setup
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart shell
uv venv --python 3.12
source .venv/bin/activate
uv pip install ruff mypy pytest
""",
        "verify_cmd": "uv run pytest tests/ && uv run ruff check src/ && uv run mypy src/",
    },
    "rust": {
        "description": "Rust development with cargo",
        "tools": [
            Tool(
                "rustc",
                "rustc",
                "--version",
                "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            ),
            Tool("cargo", "cargo", "--version", "# included with rustup"),
            Tool("clippy", "cargo clippy", "--version", "rustup component add clippy"),
            Tool("rustfmt", "rustfmt", "--version", "rustup component add rustfmt"),
        ],
        "setup_script": """
# Rust Toolchain Setup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustup default stable
rustup component add clippy rustfmt
""",
        "verify_cmd": "cargo test && cargo clippy -- -D warnings && cargo fmt --check",
    },
    "javascript": {
        "description": "JavaScript/TypeScript with bun",
        "tools": [
            Tool("bun", "bun", "--version", "curl -fsSL https://bun.sh/install | bash"),
            Tool(
                "node", "node", "--version", "# included with bun or install separately"
            ),
        ],
        "setup_script": """
# JavaScript/TypeScript Toolchain Setup
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc
bun install
""",
        "verify_cmd": "bun run tsc --noEmit && bun run eslint src/ && bun test",
    },
    "go": {
        "description": "Go development",
        "tools": [
            Tool("go", "go", "version", "brew install go"),
            Tool(
                "golangci-lint",
                "golangci-lint",
                "--version",
                "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest",
            ),
        ],
        "setup_script": """
# Go Toolchain Setup
brew install go
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
""",
        "verify_cmd": "go test ./... && go vet ./... && golangci-lint run",
    },
    "swift": {
        "description": "Swift development",
        "tools": [
            Tool("swift", "swift", "--version", "xcode-select --install"),
            Tool("swiftlint", "swiftlint", "--version", "brew install swiftlint"),
            Tool("swiftformat", "swiftformat", "--version", "brew install swiftformat"),
        ],
        "setup_script": """
# Swift Toolchain Setup
xcode-select --install
brew install swiftlint swiftformat
""",
        "verify_cmd": "swift build && swift test && swiftlint",
    },
    "csharp": {
        "description": "C#/.NET development",
        "tools": [
            Tool("dotnet", "dotnet", "--version", "brew install dotnet"),
        ],
        "setup_script": """
# C#/.NET Toolchain Setup
brew install dotnet
""",
        "verify_cmd": "dotnet build && dotnet test",
    },
    "java": {
        "description": "Java development with Gradle",
        "tools": [
            Tool("java", "java", "--version", "sdk install java 21-tem"),
            Tool("gradle", "gradle", "--version", "sdk install gradle"),
        ],
        "setup_script": """
# Java Toolchain Setup
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh
sdk install java 21-tem
sdk install gradle
""",
        "verify_cmd": "gradle clean build test",
    },
    "kotlin": {
        "description": "Kotlin development with Gradle",
        "tools": [
            Tool("kotlin", "kotlin", "-version", "sdk install kotlin"),
            Tool("gradle", "gradle", "--version", "sdk install gradle"),
        ],
        "setup_script": """
# Kotlin Toolchain Setup
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh
sdk install kotlin
sdk install gradle
""",
        "verify_cmd": "gradle clean build test",
    },
    "ruby": {
        "description": "Ruby development with Bundler",
        "tools": [
            Tool("ruby", "ruby", "--version", "rbenv install 3.3.0"),
            Tool("bundle", "bundle", "--version", "gem install bundler"),
            Tool("rubocop", "rubocop", "--version", "gem install rubocop"),
        ],
        "setup_script": """
# Ruby Toolchain Setup
brew install rbenv ruby-build
rbenv install 3.3.0
rbenv global 3.3.0
gem install bundler rubocop
""",
        "verify_cmd": "bundle exec rspec && bundle exec rubocop",
    },
    "cpp": {
        "description": "C/C++ development with CMake",
        "tools": [
            Tool("cmake", "cmake", "--version", "brew install cmake"),
            Tool("ninja", "ninja", "--version", "brew install ninja"),
            Tool("clang++", "clang++", "--version", "xcode-select --install"),
        ],
        "setup_script": """
# C/C++ Toolchain Setup
xcode-select --install
brew install cmake ninja
""",
        "verify_cmd": "cmake -B build -G Ninja && cmake --build build && ctest --test-dir build",
    },
    "bash": {
        "description": "Shell script development",
        "tools": [
            Tool("bash", "bash", "--version", "# usually pre-installed"),
            Tool("shellcheck", "shellcheck", "--version", "brew install shellcheck"),
            Tool("shfmt", "shfmt", "--version", "brew install shfmt"),
        ],
        "setup_script": """
# Bash Toolchain Setup
brew install shellcheck shfmt
""",
        "verify_cmd": 'find . -name "*.sh" -exec shellcheck {} \\;',
    },
}


def check_tool(tool: Tool) -> tuple[bool, str]:
    """Check if a tool is installed and get its version."""
    try:
        cmd = tool.command.split()
        if tool.version_flag:
            cmd.append(tool.version_flag)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            return True, version
        return False, ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False, ""


def check_toolchain(name: str) -> dict[str, Any]:
    """Check all tools in a toolchain."""
    tools: list[Tool]
    description: str
    if name == "orchestrator":
        tools = ORCHESTRATOR_TOOLS
        description = "Orchestrator required tools"
    elif name in TOOLCHAINS:
        tools = cast(list[Tool], TOOLCHAINS[name]["tools"])
        description = cast(str, TOOLCHAINS[name]["description"])
    else:
        return {"error": f"Unknown toolchain: {name}"}

    tool_results: list[dict[str, Any]] = []
    results: dict[str, Any] = {
        "name": name,
        "description": description,
        "tools": tool_results,
        "all_required_present": True,
    }

    for tool in tools:
        installed, version = check_tool(tool)
        tool_result = {
            "name": tool.name,
            "command": tool.command,
            "installed": installed,
            "version": version if installed else None,
            "required": tool.required,
            "install_cmd": tool.install_cmd,
        }
        tool_results.append(tool_result)

        if tool.required and not installed:
            results["all_required_present"] = False

    return results


def generate_verification_script(lang: str) -> str:
    """Generate a bash verification script for remote agent."""
    if lang not in TOOLCHAINS:
        return f"# Error: Unknown toolchain '{lang}'"

    tc = TOOLCHAINS[lang]
    tools = cast(list[Tool], tc["tools"])

    script_lines = [
        "#!/bin/bash",
        f"# {tc['description']} - Toolchain Verification",
        "# Generated by emasoft-orchestrator-agent",
        "",
        "set -e",
        "",
        'RED="\\033[0;31m"',
        'GREEN="\\033[0;32m"',
        'NC="\\033[0m"',
        "",
        "MISSING=0",
        "",
        "check_tool() {",
        '  local name="$1"',
        '  local cmd="$2"',
        '  local version_flag="${3:---version}"',
        "",
        "  if $cmd $version_flag &>/dev/null; then",
        "    version=$($cmd $version_flag 2>&1 | head -1)",
        '    echo -e "${GREEN}[OK]${NC} $name: $version"',
        "  else",
        '    echo -e "${RED}[MISSING]${NC} $name"',
        "    ((MISSING++))",
        "  fi",
        "}",
        "",
        'echo "=== Toolchain Verification: {} ==="'.format(lang),
        'echo ""',
    ]

    for tool in tools:
        script_lines.append(
            f'check_tool "{tool.name}" "{tool.command}" "{tool.version_flag}"'
        )

    script_lines.extend(
        [
            "",
            'echo ""',
            "if [ $MISSING -gt 0 ]; then",
            '  echo -e "${RED}Missing $MISSING required tool(s)${NC}"',
            '  echo ""',
            '  echo "Install with:"',
        ]
    )

    # Add install commands
    for tool in tools:
        if tool.install_cmd and not tool.install_cmd.startswith("#"):
            script_lines.append(f'  echo "  {tool.install_cmd}"')

    script_lines.extend(
        [
            "  exit 1",
            "fi",
            "",
            'echo -e "${GREEN}All tools verified. Ready to proceed.${NC}"',
            "",
            "# Verification command for this project:",
            f"# {tc['verify_cmd']}",
        ]
    )

    return "\n".join(script_lines)


def generate_setup_instructions(lang: str) -> str:
    """Generate setup instructions for remote agent."""
    if lang not in TOOLCHAINS:
        return f"Error: Unknown toolchain '{lang}'"

    tc = TOOLCHAINS[lang]
    return f"""
## {tc["description"]} Setup

### Installation
{tc["setup_script"]}

### Verification
After setup, verify with:
```bash
{tc["verify_cmd"]}
```
"""


def list_toolchains() -> None:
    """List all available toolchains."""
    print("Available Toolchains:")
    print("=" * 50)
    print(f"  {'orchestrator':<15} Orchestrator required tools")
    for name, tc in TOOLCHAINS.items():
        print(f"  {name:<15} {tc['description']}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify and generate toolchain requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check",
        metavar="TOOLCHAIN",
        help="Check if toolchain is installed (e.g., orchestrator, rust, python)",
    )
    parser.add_argument(
        "--generate",
        metavar="LANG",
        help="Generate verification script for language",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Output file for generated script",
    )
    parser.add_argument(
        "--setup",
        metavar="LANG",
        help="Generate setup instructions for language",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available toolchains",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    if args.list:
        list_toolchains()
        return 0

    if args.check:
        result = check_toolchain(args.check)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}")
                return 1

            print(f"\n=== {result['description']} ===\n")
            for tool in result["tools"]:
                status = "[OK]" if tool["installed"] else "[MISSING]"
                req = "" if tool["required"] else " (optional)"
                if tool["installed"]:
                    print(f"  {status} {tool['name']}: {tool['version']}{req}")
                else:
                    print(f"  {status} {tool['name']}{req}")
                    if tool["install_cmd"]:
                        print(f"         Install: {tool['install_cmd']}")

            print()
            if result["all_required_present"]:
                print("All required tools present.")
                return 0
            else:
                print("Some required tools are missing!")
                return 1

    if args.generate:
        script = generate_verification_script(args.generate)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(script)
            output_path.chmod(0o755)
            print(f"Generated: {output_path}")
        else:
            print(script)
        return 0

    if args.setup:
        instructions = generate_setup_instructions(args.setup)
        print(instructions)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
