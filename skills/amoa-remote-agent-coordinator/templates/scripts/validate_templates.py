#!/usr/bin/env python3
"""
Template validation script for remote-agent-coordinator skill.

Validates template syntax, cross-references, content, and JSON schema.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    file_path: str
    check_type: str
    passed: bool
    message: str = ""
    line_number: Optional[int] = None


@dataclass
class ValidationReport:
    """Complete validation report."""
    results: List[ValidationResult] = field(default_factory=list)

    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result."""
        self.results.append(result)

    def has_failures(self) -> bool:
        """Check if any validation failed."""
        return any(not r.passed for r in self.results)

    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        return {"passed": passed, "failed": failed, "total": len(self.results)}


class TemplateValidator:
    """Validates template files."""

    VARIABLE_PATTERN = re.compile(r'\{\{([A-Z_][A-Z0-9_]*)\}\}')
    IF_BLOCK_START = re.compile(r'\{\{#IF\s+([A-Z_][A-Z0-9_]*)\}\}')
    IF_BLOCK_END = re.compile(r'\{\{/IF\}\}')
    INCLUDE_PATTERN = re.compile(r'\{\{INCLUDE\s+([^\}]+)\}\}')

    def __init__(self, templates_dir: Path):
        """Initialize validator with templates directory."""
        self.templates_dir = templates_dir
        self.scripts_dir = templates_dir / "scripts"
        self.checklists_dir = templates_dir / "checklists"
        self.report = ValidationReport()

    def validate_all(self) -> ValidationReport:
        """Validate all templates and checklists."""
        # Find all template files (markdown files in templates/)
        template_files = list(self.templates_dir.glob("*.md"))

        for template_file in template_files:
            self.validate_template(template_file)

        # Validate JSON checklists
        if self.checklists_dir.exists():
            checklist_files = list(self.checklists_dir.glob("*.json"))
            for checklist_file in checklist_files:
                self.validate_checklist(checklist_file)

        return self.report

    def validate_template(self, template_path: Path) -> None:
        """Validate a single template file."""
        try:
            content = template_path.read_text(encoding='utf-8')
        except Exception as e:
            self.report.add_result(ValidationResult(
                file_path=str(template_path),
                check_type="read",
                passed=False,
                message=f"Failed to read file: {e}"
            ))
            return

        # Syntax validation
        self._validate_syntax(template_path, content)

        # Cross-reference validation
        self._validate_cross_references(template_path, content)

        # Content validation
        self._validate_content(template_path, content)

    def _validate_syntax(self, template_path: Path, content: str) -> None:
        """Validate template syntax."""
        lines = content.split('\n')

        # Check variable syntax
        for i, line in enumerate(lines, 1):
            for match in self.VARIABLE_PATTERN.finditer(line):
                var_name = match.group(1)
                if not self._is_valid_identifier(var_name):
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="syntax",
                        passed=False,
                        message=f"Invalid variable identifier: {var_name}",
                        line_number=i
                    ))
                else:
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="syntax",
                        passed=True,
                        message=f"Valid variable: {var_name}",
                        line_number=i
                    ))

        # Check IF block matching
        if_stack: List[Tuple[int, str]] = []
        for i, line in enumerate(lines, 1):
            # Check for IF block starts
            for match in self.IF_BLOCK_START.finditer(line):
                condition = match.group(1)
                if_stack.append((i, condition))

            # Check for IF block ends
            for _ in self.IF_BLOCK_END.finditer(line):
                if not if_stack:
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="syntax",
                        passed=False,
                        message="Orphan {{/IF}} tag without matching {{#IF}}",
                        line_number=i
                    ))
                else:
                    if_stack.pop()

        # Check for unclosed IF blocks
        if if_stack:
            for line_num, condition in if_stack:
                self.report.add_result(ValidationResult(
                    file_path=str(template_path),
                    check_type="syntax",
                    passed=False,
                    message=f"Unclosed {{{{#IF {condition}}}}} block",
                    line_number=line_num
                ))
        else:
            self.report.add_result(ValidationResult(
                file_path=str(template_path),
                check_type="syntax",
                passed=True,
                message="All IF blocks properly closed"
            ))

    def _validate_cross_references(self, template_path: Path, content: str) -> None:
        """Validate cross-references in template."""
        # Check INCLUDE references
        for match in self.INCLUDE_PATTERN.finditer(content):
            include_path = match.group(1).strip()
            full_path = self.templates_dir / include_path

            if not full_path.exists():
                self.report.add_result(ValidationResult(
                    file_path=str(template_path),
                    check_type="cross-reference",
                    passed=False,
                    message=f"INCLUDE file not found: {include_path}"
                ))
            else:
                self.report.add_result(ValidationResult(
                    file_path=str(template_path),
                    check_type="cross-reference",
                    passed=True,
                    message=f"INCLUDE file exists: {include_path}"
                ))

        # Check BASE_TOOLCHAIN.md variable documentation
        base_toolchain_path = self.templates_dir / "BASE_TOOLCHAIN.md"
        if base_toolchain_path.exists():
            base_content = base_toolchain_path.read_text(encoding='utf-8')
            template_vars = set(self.VARIABLE_PATTERN.findall(content))
            documented_vars = set(self.VARIABLE_PATTERN.findall(base_content))

            for var in template_vars:
                if var not in documented_vars and template_path != base_toolchain_path:
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="cross-reference",
                        passed=False,
                        message=f"Variable {var} not documented in BASE_TOOLCHAIN.md"
                    ))

        # Check checklist references
        checklist_pattern = re.compile(r'checklists/([^\s\)]+\.json)')
        for match in checklist_pattern.finditer(content):
            checklist_file = match.group(1)
            checklist_path = self.checklists_dir / checklist_file

            if not checklist_path.exists():
                self.report.add_result(ValidationResult(
                    file_path=str(template_path),
                    check_type="cross-reference",
                    passed=False,
                    message=f"Checklist not found: {checklist_file}"
                ))
            else:
                self.report.add_result(ValidationResult(
                    file_path=str(template_path),
                    check_type="cross-reference",
                    passed=True,
                    message=f"Checklist exists: {checklist_file}"
                ))

    def _validate_content(self, template_path: Path, content: str) -> None:
        """Validate template content structure."""
        # Check for required sections in main templates
        if template_path.name not in ["BASE_TOOLCHAIN.md"]:
            required_sections = ["Quick Reference", "Variable Substitutions"]
            for section in required_sections:
                if section in content:
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="content",
                        passed=True,
                        message=f"Required section found: {section}"
                    ))
                else:
                    # Only warn, not fail, as not all templates need all sections
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="content",
                        passed=True,
                        message=f"Section not found (may be optional): {section}"
                    ))

        # Check GitHub Actions workflow patterns
        if "uses:" in content:
            # Check for correct action format
            action_pattern = re.compile(r'uses:\s+([^\s@]+)@([^\s]+)')
            for match in action_pattern.finditer(content):
                action_name = match.group(1)
                action_version = match.group(2)

                # Basic validation - action should have org/repo format
                if '/' not in action_name:
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="content",
                        passed=False,
                        message=f"Invalid GitHub Action format: {action_name}"
                    ))
                else:
                    self.report.add_result(ValidationResult(
                        file_path=str(template_path),
                        check_type="content",
                        passed=True,
                        message=f"Valid GitHub Action: {action_name}@{action_version}"
                    ))

        # Check for deprecated patterns (example: old variable names)
        deprecated_patterns = [
            (r'\{\{AGENT_NAME\}\}', '{{AGENT_ID}}', 'Use AGENT_ID instead of AGENT_NAME'),
            (r'--legacy-flag', '--current-flag', 'Update to current flag syntax')
        ]

        for old_pattern, new_pattern, message in deprecated_patterns:
            if re.search(old_pattern, content):
                self.report.add_result(ValidationResult(
                    file_path=str(template_path),
                    check_type="content",
                    passed=False,
                    message=f"Deprecated pattern found: {message}"
                ))

    def validate_checklist(self, checklist_path: Path) -> None:
        """Validate JSON checklist file."""
        try:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.report.add_result(ValidationResult(
                file_path=str(checklist_path),
                check_type="schema",
                passed=False,
                message=f"Invalid JSON: {e}"
            ))
            return
        except Exception as e:
            self.report.add_result(ValidationResult(
                file_path=str(checklist_path),
                check_type="schema",
                passed=False,
                message=f"Failed to read file: {e}"
            ))
            return

        # Validate schema
        required_fields = ["name", "version", "categories", "items"]
        for field_name in required_fields:
            if field_name not in data:
                self.report.add_result(ValidationResult(
                    file_path=str(checklist_path),
                    check_type="schema",
                    passed=False,
                    message=f"Missing required field: {field_name}"
                ))
            else:
                self.report.add_result(ValidationResult(
                    file_path=str(checklist_path),
                    check_type="schema",
                    passed=True,
                    message=f"Required field present: {field_name}"
                ))

        # Validate items
        if "items" in data:
            item_ids = set()
            for item in data["items"]:
                # Check required item fields
                if "id" not in item:
                    self.report.add_result(ValidationResult(
                        file_path=str(checklist_path),
                        check_type="schema",
                        passed=False,
                        message="Checklist item missing 'id' field"
                    ))
                else:
                    item_id = item["id"]
                    if item_id in item_ids:
                        self.report.add_result(ValidationResult(
                            file_path=str(checklist_path),
                            check_type="schema",
                            passed=False,
                            message=f"Duplicate item ID: {item_id}"
                        ))
                    item_ids.add(item_id)

                # Check depends_on references
                if "depends_on" in item:
                    for dep_id in item["depends_on"]:
                        if dep_id not in item_ids:
                            self.report.add_result(ValidationResult(
                                file_path=str(checklist_path),
                                check_type="schema",
                                passed=False,
                                message=f"Invalid depends_on reference: {dep_id}"
                            ))

    @staticmethod
    def _is_valid_identifier(name: str) -> bool:
        """Check if name is a valid identifier."""
        return bool(re.match(r'^[A-Z_][A-Z0-9_]*$', name))


def print_summary_table(report: ValidationReport) -> None:
    """Print summary table of validation results."""
    summary = report.get_summary()

    # Group results by file and check type
    by_file: Dict[str, Dict[str, List[ValidationResult]]] = {}
    for result in report.results:
        if result.file_path not in by_file:
            by_file[result.file_path] = {}
        if result.check_type not in by_file[result.file_path]:
            by_file[result.file_path][result.check_type] = []
        by_file[result.file_path][result.check_type].append(result)

    # Print header
    print("\n" + "=" * 100)
    print("TEMPLATE VALIDATION SUMMARY")
    print("=" * 100)

    # Print per-file results
    for file_path in sorted(by_file.keys()):
        file_name = Path(file_path).name
        check_types = by_file[file_path]

        print(f"\n{file_name}")
        print("-" * 100)

        for check_type in sorted(check_types.keys()):
            results = check_types[check_type]
            passed = sum(1 for r in results if r.passed)
            failed = sum(1 for r in results if not r.passed)

            status = "✓ PASS" if failed == 0 else "✗ FAIL"
            print(f"  {check_type:20s} {status:10s} ({passed} passed, {failed} failed)")

            # Print failures
            for result in results:
                if not result.passed:
                    line_info = f" [line {result.line_number}]" if result.line_number else ""
                    print(f"    ✗ {result.message}{line_info}")

    # Print overall summary
    print("\n" + "=" * 100)
    print(f"OVERALL: {summary['passed']} passed, {summary['failed']} failed, {summary['total']} total")

    if summary['failed'] == 0:
        print("✓ ALL VALIDATIONS PASSED")
    else:
        print("✗ VALIDATION FAILURES DETECTED")

    print("=" * 100 + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate template files for remote-agent-coordinator skill"
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Validate a single template file"
    )
    parser.add_argument(
        "--checklists",
        action="store_true",
        help="Validate JSON checklists only"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output JSON report to file"
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Templates directory (default: parent of scripts/)"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = TemplateValidator(args.templates_dir)

    # Run validation
    if args.template:
        # Validate single template
        validator.validate_template(args.template)
    elif args.checklists:
        # Validate checklists only
        if validator.checklists_dir.exists():
            checklist_files = list(validator.checklists_dir.glob("*.json"))
            for checklist_file in checklist_files:
                validator.validate_checklist(checklist_file)
        else:
            print(f"Checklists directory not found: {validator.checklists_dir}")
            return 1
    else:
        # Validate all
        validator.validate_all()

    # Get report
    report = validator.report

    # Output JSON report if requested
    if args.report:
        report_data = {
            "summary": report.get_summary(),
            "results": [
                {
                    "file_path": r.file_path,
                    "check_type": r.check_type,
                    "passed": r.passed,
                    "message": r.message,
                    "line_number": r.line_number
                }
                for r in report.results
            ]
        }
        args.report.write_text(json.dumps(report_data, indent=2))
        print(f"Report written to: {args.report}")

    # Print summary table
    print_summary_table(report)

    # Return exit code
    return 1 if report.has_failures() else 0


if __name__ == "__main__":
    sys.exit(main())
