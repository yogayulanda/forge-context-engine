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

See `docs/workflow.md` for the canonical workflow narrative, approval gate UX, and post-review fix loop. See `specs/artifact-lifecycle.md` for artifact status vocabulary. See `runtime/.forge/context/00-meta/conventions-validation.md` for validation status semantics and output section structure.

### Mode Summary

| Mode | Purpose | Produces | Approval required? |
|---|---|---|---|
| `ask` | Lightweight repo understanding | Answers from evidence | No |
| `planning` | Strategic ECP reasoning | ECP (`status: proposed`) | Before implementation |
| `implementation` | Human-reviewable task decomposition | Execution Contract (`status: proposed`) | Before execute |
| `execute` | Approved repository modification | Code changes + result report | After contract approval |
| `testing` | Structured validation depth | Testing Result artifact | No (independent) |
| `review` | Correctness and risk assessment | Review Result artifact | No (independent) |
| `incident` | Issue and incident diagnosis | Incident artifact | No |
| `refactor` | Conservative behavior-preserving cleanup | Refactor artifact | Human stop for HIGH risk |

### Approval Gates

Both gates are required and cannot be skipped. See `docs/workflow.md` for exact approval signal wording.

- **Gate 1**: Human must explicitly approve an ECP before `forge-implement` treats it as approved. ECP artifact begins as `status: proposed`.
- **Gate 2**: Human must explicitly approve an Execution Contract before `forge-execute` runs. Execution Contract begins as `status: proposed`.

`READY_FOR_EXECUTION` in implementation output is a readiness signal, not autonomous permission to execute.

### Mode Boundaries

- `ask` does not plan, mutate, redesign, or run broad audits.
- `planning` produces strategic ECP with phases; it does not emit detailed executable coding tasks.
- `implementation` produces human-reviewable task cards; it does not modify code directly.
- `execute` implements approved tasks; it does not redesign architecture or absorb testing/review responsibilities.
- `testing` owns validation depth, coverage, and test-focused changes; it does not replace review mode.
- `review` assesses correctness and risk; it does not replace testing or produce implementation task lists.
- `incident` diagnoses symptoms to root cause; it does not redesign architecture or topology.
- `refactor` improves code conservatively within a bounded scope; it preserves behavior and does not hide architecture changes.

### Task Card Requirements

Implementation `READY_FOR_EXECUTION` and `READY_FOR_PARTIAL_EXECUTION` output must use task cards. Each card must include: Task ID, Title, Priority, Impact, Scope, Depends On, Parallel Safe, Goal, Why, Likely Files, Do Not Change, Out Of Scope, Derived From, Acceptance Criteria, and Test Expectation.

Task cards are an output discipline only — not DAG, scheduler, agent, workflow engine, or Jira semantics.

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

The following are invalid mode invocation behaviors. See `runtime/.forge/context/00-meta/conventions-validation.md` for validation-specific forbidden patterns. See `conventions-risk.md` for governance and secret forbidden patterns.

**Config and interaction:**
- Ignoring the requested mode file or invoking without reading `.forge/forge.config.yaml` first.
- Failing to detect, report, or apply `runtime.non_interactive` as the controlling flag.
- Treating `runtime.profile` as a second interaction flag.
- Emitting automation-style blocked reports in interactive mode instead of ask-first clarification.
- Asking conversational questions in non-interactive mode.
- Using reserved `ci` profile to introduce CI/CD, deploy, release, or executor behavior.
- Introducing any conflicting interaction or workflow flag.

**Context loading:**
- Loading broad `.forge/context` by default.
- Treating modes as optional suggestions or `on_demand` entries as unconditional defaults.
- Ignoring `exclude` entries.
- Exceeding the normal scoped `token_budget` without a concrete evidence reason.

**Decisions and approval:**
- Auto-approving HIGH-risk decisions.
- Using orchestrator authority without explicit `runtime.decision_authority: orchestrator`.
- Omitting decision trace for automation-selected LOW defaults or orchestrator-selected MEDIUM decisions.
- Treating decision traces as workflow state, scheduler input, retry policy, or execution graph.
- Treating a proposed default as confirmed.

**Mode boundaries:**
- Collapsing ask, planning, implementation, execute, testing, review, incident, and refactor into generic reasoning behavior.
- Allowing planning to produce detailed executable coding tasks instead of strategic ECP.
- Allowing implementation mode to emit final executable tasks while critical blockers remain unresolved.
- Allowing implementation mode to hide blocking decisions at the end of a full breakdown.
- Marking implementation output `READY_FOR_EXECUTION` while required execution values are conditional, unavailable, or unresolved.
- Allowing implementation to directly modify code.
- Allowing execute to redefine approved architecture or absorb testing/review responsibilities.
- Allowing review to become testing, replace test strategy, or produce implementation task lists.
- Allowing ask to become planning, review, audit, or mutation.
- Allowing incident to become speculative redesign or architecture rewrite.
- Allowing refactor to hide behavior changes, architecture rewrites, or paradigm migrations.

**Implementation task cards:**
- Allowing readiness output without bounded task cards.
- Allowing ready task cards without task ID, priority, impact, dependencies, acceptance criteria, or risky-change guardrails.
- Allowing interactive implementation confirmation without `NEEDS_CONFIRMATION`, Recommended/Alternative choices, and clear numbered reply instructions.
- Treating task cards as DAG, scheduler, agent, Jira, story-point, or workflow-engine semantics.

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
- `runtime.profile`, `runtime.non_interactive`, and decision authority detected.
- `runtime.non_interactive` applied as the controlling interaction behavior.
- Profile/non-interactive conflicts reported before mode work.
- Mode file read before mode-specific context loading.
- `include`, `on_demand`, `exclude`, `token_budget`, and `notes` considered.

**Context loading:**
- Loaded context scoped to the task; broad-loading violations avoided.
- `CONTEXT_BUDGET_LIMITED` used when required evidence exceeds scoped budget.

**Mode boundary integrity:**
- All eight modes retained distinct operational behavior per §6.
- No mode collapsed into another or absorbed out-of-scope responsibilities.
- Mode-specific behavior lives in mode files, not globally loaded conventions.

**Decisions and approval:**
- Evidence, inference, and unknown boundaries preserved.
- Unknowns classified as blocking, proposed-default, or informational.
- Proposed defaults explicitly labeled; never promoted to confirmed without human confirmation.
- HIGH-risk decisions not auto-approved; human confirmation required.
- Decision traces present for automation-selected LOW and orchestrator-selected MEDIUM decisions.
- Interactive mode used ask-first clarification; non-interactive mode used blocking status output.

**Implementation correctness:**
- Implementation blocked correctly when critical blockers exist; final task cards absent from blocked output.
- Implementation confirmation used `NEEDS_CONFIRMATION`, Recommended/Alternative choices, and numbered reply instructions.
- `READY_FOR_EXECUTION` used only with concrete execution values.
- Task cards include all required fields (Task ID, Priority, Impact, Scope, Depends On, Parallel Safe, Goal, Why, Likely Files, Do Not Change, Acceptance Criteria, Test Expectation).

**Execute correctness:**
- One clear status used; `SUCCESS` only when reliable validation evidence exists.
- Changed files grouped by responsibility; unrelated files absent; formatting churn absent.
- Rollback reported for runtime-impacting changes; reviewer focus present for non-trivial changes.
- Prior review findings verified resolved or explicitly still open.

**Testing and review correctness:**
- Testing output used required sections and grouped validation by test category.
- Review output used required sections, severity grouping, and one MR readiness result.
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
