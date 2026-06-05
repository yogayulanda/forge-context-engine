# Legacy Mode Compatibility Only

| Field | Value |
|---|---|
| Pattern | `legacy-mode-compatibility-only` |
| Lifecycle state | `benchmarked` |
| Coverage category | Lifecycle mode boundary, legacy compatibility guard |
| Scope | Forge v0.4 docs, runtime templates, and context guidance |

---

## Expected Behavior

Active core lifecycle remains:

```text
init
ask
plan
implementation
execute
review
verify-context
```

Legacy or scenario files such as:
- `planning.md`
- `testing.md`
- `incident.md`
- `refactor.md`

may remain only as compatibility, scenario, or historical guidance. They must not be presented as active core modes.

## Incorrect Behaviors Forge Must Reject

- Presenting `planning`, `testing`, `incident`, or `refactor` as active top-level lifecycle modes.
- Adding new core modes through CLI docs, packaged templates, or validation guidance.

## Regression Signals

This case regresses if any legacy/scenario mode name is presented as active current lifecycle contract rather than compatibility or scenario guidance only.
