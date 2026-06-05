# Final Mode Boundaries

| Field | Value |
|---|---|
| Pattern | `final-mode-boundaries` |
| Lifecycle state | `benchmarked` |
| Coverage category | Mode boundary, approval gate, lifecycle regression |
| Scope | Repository-neutral mode benchmark |

---

## Expected Behavior

Final core modes are:

```text
init
ask
plan
implementation
execute
review
verify-context
```

Mode boundaries:
- `init` creates confirmed `.forge/context` and config through scan plus human confirmation.
- `ask` answers evidence-aware questions without mutation.
- `plan` emits Quick Plan or SDD and waits for Gate 1 approval.
- `plan` includes assumptions when ambiguity exists plus acceptance criteria and validation commands.
- `implementation` emits ECP/readiness output and does not edit code.
- `execute` applies an approved ECP, runs per-task scoped validation and final validation, and may fix in-scope failures.
- `review` uses verdicts and checks goal alignment, validation evidence, lifecycle boundary compliance, security, and context impact.
- `verify-context` checks context health only.

## Incorrect Behaviors Forge Must Reject

- Treating `planning`, `testing`, `incident`, or `refactor` as active core modes.
- Treating `check` or `package` as top-level modes.
- Emitting code changes from `implementation`.
- Broad-loading all modes or all context before inspecting the requested mode.
- Letting `verify-context` validate plans, ECPs, code diffs, MR readiness, or production readiness.

## Regression Signals

This case regresses if any final mode collapses into generic reasoning or if old mode names are presented as current core lifecycle modes.
