#!/usr/bin/env python3
"""
Universal Code Quality Pattern Detector

Language-agnostic anti-pattern detection system using regex patterns.
Detects code smells, security issues, and quality problems across multiple languages.

WHY: Manual code review is time-consuming and inconsistent. Automated pattern
detection provides fast, consistent identification of common anti-patterns and
security vulnerabilities across codebases in any language.

WHY: Regex-based approach is language-agnostic and requires no AST parsing,
making it universally applicable and fast for large codebases.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

# WHY: Import cross-platform utilities for atomic file operations
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import atomic_write_json  # type: ignore[import-not-found]  # noqa: E402


@dataclass
class Pattern:
    """
    Represents a code quality pattern to detect.

    WHY dataclass: Provides automatic __init__, __repr__, and type hints
    without boilerplate code.
    """

    name: str
    description: str
    regex: str
    severity: str  # INFO, WARNING, ERROR, CRITICAL
    languages: list[str]
    fix_hint: str = ""

    def __post_init__(self) -> None:
        """
        Compile regex pattern for performance.

        WHY: Pre-compiling regex patterns once during initialization is
        significantly faster than re-compiling on every match attempt.
        """
        self.compiled_pattern = re.compile(self.regex, re.MULTILINE | re.IGNORECASE)


@dataclass
class Match:
    """
    Represents a detected pattern match in code.

    WHY: Structured match data enables easy reporting, filtering, and analysis
    of detected issues.
    """

    file_path: str
    line_number: int
    line_content: str
    pattern_name: str
    severity: str
    description: str
    fix_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        """
        Convert match to dictionary for JSON serialization.

        WHY: JSON output enables integration with CI/CD pipelines and
        other tooling.
        """
        return asdict(self)


class PatternDetector:
    """
    Main detector class for scanning code files for quality patterns.

    WHY class-based: Encapsulates state (patterns, matches) and provides
    clean interface for detection operations.
    """

    # WHY class constant: Language file extension mapping is shared across
    # all instances and doesn't change at runtime.
    LANGUAGE_EXTENSIONS = {
        "python": {".py", ".pyw"},
        "typescript": {".ts", ".tsx"},
        "javascript": {".js", ".jsx"},
        "go": {".go"},
        "rust": {".rs"},
        "java": {".java"},
        "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".h"},
        "c": {".c", ".h"},
        "ruby": {".rb"},
        "php": {".php"},
    }

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize detector with optional verbose output.

        WHY: Verbose mode helps debugging pattern matching and understanding
        what's being scanned.
        """
        self.patterns: list[Pattern] = []
        self.matches: list[Match] = []
        self.verbose = verbose
        self.files_scanned = 0
        self.lines_scanned = 0

    def load_patterns(self, file_path: Path | None = None) -> None:
        """
        Load pattern definitions from JSON file or use built-in patterns.

        WHY: External pattern files enable customization without code changes.
        Built-in patterns provide sensible defaults for immediate use.

        Args:
            file_path: Path to JSON pattern file. If None, uses built-in patterns.
        """
        if file_path:
            # WHY: Load custom patterns from external file for flexibility
            with open(file_path, "r", encoding="utf-8") as f:
                pattern_data = json.load(f)
                for p in pattern_data.get("patterns", []):
                    self.patterns.append(Pattern(**p))
            if self.verbose:
                print(f"Loaded {len(self.patterns)} patterns from {file_path}")
        else:
            # WHY: Built-in patterns provide immediate value without configuration
            self.patterns = self._get_builtin_patterns()
            if self.verbose:
                print(f"Loaded {len(self.patterns)} built-in patterns")

    def _get_builtin_patterns(self) -> list[Pattern]:
        """
        Return built-in pattern definitions for common anti-patterns.

        WHY: Provides comprehensive default patterns covering security,
        quality, and language-specific issues without requiring configuration.
        """
        return [
            # Security patterns - WHY: Detect common security vulnerabilities
            Pattern(
                name="hardcoded-secret",
                description="Potential hardcoded secret or password",
                regex=r'(password|passwd|pwd|secret|api_key|apikey|token|auth)\s*[=:]\s*["\'][^"\']{8,}["\']',
                severity="CRITICAL",
                languages=["python", "typescript", "javascript", "go", "rust", "java"],
                fix_hint="Store secrets in environment variables or secure vaults",
            ),
            Pattern(
                name="sql-injection-risk",
                description="Potential SQL injection vulnerability",
                regex=r"(execute|exec|query|executemany)\s*\([^)]*[+%]\s*[^)]*\)",
                severity="CRITICAL",
                languages=["python", "javascript", "typescript", "php", "java"],
                fix_hint="Use parameterized queries or ORMs with prepared statements",
            ),
            Pattern(
                name="eval-usage",
                description="Dangerous eval() usage",
                regex=r"\beval\s*\(",
                severity="CRITICAL",
                languages=["python", "javascript", "typescript", "php"],
                fix_hint="Avoid eval(). Use safer alternatives like ast.literal_eval or JSON parsing",
            ),
            # Quality patterns - WHY: Detect code smells and maintenance issues
            Pattern(
                name="todo-comment",
                description="TODO comment found",
                regex=r"#\s*TODO|//\s*TODO|/\*\s*TODO",
                severity="INFO",
                languages=[
                    "python",
                    "typescript",
                    "javascript",
                    "go",
                    "rust",
                    "java",
                    "cpp",
                    "c",
                ],
                fix_hint="Track TODOs in issue tracker instead of code comments",
            ),
            Pattern(
                name="fixme-comment",
                description="FIXME comment found",
                regex=r"#\s*FIXME|//\s*FIXME|/\*\s*FIXME",
                severity="WARNING",
                languages=[
                    "python",
                    "typescript",
                    "javascript",
                    "go",
                    "rust",
                    "java",
                    "cpp",
                    "c",
                ],
                fix_hint="Address FIXME issues before merging",
            ),
            Pattern(
                name="commented-code",
                description="Commented out code detected",
                regex=r"^[\s]*[#//]\s*(def|function|class|const|let|var|if|for|while)\s+\w+",
                severity="WARNING",
                languages=["python", "typescript", "javascript"],
                fix_hint="Remove commented code. Use version control instead",
            ),
            Pattern(
                name="magic-number",
                description="Magic number detected",
                regex=r"\b(?<![\w.])((?!0|1|2|10|100|1000)\d{3,})\b(?![\w.])",
                severity="INFO",
                languages=["python", "typescript", "javascript", "go", "rust", "java"],
                fix_hint="Extract magic numbers to named constants",
            ),
            Pattern(
                name="long-line",
                description="Line exceeds 120 characters",
                regex=r"^.{121,}$",
                severity="INFO",
                languages=["python", "typescript", "javascript", "go", "rust", "java"],
                fix_hint="Break long lines for readability",
            ),
            # TypeScript-specific - WHY: Detect TypeScript anti-patterns
            Pattern(
                name="any-usage",
                description="Unsafe 'any' type usage",
                regex=r":\s*any\b|<any>|as\s+any\b",
                severity="WARNING",
                languages=["typescript"],
                fix_hint="Use specific types or 'unknown' with type guards",
            ),
            Pattern(
                name="non-null-assertion",
                description="Non-null assertion operator usage",
                regex=r"\w+!\.|\w+!\[",
                severity="WARNING",
                languages=["typescript"],
                fix_hint="Use optional chaining (?.) or explicit null checks",
            ),
            Pattern(
                name="ts-ignore",
                description="TypeScript error suppression",
                regex=r"//\s*@ts-ignore|//\s*@ts-nocheck",
                severity="WARNING",
                languages=["typescript"],
                fix_hint="Fix the underlying type error instead of suppressing",
            ),
            # Python-specific - WHY: Detect Python anti-patterns
            Pattern(
                name="bare-except",
                description="Bare except clause catches all exceptions",
                regex=r"except\s*:",
                severity="WARNING",
                languages=["python"],
                fix_hint="Catch specific exceptions instead of bare except",
            ),
            Pattern(
                name="mutable-default",
                description="Mutable default argument",
                regex=r"def\s+\w+\([^)]*=\s*(\[\]|\{\})",
                severity="ERROR",
                languages=["python"],
                fix_hint="Use None as default and initialize inside function",
            ),
            Pattern(
                name="print-statement",
                description="Print statement (use logging instead)",
                regex=r"\bprint\s*\(",
                severity="INFO",
                languages=["python"],
                fix_hint="Use logging module instead of print statements",
            ),
            Pattern(
                name="import-star",
                description="Star import detected",
                regex=r"from\s+\S+\s+import\s+\*",
                severity="WARNING",
                languages=["python"],
                fix_hint="Import specific names or the module itself",
            ),
            # Go-specific - WHY: Detect Go anti-patterns
            Pattern(
                name="go-error-ignore",
                description="Error return value ignored",
                regex=r"_,\s*err\s*:=|_\s*=.*Error\(",
                severity="ERROR",
                languages=["go"],
                fix_hint="Always handle or explicitly ignore errors",
            ),
            # Rust-specific - WHY: Detect Rust anti-patterns
            Pattern(
                name="rust-unwrap",
                description="Unwrap usage (may panic)",
                regex=r"\.unwrap\(\)",
                severity="WARNING",
                languages=["rust"],
                fix_hint="Use pattern matching or expect() with descriptive message",
            ),
            Pattern(
                name="rust-unsafe",
                description="Unsafe block detected",
                regex=r"\bunsafe\s+\{",
                severity="WARNING",
                languages=["rust"],
                fix_hint="Document safety invariants and minimize unsafe scope",
            ),
        ]

    def _detect_language(self, file_path: Path) -> str | None:
        """
        Detect programming language from file extension.

        WHY: Automatic language detection enables filtering patterns to
        only those relevant to the file being scanned.

        Returns:
            Language name or None if unknown
        """
        ext = file_path.suffix.lower()
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        return None

    def detect(self, file_path: Path, language: str = "auto") -> list[Match]:
        """
        Detect patterns in a single file.

        WHY: Single-file detection enables targeted analysis and easier testing.

        Args:
            file_path: Path to file to scan
            language: Language filter ("auto" to detect from extension)

        Returns:
            List of matches found in the file
        """
        if not file_path.exists() or not file_path.is_file():
            if self.verbose:
                print(f"Skipping {file_path}: not a file")
            return []

        # WHY: Auto-detect language to apply appropriate patterns
        detected_lang = self._detect_language(file_path)
        if language == "auto":
            if not detected_lang:
                if self.verbose:
                    print(f"Skipping {file_path}: unknown language")
                return []
            language = detected_lang

        if self.verbose:
            print(f"Scanning {file_path} (language: {language})")

        file_matches = []

        try:
            # WHY: UTF-8 encoding with error handling prevents crashes on binary files
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            self.files_scanned += 1
            self.lines_scanned += len(lines)

            # WHY: Line-by-line scanning provides accurate line numbers for matches
            for line_num, line in enumerate(lines, start=1):
                for pattern in self.patterns:
                    # WHY: Only check patterns applicable to this language
                    if language not in pattern.languages:
                        continue

                    # WHY: Search for pattern matches in current line
                    if pattern.compiled_pattern.search(line):
                        match = Match(
                            file_path=str(file_path),
                            line_number=line_num,
                            line_content=line.strip(),
                            pattern_name=pattern.name,
                            severity=pattern.severity,
                            description=pattern.description,
                            fix_hint=pattern.fix_hint,
                        )
                        file_matches.append(match)
                        self.matches.append(match)

                        if self.verbose:
                            print(
                                f"  Line {line_num}: {pattern.name} ({pattern.severity})"
                            )

        except Exception as e:
            # WHY: Don't crash on unreadable files, just warn and continue
            if self.verbose:
                print(f"Error reading {file_path}: {e}")

        return file_matches

    def detect_all(
        self,
        dir_path: Path,
        language: str = "auto",
        exclude_dirs: set[str] | None = None,
    ) -> list[Match]:
        """
        Recursively detect patterns in all files in a directory.

        WHY: Recursive scanning enables full codebase analysis without manual
        file enumeration.

        Args:
            dir_path: Root directory to scan
            language: Language filter ("auto" to detect from extensions)
            exclude_dirs: Directory names to skip (default: common build/dependency dirs)

        Returns:
            List of all matches found
        """
        if exclude_dirs is None:
            # WHY: Exclude common build/dependency directories to avoid noise
            exclude_dirs = {
                "node_modules",
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                "build",
                "dist",
                ".mypy_cache",
                ".pytest_cache",
                "target",
                ".idea",
                ".vscode",
                "coverage",
            }

        if not dir_path.exists() or not dir_path.is_dir():
            print(f"Error: {dir_path} is not a directory", file=sys.stderr)
            return []

        all_matches = []

        # WHY: rglob recursively walks directory tree
        for file_path in dir_path.rglob("*"):
            # WHY: Skip excluded directories and their contents
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            if file_path.is_file():
                # WHY: Detect language for each file individually
                file_matches = self.detect(file_path, language)
                all_matches.extend(file_matches)

        return all_matches

    def report(self) -> dict[str, Any]:
        """
        Generate summary report of all detections.

        WHY: Structured report provides overview of findings by severity,
        pattern, and file for analysis and prioritization.

        Returns:
            Dictionary with summary statistics and findings
        """
        # WHY: Group matches by severity for prioritization
        by_severity: dict[str, list[Match]] = {}
        for match in self.matches:
            if match.severity not in by_severity:
                by_severity[match.severity] = []
            by_severity[match.severity].append(match)

        # WHY: Count matches by pattern to identify most common issues
        by_pattern: dict[str, int] = {}
        for match in self.matches:
            if match.pattern_name not in by_pattern:
                by_pattern[match.pattern_name] = 0
            by_pattern[match.pattern_name] += 1

        # WHY: Comprehensive summary enables quick assessment of code quality
        return {
            "summary": {
                "total_matches": len(self.matches),
                "files_scanned": self.files_scanned,
                "lines_scanned": self.lines_scanned,
                "patterns_used": len(self.patterns),
                "by_severity": {
                    severity: len(matches) for severity, matches in by_severity.items()
                },
                "by_pattern": by_pattern,
            },
            "matches": [match.to_dict() for match in self.matches],
        }


def main() -> None:
    """
    CLI entry point for pattern detector.

    WHY: Command-line interface enables integration with scripts, CI/CD,
    and manual usage.
    """
    parser = argparse.ArgumentParser(
        description="Universal code quality pattern detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan directory for TypeScript issues
  %(prog)s --path ./src --language typescript

  # Use custom patterns
  %(prog)s --path . --patterns custom_patterns.json

  # Save results to JSON
  %(prog)s --path ./app --output results.json

  # Verbose output for debugging
  %(prog)s --path ./lib --verbose
""",
    )

    parser.add_argument(
        "--path", type=Path, required=True, help="File or directory to scan"
    )

    parser.add_argument(
        "--patterns",
        type=Path,
        help="JSON file with custom pattern definitions (uses built-in if not specified)",
    )

    parser.add_argument(
        "--language",
        default="auto",
        choices=[
            "auto",
            "python",
            "typescript",
            "javascript",
            "go",
            "rust",
            "java",
            "cpp",
            "c",
            "ruby",
            "php",
        ],
        help="Programming language filter (default: auto-detect)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file (prints to stdout if not specified)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # WHY: Initialize detector with verbose setting
    detector = PatternDetector(verbose=args.verbose)

    # WHY: Load patterns (custom or built-in)
    detector.load_patterns(args.patterns)

    # WHY: Scan single file or entire directory
    if args.path.is_file():
        detector.detect(args.path, args.language)
    else:
        detector.detect_all(args.path, args.language)

    # WHY: Generate comprehensive report
    report = detector.report()

    # WHY: Output to file or stdout based on user preference
    if args.output:
        # WHY: Use atomic write for safe file operations
        atomic_write_json(report, Path(args.output), indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    # WHY: Print human-readable summary
    print("\nSummary:", file=sys.stderr)
    print(f"  Files scanned: {report['summary']['files_scanned']}", file=sys.stderr)
    print(f"  Lines scanned: {report['summary']['lines_scanned']}", file=sys.stderr)
    print(f"  Total matches: {report['summary']['total_matches']}", file=sys.stderr)
    print("  By severity:", file=sys.stderr)
    for severity, count in sorted(report["summary"]["by_severity"].items()):
        print(f"    {severity}: {count}", file=sys.stderr)

    # WHY: Exit with error code if critical issues found (enables CI/CD integration)
    if report["summary"]["by_severity"].get("CRITICAL", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
