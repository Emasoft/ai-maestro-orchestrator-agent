# Design Folder Structure - Part 4: Multi-Platform and Scripts

Multi-platform project organization, state file integration, and script support.

## Contents

- 6. Multi-Platform Projects
  - 6.1 Shared resources
  - 6.2 Platform-specific customization
- 7. State File Integration
- 8. Script Support
  - 8.1 eoa_init_design_folders.py   - 8.2 eoa_compile_handoff.py - 9. Checklists
  - 9.1 Design Folder Setup Checklist
  - 9.2 Per-Module Design Checklist

---

## 6. Multi-Platform Projects

### 6.1 Shared resources

For multi-platform projects, put shared resources in `designs/shared/`:

```
design/requirements/
├── shared/
│   ├── ARCHITECTURE.md           # Overall architecture
│   ├── API_SPEC.md               # Backend API (shared)
│   ├── DATA_MODELS.md            # Shared data models
│   └── AUTH_FLOW.md              # Auth flow (cross-platform)
├── web/
│   └── specs/
│       └── auth-ui.md            # Web-specific UI spec
├── ios/
│   └── specs/
│       └── auth-ui.md            # iOS-specific UI spec
└── android/
    └── specs/
        └── auth-ui.md            # Android-specific UI spec
```

### 6.2 Platform-specific customization

When same module has platform variations:

1. Create shared spec in `designs/shared/`
2. Create platform-specific overlay in `designs/{platform}/specs/`
3. Reference shared spec from platform spec:

```markdown
# Auth UI Spec (iOS)

## Base Specification

See: `[../shared/AUTH_FLOW.md]\(../shared/AUTH_FLOW.md\)`

## iOS-Specific Requirements

### Face ID Integration

- Use LocalAuthentication framework
- Fallback to passcode if biometrics unavailable
- ...
```

---

## 7. State File Integration

Add design folder tracking to Plan Phase state file:

```yaml
# In design/state/plan-phase.md
design_folders:
  root: "design"
  platforms:
    - web
    - ios
  initialized: true
  template_count: 5
  spec_count: 3
  rdd_count: 3
```

Add handoff tracking to Orchestration Phase state file:

```yaml
# In design/state/exec-phase.md
active_assignments:
  - agent: "implementer-1"
    module: "auth-core"
    handoff_path: "design/handoffs/implementer-1/auth-core-handoff.md"
    config_provided:
      - "design/config/web/tsconfig.json"
      - "design/config/shared/env.example"
```

---

## 8. Script Support

### 8.1 eoa_init_design_folders.py 
Creates standardized folder structure:

```bash
python3 eoa_init_design_folders.py <!-- TODO: Script not implemented --> --platforms web ios android

# Creates:
# design/requirements/shared/
# design/requirements/web/templates/
# design/requirements/web/specs/
# design/requirements/web/rdd/
# design/requirements/ios/templates/
# design/requirements/ios/specs/
# design/requirements/ios/rdd/
# design/requirements/android/templates/
# design/requirements/android/specs/
# design/requirements/android/rdd/
# design/config/shared/
# design/config/web/
# design/config/ios/
# design/config/android/
# design/handoffs/
# design/archive/
```

### 8.2 eoa_compile_handoff.py 
Compiles template to handoff:

```bash
python3 eoa_compile_handoff.py <!-- TODO: Script not implemented --> auth-core implementer-1 --platform web

# Output:
# Compiled handoff saved to: design/handoffs/implementer-1/auth-core-handoff.md
```

---

## 9. Checklists

### 9.1 Design Folder Setup Checklist

- [ ] Create `design/` root folder
- [ ] Create `designs/shared/` for cross-platform docs
- [ ] Create `designs/{platform}/` for each platform
- [ ] Create `templates/`, `specs/`, `rdd/` in each platform folder
- [ ] Create `config/` with platform subfolders
- [ ] Create `handoffs/` folder
- [ ] Create `archive/` folder
- [ ] Add design files to git tracking
- [ ] Update `.gitignore` for secrets only
- [ ] Create base templates in each platform

### 9.2 Per-Module Design Checklist

- [ ] Create module spec in `designs/{platform}/specs/`
- [ ] Create RDD in `designs/{platform}/rdd/`
- [ ] Compile handoff to `handoffs/{agent-id}/`
- [ ] Include config files in `config/{platform}/`
- [ ] Reference handoff path in assignment message
