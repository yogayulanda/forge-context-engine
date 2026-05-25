# Platform Context Specification

| Field | Value |
|---|---|
| Document | Platform Context Specification |
| Version | 0.1 |
| Date | 2026-05-21 |
| Status | `draft` — specification only |
| Language | English |
| Dependency | `FORGE-CONTEXT-ARCHITECTURE.md` v0.5 · local `.forge/context/` runtime |

> Defines optional multi-repo platform cognition. This document does not introduce runtime folders, CLI behavior, automation, or changes to local repo Forge structure.

---

## 1. Purpose

Platform context lets Forge reason about a bounded ecosystem spanning multiple repositories without copying each repository's local context.

It exists to capture cross-repo facts that do not belong to any single repo:

- Runtime topology.
- Shared runtime/platform component adoption.
- Integration graph.
- Shared contracts.
- Ownership map.
- Global ADRs.
- Platform-level unknowns, assumptions, and confirmations.

Platform context must distinguish service-to-service runtime topology from source-level or shared-runtime adoption. A dependency on a shared runtime foundation does not imply service-to-service traffic.

Local repo cognition remains owned by each repo's local `.forge/context/`.

---

## 2. Non-Goals

Platform context does NOT:

- Replace local `.forge/context/`.
- Merge unrelated repositories into one cognitive space.
- Store local repo implementation details.
- Duplicate `01-core/`, `layers/`, `systems/`, or knowledge ledgers from member repos.
- Override local repo code or local Forge context.
- Define runtime folder structure for v0.1.
- Define CLI, CI, automation, sync, enforcement, or validation tooling.
- Create a universal enterprise knowledge graph.

---

## 3. When To Create Platform Context

Create a platform context when multiple repositories form one bounded ecosystem and cross-repo reasoning is required.

Use it when at least two of these are true:

- Repos participate in one product, domain, or platform capability.
- Repos exchange runtime traffic, events, APIs, data contracts, or shared schemas.
- Repos share operational ownership, release coordination, or incident blast radius.
- Repos depend on shared libraries, SDKs, protocol definitions, or generated clients.
- Architectural decisions span more than one repo.
- A change in one repo regularly requires analysis of impact in another repo.

A platform context may also be created as a **pilot** when:

- At least one `deployable-service` consumes one `shared-runtime` or `platform-component`.
- Evidence is clear from local Forge context and repository code.
- The platform boundary is explicitly marked `pilot`.

Do not promote a pilot to full platform context until more consumers, runtime edges, ownership, or shared contracts are evidenced.

The boundary must be explicit. One platform context equals one bounded ecosystem.

---

## 4. When Not To Create It

Do not create platform context when:

- A repo is standalone and cross-repo reasoning is rare.
- Repos only share an organization, language, framework, or deployment platform.
- Repos are unrelated products with different owners and change cadences.
- A shared library can be referenced directly from local contexts without platform-level topology.
- One service consumes one shared runtime but the boundary cannot be marked as a pilot.
- The goal is to centralize all knowledge for convenience.
- The required facts already have a clear home in a local repo context.

Unrelated repos must not be forced into the same platform context.

---

## 5. Multi-Platform Model

Multiple platform contexts are allowed.

Rules:

- Each platform context has one bounded ecosystem.
- A repo may belong to zero, one, or multiple platform contexts when it participates in multiple ecosystems.
- Shared libraries may be referenced by multiple platform contexts.
- Shared libraries do not automatically define a platform boundary.
- Shared runtime components may be referenced by multiple platform contexts without being reduced to utility libraries.
- Platform contexts may reference each other only by stable ID or repository reference; they do not merge content.
- If two platform contexts need frequent duplicate topology, the boundary should be reviewed by humans.

Example:

| Repo | Roles | Platform context membership |
|---|---|---|
| `payments-api` | `deployable-service`, `consumer` | `platform.payments` |
| `risk-engine` | `deployable-service`, `consumer` | `platform.payments`, `platform.risk` |
| `go-core` | `shared-runtime`, `platform-component` | referenced by multiple platform contexts; not automatically a runtime node |

---

## 5.1 Ecosystem Types

### Runtime Ecosystem

Repos are connected by service-to-service traffic, events, APIs, queues, or operational workflows.

Runtime ecosystem evidence includes `runtime-calls`, `publishes-event`, `consumes-event`, or `deploys-with` edges between deployable components.

### Shared-Runtime Adoption Ecosystem

Repos are connected because one or more services adopt the same shared runtime/platform foundation.

Shared-runtime adoption may justify a narrow pilot platform context. It must not be over-modeled as full runtime topology. Full platform adoption requires more evidence than one service consuming one shared runtime.

---

## 5.2 Member Role Taxonomy

| Role | Definition |
|---|---|
| `deployable-service` | Repository that builds and runs as a service/process. |
| `shared-runtime` | Non-deployable foundation component used by services to bootstrap runtime behavior such as server startup, config, logging, DB transaction helpers, migration helpers, cache, messaging/outbox, errors, and observability. |
| `utility-library` | Smaller reusable helper library without broad runtime responsibility. |
| `platform-component` | Reusable platform-level component that may be deployable or non-deployable and is shared across services. |
| `contract-owner` | Repository that owns shared API/event/schema/protobuf/client contracts. |
| `consumer` | Repository that depends on or uses another repo/component. |

Rules:

- Do not reduce `shared-runtime` components into generic utility libraries.
- Do not classify non-deployable components as `deployable-service`.
- A repository may have multiple roles.

Examples:

| Repo | Correct roles |
|---|---|
| `shared-runtime-core` | `shared-runtime`, `platform-component` |
| `example-service` | `deployable-service`, `consumer` |

---

## 5.3 Edge Type Taxonomy

| Edge | Definition |
|---|---|
| `imports` | Source-level dependency via module/package import. |
| `uses-runtime` | A service uses a shared runtime/foundation component. |
| `runtime-calls` | Network/runtime call between deployable components. |
| `publishes-event` | Produces events/messages. |
| `consumes-event` | Consumes events/messages. |
| `owns-contract` | Owns shared API/schema/protobuf/event/client contract. |
| `generates-client` | Generates or publishes clients from shared contracts. |
| `deploys-with` | Deployment or runtime environment coupling. |

Rules:

- `imports` and `uses-runtime` are not the same as `runtime-calls`.
- A shared runtime dependency does not imply service-to-service traffic.
- Runtime topology must not be inferred from package imports alone.

Example:

```text
example-service --imports/uses-runtime--> shared-runtime-core
```

Not:

```text
example-service --runtime-calls--> shared-runtime-core
```

---

## 6. Input Requirements

Before initializing platform context, collect:

- Platform name and explicit boundary.
- Ecosystem type: `runtime` or `shared-runtime-adoption`.
- Boundary maturity: `pilot` or `full`.
- Member repos and their canonical repository URLs.
- Member roles for each repo.
- Local Forge availability for each repo: present, absent, stale, unknown.
- Primary owners for platform and member repos.
- Cross-repo edge evidence: imports, runtime usage, APIs, events, queues, schemas, package deps, generated clients, deployment wiring.
- Shared-runtime version evidence where available: module path, required version, replace directive, tag, commit SHA, or local path dependency.
- Shared contracts and their owning repo.
- Known global decisions and ADR locations.
- Known exclusions: repos that must not be considered part of the platform.

If local repo evidence is inaccessible, mark affected platform claims as `unknown` or `inferred`; do not guess.

Never collect or copy raw secrets into platform context. If cross-repo evidence contains credentials, tokens, cookies, private keys, database URLs with credentials, Kafka/SASL credentials, cloud credentials, or OAuth client secrets, record only secret type, repo/file path, line/reference when available, masked preview, and security finding status.

---

## 7. Suggested Structure

This is a suggested conceptual structure for a future platform-context artifact. It is not runtime for v0.1.

```text
platform-context/
  platform.yaml
  README.md
  topology.md
  integrations.md
  contracts.md
  ownership.md
  decisions/
    PADR-0001-title.md
  knowledge/
    inferred.md
    assumptions.md
    unknowns.md
    confirmations.md
```

Suggested responsibilities:

| File | Responsibility |
|---|---|
| `platform.yaml` | Platform ID, ecosystem type, maturity, boundary, member repos, roles, excluded repos, local context refs. |
| `topology.md` | Repo-to-repo shape, edge types, and dependency direction. |
| `integrations.md` | Runtime/API/event/data integration graph; excludes pure source imports unless runtime behavior is evidenced. |
| `contracts.md` | Shared contracts, schemas, SDKs, generated clients, ownership. |
| `ownership.md` | Platform and repo ownership map; escalation paths if known. |
| `decisions/` | Global ADRs that affect multiple repos. |
| `knowledge/*` | Platform-level inferred facts, assumptions, unknowns, confirmations. |

---

## 8. Authority Rules

Authority order:

1. Local repo code.
2. Local repo `.forge/context/`.
3. Platform context.
4. Legacy docs, external docs, chat notes, or human memory.

Rules:

- Local repo code remains the highest source of truth.
- Local `.forge/context/` remains source of truth for local repo cognition.
- Platform context owns only cross-repo cognition.
- Platform context may summarize local repo roles only as needed for topology.
- On conflict, local repo evidence wins and platform context must be corrected or marked stale.
- Global ADRs apply only to the platform boundary that accepted them.
- A platform ADR cannot silently override a local repo ADR; conflict must be recorded.

---

## 9. Anti-Duplication Rules

Platform context MUST NOT duplicate:

- Local product descriptions.
- Local architecture details.
- Local layer conventions.
- Local system internals.
- Local validation rules.
- Local ownership facts already maintained in one repo.
- Full API/schema bodies when a stable contract reference exists.

Platform context SHOULD store:

- Stable references to local context IDs and files.
- Cross-repo edges.
- Contract ownership and compatibility expectations.
- Decision scope and affected repos.
- Gaps that require multi-repo resolution.

One fact, one home. Platform context records the cross-repo relationship, not the full local fact.

---

## 10. Cross-Repo Linking Model

Use stable references that survive language, heading, and prose changes.

Recommended reference shape:

```yaml
repo: <canonical-repo-id>
remote: <git-url-or-hosted-url>
local_context: <path-or-ref-to-.forge/context>
context_id: <local-forge-id>
evidence_ref: <repo-relative-path>
commit: <optional-commit-sha>
roles: [<member-role>]
```

Rules:

- Prefer local Forge `id` references over prose headings.
- Use repo-relative paths for evidence inside member repos.
- Include commit SHA when evidence stability matters.
- Use explicit edge types from the taxonomy.
- Do not infer `runtime-calls` from `imports` or `uses-runtime`.
- Link to shared contracts by owning repo plus path.
- Do not copy large contract bodies into platform context.
- Do not copy raw secrets, credential-bearing URLs, tokens, cookies, or private keys into platform context.
- If a linked repo is unavailable, mark the link `unknown` or `stale`.
- For `shared-runtime` edges, record version evidence when available: `go.mod` require version, replace directive, commit SHA, tag, local path dependency, and module path.
- If shared-runtime version evidence is missing, mark it `unknown`; do not infer compatibility guarantees.

Example:

```yaml
from: repo.example-service
to: repo.shared-runtime-core
edge_types: [imports, uses-runtime]
version_evidence:
  module_path: github.com/example/shared-runtime-core
  require: v0.0.0
  replace: ../shared-runtime-core
evidence:
  - { repo: example-service, ref: go.mod }
  - { repo: example-service, ref: cmd/server/main.go }
owner: team.platform
status: inferred
confidence: medium
```

---

## 11. Platform Initialization Workflow

1. Declare platform boundary, ecosystem type, maturity (`pilot` or `full`), and exclusions.
2. Register member repos with canonical IDs and URLs.
3. Assign member roles using the role taxonomy.
4. Check whether each repo has local `.forge/context/`.
5. Read only enough local context to identify repo role, public interfaces, contracts, ownership, and unknowns.
6. Classify cross-repo edges using the edge taxonomy.
7. For shared-runtime edges, capture version evidence.
8. Scan repository evidence for cross-repo links when local context is missing or stale.
9. Populate topology, integrations, contracts, ownership, and global decisions using redacted evidence only.
10. Route unresolved cross-repo ambiguity to platform `knowledge/unknowns.md`.
11. Mark AI-derived platform facts as `status: inferred`, `source: ai`, default `confidence: medium`.
12. Request human confirmation for platform boundary, maturity, ownership, and global decisions.
13. Record confirmations in platform `knowledge/confirmations.md`.

If the only evidenced relationship is one `deployable-service` consuming one `shared-runtime`, initialize as `pilot` only.

Do not edit member repos during platform initialization unless that is a separate explicit task.

---

## 12. Platform Audit Workflow

Audit platform context when member repos change, integrations change, ownership changes, or global decisions are updated.

Audit checks:

- Member repo list still matches the platform boundary.
- No raw secrets appear in platform context, audit reports, validation-cases, confirmations, decisions, inferred knowledge, or unknowns.
- Excluded repos are still intentionally excluded.
- Cross-repo links still resolve.
- Contract references still exist at the owning repo.
- Integration direction, edge type, and protocol still match repo evidence.
- Runtime topology does not contain edges inferred from source imports alone.
- Shared-runtime version evidence is current or explicitly unknown.
- Local context conflicts are identified and routed.
- Ownership map does not invent owners for unresolved repos.
- Global ADRs cite actual decision files.
- Platform facts do not duplicate local facts.
- `source: ai` + `status: inferred` + `confidence: high` has deterministic evidence.

Audit outcomes:

- Confirmed current: leave unchanged.
- Drifted: mark stale and update from evidence.
- Conflicting: record both sides and add unknown.
- Unverifiable: demote to `inferred`, `assumption`, or `unknown`.

---

## 13. Unknown/Inferred/Confirmed Handling

Use the same semantic discipline as local Forge.

| Status | Platform meaning |
|---|---|
| `unknown` | Cross-repo fact is needed but not known. Guessing forbidden. |
| `assumption` | Temporary platform belief without sufficient evidence. |
| `inferred` | AI-derived platform fact with evidence. Non-authoritative. |
| `confirmed` | Human-confirmed or directly verified platform fact. |
| `deprecated` | Platform fact no longer applies. |

Confidence rules:

- Default confidence for `source: ai` + `status: inferred` is `medium`.
- Use `high` only for deterministic evidence, such as an explicit dependency declaration or contract file.
- Architecture intent, ownership, business process, compliance, and deployment responsibility are not `high` unless explicitly evidenced.
- Shared-runtime compatibility is not inferred when version evidence is missing.
- Human confirmation promotes through confirmations, not confidence inflation.

Unknown handling:

- Platform unknowns must identify affected repos.
- Ownership unknowns use `owner: unresolved`.
- Boundary ambiguity is `blocking`.
- Unknown ecosystem type or maturity is `blocking`.
- Missing shared-runtime version evidence is `informational` unless it blocks a release or compatibility decision.
- Contract ownership ambiguity is `blocking` when authoritative contract decisions are required; otherwise `informational`.
- Nice-to-have topology details are `informational`.

---

## 14. Future Extension Points

Future versions may define:

- Runtime storage location and manifest format.
- Platform context validation rules.
- Cross-repo evidence refresh semantics.
- Platform context loading modes.
- Repository membership lifecycle rules.
- Compatibility matrix format for shared contracts.
- Platform ADR naming and promotion workflow.
- Optional CLI support.
- Optional visualization of topology and integration graph.

These are extension points only. v0.1 defines the cognitive contract, not implementation.
