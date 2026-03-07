## Table of Contents
- Script Output Rules
- Token-Efficient Output Protocol
- Exception for Stop-Check Scripts

# Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: status + filepath
3. Scripts accept `--output-dir` to override the default report directory
4. Format: `[OK/ERROR] script_name - one-line summary\nReport: docs_dev/reports/script_name-YYYYMMDD-HHMMSS.md`
5. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
