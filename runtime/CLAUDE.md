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
- Treat legacy AI artifacts (`.ai/`, `.claude/`, `AGENTS.md`, etc.) as **reference**, not source-of-truth. Repo code wins on conflict.
- Tag every `unknowns.md` entry with priority: `blocking` · `important` · `informational`.
- Use `owner: unresolved` (not `TBD`) when owner is undetermined; create one root unknown `U-OWN`.
- **Evidence consistency:** cross-check critical claims (tables, migrations, entities, APIs, workers, integrations, validation rules) against repo before finalizing. If repo has N, context says N.
- **Drift:** code change at evidence path demotes `confirmed` → `inferred`; refresh and log ambiguity in `unknowns.md`.
- **No phantom ADRs:** never cite `ADR-NNNN` unless the file exists. Planned ADRs → `assumptions.md`/`unknowns.md`.
- **Implicit constraints:** during init, scan code for enums, validators, required fields, ID semantics, status fields, retry/idempotency. Place global → `constraints.md`, system-specific → `systems/<name>/system.md`.
- **Validation semantics:** preserve enforcement layer (service / handler / DB / repository fallback / business intent). Never flatten everything into "required fields".
- **Internal table hygiene:** table cells follow same conventions as front-matter (no `TBD`).
- **Language consistency:** one dominant natural language per repo (chosen at init). Never translate identifiers (table names, enum values, RPC names, etc.). No mixed-language sentences in narrative content.
- **Reference stability:** prefer `id`/file references over translated heading text. Citing `core.product` is stable; citing `"Data Sources" section` is fragile.

## Notes

`AGENTS.md` optional if second AI assistant exists. This adapter never replaces `00-meta/conventions.md` as normative contract source.
