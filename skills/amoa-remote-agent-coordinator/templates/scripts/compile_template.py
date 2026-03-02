#!/usr/bin/env python3
"""
Template compiler for markdown files with variable substitution.

Supports:
- Variable placeholders: {{VARIABLE}}
- Nested variable references: {{VAR_{{SUFFIX}}}}
- Conditional blocks: {{#IF CONDITION}}...{{/IF}}
- Template includes: {{INCLUDE path/to/template.md}}
- Validation of syntax and variables
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Set, List, Tuple


class TemplateError(Exception):
    """Base exception for template compilation errors."""
    pass


class TemplateCompiler:
    """Compiles markdown templates with variable substitution and control structures."""

    def __init__(self, variables: Dict[str, Any], template_dir: Optional[Path] = None):
        """
        Initialize the template compiler.

        Args:
            variables: Dictionary of variable names to values
            template_dir: Base directory for resolving relative template includes
        """
        self.variables = variables
        self.template_dir = template_dir or Path.cwd()
        self.used_variables: Set[str] = set()
        self.required_variables: Set[str] = set()
        self.include_stack: List[Path] = []

    def compile(self, template: str, template_path: Optional[Path] = None) -> str:
        """
        Compile a template string with variable substitution.

        Args:
            template: Template string to compile
            template_path: Path to template file (for resolving includes)

        Returns:
            Compiled template string

        Raises:
            TemplateError: If template syntax is invalid or variables are missing
        """
        if template_path:
            self.template_dir = template_path.parent

        # Process includes first
        template = self._process_includes(template, template_path)

        # Process conditional blocks
        template = self._process_conditionals(template)

        # Process variable substitutions (with nested support)
        template = self._process_variables(template)

        return template

    def _process_includes(self, template: str, current_path: Optional[Path]) -> str:
        """
        Process {{INCLUDE path/to/template.md}} directives.

        Args:
            template: Template string
            current_path: Current template file path (for circular detection)

        Returns:
            Template with includes expanded

        Raises:
            TemplateError: If include file not found or circular include detected
        """
        include_pattern = re.compile(r'{{\s*INCLUDE\s+([^\s}]+)\s*}}')

        def replace_include(match: re.Match) -> str:
            include_path_str = match.group(1)
            include_path = self.template_dir / include_path_str

            # Check for circular includes
            if include_path in self.include_stack:
                stack_str = ' -> '.join(str(p) for p in self.include_stack + [include_path])
                raise TemplateError(f"Circular include detected: {stack_str}")

            # Check if file exists
            if not include_path.exists():
                raise TemplateError(f"Include file not found: {include_path}")

            # Read and process included template
            self.include_stack.append(include_path)
            try:
                included_content = include_path.read_text(encoding='utf-8')
                # Recursively process the included template
                old_dir = self.template_dir
                self.template_dir = include_path.parent
                result = self._process_includes(included_content, include_path)
                self.template_dir = old_dir
                return result
            finally:
                self.include_stack.pop()

        return include_pattern.sub(replace_include, template)

    def _process_conditionals(self, template: str) -> str:
        """
        Process {{#IF CONDITION}}...{{/IF}} blocks.

        Args:
            template: Template string

        Returns:
            Template with conditionals evaluated

        Raises:
            TemplateError: If conditional syntax is invalid
        """
        # Match nested conditionals using a simple recursive approach
        conditional_pattern = re.compile(
            r'{{\s*#IF\s+([^\s}]+)\s*}}(.*?){{\s*/IF\s*}}',
            re.DOTALL
        )

        def evaluate_condition(condition: str) -> bool:
            """Evaluate a condition variable (checks if truthy)."""
            condition = condition.strip()
            self.required_variables.add(condition)

            if condition not in self.variables:
                return False

            self.used_variables.add(condition)
            value = self.variables[condition]

            # Evaluate truthiness
            if isinstance(value, str):
                return value.lower() not in ('', '0', 'false', 'no', 'none')
            return bool(value)

        def replace_conditional(match: re.Match) -> str:
            condition = match.group(1)
            content = match.group(2)

            if evaluate_condition(condition):
                # Recursively process nested conditionals
                return self._process_conditionals(content)
            else:
                return ''

        # Keep processing until no more conditionals found (handles nesting)
        max_iterations = 100
        iteration = 0
        while conditional_pattern.search(template) and iteration < max_iterations:
            template = conditional_pattern.sub(replace_conditional, template)
            iteration += 1

        if iteration >= max_iterations:
            raise TemplateError("Maximum conditional nesting depth exceeded (possible infinite loop)")

        return template

    def _process_variables(self, template: str) -> str:
        """
        Process {{VARIABLE}} substitutions with nested support.

        Args:
            template: Template string

        Returns:
            Template with variables substituted

        Raises:
            TemplateError: If required variables are missing
        """
        # Process nested variables first (inside-out)
        max_iterations = 100
        iteration = 0

        variable_pattern = re.compile(r'{{\s*([A-Z_][A-Z0-9_]*)\s*}}')

        while variable_pattern.search(template) and iteration < max_iterations:
            def replace_variable(match: re.Match) -> str:
                var_name = match.group(1)
                self.required_variables.add(var_name)

                if var_name not in self.variables:
                    raise TemplateError(f"Missing required variable: {var_name}")

                self.used_variables.add(var_name)
                value = self.variables[var_name]

                # Convert value to string
                if isinstance(value, (dict, list)):
                    return json.dumps(value, indent=2)
                return str(value)

            template = variable_pattern.sub(replace_variable, template)
            iteration += 1

        if iteration >= max_iterations:
            raise TemplateError("Maximum variable nesting depth exceeded (possible infinite loop)")

        return template

    def get_unused_variables(self) -> Set[str]:
        """
        Get variables that were provided but not used in the template.

        Returns:
            Set of unused variable names
        """
        return set(self.variables.keys()) - self.used_variables

    def get_missing_variables(self) -> Set[str]:
        """
        Get variables that were required but not provided.

        Returns:
            Set of missing variable names
        """
        return self.required_variables - set(self.variables.keys())


def validate_template(template_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate template syntax without variable substitution.

    Args:
        template_path: Path to template file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        content = template_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Failed to read template: {e}"]

    # Check for unclosed conditionals
    if_count = len(re.findall(r'{{\s*#IF\s+', content))
    endif_count = len(re.findall(r'{{\s*/IF\s*}}', content))
    if if_count != endif_count:
        errors.append(f"Mismatched conditionals: {if_count} #IF blocks but {endif_count} /IF blocks")

    # Check for invalid syntax patterns
    invalid_patterns = [
        (r'{{\s*#IF\s*}}', "Empty condition in #IF block"),
        (r'{{\s*/IF\s+\S+', "Unexpected content after /IF"),
        (r'{{\s*INCLUDE\s*}}', "Empty path in INCLUDE directive"),
    ]

    for pattern, error_msg in invalid_patterns:
        matches = re.findall(pattern, content)
        if matches:
            errors.append(f"{error_msg} (found {len(matches)} occurrence(s))")

    # Check for malformed variable references
    malformed_vars = re.findall(r'{{\s*([^A-Z#/\s][^}]*)\s*}}', content)
    if malformed_vars:
        errors.append(f"Malformed variable references: {', '.join(set(malformed_vars))}")

    return len(errors) == 0, errors


def parse_cli_variables(var_args: List[str]) -> Dict[str, str]:
    """
    Parse command-line variable assignments (KEY=VALUE).

    Args:
        var_args: List of KEY=VALUE strings

    Returns:
        Dictionary of variable names to values

    Raises:
        ValueError: If variable format is invalid
    """
    variables = {}

    for var_arg in var_args:
        if '=' not in var_arg:
            raise ValueError(f"Invalid variable format: {var_arg} (expected KEY=VALUE)")

        key, value = var_arg.split('=', 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Empty variable name in: {var_arg}")

        variables[key] = value

    return variables


def main() -> int:
    """
    Main entry point for template compiler CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description='Compile markdown templates with variable substitution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile with JSON config
  python compile_template.py --template task.md --config vars.json

  # Compile with CLI variables
  python compile_template.py --template task.md --var AGENT=worker --var TASK=test

  # Compile to file
  python compile_template.py --template task.md --config vars.json --output result.md

  # Validate syntax only
  python compile_template.py --validate task.md
        """
    )

    parser.add_argument(
        '--template',
        type=Path,
        help='Path to template file'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='Path to JSON config file with variables'
    )

    parser.add_argument(
        '--var',
        action='append',
        dest='variables',
        help='Variable assignment (KEY=VALUE), can be used multiple times'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--validate',
        type=Path,
        help='Validate template syntax only (no compilation)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings (unused variables) as errors'
    )

    args = parser.parse_args()

    # Validation mode
    if args.validate:
        is_valid, errors = validate_template(args.validate)

        if is_valid:
            print(f"✓ Template syntax is valid: {args.validate}", file=sys.stderr)
            return 0
        else:
            print(f"✗ Template validation failed: {args.validate}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1

    # Compilation mode requires template
    if not args.template:
        parser.error("--template is required (or use --validate)")

    if not args.template.exists():
        print(f"Error: Template file not found: {args.template}", file=sys.stderr)
        return 1

    # Load variables
    variables = {}

    if args.config:
        if not args.config.exists():
            print(f"Error: Config file not found: {args.config}", file=sys.stderr)
            return 1

        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_vars = json.load(f)
                if not isinstance(config_vars, dict):
                    print("Error: Config file must contain a JSON object", file=sys.stderr)
                    return 1
                variables.update(config_vars)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
            return 1

    if args.variables:
        try:
            cli_vars = parse_cli_variables(args.variables)
            variables.update(cli_vars)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Read template
    try:
        template_content = args.template.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading template: {e}", file=sys.stderr)
        return 1

    # Compile template
    compiler = TemplateCompiler(variables, args.template.parent)

    try:
        result = compiler.compile(template_content, args.template)
    except TemplateError as e:
        print(f"Error compiling template: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    # Check for missing variables
    missing = compiler.get_missing_variables()
    if missing:
        print(f"Error: Missing required variables: {', '.join(sorted(missing))}", file=sys.stderr)
        return 1

    # Warn about unused variables
    unused = compiler.get_unused_variables()
    if unused:
        print(f"Warning: Unused variables: {', '.join(sorted(unused))}", file=sys.stderr)
        if args.strict:
            return 1

    # Output result
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result, encoding='utf-8')
            print(f"✓ Compiled template written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(result)

    return 0


if __name__ == '__main__':
    sys.exit(main())
