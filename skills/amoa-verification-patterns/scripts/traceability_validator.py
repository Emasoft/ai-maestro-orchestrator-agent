#!/usr/bin/env python3
"""
Traceability validator for specification architect skill.
Validates that all requirements are covered by implementation tasks.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TypedDict

# WHY: Import cross-platform utilities for consistency
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from thresholds import VERIFICATION  # type: ignore[import-not-found]  # noqa: E402


class RequirementData(TypedDict):
    """Type for requirement data structure."""

    title: str
    acceptance_criteria: dict[str, str]


class TaskData(TypedDict):
    """Type for task data structure."""

    task_id: str
    requirement_references: list[str]


class TraceabilityResult(TypedDict):
    """Type for traceability validation result."""

    total_criteria: int
    covered_criteria: int
    coverage_percentage: float


class ResearchValidationResult(TypedDict, total=False):
    """Type for research validation result."""

    valid: bool
    error: str
    citation_errors: list[str]
    missing_sources: list[str]
    uncited_claims: list[str]
    total_sources: int
    total_citations: int


class TraceabilityValidator:
    """Validator for requirements traceability and research evidence."""

    def __init__(self, base_path: str) -> None:
        """Initialize the validator with a base path.

        Args:
            base_path: The base path containing specification files.
        """
        self.base_path: Path = Path(base_path)
        self.requirements: dict[str, RequirementData] = {}
        self.tasks: list[TaskData] = []
        self.research_citations: dict[str, str] = {}

    def parse_requirements(self, requirements_file: str) -> dict[str, RequirementData]:
        """Parse requirements.md to extract requirements and acceptance criteria.

        Args:
            requirements_file: The name of the requirements file.

        Returns:
            A dictionary of requirements keyed by requirement number.

        Raises:
            FileNotFoundError: If the requirements file does not exist.
        """
        req_file = self.base_path / requirements_file
        if not req_file.exists():
            raise FileNotFoundError(f"Requirements file not found: {requirements_file}")

        content = req_file.read_text(encoding="utf-8")

        # WHY: Split content by requirement headers and capture requirement numbers
        pattern = r"\n### Requirement (\d+): ([^\n]+)"
        matches = list(re.finditer(pattern, content))

        requirements: dict[str, RequirementData] = {}

        for match in matches:
            req_num = match.group(1).strip()
            req_title = match.group(2).strip()

            # WHY: Find the start and end of this requirement section
            start_pos = match.start()
            end_pos = content.find("\n### Requirement", start_pos + 1)
            if end_pos == -1:
                end_pos = len(content)

            # WHY: Extract this requirement's content
            section_content = content[start_pos:end_pos]

            # WHY: Find acceptance criteria within this section
            ac_match = re.search(
                r"#### Acceptance Criteria\n(.*?)(?=\n###|\n##|\Z)",
                section_content,
                re.DOTALL,
            )
            if not ac_match:
                continue

            ac_text = ac_match.group(1).strip()

            # WHY: Parse acceptance criteria
            requirements[req_num] = RequirementData(
                title=req_title, acceptance_criteria={}
            )

            ac_pattern = r"(\d+)\.\s+(.+)"
            ac_matches = re.findall(ac_pattern, ac_text)
            for ac_num, ac_text_item in ac_matches:
                requirements[req_num]["acceptance_criteria"][f"{req_num}.{ac_num}"] = (
                    ac_text_item.strip()
                )

        self.requirements = requirements
        return requirements

    def parse_tasks(self, tasks_file: str) -> list[TaskData]:
        """Parse tasks.md to extract tasks and their requirement references.

        Args:
            tasks_file: The name of the tasks file.

        Returns:
            A list of task data dictionaries.

        Raises:
            FileNotFoundError: If the tasks file does not exist.
        """
        task_file = self.base_path / tasks_file
        if not task_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {tasks_file}")

        content = task_file.read_text(encoding="utf-8")

        # WHY: Parse tasks and requirement references
        task_pattern = r"- \[ \] (\d+).+?_Requirements: (.+?)_"
        matches = re.findall(task_pattern, content, re.MULTILINE | re.DOTALL)

        tasks: list[TaskData] = []
        for task_num, req_refs in matches:
            # WHY: Parse requirement references
            req_refs_list = [ref.strip() for ref in req_refs.split(",")]
            tasks.append(
                TaskData(task_id=task_num, requirement_references=req_refs_list)
            )

        self.tasks = tasks
        return tasks

    def validate_traceability(
        self,
    ) -> tuple[TraceabilityResult, list[str], list[str]]:
        """Validate that all requirements are covered by tasks.

        Returns:
            A tuple containing:
                - TraceabilityResult with coverage statistics
                - List of missing criteria
                - List of invalid references
        """
        all_criteria: set[str] = set()
        for req_data in self.requirements.values():
            for ac_ref in req_data["acceptance_criteria"]:
                all_criteria.add(ac_ref)

        covered_criteria: set[str] = set()
        invalid_references: set[str] = set()

        for task in self.tasks:
            for req_ref in task["requirement_references"]:
                if req_ref in all_criteria:
                    covered_criteria.add(req_ref)
                else:
                    invalid_references.add(req_ref)

        coverage_pct = (
            (len(covered_criteria) / len(all_criteria) * 100) if all_criteria else 100.0
        )

        return (
            TraceabilityResult(
                total_criteria=len(all_criteria),
                covered_criteria=len(covered_criteria),
                coverage_percentage=coverage_pct,
            ),
            list(all_criteria - covered_criteria),
            list(invalid_references),
        )

    def validate_research_evidence(
        self, research_file: str = "example_research.md"
    ) -> ResearchValidationResult:
        """Validate research document for proper citations and evidence.

        Args:
            research_file: The name of the research file.

        Returns:
            A ResearchValidationResult with validation status and details.
        """
        research_path = self.base_path / research_file
        if not research_path.exists():
            return ResearchValidationResult(
                valid=False, error=f"Research file not found: {research_file}"
            )

        content = research_path.read_text(encoding="utf-8")

        validation_results = ResearchValidationResult(
            valid=True,
            citation_errors=[],
            missing_sources=[],
            uncited_claims=[],
            total_sources=0,
            total_citations=0,
        )

        # WHY: Extract source list (## 3. Browsed Sources section)
        source_pattern = r"## 3\. Browsed Sources\n(.*?)(?=\n##|\Z)"
        source_match = re.search(source_pattern, content, re.DOTALL)

        if not source_match:
            validation_results["valid"] = False
            validation_results["citation_errors"].append(
                "Missing 'Browsed Sources' section"
            )
            return validation_results

        sources_text = source_match.group(1)
        source_lines = [
            line.strip() for line in sources_text.split("\n") if line.strip()
        ]

        # WHY: Extract source URLs and indices
        sources: dict[str, str] = {}
        for line in source_lines:
            src_match = re.match(r"- \[(\d+)\] (https?://\S+)", line)
            if src_match:
                index = src_match.group(1)
                url = src_match.group(2)
                sources[index] = url

        validation_results["total_sources"] = len(sources)

        # WHY: Check for citations in rationale section
        rationale_pattern = r"\| \*\*(.+?)\*\* \| (.+?) \|"
        rationale_matches = re.findall(rationale_pattern, content, re.DOTALL)

        total_citations = 0
        for _technology, rationale in rationale_matches:
            # WHY: Find all citations in rationale
            citations = re.findall(r"\[cite:(\d+)\]", rationale)
            total_citations += len(citations)

            # WHY: Check each citation has corresponding source
            for citation in citations:
                if citation not in sources:
                    validation_results["citation_errors"].append(
                        f"Citation [cite:{citation}] references non-existent source"
                    )
                    validation_results["valid"] = False

        validation_results["total_citations"] = total_citations

        # WHY: Check for factual claims without citations (simplified detection)
        # Look for sentences with specific numbers, percentages, or strong claims
        factual_claims = re.findall(
            r"[^.!?]*\d+(?:\.\d+)?%?[^.!?]*\.|"
            r"[^.!?]*?(excellent|proven|ideal|best|optimal)[^.!?]*\.",
            content,
        )

        for claim in factual_claims:
            if not re.search(r"\[cite:\d+\]", claim):
                validation_results["uncited_claims"].append(claim.strip())

        # WHY: Validate that we have both sources and citations
        if len(sources) == 0:
            validation_results["valid"] = False
            validation_results["citation_errors"].append(
                "No sources found in research document"
            )

        if total_citations == 0:
            validation_results["valid"] = False
            validation_results["citation_errors"].append(
                "No citations found in technology rationales"
            )

        # WHY: Check citation to source ratio (should have reasonable coverage)
        if total_citations < len(sources):
            validation_results["citation_errors"].append(
                f"Too few citations ({total_citations}) "
                f"for number of sources ({len(sources)})"
            )

        return validation_results

    def generate_validation_report(
        self,
        requirements_file: str = "requirements.md",
        tasks_file: str = "tasks.md",
        research_file: str = "example_research.md",
    ) -> str:
        """Generate a complete validation report.

        Args:
            requirements_file: The name of the requirements file.
            tasks_file: The name of the tasks file.
            research_file: The name of the research file.

        Returns:
            A formatted validation report as a string.
        """
        self.parse_requirements(requirements_file)
        self.parse_tasks(tasks_file)

        validation_result, missing, invalid = self.validate_traceability()
        research_validation = self.validate_research_evidence(research_file)

        report = """# Validation Report

## 1. Requirements to Tasks Traceability Matrix

| Requirement | Acceptance Criterion | Implementing Task(s) | Status |
|---|---|---|---|"""

        # WHY: Generate traceability matrix
        for req_num, req_data in self.requirements.items():
            for ac_ref, _ac_text in req_data["acceptance_criteria"].items():
                # WHY: Find tasks implementing this criterion
                implementing_tasks: list[str] = []
                for task in self.tasks:
                    if ac_ref in task["requirement_references"]:
                        implementing_tasks.append(f"Task {task['task_id']}")

                status = "Covered" if implementing_tasks else "Missing"
                tasks_str = (
                    ", ".join(implementing_tasks) if implementing_tasks else "None"
                )

                report += f"\n| {req_num} | {ac_ref} | {tasks_str} | {status} |"

        total_criteria = validation_result["total_criteria"]
        covered_criteria = validation_result["covered_criteria"]
        coverage_pct = validation_result["coverage_percentage"]
        covered_list = [
            ref
            for ref in self._get_all_criteria()
            if ref in self._get_covered_criteria()
        ]
        missing_str = str(missing) if missing else "None"
        invalid_str = str(invalid) if invalid else "None"
        total_sources = research_validation.get("total_sources", 0)
        total_citations = research_validation.get("total_citations", 0)
        research_valid = research_validation.get("valid", False)
        research_status = "PASSED" if research_valid else "FAILED"
        citation_errors = research_validation.get("citation_errors", [])
        uncited_claims = research_validation.get("uncited_claims", [])

        report += f"""

## 2. Coverage Analysis

### Summary
- **Total Acceptance Criteria**: {total_criteria}
- **Criteria Covered by Tasks**: {covered_criteria}
- **Coverage Percentage**: {coverage_pct:.1f}%

### Detailed Status
- **Covered Criteria**: {covered_list}
- **Missing Criteria**: {missing_str}
- **Invalid References**: {invalid_str}

## 3. Research Evidence Validation

### Summary
- **Total Sources**: {total_sources}
- **Total Citations**: {total_citations}
- **Research Validation**: {research_status}

### Evidence Quality
- **Citation Errors**: {len(citation_errors)}
- **Uncited Claims**: {len(uncited_claims)}
"""

        if citation_errors:
            report += "\n#### Citation Issues:\n"
            for error in citation_errors:
                report += f"- {error}\n"

        if uncited_claims:
            report += "\n#### Uncited Factual Claims:\n"
            for claim in uncited_claims[:5]:  # WHY: Limit to first 5
                report += f"- {claim}\n"
            if len(uncited_claims) > 5:
                report += f"- ... and {len(uncited_claims) - 5} more\n"

        report += """

## 4. Final Validation
"""

        # WHY: Use shared threshold for minimum requirements coverage (100%)
        min_coverage = VERIFICATION.MIN_REQUIREMENTS_COVERAGE * 100
        requirements_valid = coverage_pct >= min_coverage and not invalid
        research_is_valid = research_validation.get("valid", False)

        if requirements_valid and research_is_valid:
            report += (
                f"[PASS] **VALIDATION PASSED**\n\nAll {total_criteria} acceptance "
                f"criteria are fully traced to implementation tasks AND all research "
                f"claims are properly cited with verifiable sources. The plan is "
                f"validated and ready for execution."
            )
        elif not requirements_valid and research_is_valid:
            report += (
                f"[FAIL] **VALIDATION FAILED** - Requirements Issues\n\n"
                f"{len(missing)} criteria not covered, {len(invalid)} invalid "
                f"references. Research evidence is properly cited, but requirements "
                f"traceability needs attention."
            )
        elif requirements_valid and not research_is_valid:
            report += (
                f"[FAIL] **VALIDATION FAILED** - Research Evidence Issues\n\n"
                f"Requirements traceability is complete, but research evidence has "
                f"{len(citation_errors)} citation errors and {len(uncited_claims)} "
                f"uncited claims. This violates the evidence-based protocol and "
                f"prevents professional use."
            )
        else:
            report += (
                f"[FAIL] **VALIDATION FAILED** - Multiple Issues\n\n"
                f"Requirements: {len(missing)} criteria not covered, {len(invalid)} "
                f"invalid references. Research: {len(citation_errors)} citation "
                f"errors, {len(uncited_claims)} uncited claims."
            )

        return report

    def _get_all_criteria(self) -> set[str]:
        """Get all acceptance criteria references.

        Returns:
            A set of all acceptance criteria reference strings.
        """
        all_criteria: set[str] = set()
        for req_data in self.requirements.values():
            for ac_ref in req_data["acceptance_criteria"]:
                all_criteria.add(ac_ref)
        return all_criteria

    def _get_covered_criteria(self) -> set[str]:
        """Get all covered acceptance criteria references.

        Returns:
            A set of covered acceptance criteria reference strings.
        """
        covered_criteria: set[str] = set()
        all_criteria = self._get_all_criteria()

        for task in self.tasks:
            for req_ref in task["requirement_references"]:
                if req_ref in all_criteria:
                    covered_criteria.add(req_ref)

        return covered_criteria


def main() -> int:
    """Main entry point for the traceability validator.

    Returns:
        Exit code: 0 for success, 1 for failure.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate specification architect traceability"
    )
    parser.add_argument(
        "--path", default=".", help="Base path containing specification files"
    )
    parser.add_argument(
        "--requirements", default="requirements.md", help="Requirements file name"
    )
    parser.add_argument("--tasks", default="tasks.md", help="Tasks file name")
    parser.add_argument(
        "--research", default="example_research.md", help="Research file name"
    )

    args = parser.parse_args()

    try:
        validator = TraceabilityValidator(args.path)
        report = validator.generate_validation_report(
            args.requirements, args.tasks, args.research
        )
        print(report)

        # WHY: Exit with error code if validation fails
        validation_result, _missing, invalid = validator.validate_traceability()
        research_validation = validator.validate_research_evidence(args.research)

        # WHY: Use shared threshold for minimum requirements coverage (100%)
        min_coverage: float = VERIFICATION.MIN_REQUIREMENTS_COVERAGE * 100
        coverage_pct = validation_result["coverage_percentage"]
        requirements_valid = coverage_pct >= min_coverage and not invalid
        research_valid = research_validation.get("valid", False)

        if not requirements_valid or not research_valid:
            return 1
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
