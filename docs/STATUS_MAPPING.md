# AMOA ↔ AI Maestro Status Mapping

> **Version**: 1.5.3 | **Last Updated**: 2026-03-08

## Overview

AMOA uses an 8-column GitHub Projects kanban. AI Maestro uses a 5-status task system. This document defines the bidirectional mapping between them.

## Status Mapping Table

| AMOA Column | GitHub Label | AI Maestro Status | Direction | Notes |
|-------------|-------------|-------------------|-----------|-------|
| Backlog | `status:backlog` | `backlog` | bidirectional | 1:1 match |
| Todo | `status:todo` | `pending` | bidirectional | 1:1 match |
| In Progress | `status:in-progress` | `in_progress` | bidirectional | 1:1 match |
| AI Review | `status:ai-review` | `review` | AMOA → Maestro | collapses with Human Review |
| Human Review | `status:human-review` | `review` | AMOA → Maestro | collapses with AI Review |
| Merge/Release | `status:merge-release` | `completed` | AMOA → Maestro | collapses with Done |
| Done | `status:done` | `completed` | AMOA → Maestro | collapses with Merge/Release |
| Blocked | `status:blocked` | `in_progress` | AMOA → Maestro | uses `blockedBy` metadata |

## Reverse Mapping (AI Maestro → AMOA)

When syncing from AI Maestro back to GitHub Projects:

| AI Maestro Status | Default AMOA Column | Disambiguation |
|-------------------|---------------------|----------------|
| `backlog` | Backlog | direct |
| `pending` | Todo | direct |
| `in_progress` | In Progress | check `blockedBy` → Blocked if present |
| `review` | AI Review | default; use Human Review if `reviewType: human` metadata present |
| `completed` | Done | default; use Merge/Release if `merged: false` metadata present |

## Lossy Mappings

The AMOA → Maestro direction is lossy for 3 pairs:

1. **AI Review / Human Review** → both map to `review`
2. **Merge/Release / Done** → both map to `completed`
3. **Blocked** → maps to `in_progress` (with metadata)

Phase 3 (AI Maestro configurable columns) will eliminate this loss by supporting custom status codes.
