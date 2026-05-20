---
id: meta.conventions
title: Conventions & AI Operational Contract
type: meta
status: confirmed
confidence: high
source: human
evidence:
  - { type: doc, ref: ../../../FORGE-CONTEXT-ARCHITECTURE.md }
owner: forge-context-engine
updated: 2026-05-20
---

# Context System Conventions

Rules for **managing the context system itself**. Not product engineering principles (→ `01-core/principles.md`).

## File Meta

| Attribute | Value |
|---|---|
| Source of truth | Normative. Always loaded. |
| AI writable | No |
| Human confirmation | Required for any change |
| Populated | Final in runtime; minor adaptation during target repo init |

## Naming & IDs

- Files: `kebab-case.md`
- ID format: `<zone>.<name>` (e.g. `system.payment-service`, `layer.backend`)
- ADR: `ADR-NNNN-title.md`, append-only

## Front-Matter Schema (Required on Every Context File)

```yaml
---
id: <zone>.<name>
title: <human-readable title>
type: meta|core|layer|system|knowledge|mode|generated
system_type: service|app|worker|library|infra-module|platform-component  # type=system only
status: confirmed|inferred|assumption|unknown|deprecated
confidence: high|medium|low
source: human|ai|hybrid
evidence:
  - { type: code|doc|adr|human|external, ref: <path|url> }
owner: <team-or-ref>
updated: YYYY-MM-DD
review_by: YYYY-MM-DD  # optional
---
```

## Status Vocabulary

| Status | Meaning | Authoritative |
|---|---|---|
| `confirmed` | Verified; safe as decision basis | Yes |
| `inferred` | AI-derived with evidence; non-authoritative | No |
| `assumption` | Temporary; not a final decision basis | No |
| `unknown` | Acknowledged gap; **guessing forbidden** | — |
| `deprecated` | No longer applies; not loaded | — |

## Always-Loaded Core

`00-meta/*` + `01-core/*`. Modes **never** re-list core — delta only.

## AI Operational Contract (Normative)

1. AI does not self-promote status — **propose only**.
2. AI does not present `inferred`/`assumption` as fact.
3. On encountering `unknown`, AI stops & asks or records it — **guessing forbidden**.
4. New inferences go to `knowledge/inferred.md` or `generated/`, never to `source: human` files.
5. Without `evidence`, max status is `assumption`.
6. AI does not fabricate architecture, APIs, services, databases, integrations, ownership, or business rules.
7. Treat legacy AI artifacts (`.ai/`, `.claude/`, `AGENTS.md`, etc.) as **reference**, not source-of-truth. Repo code wins on conflict.
8. Tag every `unknowns.md` entry with priority: `blocking` · `important` · `informational`.
9. Use `owner: unresolved` (not `TBD`) when owner is undetermined; create one root unknown `U-OWN`.
10. **Evidence Consistency** — before finalizing context, cross-check critical claims against repo evidence (tables, migrations, entities, repositories, APIs/handlers, workers, integrations, validation rules). If repo shows N items, context must say N — not approximate.
11. **Drift Detection** — when repo evidence changes after context was written, mark affected entries as stale, refresh from current code, log unresolved ambiguity in `unknowns.md`.
12. **No Phantom ADRs** — never list `ADR-NNNN` in `architecture.md` (or anywhere as cited evidence) unless the file actually exists. Planned ADRs go to `assumptions.md` or `unknowns.md`.
13. **Implicit Constraint Extraction** — during init, scan code for implicit constraints (enum values, validation rules, required fields, ID semantics, currency/amount rules, status fields, retry/idempotency). Global rules → `constraints.md`. System-specific → `systems/<name>/system.md`. Ambiguous → `unknowns.md`. Weak inference → `inferred.md`.
14. **Internal Table Hygiene** — markdown table cells follow the same conventions as front-matter. Owner cells use `unresolved`, never `TBD`. Status/priority cells use the canonical vocabulary.

## Status Promotion

```
assumption ──(evidence)──► inferred ──(human confirmation)──► confirmed
```

Promotion to `confirmed` requires entry in `knowledge/confirmations.md`.

## Lifecycle & Staleness

| Zone | Lifecycle |
|---|---|
| `temp/*` | Single session → deleted (gitignored, never authoritative) |
| `generated/*` | Until regenerated → overwritten. Commit only if stable & useful. Never source-of-truth. Must remain reproducible. |
| `inferred`/`assumption`/`unknown` | Until resolved |
| `core`/`layer`/`system` | Maintained → `deprecated` |
| ADR | Permanent → `superseded`, never deleted |

- `updated` exceeding `governance.staleness_days` → triggers re-review.
- Code change at `evidence` path demotes `confirmed` → `inferred`.

## Anti-Duplication

- One fact, one home.
- Shared context referenced via `id`, **never copied**.
- `systems/*` does not copy `01-core/` or `layers/*` standards.
- `modes/*` does not list `00-meta/*` or `01-core/*`.
- Domain/scope facts (e.g. producer lists, source-system enumerations) live in `01-core/product.md`. `systems/<name>/system.md` references — does not re-list — them.
- When the same list appears in two files, the file closer to the canonical home keeps it; the other becomes a reference by `id`.

## Ownership Rule

Avoid noise from repeated `owner: TBD` placeholders.

| Situation | Action |
|---|---|
| Owner known at init | Set on every file as the canonical team/individual reference |
| Owner unknown at init | Use `owner: unresolved` and create **one** unknown entry (`U-OWN`) in `knowledge/unknowns.md` referencing all affected files |
| Multiple ownership | Use a short ref token (e.g. `team.payments`) and define it once in `glossary.md` |

`owner: TBD` is deprecated as a value. Use `unresolved` (single root unknown) or a real ref.

## Layer Activation Rule

A layer is **activated** only when concrete evidence exists in the target repo.

| Layer | Evidence Required (positive) | Not Sufficient on Its Own |
|---|---|---|
| `backend` | Application code (server, API, business logic) | — |
| `frontend` | UI/web client code | — |
| `mobile` | iOS/Android/cross-platform code | — |
| `infrastructure` | Terraform/Helm/K8s manifests, CI/CD **deployment** logic, deployment scripts, environment provisioning | DB migrations, build tooling, env vars, local Dockerfile, local config — these usually belong to `backend` or `systems/<unit>` |
| `testing` | Test files or test runner configuration | — |

### Refined infrastructure rule

DB migrations, Makefile build targets, `.env.example`, local Dockerfiles for development do **not** by themselves justify activating the infrastructure layer. They are backend/system concerns. Activate `infrastructure` only when the repo demonstrably owns deployment or environment provisioning.

### Activation outcomes

- **Strong evidence** → activate, `confidence: high`.
- **Weak/partial evidence** → activate with `confidence: medium/low` + add unknown entries describing the ownership gap. Do not assume ownership of concerns hosted in another repo.
- **Evidence absent** → remove the layer folder; remove from `forge.config.yaml` → `layers_enabled`.

## README vs Layer Content Policy

Layer folder structure has two distinct file roles. **No content overlap.**

| File | Role | Content |
|---|---|---|
| `layers/<x>/README.md` | Entrypoint & TOC | Purpose statement, navigation links to sibling files, growth path. Stays lightweight. |
| `layers/<x>/<x>.md` (and sub-files) | Engineering knowledge | Conventions, patterns, tech stack, layer-specific rules, anti-patterns. Real layer content. |

README must NOT duplicate `<x>.md` content. If `<x>.md` exists, README becomes a one-paragraph pointer + table of files.

## Legacy AI Artifact Handling

When initializing on a repo that already has AI/context artifacts (`.ai/`, `.claude/`, `.cursor/`, `AGENTS.md`, ad-hoc docs), follow this discipline (operationalized in `specs/context-initialization.md` Phase 0.5):

- Treat legacy artifacts as **reference**, not source of truth.
- Repository code always wins on conflict.
- Conflicts go to `knowledge/unknowns.md`.
- Useful legacy content is re-expressed in correct zones with proper `status` + `evidence` (citing the legacy file).
- Never copy legacy content verbatim into `01-core/`/`layers/`/`systems/` without re-validating against code.

## Unknown Priority Classification

Each entry in `knowledge/unknowns.md` carries a priority field:

| Priority | Meaning | Trigger |
|---|---|---|
| `blocking` | Init or work cannot proceed without resolution | Missing constraint, undefined ownership for critical decision |
| `important` | Should be resolved within current sprint/cycle | Architectural ambiguity, incomplete contract |
| `informational` | Nice to know; resolve when convenient | Minor naming clarification, optional integration detail |

AI sorts unknowns by priority during planning mode. Blocking unknowns must be surfaced before any implementation starts.

## Glossary Signal Rule

If every entry in `glossary.md` carries the same `status`/`source`, do **not** repeat the value on each row. Use a single header note above the table:

```
> All entries below: `status: inferred`, `source: ai`, unless overridden in the row.
```

This eliminates low-value repeated metadata while preserving the override path for exceptions.

## Evidence Consistency Targets

When initializing or updating context, AI must perform an evidence sweep on these critical areas. Each claim in context must match repo reality.

| Area | Where to verify |
|---|---|
| Database tables | `migrations/*` SQL or schema files |
| Migrations | Migration filenames, sequence, content |
| Entities/models | Domain entity files, ORM models |
| Repositories | Repository implementation files |
| APIs / handlers / controllers | Proto files, route registration, handler files |
| Background workers | Worker entrypoints, job schedulers |
| External integrations | Client libraries, config of external services |
| Config / runtime hooks | Config loaders, bootstrap files |
| Validation rules | Validators, sentinel checks, enum constraints |

If context says "N items" and repo has different count → context is wrong; correct it. Log the discrepancy in `unknowns.md` if root cause is unclear.

## Drift Detection

When repo evidence at an `evidence: ref` path changes:

1. Affected file's `status: confirmed` demotes to `inferred`.
2. AI proposes refresh from current code.
3. If refresh introduces ambiguity not resolvable from code alone → log to `unknowns.md`.
4. Old assertions that no longer hold are marked `deprecated`, not silently deleted.

## Phantom ADR Rule

`architecture.md` and any other context file MUST NOT cite `ADR-NNNN` references unless the ADR file actually exists at `knowledge/decisions/ADR-NNNN-*.md`.

| Intent | Where it goes |
|---|---|
| ADR exists | Cite as `evidence: { type: adr, ref: ... }` |
| ADR planned but not written | Entry in `assumptions.md` or `unknowns.md` (priority `important`) |
| Roadmap idea | `unknowns.md` (priority `informational`) — never cited as evidence |
