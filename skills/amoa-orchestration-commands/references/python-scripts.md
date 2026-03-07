## Table of Contents
- Script inventory - Scripts and their command mappings
- Script output rules - Token-efficient output protocol

---

## Script Inventory

The following scripts implement the orchestration commands. Located in the plugin's `scripts/` directory:

| Script | Purpose | Used By |
|--------|---------|---------|
| `amoa_start_orchestration.py` | Activates orchestration phase | `/start-orchestration` |
| `amoa_orchestration_status.py` | Displays phase status | `/orchestration-status` |
| `amoa_check_orchestrator_status.py` | Shows loop state | `/orchestrator-status` |
| `amoa_setup_orchestrator_loop.py` | Creates loop state file | `/orchestrator-loop` |
| `amoa_orchestrator_stop_check.py` | Stop hook enforcement | Hook event |

---

## Script Output Rules

All scripts invoked by this skill MUST follow the token-efficient output protocol:

1. **Verbose output** goes to a timestamped report file in `docs_dev/reports/`
2. **Stdout** emits only 2-3 lines: `[OK/ERROR] script_name - summary` + `Report: path`
3. Scripts accept `--output-dir` to override the default report directory
4. **EXCEPTION**: Scripts in `scripts/amoa_stop_check/` MUST output JSON to stdout (Claude Code hook requirement)
