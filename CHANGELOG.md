# Changelog

All notable changes to this project will be documented in this file.
    ## [1.7.0] - 2026-06-10

### Bug Fixes

- Replace broken references/ link with universal-skill prose pointer    
- Restructure amoa-prrd-trdd-kanban to CPV 7-section format (<5000)    
- Stage uv.lock in the release commit (closes #10)    
- Hook timeouts are seconds, not milliseconds    
- Devitalize execution-shaped patterns flagged by CPV strict scan    
- Clear all CPV strict MINOR+NIT findings — gate now exits 0    

### Documentation

- Add approval-tiers + proposal lifecycle + baseline governance section (closes #11)    

### Features

- Add ORCH's PRRD/TRDD/Kanban layer (amoa-prrd-trdd-kanban)    
- Add Approval discipline section to amoa-prrd-trdd-kanban    
- Bootstrap PRRD with G1 GitHub self-id golden rule    
- Adopt the markdown memory system (closes #12)    

### Miscellaneous

- Update uv.lock (stale from v1.6.12 release — see issue #10)    
- Remove legacy git-hooks/pre-push (dangling validate_plugin.py ref)    


