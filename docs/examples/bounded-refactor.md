# Bounded Refactor

Use this example for behavior-preserving cleanup.

## Refactor Request

```text
Use Forge refactor mode for the notification package.
Preserve behavior, public contracts, database schema, and configuration keys.
Classify risk and identify validation needed before execution.
```

Expected output:

- problem areas supported by code evidence
- risk classification
- safe improvements
- out-of-scope redesigns
- behavior-preservation checks
- validation expectations

## Implementation Boundary

```text
Use Forge implementation mode for the approved low-risk refactor.
Produce task cards and stop if behavior preservation cannot be proven from tests or call sites.
```

Expected output:

- readiness status
- task cards
- likely files
- do-not-change boundaries
- acceptance criteria

## Execute

```text
Use Forge execute mode for the approved refactor task cards.
Keep names natural, follow nearby style, and avoid unrelated cleanup.
```

Expected output:

- changed files
- behavior-preservation checks
- validation run or blocked
- rollback notes

Refactor mode is not for architecture rewrites, paradigm migration, or hidden behavior changes.
