# Design Document Protocol


## Contents

- [1. Document UUID Format (GUUID)](#1-document-uuid-format-guuid)
- [2. Required Frontmatter Schema](#2-required-frontmatter-schema)
- [3. Document Lifecycle](#3-document-lifecycle)
- [4. Validation Procedures](#4-validation-procedures)
  - [4.1 Pre-Save Validation (REQUIRED)](#41-pre-save-validation-required)
  - [4.2 Post-Save Validation (REQUIRED)](#42-post-save-validation-required)
  - [4.3 Validation Script Usage](#43-validation-script-usage)
- [5. Search Procedures](#5-search-procedures)
  - [5.1 Search by UUID](#51-search-by-uuid)
  - [5.2 Search by Type](#52-search-by-type)
  - [5.3 Search by Status](#53-search-by-status)
  - [5.4 Search by Keyword](#54-search-by-keyword)
  - [5.5 Combined Search](#55-combined-search)
- [6. GitHub Integration](#6-github-integration)
  - [6.1 Creating GitHub Issue from Design Document](#61-creating-github-issue-from-design-document)
  - [6.2 Syncing Status](#62-syncing-status)
  - [6.3 Linking Existing Issue](#63-linking-existing-issue)
- [7. Edge Cases and Error Handling](#7-edge-cases-and-error-handling)
  - [7.1 Duplicate UUID](#71-duplicate-uuid)
  - [7.2 Malformed Frontmatter](#72-malformed-frontmatter)
  - [7.3 Missing Required Fields](#73-missing-required-fields)
  - [7.4 Invalid Status Transition](#74-invalid-status-transition)
  - [7.5 GitHub CLI Not Available](#75-github-cli-not-available)
  - [7.6 Empty Search Results](#76-empty-search-results)
  - [7.7 Design Folder Not Initialized](#77-design-folder-not-initialized)
- [8. File Naming Convention](#8-file-naming-convention)
- [9. Cross-Plugin Protocol](#9-cross-plugin-protocol)
- [10. Quick Reference](#10-quick-reference)
  - [Create Document](#create-document)
  - [Search Documents](#search-documents)
  - [Validate Document](#validate-document)

---

This protocol defines standards for creating, validating, and searching design documents in the `design/` folder structure.

## 1. Document UUID Format (GUUID)

All design documents MUST have a globally unique identifier (GUUID) in this format:

```
{TYPE}-{YYYYMMDD}-{NNNN}
```

**Components:**
- `{TYPE}` - Document type prefix (3-6 uppercase letters)
- `{YYYYMMDD}` - Creation date in ISO format
- `{NNNN}` - Sequential number (0001-9999)

**Valid Type Prefixes:**

| Prefix | Document Type | Folder Location |
|--------|---------------|-----------------|
| `REQ` | Requirement | `design/requirements/` |
| `SPEC` | Specification | `design/requirements/` |
| `ARCH` | Architecture | `design/requirements/` |
| `PDR` | Project Design Record | `design/requirements/` |
| `HAND` | Handoff Document | `design/handoffs/` |
| `MEM` | Memory/Context | `design/memory/` |
| `DEC` | Decision Record | `design/requirements/` |

**Examples:**
```
REQ-20260129-0001
SPEC-20260129-0042
HAND-20260130-0001
```

## 2. Required Frontmatter Schema

All design documents MUST include YAML frontmatter with these required fields:

```yaml
---
uuid: REQ-20260129-0001
title: "Authentication System Requirements"
type: requirement
status: DRAFT
created: 2026-01-29T10:00:00Z
updated: 2026-01-29T10:00:00Z
author: orchestrator-agent
---
```

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | string | GUUID in format `{TYPE}-{YYYYMMDD}-{NNNN}` |
| `title` | string | Human-readable title |
| `type` | enum | requirement, specification, architecture, handoff, memory, decision |
| `status` | enum | DRAFT, REVIEW, APPROVED, IMPLEMENTING, COMPLETED, ARCHIVED |
| `created` | ISO8601 | Creation timestamp |
| `updated` | ISO8601 | Last update timestamp |
| `author` | string | Creating agent identifier |

**Optional Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `github_issue` | number | Linked GitHub issue number |
| `github_pr` | number | Linked pull request number |
| `parent_uuid` | string | Parent document GUUID |
| `depends_on` | list | List of dependency GUUIDs |
| `version` | string | Semantic version (default: 1.0.0) |
| `tags` | list | Categorization tags |
| `assignee` | string | Assigned agent identifier |

## 3. Document Lifecycle

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌──────────────┐
│  DRAFT  │────▶│ REVIEW  │────▶│ APPROVED │────▶│ IMPLEMENTING │
└─────────┘     └─────────┘     └──────────┘     └──────────────┘
                    │                                    │
                    │                                    ▼
                    │                            ┌───────────┐
                    └───────────────────────────▶│ COMPLETED │
                                                 └───────────┘
                                                       │
                                                       ▼
                                                 ┌──────────┐
                                                 │ ARCHIVED │
                                                 └──────────┘
```

**Transition Rules:**
- DRAFT → REVIEW: Document is complete enough for review
- REVIEW → APPROVED: Stakeholder approval received
- REVIEW → DRAFT: Revisions needed
- APPROVED → IMPLEMENTING: Work has begun
- IMPLEMENTING → COMPLETED: All work finished
- COMPLETED → ARCHIVED: Document is historical reference

## 4. Validation Procedures

### 4.1 Pre-Save Validation (REQUIRED)

Before saving ANY design document:

1. **Check UUID uniqueness** - Search existing documents to ensure no duplicate
2. **Validate frontmatter** - All required fields present and valid
3. **Validate status** - Status is a valid enum value
4. **Validate dates** - `updated` >= `created`
5. **Validate references** - Any referenced UUIDs exist

### 4.2 Post-Save Validation (REQUIRED)

After saving ANY design document:

1. **Re-read file** - Ensure file was written correctly
2. **Parse frontmatter** - Ensure YAML is valid
3. **Verify UUID** - UUID in frontmatter matches filename convention
4. **Index update** - Add/update entry in design index

### 4.3 Validation Script Usage

```bash
# Validate a single document
uv run python scripts/eoa_design_validate.py design/requirements/REQ-20260129-0001.md

# Validate all documents in a folder
uv run python scripts/eoa_design_validate.py design/requirements/

# Validate entire design folder
uv run python scripts/eoa_design_validate.py design/
```

## 5. Search Procedures

### 5.1 Search by UUID

```bash
uv run python scripts/eoa_design_search.py --uuid REQ-20260129-0001
```

### 5.2 Search by Type

```bash
uv run python scripts/eoa_design_search.py --type requirement
uv run python scripts/eoa_design_search.py --type handoff
```

### 5.3 Search by Status

```bash
uv run python scripts/eoa_design_search.py --status APPROVED
uv run python scripts/eoa_design_search.py --status IMPLEMENTING
```

### 5.4 Search by Keyword

```bash
uv run python scripts/eoa_design_search.py --keyword "authentication"
```

### 5.5 Combined Search

```bash
uv run python scripts/eoa_design_search.py --type requirement --status DRAFT --keyword "API"
```

## 6. GitHub Integration

### 6.1 Creating GitHub Issue from Design Document

When creating a GitHub issue from a design document:

1. Use document title as issue title
2. Use document content (without frontmatter) as issue body
3. Add label based on document type: `design:{type}`
4. Add label based on status: `status:{status}`
5. Update document frontmatter with `github_issue` field

### 6.2 Syncing Status

When document status changes:
1. Update `status` field in frontmatter
2. Update `updated` timestamp
3. If linked to GitHub issue, update issue labels
4. If status is COMPLETED, close GitHub issue

### 6.3 Linking Existing Issue

To link a document to an existing issue:
1. Add `github_issue: {number}` to frontmatter
2. Post document UUID as issue comment
3. Add `design-linked` label to issue

## 7. Edge Cases and Error Handling

### 7.1 Duplicate UUID

**Detection:** Search returns existing document with same UUID
**Resolution:**
1. Generate new UUID with incremented sequence number
2. Log warning about collision
3. Retry save with new UUID

### 7.2 Malformed Frontmatter

**Detection:** YAML parsing fails
**Resolution:**
1. Do NOT save document
2. Return validation error with line numbers
3. Agent must fix frontmatter before retry

### 7.3 Missing Required Fields

**Detection:** Validation finds missing fields
**Resolution:**
1. Do NOT save document
2. Return list of missing fields
3. Agent must add fields before retry

### 7.4 Invalid Status Transition

**Detection:** Requested status change violates lifecycle
**Resolution:**
1. Do NOT update status
2. Return error explaining valid transitions
3. Agent must use valid transition

### 7.5 GitHub CLI Not Available

**Detection:** `gh` command not found or not authenticated
**Resolution:**
1. Skip GitHub operations
2. Log warning
3. Document remains valid without GitHub link
4. Retry GitHub operations later

### 7.6 Empty Search Results

**Detection:** Search returns no matches
**Resolution:**
1. Return empty result set (not error)
2. Include search criteria in response
3. Suggest alternative searches if possible

### 7.7 Design Folder Not Initialized

**Detection:** `design/` folder or subfolders don't exist
**Resolution:**
1. Run `eoa_init_design_folders.py` to create structure
2. Retry operation

## 8. File Naming Convention

Design documents SHOULD follow this naming pattern:

```
{uuid}.md
```

Or with descriptive slug:

```
{uuid}-{slug}.md
```

**Examples:**
```
REQ-20260129-0001.md
REQ-20260129-0001-authentication-requirements.md
HAND-20260130-0001-auth-module-handoff.md
```

## 9. Cross-Plugin Protocol

When handing off documents between plugins:

1. **Sender** creates handoff document in `design/handoffs/`
2. **Sender** includes all referenced document UUIDs
3. **Sender** sends AI Maestro message using the `agent-messaging` skill with handoff UUID
4. **Receiver** searches for handoff by UUID
5. **Receiver** validates handoff document
6. **Receiver** reads all referenced documents
7. **Receiver** updates handoff status to IMPLEMENTING
8. **Receiver** proceeds with work

## 10. Quick Reference

### Create Document

```python
from eoa_design_create import create_design_document

doc = create_design_document(
    doc_type="requirement",
    title="Authentication System",
    content="## Overview\n\nThis document defines..."
)
print(f"Created: {doc['uuid']}")
```

### Search Documents

```python
from eoa_design_search import search_documents

results = search_documents(
    doc_type="requirement",
    status="APPROVED"
)
for doc in results:
    print(f"{doc['uuid']}: {doc['title']}")
```

### Validate Document

```python
from eoa_design_validate import validate_document

errors = validate_document("design/requirements/REQ-20260129-0001.md")
if errors:
    for error in errors:
        print(f"Line {error['line']}: {error['message']}")
```
