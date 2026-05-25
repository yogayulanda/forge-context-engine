# Forge v1 Baseline Freeze

Date: 2026-05-25

## Freeze Summary

Forge v1 establishes the lifecycle foundation for bounded AI-assisted engineering work.

The baseline includes:

- context structure under `.forge/context/`
- mode invocation protocol
- lifecycle modes for ask, planning, implementation, execute, testing, review, incident, and refactor
- runtime profile metadata with `runtime.non_interactive` as the controlling interaction flag
- status vocabularies for implementation, execute, testing, and review
- bounded lifecycle artifact semantics
- validation rules for structure, evidence, status, runtime behavior, artifacts, governance, and drift
- repository-first safety boundaries

This freeze does not include runtime executors, orchestration, CI/CD behavior, deploy automation, agent loops, persistent AI memory, RAG, vector search, or knowledge graph systems.

## Completed Lifecycle Areas

- Lifecycle cohesion across all visible modes.
- Status consistency across implementation, execute, testing, and review.
- Runtime profile and non-interactive behavior boundaries.
- Human confirmation and `NEEDS_HUMAN_APPROVAL` semantics for high-risk decisions.
- Artifact lifecycle boundaries and mode-owned artifact types.
- Scoped loading and `CONTEXT_BUDGET_LIMITED` semantics.
- Drift reporting against current repository evidence.
- Governance risk signals for financial correctness, idempotency, retry/replay, rollback, secrets/PII, validation honesty, and blast radius.
- Runtime mode file schema with numeric `token_budget`.
- Validation rule set aligned to the v1 lifecycle.

## Known Future Directions

Future work may explore:

- automated validation checks for existing manual validation rules
- richer validation cases from real project pilots
- clearer examples for common repository shapes
- lightweight initialization ergonomics
- better documentation for target-repo adoption
- evidence-backed refinements to mode wording and report structure

These are future directions only. They do not change the v1 baseline and should not be presented as implemented behavior until they exist.

## Rules For Future Refinement

- Preserve repository/code as source of truth.
- Keep lifecycle modes distinct.
- Do not add statuses, modes, artifact types, or workflow concepts without repeated real-world evidence.
- Do not introduce orchestration, agents, DAGs, deploy automation, CI/CD execution, runtime executors, persistent AI memory, RAG, vector search, or knowledge graph semantics.
- Keep `runtime.non_interactive` as the single controlling interaction flag.
- Keep `runtime.profile` as metadata only.
- Keep artifacts small, optional, mode-owned, and non-authoritative.
- Treat high-risk governance decisions as requiring human approval.
- Prefer direct evidence over broad context loading.
- Keep output practical, concise, and MR-oriented.

## Recommended Git Baseline

Recommended tag:

```text
v1.0.0
```

Recommended baseline branch:

```text
baseline/forge-v1
```

Suggested freeze commit message:

```text
docs: freeze forge v1 lifecycle baseline
```

## Recommended Next Step

After freeze:

1. Use Forge v1 in real repositories.
2. Collect friction from actual planning, implementation, execution, testing, review, incident, and refactor sessions.
3. Convert repeated friction into small validation cases or documentation patches.
4. Refine incrementally only when evidence shows the baseline needs adjustment.

Forge v1 should now move from foundation design into real-world pilot usage and evidence-based iteration.
