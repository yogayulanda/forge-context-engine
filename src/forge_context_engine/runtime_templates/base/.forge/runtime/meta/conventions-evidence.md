---
id: meta.conventions-evidence
title: Evidence & Context Consistency Conventions
type: meta
status: confirmed
confidence: high
source: human
evidence:
  - { type: doc, ref: ../../../../specs/mode-invocation.md }
  - { type: doc, ref: ../../../FORGE-CONTEXT-ARCHITECTURE.md }
owner: forge-context-engine
updated: 2026-06-03
---

# Evidence & Context Consistency Conventions

Load this file when the task involves evidence requirements, source citation, context consistency, drift, implicit constraint extraction, or table role classification.

---

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

If context says "N items" and repo has a different count → context is wrong; correct it. Log the discrepancy in `.forge/context/99-open-questions.md` if the root cause is unclear.

---

## Drift Detection

When repo evidence at an `evidence: ref` path changes:

1. Affected file's `status: confirmed` demotes to `inferred`.
2. AI proposes refresh from current code.
3. If refresh introduces ambiguity not resolvable from code alone → log to `.forge/context/99-open-questions.md`.
4. Old assertions that no longer hold are marked `deprecated`, not silently deleted.

Drift statuses:

| Status | Meaning |
|---|---|
| `NO_DRIFT_FOUND` | Checked relevant artifacts/context against current evidence; no contradiction found. |
| `DRIFT_RISK` | Evidence may be stale or incomplete; do not treat stale context as authoritative. |
| `DRIFT_DETECTED` | Current code/repo evidence contradicts an artifact, context entry, decision assumption, or generated output. |

When drift is detected, current repository evidence wins. Stale artifacts may be cited as history only and must be labeled stale, partial, or superseded.

---

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
| Global hard rule (compliance, platform-wide, regulatory) | `.forge/context/14-decisions-assumptions-and-constraints.md` |
| Single-unit behavior | `systems/<name>/system.md` |
| Weak inference (no clear ADR backing) | active `.forge/context/*.md` entries labeled `inferred` |
| Unclear business intent | `.forge/context/99-open-questions.md` |

### Audit Triggers

Flag the context as drifted if any of these appear without a corresponding constraint entry:
- New `CHECK` constraint in a recent migration
- New `UNIQUE` index added
- New `sanitize*` empty-check added
- New repository fallback / default
- New seeded lookup row in error/code catalog

---

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

- Record table role as `unknown` in `.forge/context/99-open-questions.md`.
- Do not flatten into a generic "owned tables" claim.
- Do not assume a table is part of the runtime write path without evidence in repository code.
