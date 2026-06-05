# Final Config Shape

| Field | Value |
|---|---|
| Pattern | `final-0-3-0-config-shape` |
| Lifecycle state | `benchmarked` |
| Coverage category | Config vocabulary, migration regression |
| Scope | Repository-neutral config benchmark |

---

## Expected Behavior

`forge.config.yaml` uses the final v0.3.1 top-level keys:

```text
forge
run
workflow
context
policy
team
artifacts
tools
```

Required final values:
- `workflow.default_mode` points to a final core mode.
- `team.context_update_flow` is `reviewable_patch`.
- `team.require_context_impact_check` is `true`.
- `artifacts.output_dir` is `.forge/generated`.
- `artifacts.patch_dir` is `.forge/context-patches`.
- `artifacts.temp_dir` is `.forge/temp`.
- `artifacts.cache_dir` is `.forge/cache`.

## Incorrect Behaviors Forge Must Reject

- Active config examples using `runtime.profile`, `non_interactive`, `decision_authority`, `loading.default_mode`, or `apply_allowed`.
- Using `allowed_modes` as the default workflow shape.
- Treating `.forge/generated` as curated context source of truth.
- Ignoring context impact checks in team workflows.

## Regression Signals

This case regresses if old config vocabulary appears as current active config semantics instead of explicitly marked legacy or compatibility text.
