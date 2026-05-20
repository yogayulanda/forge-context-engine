---
id: layer.backend
title: "Layer: Backend"
type: layer
status: unknown
confidence: high
source: human
owner: TBD
updated: 2026-05-20
---

# Layer: Backend

Horizontal context for backend engineering discipline — patterns, conventions, standards spanning all backend systems.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Placeholder — no layer content yet |
| AI writable | No — AI proposes via `knowledge/` during init |
| Human confirmation | Required before creating `backend.md` |
| Populated | During Context Initialization for repos with backend ownership. Delete this folder if no backend. |

## Growth Path

1. Init creates `backend.md` (sibling of this README).
2. Brownfield → `status: inferred` + code evidence.
3. Greenfield → `status: assumption` + ADR.
4. Exceeds size budget (≤ ~150 lines) → split into sub-files in this folder.

## Boundaries

- No content files before Context Initialization.
- No copying from `01-core/`.
- No unit-specific facts (→ `systems/<unit>/`).
