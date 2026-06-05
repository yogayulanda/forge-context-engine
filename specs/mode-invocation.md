# Mode Invocation Protocol

| Field | Value |
|---|---|
| Document | Forge Mode Invocation Protocol |
| Version | 3.4 |
| Date | 2026-06-05 |
| Status | `decision` |
| Scope | Framework-level protocol for invoking Forge modes |
| Dependency | `runtime/.forge/context/00-meta/conventions.md`, `runtime/.forge/context/modes/*.md`, `runtime/skills/*/SKILL.md`, `specs/context-validation.md`, `specs/artifact-lifecycle.md`, `specs/adapter-command-foundation.md` |

---

## 0. Purpose

Mode invocation defines how an AI assistant uses Forge mode files during `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context` work.

The protocol ensures:
- Mode files are operational contracts, not optional hints.
- Context loading remains scoped and delta-based.
- `run.interaction` controls manual vs automation-safe behavior globally.
- Policy-controlled high-risk decisions require human confirmation.
- Evidence, inference, proposed-default, and unknown boundaries survive task execution.
- Unknowns are classified into blocking, proposed-default, or informational behavior.
- Sensitive values are redacted before output or context write.
- Runtime repositories receive concise, scannable engineering communication.
- Execute reports expose status, validation, rollback, review focus, and hidden-change checks without narrative noise.
- Runtime validation checks prerequisites before commands and separates implementation failures from environment/tooling blockers.
- Partial, blocked, and not-validated outcomes are first-class statuses where each mode owns the vocabulary for that outcome.
- Validation activity provides structured, contract-aware evidence grouped by test scope and runtime risk inside execute/review workflows.
- Review mode behaves like a concise senior review report with clear verdict, diff coverage, severity, evidence, lifecycle boundary assessment, and safety risk.
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
v3.3 clarifies read-only mode boundaries, normal prompt UX for plan/implementation/review, `ui.language` behavior for narration versus project artifacts, and chat-first artifact persistence. It does not add modes, CLI redesign, runtime agent behavior, schedulers, CI/CD, memory, or vector storage.
v3.4 adds a lightweight `Context Impact` review contract, reviewable `.forge/context-patches/...` proposal shape, and bounded verify-context patch/quality checks. It does not add modes, CLI commands, runtime agent behavior, schedulers, CI/CD, memory, or vector storage.

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
3. `run.interaction`, output/write/failure behavior, and policy confirmation boundaries detected.
4. `run.interaction` applied as the controlling behavior.
5. Mode file read from `.forge/context/modes/<mode>.md`.
6. `include`, `on_demand`, `exclude`, `token_budget`, and `notes` parsed.
7. Scoped context loaded according to the mode delta.
8. Task executed according to mode behavior and run interaction behavior. For `plan`, human approval is required before `implementation` proceeds. For `implementation`, human approval of the ECP is required before `execute` proceeds.
9. Policy confirmation boundaries applied before any important decision.
10. Runtime/tooling prerequisites checked before validation or testing commands when such commands depend on tooling/infra.
11. Validation evidence separated from validation gaps, blocked commands, and manual follow-up.
12. Evidence / inference / proposed-default / unknown boundaries preserved.
13. Unknowns classified by operational impact.
14. Missing evidence and unresolved ambiguity reported.
15. Loading details reported only as concise scoped-context confirmation when useful.
16. Mode sufficiency evaluated when it affects the result.
17. Lifecycle artifacts referenced or written only when useful for bounded continuity.
18. Read-only mode boundaries are enforced by the selected mode contract; users do not need to restate "Do not edit files" for normal plan, implementation, or review usage.

Mode invocation is successful only when the assistant can explain what mattered for the task, what evidence was missing, and whether the selected mode was enough. Normal interactive output should not expose full runtime/bootstrap detail.

Canonical workflow:

```
forge-plan
-> human approval (Plan: proposed -> approved)
-> forge-implementation
-> human approval (ECP: proposed -> approved)
-> forge-execute
-> forge-review
-> optional forge-verify-context
-> scoped fix loop when review returns request_changes
```

Each transition between plan output and implementation, and between ECP output and execution, requires explicit human approval. Assistants must not proceed to the next mode without that signal.

Read-only core mode UX:
- `plan` is read-only by definition.
- `implementation` is read-only by definition.
- `review` is read-only unless the human separately approves a follow-up execution flow.
- `execute` is the only core mode that may edit files, and only from approved scope.
- Safety-probe prompts may still say `Do not edit files`, but that phrase is optional rather than required for correct Forge behavior.

`ask` is an entry mode, not a mandatory lifecycle stage. Incident, refactor, and test-focused requests are workflow scenarios that use the core lifecycle modes as needed. Small, well-understood changes may skip `plan`. Execution may operate on approved task subsets.

See `docs/workflow.md` for the narrative walkthrough, approval gate UX, and post-review fix loop.

---

## 2. Global Invocation Rules

All modes follow these rules:

- Read `.forge/forge.config.yaml` before reading the requested mode file.
- Detect `run.interaction`, output/write/failure behavior, workflow defaults, and policy confirmation boundaries without requiring the user to mention them.
- Apply `run.interaction` as the single controlling interaction setting.
- Then read the requested mode file before loading mode-specific context.
- Treat relevant core context as selectively loadable from `00-meta/*` and `01-core/*`.
- Treat mode files as loading deltas on top of core.
- Treat `run.interaction: manual` as the interactive default.
- Treat `run.interaction: auto` as automation-safe behavior.
- Do not infer CI/CD, pipeline, deploy, release, trigger, executor, or orchestration behavior from any run setting.
- Report unsupported or conflicting run fields clearly and continue only when the remaining policy allows it.
- Load `include` entries normally when relevant to the task.
- Load `on_demand` entries only when task scope requires them.
- Do not load `exclude` entries unless the user explicitly changes scope.
- Use `token_budget` as the target scoped context budget for the mode.
- Treat `token_budget` as a target operating range, not a blind hard cap.
- Follow `notes` for concise operational guidance.
- Do not broad-load `.forge/context` by default.
- Prefer direct repository evidence over broad context loading.
- Expand context only with a concrete reason tied to task relevance, missing evidence, drift risk, cross-repo uncertainty, incident blast radius, refactor risk, or governance risk.
- Emit `CONTEXT_BUDGET_LIMITED` when required evidence may exceed the normal scoped budget and Forge cannot safely answer, plan, implement, execute, review, verify context, or handle the requested scenario without more context.
- Keep evidence-backed facts, inferences, proposed defaults, assumptions, and unknowns separate.
- Keep proposed defaults clearly marked as unconfirmed; when the section heading already signals uncertainty, concise readable wording is preferred over repeating the same label on every bullet.
- Redact secrets before reporting evidence, findings, plans, reviews, tests, or loaded context.
- Keep context-loading details terse in normal output; `Scoped context loaded` plus the relevant areas is enough when useful.
- Report missing evidence and unresolved ambiguity before relying on guesses.
- State whether the requested mode was insufficient when that affects the task.
- Treat lifecycle artifacts as generated continuity helpers; never treat them as source of truth over repository evidence.
- Keep mode-boundary statements separate from assumptions in human-facing plan/ECP/review outputs.

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

Workspace-aware loading rules:
- Start from the current repo context for repo-scoped work.
- Load `.forge/workspace.yaml` and workspace summary context only when the task spans multiple repos/services, integration boundaries, ownership, dependency flow, or cross-repo planning.
- When workspace context is loaded, treat it as a coordination layer only; service repo `.forge/context` remains authoritative for service facts.
- For cross-repo work, load the workspace summary first and then only the relevant linked service contexts needed for the current task.
- Broad-loading all linked repos by default is forbidden.
- Cross-repo claims should cite which repo or workspace context source the claim came from.

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

## 3. Run Interaction, Unknown Classification, and Decision Protocol

Forge uses exactly one run setting for interaction behavior: `run.interaction`.

| Value | Behavior |
|---|---|
| `manual` | Interactive-first default. Forge may ask concise clarification questions for blocking decisions and continues after human confirmation. |
| `auto` | Automation-safe behavior. Forge must not ask conversational questions and must emit structured `NEEDS_CONFIRMATION`, `BLOCKED`, or `NEEDS_HUMAN_APPROVAL` for decisions it cannot safely make. |

Other `run` fields shape output, write behavior, and failure handling. They do not define lifecycle stages, orchestration, CI/CD, deploy/release automation, triggers, or runtime executors.

Decision authority is not an active config knob. Important decisions are governed by `policy.require_human_confirmation_for`.

Decision risk levels:

| Risk | Meaning | Runtime behavior |
|---|---|---|
| `LOW` | Reversible, local, no contract/security/data correctness impact. | AI may continue with a proposed default. |
| `MEDIUM` | Operational behavior, config, or runtime behavior. | Needs confirmation when policy requires it or when the decision is not safely reversible. |
| `HIGH` | Security/compliance, PII/secrets, financial correctness, destructive migration, production topology, contract authority, or rollback-risky change. | Requires human confirmation; automation stops with `NEEDS_HUMAN_APPROVAL`. |

Automation-selected LOW defaults and confirmed important decisions must include a concise decision trace:
- Decision.
- Selected option.
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

Changing `run.interaction` never re-initializes context, rewrites repository cognition, invalidates assumptions, modifies inferred knowledge, or rewrites systems, layers, or core files.

### 3.1 Proposed Default Semantics

AI may define proposed defaults only when the choice is low-risk, operationally conventional, reversible, non-authoritative, not topology-defining, and not compliance/security defining.

Each proposed default must state:
- Proposed value.
- Reason for the proposal.
- Status: `proposed`, `not confirmed`.
- Required confirmation before production finalization when an owner/producer/platform decision is needed.

## 3.2 Human UX Rules

Forge output should read like practical engineering workflow communication, not an AI framework audit.

`ui.language` applies to narration, progress updates, and explanations. Copyable/project artifacts stay English by default unless the user explicitly requests another language. Commands, file paths, config keys, code identifiers, and status enums remain verbatim.

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

`NEEDS_HUMAN_APPROVAL` means required decision risk is HIGH or automation/orchestrator authority is insufficient. It is not an execution-ready state.

Validation sections must separate:
- What prerequisites were checked.
- What commands or checks were executed.
- What failed.
- What could not run.
- What remains unvalidated.

Manual actions must be explicit and operational, for example: `Jalankan go test ./... setelah Go toolchain tersedia`, `Validasi Kafka integration membutuhkan broker aktif`, or `Replay/DLQ flow belum tervalidasi manual`.

Status claims must never imply fully validated, production-ready, or test-passed unless the report contains evidence for that claim.

Validation reports inside execute/review workflows must use this output order when validation evidence is requested:
1. `Validation Result`
2. `Scope yang divalidasi`
3. `Automated validation`
4. `Environment/runtime blockers`
5. `Yang belum tervalidasi`
6. `Yang masih perlu dicek manual`
7. `Reviewer perlu fokus ke`
8. `Risk summary`

Validation scope must be grouped by applicable category: unit, integration, e2e, smoke, rollback, migration, runtime validation, and contract validation. Automated checks, manual validation, infra-dependent validation, and production-like verification must not be mixed ambiguously.

Contract-aware validation checks the approved ECP where possible: approved behavior, rollback assumptions, retry/idempotency semantics, runtime boundaries, and non-regression expectations. Event-driven or runtime-sensitive validation must explicitly address retryable failure behavior, non-retryable failure behavior, DLQ expectations, duplicate/idempotent replay, and partial replay when relevant.

Review reports must use this output order:
1. `Review Report`
2. `Verdict`
3. `Mode Boundary`
4. `Diff Reviewed`
5. `Summary`
6. `Critical Findings`
7. `Major Findings`
8. `Minor Findings`
9. `Validation Result Assessment`
10. `Lifecycle Boundary Assessment`
11. `Security / Risk Assessment`
12. `Context Impact`
13. `Recommended Next Step`

Review findings must be grouped by severity: `CRITICAL`, `MAJOR`, `MINOR`, and `INFO`. Each `CRITICAL` or `MAJOR` finding must include affected file/area, what is wrong, why it matters, and suggested fix.

`Context Impact` is a small per-task review section, not a full context quality audit. It must include:
- `update_needed: true | false | unknown`
- `reason:`
- `affected_context_files:`
- `suggested_context_patch:` with either `none` or `.forge/context-patches/<date>-<slug>.md`

Use `update_needed: false` for internal-only or temporary changes that do not affect durable repository knowledge, such as pure refactors without behavior change, local test-only improvements, formatting-only changes, small helper extraction preserving behavior, one-off execution reports, or generated artifacts with no durable context value.

Use `update_needed: true` when the reviewed change affects durable repository knowledge, such as architecture boundaries, public API behavior, domain rules, security boundaries, operational conventions, repository structure, service/system responsibilities, dependency/provider behavior, testing/validation conventions, workflow conventions, or durable decisions/constraints.

Use `update_needed: unknown` when evidence is insufficient to determine whether durable context should change.

When `update_needed: true`, review mode proposes a reviewable `.forge/context-patches/<date>-<slug>.md` patch instead of mutating `.forge/context` directly. The proposal should include target context files, reason, evidence, proposed update or diff, confidence, and promotion notes that require human review before promotion into `.forge/context`.

`Diff Reviewed` must name the files or diff surfaces actually inspected. If no diff or changed-file evidence is available, the report must say that explicitly and should usually return `needs_more_validation`.

`Recommended Next Step` must preserve human control. Avoid wording that implies Forge will commit, push, merge, or open MR/PR actions automatically. Safe wording includes:
- Human decides whether to commit, open MR/PR, request changes, or discard the change.
- When the verdict is `accept`, human may proceed with the normal repo workflow outside Forge.

Review mode must check architecture/contract compliance for non-trivial changes: execution contract adherence, approved boundary preservation, absence of hidden topology redesign, no service/repository boundary bypass, and no unapproved contract/schema changes. Review mode must also check relevant safety risks: secret/raw payload logging, PII exposure, retry/DLQ correctness, idempotency correctness, rollback readiness, and validation honesty.

## 3.4 Lifecycle Artifact Semantics

Lifecycle artifacts are optional mode handoff records. Persist them only when they reduce repeated context reconstruction or preserve result evidence across sessions.

Default behavior is chat output first. Do not auto-write a Markdown artifact for every small answer.

Allowed persisted location:

```
.forge/generated/
```

Recommended persisted paths:
- `.forge/generated/plans/<date>-<slug>.md`
- `.forge/generated/ecp/<date>-<slug>.md`
- `.forge/generated/reports/<date>-<slug>-execution.md`
- `.forge/generated/reviews/<date>-<slug>-review.md`

Mode-owned artifact types:

| Mode | Artifact |
|---|---|
| `plan` | Quick Plan or SDD artifact |
| `implementation` | ECP Artifact |
| `execute` | Execute Result Artifact |
| `review` | Review Result Artifact |
| `verify-context` | Context Verification Result |
| Incident scenario | Scenario artifact, explicitly marked as non-core lifecycle |
| Refactor scenario | Scenario artifact, explicitly marked as non-core lifecycle |

Artifact links may reference previous artifact IDs, plan IDs, ECP IDs, result artifact IDs, repository evidence, commits, PR/MR IDs, ADRs, and human confirmations.

Artifact links are trace references only. They must not become orchestration, DAG, workflow, scheduler, agent-memory, execution-trigger, or dependency-management semantics.

Artifacts must stay concise, human-readable, append-friendly, replaceable, and discardable. They must not contain hidden chain-of-thought, raw secrets, unnecessary conversation history, broad summaries, or autonomous memory structures.

Persistence policy:
- Save only when the user explicitly asks, when the work is medium/large and the user approves saving, or when multi-session/multi-agent continuity clearly benefits from a persisted artifact.
- Read-only modes do not write Markdown artifacts by default. If saving is explicitly requested, they may write only within their mode boundary and only to `.forge/generated/...`.
- Durable context promotion goes through `.forge/context-patches/...` review, not direct mutation of `.forge/context`.
- Context patch proposals remain reviewable proposals until a human promotes them into `.forge/context`.
- Do not force every response to mention artifact persistence status; mention it only when the user asks about saving or the workflow is explicitly discussing persistence.

If an artifact conflicts with repository evidence, code/repo evidence wins and the artifact is stale, partial, or superseded.

---

## 4. Runtime Placement

Runtime placement follows these boundaries:

- `runtime/CLAUDE.md` keeps only concise invocation entry behavior.
- `runtime/AGENTS.md` and tool adapters keep the same thin invocation-only boundary.
- `00-meta/conventions.md` keeps global cognition principles and mode-loading discipline.
- `modes/<mode>.md` owns mode-specific execution and reporting behavior in `## notes`.
- Mode-specific `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context` behavior should not be duplicated in globally loaded conventions.
- Runtime, validation, drift, artifact, governance, and secret semantics are referenced from adapters, not duplicated in adapters.
- Visible core modes remain limited to `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context`.

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

See `docs/workflow.md` for the canonical workflow narrative, approval gate UX, and post-review fix loop. See `specs/artifact-lifecycle.md` for artifact status vocabulary. See `runtime/.forge/context/00-meta/conventions-validation.md` for validation status semantics and output section structure.

### Mode Summary

| Mode | Purpose | Produces | Approval required? |
|---|---|---|---|
| `init` | Repository context/config creation | `.forge/context` and config | Before first use |
| `ask` | Lightweight repo understanding | Answers from evidence | No |
| `plan` | Quick Plan or SDD | Plan (`status: proposed`) | Before implementation |
| `implementation` | ECP generation | Execution Context Package (`status: proposed`) | Before execute |
| `execute` | Approved ECP application | Code changes + result report | After ECP approval |
| `review` | Executed-result assessment | Review Result | No (independent) |
| `verify-context` | Context health/freshness | Context Verification Result | No |
| Incident scenario | Issue and incident diagnosis using core modes | Scenario artifact when needed | Uses core-mode gates |
| Refactor scenario | Conservative behavior-preserving cleanup using core modes | Scenario artifact when needed | Uses core-mode gates |

### Approval Gates

Both gates are required and cannot be skipped. See `docs/workflow.md` for exact approval signal wording.

- **Gate 1**: Human must explicitly approve a plan before `forge-implementation` treats it as approved. Plan output begins as `status: proposed`.
- **Gate 2**: Human must explicitly approve an ECP before `forge-execute` runs. ECP begins as `status: proposed`.

ECP readiness in implementation output is a readiness signal, not autonomous permission to execute.

### Mode Boundaries

- `init` creates confirmed context/config through bounded scan and human confirmation.
- `ask` does not plan, mutate, redesign, or run broad audits.
- `plan` produces Quick Plan or SDD with explicit assumptions when ambiguity exists, plus acceptance criteria and validation commands even for small plans; it does not emit detailed executable coding tasks or modify code.
- `implementation` produces an ECP/readiness package with exact likely files, task sequence, coding rules, safety constraints, acceptance criteria, validation commands, stop conditions, and expected execution report format; it does not modify code directly.
- `execute` implements approved ECP scope; it does not redesign architecture or absorb review responsibilities.
- `review` assesses goal alignment, scope drift, lifecycle boundary compliance, validation evidence, security/risk boundaries, and context impact using verdicts `accept`, `request_changes`, `needs_more_validation`, or `blocked`; it performs a small per-task Context Impact Check and may propose a reviewable context patch, but it does not modify code or mutate `.forge/context` directly.
- `verify-context` checks `.forge/context` health, freshness, and reviewable patch quality; it may validate context quality issues or context-patch proposals, but it does not validate plans, ECPs, code diffs, MR readiness, or general code quality.
- Incident scenarios diagnose symptoms to root cause through `ask`, `plan`, `implementation`, `execute`, and `review` as needed; they do not become core lifecycle modes or redesign architecture.
- Refactor scenarios improve code conservatively through `plan`, `implementation`, `execute`, and `review` as needed; they preserve behavior and do not hide architecture changes.

### ECP Output Requirements

Implementation output must remain read-only and package execution readiness rather than apply changes. ECP output must include: Goal, Approved Scope, Non-goals, Assumptions, Relevant Context/Evidence, Exact Files Likely To Change, Task Sequence, Coding Rules, Safety/Security Constraints, Acceptance Criteria, Validation Commands, Stop Conditions, and Expected Execution Report Format.

Task sequencing is an output discipline only, not DAG, scheduler, agent, workflow engine, or Jira semantics.

### Execute Output Order

1. `Execution Result` (one of: `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, `NOT_VALIDATED`)
2. `Yang berhasil diubah`
3. `File yang berubah` (grouped by responsibility)
4. `Validasi`
5. `Yang belum tervalidasi`
6. `Yang masih perlu dicek manual`
7. `Cara rollback perubahan ini`
8. `Yang sengaja tidak diubah`
9. `Reviewer perlu fokus ke`
10. `Hidden change check`
11. `Recommended next action` (short and singular)

### Lower-Cost Execution

After architecture reasoning, unknown classification, and task-card decomposition are complete, execute mode is suitable for lower-cost execution-oriented models following an approved task plan. This does not add model routing, tool orchestration, automation tooling, runtime executors, or agent services.

---

## 7. Loading-Delta Behavior

Forge preserves a loading-delta philosophy:

- Core context is loaded selectively from the relevant adapter, mode, and evidence path.
- Mode files describe only what changes for that mode.
- Modes do not re-list core.
- Adapters start from `.forge/adapter.md`, then the requested mode contract.
- Related layers and systems are loaded by task relevance, not by default breadth.
- `on_demand` is a conditional expansion path, not a second default include list.
- `exclude` protects unrelated context from accidental loading.
- Compatibility/scenario files are loaded only when requested or clearly relevant.
- Small plans should inspect the smallest relevant code surface before expanding context.

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

The following are invalid mode invocation behaviors. See `runtime/.forge/context/00-meta/conventions-validation.md` for validation-specific forbidden patterns. See `conventions-risk.md` for governance and secret forbidden patterns.

**Config and interaction:**
- Ignoring the requested mode file or invoking without reading `.forge/forge.config.yaml` first.
- Failing to detect, report, or apply `run.interaction` as the controlling interaction setting.
- Treating old runtime profile fields as active config semantics.
- Emitting automation-style blocked reports in manual mode instead of ask-first clarification.
- Asking conversational questions in auto mode.
- Using run settings to introduce CI/CD, deploy, release, or executor behavior.
- Introducing any conflicting interaction or workflow flag.

**Context loading:**
- Loading broad `.forge/context` by default.
- Treating modes as optional suggestions or `on_demand` entries as unconditional defaults.
- Ignoring `exclude` entries.
- Exceeding the normal scoped `token_budget` without a concrete evidence reason.

**Decisions and approval:**
- Auto-approving HIGH-risk decisions.
- Silently auto-approving important decisions covered by policy confirmation boundaries.
- Omitting decision trace for automation-selected LOW defaults or confirmed important decisions.
- Treating decision traces as workflow state, scheduler input, retry policy, or execution graph.
- Treating a proposed default as confirmed.

**Mode boundaries:**
- Collapsing init, ask, plan, implementation, execute, review, and verify-context into generic reasoning behavior.
- Treating incident, refactor, or test-focused scenarios as separate core lifecycle modes.
- Allowing plan to produce detailed executable coding tasks instead of Quick Plan or SDD.
- Allowing implementation mode to emit final executable tasks while critical blockers remain unresolved.
- Allowing implementation mode to hide blocking decisions at the end of a full breakdown.
- Marking implementation output `READY_FOR_EXECUTION` while required execution values are conditional, unavailable, or unresolved.
- Allowing implementation to directly modify code.
- Allowing execute to redefine approved architecture or absorb review responsibilities.
- Allowing review to become execution, replace validation evidence, produce implementation task lists, or mutate `.forge/context` directly.
- Allowing verify-context to become code validation, MR review, implementation planning, or automatic context-patch acceptance.
- Allowing ask to become plan, review, audit, or mutation.
- Allowing incident scenarios to become speculative redesign or architecture rewrite.
- Allowing refactor scenarios to hide behavior changes, architecture rewrites, or paradigm migrations.

**Implementation readiness package:**
- Allowing readiness output without bounded ECP structure.
- Allowing ready ECP output without exact likely files, task sequence, acceptance criteria, validation commands, or risky-change guardrails.
- Allowing interactive implementation confirmation without `NEEDS_CONFIRMATION`, Recommended/Alternative choices, and clear numbered reply instructions.
- Treating ECP sequencing as DAG, scheduler, agent, Jira, story-point, or workflow-engine semantics.

**Output and evidence:**
- Inventing topology, ownership, contracts, APIs, databases, or business rules without evidence.
- Prominently exposing runtime/debug/loading internals in normal interactive output.
- Asking broad questionnaires when a minimal decision prompt is enough.
- Producing RFC/audit-style narrative when concise operational structure is enough.
- Duplicating mode-specific execution behavior in globally loaded conventions.
- Replacing repository-owned code/docs/ADRs with Forge-generated cognition.

**Artifacts:**
- Treating lifecycle artifacts as source of truth over repository evidence.
- Persisting hidden chain-of-thought, raw secrets, or generic long-form summaries in artifacts.
- Using artifact links as orchestration, DAG, workflow, scheduler, agent-memory, or execution-trigger semantics.
- Creating unclear artifact ownership or generic artifacts not owned by a mode.

**Automation:**
- Introducing agent loops, auto-retry orchestration, scheduler behavior, workflow graph execution, DAG execution, deploy/release automation, CI pipeline execution, or autonomous multi-step chaining.

---

## 11. Validation Expectations

Mode invocation validation checks that runtime behavior follows this protocol. See `validation-cases/` for regression benchmarks. See `specs/artifact-lifecycle.md` for artifact status validation. See `docs/workflow.md` for workflow validation cases. See `runtime/.forge/context/00-meta/conventions-validation.md` for detailed validation status and section expectations.

**Config and bootstrap:**
- `.forge/forge.config.yaml` read before the requested mode file.
- `run.interaction`, output/write/failure behavior, and policy confirmation boundaries detected.
- `run.interaction` applied as the controlling interaction behavior.
- Unsupported or conflicting run fields reported before mode work.
- Mode file read before mode-specific context loading.
- `include`, `on_demand`, `exclude`, `token_budget`, and `notes` considered.

**Context loading:**
- Loaded context scoped to the task; broad-loading violations avoided.
- `CONTEXT_BUDGET_LIMITED` used when required evidence exceeds scoped budget.

**Mode boundary integrity:**
- All seven core modes retain distinct operational behavior per section 6.
- No mode collapsed into another or absorbed out-of-scope responsibilities.
- Mode-specific behavior lives in mode files, not globally loaded conventions.

**Decisions and approval:**
- Evidence, inference, and unknown boundaries preserved.
- Unknowns classified as blocking, proposed-default, or informational.
- Proposed defaults explicitly labeled; never promoted to confirmed without human confirmation.
- HIGH-risk decisions not auto-approved; human confirmation required.
- Decision traces present for automation-selected LOW defaults and confirmed important decisions.
- Manual mode used ask-first clarification; auto mode used blocking status output.

**Implementation correctness:**
- Implementation blocked correctly when critical blockers exist; final ECP readiness output absent from blocked output.
- Implementation confirmation used `NEEDS_CONFIRMATION`, Recommended/Alternative choices, and numbered reply instructions.
- `READY_FOR_EXECUTION` used only with concrete execution values.
- ECP output includes required readiness fields such as Goal, Scope, Assumptions, Exact Likely Files, Task Sequence, Acceptance Criteria, Validation Commands, and Stop Conditions.

**Execute correctness:**
- One clear status used; `SUCCESS` only when reliable validation evidence exists.
- Changed files grouped by responsibility; unrelated files absent; formatting churn absent.
- Rollback reported for runtime-impacting changes; reviewer focus present for non-trivial changes.
- Prior review findings verified resolved or explicitly still open.

**Testing and review correctness:**
- Testing output used required sections and grouped validation by test category.
- Review output used required sections, named the diff reviewed, and preserved severity grouping.
- `CRITICAL`/`MAJOR` review findings included file/area, what is wrong, why it matters, and suggested fix.

**Artifacts and secrets:**
- Lifecycle artifacts mode-owned, bounded, human-readable, non-authoritative, free of raw secrets.
- Raw secret exposure absent from generated context and reports.

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
