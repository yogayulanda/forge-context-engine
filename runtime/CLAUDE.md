# CLAUDE — Context Adapter

Thin adapter for AI assistants. This file stores **no context** — it points to `.forge/`.

## Bootstrap Sequence

1. Read `.forge/forge.config.yaml` — tier, active layers, systems, default mode, `runtime.non_interactive`.
2. Read `.forge/context/00-meta/context-manifest.md` — index & loading rules.
3. Obey `.forge/context/00-meta/conventions.md` — AI operational contract (normative).
4. Always load: `00-meta/*` + `01-core/*`.
5. Select mode from `.forge/context/modes/<mode>.md` — resolve delta: `include` / `on_demand` / `exclude`.
6. Respect mode `token_budget` and per-file size budget.

## AI Operational Rules (Summary)

- Never guess. `unknown` is a mandatory destination, not a guess.
- `runtime.non_interactive: false` is the default: ask concise clarification questions for blocking decisions, then continue after human confirmation.
- `runtime.non_interactive: true`: never ask interactive questions; emit `BLOCKED`, `NEEDS_REVIEW`, or `NEEDS_CONFIRMATION` and continue only with allowed proposed defaults.
- Classify unknowns as `blocking`, `proposed-default`, or `informational`.
- Never print, copy, summarize, or store raw secrets. Redact sensitive values before any output or Forge context write.
- Never write to `source: human` files. Inferences go to `knowledge/inferred.md` or `generated/`.
- Never self-promote `status`. Propose only; promotion to `confirmed` requires entry in `knowledge/confirmations.md`.
- Without `evidence`, max status is `assumption`.
- When task conflicts with `01-core/constraints.md`, stop and flag.
- Never fabricate architecture, APIs, services, databases, integrations, ownership, or business rules.
- Treat legacy AI artifacts (`.ai/`, `.claude/`, `AGENTS.md`, etc.) as **reference**, not source-of-truth. Repo code wins on conflict.
- Tag every `unknowns.md` entry with classification: `blocking` / `proposed-default` / `informational`.
- Use `owner: unresolved` (not `TBD`) when owner is undetermined; create one root unknown `U-OWN`.
- **Evidence consistency:** cross-check critical claims (tables, migrations, entities, APIs, workers, integrations, validation rules) against repo before finalizing. If repo has N, context says N.
- **Drift:** code change at evidence path demotes `confirmed` → `inferred`; refresh and log ambiguity in `unknowns.md`.
- **No phantom ADRs:** never cite `ADR-NNNN` unless the file exists. Planned ADRs → `assumptions.md`/`unknowns.md`.
- **Implicit constraints:** during init, scan code for enums, validators, required fields, ID semantics, status fields, retry/idempotency. Place global → `constraints.md`, system-specific → `systems/<name>/system.md`.
- **Validation semantics:** preserve enforcement layer (service / handler / DB / repository fallback / business intent). Never flatten everything into "required fields".
- **Internal table hygiene:** table cells follow same conventions as front-matter (no `TBD`).
- **Language consistency:** one dominant natural language per repo (chosen at init). Never translate identifiers (table names, enum values, RPC names, etc.). No mixed-language sentences in narrative content.
- **Reference stability:** prefer `id`/file references over translated heading text. Citing `core.product` is stable; citing `"Data Sources" section` is fragile.

## Secret Safety Entry

- Report discovered secrets only as type, file path, line/reference when available, and safe masked preview such as `<REDACTED_SECRET>` or `****a91f`.
- Do not copy secrets into `.forge/context`, reports, plans, reviews, tests, migrations, validation-cases, decisions, confirmations, unknowns, inferred knowledge, or platform context.
- Classify discovered secrets as security findings and recommend rotation if they may have been committed or exposed.

## Mode Invocation Entry

- When a Forge mode is requested, read `.forge/forge.config.yaml` first and detect `runtime.non_interactive`.
- Apply interactive or non-interactive behavior from config before mode execution.
- Then read `.forge/context/modes/<mode>.md`.
- Visible modes: `planning`, `implement` (`implementation.md`), `execute`, `testing`, `review`.
- Follow that mode's `include`, `on_demand`, `exclude`, `token_budget`, and `notes`.
- Load scoped context only; do not broad-load `.forge/context` by default.
- Keep planning, task decomposition, code execution, testing, and review separate.
- Apply `runtime.non_interactive` consistently across all modes; changing it never rewrites repository cognition.

## Notes

`AGENTS.md` optional if second AI assistant exists. This adapter never replaces `00-meta/conventions.md` as normative contract source.
