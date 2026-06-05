# Context Impact Check

| Field | Value |
|---|---|
| Pattern | `context-impact-check` |
| Lifecycle state | `benchmarked` |
| Coverage category | Review context impact, patch proposal boundary, lightweight daily usage |
| Scope | Repository-neutral context benchmark |

---

## Expected Behavior

Every `forge-review` includes a small `Context Impact` section:

```text
Context Impact:
- update_needed: true | false | unknown
- reason:
- affected_context_files:
- suggested_context_patch:
```

Expected interpretations:
- `update_needed: false` for pure internal refactors, formatting-only changes, local test-only improvements, small helper extraction preserving behavior, temporary implementation detail, one-off execution report, or generated artifact with no durable context value.
- `update_needed: true` when reviewed changes affect durable repository knowledge such as architecture boundaries, public API behavior, domain rules, security boundaries, operational conventions, repository structure, service/system responsibilities, dependency/provider behavior, testing/validation conventions, workflow conventions, or durable decisions/constraints.
- `update_needed: unknown` when available evidence is insufficient for a safe conclusion.

When `update_needed: true`, Forge proposes a reviewable `.forge/context-patches/<date>-<slug>.md` path rather than mutating `.forge/context` directly.

## Incorrect Behaviors Forge Must Reject

- Omitting `Context Impact` from review output.
- Treating every review as a full context quality audit.
- Using `update_needed: true` without a reviewable patch proposal path.
- Writing `.forge/context` directly from review output.
- Auto-accepting a context patch because review found context impact.

## Regression Signals

This case regresses if routine review loses the lightweight `Context Impact` check, if durable context changes bypass `.forge/context-patches`, or if review starts mutating `.forge/context` directly.
