# Mode Invocation Protocol

| Field | Value |
|---|---|
| Document | Forge Mode Invocation Protocol |
| Version | 1.2 |
| Date | 2026-05-24 |
| Status | `decision` |
| Scope | Framework-level protocol for invoking Forge modes |
| Dependency | `runtime/CLAUDE.md`, `runtime/.forge/context/00-meta/conventions.md`, `runtime/.forge/context/modes/*.md`, `specs/context-validation.md` |

---

## 0. Purpose

Mode invocation defines how an AI assistant uses Forge mode files during planning, implementation, review, and testing.

The protocol ensures:
- Mode files are operational contracts, not optional hints.
- Context loading remains scoped and delta-based.
- Evidence, inference, proposed-default, and unknown boundaries survive task execution.
- Unknowns are classified into blocking, proposed-default, or informational behavior.
- Sensitive values are redacted before output or context write.
- Runtime repositories receive concise executable rules.
- Runtime placement stays modular: global files define entry rules, mode files define mode-specific behavior.
- Framework maintainers have an authoritative protocol for future evolution.

This document does NOT:
- Redesign Forge architecture.
- Add automation, tooling, agents, executors, or runtime services.
- Replace mode file schema rules.
- Define repository-specific domain content.

---

## 1. Invocation Lifecycle

Canonical lifecycle:

1. Requested mode identified.
2. Mode file read first from `.forge/context/modes/<mode>.md`.
3. `include`, `on_demand`, `exclude`, `token_budget`, and `notes` parsed.
4. Scoped context loaded according to the mode delta.
5. Task executed according to mode behavior.
6. Evidence / inference / proposed-default / unknown boundaries preserved.
7. Unknowns classified by operational impact.
8. Loaded context reported.
9. Missing evidence and unresolved ambiguity reported.
10. Mode sufficiency evaluated.

Mode invocation is successful only when the assistant can explain which context was loaded, which evidence was missing, and whether the selected mode was enough for the task.

---

## 2. Global Invocation Rules

All modes follow these rules:

- Read the requested mode file before loading mode-specific context.
- Treat always-loaded core as already available: `00-meta/*` and `01-core/*`.
- Treat mode files as loading deltas on top of core.
- Load `include` entries normally when relevant to the task.
- Load `on_demand` entries only when task scope requires them.
- Do not load `exclude` entries unless the user explicitly changes scope.
- Respect `token_budget` as the recommended maximum context budget.
- Follow `notes` for concise operational guidance.
- Do not broad-load `.forge/context` by default.
- Keep evidence-backed facts, inferences, proposed defaults, assumptions, and unknowns separate.
- Keep proposed defaults explicitly labeled as proposed and not confirmed.
- Redact secrets before reporting evidence, findings, plans, reviews, tests, or loaded context.
- Report loaded context areas/files in the response or work summary.
- Report missing evidence and unresolved ambiguity before relying on guesses.
- State whether the requested mode was sufficient.

---

## 3. Unknown Classification and Human Decision Protocol

Forge classifies unknowns by operational impact:

| Classification | Continue? | Behavior |
|---|---|---|
| `blocking` | No | Requires authoritative decision before implementation/release. Interactive mode asks the minimum decision question. Automation emits `BLOCKED`, `NEEDS_REVIEW`, or `NEEDS_CONFIRMATION`. |
| `proposed-default` | Yes | AI may proceed with a safe, conventional, reversible, non-authoritative default that is explicitly labeled `proposed` and `not confirmed`. |
| `informational` | Yes | Record the uncertainty; do not interrupt execution. |

Blocking unknowns include event schema authority, retry/DLQ semantics, ownership/SLA/compliance, destructive migration approval, security policy, and production runtime topology.

Interactive prompts must be concise and decision-oriented: recommended safest/production-ready option plus one viable alternative by default. Use a maximum of three options only for major architecture tradeoffs.

Automation/non-interactive mode must not require human input. When blocking unknowns exist, emit the blocking status and include a recommended option plus an alternative when useful.

### 3.1 Proposed Default Semantics

AI may define proposed defaults only when the choice is low-risk, operationally conventional, reversible, non-authoritative, not topology-defining, and not compliance/security defining.

Each proposed default must state:
- Proposed value.
- Reason for the proposal.
- Status: `proposed`, `not confirmed`.
- Required confirmation before production finalization when an owner/producer/platform decision is needed.

---

## 4. Runtime Placement

Runtime placement follows these boundaries:

- `runtime/CLAUDE.md` keeps only concise invocation entry behavior.
- `00-meta/conventions.md` keeps global cognition principles and mode-loading discipline.
- `modes/<mode>.md` owns mode-specific execution and reporting behavior in `## notes`.
- Mode-specific planning, implementation, review, and testing behavior should not be duplicated in globally loaded conventions.

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

Raw secrets must not be copied into `.forge/context`, inferred knowledge, unknowns, confirmations, decisions, mode files, platform context, audit reports, planning output, review comments, testing notes, or validation-cases.

---

## 6. Per-Mode Operational Expectations

### 6.1 Planning

Planning mode produces an Engineering Change Plan (ECP) by default.

Expected behavior:
- Architecture and runtime reasoning.
- Implementation sequencing.
- Risk and impact analysis.
- Dependency, contract, data, and topology checks when evidenced.
- Validation and rollback planning.
- No implementation code by default.
- Safe proposed defaults for low-risk operational choices.
- Escalation only for blocking decisions.
- Secret findings redacted and treated as security findings.

Planning mode must stay layer-adaptive. It must not force backend-only, deployability, ownership, contract, or runtime topology assumptions without evidence.

### 6.2 Implementation

Implementation mode executes scoped changes.

Expected behavior:
- Implement the requested change.
- Maintain repository consistency.
- Align with existing architecture and runtime constraints.
- Load only task-relevant layers, systems, decisions, and inferred knowledge.
- Avoid speculative redesign.
- Keep proposed defaults visible and unconfirmed.
- Do not copy raw secrets from existing config, env, logs, fixtures, or docs into code or context.

Implementation mode must not expand scope from code execution into architecture redesign unless the user explicitly requests that change. It must not silently promote proposed defaults into confirmed architecture or runtime behavior.

### 6.3 Review

Review mode evaluates correctness and risk.

Expected behavior:
- Correctness review.
- Regression and operational risk detection.
- Topology, runtime, data, and contract consistency checks when relevant.
- Evidence-based critique with explicit uncertainty.
- Detection of unconfirmed proposed defaults.
- Detection of accidental promotion from proposed assumption to confirmed behavior.
- Raw secret exposure in diffs, reports, generated context, or comments is a security finding.

Review mode must not treat unevidenced concerns as confirmed defects.

### 6.4 Testing

Testing mode defines or executes validation strategy.

Expected behavior:
- Validation strategy.
- Coverage reasoning.
- Rollback and regression analysis.
- Operational verification.
- Test evidence reporting.
- Blocking vs proposed-default path validation where relevant.
- Visibility checks for unresolved proposed defaults before production finalization.
- Test evidence must redact credentials, tokens, cookies, URLs with credentials, and private keys.

Testing mode must distinguish tested behavior from inferred confidence.

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

- Mode used.
- Mode file read.
- Included context areas/files loaded.
- On-demand context areas/files loaded and why.
- Excluded areas intentionally not loaded when relevant.
- Missing evidence and unresolved ambiguity.
- Blocking unknowns, proposed defaults, and informational unknowns when present.
- Redacted security findings when secrets are detected.
- Whether the mode was sufficient.

The report may be concise in normal runtime use. Maintainer-facing validation may require fuller detail.

---

## 10. Forbidden Behaviors

The following are invalid mode invocation behavior:

- Ignoring the requested mode file.
- Loading broad `.forge/context` by default.
- Treating modes as optional suggestions.
- Treating `on_demand` entries as unconditional defaults.
- Ignoring `exclude`.
- Exceeding `token_budget` without a task-specific reason.
- Inventing topology, ownership, contracts, integrations, deployment ownership, APIs, databases, or business rules without evidence.
- Printing, copying, summarizing, or storing raw secrets.
- Including raw secrets in `.forge/context`, reports, validation-cases, reviews, tests, decisions, confirmations, unknowns, inferred knowledge, modes, or platform context.
- Treating a proposed default as confirmed.
- Asking broad questionnaires when a minimal decision prompt is enough.
- Requiring interactive input in automation/non-interactive mode.
- Generating open-ended architecture option lists instead of bounded decision options.
- Collapsing planning, implementation, review, and testing into generic reasoning behavior.
- Duplicating mode-specific execution behavior in globally loaded conventions.
- Replacing repository-owned code/docs/ADRs with Forge-generated cognition.
- Adding automation/tooling/runtime execution under the guise of protocol compliance.

---

## 11. Validation Expectations

Mode invocation validation checks that runtime behavior follows this protocol:

- The requested mode file was read before mode-specific context loading.
- `include`, `on_demand`, `exclude`, `token_budget`, and `notes` were considered.
- Loaded context was scoped to the task.
- Broad-loading violations were reported or avoided.
- Planning, implementation, review, and testing retained distinct operational behavior.
- Mode-specific behavior lives in mode files rather than globally loaded conventions.
- Evidence, inference, and unknown boundaries were preserved.
- Unknowns were classified as blocking, proposed-default, or informational.
- Proposed defaults were explicitly labeled and not promoted to confirmed facts.
- Automation behavior used blocking status output instead of interactive questions.
- Human decision prompts followed option-count discipline.
- Raw secret exposure was absent from generated context and reports.
- Secret findings were redacted, classified as security findings, and included rotation guidance when exposure was possible.
- Loaded context areas/files were reported.
- Missing evidence and unresolved ambiguity were reported.
- Mode sufficiency was evaluated.

These expectations may be validated manually today and automated later.

---

## 12. Future Compatibility Direction

The protocol is compatible with future support for:

- Automatic mode invocation.
- Invocation tracing.
- Loading reports.
- Dry-run loading previews.
- Token budgeting enforcement.
- Invocation telemetry.

No automation, tooling, runtime executor, telemetry collection, or enforcement implementation is introduced by this protocol.
