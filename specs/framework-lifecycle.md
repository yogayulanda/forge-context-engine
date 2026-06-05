# Framework Lifecycle Specification

| Field | Value |
|---|---|
| Document | Forge Framework Lifecycle Specification |
| Version | 1.8 |
| Date | 2026-05-25 |
| Status | `decision` |
| Scope | Framework-level cognition maturity states |
| Dependency | `specs/context-initialization.md`, `specs/context-validation.md`, `specs/mode-invocation.md`, `specs/artifact-lifecycle.md` |

---

## 0. Purpose

This document defines the maturity and validation lifecycle of Forge cognition behavior.

It defines:
- Framework maturity states.
- Criteria for promoting cognition behavior between states.
- Criteria for creating validation cases.
- Coverage philosophy for Forge cognition evolution.
- The boundary before runtime, tooling, or automation work begins.
- Repository-wide engineering style conventions for AI-generated code.
- Runtime validation and partial/blocking execution semantics.
- Minimal artifact lifecycle semantics for continuity across modes and sessions.
- Bounded run interaction, policy-based human confirmation, and automation-safe approval semantics.
- Lightweight future-facing intelligence and fintech-grade governance semantics without automation.

This document does NOT:
- Implement tooling or automation.
- Redesign the existing Forge structure.
- Add runtime executors, orchestration, agents, or services.
- Add workflow engines, DAG systems, schedulers, triggers, CI/CD behavior, deploy workflows, persistent AI memory, or knowledge graphs.
- Add RAG systems, vector search, autonomous context expansion, cross-repo orchestration, or governance bureaucracy.
- Define repository-specific context content.
- Treat repository count or file count as maturity.
- Enforce architecture ideology, framework preference, lint tooling, or rigid code metrics.

---

## 1. Lifecycle Phases

Forge cognition behavior progresses through the following maturity states.

```
initialized -> audited -> cognition-validated -> benchmarked -> stable
```

Each state is additive. A later state requires the earlier state criteria to remain true.

---

## 2. Phase: initialized

### Meaning

`initialized` means a local Forge context has been generated for a repository.

### Criteria

- Local Forge context exists.
- Required manifests exist.
- Required IDs exist.
- Expected structure has been created.
- Runtime adapter files exist where applicable.

### Non-Claims

`initialized` does not imply:
- Semantic correctness.
- Evidence correctness.
- Complete topology understanding.
- Correct cognition behavior.
- Hallucination resistance.
- Benchmark coverage.

### Exit Condition

A repository reaches `initialized` when the Forge context structure is present and internally addressable.

---

## 3. Phase: audited

### Meaning

`audited` means the local context has been reviewed against validation rules and semantic consistency checks.

### Criteria

- Context validation rules have been applied.
- Evidence references have been reviewed.
- Semantic consistency has been checked.
- Hallucination risks have been reviewed.
- Unknowns, assumptions, and inferred claims are separated.
- Claims do not exceed their evidence.

### Non-Claims

`audited` does not imply:
- Correct cognition behavior under benchmarked reasoning tasks.
- Reusable validation-case coverage.
- Stable behavior across repository diversity.
- Runtime/tooling readiness.

### Exit Condition

A repository reaches `audited` when structural validation and evidence/semantic review are complete, with remaining risks explicitly recorded.

---

## 4. Phase: cognition-validated

### Meaning

`cognition-validated` means Forge reasoning behavior has been proven correct for a specific semantic or topology pattern.

### Criteria

- A specific cognition pattern is identified.
- Expected cognition behavior is stated before validation.
- Repository evidence confirms the expected behavior.
- Hallucination boundaries are validated.
- Topology semantics are validated.
- Incorrect interpretations are explicitly rejected.

### Example Patterns

- `imports != runtime-calls`
- `shared-runtime != deployable-service`
- `local-context-first discovery works`
- `ask-mode answers repo-understanding questions without planning or mutation`
- `plan-mode emits Quick Plan or SDD, not PRD prose`
- `plan-mode adapts sections to active layers`
- `plan-mode scopes on-demand loading to the change`
- `implementation-mode emits an Execution Context Package, not code changes`
- `execute-mode modifies repositories only from approved ECP scope`
- `execute-mode reports SUCCESS only with validation evidence`
- `execute-mode distinguishes PARTIAL_SUCCESS, BLOCKED, BLOCKED_BY_ENVIRONMENT, and NOT_VALIDATED`
- `mode outputs stay human-readable, scannable, and operational`
- `execute/review validation reporting owns structured validation, scope grouping, test strategy, mocks/fakes/stubs, coverage, and regression validation where relevant`
- `review-mode validates execute results without replacing execute mode`
- `review-mode rejects hidden success and unsupported fully-validated/test-passed claims`
- `review-mode produces senior review output with verdict, diff reviewed, severity-grouped evidence findings, and safety-focused boundary assessment`
- `review-mode checks architecture/contract drift and relevant safety risks without redesigning lifecycle or replacing post-change human responsibility`
- `incident scenarios diagnose bugs/issues without speculative redesign`
- `refactor scenarios preserve behavior and stay bounded`
- `run.interaction` controls interaction behavior without rewriting repository cognition
- `NEEDS_HUMAN_APPROVAL` blocks HIGH-risk automation decisions until human confirmation
- `CONTEXT_BUDGET_LIMITED` reports when safe scoped reasoning needs more evidence than normal budget
- `drift-detection prefers current repository evidence over stale context/artifacts`
- `cross-repo-awareness reports ownership/contract uncertainty without assuming external behavior`
- `incident scenarios distinguish symptom, likely cause, possible cause, and evidence gaps with confidence`
- `refactor scenarios classify LOW/MEDIUM/HIGH risk and require a plan path for HIGH-risk work`
- `fintech-governance surfaces concise risk signals without audit bureaucracy`
- `payment-transaction-correctness is never classified as LOW risk`
- `AI-generated code follows repository-native pragmatic naming, style, abstraction, and testing conventions`
- `lifecycle artifacts preserve mode handoff continuity without overriding repository truth`

### Required Evidence

Validation must be backed by repository evidence such as:
- Source code topology.
- Build or module metadata.
- Runtime entrypoints.
- Configuration files.
- Existing Forge context files.
- Explicit human confirmation where repository evidence alone is insufficient.

### Non-Claims

`cognition-validated` does not imply:
- The pattern is covered by a reusable benchmark.
- Future regressions can be detected automatically.
- The behavior is mature across repository diversity.

### Exit Condition

A cognition pattern reaches `cognition-validated` when Forge produces the expected reasoning result for the pattern and avoids known hallucination failure modes.

---

## 5. Phase: benchmarked

### Meaning

`benchmarked` means a validated cognition pattern has been added to `validation-cases/` so future regressions can be detected.

### Criteria

- The cognition pattern exists in `validation-cases/`.
- Expected behavior is documented.
- Failure modes are documented.
- Required evidence shape is documented.
- The case is repository-neutral enough to test framework cognition.
- The case has regression value.

For mode benchmarks, expected behavior should verify init-mode context/config creation, ask-mode repo understanding without mutation, plan-mode Quick Plan or SDD output, layer-adaptive sections, scoped loading and `CONTEXT_BUDGET_LIMITED` behavior, evidence/inference/unknown separation, implementation-mode ECP generation, execute-mode approved-ECP boundaries, grouped file-change reporting, explicit runtime prerequisite checks, partial/blocking/not-validated status semantics, concise blocker/confirmation UX, validation scope categories, contract-aware runtime-sensitive coverage, review-mode verdict plus diff-reviewed coverage, severity-grouped findings, architecture/contract drift checks, security/context-impact notes, verify-context context-health boundaries, incident/refactor scenario safety, fintech governance risk signals, and rejection of unsupported backend-only, topology, broad-loading, stale-artifact, cross-repo-assumption, generic-audit, fully-validated, production-ready, or test-passed claims.

For engineering-style benchmarks, expected behavior should verify pragmatic idiomatic implementation, natural operational naming, repository-first test placement, minimal safe improvement, and rejection of unnecessary abstraction, academic wording, competing coding paradigms, or unrelated mass refactor.

### Non-Claims

`benchmarked` does not imply:
- The pattern is mature across many repositories.
- Runtime/tooling implementation should begin immediately.
- Repository-specific business knowledge should be preserved.

### Exit Condition

A cognition pattern reaches `benchmarked` when it is represented as a validation case with documented expectations and regression value.

---

## 6. Phase: stable

### Meaning

`stable` means a cognition pattern has been validated repeatedly across multiple repositories or topology variants and is mature enough to inform future runtime or tooling evolution.

### Criteria

- The cognition pattern has been validated repeatedly.
- Validation spans multiple repositories or topology variants.
- Expected behavior remains consistent.
- Hallucination boundaries remain consistent.
- Topology reasoning remains stable under repository diversity.
- Existing validation cases continue to pass or remain semantically valid.

### Non-Claims

`stable` does not imply:
- Runtime/tooling must be implemented immediately.
- The pattern is exempt from future regression review.
- The pattern applies outside its documented semantic boundary.

### Exit Condition

A cognition pattern reaches `stable` when repeated evidence shows consistent cognition behavior across diverse topologies.

---

## 7. Validation-Case Criteria

A validation case should only be created when all of the following are true:

- A new semantic or topology pattern has been validated.
- The pattern has regression value.
- The pattern improves coverage diversity.
- The behavior is evidence-backed.
- Expected cognition behavior can be stated precisely.
- Failure behavior can be stated precisely.
- The case can be kept framework-level.

A validation case should NOT:

- Archive repositories.
- Duplicate local contexts.
- Act as marketing or demo material.
- Store business or domain details.
- Preserve private implementation detail beyond what is needed for cognition validation.
- Reward volume over semantic coverage.

### Minimum Contents

A validation case should contain only what is necessary to test the cognition pattern:

- Pattern name.
- Topology shape.
- Evidence shape.
- Expected cognition behavior.
- Known incorrect interpretation.
- Hallucination boundary.
- Source validation notes.

---

## 8. Coverage Philosophy

Forge evolves through:

- Topology diversity.
- Semantic coverage.
- Cognition correctness.
- Hallucination resistance.

Forge does not mature through:

- File count.
- Repository count.
- Automation complexity.
- Larger local contexts.
- More generated documentation.
- More lifecycle artifacts without new continuity value.
- More benchmark cases without new semantic coverage.
- Rigid style metrics or framework preference enforcement.

Coverage is valuable only when it improves Forge's ability to reason correctly from evidence.

---

## 9. Runtime Implementation Rule

Runtime, tooling, and automation work should begin only after:

- Cognition patterns are repeatedly validated.
- Validation cases provide sufficient semantic coverage.
- Topology reasoning remains stable across repository diversity.
- Hallucination boundaries are understood and documented.
- The behavior being automated is already stable at the cognition level.

Runtime implementation must not be used to discover core cognition semantics.

Automation may encode mature cognition behavior. It must not replace semantic validation.

Run interaction semantics may make local/manual and automation-safe behavior clearer. They do not create orchestration authority. Automation-safe decisions remain bounded by policy, required decisions, and human approval for high-risk changes.

---

## 10. Artifact Lifecycle Boundary

Lifecycle artifacts may preserve concise plan, implementation, execution, review, verify-context, and scenario handoff records.

Valid artifact use:
- Preserve approved engineering intent and confirmed decisions.
- Preserve execution-ready task contracts and stop conditions.
- Preserve implementation, validation, review, incident, or refactor results.
- Link directly to prior artifacts or repository evidence.
- Stay small, human-readable, replaceable, and reviewable.

Invalid artifact use:
- Treat artifacts as source of truth over code, repository docs, ADRs, or human confirmations.
- Store hidden chain-of-thought, broad conversational history, or generic long-form summaries.
- Create autonomous memory, knowledge graph, workflow engine, DAG, scheduler, agent, deploy, CI/CD, or runtime executor semantics.
- Use artifact links as execution triggers or orchestration dependencies.

Artifact maturity does not promote Forge lifecycle state by volume. A lifecycle artifact is useful only when it improves bounded continuity while preserving repository-first truth.

---

## 11. Promotion Rules

| From | To | Required Signal |
|---|---|---|
| `initialized` | `audited` | Validation rules applied; evidence and semantic risks reviewed |
| `audited` | `cognition-validated` | Specific cognition pattern proven correct against evidence |
| `cognition-validated` | `benchmarked` | Pattern added to `validation-cases/` with expected behavior and regression value |
| `benchmarked` | `stable` | Pattern repeatedly validates across repository or topology diversity |

Promotion is not automatic. Each transition requires explicit evidence for the next state.

---

## 12. State Summary

| State | What Is Proven | What Is Not Proven |
|---|---|---|
| `initialized` | Structure exists | Semantic correctness |
| `audited` | Context reviewed against validation and evidence rules | Cognition benchmark correctness |
| `cognition-validated` | One cognition pattern behaves correctly | Regression coverage |
| `benchmarked` | Future regression can be detected for the pattern | Cross-repository maturity |
| `stable` | Pattern is mature across repository/topology diversity | Universal applicability |

---

## 13. Governance Rule

Forge lifecycle state must be assigned to cognition behavior, not to repository size or documentation volume.

A large repository with many context files can remain `initialized` or `audited`.

A small repository can validate a high-value cognition pattern if it provides strong topology evidence and a clear hallucination boundary.
