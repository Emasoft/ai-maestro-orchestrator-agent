# Orchestration Commands Skill

A comprehensive skill documenting all orchestration phase commands in the EOA Tool-Chain.

## Purpose

This skill teaches how to use the orchestration commands that manage:
- Starting and coordinating orchestration phases
- Monitoring module and agent progress
- Controlling the orchestrator loop
- Handling cancellation and cleanup

## Contents

### Main File

- **SKILL.md** - Entry point with command summary and TOC-driven references

### Reference Files

| File | Description |
|------|-------------|
| `references/start-orchestration-procedure.md` | How to initialize orchestration phase |
| `references/orchestration-loop-mechanics.md` | Loop iterations, polling, monitoring |
| `references/status-monitoring.md` | Status checks and reporting |
| `references/cancellation-cleanup.md` | Cancel and cleanup procedures |
| `references/state-file-format.md` | State file structure and fields |
| `references/troubleshooting.md` | Common issues and solutions |

## Commands Covered

| Command | Purpose |
|---------|---------|
| `/start-orchestration` | Enter Orchestration Phase |
| `/orchestration-status` | View module/agent status |
| `/orchestrator-status` | Check loop status and pending tasks |
| `/orchestrator-loop` | Main orchestrator loop control |
| `/cancel-orchestrator` | Cancel orchestrator loop |

## Related Scripts

Located in `../../scripts/`:

| Script | Used By |
|--------|---------|
| `eoa_start_orchestration.py` | `/start-orchestration` |
| `eoa_orchestration_status.py` <!-- TODO: Script not implemented --> | `/orchestration-status` |
| `eoa_check_orchestrator_status.py` <!-- TODO: Script not implemented --> | `/orchestrator-status` |
| `eoa_setup_orchestrator_loop.py` | `/orchestrator-loop` |
| `eoa_orchestrator_stop_check.py` <!-- TODO: Script not implemented --> | Stop hook |

## Usage

Read SKILL.md first, then follow the TOC links to relevant reference files based on your current task.

## Prerequisites

- Plan Phase completed (`/approve-plan` executed)
- State file `design/state/exec-phase.md` exists
- Understanding of Two-Phase Mode workflow
