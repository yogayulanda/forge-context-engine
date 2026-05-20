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
owner: <team>
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

## Status Promotion

```
assumption ──(evidence)──► inferred ──(human confirmation)──► confirmed
```

Promotion to `confirmed` requires entry in `knowledge/confirmations.md`.

## Lifecycle & Staleness

| Zone | Lifecycle |
|---|---|
| `temp/*` | Single session → deleted |
| `generated/*` | Until regenerated → overwritten |
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
