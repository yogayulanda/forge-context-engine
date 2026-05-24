# Framework Lifecycle Specification

| Field | Value |
|---|---|
| Document | Forge Framework Lifecycle Specification |
| Version | 1.1 |
| Date | 2026-05-25 |
| Status | `decision` |
| Scope | Framework-level cognition maturity states |
| Dependency | `specs/context-initialization.md`, `specs/context-validation.md`, `specs/mode-invocation.md` |

---

## 0. Purpose

This document defines the maturity and validation lifecycle of Forge cognition behavior.

It defines:
- Framework maturity states.
- Criteria for promoting cognition behavior between states.
- Criteria for creating validation cases.
- Coverage philosophy for Forge cognition evolution.
- The boundary before runtime, tooling, or automation work begins.

This document does NOT:
- Implement tooling or automation.
- Redesign the existing Forge structure.
- Add runtime executors, orchestration, agents, or services.
- Define repository-specific context content.
- Treat repository count or file count as maturity.

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
- `planning-mode emits ECP, not PRD prose`
- `planning-mode adapts sections to active layers`
- `planning-mode scopes on-demand loading to the change`
- `implementation-mode emits executable task breakdown, not code changes`
- `execute-mode modifies repositories only from approved tasks`
- `testing-mode owns test strategy, mocks/fakes/stubs, coverage, and regression validation`
- `review-mode validates execute results without replacing testing mode`
- `runtime.non_interactive` controls interaction behavior without rewriting repository cognition

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

For mode benchmarks, expected behavior should verify structured Engineering Change Plan output, layer-adaptive sections, evidence/inference/unknown separation, implementation task decomposition, execute-mode repository modification boundaries, testing-mode cognition boundaries, review-mode risk validation, and rejection of unsupported backend-only or topology assumptions.

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
- More benchmark cases without new semantic coverage.

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

---

## 10. Promotion Rules

| From | To | Required Signal |
|---|---|---|
| `initialized` | `audited` | Validation rules applied; evidence and semantic risks reviewed |
| `audited` | `cognition-validated` | Specific cognition pattern proven correct against evidence |
| `cognition-validated` | `benchmarked` | Pattern added to `validation-cases/` with expected behavior and regression value |
| `benchmarked` | `stable` | Pattern repeatedly validates across repository or topology diversity |

Promotion is not automatic. Each transition requires explicit evidence for the next state.

---

## 11. State Summary

| State | What Is Proven | What Is Not Proven |
|---|---|---|
| `initialized` | Structure exists | Semantic correctness |
| `audited` | Context reviewed against validation and evidence rules | Cognition benchmark correctness |
| `cognition-validated` | One cognition pattern behaves correctly | Regression coverage |
| `benchmarked` | Future regression can be detected for the pattern | Cross-repository maturity |
| `stable` | Pattern is mature across repository/topology diversity | Universal applicability |

---

## 12. Governance Rule

Forge lifecycle state must be assigned to cognition behavior, not to repository size or documentation volume.

A large repository with many context files can remain `initialized` or `audited`.

A small repository can validate a high-value cognition pattern if it provides strong topology evidence and a clear hallucination boundary.
