# Context Initialization Protocol

| Field | Value |
|---|---|
| Document | Context Initialization Protocol |
| Version | 1.0 |
| Date | 2026-05-20 |
| Status | `decision` — awaiting owner confirmation |
| Language | English (context) · Bahasa Indonesia (human notes) |
| Dependency | `FORGE-CONTEXT-ARCHITECTURE.md` v0.5 · `runtime/` layer |

---

## 0. Purpose

This document defines the **process** for transforming an empty runtime skeleton into a living, useful context system when deployed to a real engineering repository.

It answers:
- What steps to execute, in what order.
- Who/what performs each step (human, AI, or hybrid).
- How brownfield (existing code) differs from greenfield (new project).
- What the exit criteria are for a successful init.

This is NOT:
- A redesign of the architecture.
- Automation code.
- A product specification.

---

## 1. Prerequisites

Before running init:

| Prerequisite | Description |
|---|---|
| Runtime copied | `runtime/` contents flattened into target repo root (CLAUDE.md, .gitignore merged, .forge/) |
| Repo access | AI/human has read access to target repo codebase |
| Owner identified | Someone can answer clarifying questions and confirm promotions |
| Scenario known | Explicitly declared: **brownfield** (existing code) or **greenfield** (new project) |

---

## 2. Initialization Phases

```
Phase 0: Setup & Configuration
Phase 1: Core Context Discovery
Phase 2: Layer Identification & Population
Phase 3: System Unit Registration
Phase 4: Knowledge Ledger Seeding
Phase 5: Manifest Finalization
Phase 6: Validation & First Commit
```

---

## 3. Phase 0 — Setup & Configuration

**Actor:** Human + AI assist

### Steps

1. Confirm scenario: `brownfield` or `greenfield`.
2. Edit `forge.config.yaml`:
   - Set `tier` (recommend `standard`).
   - Remove irrelevant entries from `layers_enabled`.
   - Set `loading.default_mode` based on immediate work type.
3. Merge `.gitignore` entries with target repo's existing `.gitignore`.
4. Verify `.forge/` structure is intact after copy.

### Exit Criteria

- `forge.config.yaml` reflects actual repo scope.
- `layers_enabled` contains only layers the repo owns.
- No broken folder structure.

---

## 4. Phase 1 — Core Context Discovery

**Actor:** Hybrid (AI proposes, human confirms)

### Goal

Populate `01-core/{product, architecture, principles, constraints}.md` with real content.

### Brownfield Flow

| Step | Action | Output |
|---|---|---|
| 1.1 | AI scans repo: README, docs, configs, code structure | Raw observations |
| 1.2 | AI drafts `product.md` content | `status: inferred`, evidence pointing to source files |
| 1.3 | AI drafts `architecture.md` content | `status: inferred`, evidence from code structure/configs |
| 1.4 | AI identifies principles from code patterns | `status: inferred` entries or `knowledge/assumptions.md` if uncertain |
| 1.5 | AI identifies constraints from configs/docs | `status: inferred` if evidenced, `assumption` if not |
| 1.6 | Human reviews & confirms/rejects each draft | Confirmed entries → `status: confirmed` + entry in `confirmations.md` |
| 1.7 | Gaps found → entries in `knowledge/unknowns.md` | AI does NOT guess |

### Greenfield Flow

| Step | Action | Output |
|---|---|---|
| 1.1 | Human provides product vision (even brief) | Input for `product.md` |
| 1.2 | AI + Human discuss architecture approach | ADR-0001 in `knowledge/decisions/` |
| 1.3 | AI drafts core files from decisions + human input | `status: assumption` (until implemented & validated) |
| 1.4 | Human confirms intent | `status: confirmed` for intent-level facts |
| 1.5 | Technical choices not yet validated → `assumptions.md` | Clear ownership assigned |

### Status Rules (Phase 1)

- Brownfield: AI-derived content starts at `inferred` (with evidence) or `assumption` (without).
- Greenfield: Human-stated intent starts at `confirmed`; technical choices at `assumption` until code validates.
- Nothing auto-promotes to `confirmed` without human action.

### Exit Criteria

- `product.md` has at minimum: product summary, domain, users, scope boundaries.
- `architecture.md` has at minimum: style, major components, key integrations.
- `principles.md` and `constraints.md` populated or explicitly marked `status: unknown` with entries in `unknowns.md` explaining why.
- All `01-core/` files have valid front-matter with correct `status`.

---

## 5. Phase 2 — Layer Identification & Population

**Actor:** Hybrid

### Goal

For each enabled layer, create `<layer>.md` with discipline-specific context.

### Steps

| Step | Action |
|---|---|
| 2.1 | For each entry in `forge.config.yaml` → `layers_enabled`: |
| 2.2 | **Brownfield:** AI scans relevant code directories (e.g., `src/`, `api/`, `tests/`, `infra/`) to extract patterns, conventions, tech choices. |
| 2.3 | **Greenfield:** AI + Human discuss intended conventions and technology choices for that layer. |
| 2.4 | AI creates `layers/<layer>/<layer>.md` sibling to README.md. |
| 2.5 | Content: conventions, patterns, tech stack, standards for this discipline. |
| 2.6 | Each fact tagged with appropriate `status` + `evidence` (brownfield) or ADR ref (greenfield). |
| 2.7 | Gaps → `knowledge/unknowns.md`. |

### Content Placement Test

Before writing any fact to a layer file, ask:
> "Is this true for ALL systems in this discipline, or only for ONE specific unit?"

- All systems → `layers/<layer>/<layer>.md` ✓
- One unit only → `systems/<unit>/system.md` (Phase 3)

### Exit Criteria

- Each enabled layer has `<layer>.md` with at least core conventions and tech choices.
- README.md preserved as-is (structural documentation).
- No duplication with `01-core/`.
- Layers not owned by this repo → folder deleted + removed from `layers_enabled`.

---

## 6. Phase 3 — System Unit Registration

**Actor:** Hybrid

### Goal

Identify and register every real implementation unit; create `system.md` for each.

### Steps

| Step | Action |
|---|---|
| 3.1 | **Brownfield:** AI scans for buildable/deployable units (services, apps, workers, libs, infra modules). Heuristics: separate `package.json`/`pom.xml`/`go.mod`, Dockerfiles, deployment configs, distinct source trees. |
| 3.2 | **Greenfield:** Human declares planned units. |
| 3.3 | For each unit, determine `system_type`: `service` · `app` · `worker` · `library` · `infra-module` · `platform-component`. |
| 3.4 | Add entry to `forge.config.yaml` → `systems[]`. |
| 3.5 | Create `systems/<name>/system.md` with front-matter. |
| 3.6 | Populate: responsibilities, public interfaces, dependencies (by `id` ref), layers touched, runtime context, unit-specific unknowns. |
| 3.7 | **Brownfield:** `status: inferred` + evidence for each fact. |
| 3.8 | **Greenfield:** `status: assumption` + ADR reference. |

### Anti-Duplication Check (Mandatory)

For every fact about to enter `system.md`, apply:
> "Is this ONLY true for this unit?"

- Yes → `systems/<unit>/system.md` ✓
- True for all units in one discipline → `layers/<layer>/`
- True globally → `01-core/`

### Single-Service vs Monorepo

- **Single-service:** exactly one folder under `systems/`.
- **Monorepo:** multiple sibling folders. Each gets its own `system.md`. Shared context stays in `01-core/` and `layers/`.

### Exit Criteria

- Every buildable unit registered in `forge.config.yaml` → `systems[]`.
- Every unit has `systems/<name>/system.md` with valid front-matter.
- No inter-unit content duplication.
- Dependencies between units expressed as `id` references.

---

## 7. Phase 4 — Knowledge Ledger Seeding

**Actor:** AI (with human review)

### Goal

Populate initial entries in all four knowledge ledgers from discoveries during Phases 1–3.

### Steps

| Step | Ledger | Source |
|---|---|---|
| 4.1 | `knowledge/unknowns.md` | All gaps found during Phases 1–3 |
| 4.2 | `knowledge/assumptions.md` | All unverified beliefs used during init |
| 4.3 | `knowledge/inferred.md` | All AI-derived facts with evidence |
| 4.4 | `knowledge/decisions/ADR-0001-*.md` | Key architectural decisions made during init |
| 4.5 | `knowledge/confirmations.md` | All human confirmations performed so far |

### Rules

- Every entry has: ID, owner, created date, status.
- `inferred` entries must have `evidence`.
- `unknowns` must NOT be guessed — they stay open until resolved.
- ADR numbering starts at `0001` (template is `0000`).

### Exit Criteria

- No unresolved discoveries left unrecorded.
- Every `inferred` fact in `01-core/`/`layers/`/`systems/` has corresponding entry in `inferred.md`.
- Every confirmation has entry in `confirmations.md`.
- At least one ADR exists (ADR-0001: adoption of forge-context-engine architecture).

---

## 8. Phase 5 — Manifest Finalization

**Actor:** AI (human reviews)

### Goal

Complete `00-meta/context-manifest.md` File Registry with all files created during init.

### Steps

| Step | Action |
|---|---|
| 5.1 | Enumerate all `.md` files under `.forge/context/` |
| 5.2 | For each file, record: `path | id | type | status | owner` |
| 5.3 | Verify all `id` values are unique |
| 5.4 | Verify loading tier assignments match conventions |
| 5.5 | Update `glossary.md` with domain terms discovered during init |

### Exit Criteria

- File Registry is complete and matches actual filesystem.
- Every file in `.forge/context/` is registered.
- No duplicate `id`.

---

## 9. Phase 6 — Validation & First Commit

**Actor:** Human + AI

### Validation Checklist

```
[ ] Every file has valid YAML front-matter
[ ] Every file registered in context-manifest.md
[ ] Every id is unique across all files
[ ] confirmed/inferred files have evidence
[ ] source: human files have no AI-written content
[ ] modes/* do not list 00-meta/* or 01-core/*
[ ] systems/* do not copy 01-core/ or layers/* content
[ ] No file exceeds size budget
[ ] forge.config.yaml systems[] matches actual systems/ folders
[ ] forge.config.yaml layers_enabled matches actual layers/ folders
[ ] temp/ is gitignored
[ ] At least ADR-0001 exists
```

### First Commit

```
git add .forge/ CLAUDE.md
git commit -m "forge: context initialization complete"
```

> Catatan: Jangan commit `.forge/context/temp/` — sudah di-gitignore.

### Exit Criteria

- All validation checks pass.
- Clean git status (no untracked context files).
- System ready for normal operation (AI can bootstrap using CLAUDE.md → forge.config.yaml → 00-meta → 01-core → mode).

---

## 10. Brownfield vs Greenfield — Summary Matrix

| Aspect | Brownfield | Greenfield |
|---|---|---|
| Primary input | Existing codebase | Human intent + decisions |
| Initial status | `inferred` (with evidence) | `assumption` (with ADR) |
| Discovery method | Code scan + doc scan | Conversation + ADR creation |
| Unknowns | Gaps in understanding existing system | Gaps in planned design |
| Path to confirmed | Evidence → human verification | Implementation validates assumption |
| First ADR | ADR-0001: forge-context adoption | ADR-0001: architecture decision |
| Risk | Stale/wrong inference | Premature assumption |
| Mitigation | Evidence-linked, staleness governance | ADR-linked, validate-on-implement |

---

## 11. Question Protocol

During init, AI must gather information. This is the priority order:

### Priority 1 — Blocking (Must Have Before Proceeding)

- What is the product/domain?
- Brownfield or greenfield?
- What are the buildable units?
- Who owns this repo?

### Priority 2 — Important (Needed for Quality Init)

- Architecture style?
- Key external integrations?
- Hard constraints (compliance, performance, platform)?
- Testing strategy?
- Active layers (which engineering disciplines does this repo own)?

### Priority 3 — Nice to Have (Can Be Unknown)

- Engineering principles (can be inferred later).
- Detailed conventions per layer (can grow incrementally).
- Glossary terms (grows over time).
- Non-critical unknowns (logged for future resolution).

### Rules for Asking

- Batch questions by priority level. Do not overwhelm with all questions at once.
- If codebase provides the answer, do NOT ask the human — infer and record with evidence.
- If unsure, record as `unknown`. Never fabricate.
- Brownfield: prefer code evidence over asking human.
- Greenfield: prefer human statement over guessing.

---

## 12. Error Handling

| Situation | Action |
|---|---|
| Owner unavailable for confirmation | Record as `inferred`/`assumption`; do NOT promote to `confirmed`. Continue init. |
| Conflicting signals in codebase | Record both in `unknowns.md` with evidence for each. Do not resolve by guessing. |
| Unit type unclear | Default to most conservative type; record ambiguity in `unknowns.md`. |
| Layer ownership unclear | Keep layer enabled; record gap in `unknowns.md`. |
| Size budget exceeded during init | Split file immediately. Do not defer. |
| No evidence found for a claim | Demote to `assumption`. Never infer without evidence. |

---

## 13. Post-Init Operations

After successful initialization:

| Operation | When | How |
|---|---|---|
| Incremental updates | During development | AI proposes → human confirms → update context file |
| Staleness check | After `governance.staleness_days` | Re-verify `evidence` paths; demote stale entries |
| New unit added | When new service/app created | Run Phase 3 steps for that unit only |
| New layer activated | When new discipline enters scope | Run Phase 2 steps for that layer only |
| Promote assumption | When implementation validates it | Add evidence → promote to `inferred` → human confirms → `confirmed` + entry in `confirmations.md` |
| Resolve unknown | When answer is found | Move to correct semantic location + mark unknown `resolved` |

---

## 14. Init Duration Estimate

| Repo Complexity | Estimated Effort | Phases |
|---|---|---|
| Single-service, small codebase | 30–60 min | All 6 phases |
| Single-service, medium codebase | 1–2 hours | All 6 phases |
| Monorepo, 3–5 units | 2–4 hours | All 6 phases |
| Monorepo, 10+ units | 4–8 hours (batch by unit group) | Phases 0–1 once; Phases 2–5 per batch |

> Catatan: Ini estimasi untuk kolaborasi manusia-AI. Automation akan memangkas durasi ini secara signifikan di fase tooling mendatang.

---

## 15. Relationship to Future Tooling

This protocol is designed to be **automatable**. Future `forge init` CLI will:

1. Execute Phase 0 interactively (ask config questions).
2. Execute Phases 1–3 using codebase analysis (AST, dependency graph, config detection).
3. Execute Phase 4 automatically from discoveries.
4. Execute Phase 5 by filesystem enumeration.
5. Execute Phase 6 validation programmatically.

The protocol defined here is the **specification** that future tooling must implement. Manual execution today validates the protocol's correctness.

---

## Appendix A — Init Sequence Diagram

```
Human                          AI                           Files
  │                             │                             │
  ├──── declare scenario ──────►│                             │
  │                             ├──── scan codebase ─────────►│
  │                             │◄──── raw observations ──────┤
  │                             │                             │
  │◄──── Phase 1 drafts ───────┤                             │
  ├──── confirm/reject ────────►│                             │
  │                             ├──── write 01-core/* ────────►│
  │                             ├──── write unknowns ─────────►│
  │                             │                             │
  │                             ├──── Phase 2: scan layers ──►│
  │◄──── layer proposals ──────┤                             │
  ├──── confirm/adjust ────────►│                             │
  │                             ├──── write layers/<x>.md ───►│
  │                             │                             │
  │                             ├──── Phase 3: detect units ─►│
  │◄──── system proposals ─────┤                             │
  ├──── confirm ───────────────►│                             │
  │                             ├──── write systems/*  ───────►│
  │                             │                             │
  │                             ├──── Phase 4: seed ledgers ─►│
  │                             ├──── Phase 5: finalize ─────►│
  │                             │                             │
  │◄──── validation report ────┤                             │
  ├──── approve & commit ──────►│                             │
  │                             │                             │
```

---

## Appendix B — Checklist for AI Agent (Quick Reference)

```
INIT CHECKLIST — AI Agent Quick Reference

□ Scenario confirmed (brownfield/greenfield)
□ forge.config.yaml configured
□ 01-core/product.md populated (status tagged)
□ 01-core/architecture.md populated (status tagged)
□ 01-core/principles.md populated or unknown-logged
□ 01-core/constraints.md populated or unknown-logged
□ layers/ — irrelevant folders removed
□ layers/ — <layer>.md created for each enabled layer
□ systems/ — all units registered in config
□ systems/ — system.md created for each unit
□ knowledge/unknowns.md — all gaps recorded
□ knowledge/assumptions.md — all unverified beliefs recorded
□ knowledge/inferred.md — all AI inferences recorded with evidence
□ knowledge/decisions/ADR-0001 — architecture adoption recorded
□ knowledge/confirmations.md — all human confirmations logged
□ 00-meta/context-manifest.md — file registry complete
□ 00-meta/glossary.md — domain terms added
□ Validation checklist passes (§9)
□ First commit made
```
