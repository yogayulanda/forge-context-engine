# CLAUDE — Context Adapter

Thin adapter for AI assistants. This file stores **no context** — it points to `.forge/`.

## Bootstrap Sequence

1. Read `.forge/forge.config.yaml` — tier, active layers, systems, default mode.
2. Read `.forge/context/00-meta/context-manifest.md` — index & loading rules.
3. Obey `.forge/context/00-meta/conventions.md` — AI operational contract (normative).
4. Always load: `00-meta/*` + `01-core/*`.
5. Select mode from `.forge/context/modes/<mode>.md` — resolve delta: `include` / `on_demand` / `exclude`.
6. Respect mode `token_budget` and per-file size budget.

## AI Operational Rules (Summary)

- Never guess. `unknown` is a mandatory destination, not a guess.
- Never write to `source: human` files. Inferences go to `knowledge/inferred.md` or `generated/`.
- Never self-promote `status`. Propose only; promotion to `confirmed` requires entry in `knowledge/confirmations.md`.
- Without `evidence`, max status is `assumption`.
- When task conflicts with `01-core/constraints.md`, stop and flag.
- Never fabricate architecture, APIs, services, databases, integrations, ownership, or business rules.

## Notes

`AGENTS.md` optional if second AI assistant exists. This adapter never replaces `00-meta/conventions.md` as normative contract source.
