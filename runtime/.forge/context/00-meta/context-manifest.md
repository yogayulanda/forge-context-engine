---
id: meta.context-manifest
title: Context Manifest
type: meta
status: unknown
confidence: high
source: human
owner: unresolved
updated: 2026-05-20
---

# Context Manifest

Index and routing map for the entire context system. Not a knowledge source.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | File registry & loading rules |
| AI writable | Yes — propose additions/removals, owner confirms |
| Human confirmation | Required for tier/zone changes |
| Populated | During Context Initialization |

## Bootstrap Order

1. `forge.config.yaml`
2. `00-meta/context-manifest.md` ← this file
3. `00-meta/conventions.md`
4. `00-meta/glossary.md` *(if exists)*
5. `01-core/*`
6. `modes/<default_mode>.md` → resolve delta

## Always Loaded

- `forge.config.yaml`
- `00-meta/context-manifest.md`
- `00-meta/conventions.md`
- `00-meta/glossary.md` *(if exists)*
- `01-core/product.md`
- `01-core/architecture.md`
- `01-core/principles.md` *(optional in Minimal tier)*
- `01-core/constraints.md` *(optional in Minimal tier)*

## Selective (Per Mode)

| Zone | Loaded by |
|---|---|
| `layers/<layer>` | Mode referencing that layer |
| `systems/<unit>` | Mode + task intent on that unit |
| `knowledge/decisions/` | `implementation`, `review` |
| `knowledge/assumptions.md`, `unknowns.md` | `planning`, `testing` |
| `knowledge/inferred.md` | `implementation` |
| `generated/*` | On-demand |

## Never Auto-Loaded

- `temp/*` — ephemeral scratch, gitignored.
- Files with `status: deprecated`.

## Validation Rules

- Every file has valid front-matter.
- Every file registered in this manifest.
- Every `id` unique.
- `confirmed`/`inferred` must have `evidence`.
- `source: human` files not written by AI.
- `modes/*` files never list `00-meta/*` or `01-core/*` (delta only).

## File Registry

> Populated during init. Format: `path | id | type | status | owner`

```
TBD
```
