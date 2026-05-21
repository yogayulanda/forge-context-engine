# Validation Specification

| Field | Value |
|---|---|
| Document | Context System Validation Specification |
| Version | 1.3 |
| Date | 2026-05-21 |
| Status | `decision` — finalized for forge-context-engine v0.2.1 |
| Language | English (context) · Bahasa Indonesia (human notes) |
| Dependency | `FORGE-CONTEXT-ARCHITECTURE.md` v0.5 §16 |

> **v1.2 -> v1.3 changes:** Added D8 confidence calibration and F8-F10 deterministic mode schema checks, including numeric-only `token_budget`. No new file types, zones, runtime folders, automation, or tooling.

---

## 0. Purpose

This document formalizes **all invariants** that a valid `.forge/context/` system must satisfy. Each rule is:
- Stated as a checkable assertion.
- Assigned a severity level.
- Classified as automatable or manual-only.
- Given a clear pass/fail criteria.

Use this as:
- Manual checklist during and after Context Initialization.
- Future spec for `forge validate` CLI tool.
- Acceptance criteria for real-world tests.

---

## 1. Severity Levels

| Level | Meaning | Action on Fail |
|---|---|---|
| `error` | Invariant violation. Context system is broken. | Must fix before commit. |
| `warning` | Soft violation. System works but is degrading. | Fix within current sprint/session. |
| `info` | Suggestion. System works, quality can improve. | Fix when convenient. |

---

## 2. Validation Rules

### Category A — Structural Integrity

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| A1 | `.forge/forge.config.yaml` exists and is valid YAML | error | yes |
| A2 | `.forge/context/` directory exists | error | yes |
| A3 | `00-meta/context-manifest.md` exists | error | yes |
| A4 | `00-meta/conventions.md` exists | error | yes |
| A5 | `01-core/product.md` exists | error | yes |
| A6 | `01-core/architecture.md` exists | error | yes |
| A7 | Every folder in `layers_enabled` (from config) has a corresponding `layers/<name>/` directory | error | yes |
| A8 | Every entry in `systems[]` (from config) has a corresponding `systems/<name>/` directory with `system.md` | error | yes |
| A9 | `CLAUDE.md` (or equivalent adapter) exists at repo root | warning | yes |
| A10 | `temp/` directory is gitignored | error | yes |

### Category B — Front-Matter Validity

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| B1 | Every `.md` file under `.forge/context/` has YAML front-matter block (`---` delimited) | error | yes |
| B2 | Front-matter contains required fields: `id`, `title`, `type`, `status`, `confidence`, `source`, `owner`, `updated` | error | yes |
| B3 | `type` value is one of: `meta`, `core`, `layer`, `system`, `knowledge`, `mode`, `generated` | error | yes |
| B4 | `status` value is one of: `confirmed`, `inferred`, `assumption`, `unknown`, `deprecated` | error | yes |
| B5 | `confidence` value is one of: `high`, `medium`, `low` | error | yes |
| B6 | `source` value is one of: `human`, `ai`, `hybrid` | error | yes |
| B7 | `updated` is a valid date in `YYYY-MM-DD` format | error | yes |
| B8 | Files with `type: system` must have `system_type` field with value in: `service`, `app`, `worker`, `library`, `infra-module`, `platform-component` | error | yes |
| B9 | `id` follows format `<zone>.<name>` (lowercase, dot-separated) | warning | yes |
| B10 | `review_by` (if present) is a valid date ≥ `updated` | warning | yes |

### Category C — ID Uniqueness & Registry

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| C1 | Every `id` across all files is unique (no duplicates) | error | yes |
| C2 | Every file under `.forge/context/` is registered in `context-manifest.md` File Registry | error | yes |
| C3 | Every entry in File Registry corresponds to an existing file on disk | error | yes |
| C4 | No orphan files (exist on disk but missing from registry) | warning | yes |

### Category D — Evidence & Status Integrity

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| D1 | Files with `status: confirmed` must have non-empty `evidence` array | error | yes |
| D2 | Files with `status: inferred` must have non-empty `evidence` array | error | yes |
| D3 | Files with `status: assumption` must NOT have `evidence` claiming confirmation | warning | yes |
| D4 | `evidence[].type` is one of: `code`, `doc`, `adr`, `human`, `external` | error | yes |
| D5 | `evidence[].ref` is a non-empty string (path or URL) | error | yes |
| D6 | Evidence `ref` pointing to a code path — that path exists in the repo | warning | yes (requires repo access) |
| D7 | If code at evidence path has changed since `updated` date, `status: confirmed` should demote to `inferred` | warning | yes (requires git history) |
| D8 | `source: ai` + `status: inferred` defaults to `confidence: medium`; `confidence: high` requires direct deterministic repository evidence | warning | partial |

### Category E — Source & Write Protection

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| E1 | Files with `source: human` contain no AI-generated content markers | warning | partial (heuristic) |
| E2 | `knowledge/inferred.md` entries have `source: ai` or `source: hybrid` | error | yes |
| E3 | `knowledge/confirmations.md` is only written by humans (no `source: ai` entries) | error | yes |
| E4 | `generated/*` files all have `source: ai` | error | yes |

### Category F — Anti-Duplication & Zone Boundaries

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| F1 | Files in `modes/*` do NOT reference `00-meta/*` or `01-core/*` in their `include` section | error | yes |
| F2 | Files in `systems/*` do not duplicate verbatim content from `01-core/` | error | partial (similarity check) |
| F3 | Files in `systems/*` do not duplicate verbatim content from `layers/*` | error | partial (similarity check) |
| F4 | No file in `layers/*` contains unit-specific facts (should be in `systems/`) | warning | manual |
| F5 | No file in `01-core/` contains layer-specific details (should be in `layers/`) | warning | manual |
| F6 | Inter-system dependencies expressed as `id` references, not content copies | warning | partial |
| F7 | Producer / source-system / domain enumerations defined once in `01-core/product.md`; other files reference rather than re-list *(v1.1)* | warning | partial |
| F8 | Every `modes/*.md` file exposes Markdown sections `## include`, `## on_demand`, `## exclude`, `## token_budget`, and `## notes` | error | yes |
| F9 | `modes/*.md` files are context loading deltas, not prose-only narrative instructions | warning | partial |
| F10 | `modes/*.md` `## token_budget` contains only a decimal integer; labels such as `medium` or `medium-high` are invalid | error | yes |

### Category G — Knowledge Ledger Integrity

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| G1 | Every entry in `assumptions.md` has: ID, owner, created date, status | error | yes |
| G2 | Every entry in `unknowns.md` has: ID, owner, created date, status | error | yes |
| G3 | Every entry in `inferred.md` has: ID, evidence, owner, created date, status | error | yes |
| G4 | Every entry in `confirmations.md` has: date, target ID, transition, confirmer | error | yes |
| G5 | `confirmations.md` target IDs reference existing `id` values in the system | warning | yes |
| G6 | ADR files follow naming: `ADR-NNNN-*.md` (4-digit, sequential) | warning | yes |
| G7 | ADR with `status: accepted` has not been modified after acceptance (immutable body) | error | partial (requires git history) |
| G8 | No entry in `unknowns.md` with `status: unknown` has been "resolved" by guessing elsewhere | warning | manual |

### Category H — Size Budget & Staleness

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| H1 | `01-core/*` files ≤ `size_budget.core_lines` (default 200) | warning | yes |
| H2 | `layers/*` content files ≤ `size_budget.layer_lines` (default 150) | warning | yes |
| H3 | `systems/*` files ≤ `size_budget.system_lines` (default 200) | warning | yes |
| H4 | `modes/*` files ≤ `size_budget.mode_lines` (default 40) | warning | yes |
| H5 | Files with `updated` older than `governance.staleness_days` (default 90) → flagged for review | info | yes |
| H6 | Files exceeding budget should be split into sub-files, not truncated | info | manual |

### Category I — Configuration Consistency

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| I1 | `forge_version` in config matches expected runtime version | warning | yes |
| I2 | `tier` value is one of: `minimal`, `standard`, `advanced` | error | yes |
| I3 | `layers_enabled` contains only valid layer names matching existing `layers/` folders | error | yes |
| I4 | `systems[]` entries each have `name` and `type` fields | error | yes |
| I5 | `systems[].type` is one of: `service`, `app`, `worker`, `library`, `infra-module`, `platform-component` | error | yes |
| I6 | `loading.default_mode` references an existing file in `modes/` | error | yes |
| I7 | `governance.require_evidence_for` contains only valid status values | error | yes |

### Category J — Evidence Consistency *(v1.1, extended v1.2)*

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| J1 | Database table count claimed in `architecture.md`/`system.md` matches actual migrations/schema files | error | partial (count check) |
| J2 | Migration filenames cited in context exist in `migrations/` (or equivalent) | error | yes |
| J3 | Entity/model names cited match actual domain files | error | yes |
| J4 | Repository names cited match actual repository implementation files | error | yes |
| J5 | API/RPC names cited match proto files / route registration | error | yes |
| J6 | Worker/job names cited match actual worker entrypoints | error | yes |
| J7 | External integrations cited match actual client libraries / config | error | yes |
| J8 | Validation rules listed in `constraints.md` match actual validators / sentinel checks in code | warning | partial |
| J9 | Implicit constraints found in code (enums, validators, required fields, ID semantics, currency rules) are reflected in `constraints.md` or `systems/<name>/system.md` | warning | partial |
| J10 | **Required-field claims match service-layer empty-checks** — no field listed as service-required unless a corresponding empty-check exists in code *(v1.2)* | error | partial |
| J11 | **DB constraints documented separately from service validation** — fields with `CHECK`/`NOT NULL` but no service empty-check are documented as DB-constrained, NOT service-required *(v1.2)* | error | partial |
| J12 | **Repository fallback behavior documented** — fields where repository sets a default (e.g. `IsZero() → now`) are documented as repository-fallback, not service-required *(v1.2)* | warning | partial |
| J13 | **Validation layer attribution present** — every constraint entry states which layer enforces it (service / handler / DB / repository / business intent) *(v1.2)* | warning | manual |
| J14 | **Generated code policy documented** — if `gen/` (or equivalent) is committed, the policy (always-commit vs regenerate-only) is recorded in a layer/system file or ADR | info | manual |
| J15 | **Table role not conflated** — context does not describe migration-seeded, lookup, or read-only tables as part of runtime write flows or transaction boundaries; each table's runtime role is stated explicitly *(v0.2.1 precision patch)* | error | partial |

### Category K — Drift & Phantom Detection *(v1.1)*

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| K1 | Every `ADR-NNNN` cited in any context file (esp. `architecture.md`) has a corresponding existing ADR file | error | yes |
| K2 | "Planned" / "future" ADR references do NOT appear as `evidence` entries | error | yes |
| K3 | Stale architecture claims (entries pointing to evidence paths that no longer exist) flagged | warning | yes |
| K4 | Layer activation matches actual repo evidence (no `infrastructure` activation without IaC/deploy evidence) | warning | partial |
| K5 | No internal table cell contains the deprecated value `TBD` (use `unresolved` for owner, valid status/priority elsewhere) | warning | yes |
| K6 | Glossary signal compaction: if all rows share `status`/`source`, header-note format is used | info | yes |
| K7 | Producer/source-system list is canonical in `01-core/product.md`; other files reference, do not duplicate | warning | partial |
| K8 | `inferred.md` evidence quality: every entry's evidence resolves to a real path/doc | error | yes |

### Category L — Language & Reference Stability *(v1.2)*

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| L1 | Repo declares a dominant context language (set during init; recorded in `00-meta/conventions.md` or commit history) | warning | partial (heuristic) |
| L2 | No file mixes whole-sentence prose in two languages (identifier + foreign word fragments allowed) | warning | partial (lang-detect) |
| L3 | Untranslated narrative residue (paragraph in second language inside otherwise translated file) flagged | warning | partial (lang-detect) |
| L4 | Technical identifiers (table names, enum values, RPC names, migration filenames, env keys) NOT translated | error | partial (must match code symbols verbatim) |
| L5 | Glossary terminology consistent across context (same term → same definition wherever it appears) | warning | yes |
| L6 | Cross-file references prefer `id` or file path over translated heading text | warning | partial |
| L7 | No quoted translated headings used as primary reference (e.g. citing `"Sumber Data"` or `"Data Sources"` directly) | warning | partial |
| L8 | Anchor links use stable slugs (`#producers`), not language-dependent ones | info | yes |

---

## 3. Validation Execution Modes

### 3.1 Manual Checklist (Current Phase)

Walk through each category (A–I) sequentially. Use the table format:

```
[ ] A1 — forge.config.yaml exists and valid
[ ] A2 — .forge/context/ exists
...
```

Recommended frequency:
- After Context Initialization (full pass).
- After adding new system/layer (Category A, B, C, I).
- After promoting status (Category D, E, G).
- Weekly during active development (Category H).

### 3.2 AI-Assisted Validation (Current Phase)

AI agent can be asked to run validation by reading all files and checking rules. Prompt:

```
Read all files under .forge/context/ and validate against the rules in 
specs/VALIDATION-SPEC.md. Report: rule ID, pass/fail, file path, details.
```

### 3.3 Automated CLI (Future — `forge validate`)

```bash
forge validate              # full validation
forge validate --fix        # auto-fix where possible (e.g., registry sync)
forge validate --category A # single category
forge validate --severity error  # errors only
forge validate --ci         # exit code 1 on any error (CI integration)
```

> Note: CLI spec is in the future tooling phase. This document only defines the RULES to be implemented.

---

## 4. Auto-Fixable Rules

Rules that a future `--fix` flag can resolve automatically:

| Rule | Auto-Fix Action |
|---|---|
| C2 | Add missing files to manifest registry |
| C3 | Remove non-existent entries from registry |
| C4 | Add orphan files to registry |
| H5 | Add `[STALE]` marker to flagged files |
| I3 | Sync `layers_enabled` with actual `layers/` folders |

Rules that are **never** auto-fixable (require human judgment):
- D1, D2 (evidence must come from real sources)
- E1, E3 (source attribution requires human verification)
- F2, F3 (duplication removal requires deciding which copy to keep)
- G7 (ADR immutability — requires reverting unauthorized changes)
- G8 (unknown resolution — requires domain knowledge)

---

## 5. Validation Report Format

Standard output format for reporting results:

```
FORGE CONTEXT VALIDATION REPORT
================================
Date: YYYY-MM-DD
Repo: <repo-name>
Tier: <standard|minimal|advanced>

ERRORS (must fix):
  [A7] layers_enabled contains "mobile" but layers/mobile/ not found
  [D1] systems/payment/system.md — status: confirmed but evidence is empty

WARNINGS (should fix):
  [H1] 01-core/architecture.md — 215 lines (budget: 200)
  [D6] layers/backend/backend.md — evidence ref "src/api/" path not found

INFO:
  [H5] 01-core/product.md — updated 92 days ago (staleness: 90)

SUMMARY:
  Total files checked: 24
  Errors: 2
  Warnings: 2
  Info: 1
  Status: FAIL (errors present)
```

---

## 6. Rule Dependency Map

Some rules depend on others passing first:

```
A1 (config exists) 
  └── I1–I7 (config validity)
       └── A7 (layers match config)
       └── A8 (systems match config)

A3 (manifest exists)
  └── C1–C4 (registry integrity)

B1 (front-matter exists)
  └── B2–B10 (front-matter fields)
       └── D1–D7 (evidence rules)
       └── E1–E4 (source rules)
```

Run in order: **A → B → C → I → D → E → F → G → H → J → K → L** to avoid cascading false failures.

J, K, and L depend on Phases 0.5–6 of init having completed and on D (evidence) being clean — they verify *content correctness* and *language/reference quality*, while D verifies *metadata correctness*.

---

## 7. Exceptions & Overrides

| Scenario | Override |
|---|---|
| Tier `minimal` | A7, A8 not applicable (no layers/systems required). H2, H3, H4 not applicable. |
| File explicitly `status: unknown` with `owner: TBD` | D1, D2 not applicable (awaiting init). |
| Runtime template files (pre-init) | C2 waived — registry populated during init. |
| `generated/*` files | H1–H4 budgets relaxed (AI output varies). |
| `temp/*` files | All rules waived (ephemeral, not committed). |
| `.gitkeep` files | B1 waived (not context files). |

---

## 8. Relationship to Other Specs

| Spec | Relationship |
|---|---|
| `FORGE-CONTEXT-ARCHITECTURE.md` §16 | Source of invariant definitions — this spec formalizes them |
| `CONTEXT-INITIALIZATION-PROTOCOL.md` §9 | Init Phase 6 uses this spec as acceptance criteria |
| Future `TOOLING-SPEC.md` | `forge validate` CLI implements this spec programmatically |
| Future CI pipeline | Uses `forge validate --ci` as gate |

---

## Appendix A — Quick Validation Checklist (Print-Friendly)

```
STRUCTURAL INTEGRITY
[ ] A1  forge.config.yaml valid
[ ] A2  .forge/context/ exists
[ ] A3  context-manifest.md exists
[ ] A4  conventions.md exists
[ ] A5  product.md exists
[ ] A6  architecture.md exists
[ ] A7  layers folders match config
[ ] A8  systems folders match config
[ ] A9  CLAUDE.md exists
[ ] A10 temp/ gitignored

FRONT-MATTER
[ ] B1  All .md files have front-matter
[ ] B2  Required fields present
[ ] B3  type valid
[ ] B4  status valid
[ ] B5  confidence valid
[ ] B6  source valid
[ ] B7  updated date valid
[ ] B8  system_type for systems
[ ] B9  id format correct
[ ] B10 review_by valid

REGISTRY
[ ] C1  All ids unique
[ ] C2  All files in manifest
[ ] C3  All manifest entries exist
[ ] C4  No orphan files

EVIDENCE
[ ] D1  confirmed has evidence
[ ] D2  inferred has evidence
[ ] D3  assumption not over-claiming
[ ] D4  evidence type valid
[ ] D5  evidence ref non-empty
[ ] D6  code paths exist
[ ] D7  stale confirmations flagged
[ ] D8  AI-inferred high confidence has deterministic evidence

SOURCE PROTECTION
[ ] E1  human files clean
[ ] E2  inferred.md sourced correctly
[ ] E3  confirmations.md human-only
[ ] E4  generated/ all source:ai

ANTI-DUPLICATION
[ ] F1  modes don't list core
[ ] F2  systems don't copy core
[ ] F3  systems don't copy layers
[ ] F4  layers don't hold unit-specific
[ ] F5  core doesn't hold layer-specific
[ ] F6  dependencies by id ref
[ ] F7  domain enumerations canonical in product.md
[ ] F8  modes expose Markdown sections include/on_demand/exclude/token_budget/notes
[ ] F9  modes are deltas, not prose-only instructions
[ ] F10 modes token_budget is numeric only

KNOWLEDGE LEDGERS
[ ] G1  assumptions entries valid
[ ] G2  unknowns entries valid
[ ] G3  inferred entries valid
[ ] G4  confirmations entries valid
[ ] G5  confirmation targets exist
[ ] G6  ADR naming correct
[ ] G7  accepted ADRs immutable
[ ] G8  unknowns not guessed

SIZE & STALENESS
[ ] H1  core ≤ 200 lines
[ ] H2  layers ≤ 150 lines
[ ] H3  systems ≤ 200 lines
[ ] H4  modes ≤ 40 lines
[ ] H5  stale files flagged
[ ] H6  over-budget files split

CONFIG CONSISTENCY
[ ] I1  forge_version matches
[ ] I2  tier valid
[ ] I3  layers_enabled matches folders
[ ] I4  systems entries valid
[ ] I5  system types valid
[ ] I6  default_mode exists
[ ] I7  governance values valid

EVIDENCE CONSISTENCY (J — v1.1+v1.2)
[ ] J1  table count matches migrations
[ ] J2  cited migrations exist
[ ] J3  entity names match domain files
[ ] J4  repository names match impl files
[ ] J5  API/RPC names match proto/routes
[ ] J6  worker names match entrypoints
[ ] J7  external integrations match clients
[ ] J8  validation rules match validators
[ ] J9  implicit constraints surfaced
[ ] J10 required-field claims match service empty-checks (v1.2)
[ ] J11 DB constraints separated from service validation (v1.2)
[ ] J12 repository fallback documented (v1.2)
[ ] J13 validation layer attribution present (v1.2)
[ ] J14 generated code policy documented (v1.2)
[ ] J15 table roles not conflated — seed/lookup separated from runtime writes (precision patch)

DRIFT & PHANTOM (K — v1.1)
[ ] K1  every cited ADR exists
[ ] K2  no planned ADRs cited as evidence
[ ] K3  no stale architecture claims
[ ] K4  layer activation matches evidence
[ ] K5  no internal TBD values in tables
[ ] K6  glossary signal compaction applied
[ ] K7  producer list canonical in product.md
[ ] K8  inferred entries have valid evidence

LANGUAGE & REFERENCE STABILITY (L — v1.2)
[ ] L1  dominant language declared
[ ] L2  no mixed-language sentences
[ ] L3  no untranslated residue paragraphs
[ ] L4  identifiers preserved verbatim
[ ] L5  glossary terms consistent across files
[ ] L6  cross-refs prefer id/path over heading text
[ ] L7  no quoted translated heading citations
[ ] L8  stable anchor slugs
```
