# Mode Invocation Protocol

| Field | Value |
|---|---|
| Document | Forge Mode Invocation Protocol |
| Version | 3.2 |
| Date | 2026-05-28 |
| Status | `decision` |
| Scope | Framework-level protocol for invoking Forge modes |
| Dependency | `runtime/.forge/context/00-meta/conventions.md`, `runtime/.forge/context/modes/*.md`, `runtime/skills/*/SKILL.md`, `specs/context-validation.md`, `specs/artifact-lifecycle.md`, `specs/adapter-command-foundation.md` |

---

## 0. Purpose

Mode invocation defines how an AI assistant uses Forge mode files during ask, planning, implementation task decomposition, execution, testing, review, incident, and refactor work.

The protocol ensures:
- Mode files are operational contracts, not optional hints.
- Context loading remains scoped and delta-based.
- `runtime.non_interactive` controls interactive vs automation-safe behavior globally.
- `runtime.profile` labels local vs automation runtime intent without becoming a second interaction flag.
- Decision authority and LOW/MEDIUM/HIGH risk boundaries make automation-safe behavior explicit.
- Evidence, inference, proposed-default, and unknown boundaries survive task execution.
- Unknowns are classified into blocking, proposed-default, or informational behavior.
- Sensitive values are redacted before output or context write.
- Runtime repositories receive concise, scannable engineering communication.
- Execute reports expose status, validation, rollback, review focus, and hidden-change checks without narrative noise.
- Runtime validation checks prerequisites before commands and separates implementation failures from environment/tooling blockers.
- Partial, blocked, and not-validated outcomes are first-class statuses where each mode owns the vocabulary for that outcome.
- Testing mode provides structured, contract-aware validation grouped by test scope and runtime risk.
- Review mode behaves like a concise senior MR review with clear acceptability, severity, evidence, MR readiness, reviewer focus, and safety risk.
- Runtime placement stays modular: global files define entry rules, mode files define mode-specific behavior.
- Human-reviewable execution boundaries exist before AI modifies code.
- Execution can be deterministic after architecture reasoning, unknown classification, and bounded task-card decomposition.
- Lifecycle artifacts provide bounded continuity without becoming source of truth or memory infrastructure.
- Framework maintainers have an authoritative protocol for future evolution.

v2.7 consolidates status vocabulary, human-facing section names, and mode boundaries across implementation, execute, testing, and review. It removes legacy review-needed blocking language and does not add modes, tooling, orchestration, agents, workflow engines, or runtime executors.
v2.8 adds minimal lifecycle artifact semantics for mode handoffs. It does not add orchestration, agents, workflow engines, DAG systems, CI/CD, deploy workflow, runtime executors, persistent AI memory, or knowledge graphs.
v2.9 adds bounded runtime profile, decision authority, decision risk, and automation-safe approval semantics. It does not add agents, orchestration, workflow engines, DAG systems, schedulers, triggers, CI/CD, deploy workflow, runtime executors, or autonomous loops.
v3.0 adds lightweight intelligence and governance semantics for scoped loading, drift detection, cross-repo awareness, incident/refactor reasoning, and fintech-grade risk signals. It does not add tooling, RAG, vector search, knowledge graphs, agents, orchestration, workflow engines, schedulers, CI/CD, deploy workflow, runtime executors, or autonomous loops.
v3.1 clarifies that Claude, Codex, shared skills, and tool-specific adapters are thin invocation surfaces that reference Forge core instead of duplicating runtime, validation, drift, artifact, governance, or secret semantics.
v3.2 hardens bounded execution against unintended file churn, residual review blockers, and contract-source drift, and adds one concise recommended next action to lifecycle outputs. It does not add modes, orchestration, agents, memory, schedulers, CI/CD, deploy logic, runtime executors, or autonomous chaining.

This document does NOT:
- Redesign Forge architecture.
- Add automation tooling, agents, executors, or runtime services.
- Introduce any other interaction or workflow flag.
- Implement CI/CD, deploy, scheduling, trigger, workflow graph, agent loop, or runtime execution behavior.
- Replace mode file schema rules.
- Define repository-specific domain content.
- Treat skills as cognition sources, orchestration units, memory systems, runtime executors, or lifecycle authorities.

---

## 1. Invocation Lifecycle

Canonical lifecycle:

1. Requested mode identified.
2. `.forge/forge.config.yaml` read first.
3. `runtime.profile`, `runtime.non_interactive`, and decision authority detected.
4. Profile/non-interactive conflicts reported clearly, with `runtime.non_interactive` applied as the controlling behavior.
5. Mode file read from `.forge/context/modes/<mode>.md`.
6. `include`, `on_demand`, `exclude`, `token_budget`, and `notes` parsed.
7. Scoped context loaded according to the mode delta.
8. Task executed according to mode behavior and runtime interaction behavior. For planning, human approval of the ECP is required before implementation proceeds. For implementation, human approval of the Execution Contract is required before execute proceeds.
9. Decision risk and authority applied before any automation-selected default.
10. Runtime/tooling prerequisites checked before validation or testing commands when such commands depend on tooling/infra.
11. Validation evidence separated from validation gaps, blocked commands, and manual follow-up.
12. Evidence / inference / proposed-default / unknown boundaries preserved.
13. Unknowns classified by operational impact.
14. Missing evidence and unresolved ambiguity reported.
15. Loading details reported only as concise scoped-context confirmation when useful.
16. Mode sufficiency evaluated when it affects the result.
17. Lifecycle artifacts referenced or written only when useful for bounded continuity.

Mode invocation is successful only when the assistant can explain what mattered for the task, what evidence was missing, and whether the selected mode was enough. Normal interactive output should not expose full runtime/bootstrap detail.

Canonical workflow:

```
forge-plan
→ human approval (ECP: proposed → approved)
→ forge-implement
→ human approval (Execution Contract: proposed → approved)
→ forge-execute
→ optional forge-test
→ forge-review
→ scoped fix loop when review returns NEEDS_CHANGES
```

Each transition between planning output and implementation, and between implementation task cards and execution, requires explicit human approval. Assistants must not proceed to the next mode without that signal.

Ask, incident, and refactor are entry modes, not mandatory lifecycle stages. Small, well-understood changes may skip planning. Execution may operate on approved task subsets. Testing may operate independently for test-only requests.

See `docs/workflow.md` for the narrative walkthrough, approval gate UX, and post-review fix loop.

---

## 2. Global Invocation Rules

All modes follow these rules:

- Read `.forge/forge.config.yaml` before reading the requested mode file.
- Detect `runtime.profile`, `runtime.non_interactive`, and decision authority without requiring the user to mention them.
- Apply `runtime.non_interactive` as the single controlling interaction flag.
- Then read the requested mode file before loading mode-specific context.
- Treat always-loaded core as already available: `00-meta/*` and `01-core/*`.
- Treat mode files as loading deltas on top of core.
- Treat `runtime.non_interactive: false` as the interactive default.
- Treat `runtime.non_interactive: true` as automation-safe behavior.
- Treat `runtime.profile: local` as human-in-the-loop profile metadata and `runtime.profile: automation` as automation-safe profile metadata.
- Treat `runtime.profile: ci` as reserved metadata only; do not add CI/CD, pipeline, deploy, release, trigger, or executor behavior.
- Report profile/non-interactive conflicts clearly and continue only according to `runtime.non_interactive`.
- Load `include` entries normally when relevant to the task.
- Load `on_demand` entries only when task scope requires them.
- Do not load `exclude` entries unless the user explicitly changes scope.
- Use `token_budget` as the target scoped context budget for the mode.
- Treat `token_budget` as a target operating range, not a blind hard cap.
- Follow `notes` for concise operational guidance.
- Do not broad-load `.forge/context` by default.
- Prefer direct repository evidence over broad context loading.
- Expand context only with a concrete reason tied to task relevance, missing evidence, drift risk, cross-repo uncertainty, incident blast radius, refactor risk, or governance risk.
- Emit `CONTEXT_BUDGET_LIMITED` when required evidence may exceed the normal scoped budget and Forge cannot safely answer, plan, execute, test, review, diagnose, or refactor without more context.
- Keep evidence-backed facts, inferences, proposed defaults, assumptions, and unknowns separate.
- Keep proposed defaults explicitly labeled as proposed and not confirmed.
- Redact secrets before reporting evidence, findings, plans, reviews, tests, or loaded context.
- Keep context-loading details terse in normal output; `Scoped context loaded` plus the relevant areas is enough when useful.
- Report missing evidence and unresolved ambiguity before relying on guesses.
- State whether the requested mode was insufficient when that affects the task.
- Treat lifecycle artifacts as generated continuity helpers; never treat them as source of truth over repository evidence.

## 2.1 Scoped Loading, Drift, Cross-Repo, and Governance

Smarter scoped loading remains a semantic discipline, not a retrieval system.

Allowed:
- Load task-relevant context based on mode deltas and concrete evidence needs.
- Prefer current code, repository docs, ADRs, human confirmations, and directly relevant artifacts.
- Expand scoped context when normal evidence is insufficient and the reason is reported.
- Report insufficient context instead of guessing.

`CONTEXT_BUDGET_LIMITED` output must stay short and operational:
- Required evidence missing.
- Why it affects the current conclusion or next action.
- Targeted context expansion needed.
- Safe fallback, if any, such as partial answer, blocked status, or human confirmation.

Do not use vague self-referential uncertainty or dramatic warning language. State the evidence boundary directly.

Forbidden:
- Loading all of `.forge/context` by default.
- Treating `token_budget` as permission to skip required evidence.
- Adding RAG, vector search, knowledge graphs, persistent AI memory, retrieval daemons, or autonomous context-expansion loops.

Drift detection statuses:

| Status | Meaning |
|---|---|
| `NO_DRIFT_FOUND` | Relevant context/artifacts were checked against current evidence and no contradiction was found. |
| `DRIFT_RISK` | Evidence may be stale, incomplete, or older than code reality; do not rely on it as authoritative. |
| `DRIFT_DETECTED` | Current repository evidence contradicts context, assumptions, decisions, generated artifacts, or prior output. |

When drift is detected, current repository evidence wins. Stale artifacts may be cited as history only and must be labeled stale, partial, or superseded.

Cross-repo awareness is evidence-limited:
- Forge may identify referenced external/shared repositories.
- Forge may report dependency, ownership, and contract uncertainty.
- Forge may compare contracts only when evidence from both sides is available.
- Forge must not assume another repo's behavior, runtime topology, deploy state, ownership, or contract implementation from references alone.
- Forge must not modify multiple repositories automatically or introduce cross-repo orchestration.

Governance checks are concise risk signals. Relevant modes should surface:
- PII / sensitive data.
- Secrets / credentials.
- Financial correctness.
- Idempotency.
- Retry safety.
- Replay safety.
- Rollback safety.
- Transaction consistency.
- Auditability.
- Observability.
- Blast radius.

Governance output must be operational and evidence-based: risk, evidence, impact, next check or required decision. It must not become a generic security checklist, compliance essay, or bureaucratic audit report.

HIGH-risk governance decisions require human approval. Raw secrets and raw PII must never be logged, persisted, quoted, or copied into context/artifacts. Payment, balance, ledger, settlement, reconciliation, and transaction correctness are never LOW risk.

---

## 3. Runtime Profiles, Unknown Classification, and Decision Protocol

Forge uses exactly one runtime flag for interaction behavior: `runtime.non_interactive`.

`runtime.profile` is lightweight runtime profile metadata:

| Profile | Meaning |
|---|---|
| `local` | Default human-in-the-loop workflow. Interactive-first, concise human-readable output, may ask clarification questions. Implies `runtime.non_interactive: false` unless explicitly overridden. |
| `automation` | Non-interactive-safe workflow. Must not ask conversational questions; emits structured statuses and required decisions. Implies `runtime.non_interactive: true` unless explicitly overridden. |
| `ci` | Reserved for future compatibility. It does not define CI/CD behavior, pipeline execution, deploy/release automation, triggers, or runtime executors. |

| Value | Behavior |
|---|---|
| `false` | Interactive-first default. Forge may ask concise clarification questions for blocking decisions and continues after human confirmation. |
| `true` | Non-interactive automation-safe behavior. Forge must not ask conversational questions and must emit structured `NEEDS_CONFIRMATION`, `BLOCKED`, or `NEEDS_HUMAN_APPROVAL` for decisions it cannot safely make. |

If `runtime.profile` and `runtime.non_interactive` conflict, Forge reports the conflict clearly before mode work and applies `runtime.non_interactive` as the controlling behavior. This is a validation concern, not permission to introduce another interaction flag.

Decision authority values:

| Authority | Boundary |
|---|---|
| `ai` | May choose only LOW-risk proposed defaults. Must not decide MEDIUM or HIGH risk behavior. |
| `orchestrator` | May choose MEDIUM-risk operational defaults only when explicitly configured. Must emit decision trace. Must not approve HIGH-risk decisions. |
| `human` | Required for HIGH-risk decisions and any decision whose authority is missing, disputed, or outside configured automation authority. |

Decision risk levels:

| Risk | Meaning | Runtime behavior |
|---|---|---|
| `LOW` | Reversible, local, no contract/security/data correctness impact. | AI may continue with a proposed default. |
| `MEDIUM` | Operational behavior, config, or runtime behavior. | Orchestrator may choose only when configured; otherwise needs confirmation. |
| `HIGH` | Security/compliance, PII/secrets, financial correctness, destructive migration, production topology, contract authority, or rollback-risky change. | Requires human confirmation; automation stops with `NEEDS_HUMAN_APPROVAL`. |

Automation-selected LOW defaults and orchestrator-selected MEDIUM decisions must include a concise decision trace:
- Decision.
- Selected option.
- Authority used.
- Risk level.
- Reason.
- Affected tasks/artifacts.

Forge classifies unknowns by operational impact:

| Classification | Continue? | Behavior |
|---|---|---|
| `blocking` | No | Requires authoritative decision before implementation/release. Interactive mode asks the minimum decision question. Automation emits the selected mode's allowed blocking/readiness status or `NEEDS_HUMAN_APPROVAL` for HIGH risk. |
| `proposed-default` | Yes | AI may proceed with a safe, conventional, reversible, non-authoritative default that is explicitly labeled `proposed` and `not confirmed`. |
| `informational` | Yes | Record the uncertainty; do not interrupt execution. |

Blocking unknowns include event schema authority, retry/DLQ semantics, ownership/SLA/compliance, destructive migration approval, security policy, and production runtime topology.

Interactive prompts must be concise, decision-oriented, and practical: lead with the blocker, explain why it matters for execution safety, then show the safest/production-ready `Recommended` option plus one viable `Alternative` by default. Use a maximum of three options only for major architecture tradeoffs.

When multiple blockers exist, group them as a short numbered list before options. Each blocker should state the missing value/evidence and impact in one line. Put the recommended path after the blocker list, not after a long defensive explanation.

Non-interactive mode must not ask for human input conversationally. When blocking unknowns exist, emit structured status and include required decisions, recommended option, alternative when useful, authority required, risk level, and affected tasks/artifacts.

Changing `runtime.non_interactive` never re-initializes context, rewrites repository cognition, invalidates assumptions, modifies inferred knowledge, or rewrites systems, layers, or core files.

### 3.1 Proposed Default Semantics

AI may define proposed defaults only when the choice is low-risk, operationally conventional, reversible, non-authoritative, not topology-defining, and not compliance/security defining.

Each proposed default must state:
- Proposed value.
- Reason for the proposal.
- Status: `proposed`, `not confirmed`.
- Required confirmation before production finalization when an owner/producer/platform decision is needed.

## 3.2 Human UX Rules

Forge output should read like practical engineering workflow communication, not an AI framework audit.

Prefer human-friendly section names:
- `Execution Result`
- `Yang berhasil diubah`
- `File yang berubah`
- `Validasi`
- `Yang belum tervalidasi`
- `Yang masih perlu dicek manual`
- `Cara rollback perubahan ini`
- `Yang sengaja tidak diubah`
- `Reviewer perlu fokus ke`
- `Hidden change check`
- `Recommended next action`

Avoid prominent runtime/debug labels in normal interactive usage:
- runtime interaction mode dumps
- full context loading internals
- lifecycle/debug metadata
- low-value framework metadata

Allowed: a concise scoped-context confirmation when it helps the user trust the answer.

## 3.3 Runtime Validation Status Semantics

Forge must not hide failed, skipped, blocked, or partial validation behind successful-sounding prose.

Prerequisite checks apply before validation/testing commands when the command depends on local tooling or runtime infrastructure. Examples include language/runtime tools (`go`, `node`), formatters (`gofmt`), package managers (`npm`, `pnpm`, `yarn`), dependency/codegen/protobuf tooling, Docker/compose, and explicitly required Kafka/SQL/broker/database test infrastructure.

Allowed status vocabularies:

| Mode | Statuses |
|---|---|
| Execute | `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, `NOT_VALIDATED` |
| Testing | `PASSED`, `FAILED`, `PARTIAL`, `BLOCKED_BY_ENVIRONMENT`, `NOT_RUN` |
| Review | `APPROVED`, `NEEDS_CHANGES`, `BLOCKED`, `PARTIAL_REVIEW` |
| Implementation | `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, `READY_FOR_EXECUTION` |

Execution status meanings:
- `SUCCESS`: approved implementation scope completed and reliable validation evidence exists for the executed scope.
- `PARTIAL_SUCCESS`: implementation completed partially, or implementation finished but validation is incomplete.
- `BLOCKED`: execution cannot continue because contract, approval, runtime behavior, ownership, security, or other non-environment prerequisites are unresolved.
- `BLOCKED_BY_ENVIRONMENT`: implementation or validation is blocked because required runtime/tooling/infra is unavailable.
- `NOT_VALIDATED`: code changed, but no reliable validation executed.

Testing status meanings:
- `PASSED`: selected validation ran and passed.
- `FAILED`: selected validation ran and exposed an implementation or test failure.
- `PARTIAL`: some validation ran, but required coverage or scenarios remain incomplete.
- `BLOCKED_BY_ENVIRONMENT`: validation could not run because required tooling or infra is unavailable.
- `NOT_RUN`: no reliable validation command was executed.

Review status meanings:
- `APPROVED`: reviewed scope has sufficient implementation and validation evidence with no blocking correctness or risk findings.
- `NEEDS_CHANGES`: review found implementation, test, or documentation changes required before approval.
- `BLOCKED`: required contract/runtime evidence is missing, so meaningful review cannot complete.
- `PARTIAL_REVIEW`: review covered only part of the changed scope or lacked complete validation evidence.

Review MR readiness must use exactly one of:
- `MR-ready`
- `not MR-ready`
- `MR-ready with accepted risk`
- `cannot determine`

`NEEDS_HUMAN_APPROVAL` means required decision risk is HIGH or automation/orchestrator authority is insufficient. It is not an execution-ready state.

Validation sections must separate:
- What prerequisites were checked.
- What commands or checks were executed.
- What failed.
- What could not run.
- What remains unvalidated.

Manual actions must be explicit and operational, for example: `Jalankan go test ./... setelah Go toolchain tersedia`, `Validasi Kafka integration membutuhkan broker aktif`, or `Replay/DLQ flow belum tervalidasi manual`.

Status claims must never imply fully validated, production-ready, or test-passed unless the report contains evidence for that claim.

Testing reports must use this output order:
1. `Testing Result`
2. `Scope yang divalidasi`
3. `Automated validation`
4. `Environment/runtime blockers`
5. `Yang belum tervalidasi`
6. `Yang masih perlu dicek manual`
7. `Reviewer perlu fokus ke`
8. `Risk summary`

Testing scope must be grouped by applicable category: unit, integration, e2e, smoke, rollback, migration, runtime validation, and contract validation. Automated checks, manual validation, infra-dependent validation, and production-like verification must not be mixed ambiguously.

Contract-aware testing validates the confirmed execution contract where possible: approved behavior, rollback assumptions, retry/idempotency semantics, runtime boundaries, and non-regression expectations. Event-driven or runtime-sensitive testing must explicitly address retryable failure behavior, non-retryable failure behavior, DLQ expectations, duplicate/idempotent replay, and partial replay when relevant.

Review reports must use this output order:
1. `Review Result`
2. `MR readiness`
3. `Critical findings`
4. `Major findings`
5. `Minor findings`
6. `Info / observations`
7. `Reviewer perlu fokus ke`
8. `Yang belum tervalidasi`
9. `Rollback / safety notes`
10. `Suggested next action`

Review findings must be grouped by severity: `CRITICAL`, `MAJOR`, `MINOR`, and `INFO`. Each `CRITICAL` or `MAJOR` finding must include affected file/area, what is wrong, why it matters, and suggested fix.

Review mode must check architecture/contract compliance for non-trivial changes: execution contract adherence, approved boundary preservation, absence of hidden topology redesign, no service/repository boundary bypass, and no unapproved contract/schema changes. Review mode must also check relevant safety risks: secret/raw payload logging, PII exposure, retry/DLQ correctness, idempotency correctness, rollback readiness, and validation honesty.

## 3.4 Lifecycle Artifact Semantics

Lifecycle artifacts are optional mode handoff records. Persist them only when they reduce repeated context reconstruction or preserve result evidence across sessions.

Allowed persisted location:

```
.forge/context/generated/artifacts/
```

Mode-owned artifact types:

| Mode | Artifact |
|---|---|
| `planning` | ECP Artifact |
| `implementation` | Execution Contract Artifact |
| `execute` | Execute Result Artifact |
| `testing` | Testing Result Artifact |
| `review` | Review Result Artifact |
| `incident` | Incident Artifact |
| `refactor` | Refactor Artifact |

Artifact links may reference previous artifact IDs, ECP IDs, execution contract IDs, result artifact IDs, repository evidence, commits, PR/MR IDs, ADRs, and human confirmations.

Artifact links are trace references only. They must not become orchestration, DAG, workflow, scheduler, agent-memory, execution-trigger, or dependency-management semantics.

Artifacts must stay concise, human-readable, append-friendly, replaceable, and discardable. They must not contain hidden chain-of-thought, raw secrets, unnecessary conversation history, broad summaries, or autonomous memory structures.

If an artifact conflicts with repository evidence, code/repo evidence wins and the artifact is stale, partial, or superseded.

---

## 4. Runtime Placement

Runtime placement follows these boundaries:

- `runtime/CLAUDE.md` keeps only concise invocation entry behavior.
- `runtime/AGENTS.md` and tool adapters keep the same thin invocation-only boundary.
- `00-meta/conventions.md` keeps global cognition principles and mode-loading discipline.
- `modes/<mode>.md` owns mode-specific execution and reporting behavior in `## notes`.
- Mode-specific ask, planning, implementation, execute, testing, review, incident, and refactor behavior should not be duplicated in globally loaded conventions.
- Runtime, validation, drift, artifact, governance, and secret semantics are referenced from adapters, not duplicated in adapters.
- Visible modes remain limited to `ask`, `planning`, `implementation` (user-facing `implement`), `execute`, `testing`, `review`, `incident`, and `refactor`.

This placement reduces globally loaded operational text while preserving invocation guarantees.

---

## 5. Secret-Safe Invocation

Mode invocation must never display raw secrets found in loaded context, repository files, diffs, logs, validation-cases, or generated reports.

If a sensitive value is discovered, report only:
- Secret type.
- File path and line/reference when available.
- Safe masked preview.
- Security finding status.
- Rotation recommendation when the value may have been committed, logged, displayed, or copied.

Raw secrets must not be copied into `.forge/context`, inferred knowledge, unknowns, confirmations, decisions, mode files, platform context, audit reports, planning output, review comments, verification notes, or validation-cases.

---

## 6. Per-Mode Operational Expectations

### 6.1 Ask

Ask mode answers lightweight repository-understanding questions.

Expected behavior:
- Explain current code, flow, ownership, dependencies, behavior, and loaded Forge context from evidence.
- Keep answers concise and scoped.
- Separate confirmed facts, inference, assumptions, and unknowns.
- Load only the minimum task-relevant context.
- Report `CONTEXT_BUDGET_LIMITED` when safe answering requires more evidence than the normal scoped budget.
- Report `DRIFT_DETECTED` or `DRIFT_RISK` when stale context/artifacts affect the answer.
- Treat cross-repo behavior as unknown unless directly evidenced.
- No planning, mutation, redesign, or broad audit.

Interaction behavior:
- Interactive default: ask for clarification only when the question cannot be answered safely as scoped.
- Non-interactive: emit missing evidence or ambiguity instead of guessing.

### 6.2 Planning

Planning mode produces an Engineering Change Plan (ECP) by default.

Expected behavior:
- Strategic engineering planning.
- Produce an ECP artifact when persistence is useful for approved intent, confirmed decisions, blockers, boundaries, linked systems/layers, and revision reference.
- Architecture and runtime reasoning.
- Implementation phases.
- Risk and impact analysis.
- Dependency, contract, data, and topology checks when evidenced.
- Validation and rollback planning.
- WHY and IMPACT explanation.
- No implementation code by default.
- No detailed executable coding tasks by default.
- Safe proposed defaults for low-risk operational choices.
- Escalation only for blocking decisions.
- Secret findings redacted and treated as security findings.
- Smarter scoped loading with `CONTEXT_BUDGET_LIMITED` when planning cannot proceed safely within normal scope.
- Drift checks across decisions, assumptions, generated artifacts, and current repository evidence.
- Cross-repo ownership/contract uncertainty surfaced without orchestration or assumed behavior.
- Concise governance risk signals for PII/secrets, financial correctness, idempotency, retry/replay, rollback, transaction consistency, auditability, observability, and blast radius.
- Short paragraphs, operational bullets, and highlighted blockers.

Planning mode must stay layer-adaptive. It must not force backend-only, deployability, ownership, contract, or runtime topology assumptions without evidence.

Interaction behavior:
- Interactive default: ask unresolved architecture or governance decisions early.
- Non-interactive: emit a planning blocked report and continue only with allowed proposed defaults.

### 6.3 Implementation

Implementation mode converts an approved ECP/phases or a simple request into a human-reviewable execution plan.

Expected behavior:
- Clarification phase before execution-ready phase when blocking decisions exist.
- Produce an Execution Contract artifact when persistence is useful for readiness status, task cards, dependency order, stop conditions, do-not-change boundaries, acceptance criteria, and ECP reference.
- Explicit executable engineering task cards only after blockers are resolved.
- Likely files/components impacted after blockers are resolved.
- Dependency ordering after blockers are resolved.
- Migration/runtime sequencing when relevant after blockers are resolved.
- Developer-friendly, bounded task structure after blockers are resolved.
- Required readiness status: `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, or `READY_FOR_EXECUTION`.
- Practical blocker names and concrete execution values.
- Load only task-relevant layers, systems, decisions, and inferred knowledge.
- Avoid speculative redesign.
- Keep proposed defaults visible and unconfirmed.
- Do not copy raw secrets from existing config, env, logs, fixtures, or docs into code or context.
- Do not directly modify code.
- Report `CONTEXT_BUDGET_LIMITED` instead of producing execution-ready tasks when required evidence is outside normal scoped context.
- Stop or request approval when drift makes the approved plan/artifact unsafe to execute.
- Do not create tasks that assume external repo behavior or require automatic multi-repo changes.
- HIGH-risk fintech governance decisions use `NEEDS_HUMAN_APPROVAL`.

Implementation mode must not redesign architecture again, repeat full ECP reasoning, or silently redefine approved plans. It creates the human-reviewable execution boundary before code changes.

Interaction behavior:
- Interactive default: if blocking decisions affect runtime behavior, contracts/schema, DLQ/replay, idempotency, security/compliance, ownership/governance, destructive boundaries, acceptance criteria, or rollback, stop before the final breakdown and output `NEEDS_CONFIRMATION`.
- Interactive confirmation must use CLI-friendly numbered choices: blocker title, why it matters, Recommended option with reason, Alternative option with tradeoff, and reply instructions (`1 = Recommended`, `2 = Alternative`, `custom = provide explicit value`).
- For multiple blockers, list `Blocker 1`, `Blocker 2`, etc. with one-line impact, then provide the smallest set of shared or per-blocker choices needed to unblock execution.
- Use concrete wording such as `Format event Kafka yang akan diterima service` or `Nilai runtime/config yang wajib dipastikan`; avoid abstract labels such as `Inbound contract`.
- Use 2 options by default; use a third option only for major architecture tradeoffs.
- Interactive implementation mode must wait for human answers before emitting final executable tasks, allowed file modifications, acceptance criteria, or executor instructions.
- Non-interactive: do not ask questions; emit `NEEDS_CONFIRMATION` when required execution values are missing, or `READY_FOR_PARTIAL_EXECUTION` only when safe proposed-default work can proceed.

Readiness semantics:
- `NEEDS_CONFIRMATION`: blocking decisions or required execution values are missing.
- `READY_FOR_PARTIAL_EXECUTION`: only safe scaffolding or proposed-default work can proceed; production/final behavior remains blocked.
- `READY_FOR_EXECUTION`: all required execution values are concrete enough for lower-reasoning execution.
- For execution-sensitive changes, include concrete execution values before `READY_FOR_EXECUTION`.
- Human-facing output may label this as `Nilai eksekusi yang dipakai`.
- Do not use `READY_FOR_EXECUTION` when values are assumed, provided later, unknown, missing contract details, or production behavior remains pending confirmation.

Task-card semantics:
- `READY_FOR_EXECUTION` and `READY_FOR_PARTIAL_EXECUTION` output must use task cards, not long document-style breakdowns.
- Each task card must include: Task ID, Title, Priority, Impact, Scope, Depends On, Parallel Safe, Goal, Why, Likely Files, Do Not Change, Out Of Scope, Derived From, Acceptance Criteria, and Test Expectation.
- Task IDs use stable execution labels such as `IMP-001`; a repo/domain prefix such as `TRH-KAFKA-001` is allowed when obvious from approved context.
- Priority values are `P0` critical/blocking foundation, `P1` core implementation, `P2` supporting/test/docs, and `P3` optional/follow-up.
- Impact values are `HIGH` runtime/data/contract-sensitive, `MEDIUM` behavior/config/test-impacting, and `LOW` docs/local cleanup/minor support.
- Scope values should use operational areas such as runtime, transport, service, domain, persistence, testing, docs/config, or the closest evidenced repository term.
- `Depends On` must list task IDs or `none`; multi-step work must also include a short dependency order section using task IDs.
- `Parallel Safe` must be `yes`, `no`, or `after dependencies`, with a short reason when risk is not obvious.
- `Do Not Change` guardrails are required for risky runtime, data, contract, security, or broad refactor boundaries.
- `Acceptance Criteria` and `Test Expectation` must be concrete enough for a lower-reasoning executor to implement and for MR review to verify.
- Task cards are an output discipline only. They do not define a DAG engine, scheduler, agent system, workflow engine, Jira integration, story points, or tooling.

Preferred implementation output order:
1. Status.
2. `Nilai eksekusi yang dipakai` only when concrete values exist.
3. `Yang sengaja tidak diubah`.
4. Task Cards.
5. Dependency Order.
6. Parallelization Notes.
7. Ready For Execute Checklist.
8. What executor must stop on.

Blocked behavior:
- If `runtime.non_interactive=false` and blockers exist, ask confirmation first and do not emit final task cards.
- If `runtime.non_interactive=true` and blockers exist, emit a `NEEDS_CONFIRMATION` report and do not emit final task cards as execution-ready.
- Final executable task cards are invalid while critical blockers remain unresolved.

### 6.4 Execute

Execute mode performs actual repository modifications.

Expected behavior:
- Implement approved implementation tasks or approved task subsets.
- Produce an Execute Result artifact when persistence is useful for execution result, changed file groups, validation status, manual follow-up, rollback notes, and unchanged boundaries.
- Preserve repository conventions and existing architecture/runtime constraints.
- Keep changes scoped and minimal; preserve existing formatting and line endings, avoid file-wide rewrites, and do not perform unrelated cleanup.
- Load only execution-relevant context.
- Preserve proposed vs confirmed boundaries.
- Report execution result, implemented changes, changed files, validation performed, unvalidated scope, manual checks, rollback, intentionally unchanged scope, reviewer focus, hidden-change checks, and one concise recommended next action.
- `Execution Result` must use one clear status: `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_VALIDATED`.
- Before validation, check required runtime/tooling prerequisites for the commands being attempted.
- Use `SUCCESS` only when reliable validation evidence exists; otherwise use `PARTIAL_SUCCESS`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_VALIDATED` as appropriate.
- `File yang berubah` must group files by responsibility and confirm intended files changed, unrelated files did not change, and no file-wide formatting or line-ending churn occurred.
- `Validasi` must show prerequisites checked, command run, result, and failure/not-run reason. Failed or partial validation must be highlighted directly, not buried in prose.
- `Yang belum tervalidasi` must list changed or risky scope without reliable validation evidence.
- `Yang masih perlu dicek manual` must be an actionable follow-up list.
- `Cara rollback perubahan ini` must use operational wording such as disable flag, revert config, keep fallback path, and replay if needed.
- `Yang sengaja tidak diubah` must explain risky unchanged boundaries in simple wording: no database schema change, no service topology change, no direct SQL from handler, existing fallback still works.
- `Reviewer perlu fokus ke` must highlight relevant checks such as idempotency behavior, retry vs DLQ classification, lifecycle/shutdown behavior, secret-safe logging, and boundary preservation.
- `Hidden change check` must explicitly report whether database schema, deployment pipeline, shared runtime contracts, or unrelated context/runtime files changed unexpectedly.
- When API, docs, or contracts change, wording and names must be checked against relevant source files before finalizing, such as proto, OpenAPI, grpc-gateway, generated docs, route/schema files, or existing contract sources.
- When executing after review, previous review findings must be verified as resolved or explicitly still open; execute must not finalize while obvious residual review blockers remain.
- Finalization must check that changed files are intended, unrelated files are absent, file-wide formatting or line-ending churn did not occur, validation was run or honestly not run, rollback is reported, and reviewer focus is clear.
- `Recommended next action` must be short and singular, for example proceed, fix before merge, remediate first, track as later cleanup, or needs human confirmation.
- Run narrow implementation verification when relevant.
- Do not copy raw secrets from existing config, env, logs, fixtures, or docs into code or context.
- Stop, narrow scope, or report blocked status when approved tasks depend on stale artifacts or contradicted evidence.
- Do not modify multiple repositories automatically or assume cross-repo runtime behavior.
- Treat payment/transaction correctness, financial consistency, idempotency, retry/replay, rollback, and blast-radius changes as governance-sensitive; HIGH risk requires human approval.

Execute mode must not perform major architecture redesign, invent topology/contracts, broad-load unrelated context, silently redefine approved plans, or absorb testing/review responsibilities.

Preferred execute output order:
1. `Execution Result`
2. `Yang berhasil diubah`
3. `File yang berubah`
4. `Validasi`
5. `Yang belum tervalidasi`
6. `Yang masih perlu dicek manual`
7. `Cara rollback perubahan ini`
8. `Yang sengaja tidak diubah`
9. `Reviewer perlu fokus ke`
10. `Hidden change check`
11. `Recommended next action`

Interaction behavior:
- Interactive default: ask confirmation before dangerous, destructive, or runtime-impacting changes.
- Non-interactive: stop safely and emit a blocked report.

### 6.5 Testing

Testing mode owns testing cognition and test-focused repository changes.

Expected behavior:
- Unit test strategy and test implementation guidance.
- Produce a Testing Result artifact when persistence is useful for testing result, validated scope, blockers, automated/manual validation, coverage gaps, and runtime-sensitive validation.
- Integration testing strategy.
- E2E, smoke, rollback, migration, runtime validation, and contract validation when relevant to the approved change.
- Mock, fake, stub, fixture, and test isolation reasoning.
- Regression validation and coverage reasoning.
- Operational verification and environment/test dependency considerations.
- Required testing status: `PASSED`, `FAILED`, `PARTIAL`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_RUN`.
- Required output sections: `Testing Result`, `Scope yang divalidasi`, `Automated validation`, `Environment/runtime blockers`, `Yang belum tervalidasi`, `Yang masih perlu dicek manual`, `Reviewer perlu fokus ke`, and `Risk summary`.
- Scope grouping by unit, integration, e2e, smoke, rollback, migration, runtime validation, and contract validation, omitting irrelevant categories without flattening the report.
- Contract traceability to the confirmed execution contract, approved behavior, rollback assumptions, retry/idempotency semantics, runtime boundaries, and non-regression expectations.
- Runtime/tooling prerequisite checks before validation commands that depend on tooling or infra.
- Clear separation between implementation/test failures and environment/tooling blockers.
- Clear separation between automated checks, manual validation, infra-dependent validation, and production-like verification.
- Test placement guidance: colocate unit tests near target packages/files; when no repo convention exists, prefer top-level `testing/integration`, `testing/e2e`, `testing/mocks`, `testing/fixtures`, and `testing/helpers` for non-unit concerns.
- Existing repository test conventions take precedence over the recommended layout and should be reported when detected.
- Retryable failure, non-retryable failure, DLQ, duplicate/idempotent replay, partial replay, rollback, and proposed-default path validation where relevant.
- Drift reporting when test expectations, execution contracts, context, or artifacts contradict current repository evidence.
- Cross-repo contract validation only when external evidence is available; otherwise mark external behavior as unvalidated.
- Fintech-sensitive validation gaps for financial correctness, transaction consistency, idempotency, retry/replay, rollback, auditability, observability, and blast radius.
- Identification of missing coverage.
- Reviewer-oriented visibility into unvalidated risk areas, missing coverage, risky runtime assumptions, and runtime-sensitive behavior not verified.
- Test evidence reporting with secret redaction.

Testing mode may create or modify tests when requested. It must not become generic architecture planning, replace review mode, or broadly redesign implementation.

Interaction behavior:
- Interactive default: ask unresolved validation expectations only when needed.
- Non-interactive: emit an unresolved validation report and continue only with allowed proposed defaults.

### 6.6 Review

Review mode evaluates correctness and risk.

Expected behavior:
- Correctness review.
- Produce a Review Result artifact when persistence is useful for review result, MR readiness, critical/major findings, reviewer focus, rollback/safety notes, and suggested next action.
- Regression and operational risk detection.
- Topology, runtime, data, and contract consistency checks when relevant.
- Evidence-based critique with explicit uncertainty.
- Senior MR-review framing: acceptability, required fixes, risky areas, reviewer focus, and MR readiness.
- Detection of unconfirmed proposed defaults.
- Detection of accidental promotion from proposed assumption to confirmed behavior.
- Verification of execute results.
- Required review status: `APPROVED`, `NEEDS_CHANGES`, `BLOCKED`, or `PARTIAL_REVIEW`.
- Required MR readiness: `MR-ready`, `not MR-ready`, `MR-ready with accepted risk`, or `cannot determine`.
- Required severity grouping: `CRITICAL`, `MAJOR`, `MINOR`, and `INFO`.
- `CRITICAL` and `MAJOR` findings include affected file/area, what is wrong, why it matters, and suggested fix.
- Required output sections: `Review Result`, `MR readiness`, `Critical findings`, `Major findings`, `Minor findings`, `Info / observations`, `Reviewer perlu fokus ke`, `Yang belum tervalidasi`, `Rollback / safety notes`, and `Suggested next action`.
- Assessment of whether execute/testing status claims are supported by validation evidence.
- Findings for hidden validation gaps, ambiguous partial success, missing prerequisite checks, or production-ready/test-passed claims without evidence.
- Detection of accidental architecture or contract drift: execution contract violation, boundary violation, hidden topology redesign, service/repository boundary bypass, or unapproved contract/schema change.
- Safety checks for secret/raw payload logging, PII exposure, retry/DLQ correctness, idempotency correctness, rollback readiness, and validation honesty when relevant.
- Drift checks across code, context, execution contracts, decisions, assumptions, and generated artifacts when material to MR readiness.
- Cross-repo findings limited to evidenced scope; external ownership/contract uncertainty remains unvalidated scope or a finding.
- Fintech governance checks for financial correctness, transaction consistency, replay/rollback safety, auditability, observability, and blast radius when relevant. HIGH-risk governance issues cannot be approved automatically.
- Assessment of test evidence, residual regression risk, and coverage gaps without replacing testing mode.
- Raw secret exposure in diffs, reports, generated context, or comments is a security finding.

Review mode must not treat unevidenced concerns as confirmed defects, become testing mode, emit full test plans, or turn findings into implementation task lists.

Interaction behavior:
- Interactive default: ask review-scope clarification only when necessary.
- Non-interactive: emit a review ambiguity report.

### 6.7 Incident

Incident mode diagnoses bugs, issues, and incidents.

Expected behavior:
- Identify symptom, impact, affected flow, likely root cause, mitigation, rollback, and next checks.
- Produce an Incident artifact when persistence is useful for incident summary, likely root cause, affected systems, mitigation, rollback possibility, and next checks.
- Distinguish symptom from cause.
- Use cause statuses: `LIKELY_CAUSE`, `POSSIBLE_CAUSE`, or `NEEDS_MORE_EVIDENCE`.
- Include confidence level for cause and mitigation statements.
- Never claim root cause without evidence.
- Preserve uncertainty between evidence, hypotheses, unknowns, and proposed mitigations.
- Use logs, traces, metrics, configs, contracts, migrations, recent changes, and runbooks only when relevant.
- Report drift when runbooks, context, or artifacts conflict with current code/config evidence.
- For cross-repo dependencies, report external ownership/contract uncertainty and avoid claims about another repo's runtime behavior without evidence.
- For fintech incidents, surface PII/secrets, financial correctness, idempotency, retry/replay, rollback, transaction consistency, auditability, observability, and blast-radius risks as concise operational signals.
- Redact secrets from operational evidence.
- No speculative redesign, topology invention, or architecture rewrite.

Interaction behavior:
- Interactive default: ask only for missing incident evidence that blocks diagnosis or mitigation.
- Non-interactive: emit an incident ambiguity or blocked report.

### 6.8 Refactor

Refactor mode owns safe technical debt improvement.

Expected behavior:
- Improve code conservatively within a bounded scope while preserving behavior.
- Produce a Refactor artifact when persistence is useful for problem areas, proposed safe improvements, risk areas, out-of-scope redesigns, and recommended execution boundaries.
- Prefer local simplification, duplication removal, naming cleanup, and existing convention alignment.
- Classify risk as `LOW`, `MEDIUM`, or `HIGH`.
- Prioritize LOW-risk behavior-preserving improvements.
- HIGH-risk refactors require a planning/implementation path before execution.
- Identify behavior-preservation evidence and validation expectations.
- Report drift when current code contradicts stale context/artifacts about debt or behavior.
- Do not assume external repo contracts or modify multiple repos as part of refactor.
- For fintech-sensitive code, treat financial correctness, transaction consistency, idempotency, retry/replay, rollback, auditability, observability, and blast radius as governance-sensitive.
- No architecture rewrite, paradigm migration, hidden behavior change, or unrelated cleanup.

Interaction behavior:
- Interactive default: ask or stop before broad, risky, destructive, contract-changing, or runtime-impacting refactors.
- Non-interactive: stop safely when behavior preservation cannot be established.

### 6.9 Lower-Cost Execution Philosophy

After architecture reasoning, unknown classification, and task-card decomposition are complete, execute mode should be more deterministic and less reasoning-heavy. It is suitable in principle for lower-cost execution-oriented models that follow an approved task plan.

This protocol does not add model routing, tool orchestration, automation tooling, runtime executors, or agent services.

---

## 7. Loading-Delta Behavior

Forge preserves a loading-delta philosophy:

- Core context is always loaded.
- Mode files describe only what changes for that mode.
- Modes do not re-list core.
- Related layers and systems are loaded by task relevance, not by default breadth.
- `on_demand` is a conditional expansion path, not a second default include list.
- `exclude` protects unrelated context from accidental loading.

Broad-loading the entire context tree is a violation unless the user requests a whole-repo/context audit or the task explicitly requires full coverage.

---

## 8. Evidence, Inference, Proposed, and Unknown Preservation

During invocation, assistants must preserve Forge's epistemic boundaries:

- Evidence-backed claims cite or reference loaded evidence.
- Inferences are labeled as inferred and remain non-authoritative.
- Assumptions are temporary and must not become facts.
- Unknowns are surfaced instead of guessed.
- Proposed defaults are safe operational assumptions, not confirmed facts.
- Secret evidence is preserved only as type, path, line/reference, and masked preview.
- Missing topology, ownership, contracts, integration behavior, deployment ownership, and business rules remain unknown unless evidenced.

If a task cannot proceed without missing evidence, the assistant reports the blocker or records the unknown according to runtime conventions. If a task can proceed with a proposed default, the assistant labels the default and keeps the confirmation boundary visible.

---

## 9. Loaded-Context Reporting

Each mode invocation should report:

- Concise scoped-context confirmation when useful.
- Included or on-demand context areas only when they affect the result.
- Missing evidence and unresolved ambiguity.
- Blocking unknowns, proposed defaults, and informational unknowns when present.
- Redacted security findings when secrets are detected.
- Whether the mode was insufficient when that affects the task.

Normal runtime output should not include large internal loading dumps. Maintainer-facing validation may require fuller detail.

---

## 10. Forbidden Behaviors

The following are invalid mode invocation behavior:

- Ignoring the requested mode file.
- Invoking a mode without first reading `.forge/forge.config.yaml`.
- Failing to detect, report, or apply `runtime.non_interactive`.
- Failing to report a `runtime.profile` / `runtime.non_interactive` conflict before mode work.
- Treating `runtime.profile` as a second interaction flag instead of metadata controlled by `runtime.non_interactive`.
- Emitting automation-style blocked reports in interactive repositories instead of ask-first clarification.
- Asking conversational clarification questions in non-interactive repositories.
- Auto-approving HIGH-risk decisions.
- Using orchestrator authority without explicit `runtime.decision_authority: orchestrator`.
- Omitting decision trace for automation-selected LOW defaults or orchestrator-selected MEDIUM decisions.
- Treating decision traces as workflow state, dependency state, scheduler input, retry policy, or execution graph.
- Using reserved `ci` profile to introduce CI/CD, deploy, release, pipeline, trigger, or runtime executor behavior.
- Loading broad `.forge/context` by default.
- Treating modes as optional suggestions.
- Treating `on_demand` entries as unconditional defaults.
- Ignoring `exclude`.
- Exceeding the normal scoped `token_budget` range without a task-specific evidence reason.
- Inventing topology, ownership, contracts, integrations, deployment ownership, APIs, databases, or business rules without evidence.
- Printing, copying, summarizing, or storing raw secrets.
- Including raw secrets in `.forge/context`, reports, validation-cases, reviews, tests, decisions, confirmations, unknowns, inferred knowledge, modes, or platform context.
- Treating a proposed default as confirmed.
- Asking broad questionnaires when a minimal decision prompt is enough.
- Requiring interactive input in automation/non-interactive mode.
- Generating open-ended architecture option lists instead of bounded decision options.
- Producing RFC/audit-style narrative when concise operational structure is enough.
- Prominently exposing runtime/debug/loading internals in normal interactive output.
- Dumping changed files without grouping them by responsibility when grouping is feasible.
- Emitting execute output without a clear execution result status.
- Burying failed, skipped, or partial validation inside prose.
- Emitting `SUCCESS` without clear validation status and evidence.
- Treating missing runtime/tooling/infra as an implementation failure instead of `BLOCKED_BY_ENVIRONMENT`.
- Omitting validation gaps or unvalidated scope after code changes.
- Using ambiguous `PARTIAL_SUCCESS` semantics.
- Skipping runtime prerequisite checks when validation depends on tooling or infra.
- Omitting testing or review statuses, or using status vocabularies inconsistently.
- Claiming fully validated, production-ready, or test-passed without supporting evidence.
- Emitting testing output without the required testing sections or status.
- Mixing automated validation, manual validation, infra-dependent validation, and production-like verification ambiguously.
- Burying environment/runtime blockers in prose instead of surfacing them directly.
- Ignoring retry, DLQ, idempotency, replay, or runtime-sensitive paths when the system is event-driven or runtime-sensitive.
- Letting testing output become generic QA documentation or review/governance critique.
- Emitting review output without `Review Result`, clear MR readiness, severity-grouped findings, reviewer focus, unvalidated scope, rollback/safety notes, and suggested next action.
- Emitting `CRITICAL` or `MAJOR` review findings without affected file/area, what is wrong, why it matters, and suggested fix.
- Letting review output become a generic audit/report, a full testing plan, or an implementation task breakdown.
- Skipping architecture/contract drift checks for non-trivial review scope.
- Skipping relevant review safety checks for secrets/raw payloads, PII, retry/DLQ, idempotency, rollback readiness, or validation honesty.
- Omitting rollback for runtime-impacting execute changes.
- Omitting unchanged-boundary reporting for risky execute changes.
- Omitting reviewer focus for non-trivial execute changes.
- Exposing excessive runtime interaction, bootstrap, loading, or debug details in normal execute output.
- Collapsing ask, planning, implementation task decomposition, execute, testing, review, incident, and refactor into generic reasoning behavior.
- Allowing planning to collapse into detailed executable task lists.
- Allowing implementation mode in interactive repositories to emit final executable tasks while critical blockers remain unresolved.
- Allowing implementation mode to hide blocking decisions at the end of a full breakdown.
- Allowing implementation readiness output without bounded task cards.
- Allowing ready task cards without task ID, priority, impact, dependencies, acceptance criteria, or risky-change guardrails.
- Treating implementation task cards as automation, orchestration, scheduling, DAG, agent, Jira, story-point, or workflow-engine semantics.
- Allowing interactive implementation confirmation without `NEEDS_CONFIRMATION`, Recommended/Alternative choices, or clear numbered reply instructions.
- Marking implementation output `READY_FOR_EXECUTION` while required execution values are conditional, unavailable, unresolved, or pending confirmation.
- Emitting final executor instructions without concrete execution values for execution-sensitive changes.
- Allowing implementation to directly modify code.
- Allowing execute to redefine approved architecture or task intent.
- Allowing execute to absorb testing responsibilities entirely.
- Allowing review to collapse into testing or replace test strategy/test implementation work.
- Allowing ask to become planning, review, audit, or mutation.
- Allowing incident to become speculative redesign.
- Allowing refactor to hide behavior changes, architecture rewrites, or paradigm migrations.
- Duplicating mode-specific execution behavior in globally loaded conventions.
- Replacing repository-owned code/docs/ADRs with Forge-generated cognition.
- Treating lifecycle artifacts as source of truth over repository code, docs, ADRs, or human confirmations.
- Persisting hidden chain-of-thought, raw secrets, unnecessary conversation history, or generic long-form summaries in lifecycle artifacts.
- Using artifact links as orchestration, DAG, workflow, scheduler, agent-memory, execution-trigger, or dependency-management semantics.
- Creating unclear artifact ownership or generic artifacts not owned by a mode.
- Adding automation/tooling/runtime execution under the guise of protocol compliance.
- Introducing agent loops, auto-retry orchestration, scheduler behavior, workflow graph execution, DAG execution, deploy/release automation, CI pipeline execution, or autonomous multi-step chaining.
- Introducing any conflicting interaction or workflow flag.

---

## 11. Validation Expectations

Mode invocation validation checks that runtime behavior follows this protocol:

- `.forge/forge.config.yaml` was read before the requested mode file.
- `runtime.profile`, `runtime.non_interactive`, and decision authority were detected.
- `runtime.non_interactive` was applied as the controlling interaction behavior.
- Profile/non-interactive conflicts were reported clearly before mode work.
- The requested mode file was read before mode-specific context loading.
- `include`, `on_demand`, `exclude`, `token_budget`, and `notes` were considered.
- Loaded context was scoped to the task.
- Broad-loading violations were reported or avoided.
- Ask, planning, implementation, execute, testing, review, incident, and refactor retained distinct operational behavior.
- Visible modes were constrained to `ask`, `planning`, `implementation`/`implement`, `execute`, `testing`, `review`, `incident`, and `refactor`.
- Ask answered lightweight repo-understanding questions without planning, mutation, redesign, or broad audit.
- Planning produced strategic ECP/phases without detailed executable coding tasks.
- Implementation used clarification phase before execution-ready phase when blocking decisions were present.
- Implementation produced executable task cards with likely file/component visibility and dependency ordering only after critical blockers were resolved.
- Execute owned actual repository modification behavior and did not silently redefine approved plans.
- Testing remained visible and distinct from execute/review, with test strategy, test implementation guidance, coverage, mocks/fakes/stubs, and regression validation responsibilities.
- Review assessed correctness/risk and execute results without replacing testing mode.
- Incident diagnosed symptoms, impact, affected flow, root cause, mitigation, rollback, and next checks without speculative redesign.
- Refactor remained conservative, bounded, and behavior-preserving.
- Architecture reasoning and execution reasoning remained separated.
- Mode-specific behavior lives in mode files rather than globally loaded conventions.
- Evidence, inference, and unknown boundaries were preserved.
- Unknowns were classified as blocking, proposed-default, or informational.
- Proposed defaults were explicitly labeled and not promoted to confirmed facts.
- Non-interactive behavior used blocking status output instead of interactive questions.
- `runtime.non_interactive` existed, was boolean, and defaulted to `false`.
- No conflicting interaction flags existed.
- Interactive repositories used ask-first clarification for blocking decisions instead of automation-style blocked reports.
- Non-interactive repositories avoided conversational questions and emitted the selected mode's allowed blocking/readiness status when blocked.
- Automation-safe output used `NEEDS_CONFIRMATION`, `BLOCKED`, or `NEEDS_HUMAN_APPROVAL` for decisions it could not safely make.
- HIGH-risk decisions were not auto-approved and required human confirmation.
- Orchestrator authority was used only when explicitly configured.
- Automation-selected LOW defaults and orchestrator-selected MEDIUM decisions included decision trace with decision, selected option, authority used, risk level, reason, and affected tasks/artifacts.
- Interactive implementation mode did not emit final executable tasks, allowed file modifications, acceptance criteria, or executor instructions while critical blockers remained unresolved.
- Interactive implementation mode did not bury blockers at the end of a full breakdown.
- Interactive implementation confirmation used `NEEDS_CONFIRMATION`, Recommended and Alternative choices, reasons/tradeoffs, and clear reply instructions.
- Interactive implementation confirmation explained why the decision mattered and used concrete engineering language.
- Interactive implementation confirmation used 2 options by default and at most 3 for major architecture tradeoffs.
- Implementation output included one readiness status: `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, or `READY_FOR_EXECUTION`.
- `READY_FOR_EXECUTION` appeared only with concrete required execution values and no conditional/unavailable value language.
- Execution-sensitive `READY_FOR_EXECUTION` output included concrete execution values before final executor instructions.
- `READY_FOR_EXECUTION` and `READY_FOR_PARTIAL_EXECUTION` output included task cards with Task ID, Title, Priority, Impact, Scope, Depends On, Parallel Safe, Goal, Why, Likely Files, Do Not Change, Out Of Scope, Derived From, Acceptance Criteria, and Test Expectation.
- Multi-step implementation output included Dependency Order and Parallelization Notes using task IDs.
- Final task cards were absent from blocked interactive confirmation output and absent from non-interactive blocked reports marked as execution-ready.
- Execute output used one clear status: `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_VALIDATED`.
- Execute status matched validation evidence and did not use `SUCCESS` when reliable validation was absent.
- Execute output prioritized result, changed files grouped by responsibility, validation, unvalidated scope, manual checks, rollback, intentionally unchanged scope, reviewer focus, and hidden-change checks.
- Execute output included one concise recommended next action after drift, risk, partial validation, or residual manual checks.
- Execute finalization confirmed intended files changed, unrelated files were absent, file-wide formatting/line-ending churn was absent, validation was run or honestly not run, rollback was reported, and reviewer focus was clear.
- Execute checked contract/docs/API wording against source files when API, docs, or contract surfaces changed.
- Execute after review verified prior findings were resolved or explicitly still open and did not finalize with obvious residual blockers.
- Execute validation failures, skipped validation, and partial validation were highlighted directly.
- Execute/testing prerequisite checks were reported when validation depended on tooling or infra.
- Environment/tooling blockers were classified as `BLOCKED_BY_ENVIRONMENT`, separate from implementation failures and contract/runtime blockers.
- Testing output used one clear status: `PASSED`, `FAILED`, `PARTIAL`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_RUN`.
- Testing output used the required sections and grouped validation scope by relevant test category.
- Testing output separated automated, manual, infra-dependent, and production-like validation.
- Testing output traced checks to the confirmed execution contract where evidence existed.
- Runtime-sensitive testing addressed retry, DLQ, idempotency, replay, runtime boundaries, and rollback assumptions when relevant.
- Testing output surfaced coverage gaps, unvalidated risks, and reviewer focus without becoming review mode.
- Review output used one clear status: `APPROVED`, `NEEDS_CHANGES`, `BLOCKED`, or `PARTIAL_REVIEW`.
- Review output stated one MR readiness result: `MR-ready`, `not MR-ready`, `MR-ready with accepted risk`, or `cannot determine`.
- Review findings were grouped by `CRITICAL`, `MAJOR`, `MINOR`, and `INFO`.
- `CRITICAL` and `MAJOR` review findings included affected file/area, what is wrong, why it matters, and suggested fix.
- Non-trivial review checked execution contract adherence, boundary preservation, topology drift, service/repository boundary bypass, and unapproved contract/schema changes.
- Review checked relevant safety risks including secret/raw payload logging, PII exposure, retry/DLQ, idempotency, rollback readiness, and validation honesty.
- Review output stayed concise and MR-oriented without becoming testing mode, a generic audit, or an implementation task list.
- Validation sections separated executed checks, failures, blocked/not-run checks, remaining unvalidated scope, and manual action.
- Runtime-impacting execute changes included rollback guidance.
- Risky execute changes reported intentionally unchanged boundaries.
- Non-trivial execute changes included reviewer focus.
- Changing runtime interaction behavior did not require context re-init or repository cognition rewrite.
- Human decision prompts followed option-count discipline.
- Raw secret exposure was absent from generated context and reports.
- Secret findings were redacted, classified as security findings, and included rotation guidance when exposure was possible.
- Context loading details stayed concise in normal output.
- Missing evidence and unresolved ambiguity were reported.
- Mode sufficiency was evaluated.
- Lifecycle artifacts, when used, stayed mode-owned, bounded, human-readable, link-only, non-authoritative, and free of chain-of-thought/raw secrets.
- Artifact references did not imply orchestration, workflow, DAG, scheduler, agent memory, execution triggers, persistent AI memory, or knowledge graph behavior.
- Runtime profile and automation-safe semantics did not imply agent loops, auto-retry orchestration, scheduler behavior, workflow graph execution, DAG execution, deploy/release automation, CI pipeline execution, runtime executors, or autonomous multi-step chaining.

These expectations may be validated manually today and automated later.

---

## 12. Future Compatibility Direction

The protocol is compatible with future support for:

- Automatic mode invocation.
- Invocation tracing.
- Loading reports.
- Dry-run loading previews.
- Token budget discipline and reporting.
- Invocation telemetry.
- Bounded artifact handoff references.
- Runtime profile metadata for local/automation behavior.

No automation tooling, runtime executor, telemetry collection, orchestration, scheduling, DAG, workflow engine, Jira integration, story-point system, persistent AI memory, knowledge graph, CI/CD pipeline, deploy/release automation, trigger system, autonomous loop, or agent service is introduced by this protocol.
