# Changelog

All notable changes to this project will be documented in this file.
    ## [1.6.9] - 2026-04-10

### Bug Fixes

- Normalize assign: label prefix (was assigned: in reassignment scripts)    
- Add AMP communication restriction to all sub-agents    
- Correct communication rules in main-agent    
- Correct governance terminology, version sync, and communication rules    
- Resolve all CPV MINOR issues (2 → 0)    
- Stop hook ImportError — run amoa_stop_check as module    
- Publish.py runs CPV validation remotely + pre-push enforces --strict    
- Ruff F541 — remove extraneous f-prefix in publish.py    
- Remove CPV_PUBLISH_PIPELINE bypass from pre-push hook — CPV --strict always runs    
- Publish.py + pre-push use cpv-remote-validate via uvx    
- Remove unused imports (ruff F401)    

### Features

- Add compatible-titles and compatible-clients to agent profile    
- Add communication permissions from title-based graph    
- Add publish.py and lint_files.py for publish pipeline    
- Add smart publish pipeline + pre-push hook enforcement    

### Miscellaneous

- Update uv.lock    

### Tests

- Fix stale OUTPUT_SKILLS path in replacement-handoff test    
- Fix stale OUTPUT_SKILLS paths in all unit tests    
- Remove conceptual tests for unimplemented --project-id/--project-name    

### Ci

- Update validate.yml to use cpv-remote-validate --strict    
- Strict publish.py + pre-push hook + release.yml propagation    


