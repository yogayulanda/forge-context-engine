# Stale Terminology Guards

| Field | Value |
|---|---|
| Pattern | `stale-terminology-guards` |
| Lifecycle state | `benchmarked` |
| Coverage category | Migration regression, stale vocabulary |
| Scope | Repository-neutral terminology benchmark |

---

## Guarded Terms

These terms must not appear as current active config, lifecycle, or mode semantics:

```text
runtime.profile
non_interactive
decision_authority
loading.default_mode
apply_allowed
ready_for_package
check as generic mode
package as top-level mode
planning as active core mode
testing as active core mode
incident as active core mode
refactor as active core mode
```

## Allowed Preservation

Old terms may remain only when explicitly marked as:
- legacy,
- compatibility,
- scenario,
- generic English,
- historical note,
- false positive in a validation report.

## Regression Signals

This case regresses if any guarded term appears in active instructions, config examples, mode lists, command docs, or validation expectations without an explicit preservation reason.
