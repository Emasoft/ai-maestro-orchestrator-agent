## Table of Contents
- [Design Search Script](#design-search-script)
- [Script Location](#script-location)
- [Usage Examples](#usage-examples)

# Design Document Scripts

## Design Search Script

| Script | Purpose | Usage |
|--------|---------|-------|
| `amoa_design_search.py` | Search design documents for task delegation | `python scripts/amoa_design_search.py --type <TYPE> --status <STATUS>` |

Use `amoa_design_search.py` when:
- Looking up design specifications to include in task delegations
- Finding related designs for context when assigning work
- Verifying design status before creating implementation tasks

## Script Location

The script is located at `../../scripts/amoa_design_search.py` relative to this skill.

## Usage Examples

```bash
# Find all pending designs
python scripts/amoa_design_search.py --status pending

# Find designs by type
python scripts/amoa_design_search.py --type module

# Find designs for a specific component
python scripts/amoa_design_search.py --type component --status approved
```
