# LSP Selection Guide - Part 1: Language Detection

## Automatic Detection

The orchestrator automatically detects project language using these methods (in priority order):

1. **Explicit configuration file**: Read from `{{PROJECT_ROOT}}/.toolchain`
2. **Build system files**: Detect from package.json, Cargo.toml, go.mod, etc.
3. **File extension analysis**: Count source files by extension
4. **Git repository language**: Query GitHub API for primary language

## Detection Script

```python
#!/usr/bin/env python3
# detect_language.py

import os
import json
from pathlib import Path
from collections import Counter

def detect_language(project_root: str) -> str:
    """Detect primary language of project."""
    project_path = Path(project_root)

    # Method 1: Check .toolchain file
    toolchain_file = project_path / ".toolchain"
    if toolchain_file.exists():
        return toolchain_file.read_text().strip()

    # Method 2: Check build system files
    build_files = {
        "package.json": "nodejs",
        "Cargo.toml": "rust",
        "go.mod": "go",
        "pyproject.toml": "python",
        "setup.py": "python",
        "requirements.txt": "python",
        "CMakeLists.txt": "cpp",
        "Makefile": "cpp",
        "pom.xml": "java",
        "build.gradle": "java",
        "Gemfile": "ruby",
        "composer.json": "php",
        "*.csproj": "csharp",
        "Package.swift": "swift"
    }

    for filename, language in build_files.items():
        if list(project_path.glob(filename)):
            return language

    # Method 3: Count source files by extension
    extensions = {
        ".py": "python",
        ".js": "nodejs",
        ".ts": "nodejs",
        ".jsx": "nodejs",
        ".tsx": "nodejs",
        ".rs": "rust",
        ".go": "go",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c": "cpp",
        ".h": "cpp",
        ".hpp": "cpp",
        ".java": "java",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".swift": "swift"
    }

    counter = Counter()
    for ext, lang in extensions.items():
        count = len(list(project_path.rglob(f"*{ext}")))
        counter[lang] += count

    if counter:
        return counter.most_common(1)[0][0]

    # Default fallback
    return "unknown"

if __name__ == "__main__":
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    language = detect_language(project)
    print(language)
```

Usage:
```bash
python detect_language.py {{PROJECT_ROOT}}
# Output: python
```

## LSP Server Selection Matrix

Based on detected language, select the appropriate LSP server:

| Language | Primary LSP | Alternative LSP | Installation Command |
|----------|-------------|-----------------|----------------------|
| Python | `pylsp` | `pyright`, `jedi-language-server` | `pipx install python-lsp-server` |
| JavaScript/TypeScript | `typescript-language-server` | `vscode-langservers-extracted` | `npm install -g typescript-language-server` |
| Rust | `rust-analyzer` | - | `rustup component add rust-analyzer` |
| Go | `gopls` | - | `go install golang.org/x/tools/gopls@latest` |
| C/C++ | `clangd` | `ccls` | `brew install llvm` or apt/pacman |
| Java | `jdtls` | - | Download from Eclipse JDT |
| Ruby | `solargraph` | - | `gem install solargraph` |
| PHP | `intelephense` | `phpactor` | `npm install -g intelephense` |
| C# | `omnisharp` | - | Download from OmniSharp |
| Swift | `sourcekit-lsp` | - | Included with Swift toolchain |

---

**Next**: [Part 2 - LSP Selection Scripts](./LSP_SELECTION_GUIDE-part2-selection-scripts.md)

**Back to**: [LSP Selection Guide (Index)](./LSP_SELECTION_GUIDE.md)
