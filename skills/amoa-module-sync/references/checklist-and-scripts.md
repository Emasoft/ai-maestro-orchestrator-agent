## Table of Contents

- 1 Module management checklist
- 2 Script output rules and token-efficient protocol

---

## 1 Module Management Checklist

Copy this checklist and track your progress:

- [ ] Identify module management action needed (add/modify/remove/prioritize/reassign)
- [ ] Verify Orchestration Phase is active
- [ ] Confirm gh CLI is authenticated
- [ ] Verify AI Maestro messaging system (AMP) is running
- [ ] Execute appropriate command with required parameters
- [ ] Check module state updated in design/state/exec-phase.md
- [ ] Verify GitHub Issue created/updated with correct labels
- [ ] Confirm agent notification sent via AI Maestro (if applicable)
- [ ] Validate module-to-issue 1:1 relationship maintained
- [ ] Document any errors in troubleshooting log

## 2 Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
