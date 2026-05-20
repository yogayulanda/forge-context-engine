---
id: meta.context-content-contract
title: Context Content Contract — forge-context-engine
type: meta
status: decision
confidence: high
source: hybrid
evidence:
  - { type: doc, ref: FORGE-CONTEXT-ARCHITECTURE.md }
  - { type: doc, ref: CLAUDE.md }
owner: forge-context-engine
updated: 2026-05-20
---

# Context Content Contract — forge-context-engine

> v0.2 · Companion to `FORGE-CONTEXT-ARCHITECTURE.md` v0.5

## 0. About This Document

`FORGE-CONTEXT-ARCHITECTURE.md` answers **where** context lives — folder structure, zones, tiers. This document answers **what** may live in each place and **how** AI treats it: semantic contract per component.

This is NOT a document template, NOT a mandatory markdown schema, NOT format bureaucracy. The contract binds **meaning and boundaries**, not layout. File authors may use adaptive structure (headings, tables, lists) as long as semantic boundaries are respected.

Functions: AI-readable context engineering rules, anti-overlap guide, anti-hallucination guide, long-term maintenance guide.

`CLAUDE.md` (root adapter) stores no context and is outside this contract's scope.

**Loading this document:** it is `type: meta` in `00-meta/`, but is a verbose governance reference. Recommended: load **selectively** (during Context Initialization & context maintenance), not on every bootstrap — `conventions.md` remains the only normative file always loaded. Consequences for architecture invariant §8 noted in §6.

## 1. How to Read This Contract

Each component in §3 is defined via seven fixed fields:

1. **Purpose** — reason for the component's existence, one sentence.
2. **Knowledge it holds** — type of knowledge it owns.
3. **What it must NOT hold** — exclusion boundaries; prevents overlap.
4. **AI behavior** — how AI reads/writes/trusts the component.
5. **Verbosity** — expected density (see scale below).
6. **Loading** — when the component enters the AI context window (see §2.1).
7. **Relations** — connections & separation lines with other components.

**Verbosity scale:** `Minimal` (key/value) · `Very concise` (one line per entry) · `Concise` (assertive statements) · `Medium` (dense structured prose) · `Adaptive` (variable by content).

## 2. Global Rules

### 2.1 Three Loading Tiers

| Tier | Components | Contract implication |
|---|---|---|
| **Always loaded** | `forge.config.yaml`, `00-meta/*`, `01-core/*` | Cost paid on every task → **must be token-efficient** (strict size budget). |
| **Selective** | `layers/*`, `systems/*`, `knowledge/*`, `modes/<active>` | Loaded only when mode/intent references them → **this is where token savings come from**. |
| **Generated later** | `generated/*`, `temp/*` | Absent at bootstrap; created when needed, loaded on-demand. |

### 2.2 Authority Hierarchy (context conflict resolution)

When two context sources conflict, AI follows this trust order (highest → lowest):

1. **Live repo code** — source of truth for implementation facts; context is a derived cache.
2. **`knowledge/decisions/` (ADR)** — source of truth for intent & decisions.
3. **`01-core/constraints.md`** — hard limits; overrides design convenience.
4. **`status: confirmed` human-authored facts** in `01-core/`, `layers/`, `systems/`.
5. **`01-core/principles.md`** — soft guidance/heuristics.
6. **`status: inferred`** — `knowledge/inferred.md` and inferred layer/system entries.
7. **`status: assumption`** — `knowledge/assumptions.md`.
8. **`generated/*`** — never authoritative.
9. **`temp/*`** — never authoritative; disposable.

### 2.3 Placement Test — One Fact, One Home

Before writing a fact, ask: *"At what scope is this fact true?"*
- True for the entire product → `01-core/`
- True for one engineering discipline → `layers/`
- True **only** for one implementation unit → `systems/`

Shared context declared once, referenced via `id`, **never copied**. Duplication only valid as an intentional summary explicitly marked as derivative.

### 2.4 Token Efficiency

Prioritize signal-dense context over verbose documentation. Respect size budgets (`01-core/*` ≤ ~200 lines; `layers/*` ≤ ~150; `systems/*` ≤ ~200; `modes/*` ≤ ~40). Files exceeding budget split into sub-files, not compressed at the cost of clarity. Always-loaded tier components carry the strictest discipline.

### 2.5 Anti-Hallucination

AI never fabricates architecture, APIs, services, databases, integrations, ownership, or business rules. Without `evidence`, max status is `assumption`. New inferences go to `inferred.md`/`generated/`, never to `source: human` files. `unknown` is a mandatory destination — guessing forbidden. Normative AI operational contract lives in `00-meta/conventions.md`.

## 3. Per-Component Contract

### 3.1 `00-meta/context-manifest.md`

*Location: `.forge/context/00-meta/` · type: `meta`*

- **Purpose** — Index and routing map for the entire context system; single entry point telling AI what files exist, where, and their loading rules.
- **Knowledge it holds** — File/folder registry with loading tiers; bootstrap order & rules; active layers, systems, and modes; manifest validation rules. Pointers, not content.
- **Must NOT hold** — Any domain knowledge (product, architecture, conventions, business rules); copies of other file content; engineering decisions.
- **AI behavior** — Read first (after config) as routing table to determine which files to load per mode/intent. Not a fact source; if manifest and actual files differ, actual files win and manifest is updated.
- **Verbosity** — Very concise; table/list style.
- **Loading** — Always loaded (bootstrap, first `00-meta` file).
- **Relations** — Root of dependency graph; references all components. Paired with `forge.config.yaml` (config = settings; manifest = content & routing). Consumed by `modes/` during delta resolution.

### 3.2 `00-meta/conventions.md`

*Location: `.forge/context/00-meta/` · type: `meta`*

- **Purpose** — Rules of the context system itself: naming & ID conventions, front-matter schema, status vocabulary, AI operational contract (normative), status promotion path, lifecycle & staleness.
- **Knowledge it holds** — Stable repo-wide conventions about **how to manage context**; definition of always-loaded core; AI read/write contract.
- **Must NOT hold** — Discipline-specific coding conventions (→ `layers/`); product engineering principles (→ `principles.md`); domain knowledge; engine settings (→ `forge.config.yaml`).
- **AI behavior** — Always present; AI operational contract here is **normative** and must be obeyed (no self-promoting status, no writing to `source: human` files, no guessing `unknown`). Reference every time creating/updating context files.
- **Verbosity** — Concise; assertive, checkable rule statements.
- **Loading** — Always loaded (bootstrap, `00-meta`).
- **Relations** — Normalizes every context file. Rules enforced by `governance` block in `forge.config.yaml`. Distinct from `principles.md`: this is context system rules, not product engineering principles.

### 3.3 `00-meta/glossary.md`

*Location: `.forge/context/00-meta/` · type: `meta` · optional in Minimal tier*

- **Purpose** — Canonical vocabulary: single authoritative definition for ambiguous or project-specific domain/technical terms.
- **Knowledge it holds** — `term — canonical definition` entries; only project/domain-specific terms, acronyms, or terms with special meaning in this repo; aliases if needed.
- **Must NOT hold** — General engineering terms; tutorials/long explanations; architecture or product descriptions (→ `01-core/`).
- **AI behavior** — Lookup table for resolving ambiguous terms and aligning naming; prevents fabricated meanings. If usage deviates from glossary, glossary wins or gap is recorded.
- **Verbosity** — Very concise; one line per term. Because always loaded, tight-dense is a requirement.
- **Loading** — Always loaded when present (`00-meta`); optional in Minimal tier.
- **Relations** — Supports `product.md`, `architecture.md`, `systems/*` with shared vocabulary; referenced by term, not copied.

### 3.4 `01-core/product.md`

*Location: `.forge/context/01-core/` · type: `core`*

- **Purpose** — Global product & domain context: what the product is, problem solved, for whom, and system boundaries — answers "what product & why".
- **Knowledge it holds** — Product summary; domain & problem space; users & stakeholders; system boundaries (IN/OUT scope); core product terms. Facts & explicit decisions.
- **Must NOT hold** — Technical architecture & solutions (→ `architecture.md`); single-unit details (→ `systems/`); coding conventions; speculative roadmap; marketing material.
- **AI behavior** — Always available as background. AI anchors every generation/spec decision to product intent & scope boundaries; refuses to add features outside scope without a decision; unclear scope → `unknowns.md`.
- **Verbosity** — Medium; dense prose, ≤ ~200 lines.
- **Loading** — Always loaded (`01-core` core).
- **Relations** — Constrains `architecture.md` (problem → solution). Intent source for `modes/planning` & future SDD. Distinct from `architecture.md`: product = problem space, architecture = solution space.

### 3.5 `01-core/architecture.md`

*Location: `.forge/context/01-core/` · type: `core`*

- **Purpose** — High-level global system architecture: architecture style, major components, end-to-end data flows, external integrations, architectural constraints.
- **Knowledge it holds** — System-level structure; major component responsibilities & boundaries; high-level data flows; external integration points; major architectural decisions (with `status` & `evidence`).
- **Must NOT hold** — Single-discipline internals (→ `layers/`); single-unit details (→ `systems/`); business rationale (→ `product.md`); coding conventions; architecture guessed without evidence.
- **AI behavior** — Always-present mental model of the system. AI respects component boundaries, **does not fabricate** components/services/databases/integrations beyond what is registered; unverified components → `inferred`; gaps → `unknowns.md`.
- **Verbosity** — Medium; structured, ≤ ~200 lines.
- **Loading** — Always loaded (`01-core` core).
- **Relations** — Conceptual parent of `layers/` & `systems/` (both specialize, not copy). Constrained by `product.md` & `constraints.md`. Major decisions recorded as ADRs in `knowledge/decisions/`.

### 3.6 `01-core/principles.md`

*Location: `.forge/context/01-core/` · type: `core` · optional in Minimal tier*

- **Purpose** — Durable engineering values & standards: decision-making heuristics that guide judgment when concrete rules don't cover a case.
- **Knowledge it holds** — Prioritized engineering principles; trade-off heuristics; decision philosophy & quality standards. Stable, rarely changes.
- **Must NOT hold** — Context management conventions (→ `conventions.md`); hard constraints (→ `constraints.md`); product goals (→ `product.md`); implementation details or layer-specific rules.
- **AI behavior** — Trade-off arbiter when concrete rules are insufficient; used to justify recommendations. Not a hard limit — yields to `constraints.md` on conflict.
- **Verbosity** — Very concise; principle statements.
- **Loading** — Always loaded when present (`01-core` core); optional in Minimal tier.
- **Relations** — Underlies per-layer coding conventions (convention = concretized principle). Used by `modes/review`. Distinct from `constraints.md`: principles = "should", constraints = "must".

### 3.7 `01-core/constraints.md`

*Location: `.forge/context/01-core/` · type: `core` · optional in Minimal tier*

- **Purpose** — Hard limits and non-negotiables: compliance, performance, cost, security, and legacy/platform constraints that must be obeyed.
- **Knowledge it holds** — Explicit & factual constraints: regulatory mandates, performance budgets, platform limits, security mandates, required/banned technologies — with `evidence`/source.
- **Must NOT hold** — Soft preferences or principles (→ `principles.md`); conventions; aspirational goals; assumptions presented as constraints (→ `knowledge/assumptions.md`).
- **AI behavior** — Absolute hard limits. AI never proposes solutions that violate them; task-vs-constraint conflict → **stop and flag**. Highest authority after live code & ADR.
- **Verbosity** — Very concise; enumerated, assertive, auditable.
- **Loading** — Always loaded when present (`01-core` core); optional in Minimal tier.
- **Relations** — Constrains `architecture.md`, `layers/`, `systems/`, and `modes/implementation`. Overrides `principles.md` on conflict.

### 3.8 `forge.config.yaml`

*Location: `.forge/` (root namespace, only component outside `context/`) · no front-matter — config file, not narrative context*

- **Purpose** — Machine-readable engine manifest: declares **configuration** of the context system — tier, active layers, systems list, default mode, governance & size budget parameters.
- **Knowledge it holds** — Configuration values only: `forge_version`, `tier`, `layers_enabled`, `systems[]`, `loading.default_mode`, `size_budget`, `governance.*`.
- **Must NOT hold** — Domain knowledge; prose; architecture facts; conventions; human narrative. Minimal comments only.
- **AI behavior** — Read earliest at bootstrap to know **how** the engine is configured. Not a knowledge source; never cited as domain fact. AI may propose changes, not silently modify.
- **Verbosity** — Minimal; key/value only.
- **Loading** — Always loaded (bootstrap step 2, before `context/`).
- **Relations** — Paired with `context-manifest.md` (config = settings & toggles; manifest = content index). Activates `layers/`, `systems/`, and default mode. `governance`/`size_budget` parameters enforce `conventions.md` rules.

### 3.9 `layers/`

*Location: `.forge/context/layers/` · type: `layer` (per `<layer>.md` file)*

- **Purpose** — **Horizontal** context per engineering role/discipline — backend, frontend, mobile, infrastructure, testing (+ observability & security in Advanced tier); answers "how we work in one discipline", spanning all systems.
- **Knowledge it holds** — Per layer: discipline-specific conventions & patterns, standards, structure, layer constraints. Starts as `README.md` placeholder; `<layer>.md` content generated at init.
- **Must NOT hold** — Cross-discipline global context (→ `01-core/`); single-unit specific context (→ `systems/`); product knowledge; anything copied from core. One layer file does not mix two disciplines.
- **AI behavior** — Loads **only** layers relevant to the task; does not mix cross-layer context. Brownfield facts → `inferred`+evidence; greenfield → `assumption`+ADR.
- **Verbosity** — Medium per layer; focused, ≤ ~150 lines; split into sub-files when over budget.
- **Loading** — Selective; per layer, driven by mode/intent. Placeholder README is lightweight; content loaded only when layer is active.
- **Relations** — Specializes `architecture.md` and applies `principles.md`. Orthogonal to `systems/` (layer = horizontal slice, system = vertical slice); placement test §2.3 prevents duplication.

### 3.10 `systems/`

*Location: `.forge/context/systems/` · type: `system` (per `<name>/system.md`)*

- **Purpose** — **Vertical** context per real implementation unit — service, app, worker, library, infra-module, platform-component; answers "what is specific about this one unit", cutting across all layers it touches.
- **Knowledge it holds** — Per unit: responsibilities, public interfaces/API, dependencies (other units via `id` + external), layers touched (references), unit-specific runtime context, unit unknowns/assumptions. Only what is true **only** for this unit.
- **Must NOT hold** — Global context (→ `01-core/`); discipline standards applying to all similar units (→ `layers/`); business domain documentation; fabricated units.
- **AI behavior** — Loads only systems touched by the task; used to understand cross-layer impact & inter-unit dependencies. Dependencies declared as `id` references, not copies.
- **Verbosity** — Medium; focused per unit, ≤ ~200 lines; split when large.
- **Loading** — Selective; per unit, driven by mode/intent. In monorepo, only related units loaded (per-task token cost O(1)).
- **Relations** — Composes `layers/` vertically; detailed under `architecture.md`. Strict placement test prevents duplication with core & layers.

### 3.11 `knowledge/`

*Location: `.forge/context/knowledge/` · contains `decisions/`, `assumptions.md`, `unknowns.md`, `inferred.md`, `confirmations.md`*

- **Purpose** — Single truth ledger: physically separates the six knowledge states and serves as the system's hallucination-resistance engine.
- **Knowledge it holds** — See per-sub-component boundaries:

  | Sub-component | State | Authoritative? | Notes |
  |---|---|---|---|
  | `decisions/` (ADR) | Decision / intent | Yes (for intent) | Append-only; `ADR-NNNN`; immutable when `accepted` |
  | `assumptions.md` | Temporary assumptions | No | Not a basis for final decisions |
  | `unknowns.md` | Acknowledged gaps | — | Mandatory destination; guessing forbidden |
  | `inferred.md` | AI inferences | No | `source: ai`; must be labeled; quarantined |
  | `confirmations.md` | Confirmation log | Yes (audit) | Records status promotions to `confirmed` |

- **Must NOT hold** — Authoritative human facts (→ `01-core/`/`layers/`/`systems/`); raw generated artifacts (→ `generated/`); scratch (→ `temp/`). `inferred` never physically mixed with human facts.
- **AI behavior** — AI writes inferences/assumptions/unknowns **here**, never to `source: human` files. AI does not self-promote status — proposes only; promotion to `confirmed` requires `confirmations.md` entry. `unknown` = mandatory destination, guessing forbidden.
- **Verbosity** — Concise, append-only; ledger tables; structured ADRs. Grows by adding entries, not enlarging files.
- **Loading** — Selective per mode: `decisions/` → implementation/review; `assumptions`/`unknowns` → planning/testing; `inferred` → implementation.
- **Relations** — `decisions/` = intent source of truth (binds `architecture.md` & `systems/`). Feeds `modes/`. `inferred.md` paired with `generated/` (both non-authoritative).

### 3.12 `modes/`

*Location: `.forge/context/modes/` · type: `mode` (per `<mode>.md`)*

- **Purpose** — Context loading declaration per work type — planning, implementation, review, testing (+ security & documentation in Advanced); determines **what** context enters the AI window.
- **Knowledge it holds** — Per mode: `include` (delta above always-loaded core), `on_demand`, `exclude`, `token_budget`. Declaration references only.
- **Must NOT hold** — Any domain knowledge; runtime/automation code; procedural/behavioral steps; `00-meta/*` or `01-core/*` (core never re-listed — delta only).
- **AI behavior** — AI identifies active mode then follows its loading recipe (resolve `include`/`on_demand`/`exclude`, respect `token_budget`). Mode = context selection policy, not behavior policy.
- **Verbosity** — Very concise; pure declaration, ≤ ~40 lines per mode.
- **Loading** — Selective; only active mode resolved (`default_mode` from `forge.config.yaml`). Mode itself drives loading of other components.
- **Relations** — Consumes `context-manifest.md`; drives selective loading of `layers/`, `systems/`, `knowledge/`. Extension point for future SDD & agent workflows.

### 3.13 `generated/`

*Location: `.forge/context/generated/` · type: `generated` · created when needed*

- **Purpose** — AI-generated derivative context: summaries, indexes, code maps, snapshots extracted by AI from the real repo/context — strictly separated from human-authored ground truth.
- **Knowledge it holds** — Machine-derived artifacts: code maps, dependency summaries, extracted architecture snapshots. Always tagged `source: ai`, non-authoritative status, with timestamp & source.
- **Must NOT hold** — Human-authored ground truth; decisions; constraints; anything authoritative. Not hand-edited — regenerated, not maintained.
- **AI behavior** — Treated as low-trust & regenerable. AI verifies against real sources before relying on it; never cited over `01-core/`. Can be stale.
- **Verbosity** — Adaptive; stays concise — token-efficient summaries, not dumps.
- **Loading** — Generated later; created when needed, loaded selectively on-demand; never always-loaded.
- **Relations** — Derived from real repo + core context; consumed by `modes/`. Paired with `knowledge/inferred.md` (both non-authoritative).

### 3.14 `temp/`

*Location: `.forge/context/temp/` · gitignored · created when needed*

- **Purpose** — Ephemeral scratch: short-lived working context for one session/task. Fully disposable.
- **Knowledge it holds** — Transient notes, intermediate task state, context drafts — anything safe to delete when the session ends.
- **Must NOT hold** — Anything durable; decisions; ground truth; anything other components depend on. Not committed (gitignored).
- **AI behavior** — May be used freely as scratchpad within one task; never relied on across sessions; never made authoritative without being promoted out first.
- **Verbosity** — Unconstrained; irrelevant because content is disposable.
- **Loading** — Never auto-loaded; only within the active task that created it. Excluded from manifest routing.
- **Relations** — Isolated — no component may depend on it. Promotion path: `temp/` → (verified) → `knowledge/` or `01-core/`.

## 4. Summary Matrix

| Component | Loading tier | Verbosity | Core semantic boundary |
|---|---|---|---|
| `context-manifest.md` | Always | Very concise | Index & routing — not knowledge |
| `conventions.md` | Always | Concise | Context system rules & AI contract |
| `glossary.md` | Always* | Very concise | Canonical vocabulary |
| `product.md` | Always | Medium | Problem space & domain |
| `architecture.md` | Always | Medium | Solution space at system level |
| `principles.md` | Always* | Very concise | "Should" heuristics |
| `constraints.md` | Always* | Very concise | "Must" hard limits |
| `forge.config.yaml` | Always | Minimal | Engine settings |
| `layers/` | Selective | Medium / layer | Horizontal engineering discipline |
| `systems/` | Selective | Medium / unit | Vertical real implementation unit |
| `knowledge/` | Selective | Concise, append-only | Six-state knowledge ledger |
| `modes/` | Selective | Very concise | Loading delta declaration |
| `generated/` | Generated later | Adaptive concise | Non-authoritative AI derivative |
| `temp/` | Never auto | Free / disposable | Single-session scratch |

\* Always loaded when present; optional in Minimal tier.

## 5. Anti-Overlap Map

Separation lines for the most commonly confused component pairs:

| Pair | Separation line |
|---|---|
| `product.md` ↔ `architecture.md` | Problem & "why" vs solution & "how the system works" |
| `architecture.md` ↔ `layers/` ↔ `systems/` | Global vs horizontal discipline vs vertical unit |
| `principles.md` ↔ `constraints.md` | "Should" guidance vs "must" hard limits |
| `conventions.md` ↔ `principles.md` | Context system management rules vs product engineering principles |
| `conventions.md` ↔ `layers/` | Meta-context conventions vs per-discipline coding conventions |
| `glossary.md` ↔ `product.md` | One-line term definitions vs domain description |
| `context-manifest.md` ↔ `forge.config.yaml` | Content index & routing vs settings & engine toggles |
| `knowledge/inferred.md` ↔ `generated/` | Curated inference ledger entries vs raw generated artifacts |
| `generated/` ↔ `temp/` | Persistent until regenerated vs single-session scratch |
| `layers/` ↔ `modes/` | Durable discipline knowledge vs per-work-type loading lens |

## 6. Open Points

Items requiring owner decision before this contract promotes from `status: decision` to `confirmed`:

1. **Loading of this document** — Placing a verbose file in `00-meta/` conflicts with architecture invariant §8 ("`00-meta/*` always loaded"). Recommendation: load **selectively** (mode `init` & context maintenance), refine §8 to "`00-meta/*` always loaded **except** files with explicit `loading: selective`". Alternative: move to `00-meta/governance/` sub-folder excluded from always-load.
2. **Registration & validation** — When skeleton is created (Context Initialization phase), `context-content-contract.md` must be registered in `context-manifest.md` and pass architecture validation invariants §16 (valid front-matter, unique `id`, registered in manifest).
3. **Status promotion** — This document is `status: decision`; owner confirmation promotes it to `confirmed` by recording an entry in `confirmations.md` when the `knowledge/` ledger is active.
