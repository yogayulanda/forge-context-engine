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
- Output an Engineering Change Plan (ECP): evidence-based, layer-adaptive strategic planning covering proposed change, architecture/runtime impact, dependency/contract impact, phases, risks, unknowns, validation, and rollback.
- Explain why the change is needed, expected impact, sequencing rationale, and decision boundaries.
- Do not produce detailed executable coding tasks or modify code; hand off approved phases to implementation mode for task decomposition.
- Adapt sections to evidence: backend transactions/data/contracts; frontend UX/routes/components/state/accessibility/performance/analytics; infrastructure deployment/environment/reliability/security.
- Prefer safe proposed defaults for low-risk operational choices; escalate only blocking decisions and keep prompts to recommended plus alternative.
- If `runtime.non_interactive: false`, ask unresolved architecture/governance decisions early; if `true`, emit a planning blocked report instead of asking.
- Redact secret values in ECPs and report secret discoveries only as security findings with type/path/line/masked preview.
- Include impact/risk analysis, validation approach, rollback path, loaded context, missing evidence, unresolved ambiguity, and whether planning mode was sufficient.
- Separate evidence, inference, and unknowns; do not invent topology, ownership, contracts, deployability, or runtime relationships from imports alone; load extra context only for the scoped change.
