# Validation Specification

| Field | Value |
|---|---|
| Document | Context System Validation Specification |
| Version | 3.7 |
| Date | 2026-05-28 |
| Status | `decision` — finalized for forge-context-engine v0.3.1 |
| Language | English (context) · Bahasa Indonesia (human notes) |
| Dependency | `FORGE-CONTEXT-ARCHITECTURE.md` v0.8 §16 · `specs/mode-invocation.md` v3.2 · `specs/artifact-lifecycle.md` v1.0 |

> **v2.5 -> v2.6 changes:** Human UX refinement for mode outputs: concise operational wording, quieter runtime internals, clearer confirmation prompts, grouped file-change reporting, and execute reports focused on result/validation/rollback. No lifecycle redesign, tooling, automation, runtime executors, orchestration, or new folders.
> **v2.6 -> v2.7 changes:** Implementation readiness now requires deterministic task cards for `READY_FOR_EXECUTION` and `READY_FOR_PARTIAL_EXECUTION`, with explicit dependencies, guardrails, acceptance criteria, validation expectations, and blocker gates. No tooling, orchestration, agents, schedulers, workflow engines, DAGs, Jira integration, or story points.
> **v2.7 -> v2.8 changes:** Execute reports require explicit result status, responsibility-grouped files, visible validation failures, operational rollback, unchanged-boundary reporting, reviewer focus, hidden-change checks, and quiet internals. No lifecycle redesign, tooling, orchestration, agents, deploy workflow, or runtime executor changes.
> **v2.8 -> v2.9 changes:** Runtime validation now requires prerequisite checks, standardized execute/testing/review statuses, formal partial/blocking/not-validated semantics, separated validation reporting, explicit manual actions, and invalid-output rules for hidden success. No orchestration, deploy workflow, CI pipeline logic, agents, or workflow engines.
> **v2.9 -> v3.0 historical note:** Earlier validation work added structured testing sections, scope categories, contract-aware validation, runtime-sensitive retry/DLQ/idempotency coverage, manual vs automated separation, and reviewer-visible coverage gaps. In the current lifecycle, validation is an activity inside execute/review workflows, not a core lifecycle mode.
> **v3.0 -> v3.1 changes:** Review mode now requires MR-oriented result/readiness semantics, severity-grouped evidence-based findings, architecture/contract and safety checks, reviewer focus, and invalid-output rules for generic audit/test-plan/task-list drift. No lifecycle redesign, tooling, orchestration, deploy workflow, agents, CI/CD, or runtime executors.
> **v3.1 -> v3.2 changes:** Consolidates status vocabulary, section names, and mode-boundary validation so implementation, execute, testing, and review use one operational language. Removes legacy review-needed blocking language. No lifecycle redesign, new modes, tooling, orchestration, agents, deploy workflow, CI/CD, workflow engines, or runtime executors.
> **v3.2 -> v3.3 historical note:** Earlier artifact validation used Execution Contract and Testing Result names. In the current lifecycle, implementation produces ECP and validation is inside execute/review workflows. No orchestration, agents, workflow engines, DAG systems, CI/CD, deploy workflow, runtime executors, persistent AI memory, or knowledge graphs.
> **v3.3 -> v3.4 changes:** Adds bounded runtime profile, decision authority, decision risk, `NEEDS_HUMAN_APPROVAL`, and automation-safe decision trace validation. No agents, orchestration, workflow engines, DAG systems, schedulers, triggers, CI/CD behavior, deploy workflow, runtime executors, or autonomous loops.
> **v3.4 -> v3.5 changes:** Adds future-safe intelligence and governance validation for scoped loading, `CONTEXT_BUDGET_LIMITED`, drift, cross-repo awareness, incident/refactor cause/risk semantics, and fintech-grade governance signals. No tooling, RAG, vector DB, knowledge graph, orchestration, agents, deploy workflow, CI/CD behavior, runtime executors, or autonomous loops.
> **v3.5 -> v3.6 changes:** Adds thin-adapter validation rules so root adapters reference Forge core instead of duplicating cognition, lifecycle, validation, drift, artifact, governance, or secret semantics. No orchestration, memory, agent, runtime executor, deploy, CI/CD, or workflow behavior added.
> **v3.6 -> v3.7 changes:** Adds execute hardening validation for minimal diffs, finalization checks, contract-source checks, review-loop closure, and concise recommended next action. No lifecycle redesign, modes, orchestration, memory, agents, runtime executors, deploy, CI/CD, or autonomous chaining added.

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
| `critical` | Security exposure or irreversible safety violation. | Stop, redact, rotate if exposed, and fix before any report or commit. |
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
| B2 | Front-matter contains required fields: `id`, `title`, `type`, `status`, `confidence`, `source`, `owner`, `updated`; curated context cards also include `source_paths`, `source_commit`, and `last_verified` or an explicit compatibility exception | error | yes |
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
| F9 | `modes/*.md` files remain context loading deltas with concise operational notes, not domain knowledge or prose-only narratives | warning | partial |
| F10 | `modes/*.md` `## token_budget` contains only a decimal integer; labels such as `medium` or `medium-high` are invalid | error | yes |
| F11 | Plan mode uses Quick Plan or SDD terminology and rejects generic PRD/business prose | warning | manual |
| F12 | Plan mode is layer-adaptive and does not force backend-specific sections when active layer evidence is non-backend or mixed | warning | manual |
| F13 | Plan mode preserves evidence/inference/unknown separation and does not infer deployability, ownership, contracts, or runtime topology from imports alone | warning | manual |
| F14 | Plan mode on-demand loading is scoped to the requested change and does not broadly load unrelated layers/systems by default | warning | manual |
| F15 | Mode invocation reads `.forge/forge.config.yaml` before `.forge/context/modes/<mode>.md` | warning | manual |
| F16 | Mode invocation keeps context-loading details concise in normal output and reports missing evidence that affects the task | warning | manual |
| F17 | Mode invocation does not broad-load `.forge/context` by default when the mode delta is sufficient | warning | manual |
| F18 | Init, ask, plan, implementation, execute, review, and verify-context preserve distinct operational behavior instead of collapsing into generic reasoning | warning | manual |
| F19 | Mode invocation reports unresolved ambiguity and only highlights mode insufficiency when it affects the task | warning | manual |
| F20 | Mode-specific execution behavior lives in `modes/<mode>.md` rather than being duplicated in globally loaded `00-meta/conventions.md` | warning | manual |
| F21 | Unknown handling distinguishes `blocking`, `proposed-default`, and `informational` behavior | warning | manual |
| F22 | Proposed defaults are explicitly labeled `proposed` and `not confirmed`, with reason and confirmation boundary when needed | warning | manual |
| F23 | `run.interaction: auto` emits required decisions or blocking status instead of conversational questions | warning | manual |
| F24 | `run.interaction: manual` remains interactive-first and uses ask-first clarification for blocking decisions | warning | manual |
| F25 | Plan output discourages excessive architecture-option generation and open-ended brainstorming | warning | manual |
| F26 | Proposed defaults do not silently become confirmed facts, topology, ownership, contracts, or production runtime behavior | warning | manual |
| F27 | Visible core modes are constrained to `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context` | warning | manual |
| F28 | Plan mode produces Quick Plan or SDD and does not collapse into detailed executable coding tasks | warning | manual |
| F29 | Implementation mode produces an ECP only after critical blockers are resolved, without modifying code | warning | manual |
| F30 | Execute mode owns actual repository modification behavior and reports modified files grouped by responsibility | warning | manual |
| F31 | Execute mode does not silently redefine approved plans, topology, contracts, or architecture | warning | manual |
| F32 | Architecture reasoning and execution reasoning remain separated by a human-reviewable execution boundary | warning | manual |
| F33 | Validation activity remains evidence-based inside execute/review workflows and does not become a separate core mode | warning | manual |
| F34 | Execute mode reports scoped validation without replacing review | warning | manual |
| F35 | Review mode checks validation evidence and gaps without becoming execution | warning | manual |
| F36 | Mode responsibilities remain separated across init, ask, plan, implementation, execute, review, and verify-context | warning | manual |
| F37 | Test placement respects existing repository conventions and does not force the recommended `testing/` layout without evidence | warning | manual |
| F38 | Unit tests are not placed far from the target package/file without a repository convention or explicit reason | warning | manual |
| F39 | Integration/e2e tests are not mixed into unit test folders without a repository convention or explicit reason | warning | manual |
| F40 | Reusable mocks, fakes, stubs, fixtures, and helpers are not scattered without a clear repository convention | warning | manual |
| F41 | Human decision prompts are bounded: recommended plus alternative by default, maximum three options for major architecture tradeoffs | warning | manual |
| F42 | `run.interaction` is detected and applied during every mode invocation without requiring prompt mention; normal output does not dump runtime internals | warning | manual |
| F43 | Interactive repositories do not emit automation-style blocked reports when ask-first clarification is required | warning | manual |
| F44 | Non-interactive repositories do not ask conversational clarification questions | warning | manual |
| F45 | Interactive implementation mode stops before final breakdown when blocking decisions affect runtime behavior, contracts/schema, DLQ/replay, idempotency, security/compliance, ownership/governance, destructive boundaries, acceptance criteria, or rollback | warning | manual |
| F46 | Interactive implementation mode asks concise Recommended/Alternative clarification questions before execution-ready tasks | warning | manual |
| F47 | Interactive implementation mode does not hide blockers at the end of a full breakdown | warning | manual |
| F48 | Final executable tasks, allowed file modifications, acceptance criteria, and executor instructions are not emitted while critical blockers remain unresolved | warning | manual |
| F49 | Non-interactive implementation mode emits `NEEDS_CONFIRMATION` when required execution values are missing, `NEEDS_HUMAN_APPROVAL` for HIGH-risk decisions, or `READY_FOR_PARTIAL_EXECUTION` only when safe proposed-default work can proceed | warning | manual |
| F50 | Interactive implementation confirmation starts with `NEEDS_CONFIRMATION` | warning | manual |
| F51 | Interactive implementation confirmation includes blocker title, practical why-it-matters explanation, Recommended option with reason, Alternative option with tradeoff, and clear reply instructions | warning | manual |
| F52 | Interactive implementation confirmation uses 2 options by default and at most 3 only for major architecture tradeoffs | warning | manual |
| F53 | Implementation output includes exactly one readiness status: `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, or `READY_FOR_EXECUTION` | warning | manual |
| F54 | `READY_FOR_EXECUTION` is not used with conditional language such as assumed values, values provided later, unknown topics/schema/groups/DLQ, unknown duplicate policy, missing contract details, or pending production confirmation | error | manual |
| F55 | Execution-sensitive `READY_FOR_EXECUTION` output includes concrete execution values before executor instructions | error | manual |
| F56 | Final executor instructions do not contain unresolved required execution values | error | manual |
| F57 | Ask mode answers lightweight repo-understanding questions without planning, mutation, redesign, or broad audit | warning | manual |
| F58 | Incident scenarios diagnose bugs/issues/incidents without speculative redesign | warning | manual |
| F59 | Refactor scenarios remain bounded, conservative, and behavior-preserving without architecture rewrite or paradigm migration | warning | manual |
| F60 | Normal interactive mode output avoids large runtime/internal dumps and audit/RFC-style narrative when concise operational structure is enough | warning | manual |
| F61 | Execute output prioritizes result, implemented changes, validation, not-validated items, manual checks, rollback, intentionally unchanged scope, reviewer focus, and hidden-change checks | warning | manual |
| F62 | Human-facing section names are scannable and operational, e.g. `Yang berhasil diubah`, `File yang berubah`, `Validasi`, `Yang belum tervalidasi`, `Yang masih perlu dicek manual`, `Cara rollback perubahan ini`, `Yang sengaja tidak diubah`, `Reviewer perlu fokus ke`, and `Hidden change check` | warning | manual |
| F63 | `READY_FOR_EXECUTION` and `READY_FOR_PARTIAL_EXECUTION` implementation output includes task cards instead of document-style breakdowns | error | manual |
| F64 | Every implementation task card includes Task ID, Title, Priority, Impact, Scope, Depends On, Parallel Safe, Goal, Why, Likely Files, Do Not Change, Out Of Scope, Derived From, Acceptance Criteria, and Test Expectation | error | manual |
| F65 | Task card priority uses only `P0`, `P1`, `P2`, or `P3`; impact uses only `HIGH`, `MEDIUM`, or `LOW`; dependencies reference task IDs or `none` | error | manual |
| F66 | Risky implementation tasks include explicit `Do Not Change` guardrails for runtime, data, contract, security, broad refactor, or destructive boundaries | error | manual |
| F67 | Multi-step implementation output includes Dependency Order and Parallelization Notes using task IDs | error | manual |
| F68 | Final executable task cards are not emitted while critical blockers remain unresolved, including non-interactive blocked reports | error | manual |
| F69 | Implementation task cards remain output structure only and do not introduce tooling, orchestration, agents, schedulers, workflow engines, DAG systems, Jira integration, story points, or sprint planning | error | manual |
| F70 | Execute output starts with `Execution Result` and one clear status: `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_VALIDATED` | error | manual |
| F71 | Execute changed files are grouped by responsibility: Runtime / Bootstrap, Adapter / Handler, Service / Domain, Persistence, Config / Docs, or Tests | error | manual |
| F72 | Failed, skipped, partial, or not-run validation is highlighted in `Validasi` with command, result, reason, and remaining unvalidated scope | error | manual |
| F73 | Runtime-impacting execute output includes operational rollback guidance such as disable flag, revert config, keep fallback path, or replay if needed | error | manual |
| F74 | Risky execute output reports intentionally unchanged boundaries such as database schema, service topology, handler/persistence boundary, fallback path, or shared contract scope | error | manual |
| F75 | Non-trivial execute output includes `Reviewer perlu fokus ke` covering relevant risks such as idempotency, retry vs DLQ, lifecycle/shutdown, secret-safe logging, or boundary preservation | warning | manual |
| F76 | Execute output includes `Hidden change check` for unexpected database schema, deployment pipeline, shared runtime contract, and unrelated context/runtime changes | warning | manual |
| F77 | Normal interactive execute output does not expose excessive runtime interaction mode, bootstrap, loaded-context, lifecycle, or debug details unless audit/debug mode is requested | warning | manual |
| F78 | Execute output does not use `SUCCESS` unless implementation scope completed and reliable validation evidence exists for the executed scope | error | manual |
| F79 | Execute output uses `PARTIAL_SUCCESS` when implementation is partial or validation is incomplete, and explains which scope remains incomplete | error | manual |
| F80 | Execute output uses `BLOCKED_BY_ENVIRONMENT` for missing tooling/runtime/infra and `BLOCKED` for contract/runtime/approval blockers | error | manual |
| F81 | Execute output uses `NOT_VALIDATED` when code changed but no reliable validation executed | error | manual |
| F82 | Validation output uses one status only when validation is requested: `PASSED`, `FAILED`, `PARTIAL`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_RUN` | error | manual |
| F83 | Review output uses one status only: `APPROVED`, `NEEDS_CHANGES`, `BLOCKED`, or `PARTIAL_REVIEW` | error | manual |
| F84 | Runtime/tooling prerequisite checks are reported before validation/testing execution when commands depend on tools or infra | error | manual |
| F85 | Validation sections separate prerequisites checked, executed commands, failures, checks that could not run, remaining unvalidated scope, and manual actions | error | manual |
| F86 | Environment/tooling failures are not mixed into generic `validation failed` prose or reported as implementation failures | error | manual |
| F87 | Output does not imply fully validated, production-ready, or test-passed unless direct validation evidence exists | critical | manual |
| F88 | Manual actions are explicit and operational, e.g. rerun tests after toolchain availability or start required broker/database infra | warning | manual |
| F89 | Execute/review validation ownership remains distinct: execute may run scoped validation, review owns correctness/risk assessment and validation-gap review | warning | manual |
| F90 | Validation output uses required evidence sections when validation is requested: result, validated scope, automated validation, environment/runtime blockers, unvalidated scope, manual checks, reviewer focus, and risk summary | error | manual |
| F91 | Validation scope is grouped by relevant category: unit, integration, e2e, smoke, rollback, migration, runtime validation, and contract validation | error | manual |
| F92 | Validation output separates automated checks, manual validation, infra-dependent validation, and production-like verification | error | manual |
| F93 | Validation checks the confirmed ECP where possible, including approved behavior, rollback assumptions, retry/idempotency semantics, runtime boundaries, and non-regression expectations | error | manual |
| F94 | Event-driven or runtime-sensitive validation explicitly addresses retryable failure, non-retryable failure, DLQ expectations, duplicate/idempotent replay, and partial replay when relevant | error | manual |
| F95 | Environment/runtime blockers are surfaced directly and not buried inside prose | error | manual |
| F96 | Validation output highlights unvalidated risk areas, missing coverage, risky runtime assumptions, and runtime-sensitive behavior not verified | warning | manual |
| F97 | Validation output does not collapse into review/governance language or generic QA-document prose | warning | manual |
| F98 | Review output uses required sections in order: `Review Result`, `MR readiness`, `Critical findings`, `Major findings`, `Minor findings`, `Info / observations`, `Reviewer perlu fokus ke`, `Yang belum tervalidasi`, `Rollback / safety notes`, and `Suggested next action` | error | manual |
| F99 | Review output states one MR readiness result: `MR-ready`, `not MR-ready`, `MR-ready with accepted risk`, or `cannot determine` | error | manual |
| F100 | Review findings are grouped by severity: `CRITICAL`, `MAJOR`, `MINOR`, and `INFO` | error | manual |
| F101 | Each `CRITICAL` or `MAJOR` review finding includes affected file/area, what is wrong, why it matters, and suggested fix | error | manual |
| F102 | Non-trivial review checks architecture/contract drift: execution contract adherence, confirmed boundary preservation, no hidden topology redesign, no service/repository boundary bypass, and no unapproved contract/schema change | error | manual |
| F103 | Review checks relevant safety areas: secret/raw payload logging, PII exposure, retry/DLQ correctness, idempotency correctness, rollback readiness, and validation honesty | error | manual |
| F104 | Review highlights validation gaps as review findings or coverage gaps without becoming a full validation report or test plan | warning | manual |
| F105 | Review output stays concise and MR-oriented, not a generic audit/report, planning narrative, or implementation task list | warning | manual |
| F106 | Run behavior semantics are bounded to interaction, output, output detail, write behavior, and failure behavior; run config does not introduce CI/CD, deploy, pipeline, trigger, or executor behavior | error | manual |
| F107 | `run.interaction` remains the controlling interaction setting and no overlapping interaction flags are introduced | error | manual |
| F108 | Unsupported or conflicting run fields are reported clearly before mode work | error | manual |
| F109 | Automation-safe behavior emits structured `NEEDS_CONFIRMATION`, `BLOCKED`, or `NEEDS_HUMAN_APPROVAL` and does not ask conversational questions | error | manual |
| F110 | HIGH-risk decisions are never auto-approved by AI or orchestrator and require human confirmation | critical | manual |
| F111 | Important decisions covered by policy confirmation boundaries are not silently auto-approved | critical | manual |
| F112 | Automation-selected LOW defaults and confirmed important decisions include decision trace: decision, selected option, risk level, reason, and affected tasks/artifacts | error | manual |
| F113 | Automation semantics do not imply agents, orchestration, workflow engines, DAGs, schedulers, triggers, auto-retry loops, CI/CD, deploy/release automation, runtime executors, or autonomous multi-step chaining | critical | manual |
| F114 | `NEEDS_HUMAN_APPROVAL` is used for HIGH-risk security/compliance, PII/secrets, financial correctness, destructive migration, production topology, contract authority, or rollback-risky decisions | error | manual |
| F115 | Mode invocation treats `token_budget` as a target operating range and uses `CONTEXT_BUDGET_LIMITED` when required evidence may exceed normal scoped budget | warning | manual |
| F116 | Mode output does not encourage broad-loading all of `.forge/context` by default or treat broad loading as the normal answer to uncertainty | error | manual |
| F117 | Artifact/context drift is reported with `DRIFT_DETECTED`, `DRIFT_RISK`, or `NO_DRIFT_FOUND` when material to the task | warning | manual |
| F118 | Stale artifacts, stale generated context, or old assumptions never override current code/repository evidence | critical | manual |
| F119 | Cross-repo behavior, ownership, runtime topology, and contracts are not assumed without evidence from the referenced repo or authoritative source | error | manual |
| F120 | Incident scenarios distinguish symptoms from causes, use `LIKELY_CAUSE`, `POSSIBLE_CAUSE`, or `NEEDS_MORE_EVIDENCE`, and include confidence when discussing cause | error | manual |
| F121 | Incident scenarios do not claim root cause without direct supporting evidence | critical | manual |
| F122 | Refactor scenarios classify risk as `LOW`, `MEDIUM`, or `HIGH`, and HIGH-risk refactors require a plan/implementation path before execution | error | manual |
| F123 | Refactor scenarios do not present architecture rewrite, paradigm migration, or broad redesign as a normal refactor | error | manual |
| F124 | Fintech HIGH-risk governance decisions require human approval and are not auto-approved by AI or orchestrator | critical | manual |
| F125 | Governance output remains concise, risk-focused, operational, and evidence-based instead of becoming generic audit bureaucracy | warning | manual |
| F126 | Payment, balance, ledger, settlement, reconciliation, or transaction correctness is never classified as LOW risk | critical | manual |
| F127 | Governance-sensitive output never logs, persists, quotes, or copies raw secrets or raw PII | critical | manual |
| F128 | Intelligence/governance semantics do not add tooling, RAG, vector search, knowledge graphs, persistent AI memory, agents, orchestration, workflow engines, schedulers, CI/CD, deploy workflow, runtime executors, or autonomous loops | critical | manual |
| F129 | Root adapters such as `CLAUDE.md` and `AGENTS.md` remain thin bootstrap/invocation adapters and do not duplicate Forge cognition, lifecycle, validation, drift, artifact, governance, or secret semantics | error | manual |
| F130 | Adapter files point to `.forge/context` and specs for normative behavior instead of creating parallel source-of-truth rules | error | manual |
| F131 | Execute preserves existing formatting and line endings, avoids file-wide rewrites, and limits mutation to approved task scope | error | manual |
| F132 | Execute finalization confirms changed files are intended, unrelated file changes are absent, and no broad formatting or line-ending churn occurred | error | manual |
| F133 | Execute checks API/docs/contract wording against relevant source files, such as proto, OpenAPI, grpc-gateway, generated docs, route/schema files, or existing contract sources, before finalizing when those surfaces changed | error | manual |
| F134 | Execute after review verifies prior findings are resolved or explicitly still open and does not finalize with obvious residual review blockers | error | manual |
| F135 | Lifecycle outputs include one concise `Recommended next action`, such as proceed, fix before merge, remediate first, track as later cleanup, or needs human confirmation | warning | manual |

### Category G — Knowledge Ledger Integrity

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| G1 | Every entry in `assumptions.md` has: ID, owner, created date, status | error | yes |
| G2 | Every entry in `unknowns.md` has: ID, owner, created date, status, classification | error | yes |
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
| H4 | `modes/*` files ≤ `size_budget.mode_lines` (default 50) — budget includes required YAML front-matter (~11 lines); operational notes may use the remaining line budget | warning | yes |
| H5 | Files with `updated` older than `governance.staleness_days` (default 90) → flagged for review | info | yes |
| H6 | Files exceeding budget should be split into sub-files, not truncated | info | manual |

### Category I — Configuration Consistency

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| I1 | `forge.version` in config matches expected runtime version `0.3.0` | warning | yes |
| I2 | `run.interaction` is `manual` or `auto` | error | yes |
| I3 | `run.output` is `human`, `markdown`, or `json` | error | yes |
| I4 | `run.output_detail` is `compact`, `standard`, or `full` | error | yes |
| I5 | `run.write_behavior` is `readonly`, `draft`, or `confirmed_apply` | error | yes |
| I6 | `run.failure_behavior` is `stop`, `warn_continue`, or `report_only` | error | yes |
| I7 | `workflow.default_mode` exists and defaults to `ask` in runtime templates | error | yes |
| I8 | `workflow.disabled_modes` exists and replaces default `allowed_modes` configuration | error | yes |
| I9 | `context.root` and `context.budget_profile` exist; context config remains intentionally small | error | yes |
| I10 | `policy.high_risk_areas` and `policy.require_human_confirmation_for` contain seeded defaults | error | yes |
| I11 | `team.context_update_flow` is `reviewable_patch` and `team.require_context_impact_check` is `true` | error | yes |
| I12 | `artifacts` separates `.forge/generated`, `.forge/context-patches`, `.forge/temp`, and `.forge/cache`; temp/cache are ignored/local-only | error | yes |
| I13 | Active config docs do not use old runtime profile, non-interactive, or decision-authority fields as current config semantics | error | partial |
| I14 | The context update flow is changed files -> affected context cards -> context patch -> review -> promote to `.forge/context` | error | manual |

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

### Category M — Secret Safety & Redaction *(v1.7)*

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| M1 | Generated context, reports, plans, reviews, tests, migrations, validation-cases, and platform context contain no raw secrets | critical | partial |
| M2 | Secret findings report only secret type, file path, line/reference when available, and safe masked preview | critical | manual |
| M3 | Raw secrets are not copied into `knowledge/inferred.md`, `knowledge/unknowns.md`, `knowledge/confirmations.md`, decisions, modes, or generated context | critical | partial |
| M4 | Discovered secrets are classified as security findings | error | manual |
| M5 | Rotation is recommended when a secret may have been committed, logged, displayed, copied, or otherwise exposed | warning | manual |
| M6 | Database URLs with credentials, Kafka/SASL credentials, cloud credentials, OAuth client secrets, JWTs, cookies, private keys, tokens, and passwords are redacted before output | critical | partial |

### Category N — Lifecycle Artifact Boundaries *(v3.3)*

| ID | Rule | Severity | Automatable |
|---|---|---|---|
| N1 | Persisted lifecycle artifacts live under `.forge/generated/` or are explicitly identified as external handoff artifacts | warning | partial |
| N2 | Lifecycle artifacts are treated as supporting continuity helpers, never source of truth over repository code, docs, ADRs, or human confirmations | critical | manual |
| N3 | Artifact types are limited to Plan, ECP, Execute Result, Validation Result, Review Result, Context Verification Result, and scenario artifacts explicitly marked as incident/refactor workflow scenarios | error | manual |
| N4 | Artifact ownership is clear from `produced_by_mode` or equivalent mode-owned section | error | partial |
| N5 | Artifact links are shallow trace references only and do not imply orchestration, workflow, DAG, scheduler, dependency-management, execution-trigger, or agent-memory semantics | critical | manual |
| N6 | Artifacts do not contain hidden chain-of-thought, raw secrets, unnecessary conversation history, generic long-form summaries, or autonomous memory structures | critical | partial |
| N7 | Artifacts remain concise, human-readable, append-friendly, replaceable, discardable, and reviewable in diffs | warning | manual |
| N8 | Artifact status and revision references are operational and do not promote artifact volume into lifecycle maturity | warning | manual |
| N9 | Artifact conflicts with repository evidence are surfaced as stale, partial, or superseded; repository evidence wins | error | manual |
| N10 | Ask mode does not create lifecycle artifacts by default and references artifacts only when relevant to a lightweight question | warning | manual |
| N11 | `.forge/context` is the committed curated context source of truth; `.forge/context-patches` contains reviewable proposals only | error | manual |

---

## 3. Validation Execution Modes

### 3.1 Manual Checklist (Current Phase)

Walk through each category sequentially. Use the table format:

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
forge validate --severity critical  # critical findings only
forge validate --severity error  # errors only
forge validate --ci         # future reserved validation profile; no CI pipeline behavior is defined here
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

CRITICAL (stop and remediate):
  [M1] generated/report.md — raw secret exposure detected; redact and rotate if exposed

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
  Critical: 1
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

Run in order: **M -> A -> B -> C -> I -> D -> E -> F -> G -> H -> J -> K -> L -> N** to avoid cascading false failures and prevent raw secret propagation.

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
| `specs/mode-invocation.md` | Source of mode invocation lifecycle and runtime behavior expectations |
| `specs/artifact-lifecycle.md` | Source of bounded lifecycle artifact semantics and invalid artifact boundaries |
| Future `TOOLING-SPEC.md` | `forge validate` CLI implements this spec programmatically |
| Future automation/CI integration | May use validation results later; this spec defines rules only, not pipeline, deploy, trigger, or executor behavior |

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
[ ] F11 plan uses ECP-ready output, not PRD/business prose
[ ] F12 plan adapts sections to active layers
[ ] F13 plan preserves evidence/inference/unknown boundaries
[ ] F14 plan uses scoped on-demand loading
[ ] F15 forge.config.yaml read before mode file
[ ] F16 context-loading detail concise; missing evidence reported
[ ] F17 no broad-loading by default
[ ] F18 mode distinctions preserved
[ ] F19 ambiguity reported; mode insufficiency highlighted only when relevant
[ ] F20 mode-specific behavior lives in mode files, not global conventions
[ ] F21 unknowns classified blocking/proposed-default/informational
[ ] F22 proposed defaults labeled and bounded
[ ] F23 run.interaction auto emits required decisions or blocking status, not interactive questions
[ ] F24 run.interaction manual remains interactive-first
[ ] F25 excessive architecture-option generation discouraged
[ ] F26 proposed defaults not promoted to confirmed facts
[ ] F27 visible core modes constrained to init/ask/plan/implementation/execute/review/verify-context
[ ] F28 plan produces Quick Plan or SDD, not detailed coding tasks
[ ] F29 implementation produces an ECP only after critical blockers are resolved
[ ] F30 execute owns repository modification behavior and groups changed files by responsibility
[ ] F31 execute does not redefine approved plans or architecture
[ ] F32 architecture reasoning and execution reasoning remain separated
[ ] F33 validation remains evidence-based inside execute/review workflows
[ ] F34 execute reports scoped validation without replacing review
[ ] F35 review checks validation evidence without becoming execution
[ ] F36 mode responsibilities remain separated
[ ] F37 test placement respects existing repo conventions
[ ] F38 unit tests not placed far from target package without reason
[ ] F39 integration/e2e tests not mixed into unit folders without reason
[ ] F40 reusable mocks/fixtures/helpers follow a clear convention
[ ] F41 decision prompts bounded to 2 options by default
[ ] F42 run.interaction detected/applied without prompt mention; internals not dumped
[ ] F43 interactive repos use ask-first behavior, not automation blocked reports
[ ] F44 non-interactive repos do not ask conversational questions
[ ] F45 interactive implementation stops before final breakdown on critical blockers
[ ] F46 interactive implementation asks concise Recommended/Alternative questions first
[ ] F47 interactive implementation does not bury blockers at the end
[ ] F48 final executable tasks are not emitted while critical blockers remain unresolved
[ ] F49 non-interactive implementation emits NEEDS_CONFIRMATION or safe READY_FOR_PARTIAL_EXECUTION, not questions
[ ] F50 interactive implementation confirmation starts with NEEDS_CONFIRMATION
[ ] F51 interactive implementation confirmation includes blocker, why it matters, Recommended/Alternative, and reply instructions
[ ] F52 interactive implementation confirmation uses 2 options by default, max 3 for major tradeoffs
[ ] F53 implementation output includes exactly one readiness status
[ ] F54 READY_FOR_EXECUTION has no conditional or unresolved required values
[ ] F55 execution-sensitive READY_FOR_EXECUTION includes concrete execution values
[ ] F56 final executor instructions contain no unresolved required execution values
[ ] F57 ask answers lightweight repo-understanding questions only
[ ] F58 incident diagnoses without speculative redesign
[ ] F59 refactor remains bounded and behavior-preserving
[ ] F60 normal interactive output avoids runtime/internal dumps and RFC/audit narrative
[ ] F61 execute output prioritizes result, changes, validation, manual checks, rollback, unchanged scope, reviewer focus, hidden-change checks
[ ] F62 section names are scannable and operational
[ ] F63 ready/partial implementation output uses task cards
[ ] F64 task cards include required fields
[ ] F65 task card priority, impact, and dependencies use allowed values
[ ] F66 risky task cards include Do Not Change guardrails
[ ] F67 multi-step output includes Dependency Order and Parallelization Notes
[ ] F68 executable task cards are not emitted while critical blockers remain
[ ] F69 task cards do not introduce tooling/orchestration/agents/workflows
[ ] F70 execute output starts with Execution Result and clear status
[ ] F71 execute changed files are grouped by responsibility
[ ] F72 failed/skipped/partial validation is highlighted with command, result, reason, and unvalidated scope
[ ] F73 runtime-impacting execute output includes operational rollback guidance
[ ] F74 risky execute output reports intentionally unchanged boundaries
[ ] F75 non-trivial execute output includes Reviewer perlu fokus ke
[ ] F76 execute output includes Hidden change check
[ ] F77 normal execute output avoids excessive runtime/debug/loading internals
[ ] F78 execute SUCCESS requires reliable validation evidence
[ ] F79 partial implementation or incomplete validation uses PARTIAL_SUCCESS with remaining scope
[ ] F80 environment blockers and contract/runtime blockers are classified separately
[ ] F81 code changes without reliable validation use NOT_VALIDATED
[ ] F82 validation output uses PASSED/FAILED/PARTIAL/BLOCKED_BY_ENVIRONMENT/NOT_RUN when validation is requested
[ ] F83 review output uses APPROVED/NEEDS_CHANGES/BLOCKED/PARTIAL_REVIEW
[ ] F84 prerequisite checks are reported before tool/infra-dependent validation
[ ] F85 validation reporting separates executed, failed, could-not-run, unvalidated, and manual action
[ ] F86 environment/tooling failures are not described as implementation failures
[ ] F87 no fully-validated, production-ready, or test-passed claim without evidence
[ ] F88 manual actions are explicit and operational
[ ] F89 execute/review validation ownership remains distinct
[ ] F90 validation reporting uses required evidence sections when validation is requested
[ ] F91 validation scope is grouped by unit/integration/e2e/smoke/rollback/migration/runtime/contract category
[ ] F92 automated, manual, infra-dependent, and production-like validation are separated
[ ] F93 validation checks the confirmed ECP where possible
[ ] F94 runtime-sensitive validation covers retry/DLQ/idempotency/replay when relevant
[ ] F95 environment/runtime blockers are surfaced directly
[ ] F96 unvalidated risks, missing coverage, and risky runtime assumptions are visible
[ ] F97 validation reporting stays out of generic QA prose and review/governance critique
[ ] F98 review output uses required MR-review sections
[ ] F99 review states clear MR readiness
[ ] F100 review findings grouped by CRITICAL/MAJOR/MINOR/INFO
[ ] F101 critical/major review findings include evidence, impact, and suggested fix
[ ] F102 non-trivial review checks architecture/contract drift
[ ] F103 review checks relevant safety areas
[ ] F104 review testing gaps do not become full test plans
[ ] F105 review stays concise, MR-oriented, and not audit/task-list prose
[ ] F106 run behavior remains bounded and does not introduce CI/CD/pipeline/executor behavior
[ ] F107 run.interaction remains the controlling interaction setting
[ ] F108 unsupported or conflicting run fields are reported
[ ] F109 automation-safe behavior uses structured status, not questions
[ ] F110 HIGH-risk decisions are not auto-approved
[ ] F111 policy-covered important decisions are not silently auto-approved
[ ] F112 automation-selected LOW defaults and confirmed important decisions include decision trace
[ ] F113 automation semantics do not imply agents/orchestration/workflows
[ ] F114 NEEDS_HUMAN_APPROVAL used for HIGH-risk decisions
[ ] F115 CONTEXT_BUDGET_LIMITED used when required evidence exceeds normal scoped budget
[ ] F116 broad context loading is not encouraged by default
[ ] F117 drift statuses reported when material
[ ] F118 stale artifacts/context never override current repo evidence
[ ] F119 cross-repo behavior is not assumed without evidence
[ ] F120 incident cause status and confidence are present
[ ] F121 incident root cause is not claimed without evidence
[ ] F122 refactor scenario risk is classified and HIGH risk requires a plan/implementation path
[ ] F123 architecture rewrite is not presented as normal refactor
[ ] F124 fintech HIGH-risk governance decisions are not auto-approved
[ ] F125 governance output stays concise, operational, and evidence-based
[ ] F126 payment/transaction correctness is never LOW risk
[ ] F127 raw secrets/PII are not logged, persisted, quoted, or copied
[ ] F128 intelligence/governance semantics do not add tooling/RAG/vector DB/knowledge graph/orchestration/agents/runtime behavior
[ ] F129 root adapters remain thin and do not duplicate Forge operational semantics
[ ] F130 adapter files point to `.forge/context` and specs instead of creating parallel source-of-truth rules
[ ] F131 execute preserves formatting/line endings and avoids file-wide rewrites
[ ] F132 execute finalization confirms intended changes, no unrelated files, and no churn
[ ] F133 execute contract/docs/API wording is checked against source files when relevant
[ ] F134 execute after review verifies prior findings and does not finalize with residual blockers
[ ] F135 lifecycle outputs include one concise Recommended next action

KNOWLEDGE LEDGERS
[ ] G1  assumptions entries valid
[ ] G2  unknowns entries include classification
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
[ ] H4  modes ≤ 50 lines (including front-matter)
[ ] H5  stale files flagged
[ ] H6  over-budget files split

CONFIG CONSISTENCY
[ ] I1  forge.version matches expected runtime version
[ ] I2  run.interaction valid
[ ] I3  run.output valid
[ ] I4  run.output_detail valid
[ ] I5  run.write_behavior valid
[ ] I6  run.failure_behavior valid
[ ] I7  workflow.default_mode exists
[ ] I8  workflow.disabled_modes exists
[ ] I9  context root and budget profile exist
[ ] I10 policy defaults exist
[ ] I11 team context update flow requires reviewable patches
[ ] I12 artifact directories are separated
[ ] I13 active config docs avoid old runtime profile/non-interactive/decision-authority fields
[ ] I14 context update flow uses changed files -> affected cards -> patch -> review -> promote

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

SECRET SAFETY & REDACTION (M — v1.7)
[ ] M1  no raw secrets in generated context or reports
[ ] M2  secret findings use type/path/line/masked preview only
[ ] M3  no raw secrets copied into knowledge, decisions, modes, or generated context
[ ] M4  discovered secrets classified as security findings
[ ] M5  rotation recommended when exposure is possible
[ ] M6  credentials/tokens/private keys/cookies/passwords redacted before output

LIFECYCLE ARTIFACT BOUNDARIES (N - v3.3)
[ ] N1  persisted artifacts live under generated/artifacts or are explicitly external
[ ] N2  artifacts never override repository truth
[ ] N3  artifact types are limited to mode-owned lifecycle artifacts
[ ] N4  artifact ownership is clear
[ ] N5  artifact links do not imply orchestration/workflow/DAG semantics
[ ] N6  no chain-of-thought, raw secrets, conversational history, long summaries, or autonomous memory structures
[ ] N7  artifacts remain concise, human-readable, append-friendly, replaceable, and reviewable
[ ] N8  artifact revisions do not promote volume into maturity
[ ] N9  artifact conflicts defer to repository evidence
[ ] N10 ask does not create lifecycle artifacts by default
[ ] N11 .forge/context is source of truth and context-patches are proposals only
```
