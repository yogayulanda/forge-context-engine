---
id: meta.context-manifest
title: Context Manifest
type: meta
status: unknown
confidence: high
source: human
owner: unresolved
updated: 2026-05-25
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
6. `modes/<workflow.default_mode>.md` resolves the mode delta

## Always Loaded

- `forge.config.yaml`
- `00-meta/context-manifest.md`
- `00-meta/conventions.md`
- `00-meta/glossary.md` *(if exists)*
- `01-core/product.md`
- `01-core/architecture.md`
- `01-core/principles.md` *(optional in Minimal tier)*
- `01-core/constraints.md` *(optional in Minimal tier)*

## Scoped Convention Files (On Demand)

Load based on task type. Do not load all for every task.

| File | Load when |
|---|---|
| `00-meta/conventions-evidence.md` | Evidence, drift, constraint extraction, table role classification |
| `00-meta/conventions-validation.md` | Validation statuses, prerequisite checks, testing/review conventions |
| `00-meta/conventions-risk.md` | Governance, risk levels, secret safety, approval-sensitive decisions |
| `00-meta/conventions-language.md` | Language consistency, naming, reference stability, engineering style |

## Selective (Per Mode)

| Zone | Loaded by |
|---|---|
| `layers/<layer>` | Mode referencing that layer |
| `systems/<unit>` | Mode + task intent on that unit |
| `knowledge/decisions/` | `plan`, `implementation`, `execute`, `review`; on-demand in `ask` |
| `knowledge/assumptions.md`, `unknowns.md` | `plan`; on-demand in `ask`/`implementation`/`execute`/`review`/`verify-context` |
| `knowledge/inferred.md` | `ask`, `implementation`, `execute`; on-demand in `plan`/`review`/`verify-context` |
| `.forge/generated/*` | On-demand |
| `.forge/context-patches/*` | Explicit reference, context impact, or `verify-context` only |

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
- Lifecycle artifacts are non-authoritative generated continuity helpers; artifact links never imply workflow, DAG, orchestration, agent memory, or execution-trigger semantics.
- `run.interaction` is the controlling interaction setting and automation-safe behavior never implies orchestration, agents, CI/CD, deploy, triggers, or executors.

## File Registry

> Runtime template placeholder. Target repositories populate this during Context Initialization. Format: `path | id | type | status | owner`

```
TBD
```
