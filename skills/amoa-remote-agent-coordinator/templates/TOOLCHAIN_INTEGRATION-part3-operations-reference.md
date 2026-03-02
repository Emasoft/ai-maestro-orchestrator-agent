# Toolchain Integration: Operations & Reference

**Parent Document**: [TOOLCHAIN_INTEGRATION.md](./TOOLCHAIN_INTEGRATION.md)
**Part**: 3 of 3

---

## Error Handling

### Compilation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| **Missing variable mapping** | Language mapping file incomplete | Add missing variable to `{LANGUAGE}.json` |
| **Unknown language** | Language not supported | Create new language mapping file |
| **Template variable remains** | Substitution incomplete | Check substitution dictionary |
| **Invalid command** | Tool not available on platform | Use platform-specific fallback |

### Setup Errors (Remote Agent)

| Error | Cause | Fix |
|-------|-------|-----|
| **Command not found** | Tool not in PATH | Install missing tool |
| **Permission denied** | Missing execute permission | `chmod +x script.sh` |
| **Version mismatch** | Wrong version installed | Reinstall with correct version |
| **Network error** | Download failed | Retry or use offline cache |
| **Config conflict** | Existing config differs | Backup and regenerate |

---

## Checklist Integration

### Checklist Types in Toolchain Workflow

1. **Toolchain Setup Checklist** (Phase 3)
   - Embedded in compiled `TOOLCHAIN.md`
   - Agent verifies each item after setup
   - Reports completion to orchestrator

2. **Development Workflow Checklist** (Implementation Phase)
   - Agent follows during coding
   - Ensures code quality standards met
   - Checked before PR creation

3. **Verification Checklist** (Code Review Phase)
   - Reviewer follows this checklist
   - All language-specific checks must pass
   - Generated from `template_generator.py --type checklist`

4. **Platform-Specific Checklists** (Pre-Merge & Release)
   - One per target platform
   - Must ALL pass before merge/release
   - Cross-compilation verification included

### Checklist Status Tracking

**Tool**: `checklist_validator.py`

**Usage**:
```bash
python3 skills/verification-patterns/scripts/checklist_validator.py \
  --checklist templates/checklists/{LANGUAGE}-checklist.json \
  --status current-status.json \
  --output validation-report.json
```

**Integration with Pipeline**:
- Code Review Stage: Run validator before PR approval
- Pre-Merge Stage: Run validator with ALL platform checklists
- Release Stage: Run validator + platform tests

---

## Multiplatform Toolchain Strategy

### Strategy 1: Single Unified Toolchain

**Use when**: Single language, multiple target platforms

**Structure**:
```markdown
# Toolchain: {PROJECT_NAME} ({LANGUAGE})

## Core Configuration
[Base toolchain setup]

## Cross-Platform Build
[Build commands for all targets]

## Platform-Specific Testing
### Linux
[Linux tests]

### macOS
[macOS tests]

### Windows
[Windows tests]
```

**Agent workflow**: Agent runs core setup + specific platform section.

---

### Strategy 2: Platform-Specific Toolchains

**Use when**: Complex platform-specific requirements

**Structure**:
- `TOOLCHAIN-linux.md`
- `TOOLCHAIN-macos.md`
- `TOOLCHAIN-windows.md`

**Agent workflow**: Agent receives only relevant platform toolchain.

**Orchestrator logic**:
```bash
if [[ $REMOTE_AGENT_PLATFORM == "linux" ]]; then
  compile_toolchain.py --platforms linux --output TOOLCHAIN-linux.md
fi
```

---

### Strategy 3: Mixed Language Toolchains

**Use when**: Project uses multiple languages

**Structure**:
```markdown
# Toolchain: {PROJECT_NAME} (Mixed)

## Primary Language: {LANGUAGE_1}
[Full toolchain for primary language]

## Secondary Language: {LANGUAGE_2}
[Minimal toolchain for secondary language]

## Integration
[How languages interact during build/test]
```

**Example**: Rust + Python project
- Primary: Rust (core application)
- Secondary: Python (build scripts, tests)
- Integration: Python scripts call `cargo build`

---

## Toolchain Caching Strategy

### Goal: Avoid re-compiling identical toolchains

**Cache Key Generation**:
```
{LANGUAGE}:{VERSION}:{PLATFORMS}:{TIMESTAMP_DAILY}
```

**Example**:
```
rust:1.75:linux,macos:2026-01-05
```

**Cache Storage**:
```
/tmp/eoa-toolchain-cache/{CACHE_KEY}/TOOLCHAIN.md
```

**Orchestrator Logic**:
1. Generate cache key
2. Check if cached toolchain exists
3. If exists and fresh (< 24 hours): Use cached version
4. If not: Compile new toolchain and cache it

**Cache Invalidation**:
- Language mapping file changes
- BASE_TOOLCHAIN.md template changes
- Cache older than 24 hours

---

## Testing Toolchain Integration

### Unit Tests

**Test compilation**:
```bash
python3 -m pytest skills/remote-agent-coordinator/tests/test_compile_toolchain.py
```

**Test language detection**:
```bash
python3 -m pytest skills/remote-agent-coordinator/tests/test_language_detection.py
```

### Integration Tests

**Test full workflow**:
```bash
# 1. Compile toolchain
compile_toolchain.py --language rust --platforms linux --output /tmp/test-toolchain.md

# 2. Verify no template variables remain
grep -q '{{' /tmp/test-toolchain.md && echo "FAIL: Variables remain" || echo "PASS"

# 3. Extract and run setup script
extract_toolchain_script.py /tmp/test-toolchain.md > /tmp/setup.sh
bash /tmp/setup.sh
```

---

## Future Enhancements

### Planned Features

1. **Auto-Update Language Mappings**
   - Fetch latest tool versions from package registries
   - Update mapping files automatically

2. **Toolchain Profiles**
   - Minimal (format + lint only)
   - Standard (+ type check + tests)
   - Full (+ benchmarks + coverage)

3. **IDE Integration**
   - Generate VSCode `settings.json` from toolchain
   - Generate `.editorconfig` from toolchain

4. **Toolchain Telemetry**
   - Track setup time per language
   - Track verification failure rates
   - Optimize slow toolchains

---

## Quick Reference

### Common Commands

```bash
# Compile Rust toolchain for Linux + macOS
compile_toolchain.py --language rust --version 1.75 --platforms linux,macos \
  --project xls-cross-platform --task-id GH-42 --output TOOLCHAIN.md

# Compile Python toolchain for all platforms
compile_toolchain.py --language python --version 3.12 --platforms all \
  --project my-app --task-id GH-99 --output TOOLCHAIN.md

# Verify compiled toolchain
validate_toolchain.py --toolchain TOOLCHAIN.md

# Extract setup script
extract_toolchain_script.py TOOLCHAIN.md > setup.sh

# Run setup
bash setup.sh
```

### File Locations

| File | Path |
|------|------|
| Base template | `skills/remote-agent-coordinator/templates/toolchain/BASE_TOOLCHAIN.md` |
| Language mappings | `skills/remote-agent-coordinator/templates/toolchain/languages/{LANGUAGE}.json` |
| Compiled toolchains | Agent workspace (ephemeral) |
| Toolchain cache | `/tmp/eoa-toolchain-cache/` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial release |

---

**Previous**: [Part 2 - Language Detection & Platform](./TOOLCHAIN_INTEGRATION-part2-language-platform.md)

---

**REMEMBER**: Toolchains are the bridge between EOA orchestrator's language-agnostic workflow and remote agents' language-specific execution. A well-compiled toolchain eliminates ambiguity and ensures consistent development environments across all agents.
