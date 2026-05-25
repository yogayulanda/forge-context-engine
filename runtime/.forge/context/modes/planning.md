---
id: mode.planning
title: "Mode: Planning"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
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
- Output an ECP that reads like an engineering work plan, not an RFC.
- When persistence helps continuity, write or reference an ECP Artifact with approved intent, decisions, blockers, boundaries, linked systems/layers, and revision reference.
- Prefer sections such as: `Tujuan perubahan`, `Dampak teknis`, `Tahapan kerja`, `Risiko`, `Validasi`, `Rollback`, `Yang sengaja tidak diubah`.
- Keep paragraphs short and operational; highlight blockers and decisions before detail.
- Do not produce detailed executable coding tasks or modify code; approved phases hand off to implementation mode.
- Adapt sections to evidence: backend data/contracts, frontend UX/state/accessibility, infrastructure deployment/reliability/security.
- Ask unresolved architecture/governance decisions early; in non-interactive repos emit a concise blocked plan.
- Redact secret values and report secret discoveries only as masked security findings.
- Separate evidence, inference, and unknowns; do not invent topology, ownership, contracts, deployability, or runtime relationships from imports alone.
- Prefer direct evidence and scoped loading; use `CONTEXT_BUDGET_LIMITED` only when required evidence exceeds the normal scoped budget, naming missing evidence, affected planning decision, and targeted expansion needed.
- Check for drift between current code/repo evidence, decisions, assumptions, and generated artifacts; report `DRIFT_DETECTED`, `DRIFT_RISK`, or `NO_DRIFT_FOUND` calmly when it affects the plan.
- For cross-repo references, identify external/shared repo uncertainty and compare contracts only with available evidence; do not plan orchestration or automatic multi-repo changes.
- Surface fintech governance risks only when relevant: PII/secrets, financial correctness, idempotency, retry/replay, rollback, transaction consistency, auditability, observability, and blast radius. HIGH-risk governance decisions require human approval.
- If useful, say `Scoped context loaded`; do not expose full loading internals in normal output.
