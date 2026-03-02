#!/usr/bin/env python3
"""Universal consistency verification script with source-routed verification.

WHY: Provides a pluggable verification system that routes verification requests
to appropriate source-specific verifiers (file, git, url, json, etc.).
WHY: Enables batch verification with error aggregation and graceful degradation.
WHY: Uses dict dispatch pattern for extensibility and clean separation of concerns.
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Union

# WHY: Import cross-platform utilities for subprocess and file operations
# WHY: Dynamic path insertion required before importing local modules
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import run_command, atomic_write_json  # type: ignore[import-not-found]  # noqa: E402
from thresholds import TIMEOUTS  # type: ignore[import-not-found]  # noqa: E402


class Verifier(ABC):
    """Base class for all source-specific verifiers.

    WHY: Provides common interface for all verification backends.
    WHY: Enables polymorphic verification dispatch without conditional logic.
    """

    @abstractmethod
    def verify(self, item: str, context: dict[str, Any]) -> dict[str, Any]:
        """Verify an item from this source.

        Args:
            item: The item identifier to verify (path, URL, commit hash, etc.)
            context: Additional verification context (expected_hash, schema, etc.)

        Returns:
            Verification result dict with keys: verified (bool), error (str|None)

        WHY: Standard interface allows uniform batch processing.
        """
        pass


class FileVerifier(Verifier):
    """Verifies file existence, hashes, and permissions.

    WHY: Files are fundamental to most verification scenarios.
    WHY: Hash verification prevents silent corruption.
    WHY: Permission checks ensure security requirements are met.
    """

    def verify(self, item: str, context: dict[str, Any]) -> dict[str, Any]:
        """Verify file exists and optionally check hash/permissions."""
        path = Path(item)

        # WHY: Non-existent files fail immediately - no point checking further
        if not path.exists():
            return {"verified": False, "error": f"File does not exist: {item}"}

        # WHY: Verify it's actually a file, not a directory or symlink
        if not path.is_file():
            return {"verified": False, "error": f"Path is not a file: {item}"}

        # WHY: Hash verification detects corruption or tampering
        if "expected_hash" in context:
            try:
                actual_hash = self._compute_hash(
                    path, context.get("hash_algo", "sha256")
                )
                if actual_hash != context["expected_hash"]:
                    return {
                        "verified": False,
                        "error": f"Hash mismatch. Expected: {context['expected_hash']}, Got: {actual_hash}",
                    }
            except Exception as e:
                return {"verified": False, "error": f"Hash computation failed: {e}"}

        # WHY: Permission verification ensures security policies are enforced
        if "expected_mode" in context:
            actual_mode = oct(path.stat().st_mode)[-3:]
            expected_mode = str(context["expected_mode"])
            if actual_mode != expected_mode:
                return {
                    "verified": False,
                    "error": f"Permission mismatch. Expected: {expected_mode}, Got: {actual_mode}",
                }

        return {"verified": True, "error": None}

    def _compute_hash(self, path: Path, algo: str = "sha256") -> str:
        """Compute file hash using specified algorithm.

        WHY: Supports multiple hash algorithms for different use cases.
        WHY: Streams file content to handle large files efficiently.
        """
        hash_obj = hashlib.new(algo)
        with open(path, "rb") as f:
            # WHY: Read in chunks to avoid loading entire file into memory
            for chunk in iter(lambda: f.read(65536), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()


class GitVerifier(Verifier):
    """Verifies git commits, branches, and tags exist.

    WHY: Git verification ensures referenced commits/branches are valid.
    WHY: Prevents broken references in documentation and workflows.
    """

    def verify(self, item: str, context: dict[str, Any]) -> dict[str, Any]:
        """Verify git object exists in repository."""
        repo_path = context.get("repo_path", ".")
        item_type = context.get("type", "commit")  # commit, branch, tag

        # WHY: Different git objects require different verification commands
        if item_type == "commit":
            return self._verify_commit(item, repo_path)
        elif item_type == "branch":
            return self._verify_branch(item, repo_path)
        elif item_type == "tag":
            return self._verify_tag(item, repo_path)
        else:
            return {"verified": False, "error": f"Unknown git type: {item_type}"}

    def _verify_commit(self, commit_hash: str, repo_path: str) -> dict[str, Any]:
        """Verify commit exists in repository.

        WHY: Uses git cat-file to check object existence efficiently.
        """
        try:
            # WHY: run_command provides cross-platform subprocess execution
            # WHY: Use git-specific timeout from shared thresholds
            code, out, err = run_command(
                ["git", "-C", repo_path, "cat-file", "-e", commit_hash],
                timeout=TIMEOUTS.GIT,
            )
            if code == 0:
                return {"verified": True, "error": None}
            return {"verified": False, "error": f"Commit not found: {commit_hash}"}
        except TimeoutError:
            return {"verified": False, "error": "Git command timeout"}
        except Exception as e:
            return {"verified": False, "error": f"Git verification failed: {e}"}

    def _verify_branch(self, branch: str, repo_path: str) -> dict[str, Any]:
        """Verify branch exists in repository.

        WHY: Uses git show-ref to check branch existence without checkout.
        """
        try:
            # WHY: run_command provides cross-platform subprocess execution
            # WHY: Use git-specific timeout from shared thresholds
            code, out, err = run_command(
                [
                    "git",
                    "-C",
                    repo_path,
                    "show-ref",
                    "--verify",
                    f"refs/heads/{branch}",
                ],
                timeout=TIMEOUTS.GIT,
            )
            if code == 0:
                return {"verified": True, "error": None}
            return {"verified": False, "error": f"Branch not found: {branch}"}
        except TimeoutError:
            return {"verified": False, "error": "Git command timeout"}
        except Exception as e:
            return {"verified": False, "error": f"Git verification failed: {e}"}

    def _verify_tag(self, tag: str, repo_path: str) -> dict[str, Any]:
        """Verify tag exists in repository.

        WHY: Uses git show-ref to check tag existence.
        """
        try:
            # WHY: run_command provides cross-platform subprocess execution
            # WHY: Use git-specific timeout from shared thresholds
            code, out, err = run_command(
                ["git", "-C", repo_path, "show-ref", "--verify", f"refs/tags/{tag}"],
                timeout=TIMEOUTS.GIT,
            )
            if code == 0:
                return {"verified": True, "error": None}
            return {"verified": False, "error": f"Tag not found: {tag}"}
        except TimeoutError:
            return {"verified": False, "error": "Git command timeout"}
        except Exception as e:
            return {"verified": False, "error": f"Git verification failed: {e}"}


class URLVerifier(Verifier):
    """Verifies URLs are reachable via HEAD request.

    WHY: HEAD requests verify availability without downloading content.
    WHY: Lightweight check for link validation in documentation.
    """

    def verify(self, item: str, context: dict[str, Any]) -> dict[str, Any]:
        """Verify URL is reachable."""
        # WHY: Use API timeout from shared thresholds as default for HTTP requests
        timeout = context.get("timeout", TIMEOUTS.API)

        try:
            # WHY: HEAD request checks availability without downloading body
            req = urllib.request.Request(item, method="HEAD")
            # WHY: User-Agent header prevents some servers from blocking requests
            req.add_header("User-Agent", "ConsistencyVerifier/1.0")

            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.getcode()
                # WHY: 2xx and 3xx are considered successful
                if 200 <= status < 400:
                    return {"verified": True, "error": None}
                return {"verified": False, "error": f"HTTP {status}"}
        except urllib.error.HTTPError as e:
            return {"verified": False, "error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"verified": False, "error": f"URL error: {e.reason}"}
        except Exception as e:
            return {"verified": False, "error": f"Request failed: {e}"}


class JSONVerifier(Verifier):
    """Verifies JSON is valid and optionally matches schema.

    WHY: JSON validation prevents malformed configuration files.
    WHY: Schema validation enforces data contracts.
    """

    def verify(self, item: str, context: dict[str, Any]) -> dict[str, Any]:
        """Verify JSON file is valid and optionally matches schema."""
        # WHY: Support both file paths and raw JSON strings
        # WHY: Use Path for cross-platform file operations
        item_path = Path(item)
        if item_path.is_file():
            try:
                with open(item_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                return {"verified": False, "error": f"Invalid JSON: {e}"}
            except Exception as e:
                return {"verified": False, "error": f"Failed to read file: {e}"}
        else:
            try:
                data = json.loads(item)
            except json.JSONDecodeError as e:
                return {"verified": False, "error": f"Invalid JSON: {e}"}

        # WHY: Optional schema validation enforces structure
        if "schema" in context:
            schema_result = self._validate_schema(data, context["schema"])
            if not schema_result["verified"]:
                return schema_result

        return {"verified": True, "error": None}

    def _validate_schema(self, data: Any, schema: dict[str, Any]) -> dict[str, Any]:
        """Validate data against simple schema.

        WHY: Basic schema validation without external dependencies.
        WHY: Checks required fields and types only (not full JSON Schema).
        """
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # WHY: Check required fields exist
        if isinstance(data, dict):
            for field in required:
                if field not in data:
                    return {
                        "verified": False,
                        "error": f"Missing required field: {field}",
                    }

            # WHY: Check field types match
            for field, field_schema in properties.items():
                if field in data:
                    expected_type = field_schema.get("type")
                    if expected_type:
                        actual_value = data[field]
                        if not self._check_type(actual_value, expected_type):
                            return {
                                "verified": False,
                                "error": f"Field '{field}' has wrong type. Expected: {expected_type}",
                            }

        return {"verified": True, "error": None}

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON type.

        WHY: Maps JSON Schema types to Python types.
        """
        # WHY: Explicit type annotation ensures isinstance gets proper _ClassInfo type
        type_map: dict[str, Union[type[Any], tuple[type[Any], ...]]] = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        expected_py_type = type_map.get(expected_type)
        if expected_py_type is not None:
            return isinstance(value, expected_py_type)
        return False


class ConsistencyVerifier:
    """Main verification dispatcher with pluggable backends.

    WHY: Central point for routing verification requests to appropriate verifiers.
    WHY: Dict dispatch pattern enables easy addition of new verifiers.
    WHY: Graceful degradation allows partial verification when sources unavailable.
    """

    def __init__(self, verbose: bool = False):
        """Initialize verifier with available backends.

        WHY: Dict dispatch avoids long if-elif chains and enables extensibility.
        """
        self.verbose = verbose
        # WHY: Registry pattern allows runtime addition of verifiers
        self.verifiers: dict[str, Verifier] = {
            "file": FileVerifier(),
            "git": GitVerifier(),
            "url": URLVerifier(),
            "json": JSONVerifier(),
        }

    def verify_item(
        self, source: str, item: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Verify a single item using appropriate verifier.

        WHY: Single point of entry for all verification requests.
        WHY: Returns consistent format regardless of verifier type.
        """
        if source not in self.verifiers:
            # WHY: Unknown sources fail gracefully instead of crashing
            return {
                "source": source,
                "item": item,
                "verified": False,
                "error": f"Unknown source type: {source}",
            }

        verifier = self.verifiers[source]

        try:
            result = verifier.verify(item, context)
            # WHY: Add source and item to result for batch processing
            result["source"] = source
            result["item"] = item
            return result
        except Exception as e:
            # WHY: Catch-all ensures verification never crashes the batch
            return {
                "source": source,
                "item": item,
                "verified": False,
                "error": f"Verification exception: {e}",
            }

    def verify_batch(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Verify multiple items and aggregate results.

        WHY: Batch processing is more efficient than individual calls.
        WHY: Error aggregation provides overview of all failures.
        """
        results = []
        total = len(items)
        verified_count = 0
        failed_count = 0

        for item_spec in items:
            source = item_spec.get("source", "")
            item = item_spec.get("item", "")
            # WHY: Extract all other keys as verification context
            context = {
                k: v for k, v in item_spec.items() if k not in ("source", "item")
            }

            if self.verbose:
                print(f"Verifying {source}:{item}...", file=sys.stderr)

            result = self.verify_item(source, item, context)
            results.append(result)

            if result["verified"]:
                verified_count += 1
            else:
                failed_count += 1
                if self.verbose:
                    print(f"  FAILED: {result['error']}", file=sys.stderr)

        return {
            "total": total,
            "verified": verified_count,
            "failed": failed_count,
            "results": results,
        }


def main() -> None:
    """CLI entry point for consistency verification.

    WHY: Provides command-line interface for automation and scripting.
    WHY: JSON input/output enables integration with other tools.
    """
    parser = argparse.ArgumentParser(
        description="Universal consistency verification with source-routed backends"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with items to verify",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file for verification results",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose progress to stderr",
    )

    args = parser.parse_args()

    # WHY: Read input specifications from JSON file
    try:
        with open(args.input, encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to read input file: {e}", file=sys.stderr)
        sys.exit(1)

    # WHY: Validate input format
    if not isinstance(items, list):
        print(
            "ERROR: Input must be a JSON array of item specifications", file=sys.stderr
        )
        sys.exit(1)

    # WHY: Perform batch verification
    verifier = ConsistencyVerifier(verbose=args.verbose)
    verification_results = verifier.verify_batch(items)

    # WHY: Write results to output file using atomic write
    try:
        atomic_write_json(verification_results, Path(args.output), indent=2)
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)

    # WHY: Exit with non-zero if any verifications failed
    if verification_results["failed"] > 0:
        print(
            f"Verification completed: {verification_results['verified']}/{verification_results['total']} passed",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.verbose:
        print(
            f"All {verification_results['total']} items verified successfully",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
