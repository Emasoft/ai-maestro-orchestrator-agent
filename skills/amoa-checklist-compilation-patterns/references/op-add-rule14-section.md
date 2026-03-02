---
procedure: support-skill
workflow-instruction: support
---

# Operation: Add RULE 14 Compliance Section


## Contents

- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [What is RULE 14?](#what-is-rule-14)
- [Procedure](#procedure)
  - [Step 1: Verify USER_REQUIREMENTS.md Exists](#step-1-verify-user_requirementsmd-exists)
  - [Step 2: Check Requirements Currency](#step-2-check-requirements-currency)
  - [Step 3: Create RULE 14 Section](#step-3-create-rule-14-section)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 4: Customize for Checklist Type](#step-4-customize-for-checklist-type)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
  - [Step 5: Verify Each Item](#step-5-verify-each-item)
  - [Step 6: Document Exceptions](#step-6-document-exceptions)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example: Adding to Existing Checklist](#example-adding-to-existing-checklist)
- [Implementation](#implementation)
- [Testing](#testing)
- [Implementation](#implementation)
- [Testing](#testing)
- [Requirement Compliance (RULE 14)](#requirement-compliance-rule-14)
- [Checklist](#checklist)

## When to Use

Use this operation when adding or verifying the RULE 14 compliance section in any checklist.

## Prerequisites

- USER_REQUIREMENTS.md exists in the project
- Understanding of what RULE 14 requires
- Existing checklist to augment

## What is RULE 14?

RULE 14 ensures that:
1. User requirements are documented and current
2. All requirements are addressed (no omissions)
3. No technology substitutions without explicit user approval
4. No scope reductions without explicit user approval

## Procedure

### Step 1: Verify USER_REQUIREMENTS.md Exists

```bash
# Check if file exists
ls USER_REQUIREMENTS.md 2>/dev/null || echo "Missing!"

# Or in project root
ls design/USER_REQUIREMENTS.md 2>/dev/null
```

### Step 2: Check Requirements Currency

USER_REQUIREMENTS.md should:
- Have a last-updated date
- Reflect current user needs
- Not be outdated by later communications

### Step 3: Create RULE 14 Section

```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All user requirements addressed
- [ ] No technology substitutions without approval
- [ ] No scope reductions without approval
```

### Step 4: Customize for Checklist Type

**For Module Completion:**
```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] Module requirements from section X addressed
- [ ] Using specified technologies only
- [ ] Full module scope as specified (no cuts)
```

**For Quality Gate:**
```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] Quality standards from requirements met
- [ ] No quality shortcuts taken
- [ ] All specified validations performed
```

**For Release:**
```markdown
## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] All planned features from requirements complete
- [ ] No features deferred without approval
- [ ] No technology changes from plan
```

### Step 5: Verify Each Item

For each item in the RULE 14 section:

1. **USER_REQUIREMENTS.md exists**: Physically verify the file
2. **Requirements addressed**: Cross-reference checklist items to requirements
3. **No tech substitutions**: Verify using specified libraries/tools
4. **No scope reductions**: Compare deliverables to original scope

### Step 6: Document Exceptions

If any RULE 14 item cannot be satisfied:

```markdown
## Requirement Compliance (RULE 14)
- [x] USER_REQUIREMENTS.md exists and is current
- [x] All user requirements addressed
- [ ] No technology substitutions without approval
  - **Exception**: Replaced `old-lib` with `new-lib` - awaiting approval (issue #45)
- [x] No scope reductions without approval
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| RULE 14 Section | Markdown | Compliance section to add to checklist |
| Compliance Status | Boolean | Whether all items are satisfied |
| Exceptions | Array | Any items requiring approval |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| USER_REQUIREMENTS.md missing | Never created | Create from user communications |
| Requirements outdated | New user input not captured | Update requirements document |
| Tech substitution needed | Original tech doesn't work | Document reason, request approval |
| Scope reduction needed | Constraints discovered | Document reason, request approval |

## Example: Adding to Existing Checklist

**Before:**
```markdown
# Module: api-auth Completion Checklist

## Implementation
- [ ] Login endpoint implemented
- [ ] Token validation implemented

## Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
```

**After:**
```markdown
# Module: api-auth Completion Checklist

## Implementation
- [ ] Login endpoint implemented
- [ ] Token validation implemented

## Testing
- [ ] Unit tests passing
- [ ] Integration tests passing

## Requirement Compliance (RULE 14)
- [ ] USER_REQUIREMENTS.md exists and is current
- [ ] Authentication requirements (Section 3) addressed
- [ ] Using specified jose library (no substitution)
- [ ] Full auth scope as specified (no cuts)
```

## Checklist

- [ ] Verify USER_REQUIREMENTS.md exists
- [ ] Check requirements are current
- [ ] Create RULE 14 section with 4 standard items
- [ ] Customize items for checklist type
- [ ] Cross-reference requirements to checklist items
- [ ] Document any exceptions requiring approval
- [ ] Add section to checklist
