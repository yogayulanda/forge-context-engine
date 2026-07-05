---
id: meta.context-manifest
title: Context Manifest
type: meta
status: unknown
confidence: high
source: human
owner: unresolved
updated: 2026-06-09
---

# Context Manifest

Index and routing map for the entire context system. Not a knowledge source.

Fresh CLI init now seeds v2 numbered service/workspace context profiles by default. Older pre-v2 layouts may still appear in existing repositories. `forge update` does not migrate them automatically; `forge migrate-context --dry-run` previews direct migration, and `forge migrate-context` writes numbered v2 files into `.forge/context/`, archives legacy-v1 paths under `.forge/context-archive/legacy-v1/`, and updates the manifest to context profile version 2.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | File registry & loading rules |
| AI writable | Yes — propose additions/removals, owner confirms |
| Human confirmation | Required for tier/zone changes |
| Populated | During Context Initialization |

## Bootstrap Order

1. `forge.config.yaml`
2. `.forge/adapter.md`
3. requested core mode or relevant compatibility/scenario guidance
4. `.forge/runtime/meta/conventions.md` when task behavior, output shape, evidence handling, validation, or risk rules need it
5. `.forge/runtime/meta/context-manifest.md` only as a routing index when navigation help is needed

## Daily Default Load

- `forge.config.yaml`
- `.forge/adapter.md`
- requested mode file only

## On-Demand Core

- `.forge/runtime/meta/conventions.md`
- `.forge/runtime/meta/glossary.md` *(if needed)*
- relevant active `.forge/context/*.md` files for the current service/workspace profile
- `.forge/runtime/meta/context-manifest.md` only when routing help is needed
- `.forge/runtime/meta/ai-readiness-factors.md` only during `ai-readiness` audits (factor catalog and band→verdict map)
- active `.forge/context/*.md` plus `00-index.md` during `update-context` and `verify-context` work, scoped to the area under review

## Scoped Convention Files (On Demand)

Load based on task type. Do not load all for every task.

| File | Load when |
|---|---|
| `.forge/runtime/meta/conventions-evidence.md` | Evidence, drift, constraint extraction, table role classification |
| `.forge/runtime/meta/conventions-validation.md` | Validation statuses, prerequisite checks, testing/review conventions |
| `.forge/runtime/meta/conventions-risk.md` | Governance, risk levels, secret safety, approval-sensitive decisions |
| `.forge/runtime/meta/conventions-language.md` | Language consistency, naming, reference stability, engineering style |

## Selective (Per Mode)

| Zone | Loaded by |
|---|---|
| related active `.forge/context/*.md` files | Mode + task intent on that area |
| `.forge/context/14-decisions-assumptions-and-constraints.md`, `.forge/context/99-open-questions.md` | `plan`; on-demand in `ask`/`implementation`/`execute`/`review`/`ai-readiness`/`verify-context` |
| active `.forge/context/*.md` entries with `status: inferred` or open questions | `ask`, `implementation`, `execute`; on-demand in `plan`/`review`/`ai-readiness`/`verify-context` |
| `.forge/generated/*` | On-demand |
| `.forge/context-patches/*` | Explicit reference, context impact, `ai-readiness`, or `verify-context` only |

## Never Auto-Loaded

- `temp/*` — ephemeral scratch, gitignored.
- Files with `status: deprecated`.
- All of `.forge/context` or all linked workspace repos by default.

## Validation Rules

- Every file has valid front-matter.
- Every file registered in this manifest.
- Every `id` unique.
- `confirmed`/`inferred` must have `evidence`.
- `source: human` files not written by AI.
- `modes/*` files never list `.forge/runtime/meta/*` or profile core files directly unless explicitly needed (delta only).
- Lifecycle artifacts are non-authoritative generated continuity helpers; artifact links never imply workflow, DAG, orchestration, agent memory, or execution-trigger semantics.
- `run.interaction` is the controlling interaction setting and automation-safe behavior never implies orchestration, agents, CI/CD, deploy, triggers, or executors.

## File Registry

> Runtime template placeholder. Target repositories populate this during Context Initialization. Format: `path | id | type | status | owner`

```
TBD
```
