# Context Initialization Protocol

| Field | Value |
|---|---|
| Document | Context Initialization Protocol |
| Version | 1.2 |
| Date | 2026-05-20 |
| Status | `decision` — finalized for forge-context-engine v0.2.1 |
| Language | English (context) · Bahasa Indonesia (human notes) |
| Dependency | `FORGE-CONTEXT-ARCHITECTURE.md` v0.5 · `runtime/` layer · `specs/context-validation.md` v1.2 |

> **v1.1 → v1.2 changes:** Added evidence consistency sweep, implicit constraint extraction, validation layer attribution, generated code policy check to Phase 1; drift refresh guidance to Phase 6; refined infrastructure activation criteria. Aligned with `forge-context-engine` v0.2.1 patch.

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
Phase 0:    Setup & Configuration
Phase 0.5:  Legacy AI Context Discovery       ← NEW (operational feedback v1.1)
Phase 1:    Core Context Discovery
Phase 2:    Layer Identification & Population
Phase 3:    System Unit Registration
Phase 4:    Knowledge Ledger Seeding
Phase 5:    Manifest Finalization
Phase 6:    Validation & First Commit
Phase 7:    Human Confirmation Pass            ← NEW (operational feedback v1.1)
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
5. **Declare dominant context language** *(v1.2)* — pick one based on (in order): existing repo docs language, team convention, legacy `.ai/` content, dominant commit language. Record in `00-meta/conventions.md` if it differs from the runtime default. Apply consistently from this phase onward.

### Exit Criteria

- `forge.config.yaml` reflects actual repo scope.
- `layers_enabled` contains only layers the repo owns.
- No broken folder structure.
- Dominant context language declared.

---

## 4. Phase 0.5 — Legacy AI Context Discovery

**Actor:** Hybrid (AI scans, human classifies on conflict)

### Goal

Discover and classify pre-existing AI/context artifacts before populating new context. Real repos often contain `.ai/`, `.claude/`, `.cursor/`, `AGENTS.md`, or ad-hoc architecture docs. These accelerate init when used correctly — and corrupt it when blindly trusted.

### Discovery Targets

Scan target repo for:

- `.ai/`, `.claude/`, `.cursor/`, `.github/copilot/`, `.aider/`
- `AGENTS.md`, `CLAUDE.md` (existing), `CONTEXT.md`, `ARCHITECTURE.md` at root
- `docs/`, `architecture/`, `adr/`, `decisions/` folders
- README sections that describe architecture, conventions, decisions
- `*.context.md`, `*.ai.md` patterns

### Classification

Each discovered artifact gets one classification:

| Class | Meaning | Treatment |
|---|---|---|
| `authoritative` | Owned, current, validated by team | Reference as evidence; promote facts to correct zone with `source: hybrid` |
| `useful-reference` | Likely accurate but not formally validated | Use to seed `inferred` entries; cite as evidence |
| `outdated` | Predates significant changes; contradicts code | Record contradiction in `unknowns.md`; do NOT use as evidence |
| `unknown-authority` | Origin/freshness unclear | Default to `useful-reference` until confirmed; add unknown entry |

### Operating Rules

1. **Repo code wins on conflict.** If legacy doc says X but code shows Y, code is truth.
2. **Never copy verbatim** into `01-core/`/`layers/`/`systems/`. Re-express with proper `status` + `evidence`.
3. **Conflicts → `unknowns.md`** with priority `important` (or `blocking` for security/data integrity).
4. **Cite legacy as evidence** with `evidence: [{ type: doc, ref: .ai/architecture.md }]` when content is reused.
5. Legacy artifacts may **stay in place** during transition. They are reference, not source-of-truth.

### Output

A discovery summary added to `knowledge/inferred.md` listing each legacy artifact and its classification. Used as input for Phases 1–3.

### Exit Criteria

- All legacy AI artifacts identified and classified.
- Conflicts with code recorded as unknowns.
- AI is aware of which legacy content to lean on (vs ignore) during downstream phases.

---

## 5. Phase 1 — Core Context Discovery

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

### Evidence Consistency Sweep *(v1.2)*

Before exiting Phase 1, AI runs a cross-check pass:

| Area | Verify against |
|---|---|
| Database tables | `migrations/*` files / schema dumps |
| Migrations | Filenames, sequence, content |
| Entities/models | Domain layer files / ORM models |
| Repositories | Repository implementation files |
| APIs / handlers / RPCs | Proto files, route registration |
| Background workers | Worker entrypoints, schedulers |
| External integrations | Client libs, dep manifests, integration configs |
| Validation rules / implicit constraints | Validators, sentinels, enum constraints, required fields, ID semantics, currency rules |
| Generated code policies | `gen/` directory + commit history (regenerate-only vs always-commit) |

If a context claim does not match the repo (e.g. "3 tables" vs 4 migrations), correct the context. Log root-cause ambiguity in `unknowns.md`.

### Table Role Classification *(precision patch)*

For each database table discovered, determine its runtime role before writing context:

| Question | If yes → role |
|---|---|
| Written by application code during normal request/event processing? | `operational-write` |
| Written together with other tables inside one transaction boundary? | `transactional-write` |
| Read at runtime but never written by application code? | `read-only-runtime` or `lookup/reference` |
| Populated only by migration scripts (`INSERT` in `*.up.sql`, no runtime write)? | `migration-seeded` |
| Created by framework/ORM/tooling, not owned by application? | `generated/internal` |
| Cannot determine from available evidence? | `unknown` → `unknowns.md` |

State each table's role explicitly in `architecture.md` and `system.md`. Never describe migration-seeded or lookup tables as part of runtime write flows or transaction boundaries.

### Validation Layer Attribution *(v1.2 patch)*

When documenting field constraints, attribute each to the layer that enforces it. Never flatten different validation realities into one "required" list.

| Layer | Source |
|---|---|
| Service | `internal/service/*` empty-checks, `sanitize*Input` |
| Handler / API | `internal/handler/*` validators, OpenAPI/proto annotations |
| Database | `migrations/*` `NOT NULL`, `CHECK`, `UNIQUE`, FK |
| Repository | `internal/repository/*` defaults, fallbacks (`IsZero() → now`) |
| Business intent | ADRs, `01-core/product.md` |

A field can be DB-constrained but not service-required. Document both facts; do not collapse them.

### Implicit Constraint Extraction *(v1.2)*

While reading code, harvest implicit rules and route them:

| Source pattern | Destination |
|---|---|
| Global hard rule (compliance, platform-wide) | `01-core/constraints.md` |
| Single-unit rule | `systems/<unit>/system.md` |
| Unclear meaning | `knowledge/unknowns.md` |
| Weak inference | `knowledge/inferred.md` |

### Phantom ADR Guard *(v1.2)*

`architecture.md` must NOT cite ADR-NNNN entries that do not exist as files. If only ADR-0001 exists, only ADR-0001 may appear with `evidence: { type: adr, ... }`. Planned/anticipated ADRs go to `assumptions.md` with priority `important` or `unknowns.md` — never to `architecture.md` body as evidence.

### Exit Criteria

- `product.md` has at minimum: product summary, domain, users, scope boundaries.
- `architecture.md` has at minimum: style, major components, key integrations.
- `principles.md` and `constraints.md` populated or explicitly marked `status: unknown` with entries in `unknowns.md` explaining why.
- All `01-core/` files have valid front-matter with correct `status`.
- Evidence consistency sweep complete; mismatches corrected or logged.
- Implicit constraints harvested and routed.
- **Validation layer attribution present** for every constraint entry (which layer enforces it).
- No phantom ADR references.

---

## 6. Phase 2 — Layer Identification & Population

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

## 7. Phase 3 — System Unit Registration

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

## 8. Phase 4 — Knowledge Ledger Seeding

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

- Every entry has: ID, owner, created date, status, **priority**.
- Unknown priority levels: `blocking` · `important` · `informational`.
- `inferred` entries must have `evidence`.
- `unknowns` must NOT be guessed — they stay open until resolved.
- ADR numbering starts at `0001` (template is `0000`).
- If repo owner is not yet identified, create a **single** root unknown `U-OWN` rather than spreading `owner: TBD` across files.

### Exit Criteria

- No unresolved discoveries left unrecorded.
- Every `inferred` fact in `01-core/`/`layers/`/`systems/` has corresponding entry in `inferred.md`.
- Every confirmation has entry in `confirmations.md`.
- At least one ADR exists (ADR-0001: adoption of forge-context-engine architecture).

---

## 9. Phase 5 — Manifest Finalization

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

## 10. Phase 6 — Validation & First Commit

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
[ ] (v1.2) Evidence consistency: table/migration/entity/api counts match repo
[ ] (v1.2) No phantom ADR references in architecture.md
[ ] (v1.2) No internal `TBD` table cells (use `unresolved`)
[ ] (v1.2) Producer/source-system list canonical in product.md
[ ] (v1.2) Layer activation matches evidence (no infrastructure without IaC/deploy)
```

> Full rule list with severity & automatability: `specs/context-validation.md` (Categories A–K).

### First Commit

```
git add .forge/ CLAUDE.md
git commit -m "forge: context initialization complete"
```

> Note: Do not commit `.forge/context/temp/` — already gitignored.

### Exit Criteria

- All validation checks pass.
- Clean git status (no untracked context files).
- System ready for normal operation (AI can bootstrap using CLAUDE.md → forge.config.yaml → 00-meta → 01-core → mode).

---

## 11. Phase 7 — Human Confirmation Pass

**Actor:** Human (AI prepares the summary)

### Goal

Surface critical inferred knowledge and high-priority unknowns to the human owner for explicit confirmation. Without this pass, `inferred` content can drift indefinitely without ever being promoted or rejected.

### Steps

| Step | Action |
|---|---|
| 7.1 | AI generates a confirmation summary (max ~30 items) |
| 7.2 | Summary groups items into: **critical inferred** (high-confidence facts ready to promote), **blocking unknowns**, **important unknowns** |
| 7.3 | Human reviews each item: confirm / reject / defer |
| 7.4 | Confirmed items → `status: confirmed` + entry in `knowledge/confirmations.md` |
| 7.5 | Rejected items → demote to `assumption` or move to `unknowns.md` |
| 7.6 | Deferred items → stay `inferred` with `review_by` date set |

### Confirmation Summary Format

```
=== CONFIRMATION REQUEST ===

CRITICAL INFERRED (recommend promote → confirmed):
  [I-002] Framework-first runtime via go-core
          Evidence: go.mod replace + .ai/decisions.md
          → Confirm? (y/n/defer)

  [I-007] DB tables: transaction_histories, ...
          Evidence: migrations/transaction/0001_init...
          → Confirm? (y/n/defer)

BLOCKING UNKNOWNS (must resolve before next implementation work):
  [U-007] Compliance regime — PII/retention/audit?
  [U-006] SLA / performance targets?

IMPORTANT UNKNOWNS:
  [U-002] Does this repo own deployment manifests?
  [U-008] Cursor pagination roadmap?
```

### Rules

- Do NOT request confirmation for trivial inferences (low-noise rule).
- Cap summary at ~30 items per session — split across multiple passes if needed.
- AI never promotes without explicit `y` from human.
- Deferred items automatically resurface when `review_by` date arrives.

### Exit Criteria

- Critical inferences explicitly confirmed or rejected.
- Blocking unknowns have an action plan or owner assigned.
- `confirmations.md` reflects all promotions performed in this pass.

---

## 12. Operational Rule — Ownership Handling

`owner: TBD` is **deprecated** as a value (creates noise across many files).

### Rules

| Situation | Action |
|---|---|
| Owner known at init | Set on every file as canonical team/individual reference |
| Owner unknown at init | Use `owner: unresolved` and create **one** root unknown entry (`U-OWN`) in `unknowns.md` |
| Multiple ownership | Use a short ref token (e.g. `team.payments`) and define it once in `glossary.md` |
| Ownership changes | Update files in batch; record reason in `confirmations.md` |

### Anti-Pattern

Repeating `owner: TBD` across 20 files = 20 noise points. Repeating `owner: unresolved` references **one** unknown = 1 actionable item.

---

## 13. Operational Rule — Layer Activation

A layer is **activated** only when concrete evidence exists. See `00-meta/conventions.md` → "Layer Activation Rule" for the canonical evidence table.

### Decision Flow

```
Evidence strong?  → Activate, confidence: high
Evidence partial? → Activate, confidence: medium/low + add unknowns
Evidence absent?  → Delete folder + remove from layers_enabled
```

### Common Trap

Service repos often delegate deployment to a separate repo. Activating `infrastructure` based on the *presence of a Dockerfile* alone is too aggressive — Dockerfiles often serve only local dev. Look for **deployment-binding** evidence:
- Helm / Terraform / K8s manifests
- CI/CD deploy steps (not just test/build)
- Cloud-resource configs (cluster definitions, infra modules)

If only Dockerfile + Makefile exist, infrastructure layer = `confidence: medium` with explicit unknowns about deployment ownership.

---

## 14. Brownfield vs Greenfield — Summary Matrix

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

## 15. Question Protocol

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

## 16. Error Handling

| Situation | Action |
|---|---|
| Owner unavailable for confirmation | Record as `inferred`/`assumption`; do NOT promote to `confirmed`. Continue init. |
| Conflicting signals in codebase | Record both in `unknowns.md` with evidence for each. Do not resolve by guessing. |
| Unit type unclear | Default to most conservative type; record ambiguity in `unknowns.md`. |
| Layer ownership unclear | Keep layer enabled; record gap in `unknowns.md`. |
| Size budget exceeded during init | Split file immediately. Do not defer. |
| No evidence found for a claim | Demote to `assumption`. Never infer without evidence. |

---

## 17. Post-Init Operations

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

## 18. Init Duration Estimate

| Repo Complexity | Estimated Effort | Phases |
|---|---|---|
| Single-service, small codebase | 30–60 min | All 6 phases |
| Single-service, medium codebase | 1–2 hours | All 6 phases |
| Monorepo, 3–5 units | 2–4 hours | All 6 phases |
| Monorepo, 10+ units | 4–8 hours (batch by unit group) | Phases 0–1 once; Phases 2–5 per batch |

> Note: This is an estimate for human-AI collaboration. Automation will significantly reduce these durations in future tooling phases.

---

## 19. Relationship to Future Tooling

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

PHASE 0.5 — LEGACY DISCOVERY
□ Legacy AI artifacts scanned (.ai/, .claude/, AGENTS.md, etc.)
□ Each artifact classified (authoritative/useful-reference/outdated/unknown-authority)
□ Conflicts with code recorded as unknowns

PHASE 1–3 — POPULATION
□ 01-core/product.md populated (status tagged)
□ 01-core/architecture.md populated (status tagged)
□ 01-core/principles.md populated or unknown-logged
□ 01-core/constraints.md populated or unknown-logged
□ layers/ — irrelevant folders removed (per Layer Activation Rule §13)
□ layers/ — <layer>.md created for each enabled layer
□ layers/ — README.md kept lightweight (TOC only, no content duplication)
□ systems/ — all units registered in config
□ systems/ — system.md created for each unit

PHASE 4 — KNOWLEDGE LEDGERS
□ knowledge/unknowns.md — all gaps recorded with priority (blocking/important/informational)
□ knowledge/assumptions.md — all unverified beliefs recorded
□ knowledge/inferred.md — all AI inferences recorded with evidence
□ knowledge/decisions/ADR-0001 — architecture adoption recorded
□ knowledge/confirmations.md — all human confirmations logged
□ Owner handling: single U-OWN if owner unresolved (no spread of owner: TBD)

PHASE 5–6 — FINALIZATION
□ 00-meta/context-manifest.md — file registry complete
□ 00-meta/glossary.md — domain terms added
□ Validation checklist passes (specs/context-validation.md)
□ First commit made

PHASE 7 — CONFIRMATION PASS
□ Confirmation summary presented to human
□ Critical inferences confirmed/rejected/deferred
□ Blocking unknowns assigned owners
□ confirmations.md updated with promotions
```


---

## Appendix C — Operational Recommendations (After First Real-World Validation)

Distilled from initialization on `transaction-history-service` (2026-05-20). These are operational defaults — not architectural changes.

### What Worked Well

- Existing `.ai/` artifacts dramatically accelerated Phase 1–3 when treated as evidence, not authority.
- `inferred + evidence` workflow produced high-quality drafts on first pass.
- Single-service Standard tier scaled well for a focused Go service.
- Anti-hallucination rules held: every claim was either evidenced or routed to `unknowns.md`.

### Behaviors to Default On

1. **Always run Phase 0.5** (legacy artifact discovery) before Phase 1 on brownfield repos.
2. **Conditional layer activation** — never auto-include layers without evidence.
3. **Single-root unknown for ownership** — never spread `owner: TBD` across files.
4. **Priority on every unknown entry** — blocking/important/informational.
5. **Phase 7 confirmation pass** before declaring init complete.
6. **README = TOC only** — content lives in `<layer>.md`.

### Behaviors to Avoid

- Verbatim copying from legacy `.ai/` to new `01-core/` (use as evidence, not source).
- Activating `infrastructure` layer just because Dockerfile exists.
- Treating high inference volume as a sign of completeness — without confirmation pass, nothing has actually been validated.
- Inflating `01-core/*` files beyond size budget to capture every detail (split or push detail to `layers/`).

### Token Efficiency Guardrails

These improvements MUST preserve runtime lightweight behavior:

| Concern | Default |
|---|---|
| README size | Stays small — TOC + activation rule only |
| Confirmation summary cap | ~30 items per pass |
| Unknown growth | Bounded by priority filtering during planning mode |
| Legacy reference | Never inlined into core context |
| Generated artifacts | Default gitignored; commit only when reproducibly useful |

### When to Re-Run Phases

| Trigger | Re-run |
|---|---|
| New unit added | Phase 3 + Phase 5 (manifest update) |
| New layer needed | Phase 2 + Phase 5 |
| Major refactor | Phase 1 (re-verify core) + Phase 7 (re-confirm) |
| Ownership change | Phase 4 (update ledgers) + Phase 5 |
| Quarterly review | Phase 7 (confirmation pass on stale `inferred`) |

### Final Note

The framework's value comes from **discipline**, not volume. A 25-file context with confirmed core + acknowledged unknowns beats a 60-file context full of unverified `inferred` entries. Resist the urge to "fill everything in" during init — leave gaps explicit.
