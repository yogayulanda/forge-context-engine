---
id: layer.infrastructure
title: "Layer: Infrastructure"
type: layer
status: unknown
confidence: high
source: human
owner: TBD
updated: 2026-05-20
---

# Layer: Infrastructure

Horizontal context for infrastructure discipline — IaC patterns, deployment conventions, networking, environment standards spanning all systems.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Placeholder — no layer content yet |
| AI writable | No — AI proposes via `knowledge/` during init |
| Human confirmation | Required before creating `infrastructure.md` |
| Populated | During Context Initialization for repos with infra ownership. Delete this folder if infra managed elsewhere. |

## Growth Path

1. Init creates `infrastructure.md` (sibling of this README).
2. Brownfield → `status: inferred` + code evidence.
3. Greenfield → `status: assumption` + ADR.
4. Exceeds size budget (≤ ~150 lines) → split into sub-files.

## Boundaries

- No content files before Context Initialization.
- No copying from `01-core/`.
- No unit-specific facts (→ `systems/<unit>/`).
