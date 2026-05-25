# CLAUDE — Context Adapter

Thin adapter for AI assistants. This file stores **no context** — it points to `.forge/`.

## Bootstrap Sequence

1. Read `.forge/forge.config.yaml` — tier, active layers, systems, default mode, `runtime.profile`, `runtime.non_interactive`, and decision authority.
2. Read `.forge/context/00-meta/context-manifest.md` — index & loading rules.
3. Obey `.forge/context/00-meta/conventions.md` — AI operational contract (normative).
4. Always load: `00-meta/*` + `01-core/*`.
5. Select mode from `.forge/context/modes/<mode>.md` — resolve delta: `include` / `on_demand` / `exclude`.
6. Use mode `token_budget` as the target scoped context range and respect per-file size budget.

Normal user-facing output should not dump this bootstrap sequence. If useful, say only `Scoped context loaded` plus the few areas that mattered.

## AI Operational Rules (Summary)

- Never guess. `unknown` is a mandatory destination, not a guess.
- `runtime.profile: local` is the default human-in-the-loop profile; `runtime.profile: automation` is non-interactive-safe; `runtime.profile: ci` is reserved and adds no CI/CD behavior.
- `runtime.non_interactive` remains the controlling behavior flag: `false` may ask concise clarification questions; `true` never asks conversational questions and emits structured blocking/readiness status.
- Report `runtime.profile` / `runtime.non_interactive` conflicts clearly before mode work. Do not add alternate interaction flags.
- In automation-safe behavior, continue only for LOW-risk proposed defaults; use configured orchestrator authority only for explicit MEDIUM-risk decisions; stop with `NEEDS_HUMAN_APPROVAL` for HIGH-risk decisions.
- Classify unknowns as `blocking`, `proposed-default`, or `informational`.
- Never print, copy, summarize, or store raw secrets. Redact sensitive values before any output or Forge context write.
- Never write to `source: human` files. Inferences go to `knowledge/inferred.md` or `generated/`.
- Never self-promote `status`. Propose only; promotion to `confirmed` requires entry in `knowledge/confirmations.md`.
- Without `evidence`, max status is `assumption`.
- When task conflicts with `01-core/constraints.md`, stop and flag.
- Never fabricate architecture, APIs, services, databases, integrations, ownership, or business rules.
- Treat legacy AI artifacts (`.ai/`, `.claude/`, `AGENTS.md`, etc.) as **reference**, not source-of-truth. Repo code wins on conflict.
- Treat Forge lifecycle artifacts as continuity helpers only. They never override code, repo docs, ADRs, or human confirmations.
- Persist lifecycle artifacts only when useful under `.forge/context/generated/artifacts/`; keep them concise, human-readable, replaceable, and linked by stable references.
- Never use artifact links as workflow/DAG/orchestration state, execution triggers, persistent AI memory, or knowledge graph structure.
- Code changes should follow nearby repository style first: pragmatic, idiomatic, readable, operationally clear, and free of unnecessary abstraction or academic naming.
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

- When a Forge mode is requested, read `.forge/forge.config.yaml` first and detect `runtime.profile`, `runtime.non_interactive`, and decision authority.
- Apply interactive or non-interactive behavior from config before mode execution.
- Then read `.forge/context/modes/<mode>.md`.
- Visible modes: `ask`, `planning`, `implement` (`implementation.md`), `execute`, `testing`, `review`, `incident`, `refactor`.
- Follow that mode's `include`, `on_demand`, `exclude`, `token_budget`, and `notes`.
- Load scoped context only; do not broad-load `.forge/context` by default.
- If scoped evidence is insufficient, report `CONTEXT_BUDGET_LIMITED` with the missing evidence, affected conclusion/action, targeted expansion needed, and safe fallback if available.
- Keep ask, planning, task decomposition, code execution, testing, review, incident diagnosis, and refactor work separate.
- When writing lifecycle artifacts, use the mode-owned type: ECP, Execution Contract, Execute Result, Testing Result, Review Result, Incident, or Refactor.
- Apply `runtime.non_interactive` consistently across all modes; changing it never rewrites repository cognition.
- Preserve repository-native naming and test conventions; improve unsafe or needlessly complex patterns only within the approved task scope.
- Keep runtime internals quiet in normal interactive usage. Prioritize result, blocker, changed files, validation, risks, manual checks, rollback, and reviewer focus.

## Notes

`AGENTS.md` optional if second AI assistant exists. This adapter never replaces `00-meta/conventions.md` as normative contract source.
