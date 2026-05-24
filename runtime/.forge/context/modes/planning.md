---
id: mode.planning
title: "Mode: Planning"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-24
---

# Mode: Planning

## include

- `knowledge/decisions/`
- `knowledge/assumptions.md`, `knowledge/unknowns.md`
- `layers/<related>`

## on_demand

- `systems/<related>`, `knowledge/inferred.md`
- Contracts/events/data: API, proto, route, topic, producer/consumer, migration, constraint, table-role context
- UI/ops/runtime: route, page, component, state, API-consumption, accessibility, deployment, environment, logging/metrics/tracing context

## exclude

- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget

4000

## notes

- Output an Engineering Change Plan (ECP): evidence-based, layer-adaptive engineering planning covering proposed change, architecture/runtime impact, dependency/contract impact, implementation strategy, risks, unknowns, validation, and rollback.
- ECP is not brainstorming, PRD/business prose, implementation code, or architecture rewrite by default.
- Adapt sections to evidence: backend transactions/data/contracts; frontend UX/routes/components/state/accessibility/performance/analytics; infrastructure deployment/environment/reliability/security.
- Separate evidence, inference, and unknowns; do not invent topology, ownership, contracts, deployability, or runtime relationships from imports alone; load extra context only for the scoped change.
