## Table of Contents
- [Pattern Selection Guide](#pattern-selection-guide)
- [Exit Codes](#exit-codes)
- [Output Format](#output-format)
- [Error Handling](#error-handling)
- [Verification Checklist](#verification-checklist)
- [Script Output Rules](#script-output-rules)

---

## Pattern Selection Guide

| Situation | Pattern | Reference |
|-----------|---------|-----------|
| Prove a function returns correct value | Evidence-based verification | [evidence-based-verification.md](./evidence-based-verification.md) |
| Check if a script succeeded | Exit code proof | [exit-code-proof.md](./exit-code-proof.md) |
| Verify user workflow works | E2E testing | [end-to-end-testing.md](./end-to-end-testing.md) |
| Test API calls database correctly | Integration verification | [integration-verification.md](./integration-verification.md) |
| Build CI/CD pipeline | Exit code proof + E2E | [combining-patterns.md](./combining-patterns.md) |
| Cross-platform script | Platform-aware commands | [cross-platform-support.md](./cross-platform-support.md) |
| Report to orchestrator | Evidence format | [evidence-format.md](./evidence-format.md) |
| Run tests in isolation | Worktree testing | [testing-protocol.md](./testing-protocol.md) |
| Update GitHub issues | gh CLI integration | [github-integration.md](./github-integration.md) |
| Debug flaky tests | Troubleshooting guide | [troubleshooting.md](./troubleshooting.md) |
| Automate quality checks | Automation scripts | [automation-scripts.md](./automation-scripts.md) |

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | Success | Continue workflow |
| `1` | General failure | Stop and report |
| `2` | Script validation failed | Fix script issues |

## Output Format

When verification tasks complete, provide results in this format:

| Field | Description | Example |
|-------|-------------|---------|
| **Status** | PASSED, FAILED, or ERROR | `PASSED` |
| **Evidence Type** | Type of verification performed | `EXIT_CODE`, `FILE_CONTENT`, `TEST_RESULT` |
| **Evidence** | Measurable proof collected | `Exit code: 0`, `All 42 tests passed` |
| **Timestamp** | When verification was performed | `2024-01-15T10:30:00Z` |
| **Details** | Additional context or failure reasons | `See test_results.json for details` |

## Error Handling

| Issue | Cause | Resolution |
|-------|-------|------------|
| Tests pass locally, fail in CI | Environment differences | Check env vars, dependencies |
| Exit code 0 but process failed | Missing exit code in script | Add explicit `sys.exit(1)` on failure |
| Integration test timeout | Slow service startup | Increase timeout, add health checks |
| Flaky E2E test | Race conditions | Add explicit waits, retry logic |

See [Troubleshooting](./troubleshooting.md) for complete solutions.

## Verification Checklist

Copy this checklist and track your progress:

- [ ] Understand verification principles (never trust assumptions, measure what matters)
- [ ] Define expected outcome for the verification task
- [ ] Select appropriate verification pattern (evidence-based, exit code, E2E, or integration)
- [ ] Prepare test environment (dependencies, services, test data)
- [ ] Execute verification steps according to selected pattern
- [ ] Collect measurable evidence (return values, output files, exit codes, state changes)
- [ ] Compare evidence to expected outcome
- [ ] Document verification results in standard format
- [ ] Handle failures with fail-fast approach (stop and report immediately)
- [ ] Ensure reproducibility of verification (can be repeated with same results)
- [ ] Report results to orchestrator with proper evidence format
- [ ] Update GitHub issues if applicable (status transitions, evidence comments)
- [ ] Clean up test environment and temporary resources

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
