---
id: systems.readme
title: "Systems Zone"
type: meta
status: unknown
confidence: high
source: human
owner: TBD
updated: 2026-05-20
---

# Systems

Vertical context per real implementation unit — service, app, worker, library, infra-module, platform-component.

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Placeholder for `systems/` zone |
| AI writable | No — AI proposes new units via `knowledge/inferred.md` |
| Human confirmation | Required before creating unit folders |
| Populated | During Context Initialization |

## How to Add a Unit

1. Identify unit type: `service` · `app` · `worker` · `library` · `infra-module` · `platform-component`
2. Add entry to `forge.config.yaml` → `systems[]`
3. Create `systems/<name>/system.md` with `type: system` & `system_type` in front-matter
4. Brownfield → `status: inferred` + evidence; Greenfield → `assumption` + ADR
5. Register in `00-meta/context-manifest.md`

## Repo Models

- **Single-service** — `systems/` contains exactly one folder.
- **Monorepo** — multiple sibling folders; `01-core/` & `layers/` shared once across all units.

## Anti-Duplication Rule

`systems/<unit>/` contains **only** facts true exclusively for that unit.
- Global context → `01-core/`
- Cross-unit discipline standards → `layers/`
- Inter-unit dependencies declared via `id` reference, never copied.
