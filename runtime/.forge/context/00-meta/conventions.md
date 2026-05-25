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
updated: 2026-05-24
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

## Mode File Schema

Every `modes/*.md` file MUST expose exactly these Markdown sections after the title, in this order:

| Section | Meaning |
|---|---|
| `## include` | Context components normally loaded for this mode. |
| `## on_demand` | Context components loaded only when relevant. |
| `## exclude` | Context components never loaded by default. |
| `## token_budget` | Numeric recommended maximum context budget for this mode. |
| `## notes` | Concise mode-specific execution and reporting guidance. |

`token_budget` MUST contain only a decimal integer such as `4000`, `8000`, or `12000`; labels such as `medium` or `medium-high` are invalid.

Mode files are machine-resolvable context loading deltas and the authority for mode-specific execution behavior. They MUST NOT re-list `00-meta/*` or `01-core/*` unless explicitly needed, contain domain knowledge, or duplicate `conventions.md`.

## Mode Invocation

- Modes are loading deltas on top of always-loaded core.
- Read `.forge/forge.config.yaml` before mode execution and apply `runtime.non_interactive`.
- Mode files are authoritative for mode-specific execution behavior.
- Visible modes are limited to `planning`, `implementation` (invoked as implement), `execute`, `testing`, and `review`.
- `planning` owns strategic ECP reasoning; `implementation` owns human-reviewable task decomposition; `execute` owns repository modification; `testing` owns testing strategy/test changes; `review` owns correctness and risk review.
- Keep testing distinct from execute and review: execute modifies implementation, testing reasons about tests/coverage/verification, review evaluates correctness and risk.
- Test placement is convention-sensitive: unit tests are usually colocated, while non-unit tests may use a top-level `testing/` structure; testing mode owns detailed placement guidance.
- Load only context required by the task; do not broad-load `.forge/context` by default.
- Preserve evidence, inference, and unknown boundaries.
- Report loaded context, missing evidence, unresolved ambiguity, and mode sufficiency according to the selected mode.
- Runtime-managed cognition lives under `.forge/context`; repository-owned cognition remains in application code, repository docs, ADRs, and human confirmations.

## Runtime Interaction Behavior

Forge uses one runtime flag: `runtime.non_interactive`.

| Value | Behavior |
|---|---|
| `false` | Default interactive behavior. Ask concise clarification questions for blocking decisions, governance uncertainty, missing contract authority, ambiguous runtime behavior, or dangerous/destructive execution; continue after human confirmation. |
| `true` | Automation-safe behavior. Do not ask conversational questions; emit `BLOCKED`, `NEEDS_REVIEW`, or `NEEDS_CONFIRMATION`; continue only with allowed proposed defaults. |

Interactive prompts should offer the recommended option plus one alternative by default; use a third option only for major architecture tradeoffs. Avoid repetitive clarification loops and broad questionnaires.

Changing `runtime.non_interactive` is runtime-managed operational behavior only. It must not re-init context, rewrite knowledge, invalidate assumptions, modify inferred context, or rewrite systems, layers, or core cognition files.

## Unknown Decision Semantics

Unknowns are classified as:

| Classification | Meaning | Runtime behavior |
|---|---|---|
| `blocking` | Cannot safely continue without an authoritative decision | Interactive: ask the minimum decision question. Automation: emit `BLOCKED`, `NEEDS_REVIEW`, or `NEEDS_CONFIRMATION`. |
| `proposed-default` | Low-risk, conventional, reversible, non-authoritative operational choice | AI may continue, but must label the value `proposed`, `not confirmed`, and record why it is safe. |
| `informational` | Useful uncertainty that does not affect safe continuation | Record only; do not interrupt workflow. |

Proposed defaults never become confirmed facts without human confirmation. Blocking applies to authoritative contracts, ownership/SLA/compliance, destructive migration approval, security policy, production topology, retry/DLQ semantics, and event schema authority.

Human decision prompts must be decision-oriented: recommended safest option plus one viable alternative by default; use a third option only for major architecture tradeoffs.

## Secret Safety

Forge must never print, copy, summarize, or expose raw secrets discovered during init, audit, planning, implementation, review, testing, migration, or platform discovery.

Sensitive values include API keys, access tokens, refresh tokens, passwords, private keys, JWTs, session cookies, webhook secrets, database URLs with credentials, Kafka/SASL credentials, cloud credentials, and OAuth client secrets.

When a secret is detected:

- Redact the raw value before output or context write.
- Report only secret type, file path, line/reference when available, and safe masked preview such as `<REDACTED_SECRET>`, `<REDACTED_PRIVATE_KEY>`, or `****a91f`.
- Do not copy the raw value into `.forge/context`, `knowledge/inferred.md`, `knowledge/unknowns.md`, `knowledge/confirmations.md`, decisions, modes, reports, validation-cases, or platform context.
- Classify it as a security finding.
- Recommend rotation if the secret may have been committed, logged, displayed, copied, or otherwise exposed.
- Preserve enough evidence for remediation without revealing the value.

## Confidence Calibration

Default confidence for `source: ai` + `status: inferred` is `medium`.

Use `confidence: high` only when the claim is directly and deterministically verifiable from repository evidence. Never use `high` merely because the reasoning feels plausible. If human confirmation exists, promote through `knowledge/confirmations.md` instead of inflating confidence.

For brownfield init, unknown ownership, architecture intent, business rules, compliance, and deployment ownership MUST NOT be high confidence unless explicitly evidenced.

Examples:

| Claim type | Confidence |
|---|---|
| Direct code evidence, e.g. module name declared in `go.mod` | `high` allowed |
| Inferred architecture intent from docs/code pattern | `medium` |
| Ownership inferred from absence of `CODEOWNERS` | `unknown`, not `high` |
| Deployment ownership not found in repo | `unknown` or `medium`, not `high` |

## AI Operational Contract (Normative)

1. AI does not self-promote status — **propose only**.
2. AI does not present `inferred`/`assumption` as fact.
3. On encountering `unknown`, AI classifies it as `blocking`, `proposed-default`, or `informational`; guessing confirmed facts is forbidden.
4. New inferences go to `knowledge/inferred.md` or `generated/`, never to `source: human` files.
5. Without `evidence`, max status is `assumption`.
6. AI does not fabricate architecture, APIs, services, databases, integrations, ownership, or business rules.
7. Treat legacy AI artifacts (`.ai/`, `.claude/`, `AGENTS.md`, etc.) as **reference**, not source-of-truth. Repo code wins on conflict.
8. Tag every `unknowns.md` entry with classification: `blocking` / `proposed-default` / `informational`.
9. Use `owner: unresolved` (not `TBD`) when owner is undetermined; create one root unknown `U-OWN`.
10. **Evidence Consistency** — before finalizing context, cross-check critical claims against repo evidence (tables, migrations, entities, repositories, APIs/handlers, workers, integrations, validation rules). If repo shows N items, context must say N — not approximate.
11. **Drift Detection** — when repo evidence changes after context was written, mark affected entries as stale, refresh from current code, log unresolved ambiguity in `unknowns.md`.
12. **No Phantom ADRs** — never list `ADR-NNNN` in `architecture.md` (or anywhere as cited evidence) unless the file actually exists. Planned ADRs go to `assumptions.md` or `unknowns.md`.
13. **Implicit Constraint Extraction** — during init, scan code for implicit constraints (enum values, validation rules, required fields, ID semantics, currency/amount rules, status fields, retry/idempotency). Global rules → `constraints.md`. System-specific → `systems/<name>/system.md`. Ambiguous → `unknowns.md`. Weak inference → `inferred.md`.
14. **Internal Table Hygiene** — markdown table cells follow the same conventions as front-matter. Owner cells use `unresolved`, never `TBD`. Status/classification cells use the canonical vocabulary.
15. **Secret Safety** — raw secrets are never displayed, copied, summarized, or stored; report redacted evidence only and classify discoveries as security findings.

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

## Unknown Classification

Each entry in `knowledge/unknowns.md` carries a classification field:

| Classification | Meaning | Trigger |
|---|---|---|
| `blocking` | Work cannot safely continue without resolution | Authoritative contract, ownership/SLA/compliance, destructive migration, security, production topology, retry/DLQ, event schema authority |
| `proposed-default` | Work may continue using a labeled safe default | Topic/package/handler/feature-flag/internal routing naming or other low-risk reversible operational choice |
| `informational` | Work may continue without a default | Optional optimization, future topology possibility, non-critical ambiguity |

AI sorts unknowns by classification during planning mode. Blocking unknowns must be surfaced before implementation or release. Proposed defaults must remain explicitly `proposed` and `not confirmed`.

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

## Language Consistency Rule

Each repo's `.forge/context/` uses **one dominant natural language** for narrative content. Selected during init based on (in order):

1. Existing repo documentation language (README, ADRs, /docs)
2. Engineering team convention
3. Pre-existing context (legacy `.ai/` etc.)
4. Dominant commit/documentation language

The chosen language must be applied consistently across:

`01-core/product.md` · `01-core/architecture.md` · `01-core/principles.md` · `01-core/constraints.md` · `systems/<unit>/system.md` · `layers/<x>/<x>.md` · `00-meta/glossary.md` · `knowledge/inferred.md` · `knowledge/assumptions.md` · `knowledge/unknowns.md` · `knowledge/decisions/ADR-NNNN-*.md` · layer `README.md`

### What MUST NEVER Be Translated

Technical identifiers stay verbatim regardless of dominant language:

- Source code symbols (function/class/variable names)
- Database table & column names
- Field names, enum values, status codes
- Protocol names (gRPC, HTTP, AMQP, etc.)
- API paths, RPC method names, route patterns
- Migration filenames
- Event/topic names, queue names
- External system names, dependency names
- Configuration keys (env vars, config paths)

Examples:

| Rule | Example |
|---|---|
| Keep verbatim | `ExternalRefID` stays `ExternalRefID` |
| Keep verbatim | `transaction_error_definitions` stays as-is |
| Keep verbatim | `direction: INBOUND/OUTBOUND` enum values unchanged |
| Keep verbatim | `CreateTransactionHistory` RPC name unchanged |

### Mixed Language Allowed Only For

- Preserving repo-native or business-native terminology when no equivalent exists
- External protocol or product naming
- Source-code identifiers embedded in prose

Whole sentences in a second language inside an otherwise single-language file are NOT acceptable.

### Anti-Patterns

- Translating only headings while leaving body in another language.
- Half-translating a file then leaving residue paragraphs untranslated.
- Translating identifier-shaped terms to "explain" them in prose.
- Forcing translation of repo-native business jargon that has no equivalent.

## Reference Stability Rule

When one context file refers to content in another, prefer **stable references** over fragile prose pointers — especially for translated/translatable headings.

| Prefer (stable) | Avoid (fragile) |
|---|---|
| `core.product` (id ref) | "the product file" |
| `01-core/product.md` (file ref) | the file currently named "Product" |
| `core.product → producers list` (semantic ref) | `"Sumber Data"` section / `"Data Sources"` section |
| `system.payment-service` (id ref) | "payment service docs" |
| Slug anchor `#producers` if used consistently | Verbatim heading text in any language |

### Why

Heading text changes when language switches or when content is refactored. Identifier (`id`) and file-path references survive both.

### Practical Guidance

- Reference by `id` first, then file path, then anchor — heading text last.
- If anchor must be used, define it via consistent slug (e.g. `#producers`, `#data-flow`) that does not depend on translated heading.
- Avoid quoting translated headings inline; cite the file/id and let the reader navigate.

## Validation Semantics Rule

Validation lives in **multiple layers**. Context must preserve where each rule is enforced — never flatten everything into "required fields".

### Validation Layers

| Layer | Where | What it does | How to read in code |
|---|---|---|---|
| Handler / API | `internal/handler/*` (or routes) | Transport-level shape, format, range | Validators on request DTOs, OpenAPI/proto annotations |
| Service | `internal/service/*` (or use-cases) | Business validation, empty-checks, normalization | Functions like `sanitize<X>Input`, explicit `if x == "" return error` |
| Database | `migrations/*`, schema | `NOT NULL`, `CHECK`, `UNIQUE`, FK | SQL DDL + index definitions |
| Repository | `internal/repository/*` | Persistence-time fallback, defaults, transaction boundary | Code paths like `if x.IsZero() { x = now }` |
| Business intent | ADRs, product spec | Why a rule exists | Cross-reference between code and `01-core/product.md` |
| Inferred | `knowledge/inferred.md` | AI-derived guesses (still needs validation) | — |

### Mandatory Distinctions

When documenting a field constraint, the context must state:

1. **At which layer is it enforced?** (service / handler / DB / repository)
2. **What is the failure mode?** (returns error, demoted to default, DB-rejected)
3. **Is it consistent across layers?** (e.g. service-required + DB-NOT NULL = aligned; service-optional + DB-CHECK = different concerns)

### Anti-Pattern

```
❌ "required: user_id, channel, direction, transaction_time"
   (flattens 4 different validation realities into one false claim)

✅ Service-required (empty-check): user_id, channel
   DB-constrained (CHECK): direction (∈ debit|credit)
   Repository fallback: transaction_time (zero → now)
```

### Source-of-Truth Order

When validation evidence conflicts:
1. **Code** wins (service code, schema DDL, repository code).
2. **ADR** for intent ("why").
3. **Existing context** is least authoritative — corrected against #1 and #2.

If business intent is unclear (a field is DB-constrained but never service-validated, and no ADR explains why), record an unknown with priority `important`.

## Implicit Constraint Extraction

During brownfield init, AI must scan code for **implicit constraints not obvious from naming alone**, and route them correctly.

### What to Extract

| Source | Extract |
|---|---|
| SQL `CHECK` constraints | Enum value sets per column |
| `UNIQUE` indexes | Uniqueness contracts (e.g. `reference_id`) |
| `NOT NULL` columns | Hard required-at-DB fields |
| FK with `CASCADE` / `RESTRICT` | Lifecycle coupling between tables |
| Service `sanitize*Input` | Service-required vs trimmed-only fields |
| Validators (`isAlphaString`, regex, length) | Format constraints |
| Repository defaults / fallbacks | What happens when caller omits a value |
| Retry / idempotency code | Whether operation is replay-safe |
| Status transition tables | Allowed lifecycle moves |
| Currency / amount handling | Smallest-unit storage, ISO codes, non-negative checks |
| Seeded reference data | Pre-defined codes (error catalogs, lookup tables) |

### Routing

| Constraint nature | Destination |
|---|---|
| Global hard rule (compliance, platform-wide, regulatory) | `01-core/constraints.md` |
| Single-unit behavior | `systems/<name>/system.md` |
| Weak inference (no clear ADR backing) | `knowledge/inferred.md` |
| Unclear business intent | `knowledge/unknowns.md` (priority `important`) |

### Audit Triggers

Flag the context as drifted if any of these appear without a corresponding constraint entry:
- New `CHECK` constraint in a recent migration
- New `UNIQUE` index added
- New `sanitize*` empty-check added
- New repository fallback / default
- New seeded lookup row in error/code catalog

## Runtime vs Seed Semantics Rule

AI must not describe migration-seeded, bootstrap-only, lookup, or static configuration tables as part of runtime operational write flows unless runtime code actually writes to them.

### Table Role Classification

When extracting database tables during init, classify each by role:

| Role | Definition | Evidence |
|---|---|---|
| `operational-write` | Written by application code during normal request/event processing | Repository `Create`/`Update`/`Delete` calls |
| `transactional-write` | Written together inside one runtime transaction boundary | `dbtx.WithTx` / `BEGIN...COMMIT` wrapping multiple tables |
| `read-only-runtime` | Read at runtime but never written by application code | Only `SELECT` in repository; no `INSERT`/`UPDATE` |
| `migration-seeded` | Rows/tables populated only by migration scripts or init scripts | `INSERT` only in `*.up.sql`; no runtime write path |
| `lookup/reference` | Read at runtime for resolution (e.g. error catalogs, config tables) | `SELECT` in service/repository; seeded by migration |
| `generated/internal` | Created by framework, ORM, or tooling; not owned by application | ORM audit tables, migration tracking tables |
| `unknown` | Role cannot be determined from available evidence | — |

### Mandatory Distinctions in Context

When documenting tables in `architecture.md`, `system.md`, or `constraints.md`:

1. **Runtime write path** — tables written by application code during normal operations.
2. **Transactional write path** — tables written together inside one transaction boundary. State the exact count and names.
3. **Migration/seed data** — tables or rows populated only by migration scripts. Must NOT be described as part of runtime write flows.
4. **Lookup/reference** — tables read at runtime for resolution; seeded by migration. State read-only runtime role explicitly.
5. **Repository fallback** — values assigned by repository code when caller omits them (e.g. `IsZero() → now`). Not a service-layer default.
6. **Database constraints** — `CHECK`, `UNIQUE`, `FK`, `NOT NULL` enforced at persistence layer. Separate from service validation.

### Anti-Patterns

```
❌ "writes to 4 tables" — when one table is migration-seeded only
❌ "4-table transaction" — when only 3 tables are in the runtime transaction boundary
❌ "owned tables: [A, B, C, D]" — without clarifying runtime role of each

✅ "Create-flow transaction writes to 3 operational tables: A, B, C.
    D is migration-seeded and read at runtime for lookup; not part of runtime writes."
```

### If Classification Is Unclear

- Record table role as `unknown` in `knowledge/unknowns.md` (priority `important`).
- Do not flatten into a generic "owned tables" claim.
- Do not assume a table is part of the runtime write path without evidence in repository code.
