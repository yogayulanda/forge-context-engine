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

| Layer | Evidence Required |
|---|---|
| `backend` | Application code (server, API, business logic) |
| `frontend` | UI/web client code |
| `mobile` | iOS/Android/cross-platform code |
| `infrastructure` | IaC (Terraform/Helm/K8s), Dockerfiles for deployment, CI/CD deploy logic |
| `testing` | Test files or test runner configuration |

If evidence is **weak or partial**:
- Activate layer with `confidence: medium` or `low`.
- Add unknown entries describing the ownership gap.
- Do not assume ownership of concerns hosted in another repo.

If evidence is **absent**:
- Remove the layer folder.
- Remove from `forge.config.yaml` → `layers_enabled`.

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
